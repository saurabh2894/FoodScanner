"""Synthetic setup/failure controls for the strict local browser gate."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location('provenance_gate', Path(__file__).resolve().parents[1] / 'scripts/run_provenance_check.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def test_missing_node_is_setup_failure_not_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(gate.shutil, 'which', lambda _: None)
    assert gate.run(tmp_path) == 2


def test_missing_dependency_is_setup_failure_not_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(gate.shutil, 'which', lambda _: '/node')
    monkeypatch.setattr(gate.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=1, stdout='', stderr='missing'))
    assert gate.run(tmp_path) == 2


def test_invalid_browser_is_setup_failure_not_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(gate.shutil, 'which', lambda _: '/node')
    monkeypatch.setattr(gate.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout='/missing/chromium', stderr=''))
    assert gate.run(tmp_path, str(tmp_path / 'absent-browser')) == 2


def test_missing_build_is_setup_failure_not_pass(tmp_path, monkeypatch):
    browser = tmp_path / 'browser'
    browser.touch()
    monkeypatch.setattr(gate, 'ROOT', tmp_path)
    monkeypatch.setattr(gate.shutil, 'which', lambda _: '/node')
    monkeypatch.setattr(gate.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout=str(browser), stderr=''))
    assert gate.run(tmp_path / 'out', str(browser)) == 2


def test_failed_browser_cannot_reuse_previous_passing_evidence(tmp_path, monkeypatch):
    import json
    import subprocess
    root = tmp_path / 'repo'
    browser = tmp_path / 'browser'
    browser.touch()
    (root / 'web_preview/dist').mkdir(parents=True)
    (root / 'web_preview/dist/index.html').write_text('test page')
    image = root / 'evaluation/browser_acceptance_18_senior/inputs/original_multigrain_label.jpg'
    image.parent.mkdir(parents=True)
    image.touch()
    out = tmp_path / 'out'
    out.mkdir()
    record = out / 'result-source-controls.json'
    record.write_text(json.dumps({'checks': [{'passed': True}] * 22}))
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
    import run_browser_acceptance_18
    monkeypatch.setattr(run_browser_acceptance_18, 'build_provenance', lambda: {'status': 'exact_rebuild_match'})
    monkeypatch.setattr(gate, 'ROOT', root)
    monkeypatch.setattr(gate.shutil, 'which', lambda _: '/node')
    calls = []
    def fake_run(*args, **kwargs):
        calls.append(args)
        if len(calls) == 1:
            return subprocess.CompletedProcess(args[0], 0, str(browser), '')
        return subprocess.CompletedProcess(args[0], 1, '', 'synthetic failure')
    monkeypatch.setattr(gate.subprocess, 'run', fake_run)
    assert gate.run(out, str(browser)) == 1
    assert not record.exists()
    assert (out / 'browser.stderr.log').read_text() == 'synthetic failure'


def test_wrong_build_is_failure_not_setup_or_pass(tmp_path, monkeypatch):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
    import run_browser_acceptance_18
    monkeypatch.setattr(run_browser_acceptance_18, 'build_provenance', lambda: {'status': 'mismatch'})
    root = tmp_path / 'repo'
    (root / 'web_preview/dist').mkdir(parents=True)
    (root / 'web_preview/dist/index.html').write_text('stale page')
    browser = tmp_path / 'browser'
    browser.touch()
    monkeypatch.setattr(gate, 'ROOT', root)
    monkeypatch.setattr(gate.shutil, 'which', lambda _: '/node')
    monkeypatch.setattr(gate.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout=str(browser), stderr=''))
    assert gate.run(tmp_path / 'out', str(browser)) == 1
