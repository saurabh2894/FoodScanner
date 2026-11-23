"""Presentation gate on three existing real labels. No new classification expectations."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_real_label_item_explanations_are_visible_and_evidence_expands(tmp_path):
    if not shutil.which('node') or not (ROOT / 'web_preview/dist/index.html').exists():
        pytest.skip('needs node and a current built preview')
    probe = subprocess.run(['node', '-e', "require('playwright')"], cwd=ROOT / 'tests/js', capture_output=True)
    if probe.returncode:
        pytest.skip('needs playwright')
    r = subprocess.run(['node', str(ROOT / 'tests/js/item_explanation_review.js'), str(tmp_path)],
                       cwd=ROOT / 'tests/js', env=os.environ.copy(), capture_output=True, text=True, timeout=90)
    assert r.returncode == 0, r.stdout + r.stderr
    checks = json.loads((tmp_path / 'ui-checks.json').read_text())
    assert checks and all(c['pass'] for c in checks)
