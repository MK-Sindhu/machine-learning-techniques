#!/usr/bin/env python3
"""Navigation for the "extra" series: notes on a long single video, split into pages.

Fills:
  - index.html             <!-- EXTRA-MAP:START --> ... <!-- EXTRA-MAP:END -->
  - <PREFIX>NN.html        <!-- PARTNAV:START --> ... <!-- PARTNAV:END -->
                           <!-- PAGER:START --> ... <!-- PAGER:END -->

Called from sync_nav.py. A page counts as ready when its file exists, or, with
--extra-ready 1,2,3, only the listed pages do.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- configuration for this site ----
PREFIX = "krish-ml-"
SERIES = "Complete Machine Learning in 6 Hours"
AUTHOR = "Krish Naik"
VIDEO = "JxgmHe2NyeY"
HUB_LABEL = "ML in 6 hours"
# (page, title, start second, end second)
PAGES = [
    (1, "Introduction, regression vs classification, linear regression", 0, 4034),
    (2, "Ridge, Lasso and logistic regression", 4034, 8032),
    (3, "Practical: linear, ridge and lasso regression", 8032, 10461),
    (4, "Naive Bayes and KNN", 10461, 12227),
    (5, "Decision trees", 12227, 14954),
    (6, "Ensembles: bagging, random forest, AdaBoost", 14954, 17250),
    (7, "Clustering: K-means, hierarchical, silhouette, DBSCAN", 17250, 20151),
    (8, "Bias–variance, XGBoost and SVM", 20151, 23872),
]
# -------------------------------------

LAST = len(PAGES)
BY_N = {p[0]: p for p in PAGES}
ONLY: set[int] | None = None


def fname(n: int) -> str:
    return f"{PREFIX}{n:02d}.html"


def hms(s: int) -> str:
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def ready(n: int) -> bool:
    if ONLY is not None and n not in ONLY:
        return False
    return (ROOT / fname(n)).exists()


def replace_region(text: str, name: str, content: str) -> str:
    pat = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    return pat.sub(lambda m: m.group(1) + content + m.group(3), text) if pat.search(text) else text


def write_if_changed(path: Path, text: str) -> None:
    if path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def extra_map() -> str:
    rows = []
    for n, title, a, b in PAGES:
        t = html.escape(title)
        cell = f'<a href="{fname(n)}">{t}</a>' if ready(n) else t
        link = f'<a href="https://www.youtube.com/watch?v={VIDEO}&amp;t={a}s" target="_blank" rel="noopener">{hms(a)}–{hms(b)}</a>'
        chip = '<span class="chip ready">Ready</span>' if ready(n) else '<span class="chip planned">Coming</span>'
        rows.append(f"<tr><td>{n:02d}</td><td>{cell}</td><td>{link}</td><td>{chip}</td></tr>")
    return "\n" + "\n".join(rows) + "\n"


def neighbours(n: int):
    prev = next((m for m in range(n - 1, 0, -1) if ready(m)), None)
    nxt = next((m for m in range(n + 1, LAST + 1) if ready(m)), None)
    return prev, nxt


def partnav(n: int) -> str:
    prev, nxt = neighbours(n)
    bits = ['<a href="index.html#extra">All notes</a>', '<span class="sep">/</span>', f"<span>{html.escape(HUB_LABEL)} · Part {n} of {LAST}</span>"]
    if prev:
        bits += ['<span class="sep">·</span>', f'<a href="{fname(prev)}">← Part {prev}</a>']
    if nxt:
        bits += ['<span class="sep">·</span>', f'<a href="{fname(nxt)}">Part {nxt} →</a>']
    return '<nav class="partnav" aria-label="Parts">' + "".join(bits) + "</nav>"


def pager(n: int) -> str:
    prev, nxt = neighbours(n)
    out = ['<nav class="pager" aria-label="Previous and next part">']
    if prev:
        out.append(f'<a href="{fname(prev)}"><span class="dir">← Part {prev}</span><span class="nm">{html.escape(BY_N[prev][1])}</span></a>')
    else:
        out.append(f'<a href="index.html#extra"><span class="dir">← All notes</span><span class="nm">{html.escape(SERIES)}</span></a>')
    if nxt:
        out.append(f'<a class="next" href="{fname(nxt)}"><span class="dir">Part {nxt} →</span><span class="nm">{html.escape(BY_N[nxt][1])}</span></a>')
    elif n < LAST:
        out.append(f'<a class="next" href="index.html#extra"><span class="dir">Part {n + 1} · coming</span><span class="nm">{html.escape(BY_N[n + 1][1])}</span></a>')
    else:
        out.append('<a class="next" href="index.html#extra"><span class="dir">Finished →</span><span class="nm">Back to all notes</span></a>')
    out.append("</nav>")
    return "".join(out)


def run(argv: list[str]) -> None:
    global ONLY
    if "--extra-ready" in argv:
        i = argv.index("--extra-ready")
        if i + 1 < len(argv):
            ONLY = {int(x) for x in argv[i + 1].split(",") if x.strip()}
    idx = ROOT / "index.html"
    if idx.exists():
        write_if_changed(idx, replace_region(idx.read_text(encoding="utf-8"), "EXTRA-MAP", extra_map()))
    done = []
    for n, *_ in PAGES:
        f = ROOT / fname(n)
        if not f.exists() or (ONLY is not None and n not in ONLY):
            continue
        t = f.read_text(encoding="utf-8")
        write_if_changed(f, replace_region(replace_region(t, "PARTNAV", partnav(n)), "PAGER", pager(n)))
        done.append(n)
    print(f"ready {PREFIX}* pages:", done)


if __name__ == "__main__":
    run(sys.argv[1:])
