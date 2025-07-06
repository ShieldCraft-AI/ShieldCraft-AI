
set -euo pipefail

# --- Professional, Polished Banner ---
echo -e "\n\033[1;36m╔══════════════════════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[1;36m║         🛡️  ShieldCraft AI Commit & CI Preflight Utility             ║\033[0m"
echo -e "\033[1;36m╠══════════════════════════════════════════════════════════════════════╣\033[0m"
echo -e "\033[1;36m║  Hardened, DRY, and production-grade commit workflow for MLOps       ║\033[0m"
echo -e "\033[1;36m║  All automation is cross-platform, CI-friendly, and self-healing     ║\033[0m"
echo -e "\033[1;36m║  Project: ShieldCraft AI | Author: $(git config user.name)                     ║\033[0m"
echo -e "\033[1;36m╚══════════════════════════════════════════════════════════════════════╝\033[0m\n"

# --- Set repo root and debug log file ---
REPO_ROOT="$(git rev-parse --show-toplevel)"
DEBUG_LOG_FILE="$REPO_ROOT/commit_nox_debug.log"
echo "--- $(date) ---" >"$DEBUG_LOG_FILE"
cd "$REPO_ROOT"


# --- Automatically stage all changes ---
if ! git diff --quiet; then
    echo "Auto-staging all changes for commit..." | tee -a "$DEBUG_LOG_FILE"
    git add .
fi

if git ls-files | grep -E '\.(env|pem|key|sqlite3|db|csv|tsv|parquet|h5|hdf5|npz|npy|sav|dat|tmp|log|pkl)$' | grep -vE 'docs-site|notebooks' | grep -vE '(^$)' >/tmp/large_or_secret_files.txt; then
    cat /tmp/large_or_secret_files.txt | tee -a "$DEBUG_LOG_FILE"
    read -rp "Continue anyway? [y/N]: " cont_secrets
    cont_secrets=${cont_secrets:-N}
    if [[ ! "$cont_secrets" =~ ^[Yy]$ ]]; then
        echo "Aborting commit script." | tee -a "$DEBUG_LOG_FILE"
        exit 1
    fi
fi

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




# --- Check poetry.lock freshness, auto-heal if needed (relaxed) ---
if ! poetry lock --check 2>/dev/null; then
    echo "🟨 WARNING: poetry.lock is out of date with pyproject.toml. Running 'poetry lock' to heal..." | tee -a "$DEBUG_LOG_FILE"
    poetry_lock_output=$(poetry lock 2>&1)
    poetry_lock_status=$?
    echo "$poetry_lock_output" | tee -a "$DEBUG_LOG_FILE"
    if [ $poetry_lock_status -ne 0 ]; then
        echo "🟥 CRITICAL: 'poetry lock' failed. Please fix lockfile issues and try again." | tee -a "$DEBUG_LOG_FILE"
        read -rp "Continue anyway? [y/N]: " cont_poetry
        cont_poetry=${cont_poetry:-N}
        if [[ ! "$cont_poetry" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        git add poetry.lock
        echo "Auto-healed poetry.lock and staged. Continuing..." | tee -a "$DEBUG_LOG_FILE"
    fi
fi



echo -e "\n\033[1;36m╔══════════════════════════════════════════════╗\033[0m" | tee -a "$DEBUG_LOG_FILE"
echo -e "\033[1;36m║        🚀 Poetry lock check complete         ║\033[0m" | tee -a "$DEBUG_LOG_FILE"
echo -e "\033[1;36m╚══════════════════════════════════════════════╝\033[0m\n" | tee -a "$DEBUG_LOG_FILE"

# --- Use preflight script for all Nox session invocations ---

EXPECTED_NOX_VERSION="2023.4.22"
NOX_VERSION_OUTPUT=$(python scripts/pre_nox.py -- --version 2>&1)
ACTUAL_NOX_VERSION=$(echo "$NOX_VERSION_OUTPUT" | head -n 1 | awk '{print $NF}' | tr -d '\r\n')
echo -e "\n\033[1;35m╔══════════════════════════════════════════════╗\033[0m" | tee -a "$DEBUG_LOG_FILE"
echo -e "\033[1;35m║      🧪 Poetry-managed Nox version check     ║\033[0m" | tee -a "$DEBUG_LOG_FILE"
echo -e "\033[1;35m╠══════════════════════════════════════════════╣\033[0m" | tee -a "$DEBUG_LOG_FILE"
echo -e "\033[1;35m║  Expected: $EXPECTED_NOX_VERSION"                              ║
echo -e "\033[1;35m║  Actual:   $ACTUAL_NOX_VERSION"                                ║
echo -e "\033[1;35m╚══════════════════════════════════════════════╝\033[0m\n" | tee -a "$DEBUG_LOG_FILE"

if [[ -z "$ACTUAL_NOX_VERSION" ]]; then
    echo -e "\033[1;31m🟥 CRITICAL: Could not detect Poetry-managed Nox version (got empty string).\033[0m" | tee -a "$DEBUG_LOG_FILE"
    echo -e "\033[1;33mTIP: Try running 'poetry install' and ensure Nox is in your dev dependencies.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi



# --- Use preflight script for all Nox session invocations ---

if [[ "$ACTUAL_NOX_VERSION" != "$EXPECTED_NOX_VERSION" ]]; then
    echo -e "\033[1;31m🟥 CRITICAL: Poetry-managed Nox version is '$ACTUAL_NOX_VERSION', expected '$EXPECTED_NOX_VERSION'.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    echo -e "\033[1;33mTIP: Run 'poetry add --group dev nox@$EXPECTED_NOX_VERSION' to fix.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

# --- Run npm preflight for all Node.js projects (docs-site, ui, etc.) ---

if command -v node >/dev/null 2>&1; then
    if [ -f scripts/pre_npm.py ]; then
        echo -e "\n\033[1;33m╔═══════════════════════════════════════════════════════╗\033[0m" | tee -a "$DEBUG_LOG_FILE"
        echo -e "\033[1;33m║   🟡 Running npm preflight for all Node.js projects...║\033[0m" | tee -a "$DEBUG_LOG_FILE"
        echo -e "\033[1;33m╚═══════════════════════════════════════════════════════╝\033[0m\n" | tee -a "$DEBUG_LOG_FILE"
        if ! python scripts/pre_npm.py 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
            echo -e "\033[1;41m\033[1;97m🟥 npm preflight failed. Please fix npm issues and try again.\033[0m" | tee -a "$DEBUG_LOG_FILE"
            echo -e "\033[1;31m╔══════════════════════════════════════════════════════════════════════╗\033[0m" | tee -a "$DEBUG_LOG_FILE"
            echo -e "\033[1;31m║  💡 Try running: npm install (in each Node.js project directory)    ║\033[0m" | tee -a "$DEBUG_LOG_FILE"
            echo -e "\033[1;31m╚══════════════════════════════════════════════════════════════════════╝\033[0m" | tee -a "$DEBUG_LOG_FILE"
            exit 1
        fi
    fi
fi

if ! python scripts/pre_nox.py format 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo -e "\033[1;31m🟥 Auto-formatting failed. Please fix formatting issues and try again.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

export PYTHONUNBUFFERED=1
if ! python scripts/pre_nox.py commit_flow 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo -e "\033[1;31m🟥 Nox commit_flow session failed. No commit performed.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    git reset
    exit 1
fi
unset PYTHONUNBUFFERED

# --- Commit message and tagging workflow ---
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
1 | feat) commit_type="feat" ;;
2 | fix) commit_type="fix" ;;
3 | chore) commit_type="chore" ;;
4 | docs) commit_type="docs" ;;
5 | style) commit_type="style" ;;
6 | refactor) commit_type="refactor" ;;
7 | perf) commit_type="perf" ;;
8 | test) commit_type="test" ;;
9 | ci) commit_type="ci" ;;
10 | build) commit_type="build" ;;
11 | revert) commit_type="revert" ;;
*) commit_type="feat" ;;
fi

