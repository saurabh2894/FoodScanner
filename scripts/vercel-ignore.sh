#!/bin/sh
# vercel-ignore.sh — Vercel Ignored Build Step for FoodScanner
#
# Called by Vercel via vercel.json "ignoreCommand".
# Exit 0 -> cancel build (skips build compute).
# Exit 1 -> proceed with build.
#
# IMPORTANT QUOTA DISTINCTION:
# Cancelling a build via exit 0 in an Ignored Build Step does NOT save a daily
# deployment slot against the Hobby plan 100 deployments/day cap.
# Vercel official documentation states:
# "Builds that the Ignored Build Step cancels still count toward deployment
# and concurrent build limits."
# The primary mechanism for preventing quota exhaustion from branch pushes
# is disabling preview deployments (via git.deploymentEnabled in vercel.json
# or Project Settings -> Git -> Deployment Branches).
# This script serves as Layer 2: suppressing redundant build compute when
# changes on an enabled branch are strictly non-runtime (docs, evals, tests).
#
# DESIGN: Fail open to build on any uncertainty.
# A redundant build is harmless; a skipped necessary build breaks production.

set -e

echo "vercel-ignore: checking for runtime-affecting changes..."

# ---------------------------------------------------------------------------
# Runtime path patterns — files whose changes affect the deployed web app.
# Dependency closure:
#   - Python classifier & data resources: src/foodscan/**
#   - Web app engine, HTML template, worker bootstrap: web_preview/**
#   - Build & verification scripts:
#       scripts/build_web_preview.py
#       scripts/fetch_tesseract_assets.py
#       scripts/parity_check.py
#       scripts/web_tables.py
#       scripts/vercel-ignore.sh
#   - Project manifests & hosting configuration:
#       vercel.json
#       pyproject.toml
#       requirements*.txt
#       package.json
#       package-lock.json
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 1. Determine base commit for diff.
#    Priority 1: VERCEL_GIT_PREVIOUS_SHA (if provided by Vercel and present)
#    Priority 2: HEAD~1 (first parent of current commit)
#    Fallback: Fail open -> build (exit 1)
# ---------------------------------------------------------------------------
BASE=""

if [ -n "${VERCEL_GIT_PREVIOUS_SHA:-}" ]; then
    # Verify the previous commit actually exists in this checkout
    # (Vercel shallow clone --depth=10 may not contain older SHAs)
    if git cat-file -e "${VERCEL_GIT_PREVIOUS_SHA}^{commit}" 2>/dev/null; then
        BASE="$VERCEL_GIT_PREVIOUS_SHA"
        echo "vercel-ignore: using verified VERCEL_GIT_PREVIOUS_SHA=$BASE"
    else
        echo "vercel-ignore: VERCEL_GIT_PREVIOUS_SHA=$VERCEL_GIT_PREVIOUS_SHA not in local history (shallow clone?)"
    fi
fi

if [ -z "$BASE" ]; then
    # Check if HEAD~1 exists (parent of current commit)
    if git rev-parse --verify -q "HEAD~1" >/dev/null 2>&1; then
        BASE="HEAD~1"
        echo "vercel-ignore: using parent commit HEAD~1"
    else
        echo "vercel-ignore: no parent commit found (initial commit?) — building (fail open)"
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# 2. Compute diff.
#    Use --no-renames so that renamed/deleted runtime files show their original
#    path, preventing evasion if a runtime file is renamed to a docs path.
# ---------------------------------------------------------------------------
CHANGED_FILES=$(git diff --name-only --no-renames "$BASE" HEAD 2>/dev/null) || {
    echo "vercel-ignore: git diff failed — building (fail open)"
    exit 1
}

# If diff is empty (e.g. empty commit, amend with identical tree): conservative -> build
if [ -z "$CHANGED_FILES" ]; then
    echo "vercel-ignore: no changed files detected in diff — building (conservative)"
    exit 1
fi

echo "vercel-ignore: changed files between $BASE and HEAD:"
echo "$CHANGED_FILES" | sed 's/^/  /'

# ---------------------------------------------------------------------------
# 3. Check each changed file against runtime patterns.
#    If ANY file matches a runtime pattern -> exit 1 (build).
#    If ALL files are non-runtime -> exit 0 (skip build).
# ---------------------------------------------------------------------------
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
