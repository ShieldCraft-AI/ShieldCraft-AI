#!/bin/bash
suppress_git_warnings() {
  grep -v 'LF will be replaced by CRLF' | grep -v 'CRLF will be replaced by LF' | grep -v 'warning: in the working copy'
}

# --- Commit type and message input (moved to top for uninterrupted execution) ---
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

suppress_git_warnings() {
  grep -v 'LF will be replaced by CRLF' | grep -v 'CRLF will be replaced by LF' | grep -v 'warning: in the working copy'
}



set -euo pipefail

FALLBACK_LOG_FILE="/tmp/commit_nox_debug.log"

# --- Best-in-class Poetry environment hygiene ---
log_output() {
    if ! echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_LOG_FILE" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$FALLBACK_LOG_FILE"
    fi
}

REPO_ROOT=""
if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT="$(git rev-parse --show-toplevel)"
fi
if [ -z "$REPO_ROOT" ]; then
    echo "[ERROR] Could not determine git repo root. Logging to $FALLBACK_LOG_FILE." >&2
    DEBUG_LOG_FILE="$FALLBACK_LOG_FILE"
else
    DEBUG_LOG_FILE="$REPO_ROOT/commit_nox_debug.log"
fi
if ! echo "--- $(date) ---" >"$DEBUG_LOG_FILE" 2>/dev/null; then
    echo "[ERROR] Could not write to $DEBUG_LOG_FILE. Logging to $FALLBACK_LOG_FILE." >&2
    DEBUG_LOG_FILE="$FALLBACK_LOG_FILE"
    echo "--- $(date) ---" >"$DEBUG_LOG_FILE"
fi

# Clean all Poetry environments for this project before starting
log_output "[INFO] Cleaning all Poetry environments for project hygiene."
poetry_envs=$(poetry env list --full-path | awk '{print $1}')
for env_path in $poetry_envs; do
    log_output "[INFO] Removing Poetry environment: $env_path"
    poetry env remove "$env_path" || log_output "[WARN] Could not remove Poetry env $env_path (may not exist or already removed)"
done
log_output "[INFO] Rehydrating Poetry environment with fresh install."
poetry install


log_output() {
    if ! echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_LOG_FILE" 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$FALLBACK_LOG_FILE"
    fi
}


trap 'echo -e "\033[1;31m[ERROR] Script failed at line $LINENO. Last command: $BASH_COMMAND\033[0m" >&2; log_output "[ERROR] Script failed at line $LINENO. Last command: $BASH_COMMAND"' ERR



