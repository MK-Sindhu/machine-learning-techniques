#!/usr/bin/env python3
"""Regenerate navigation for the MLT notes site.

Rewrites the marked regions in:
  - index.html      <!-- COURSE-MAP:START --> ... <!-- COURSE-MAP:END -->
  - part-XX.html    <!-- PARTNAV:START --> ... <!-- PARTNAV:END -->
                    <!-- PAGER:START --> ... <!-- PAGER:END -->

A part counts as "ready" when its part-XX.html file exists.
Run from anywhere:  python3 scripts/sync_nav.py
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOTAL = 18

# (part number, title, lecture range, group)
PARTS = [
    (1, "Introduction and paradigms", "L1–L2", "Introduction"),
    (2, "Representation learning", "L3–L5", "Unsupervised learning"),
    (3, "Principal component analysis", "L6–L7", "Unsupervised learning"),
    (4, "Issues with PCA, and computing it fast", "L8–L9", "Unsupervised learning"),
    (5, "Feature maps, kernels and kernel PCA", "L10–L12", "Unsupervised learning"),
    (6, "K-means: the algorithm and its convergence", "L13–L15", "Unsupervised learning"),
    (7, "K-means: geometry, initialization, choosing K", "L16–L18", "Unsupervised learning"),
    (8, "Estimation: maximum likelihood and Bayesian", "L19–L21", "Unsupervised learning"),
    (9, "Gaussian mixture models and EM", "L22–L26", "Unsupervised learning"),
    (10, "Linear regression and gradient descent", "L27–L31", "Supervised learning"),
    (11, "Kernel and probabilistic regression", "L32–L35", "Supervised learning"),
    (12, "Ridge and LASSO", "L36–L40", "Supervised learning"),
    (13, "Classification: k-NN and decision trees", "L41–L44", "Supervised learning"),
    (14, "Generative models and Naive Bayes", "L45–L51", "Supervised learning"),
    (15, "Perceptron and logistic regression", "L52–L56", "Supervised learning"),
    (16, "Support vector machines", "L57–L65", "Supervised learning"),
    (17, "Ensembles: bagging and boosting", "L66–L68", "Supervised learning"),
    (18, "Loss functions, neural networks and summary", "L69–L74", "Supervised learning"),
]


def fname(n: int) -> str:
    return f"part-{n:02d}.html"


ONLY: set[int] | None = None  # set by --ready 1,2,4 to restrict which parts count as ready


def ready(n: int) -> bool:
    if ONLY is not None and n not in ONLY:
        return False
    return (ROOT / fname(n)).exists()


def write_if_changed(path: Path, text: str) -> None:
    if path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def replace_region(text: str, name: str, content: str) -> str:
    pat = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    if not pat.search(text):
        return text
    return pat.sub(lambda m: m.group(1) + content + m.group(3), text)


def course_map() -> str:
    rows, group = [], None
    for n, title, lec, grp in PARTS:
        if grp != group:
            rows.append(f'<tr class="group"><td colspan="4">{html.escape(grp)}</td></tr>')
            group = grp
        t = html.escape(title)
        if ready(n):
            cell = f'<a href="{fname(n)}">{t}</a>'
            chip = '<span class="chip ready">Ready</span>'
        else:
            cell = t
            chip = '<span class="chip planned">Coming</span>'
        rows.append(f"<tr><td>{n:02d}</td><td>{cell}</td><td>{lec}</td><td>{chip}</td></tr>")
    return "\n" + "\n".join(rows) + "\n"


def partnav(n: int) -> str:
    bits = ['<a href="index.html">MLT Notes</a>', '<span class="sep">/</span>', f"<span>Part {n} of {TOTAL}</span>"]
    if n > 1 and ready(n - 1):
        bits += ['<span class="sep">·</span>', f'<a href="{fname(n - 1)}">← Part {n - 1}</a>']
    if n < TOTAL and ready(n + 1):
        bits += ['<span class="sep">·</span>', f'<a href="{fname(n + 1)}">Part {n + 1} →</a>']
    return '<nav class="partnav" aria-label="Parts">' + "".join(bits) + "</nav>"


def pager(n: int) -> str:
    out = ['<nav class="pager" aria-label="Previous and next part">']
    if n > 1:
        p = PARTS[n - 2]
        if ready(n - 1):
            out.append(f'<a href="{fname(n - 1)}"><span class="dir">← Part {n - 1}</span><span class="nm">{html.escape(p[1])}</span></a>')
    else:
        out.append('<a href="index.html"><span class="dir">← All parts</span><span class="nm">Course map</span></a>')
    if n < TOTAL:
        q = PARTS[n]
        if ready(n + 1):
            out.append(f'<a class="next" href="{fname(n + 1)}"><span class="dir">Part {n + 1} →</span><span class="nm">{html.escape(q[1])}</span></a>')
        else:
            out.append(f'<a class="next" href="index.html"><span class="dir">Part {n + 1} · coming</span><span class="nm">{html.escape(q[1])}</span></a>')
    else:
        out.append('<a class="next" href="index.html"><span class="dir">Finished →</span><span class="nm">Back to all parts</span></a>')
    out.append("</nav>")
    return "".join(out)


def main() -> None:
    global ONLY
    args = sys.argv[1:]
    if args[:1] == ["--ready"] and len(args) > 1:
        ONLY = {int(x) for x in args[1].split(",") if x.strip()}
    idx = ROOT / "index.html"
    if idx.exists():
        write_if_changed(idx, replace_region(idx.read_text(encoding="utf-8"), "COURSE-MAP", course_map()))
    done = []
    for n, *_ in PARTS:
        f = ROOT / fname(n)
        if not f.exists() or (ONLY is not None and n not in ONLY):
            continue
        t = f.read_text(encoding="utf-8")
        t = replace_region(t, "PARTNAV", partnav(n))
        t = replace_region(t, "PAGER", pager(n))
        write_if_changed(f, t)
        done.append(n)
    print("ready parts:", done)


if __name__ == "__main__":
    main()
