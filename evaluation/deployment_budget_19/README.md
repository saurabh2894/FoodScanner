# Deployment Budget Guard Investigation & Proposed Solution (Task 19)

## 1. Executive Summary & Measured Bottleneck

### The Release Bottleneck
On **November 21, 2026 at 21:40 IST**, deployment of reviewed `origin/main` commit `4e626f9` (509 canonical lexicon rows, 921 parity test cases) failed on Vercel with:
```
Resource is limited - try again in X hours (more than 100, code: "api-deployments-free-per-day")
```
* **Production site** (`https://foodscan-nine.vercel.app/`): Stale at commit `a6cacbc` (433 rows, 859 parity).
* **Main branch**: Successfully integrated at commit `4e626f9` (509 rows, 921 parity).
* **Constraint**: Hobby plan hard ceiling of **100 deployments per rolling 24-hour window** (86,400 seconds). No spending, no plan upgrades, no account changes, and no unauthorized deployment retries. One permitted free retry is scheduled after Nov 22, 2026 at 21:40 IST.

---

## 2. Verified Facts vs. Proposals

### Critical Finding: Ignored Build Step Does NOT Avoid the Daily Deployment Quota
An initial hypothesis was that configuring Vercel's **Ignored Build Step** (`ignoreCommand`) to skip builds when non-runtime documentation or evaluation files change would prevent hitting the 100 deployments/day cap.

