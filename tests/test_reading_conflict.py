"""Keep actual millet OCR alternatives separate, without changing selection."""
import io
from pathlib import Path
from foodscan.pipeline import analyse_image
from foodscan.web.app import create_app

D = Path(__file__).parent / 'fixtures/native_millet_readings'
class ActualFrozenReadings:
    def extract_text(self, path): return (D / 'first.txt').read_text()
    def extract_text_alt(self, path): return (D / 'second.txt').read_text()


def test_actual_readings_keep_first_and_both_conflicting_code_sets():
    a = analyse_image('unused', ActualFrozenReadings())
    assert [s[0] for s in a.sections] == ['Seasoning 12%']
    assert '296' in {u.code for u in a.ins_mappings} and '295' not in {u.code for u in a.ins_mappings}
    c = a.reading_conflict
    assert c['chosen'] == 'first'
    assert c['readings'][0]['sections'] == ['Seasoning 12%']
    assert c['readings'][1]['sections'] == ['Puff 88%', 'Seasoning 12%']
    assert '296' in c['readings'][0]['codes'] and '295' not in c['readings'][0]['codes']
    assert '295' in c['readings'][1]['codes'] and '296' not in c['readings'][1]['codes']
    assert any('disagree' in w and '296' in w and '295' in w for w in a.warnings)


def test_native_web_shows_chosen_and_alternative_without_merging():
    r = create_app(ActualFrozenReadings()).test_client().post('/', data={'photo': (io.BytesIO(b'x'), 'label.jpg')}, content_type='multipart/form-data')
    h = r.get_data(as_text=True)
    for x in ['Photo readings differ', 'first reading only', 'Compare both readings', 'Second reading (not used)', 'INS 295', 'INS 296', 'does not prove correct characters or codes']:
        assert x in h


def test_identical_actual_readings_have_no_conflict_panel():
    class Same(ActualFrozenReadings):
        def extract_text_alt(self, path): return self.extract_text(path)
    assert analyse_image('unused', Same()).reading_conflict is None


def test_browser_conflict_panel_with_frozen_actual_readings(tmp_path):
    import os
    import shutil
    import subprocess
    import pytest
    root = Path(__file__).resolve().parents[1]
    if not shutil.which('node') or not (root / 'web_preview/dist/index.html').exists():
        pytest.skip('needs node and built preview')
    probe = subprocess.run(['node', '-e', "require('playwright')"], cwd=root / 'tests/js', capture_output=True)
    if probe.returncode:
        pytest.skip('needs playwright')
    r = subprocess.run(['node', str(root / 'tests/js/reading_conflict_review.js'), str(tmp_path)],
                       cwd=root / 'tests/js', env=os.environ.copy(), capture_output=True, text=True, timeout=90)
    assert r.returncode == 0, r.stdout + r.stderr
