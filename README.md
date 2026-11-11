# Machine Learning Techniques: lecture notes

Notes for the IIT Madras BS course **Machine Learning Techniques** (Prof. Arun Rajkumar), covering all 74 lectures of the [YouTube playlist](https://www.youtube.com/playlist?list=PLZ2ps__7DhBbA_e6_G3FI-BA1f7lCINUu), grouped into 18 parts. Each part has diagrams, the maths written out, timestamp links into the videos, and self-test questions.

Written from the lecture transcripts. Not an official IIT Madras resource.

## Structure

| Path | What it is |
| --- | --- |
| `index.html` | Hub page with the course map |
| `part-01.html` … `part-18.html` | One page per part |
| `notes.css`, `notes.js` | Styles and behaviour shared by every page |
| `theme.js` | Light/dark theme switch (button in the top-right corner; remembers your choice) |
| `scripts/sync_nav.py` | Regenerates the course map and prev/next links |

It is a plain static site: no build step, no dependencies. Maths is rendered by MathJax from a CDN.

## View locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy on Vercel

Import the repository, choose the **Other** framework preset, and leave the build command and output directory empty. Vercel serves the files from the repository root.

## Adding or editing a part

After adding a `part-XX.html` file, run:

```bash
python3 scripts/sync_nav.py
```

It marks the part as ready on the hub and updates the previous/next links on every page.
