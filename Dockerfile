# --- Base image for all environments ---
# Using official Python base image for maximum compatibility
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# --- OS security updates ---
# Chainguard images are continuously updated and minimal, so explicit OS update is not required

# --- Dev stage ---
FROM base AS dev
ARG BUILDKIT_INLINE_CACHE=1
# Install dev tools and dependencies, combine steps for smaller image
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    pip install --upgrade pip pipx && \
    pipx install poetry && \
    pipx ensurepath && \
    echo "[dev] Poetry and pipx installed"
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --with dev --no-interaction --no-ansi
ARG SKIP_LARGE_DOWNLOADS=0
RUN if [ "$SKIP_LARGE_DOWNLOADS" = "1" ]; then echo "Skipping large downloads in dev"; fi
COPY . .

# --- Staging stage ---
FROM base AS staging
ARG BUILDKIT_INLINE_CACHE=1
COPY pyproject.toml poetry.lock ./
RUN ["python", "-m", "pip", "install", "--upgrade", "pip"]
RUN ["python", "-m", "pip", "install", "poetry"]
RUN ["poetry", "install", "--only", "main", "--no-interaction", "--no-ansi"]
RUN ["poetry", "export", "-f", "requirements.txt", "--output", "requirements.txt", "--without-hashes"]
RUN ["python", "-m", "pip", "install", "--no-cache-dir", "-r", "requirements.txt"]
RUN ["sh", "-c", "poetry env remove python || true"]
COPY . .
# Remove dev files, tests, docs, .env, build artifacts, and pip/poetry caches
RUN ["rm", "-rf", "tests/", "docs/", ".git/", ".github/", ".vscode/", ".env", "*.pyc", "*.pyo", "__pycache__", "/root/.cache/pip", "/root/.cache/pypoetry"]
# Use a custom non-root user for security and explicit UID/GID
RUN ["useradd", "-u", "10001", "-m", "appuser"]
RUN ["chown", "-R", "appuser", "/app"]
USER appuser


# --- Production/final image ---
FROM staging AS final
WORKDIR /app
# Use custom non-root user for security
USER 10001
ARG ENV=prod
ENV ENV=${ENV}
# Healthcheck for orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -m src.main_healthcheck || exit 1
# Entrypoint for flexibility
ENTRYPOINT ["python"]
CMD ["-m", "src.main"]

# --- Target selection ---
# docker build --target=dev --build-arg ENV=dev .
# docker build --target=staging --build-arg ENV=staging .
# docker build --target=final --build-arg ENV=prod .

# --- Build and push with BuildKit cache (Main) ---
# uses: docker/build-push-action@v5
# with:
# context: .
# file: Dockerfile
# target: final
# push: true
# tags: ghcr.io/${{ github.repository_owner }}/shieldcraft-main:latest
# cache-from: type=gha
# cache-to: type=gha,mode=max
