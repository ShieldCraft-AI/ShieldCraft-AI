# 🟫 OPS: Unified, production-grade developer workflow for commit and push with pre-commit/pre-push checks.
# 🟦 NOTE: Automates environment setup, hook installation, and ensures all git operations use the Poetry-managed environment.
# 🟪 ARCH: AWS-native, clean architecture, cross-platform, and frictionless for all contributors.

set -e

# --- Always resolve paths relative to the repo root ---
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOKS_INSTALLED_MARKER="$HOOKS_DIR/.precommit_hooks_installed"

# --- Ensure Poetry is installed ---
if ! command -v poetry >/dev/null 2>&1; then
    echo "🟥 CRITICAL: Poetry is not installed. Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

# --- Poetry version check & optional self-update (modernized for Poetry 2.x) ---
MIN_POETRY_VERSION="2.1.0"
INSTALLED_POETRY_VERSION=$(poetry --version | awk '{print $3}')
compare_versions() {
    # returns 0 if $1 >= $2
    [ "$1" = "$2" ] && return 0
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        # Only compare if both are numbers
        if [[ ${ver1[i]} =~ ^[0-9]+$ ]] && [[ ${ver2[i]} =~ ^[0-9]+$ ]]; then
            if ((10#${ver1[i]} > 10#${ver2[i]})); then
                return 0
            fi
            if ((10#${ver1[i]} < 10#${ver2[i]})); then
                return 1
            fi
        else
            # fallback to string comparison if not numbers
            if [[ "${ver1[i]}" > "${ver2[i]}" ]]; then
                return 0
            fi
            if [[ "${ver1[i]}" < "${ver2[i]}" ]]; then
                return 1
            fi
        fi
    done
    return 0
}
if ! compare_versions "$INSTALLED_POETRY_VERSION" "$MIN_POETRY_VERSION"; then
    echo "🟨 WARNING: Poetry $MIN_POETRY_VERSION or newer is recommended. Found $INSTALLED_POETRY_VERSION."
    read -rp "🟦 Would you like to update Poetry to the latest version now? [y/N]: " update_poetry
    if [[ "$update_poetry" =~ ^[Yy]$ ]]; then
        poetry self update --preview
    else
        echo "🟨 Continuing with Poetry $INSTALLED_POETRY_VERSION. Some features may not work as expected."
    fi
fi

# --- Python version check (robust range check) ---
REQUIRED_PYTHON_VERSION=$(grep requires-python pyproject.toml | head -1 | awk -F'"' '{print $2}')
CURRENT_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
# Parse lower and upper bounds (e.g., ">=3.11,<4.0")
PY_LOWER=$(echo "$REQUIRED_PYTHON_VERSION" | grep -oE '>=([0-9]+\.[0-9]+)' | grep -oE '[0-9]+\.[0-9]+')
PY_UPPER=$(echo "$REQUIRED_PYTHON_VERSION" | grep -oE '<([0-9]+\.[0-9]+)' | grep -oE '[0-9]+\.[0-9]+')
# Compare current version to bounds
version_ge() {  # $1 >= $2
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=0; i<${#ver2[@]}; i++)); do
        if ((10#${ver1[i]:-0} > 10#${ver2[i]:-0})); then return 0; fi
        if ((10#${ver1[i]:-0} < 10#${ver2[i]:-0})); then return 1; fi
    done
    return 0
}
version_lt() {  # $1 < $2
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=0; i<${#ver2[@]}; i++)); do
        if ((10#${ver1[i]:-0} < 10#${ver2[i]:-0})); then return 0; fi
        if ((10#${ver1[i]:-0} > 10#${ver2[i]:-0})); then return 1; fi
    done
    return 1
}
if ! version_ge "$CURRENT_PYTHON_VERSION" "$PY_LOWER" || { [ -n "$PY_UPPER" ] && version_ge "$CURRENT_PYTHON_VERSION" "$PY_UPPER"; }; then
    echo "🟨 WARNING: Python $REQUIRED_PYTHON_VERSION required, found $CURRENT_PYTHON_VERSION."
fi

# --- Poetry update (optional, default: N) ---
read -rp "🟦 Run 'poetry update' to update dependencies? [Y/n]: " run_poetry_update
echo
run_poetry_update=${run_poetry_update:-Y}
if [[ "$run_poetry_update" =~ ^[Yy]$ ]]; then
    poetry update
fi

# --- Self-heal: if poetry install fails, try removing env and reinstalling ---
if ! poetry install; then
    echo "🟨 Attempting to self-heal Poetry environment..."
    poetry env remove $(poetry env list --full-path | grep Activated | awk '{print $1}')
    poetry install || { echo "🟥 CRITICAL: Poetry install failed after self-heal. Auto-resume..."; resume_script "$@"; exit 1; }
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

# --- Ensure Poetry environment and dependencies are present ---
if ! poetry env info -p >/dev/null 2>&1; then
    echo "🟦 NOTE: Creating Poetry environment and installing dependencies..."
    poetry install
fi

# --- Ensure pre-commit is in dev-dependencies and installed ---
if ! poetry run pre-commit --version >/dev/null 2>&1; then
    if ! grep -q 'pre-commit' pyproject.toml; then
        echo "🟦 Adding pre-commit to dev-dependencies..."
        poetry add --dev pre-commit
    else
        echo "🟦 Installing pre-commit in Poetry environment..."
        poetry install
    fi
fi

# --- Ensure pytest and ruff are installed ---
if ! poetry run pytest --version >/dev/null 2>&1; then
    if ! grep -q 'pytest' pyproject.toml; then
        echo "🟦 Adding pytest to dev-dependencies..."
        poetry add --dev pytest
    else
        poetry install
    fi
fi
if ! poetry run ruff --version >/dev/null 2>&1; then
    if ! grep -q 'ruff' pyproject.toml; then
        echo "🟦 Adding ruff to dev-dependencies..."
        poetry add --dev ruff
    else
        poetry install
    fi
fi

# --- Ensure hooks are installed and executable (idempotent, but skip if already installed) ---
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

# --- Helper: auto-resume on failure ---
resume_script() {
    echo "🟦 Attempting auto-resume..."
    exec "$0" "$@"
}

# --- Main commit+push workflow (default) ---
# 1. Stage all changes
git add .

# 2. Run pre-commit hooks (auto-fix) after staging
if ! poetry run pre-commit run --all-files; then
    echo "🟨 CAUTION: Pre-commit hooks made changes or failed. Staging all changes for review."
    git add .
    # If there are now staged changes, auto-commit them as a sanitation commit
    if ! git diff --cached --quiet; then
        echo "🟦 Auto-committing code sanitation changes (pre-commit fixes)..."
        if ! poetry run git commit -m "chore: code sanitation (pre-commit auto-fixes)"; then
            echo "🟥 CRITICAL: Auto-commit of sanitation changes failed. Auto-resume..."; resume_script "$@"; exit 1;
        fi
    fi
    # Re-run pre-commit hooks to ensure a clean state
    if ! poetry run pre-commit run --all-files; then
        echo "🟥 CRITICAL: Pre-commit hooks failed after sanitation commit. Please fix issues manually. Auto-resume..."; resume_script "$@"; exit 1;
    fi
fi

# 3. If no staged changes remain, exit (nothing to commit)
if git diff --cached --quiet; then
    echo "🟦 No staged changes to commit."
    exit 0
fi

# 4. Prompt for commit message and commit user changes
read -rp "🟦 Enter your commit message (conventional: feat:, fix:, chore:, etc.): " commit_msg
if [ -z "$commit_msg" ]; then
    echo "🟥 CRITICAL: Commit message cannot be empty. Auto-resume..."
    resume_script "$@"; exit 1
fi
# Enforce conventional commit style (basic check)
if ! [[ "$commit_msg" =~ ^(feat|fix|chore|docs|style|refactor|perf|test|ci|build|revert)(\(.+\))?: ]]; then
    echo "🟨 WARNING: Commit message does not follow conventional style. (e.g., feat:, fix:, chore:). Continue? [y/N]: "
    read -r continue_commit
    continue_commit=${continue_commit:-N}
    if [[ ! "$continue_commit" =~ ^[Yy]$ ]]; then
        echo "🟥 Commit aborted. Please use a conventional commit message."
        resume_script "$@"; exit 1
    fi
fi
if ! poetry run git commit -m "$commit_msg"; then
    echo "🟥 CRITICAL: Commit failed. Auto-resume..."
    resume_script "$@"; exit 1
fi

# 5. Update checklist progress bar and auto-commit if changed
echo "🟦 Updating checklist progress bar..."
CHECKLIST_SCRIPT_PATH="$REPO_ROOT/.github/scripts/update_checklist_progress.py"
if poetry run python "$CHECKLIST_SCRIPT_PATH" | grep -q 'updated'; then
    git add "$REPO_ROOT/docs/checklist.md"
    echo "🟦 Auto-committing checklist progress bar update..."
    if ! poetry run git commit -m "chore: update checklist progress bar"; then
        echo "🟥 CRITICAL: Auto-commit of checklist progress bar failed. Auto-resume..."
        resume_script "$@"; exit 1
    fi
fi

# 6. Final pre-commit check to ensure all is clean
if ! poetry run pre-commit run --all-files; then
    echo "🟥 CRITICAL: Pre-commit hooks failed after all commits. Please fix issues manually."
    exit 1
fi

# 7. Pull with rebase before push
echo "🟦 Pulling latest changes with 'git pull --rebase' before push..."
if ! git pull --rebase; then
    echo "🟥 CRITICAL: Pull (rebase) failed. Resolve conflicts before pushing."
    exit 1
fi

# 8. Push to remote
echo "🟦 Pushing to remote..."
if ! poetry run git push; then
    echo "🟥 CRITICAL: Push failed."
    exit 1
fi

# --- Poetry check and outdated dependencies ---
echo "🟦 Checking Poetry project integrity..."
if ! poetry check; then
    echo "🟥 CRITICAL: Poetry project check failed. Auto-resume..."
    resume_script "$@"; exit 1
fi

echo "🟦 Checking for outdated dependencies..."
if poetry show --outdated | grep -q .; then
    echo "🟦 Outdated dependencies found. Running 'poetry update' to correct..."
    if ! poetry update; then
        echo "🟥 CRITICAL: Poetry update failed. Auto-resume..."
        resume_script "$@"; exit 1
    fi
    git add poetry.lock pyproject.toml
    echo "🟦 Auto-committing dependency updates..."
    if ! poetry run git commit -m "chore: update dependencies to latest versions"; then
        echo "🟥 CRITICAL: Auto-commit of dependency updates failed. Auto-resume..."
        resume_script "$@"; exit 1
    fi
else
    echo "🟩 All dependencies are up to date."
fi

# --- Run tests and lint locally in parallel ---
echo "🟦 Running tests (pytest) and linter (ruff) in parallel..."
poetry run pytest &
PYTEST_PID=$!
poetry run ruff check . &
RUFF_PID=$!
wait $PYTEST_PID
PYTEST_STATUS=$?
wait $RUFF_PID
RUFF_STATUS=$?
if [ $PYTEST_STATUS -ne 0 ]; then
    echo "🟥 CRITICAL: Tests failed. Auto-resume..."
    resume_script "$@"; exit 1
fi
if [ $RUFF_STATUS -ne 0 ]; then
    echo "🟥 CRITICAL: Ruff linter failed. Auto-resume..."
    resume_script "$@"; exit 1
fi

# --- Docker build and scan for all environments and Dockerfiles ---
DOCKERFILES=(Dockerfile Dockerfile.api Dockerfile.ingestion)
ENVS=(dev staging prod)
for dockerfile in "${DOCKERFILES[@]}"; do
    if [ -f "$dockerfile" ]; then
        for env in "${ENVS[@]}"; do
            IMAGE_TAG="shieldcraft-ai-${env}-$(basename $dockerfile | tr '[:upper:]' '[:lower:]' | sed 's/dockerfile//;s/\.//g')"
            echo "🟦 Building Docker image $IMAGE_TAG from $dockerfile for $env..."
            # Optimize for dev: use --target=dev if multi-stage, limit build context, skip large downloads
            DEV_BUILD_ARGS=""
            if [ "$env" = "dev" ]; then
                # If Dockerfile supports, use a dev target
                if grep -q "^FROM" "$dockerfile" && grep -q "AS dev" "$dockerfile"; then
                    DEV_BUILD_ARGS="--target=dev"
                fi
                # Optionally, pass a build arg to skip large downloads in dev
                DEV_BUILD_ARGS="$DEV_BUILD_ARGS --build-arg SKIP_LARGE_DOWNLOADS=1"
            fi
            if ! docker build -f "$dockerfile" -t "$IMAGE_TAG" --build-arg ENV="$env" $DEV_BUILD_ARGS .; then
                echo "🟥 CRITICAL: Docker build failed for $dockerfile ($env). Auto-resume..."
                resume_script "$@"; exit 1
            fi
            echo "🟦 Scanning Docker image $IMAGE_TAG for vulnerabilities (Trivy)..."
            if ! command -v trivy >/dev/null 2>&1; then
                echo "🟨 WARNING: Trivy not installed, skipping vulnerability scan for $IMAGE_TAG."
            else
                if ! trivy image --severity CRITICAL,HIGH "$IMAGE_TAG"; then
                    echo "🟥 CRITICAL: Vulnerabilities found in Docker image $IMAGE_TAG. Auto-resume..."
                    resume_script "$@"; exit 1
                fi
            fi
            # Optionally: Run container and health check here
            # docker run --rm $IMAGE_TAG python -m src.main --healthcheck
        done
    fi
    # else: skip missing Dockerfile
    # echo "🟦 Skipping $dockerfile (not found)"
done

echo "🟩 GOOD: All changes committed, checklist updated, and pushed successfully."
echo "🟦 See CI/CD status at: https://github.com/<your-org-or-user>/shieldcraft-ai/actions"
echo "🟦 For docs and next steps, see: $REPO_ROOT/README.md"