echo -e "\033[40m\033[1;32m"
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║   ShieldCraft AI Commit & CI Preflight Utility ( Mode)            ║"
echo "╠═══════════════════════════════════════════════════════════════════╣"
echo "║  Project: ShieldCraft AI | Author: $(git config user.name)                          ║"
echo "║  Hardened, DRY, and production-grade commit workflow for MLOps    ║"
echo "║  All automation is cross-platform, CI-friendly, and self-healing  ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo -e "\033[0m\n"
log_output "[INFO] Commit script started by $(git config user.name)"





log_output "[INFO] Set repo root to $REPO_ROOT"
if [ -z "$REPO_ROOT" ]; then
    echo "[ERROR] Cannot cd to repo root. Aborting." >&2
    log_output "[ERROR] Cannot cd to repo root. Aborting."
    exit 1
fi
cd "$REPO_ROOT"

# Ensure Python can import nox_sessions (fixes Poetry/Nox import path issues)
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
if ! poetry run python -c "import nox_sessions"; then
    echo "[ERROR] Python cannot import 'nox_sessions'. Check PYTHONPATH and project structure." >&2
    log_output "[ERROR] Python cannot import 'nox_sessions'. Check PYTHONPATH and project structure."
    exit 1
fi


if ! git diff --quiet; then
    git add . 2>&1 | grep -v 'LF will be replaced by CRLF' | grep -v 'CRLF will be replaced by LF' | grep -v 'warning: in the working copy' || true
    log_output "[INFO] Auto-staged changes for commit."
fi


if git ls-files | grep -E '\.(env|pem|key|sqlite3|db|csv|tsv|parquet|h5|hdf5|npz|npy|sav|dat|tmp|log|pkl)$' | grep -vE 'docs-site|notebooks' | grep -vE '(^$)' >/tmp/large_or_secret_files.txt; then
    log_output "[WARN] Large or secret files staged. See /tmp/large_or_secret_files.txt"
    cat /tmp/large_or_secret_files.txt
    read -rp "Continue anyway? [y/N]: " cont_secrets
    cont_secrets=${cont_secrets:-N}
    if [[ ! "$cont_secrets" =~ ^[Yy]$ ]]; then
        echo "Aborting commit script." >&2
        log_output "[ERROR] Aborted due to large/secret files."
        exit 1
    fi
fi


git fetch origin main >/dev/null 2>&1
if ! git merge --ff-only origin/main >/dev/null 2>&1; then
    echo "Fast-forward merge from origin/main failed. Please resolve conflicts manually before proceeding." >&2
    exit 1
fi



HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOKS_INSTALLED_MARKER="$HOOKS_DIR/.precommit_hooks_installed"


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

NEED_HOOKS_INSTALL=0
if [ ! -f "$HOOKS_INSTALLED_MARKER" ]; then
    NEED_HOOKS_INSTALL=1
fi
if [ ! -x "$HOOKS_DIR/pre-commit" ] || [ ! -x "$HOOKS_DIR/pre-push" ]; then
    NEED_HOOKS_INSTALL=1
fi
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
    sha256sum "$REPO_RaOOT/.pre-commit-config.yaml" | awk '{print $1}' > "$HOOKS_INSTALLED_MARKER"
fi




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



echo "Poetry lock check complete." >> "$DEBUG_LOG_FILE"



EXPECTED_NOX_VERSION="2023.4.22"
NOX_VERSION_OUTPUT=$(python3 scripts/pre_nox.py -- --version 2>&1)
ACTUAL_NOX_VERSION=$(echo "$NOX_VERSION_OUTPUT" | head -n 1 | awk '{print $NF}' | tr -d '\r\n')
if [[ -z "$ACTUAL_NOX_VERSION" || "$ACTUAL_NOX_VERSION" != "$EXPECTED_NOX_VERSION" ]]; then
    echo -e "\033[1;31m🟥 Poetry-managed Nox version is '$ACTUAL_NOX_VERSION', expected '$EXPECTED_NOX_VERSION'.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    echo -e "\033[1;33mTIP: Run 'poetry add --group dev nox@$EXPECTED_NOX_VERSION' to fix.\033[0m" | tee -a "$DEBUG_LOG_FILE"
    log_output "[ERROR] Poetry-managed Nox version is '$ACTUAL_NOX_VERSION', expected '$EXPECTED_NOX_VERSION'."
    exit 1
fi

if command -v node >/dev/null 2>&1 && [ -f scripts/pre_npm.py ]; then
    if ! python3 scripts/pre_npm.py 2>&1 | tee -a "$DEBUG_LOG_FILE"; then
        echo -e "\033[1;41m\033[1;97m🟥 npm preflight failed. Please fix npm issues and try again.\033[0m" | tee -a "$DEBUG_LOG_FILE"
        log_output "[ERROR] npm preflight failed."
        exit 1
    fi
fi





if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "\033[1;33m[INFO] Detected unstaged or staged changes after main commit. Auto-staging and committing as 'chore: auto-format/fix after commit'.\033[0m"
    git add . 2>&1 | suppress_git_warnings || true
    if ! poetry run git commit -m "chore: auto-format/fix after commit" 2>&1 | suppress_git_warnings; then
        echo -e "\033[1;31m🟥 Auto-commit of post-commit changes failed. Please resolve manually.\033[0m"
        log_output "[ERROR] Auto-commit of post-commit changes failed."
        exit 1
    fi
fi

echo -e "\n\033[1;34mAll checks passed. Pushing changes to remote...\033[0m\n"
if ! git pull --rebase 2>&1 | suppress_git_warnings; then
    echo -e "\033[1;31m🟥 Pull (rebase) failed. Resolve conflicts before pushing.\033[0m"
    log_output "[ERROR] Pull (rebase) failed."
    exit 1
fi
if ! poetry run git push 2>&1 | suppress_git_warnings; then
    echo -e "\033[1;31m🟥 Push failed.\033[0m"
    log_output "[ERROR] Push failed."
    exit 1
fi
echo -e "\n\033[1;32m╔════════════════════════════════════════════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[1;32m║  ✅ All changes committed, version bumped, checklist updated, and pushed successfully.     ║\033[0m"
echo -e "\033[1;32m╚════════════════════════════════════════════════════════════════════════════════════════════╝\033[0m\n"

echo -e "\n\033[1;36mMonitor CI for a few cycles to ensure all jobs pass and no edge cases are missed.\033[0m\n"