read -rp "Enter commit message: " commit_msg
if [ -z "$commit_msg" ]; then
    echo "Commit message cannot be empty."
    exit 1
fi
full_commit_msg="$commit_type: $commit_msg"
if ! poetry run git commit -m "$full_commit_msg"; then
    echo "Commit failed."
    exit 1
fi

CHECKLIST_SCRIPT_PATH="$REPO_ROOT/.github/scripts/update_checklist_progress.py"
if poetry run python "$CHECKLIST_SCRIPT_PATH" | grep -q 'updated'; then
    git add "$REPO_ROOT/docs-site/docs/checklist.md" "$REPO_ROOT/README.md"
    if ! poetry run git commit -m "chore: update checklist progress bar"; then
        echo "Auto-commit of checklist progress bar failed."
        exit 1
    fi
fi

if ! python scripts/pre_nox.py all 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo -e "\033[1;31m🟥 Final Nox all session failed after all commits. Please fix issues manually.\033[0m" | tee -a "$DEBUG_LOG_FILE"
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
    echo -e "\n\033[1;32m╔══════════════════════════════════════════════════════════════════════╗\033[0m"
    echo -e "\033[1;32m║  ✅ All changes committed, version bumped, checklist updated, and pushed successfully. ║\033[0m"
    echo -e "\033[1;32m╚══════════════════════════════════════════════════════════════════════╝\033[0m\n"

    # --- Tagging major architectural improvements ---
    read -rp "Tag this commit as a release? [y/N]: " do_tag
    do_tag=${do_tag:-N}
    if [[ "$do_tag" =~ ^[Yy]$ ]]; then
        read -rp "Enter tag name (e.g., v0.9.0): " tag_name
        if [ -n "$tag_name" ]; then
            git tag -a "$tag_name" -m "Centralized dependency preflight for Poetry and npm; session/CI cleanup"
            git push origin "$tag_name"
            echo "Tag '$tag_name' created and pushed."
        else
            echo "Tag name cannot be empty. Skipping tag."
        fi
    fi
else
    echo -e "\n\033[1;34mPush skipped. You can push manually with 'git push' when ready.\033[0m\n"
fi

echo -e "\n\033[1;36mMonitor CI for a few cycles to ensure all jobs pass and no edge cases are missed.\033[0m\n"