**Verified Fact:** **This hypothesis is false.**
Official Vercel documentation explicitly states:
> *"Builds that the Ignored Build Step cancels still count toward deployment and concurrent build limits."*  
> — Source: [Vercel Docs: Ignored Build Step](https://vercel.com/docs/deployments/configure-a-build#ignored-build-step)

When a Git push event reaches Vercel:
1. Vercel registers a **Deployment entity** in its API immediately.
2. Vercel clones the repository and evaluates `ignoreCommand`.
3. If `ignoreCommand` exits with code `0`, Vercel marks the deployment state as `CANCELED` / `SKIPPED`.
4. **However**, the deployment entity was already created and is charged against the 100 deployments/day Hobby limit (`api-deployments-free-per-day`).

Therefore, **Ignored Build Step provides *Compute Suppression* (saving build minutes and worker concurrency), NOT *Quota Prevention*.**

### Root Cause of Quota Exhaustion
The FoodScanner repository currently tracks **69+ remote branches** (`antigravity/*`, `claude/*`, etc.). Every push to any of these development branches automatically triggers a **Preview Deployment** on Vercel. With active multi-agent engineering pushing intermediate checkpoints and evaluation evidence, 100 deployments per day is easily exhausted by preview branch activity alone, leaving zero quota for production releases on `main`.

### The True Quota-Saving Mechanism: `git.deploymentEnabled`
To stop non-production branches from creating deployment entities and consuming quota slots, Vercel provides two supported mechanisms:

1. **Declarative via `vercel.json` (`git.deploymentEnabled`)**:
   Vercel supports branch filtering in `vercel.json` using minimatch patterns. When a branch matches a `false` rule, Vercel's Git webhook ignores the push event entirely and **creates 0 deployments**:
   ```json
   {
     "git": {
       "deploymentEnabled": {
         "main": true,
         "antigravity/*": false,
         "claude/*": false
       }
     }
   }
   ```
2. **Vercel Project Dashboard (Git Settings)**:
   Under **Project Settings -> Git -> Deployment Branches**, preview deployments can be disabled completely or restricted to specific branches.

---

## 3. Two-Layer Architecture: Quota Prevention + Compute Suppression

To completely protect the release pipeline, a two-layer defense is proposed:

| Layer | Goal | Mechanism | Action on Non-Runtime Commits | Impact on Quota |
|---|---|---|---|---|
| **Layer 1** | **Quota Prevention** | `git.deploymentEnabled` in `vercel.json` | Blocks automatic deployments for work branches (`antigravity/*`, `claude/*`) | **Completely saves deployment quota** (0 deployments created) |
| **Layer 2** | **Compute Suppression** | Path-sensitive `scripts/vercel-ignore.sh` via `ignoreCommand` | Cancels build step on `main` when commit only touches docs/evals/tests | Saves build minutes and queue concurrency |

### Exit-Code Semantics for `scripts/vercel-ignore.sh`
* **Exit 0**: Skip / cancel build (all changed files are non-runtime).
* **Exit 1**: Proceed with build (runtime changes detected, OR uncertain diff / error / initial commit / missing parent).
* **Design Principle — Fail Open**: If git diff fails, if git history is shallow and previous SHA is missing, or if diff output is empty/ambiguous, the script **exits 1 to build**. A redundant build is cheap; an erroneously skipped build breaks production.

---

## 4. Build Dependency Closure Analysis

The build process defined in `vercel.json` executes:
`PYTHONPATH=src python3 scripts/fetch_tesseract_assets.py && PYTHONPATH=src python3 scripts/build_web_preview.py`

Tracing the exact runtime closure of files that affect deployed web assets:
1. **Classifier Engine & Runtime Tables**:
   * `src/foodscan/**` (all Python classifier logic and resource CSVs: `lexicon.csv`, `synonyms.csv`, `markers.csv`, `ins_map.csv`, `ins_names.csv`, `descriptors.csv`, `declared_roles.csv`).
2. **Client-side Web Assets**:
   * `web_preview/template.html` (HTML skeleton and base styling).
   * `web_preview/foodscan.js` (JavaScript classifier engine and UI interactions).
   * `web_preview/worker-boot.js` (Tesseract OCR worker bootstrap).
3. **Build & Parity Verification Scripts**:
   * `scripts/build_web_preview.py` (builds artifact and static HTML).
   * `scripts/fetch_tesseract_assets.py` (downloads and extracts pinned Tesseract assets).
   * `scripts/parity_check.py` (executed by `build_web_preview.py`; enforces 100% agreement before building).
   * `scripts/web_tables.py` (serializes resource CSVs to JSON for web embedding).
   * `scripts/vercel-ignore.sh` (the ignore script itself).
4. **Configuration & Dependency Manifests**:
   * `vercel.json` (build commands, routes, headers).
   * `pyproject.toml`, `requirements*.txt`, `package.json`, `package-lock.json` (runtime dependencies).

### Non-Runtime Files (Ignored for Builds):
* `evaluation/**` (task reports, evaluation artifacts, test scans).
* `tests/**` (pytest test suite — verified in CI, not during Vercel web preview build).
* `research/**` (background research and documentation).
* `data/**` (raw datasets, cache, and intermediate corpora).
* `.instinct/**` (agent memory and reflection logs).
* `*.md` (`README.md`, `STATUS.md`, etc.).
* Offline batch scripts in `scripts/` not in build chain (e.g. `oos_eval.py`, `demand_batch.py`, `class_gate.py`, etc.).

---

## 5. Exact File Diffs

### 1. Created File: `scripts/vercel-ignore.sh`
```sh
#!/bin/sh
# vercel-ignore.sh — Vercel Ignored Build Step for FoodScanner
# Called by Vercel via vercel.json "ignoreCommand".
# Exit 0 -> cancel build (skips build compute).
# Exit 1 -> proceed with build.

set -e

echo "vercel-ignore: checking for runtime-affecting changes..."

RUNTIME_PATTERNS='
^src/foodscan/
^web_preview/
^scripts/build_web_preview\.py$
^scripts/fetch_tesseract_assets\.py$
^scripts/parity_check\.py$
^scripts/web_tables\.py$
^scripts/vercel-ignore\.sh$
^vercel\.json$
^pyproject\.toml$
^requirements.*\.txt$
^package\.json$
^package-lock\.json$
'

BASE=""

if [ -n "${VERCEL_GIT_PREVIOUS_SHA:-}" ]; then
    if git cat-file -e "${VERCEL_GIT_PREVIOUS_SHA}^{commit}" 2>/dev/null; then
        BASE="$VERCEL_GIT_PREVIOUS_SHA"
        echo "vercel-ignore: using verified VERCEL_GIT_PREVIOUS_SHA=$BASE"
    else
        echo "vercel-ignore: VERCEL_GIT_PREVIOUS_SHA=$VERCEL_GIT_PREVIOUS_SHA not in local history (shallow clone?)"
    fi
fi

if [ -z "$BASE" ]; then
    if git rev-parse --verify -q "HEAD~1" >/dev/null 2>&1; then
        BASE="HEAD~1"
        echo "vercel-ignore: using parent commit HEAD~1"
    else
        echo "vercel-ignore: no parent commit found (initial commit?) — building (fail open)"
        exit 1
    fi
fi

CHANGED_FILES=$(git diff --name-only --no-renames "$BASE" HEAD 2>/dev/null) || {
    echo "vercel-ignore: git diff failed — building (fail open)"
    exit 1
}

if [ -z "$CHANGED_FILES" ]; then
    echo "vercel-ignore: no changed files detected in diff — building (conservative)"
    exit 1
fi

echo "vercel-ignore: changed files between $BASE and HEAD:"
echo "$CHANGED_FILES" | sed 's/^/  /'

for FILE in $CHANGED_FILES; do
    for PATTERN in $RUNTIME_PATTERNS; do
        [ -z "$PATTERN" ] && continue
        if echo "$FILE" | grep -qE "$PATTERN"; then
            echo "vercel-ignore: runtime change detected: $FILE (matched $PATTERN) — proceeding with build"
            exit 1
        fi
    done
done

echo "vercel-ignore: all changed files are non-runtime (docs/eval/tests/offline) — skipping build"
exit 0
```

### 2. Created File: `tests/test_vercel_ignore_19.py`
A comprehensive 24-test deterministic fixture suite validating all positive, negative, and edge cases against isolated temporary Git repositories.

### 3. Proposed Update for `vercel.json` (Presented for Senior Review, Not Committed Unilaterally)
```diff
--- a/vercel.json
+++ b/vercel.json
@@ -1,6 +1,14 @@
 {
   "installCommand": "echo 'no install step: the build uses only the Python standard library, node and npm'",
   "buildCommand": "PYTHONPATH=src python3 scripts/fetch_tesseract_assets.py && PYTHONPATH=src python3 scripts/build_web_preview.py",
+  "ignoreCommand": "sh scripts/vercel-ignore.sh",
+  "git": {
+    "deploymentEnabled": {
+      "main": true,
+      "antigravity/*": false,
+      "claude/*": false
+    }
+  },
   "outputDirectory": "web_preview/dist",
   "cleanUrls": true,
   "headers": [
```

---

## 6. Deterministic Local Fixture Test Results

All 24 test cases in `tests/test_vercel_ignore_19.py` pass deterministically:

| Test Case | Scenario Description | Expected Exit | Result | Output Verification |
|---|---|:---:|:---:|---|
| `test_runtime_only_change` | Edit `src/foodscan/classify.py` | 1 | **PASSED** | "runtime change detected: src/foodscan/classify.py" |
| `test_resource_only_change` | Edit `src/foodscan/resources/lexicon.csv` | 1 | **PASSED** | "runtime change detected: src/foodscan/resources/lexicon.csv" |
| `test_docs_only_change` | Edit `README.md` and `evaluation/batch_1/README.md` | 0 | **PASSED** | "all changed files are non-runtime — skipping build" |
| `test_tests_only_change` | Edit `tests/test_something.py` | 0 | **PASSED** | "all changed files are non-runtime — skipping build" |
| `test_mixed_changes` | Edit `README.md` + `src/foodscan/normalise.py` | 1 | **PASSED** | "runtime change detected: src/foodscan/normalise.py" |
| `test_initial_commit_fail_open` | Root commit with no parent | 1 | **PASSED** | "no parent commit found (initial commit?) — building (fail open)" |
| `test_merge_release_with_runtime` | Merge commit introducing `src/foodscan/pipeline.py` | 1 | **PASSED** | "runtime change detected: src/foodscan/pipeline.py" |
| `test_merge_release_docs_only` | Merge commit introducing only `evaluation/notes.txt` | 0 | **PASSED** | "all changed files are non-runtime — skipping build" |
| `test_renamed_runtime_file` | `git mv web_preview/foodscan.js web_preview/engine.js` | 1 | **PASSED** | "runtime change detected" (`--no-renames` preserves detection) |
| `test_deleted_runtime_file` | Deleting `src/foodscan/legacy.py` | 1 | **PASSED** | "runtime change detected: src/foodscan/legacy.py" |
| `test_all_build_closure_files[template.html]` | Edit `web_preview/template.html` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[foodscan.js]` | Edit `web_preview/foodscan.js` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[worker-boot.js]` | Edit `web_preview/worker-boot.js` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[build_web_preview.py]` | Edit `scripts/build_web_preview.py` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[fetch_tesseract_assets.py]` | Edit `scripts/fetch_tesseract_assets.py` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[parity_check.py]` | Edit `scripts/parity_check.py` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[web_tables.py]` | Edit `scripts/web_tables.py` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[vercel-ignore.sh]` | Edit `scripts/vercel-ignore.sh` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[vercel.json]` | Edit `vercel.json` | 1 | **PASSED** | Build triggered |
| `test_all_build_closure_files[pyproject.toml]` | Edit `pyproject.toml` | 1 | **PASSED** | Build triggered |
| `test_offline_batch_script_skips_build` | Edit `scripts/oos_eval.py` | 0 | **PASSED** | Build skipped |
| `test_vercel_git_previous_sha_runtime` | Multi-commit range with runtime change | 1 | **PASSED** | Build triggered via `VERCEL_GIT_PREVIOUS_SHA` |
| `test_vercel_git_previous_sha_non_runtime` | Multi-commit range with docs/tests only | 0 | **PASSED** | Build skipped via `VERCEL_GIT_PREVIOUS_SHA` |
| `test_vercel_git_previous_sha_missing_in_shallow_clone` | Missing SHA falls back to `HEAD~1` | 0 | **PASSED** | Graceful fallback without crashing |

**Full repository regression status:**
* Parity check: `921/921 analyses identical between Python and JS` (0 regressions).
* Pytest suite: `2375 passed, 6 skipped, 5 xfailed in 75.71s` (0 failures).

---

## 7. Official Documentation References

1. **Vercel Ignored Build Step**:
   * https://vercel.com/docs/deployments/configure-a-build#ignored-build-step
   * Confirms exit code 0 skips the build, non-zero continues.
   * Confirms cancelled builds still consume deployment limits.
2. **Vercel System Environment Variables**:
   * https://vercel.com/docs/projects/environment-variables/system-environment-variables
   * Documents `VERCEL_GIT_PREVIOUS_SHA`, `VERCEL_GIT_COMMIT_SHA`, and shallow clone depth caveats.
3. **Vercel `git.deploymentEnabled` Configuration**:
   * https://vercel.com/docs/projects/project-configuration#git.deploymentenabled
   * Documents minimatch branch-level enabling/disabling to prevent deployment creation.
4. **Vercel Rate Limits**:
   * https://vercel.com/docs/limits#deployments
   * Details the 100 deployments per rolling 24-hour limit on Hobby plans.
