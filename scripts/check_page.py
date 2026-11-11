#!/usr/bin/env python3
"""Sanity-check one or more note pages.

Usage:  python3 scripts/check_page.py part-03.html [part-04.html ...]

Checks: balanced HTML tags, inline <script> syntax (needs node), required
markers, duplicate ids, literal colours in markup, MathJax delimiter balance,
and YouTube timestamp links.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

VOID = {"meta", "link", "br", "img", "input", "hr", "source", "wbr", "col", "area", "base", "embed", "track", "param"}
SVG_SELF = {"path", "line", "circle", "rect", "ellipse", "polygon", "polyline", "stop", "use"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, tuple[int, int]]] = []
        self.errors: list[str] = []
        self.ids: dict[str, int] = {}

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == "id" and v:
                self.ids[v] = self.ids.get(v, 0) + 1
        if tag in VOID:
            return
        self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        for k, v in attrs:
            if k == "id" and v:
                self.ids[v] = self.ids.get(v, 0) + 1

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
            return
        # tolerate implicit closes of <p>/<li>/<td>/<tr>/<dt>/<dd>
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                skipped = [t for t, _ in self.stack[i + 1:]]
                if any(t not in {"p", "li", "td", "th", "tr", "dt", "dd", "option"} for t in skipped):
                    self.errors.append(f"</{tag}> at line {self.getpos()[0]} closes over unclosed {skipped}")
                del self.stack[i:]
                return
        self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []

    b = Balance()
    b.feed(text)
    problems += b.errors[:10]
    left = [f"<{t}> line {pos[0]}" for t, pos in b.stack if t not in {"p", "li", "td", "th", "tr", "dt", "dd"}]
    if left:
        problems.append(f"unclosed tags: {left[:8]}")
    dups = [k for k, v in b.ids.items() if v > 1]
    if dups:
        problems.append(f"duplicate ids: {dups[:10]}")

    for name in ("PARTNAV", "PAGER"):
        if f"<!-- {name}:START -->" not in text or f"<!-- {name}:END -->" not in text:
            problems.append(f"missing <!-- {name}:START/END --> markers")
    for needed in ('href="notes.css"', 'src="notes.js"', 'src="theme.js"', "<!doctype html>", '<meta charset="utf-8">', "<title>"):
        if needed not in text:
            problems.append(f"missing {needed}")

    # literal colours in markup (outside <style> blocks)
    markup = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
    markup = re.sub(r"<script.*?</script>", "", markup, flags=re.S)
    markup = re.sub(r'<link rel="icon"[^>]*>', "", markup)
    for m in re.finditer(r'(fill|stroke|color|background)\s*[:=]\s*"?\s*(#[0-9a-fA-F]{3,8}|rgba?\()', markup):
        line = markup[: m.start()].count("\n") + 1
        problems.append(f"literal colour near markup line {line}: {m.group(0)[:40]}")
        break

    # inline scripts
    for i, s in enumerate(re.findall(r"<script>(.*?)</script>", text, re.S)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(s)
        try:
            r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
            if r.returncode != 0:
                problems.append(f"inline script {i} syntax error: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.stderr}")
        except FileNotFoundError:
            problems.append("node not found; script syntax not checked")
            break

    # MathJax delimiters (ignore <script> contents)
    body = re.sub(r"<script.*?</script>", "", text, flags=re.S)
    if body.count("\\(") != body.count("\\)"):
        problems.append(f"unbalanced \\( \\): {body.count(chr(92) + '(')} vs {body.count(chr(92) + ')')}")
    if body.count("\\[") != body.count("\\]"):
        problems.append(f"unbalanced \\[ \\]: {body.count(chr(92) + '[')} vs {body.count(chr(92) + ']')}")

    # timestamp links
    ts = re.findall(r'youtube\.com/watch\?v=([\w-]{11})&amp;t=(\d+)s', text)
    if not ts:
        problems.append("no timestamp links found")
    bad_amp = re.findall(r'youtube\.com/watch\?v=[\w-]{11}&(?!amp;)', text)
    if bad_amp:
        problems.append(f"{len(bad_amp)} YouTube links use a bare & (write &amp;)")

    return problems


def main() -> None:
    files = [Path(a) for a in sys.argv[1:]]
    if not files:
        print(__doc__)
        sys.exit(2)
    bad = 0
    for f in files:
        probs = check(f)
        if probs:
            bad += 1
            print(f"✗ {f.name}")
            for p in probs:
                print("   -", p)
        else:
            print(f"✓ {f.name}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
