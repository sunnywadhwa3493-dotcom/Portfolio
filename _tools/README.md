# Job kit generator

1. Add `_tools/jobs/<slug>.json` (copy an existing one; facts only).
2. Run `python3 _tools/build.py <slug>` (or `all`).
3. Commit and push. Kit goes live at `/Portfolio/jobs/<slug>/` with the resume PDF beside it.

Folders starting with `_` are not published by GitHub Pages.
