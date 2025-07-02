set -euo pipefail

# --- Set repo root and debug log file ---
REPO_ROOT="$(git rev-parse --show-toplevel)"
DEBUG_LOG_FILE="$REPO_ROOT/commit_nox_debug.log"
echo "--- $(date) ---" > "$DEBUG_LOG_FILE"
cd "$REPO_ROOT"

if ! git diff --quiet; then
    git status --short | tee -a "$DEBUG_LOG_FILE"
    read -rp "Continue and stage all changes? [Y/n]: " cont_stage
    cont_stage=${cont_stage:-Y}
    if [[ ! "$cont_stage" =~ ^[Yy]$ ]]; then
        echo "Aborting commit script." | tee -a "$DEBUG_LOG_FILE"
        exit 1
    fi
fi

if git ls-files | grep -E '\.(env|pem|key|sqlite3|db|csv|tsv|parquet|h5|hdf5|npz|npy|sav|dat|tmp|log|pkl)$' | grep -vE 'docs-site|notebooks' | grep -vE '(^$)' > /tmp/large_or_secret_files.txt; then
    cat /tmp/large_or_secret_files.txt | tee -a "$DEBUG_LOG_FILE"
    read -rp "Continue anyway? [y/N]: " cont_secrets
    cont_secrets=${cont_secrets:-N}
    if [[ ! "$cont_secrets" =~ ^[Yy]$ ]]; then
        echo "Aborting commit script." | tee -a "$DEBUG_LOG_FILE"
        exit 1
    fi
fi

## Removed .env staged file block as requested

git fetch origin main 2>&1 | tee -a "$DEBUG_LOG_FILE"
if ! git merge --ff-only origin/main 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo "Fast-forward merge from origin/main failed. Please resolve conflicts manually before proceeding." | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOKS_INSTALLED_MARKER="$HOOKS_DIR/.precommit_hooks_installed"

if ! command -v poetry >/dev/null 2>&1; then
    echo "Poetry is not installed. Please install Poetry: https://python-poetry.org/docs/#installation" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi



LESS_SECURE_COMMIT=0
read -rp "Use FAST COMMIT mode (skip slow/strict checks)? [Y/n]: " fast_commit_choice
fast_commit_choice=${fast_commit_choice:-Y}
if [[ "$fast_commit_choice" =~ ^[Yy]$ ]]; then
    LESS_SECURE_COMMIT=1
fi







if ! poetry run nox --version 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo "Nox is not installed in the Poetry environment. Please run: poetry add --group dev nox@2023.4.22" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

if [ ! -f "$HOOKS_INSTALLED_MARKER" ] || [ ! -x "$HOOKS_DIR/pre-commit" ] || [ ! -x "$HOOKS_DIR/pre-push" ]; then
    poetry run pre-commit install --hook-type pre-commit --hook-type pre-push 2>&1 | tee -a "$DEBUG_LOG_FILE" || true
    if [ -d "$HOOKS_DIR" ]; then
        for hook in "$HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-push"; do
            [ -f "$hook" ] && chmod +x "$hook"
            [ -f "$hook" ] && dos2unix "$hook" 2>>"$DEBUG_LOG_FILE" || true
        done
    fi
    touch "$HOOKS_INSTALLED_MARKER"
fi


git add .









EXPECTED_NOX_VERSION="2023.4.22"
# Robust version detection for cross-shell compatibility
ACTUAL_NOX_VERSION=$(poetry run nox --version 2>&1 | head -n 1 | awk '{print $NF}' | tr -d '\r\n')
if [[ -z "$ACTUAL_NOX_VERSION" ]]; then
    echo "🟥 CRITICAL: Could not detect Poetry-managed Nox version (got empty string)."
    exit 1
fi
if [[ "$ACTUAL_NOX_VERSION" != "$EXPECTED_NOX_VERSION" ]]; then
    echo "🟥 CRITICAL: Poetry-managed Nox version is '$ACTUAL_NOX_VERSION', expected '$EXPECTED_NOX_VERSION'."
    exit 1
fi



# Use correct Nox invocation for your version (no --session, use -s)
if ! poetry run nox -s format 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo "Auto-formatting failed. Please fix formatting issues and try again." | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

export PYTHONUNBUFFERED=1
if [[ $LESS_SECURE_COMMIT -eq 1 ]]; then
    if ! poetry run nox -s commit_flow -- --fast 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
        echo "Nox commit_flow session failed. No commit performed." | tee -a "$DEBUG_LOG_FILE"
        git reset
        exit 1
    fi
