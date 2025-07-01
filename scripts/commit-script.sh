# 🟫 OPS: Unified, production-grade developer workflow for commit and push with pre-commit/pre-push checks.
# 🟦 NOTE: Automates environment setup, hook installation, and ensures all git operations use the Poetry-managed environment.
# 🟪 ARCH: AWS-native, clean architecture, cross-platform, and frictionless for all contributors.

set -e

# --- Always resolve paths relative to the repo root ---
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# --- Ensure up-to-date with origin/main before anything else ---
echo "🟦 Fetching latest changes from origin/main..."
git fetch origin main
if ! git merge --ff-only origin/main; then
    echo "🟥 CRITICAL: Fast-forward merge from origin/main failed. Please resolve conflicts manually before proceeding."
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOKS_INSTALLED_MARKER="$HOOKS_DIR/.precommit_hooks_installed"

# --- Ensure Poetry is installed ---
if ! command -v poetry >/dev/null 2>&1; then
    echo "🟥 CRITICAL: Poetry is not installed. Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

# --- Poetry update (optional, default: Y) ---
read -rp "🟦 Run 'poetry update' to update dependencies? [Y/n]: " run_poetry_update
run_poetry_update=${run_poetry_update:-Y}
if [[ "$run_poetry_update" =~ ^[Yy]$ ]]; then
    poetry update
fi

# --- Self-heal: if poetry install fails, try removing env and reinstalling ---
if ! poetry install; then
    echo "🟨 Attempting to self-heal Poetry environment..."
    poetry env remove $(poetry env list --full-path | grep Activated | awk '{print $1}')
    poetry install || { echo "🟥 CRITICAL: Poetry install failed after self-heal."; exit 1; }
fi

# --- Ensure pre-commit, pytest, ruff are installed ---
if ! poetry run pre-commit --version >/dev/null 2>&1; then
    poetry add --dev pre-commit
fi
if ! poetry run pytest --version >/dev/null 2>&1; then
    poetry add --dev pytest
fi
if ! poetry run ruff --version >/dev/null 2>&1; then
    poetry add --dev ruff
fi

# --- Ensure hooks are installed and executable ---
if [ ! -f "$HOOKS_INSTALLED_MARKER" ] || [ ! -x "$HOOKS_DIR/pre-commit" ] || [ ! -x "$HOOKS_DIR/pre-push" ]; then
    poetry run pre-commit install --hook-type pre-commit --hook-type pre-push >/dev/null 2>&1 || true
    if [ -d "$HOOKS_DIR" ]; then
        for hook in "$HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-push"; do
            [ -f "$hook" ] && chmod +x "$hook"
            [ -f "$hook" ] && dos2unix "$hook" 2>/dev/null || true
        done
    fi
    touch "$HOOKS_INSTALLED_MARKER"
fi

# --- Stage all changes ---
git add .

# --- Run pre-commit hooks (auto-fix) after staging ---
if ! poetry run pre-commit run --all-files; then
    echo "🟨 CAUTION: Pre-commit hooks made changes or failed. Staging all changes for review."
    git add .
    # If there are now staged changes, auto-commit them as a sanitation commit
    if ! git diff --cached --quiet; then
        echo "🟦 Auto-committing code sanitation changes (pre-commit fixes)..."
        if ! poetry run git commit -m "chore: code sanitation (pre-commit auto-fixes)"; then
            echo "🟥 CRITICAL: Auto-commit of sanitation changes failed."; exit 1;
        fi
    fi
    # Re-run pre-commit hooks to ensure a clean state
    if ! poetry run pre-commit run --all-files; then
        echo "🟥 CRITICAL: Pre-commit hooks failed after sanitation commit. Please fix issues manually."; exit 1;
    fi
fi


echo "🟦 Staged changes ready for commit."
echo "🟦 Select commit type:"
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
read -rp "🟦 Enter the number for commit type [default: 1]: " commit_type_num
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

read -rp "🟦 Enter your commit message: " commit_msg
if [ -z "$commit_msg" ]; then
    echo "🟥 CRITICAL: Commit message cannot be empty."; exit 1
fi
full_commit_msg="$commit_type: $commit_msg"
if ! poetry run git commit -m "$full_commit_msg"; then
    echo "🟥 CRITICAL: Commit failed."; exit 1
fi

# --- Version bump prompt and update pyproject.toml (robust, poetry-native) ---
CURRENT_VERSION=$(poetry version -s)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
echo "🟦 Current project version: $CURRENT_VERSION"
echo "  1) Major ($MAJOR)\n  2) Minor ($MINOR)\n  3) Patch ($PATCH) (default)"
read -rp "🟦 Which part of the version would you like to increment? [Major/Minor/Patch, default: 3]: " version_part
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
    echo "🟦 Updating version to $NEW_VERSION in pyproject.toml (via poetry)..."
    poetry version "$NEW_VERSION"
    git add pyproject.toml
    echo "🟦 Auto-committing version bump..."
    if ! poetry run git commit -m "chore: bump version to $NEW_VERSION"; then
        echo "🟥 CRITICAL: Auto-commit of version bump failed."
        exit 1
    fi
fi

# --- Update checklist progress bar and auto-commit if changed ---
echo "🟦 Updating checklist progress bar..."
CHECKLIST_SCRIPT_PATH="$REPO_ROOT/.github/scripts/update_checklist_progress.py"
if poetry run python "$CHECKLIST_SCRIPT_PATH" | grep -q 'updated'; then
    git add "$REPO_ROOT/docs-site/docs/checklist.md" "$REPO_ROOT/README.md"
    echo "🟦 Auto-committing checklist progress bar update..."
    if ! poetry run git commit -m "chore: update checklist progress bar"; then
        echo "🟥 CRITICAL: Auto-commit of checklist progress bar failed."
        exit 1
    fi
fi

# --- Final pre-commit check to ensure all is clean ---
if ! poetry run pre-commit run --all-files; then
    echo "🟥 CRITICAL: Pre-commit hooks failed after all commits. Please fix issues manually."
    exit 1
fi

# --- Ask user if they want to push ---
read -rp "🟦 All checks passed. Do you want to push to remote now? [Y/n]: " do_push
do_push=${do_push:-Y}
if [[ "$do_push" =~ ^[Yy]$ ]]; then
    echo "🟦 Pulling latest changes with 'git pull --rebase' before push..."
    if ! git pull --rebase; then
        echo "🟥 CRITICAL: Pull (rebase) failed. Resolve conflicts before pushing."
        exit 1
    fi
    echo "🟦 Pushing to remote..."
    if ! poetry run git push; then
        echo "🟥 CRITICAL: Push failed."
        exit 1
    fi
    echo "🟩 GOOD: All changes committed, version bumped, checklist updated, and pushed successfully."
    echo "🟦 See CI/CD status at: https://github.com/<your-org-or-user>/shieldcraft-ai/actions"
    echo "🟦 For docs and next steps, see: $REPO_ROOT/README.md"
else
    echo "🟦 Push skipped. You can push manually with 'git push' when ready."
fi
