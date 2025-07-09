# --- Suppress Git line-ending warnings everywhere ---
suppress_git_warnings() {
  grep -v 'LF will be replaced by CRLF' | grep -v 'CRLF will be replaced by LF' | grep -v 'warning: in the working copy'
}

set -euo pipefail

trap 'echo -e "\033[1;31m[ERROR] Script failed at line $LINENO. Last command: $BASH_COMMAND\033[0m" >&2' ERR



# --- -Style Banner (no rain effect) ---
echo -e "\033[40m\033[1;32m"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║   ShieldCraft AI Commit & CI Preflight Utility ( Mode)               ║"
echo "╠══════════════════════════════════════════════════════════════════════╣"
echo "║  Project: ShieldCraft AI | Author: $(git config user.name)                               ║"
echo "║  Hardened, DRY, and production-grade commit workflow for MLOps       ║"
echo "║  All automation is cross-platform, CI-friendly, and self-healing     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "\033[0m\n"


# --- Set repo root and debug log file (minimal output) ---
REPO_ROOT="$(git rev-parse --show-toplevel)"
DEBUG_LOG_FILE="$REPO_ROOT/commit_nox_debug.log"
echo "--- $(date) ---" >"$DEBUG_LOG_FILE"
cd "$REPO_ROOT"





# --- Automatically stage all changes (silent unless staged) ---
if ! git diff --quiet; then
    git add . 2>&1 | grep -v 'LF will be replaced by CRLF' | grep -v 'CRLF will be replaced by LF' | grep -v 'warning: in the working copy' || true
    echo "Auto-staged changes for commit." >> "$DEBUG_LOG_FILE"
fi


# --- Warn if large/secret files are staged (minimal output) ---
if git ls-files | grep -E '\.(env|pem|key|sqlite3|db|csv|tsv|parquet|h5|hdf5|npz|npy|sav|dat|tmp|log|pkl)$' | grep -vE 'docs-site|notebooks' | grep -vE '(^$)' >/tmp/large_or_secret_files.txt; then
    echo "Warning: Large or secret files staged. See /tmp/large_or_secret_files.txt" >> "$DEBUG_LOG_FILE"
    cat /tmp/large_or_secret_files.txt
    read -rp "Continue anyway? [y/N]: " cont_secrets
    cont_secrets=${cont_secrets:-N}
    if [[ ! "$cont_secrets" =~ ^[Yy]$ ]]; then
        echo "Aborting commit script." >&2
        exit 1
    fi
fi


# --- Fast-forward merge (minimal output) ---
git fetch origin main >/dev/null 2>&1
if ! git merge --ff-only origin/main >/dev/null 2>&1; then
    echo "Fast-forward merge from origin/main failed. Please resolve conflicts manually before proceeding." >&2
    exit 1
fi



HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOKS_INSTALLED_MARKER="$HOOKS_DIR/.precommit_hooks_installed"


# --- Poetry/Nox preflight (self-healing) ---
if ! command -v poetry >/dev/null 2>&1; then
    echo "Poetry is not installed. Attempting self-heal..." >&2
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v poetry >/dev/null 2>&1; then
        echo "[ERROR] Poetry installation failed. Please install manually: https://python-poetry.org/docs/#installation" >&2
        exit 1
    fi
    echo "[INFO] Poetry installed successfully." >&2
fi
if ! poetry run nox --version >/dev/null 2>&1; then
    echo "Nox is not installed in the Poetry environment. Attempting self-heal..." >&2
    poetry add --group dev nox@2023.4.22
    if ! poetry run nox --version >/dev/null 2>&1; then
        echo "[ERROR] Nox installation failed in Poetry environment. Please run: poetry add --group dev nox@2023.4.22" >&2
        exit 1
    fi
    echo "[INFO] Nox installed successfully in Poetry environment." >&2
fi

# --- Ensure pre-commit hooks are always installed and up-to-date (idempotent) ---
NEED_HOOKS_INSTALL=0
if [ ! -f "$HOOKS_INSTALLED_MARKER" ]; then
    NEED_HOOKS_INSTALL=1
fi
if [ ! -x "$HOOKS_DIR/pre-commit" ] || [ ! -x "$HOOKS_DIR/pre-push" ]; then
    NEED_HOOKS_INSTALL=1
fi
# Check if the installed hooks are out of date (compare hash of .pre-commit-config.yaml and marker)
if [ -f "$HOOKS_INSTALLED_MARKER" ]; then
    PRECOMMIT_CONFIG_HASH=$(sha256sum "$REPO_ROOT/.pre-commit-config.yaml" | awk '{print $1}')
    MARKER_HASH=$(cat "$HOOKS_INSTALLED_MARKER" 2>/dev/null | head -n1)
    if [ "$PRECOMMIT_CONFIG_HASH" != "$MARKER_HASH" ]; then
        NEED_HOOKS_INSTALL=1
    fi
fi
if [ "$NEED_HOOKS_INSTALL" -eq 1 ]; then
    poetry run pre-commit install --hook-type pre-commit --hook-type pre-push >/dev/null 2>&1 || true
    if [ -d "$HOOKS_DIR" ]; then
        for hook in "$HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-push"; do
            [ -f "$hook" ] && chmod +x "$hook"
            [ -f "$hook" ] && dos2unix "$hook" 2>>"$DEBUG_LOG_FILE" || true
        done
    fi
    # Store hash of .pre-commit-config.yaml in marker for idempotency
    sha256sum "$REPO_ROOT/.pre-commit-config.yaml" | awk '{print $1}' > "$HOOKS_INSTALLED_MARKER"
fi




# --- Check poetry.lock freshness, auto-heal if needed (relaxed) ---

# --- Check poetry.lock freshness (minimal output) ---
if ! poetry lock --check >/dev/null 2>&1; then
    poetry lock >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "CRITICAL: 'poetry lock' failed. Please fix lockfile issues and try again." >&2
        read -rp "Continue anyway? [y/N]: " cont_poetry
        cont_poetry=${cont_poetry:-N}
        if [[ ! "$cont_poetry" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        git add poetry.lock
        echo "Auto-healed poetry.lock and staged." >> "$DEBUG_LOG_FILE"
    fi
fi



# --- Poetry lock check complete (minimal output) ---
echo "Poetry lock check complete." >> "$DEBUG_LOG_FILE"


# --- Nox/Poetry/Node preflight (minimal, DRY, no duplication) ---


# 1. Check Nox version (fail fast if not correct)
EXPECTED_NOX_VERSION="2023.4.22"
NOX_VERSION_OUTPUT=$(python3 scripts/pre_nox.py -- --version 2>&1)
ACTUAL_NOX_VERSION=$(echo "$NOX_VERSION_OUTPUT" | head -n 1 | awk '{print $NF}' | tr -d '\r\n')
if [[ -z "$ACTUAL_NOX_VERSION" || "$ACTUAL_NOX_VERSION" != "$EXPECTED_NOX_VERSION" ]]; then
    echo -e "\033[1;31m🟥 Poetry-managed Nox version is '$ACTUAL_NOX_VERSION', expected '$EXPECTED_NOX_VERSION'.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    echo -e "\033[1;33mTIP: Run 'poetry add --group dev nox@$EXPECTED_NOX_VERSION' to fix.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

# 2. Run npm preflight if needed
if command -v node >/dev/null 2>&1 && [ -f scripts/pre_npm.py ]; then
    if ! python3 scripts/pre_npm.py 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
        echo -e "\033[1;41m\033[1;97m🟥 npm preflight failed. Please fix npm issues and try again.\033[0m" | tee -a "$DEBUG_LOG_FILE"
        exit 1
    fi
fi


# 3. Run auto-formatting (fail fast)
echo -e "\033[40m\033[1;32mRunning: format session...\033[0m"
if ! python3 scripts/pre_nox.py format 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo -e "\033[1;31m🟥 Auto-formatting failed. Please fix formatting issues and try again.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi


# 4. Run the single orchestration point for all checks (commit_flow)
export PYTHONUNBUFFERED=1
if ! python3 scripts/pre_nox.py commit_flow 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
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
esac


# --- Robust commit message input (multi-line and single-line safe) ---
echo "Enter commit message. End with an empty line (press Enter twice):"
commit_msg=""
while IFS= read -r line; do
    [ -z "$line" ] && break
    commit_msg+="$line\n"
done
commit_msg="${commit_msg%\\n}"
if [ -z "$commit_msg" ]; then
    echo "Commit message cannot be empty."
    exit 1
fi
full_commit_msg="$commit_type: $commit_msg"
tmp_commit_file=".git/COMMIT_EDITMSG"
echo -e "$full_commit_msg" > "$tmp_commit_file"

# --- Auto-stage all changes again before commit to catch late modifications ---
git add . 2>&1 | suppress_git_warnings || true
if ! poetry run git commit -F "$tmp_commit_file" 2>&1 | suppress_git_warnings; then
    echo -e "\033[1;31m🟥 Commit failed.\033[0m"
    rm -f "$tmp_commit_file"
    exit 1
fi
rm -f "$tmp_commit_file"

CHECKLIST_SCRIPT_PATH="$REPO_ROOT/.github/scripts/update_checklist_progress.py"
if poetry run python "$CHECKLIST_SCRIPT_PATH" | grep -q 'updated'; then
    git add "$REPO_ROOT/docs-site/docs/checklist.md" "$REPO_ROOT/README.md" 2>&1 | suppress_git_warnings
    if ! poetry run git commit -m "chore: update checklist progress bar" 2>&1 | suppress_git_warnings; then
        echo -e "\033[1;31m🟥 Auto-commit of checklist progress bar failed.\033[0m"
        exit 1
    fi
fi


# --- Run the main orchestration session (commit_flow) instead of 'all' ---
if ! python3 scripts/pre_nox.py commit_flow 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
    echo -e "\033[1;31m🟥 Final Nox commit_flow session failed after all commits. Please fix issues manually.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    exit 1
fi

read -rp "All checks passed. Do you want to push to remote now? [Y/n]: " do_push
do_push=${do_push:-Y}
if [[ "$do_push" =~ ^[Yy]$ ]]; then
    if ! git pull --rebase 2>&1 | suppress_git_warnings; then
        echo -e "\033[1;31m🟥 Pull (rebase) failed. Resolve conflicts before pushing.\033[0m"
        exit 1
    fi
    if ! poetry run git push 2>&1 | suppress_git_warnings; then
        echo -e "\033[1;31m🟥 Push failed.\033[0m"
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
            git push origin "$tag_name" 2>&1 | suppress_git_warnings
            echo -e "\033[1;32mTag '$tag_name' created and pushed.\033[0m"
        else
            echo "Tag name cannot be empty. Skipping tag."
        fi
    fi
else
    echo -e "\n\033[1;34mPush skipped. You can push manually with 'git push' when ready.\033[0m\n"
fi

echo -e "\n\033[1;36mMonitor CI for a few cycles to ensure all jobs pass and no edge cases are missed.\033[0m\n"