else
    if ! poetry run nox -s commit_flow 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
        echo "Nox commit_flow session failed. No commit performed." | tee -a "$DEBUG_LOG_FILE"
        git reset
        exit 1
    fi
fi
unset PYTHONUNBUFFERED



branch_name=$(git rev-parse --abbrev-ref HEAD)
if ! [[ "$branch_name" =~ ^(feature|bugfix|chore|docs|refactor|test|ci|build|perf|revert)/ ]]; then
    read -rp "Branch name '$branch_name' does not follow convention (e.g., feature/xyz, bugfix/abc). Continue anyway? [Y/n]: " branch_ok
    branch_ok=${branch_ok:-Y}
    if [[ ! "$branch_ok" =~ ^[Yy]$ ]]; then
        echo "Aborting commit script."
        exit 1
    fi
fi

echo "Select commit type:"
echo "  1) feat (default)"
echo "  2) fix"
echo "  3) chore"
echo "  4) docs"
echo "  5) style"
echo "  6) refactor"
echo "  7) perf"
echo "  8) test"
echo "  9) ci"
echo " 10) build"
echo " 11) revert"
read -rp "Enter the number for commit type [default: 1]: " commit_type_num
commit_type_num=${commit_type_num:-1}
case $commit_type_num in
    1|feat) commit_type="feat" ;;
    2|fix) commit_type="fix" ;;
    3|chore) commit_type="chore" ;;
    4|docs) commit_type="docs" ;;
    5|style) commit_type="style" ;;
    6|refactor) commit_type="refactor" ;;
    7|perf) commit_type="perf" ;;
    8|test) commit_type="test" ;;
    9|ci) commit_type="ci" ;;
    10|build) commit_type="build" ;;
    11|revert) commit_type="revert" ;;
    *) commit_type="feat" ;;
esac

read -rp "Enter your commit message: " commit_msg
if [ -z "$commit_msg" ]; then
    echo "Commit message cannot be empty."; exit 1
fi
full_commit_msg="$commit_type: $commit_msg"
if ! poetry run git commit -m "$full_commit_msg"; then
    echo "Commit failed."; exit 1
fi

CURRENT_VERSION=$(poetry version -s)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
echo "Current project version: $CURRENT_VERSION"
echo "  1) Major ($MAJOR)\n  2) Minor ($MINOR)\n  3) Patch ($PATCH) (default)"
read -rp "Which part of the version would you like to increment? [Major/Minor/Patch, default: 3]: " version_part
version_part=${version_part:-3}
if [ "$version_part" = "1" ]; then
    MAJOR=$((MAJOR+1)); MINOR=0; PATCH=0
elif [ "$version_part" = "2" ]; then
    MINOR=$((MINOR+1)); PATCH=0
elif [ "$version_part" = "3" ]; then
    PATCH=$((PATCH+1))
fi
NEW_VERSION="$MAJOR.$MINOR.$PATCH"
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    poetry version "$NEW_VERSION"
    git add pyproject.toml
    if ! poetry run git commit -m "chore: bump version to $NEW_VERSION"; then
        echo "Auto-commit of version bump failed."
        exit 1
    fi
fi

CHECKLIST_SCRIPT_PATH="$REPO_ROOT/.github/scripts/update_checklist_progress.py"
if poetry run python "$CHECKLIST_SCRIPT_PATH" | grep -q 'updated'; then
    git add "$REPO_ROOT/docs-site/docs/checklist.md" "$REPO_ROOT/README.md"
    if ! poetry run git commit -m "chore: update checklist progress bar"; then
        echo "Auto-commit of checklist progress bar failed."
        exit 1
    fi
fi






if ! poetry run nox -s all 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo "Final Nox all session failed after all commits. Please fix issues manually." | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

read -rp "All checks passed. Do you want to push to remote now? [Y/n]: " do_push
do_push=${do_push:-Y}
if [[ "$do_push" =~ ^[Yy]$ ]]; then
    if ! git pull --rebase; then
        echo "Pull (rebase) failed. Resolve conflicts before pushing."
        exit 1
    fi
    if ! poetry run git push; then
        echo "Push failed."
        exit 1
    fi
    echo "All changes committed, version bumped, checklist updated, and pushed successfully."
else
    echo "Push skipped. You can push manually with 'git push' when ready."
fi
