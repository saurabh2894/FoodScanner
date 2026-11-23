"""Real-evidence triage is current, text-deduplicated and read-only."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.triage_real_label_gaps import triage


def test_real_inputs_tie_out_and_keep_original_abstention():
    r = triage()
    assert r['unique_inputs'] == r['answered'] + r['abstained']
    originals = [x for x in r['records'] if x['input_path'].endswith('/original_multigrain_label.txt')]
    assert len(originals) == 1 and not originals[0]['answered']
    assert 'Sprouted Ragi' in originals[0]['recognised_unplaced']
    assert 'Date Powder' in originals[0]['reason']
    assert all('group name; its contents were assessed separately' not in u for x in r['records'] for u in x['not_assessed'])


def test_refuses_overwrite_and_tracked_evaluation_output(tmp_path):
    out = tmp_path / 'result.json'
    cmd = [sys.executable, str(ROOT / 'scripts/triage_real_label_gaps.py'), '--out', str(out)]
    assert subprocess.run(cmd, capture_output=True).returncode == 0
    first = out.read_bytes()
    assert subprocess.run(cmd, capture_output=True).returncode != 0 and out.read_bytes() == first
    blocked = ROOT / 'evaluation/triage-must-not-be-created.json'
    r = subprocess.run(cmd[:-1] + [str(blocked)], capture_output=True)
    assert r.returncode != 0 and not blocked.exists()
