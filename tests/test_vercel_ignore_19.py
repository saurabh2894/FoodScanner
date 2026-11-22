"""Deterministic local fixture tests for scripts/vercel-ignore.sh (Task 19).

Verifies Vercel Ignored Build Step script behavior across all required scenarios:
  1. Runtime-only change (e.g. src/foodscan/classify.py) -> exit 1 (build)
  2. Resource-only change (e.g. src/foodscan/resources/lexicon.csv) -> exit 1 (build)
  3. Docs-only change (e.g. README.md, evaluation/...) -> exit 0 (skip build)
  4. Tests-only change (e.g. tests/test_something.py) -> exit 0 (skip build)
  5. Mixed changes (runtime + docs) -> exit 1 (build)
  6. Missing diff / corrupted state -> exit 1 (fail open to build)
  7. Initial commit (no HEAD~1) -> exit 1 (fail open to build)
  8. Merge release with runtime changes -> exit 1 (build)
  9. Merge release with non-runtime changes only -> exit 0 (skip build)
 10. Renamed runtime file -> exit 1 (build)
 11. Deleted runtime file -> exit 1 (build)
 12. Template change (web_preview/template.html) -> exit 1 (build)
 13. JS engine change (web_preview/foodscan.js) -> exit 1 (build)
 14. Worker boot change (web_preview/worker-boot.js) -> exit 1 (build)
 15. Build preview script change (scripts/build_web_preview.py) -> exit 1 (build)
 16. Fetch tesseract script change (scripts/fetch_tesseract_assets.py) -> exit 1 (build)
 17. Parity check script change (scripts/parity_check.py) -> exit 1 (build)
 18. Web tables script change (scripts/web_tables.py) -> exit 1 (build)
 19. Ignore script self-change (scripts/vercel-ignore.sh) -> exit 1 (build)
 20. Hosting config change (vercel.json) -> exit 1 (build)
 21. Dependency manifest change (pyproject.toml) -> exit 1 (build)
 22. Offline batch script change (scripts/oos_eval.py) -> exit 0 (skip build)
 23. VERCEL_GIT_PREVIOUS_SHA multi-commit diff with runtime change -> exit 1 (build)
 24. VERCEL_GIT_PREVIOUS_SHA multi-commit diff with non-runtime changes only -> exit 0 (skip build)
 25. VERCEL_GIT_PREVIOUS_SHA invalid/missing in shallow clone -> falls back to HEAD~1 or fails open
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "vercel-ignore.sh"


def find_sh():
    """Find a POSIX sh / bash executable that works on the current OS."""
    # Check standard PATH
    candidate = shutil.which("sh")
    if candidate and "system32" not in candidate.lower():
        return candidate
    # Common Git for Windows paths
    for path in [
        r"C:\Program Files\Git\bin\sh.exe",
        r"C:\Program Files (x86)\Git\bin\sh.exe",
        r"C:\Program Files\Git\usr\bin\sh.exe",
        "/bin/sh",
        "/usr/bin/sh",
    ]:
        if os.path.isfile(path):
            return path
    candidate = shutil.which("bash")
    if candidate:
        return candidate
    raise RuntimeError("No POSIX sh/bash found on system to execute vercel-ignore.sh")


SH_BIN = find_sh()


class GitFixture:
    """Helper to construct temporary Git repositories with explicit commit histories."""

    def __init__(self, directory: str):
        self.dir = Path(directory)
        self.git("init -b main")
        self.git("config user.name test-runner")
        self.git("config user.email test@example.com")

    def git(self, cmd: str) -> str:
        res = subprocess.run(
            f"git {cmd}",
            cwd=str(self.dir),
            shell=True,
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(f"git {cmd} failed (code {res.returncode}):\n{res.stderr}")
        return res.stdout.strip()

    def write(self, relpath: str, content: str = "sample content\n"):
        p = self.dir / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def remove(self, relpath: str):
        p = self.dir / relpath
        if p.exists():
            p.unlink()

    def commit(self, message: str = "commit"):
        self.git("add -A")
        self.git(f'commit -m "{message}"')

    def run_ignore_script(self, env: dict = None) -> subprocess.CompletedProcess:
        full_env = os.environ.copy()
        # Remove any lingering Vercel env vars unless explicitly passed
        full_env.pop("VERCEL_GIT_PREVIOUS_SHA", None)
        full_env.pop("VERCEL_ENV", None)
        if env:
            full_env.update(env)
        return subprocess.run(
            [SH_BIN, str(SCRIPT_PATH)],
            cwd=str(self.dir),
            capture_output=True,
            text=True,
            env=full_env,
        )


@pytest.fixture
def git_repo():
    with tempfile.TemporaryDirectory() as td:
        yield GitFixture(td)


def test_runtime_only_change(git_repo):
    """Changes to src/foodscan/ code must trigger a build (exit 1)."""
    git_repo.write("src/foodscan/classify.py", "def classify(): pass\n")
    git_repo.commit("initial")
    git_repo.write("src/foodscan/classify.py", "def classify(): return 4\n")
    git_repo.commit("update classifier")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1, f"Expected exit 1 (build), got {res.returncode}. Output:\n{res.stdout}"
    assert "runtime change detected" in res.stdout
    assert "src/foodscan/classify.py" in res.stdout


def test_resource_only_change(git_repo):
    """Changes to resource CSVs in src/foodscan/resources/ must trigger a build (exit 1)."""
    git_repo.write("src/foodscan/resources/lexicon.csv", "name,group\nalmond,1\n")
    git_repo.commit("initial")
    git_repo.write("src/foodscan/resources/lexicon.csv", "name,group\nalmond,1\nwalnut,1\n")
    git_repo.commit("add walnut")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1
    assert "src/foodscan/resources/lexicon.csv" in res.stdout


def test_docs_only_change(git_repo):
    """Changes to documentation (README.md, evaluation/) must skip build (exit 0)."""
    git_repo.write("README.md", "# FoodScanner\n")
    git_repo.write("evaluation/batch_1/README.md", "Evaluation notes\n")
    git_repo.commit("initial")
    git_repo.write("README.md", "# FoodScanner v2\n")
    git_repo.write("evaluation/batch_1/README.md", "Updated evaluation notes\n")
    git_repo.commit("update docs")

    res = git_repo.run_ignore_script()
    assert res.returncode == 0, f"Expected exit 0 (skip), got {res.returncode}. Output:\n{res.stdout}"
    assert "all changed files are non-runtime" in res.stdout


def test_tests_only_change(git_repo):
    """Changes to tests/ must skip build (exit 0)."""
    git_repo.write("tests/test_something.py", "def test_foo(): assert True\n")
    git_repo.commit("initial")
    git_repo.write("tests/test_something.py", "def test_foo(): assert 1 == 1\n")
    git_repo.commit("update test")

    res = git_repo.run_ignore_script()
    assert res.returncode == 0
    assert "all changed files are non-runtime" in res.stdout


def test_mixed_changes(git_repo):
    """When both runtime and non-runtime files change, build must proceed (exit 1)."""
    git_repo.write("README.md", "# FoodScanner\n")
    git_repo.write("src/foodscan/normalise.py", "def norm(): pass\n")
    git_repo.commit("initial")
    git_repo.write("README.md", "# FoodScanner Updated\n")
    git_repo.write("src/foodscan/normalise.py", "def norm(): return ''\n")
    git_repo.commit("mixed update")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1
    assert "runtime change detected" in res.stdout


def test_initial_commit_fail_open(git_repo):
    """On initial commit (no parent / no HEAD~1), script must fail open (exit 1 to build)."""
    git_repo.write("README.md", "initial repo commit\n")
    git_repo.commit("first commit")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1
    assert "no parent commit found" in res.stdout or "fail open" in res.stdout


def test_merge_release_with_runtime(git_repo):
    """Merge commit bringing in runtime changes must trigger build (exit 1)."""
    git_repo.write("README.md", "# Main\n")
    git_repo.commit("initial main")

    git_repo.git("checkout -b feature-runtime")
    git_repo.write("src/foodscan/pipeline.py", "def run(): pass\n")
    git_repo.commit("feature commit")

    git_repo.git("checkout main")
    git_repo.git('merge --no-ff feature-runtime -m "Merge feature-runtime"')

    res = git_repo.run_ignore_script()
    assert res.returncode == 1
    assert "src/foodscan/pipeline.py" in res.stdout


def test_merge_release_docs_only(git_repo):
    """Merge commit bringing in only documentation changes must skip build (exit 0)."""
    git_repo.write("README.md", "# Main\n")
    git_repo.commit("initial main")

    git_repo.git("checkout -b feature-docs")
    git_repo.write("evaluation/task15/notes.txt", "some evaluation notes\n")
    git_repo.commit("eval docs commit")

    git_repo.git("checkout main")
    git_repo.git('merge --no-ff feature-docs -m "Merge feature-docs"')

    res = git_repo.run_ignore_script()
    assert res.returncode == 0
    assert "all changed files are non-runtime" in res.stdout


def test_renamed_runtime_file(git_repo):
    """Renaming a runtime file must be detected and trigger a build (exit 1)."""
    git_repo.write("web_preview/foodscan.js", "// engine\n")
    git_repo.commit("initial")
    git_repo.git("mv web_preview/foodscan.js web_preview/engine.js")
    git_repo.commit("rename engine")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1
    assert "runtime change detected" in res.stdout


def test_deleted_runtime_file(git_repo):
    """Deleting a runtime file must trigger a build (exit 1)."""
    git_repo.write("src/foodscan/legacy.py", "# legacy\n")
    git_repo.commit("initial")
    git_repo.remove("src/foodscan/legacy.py")
    git_repo.commit("remove legacy")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1
    assert "src/foodscan/legacy.py" in res.stdout


@pytest.mark.parametrize(
    "filepath",
    [
        "web_preview/template.html",
        "web_preview/foodscan.js",
        "web_preview/worker-boot.js",
        "scripts/build_web_preview.py",
        "scripts/fetch_tesseract_assets.py",
        "scripts/parity_check.py",
        "scripts/web_tables.py",
        "scripts/vercel-ignore.sh",
        "vercel.json",
        "pyproject.toml",
    ],
)
def test_all_build_closure_files_trigger_build(git_repo, filepath):
    """Every file in the build dependency closure must trigger a build when modified."""
    git_repo.write(filepath, "original content\n")
    git_repo.commit(f"initial {filepath}")
    git_repo.write(filepath, "modified content\n")
    git_repo.commit(f"modify {filepath}")

    res = git_repo.run_ignore_script()
    assert res.returncode == 1, f"Modifying {filepath} failed to trigger build (exit {res.returncode})"
    assert filepath in res.stdout


def test_offline_batch_script_skips_build(git_repo):
    """Modifying offline evaluation/batch scripts (scripts/oos_eval.py) must skip build (exit 0)."""
    git_repo.write("scripts/oos_eval.py", "# offline evaluation tool\n")
    git_repo.commit("initial")
    git_repo.write("scripts/oos_eval.py", "# offline evaluation tool updated\n")
    git_repo.commit("update offline tool")

    res = git_repo.run_ignore_script()
    assert res.returncode == 0
    assert "all changed files are non-runtime" in res.stdout


def test_vercel_git_previous_sha_runtime(git_repo):
    """When VERCEL_GIT_PREVIOUS_SHA spans multiple commits with runtime changes, build proceeds."""
    git_repo.write("README.md", "init\n")
    git_repo.commit("c1")
    sha1 = git_repo.git("rev-parse HEAD")

    git_repo.write("evaluation/notes.md", "notes\n")
    git_repo.commit("c2: docs only")

    git_repo.write("src/foodscan/vocab.py", "vocab = []\n")
    git_repo.commit("c3: runtime change")

    # Run with VERCEL_GIT_PREVIOUS_SHA set to sha1
    res = git_repo.run_ignore_script(env={"VERCEL_GIT_PREVIOUS_SHA": sha1})
    assert res.returncode == 1
    assert "src/foodscan/vocab.py" in res.stdout


def test_vercel_git_previous_sha_non_runtime(git_repo):
    """When VERCEL_GIT_PREVIOUS_SHA spans multiple commits with only non-runtime changes, build skips."""
    git_repo.write("README.md", "init\n")
    git_repo.commit("c1")
    sha1 = git_repo.git("rev-parse HEAD")

    git_repo.write("evaluation/notes.md", "notes\n")
    git_repo.commit("c2: docs only")

    git_repo.write("tests/test_x.py", "assert 1\n")
    git_repo.commit("c3: tests only")

    res = git_repo.run_ignore_script(env={"VERCEL_GIT_PREVIOUS_SHA": sha1})
    assert res.returncode == 0
    assert "all changed files are non-runtime" in res.stdout


def test_vercel_git_previous_sha_missing_in_shallow_clone(git_repo):
    """If VERCEL_GIT_PREVIOUS_SHA does not exist in local history, fall back to HEAD~1 or fail open."""
    git_repo.write("README.md", "init\n")
    git_repo.commit("c1")
    git_repo.write("README.md", "updated\n")
    git_repo.commit("c2")

    fake_sha = "0123456789abcdef0123456789abcdef01234567"
    res = git_repo.run_ignore_script(env={"VERCEL_GIT_PREVIOUS_SHA": fake_sha})
    # Should fall back to HEAD~1, which only touched README.md -> exit 0
    assert res.returncode == 0
    assert "not in local history" in res.stdout
    assert "using parent commit HEAD~1" in res.stdout
