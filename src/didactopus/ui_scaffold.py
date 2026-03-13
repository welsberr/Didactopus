from __future__ import annotations

from pathlib import Path


HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Didactopus Review UI</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.4; }
.card { border: 1px solid #bbb; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
.small { color: #555; font-size: 0.95rem; }
code { background: #f3f3f3; padding: 0.1rem 0.3rem; border-radius: 4px; }
</style>
</head>
<body>
<h1>Didactopus Draft Pack Review</h1>
<p class="small">Static scaffold. Load <code>review_data.json</code> next to this file for future richer UI behavior.</p>

<div class="card">
  <h2>Workflow</h2>
  <ol>
    <li>Inspect concept list and statuses</li>
    <li>Review prerequisite edges</li>
    <li>Resolve conflicts and flags</li>
    <li>Record curation actions in ledger</li>
    <li>Promote reviewed pack</li>
  </ol>
</div>

<div class="card">
  <h2>Expected local files</h2>
  <ul>
    <li><code>review_data.json</code></li>
    <li><code>review_ledger.json</code></li>
    <li><code>pack.yaml</code></li>
    <li><code>concepts.yaml</code></li>
  </ul>
</div>

<div class="card">
  <h2>Next UI step</h2>
  <p>Replace this scaffold with a SPA that edits the same JSON review-state model.</p>
</div>
</body>
</html>
'''


def write_review_ui(outdir: str | Path) -> None:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "index.html").write_text(HTML, encoding="utf-8")
