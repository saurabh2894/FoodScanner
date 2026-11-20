Put label photos in data/samples/ (git-ignored) and add one row per photo to labels.csv:

    file,nova_ref,status,notes
    atta_front.jpg,1,confirmed,plain atta

- `nova_ref`: your own NOVA call (1-4). Provisional, not ground truth.
- `status`: `confirmed` or `uncertain`. Uncertain rows are excluded from accuracy
  but kept in the abstention analysis.
- `file` may be an image, or a `.txt` file holding label text (bypasses OCR).
- Do a second review pass on a different day and compare a sample to Open Food Facts.

data/synthetic/ holds the four invented examples from research/02 rendered as PNGs
(scripts/make_synthetic.py). They test the plumbing only; accuracy on them says nothing
about real labels. Run: python -m foodscan.evaluate data/synthetic/labels.csv
