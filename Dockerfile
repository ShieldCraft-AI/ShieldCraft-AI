# --- Base image for all environments ---
FROM python:3.11.9-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# --- OS security updates ---
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Dev stage ---
FROM base AS dev
# Install dev tools and dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    pip install --upgrade pip pipx && \
    pipx install poetry && \
    pipx ensurepath
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --with dev --no-interaction --no-ansi
# Optionally skip large downloads in dev
ARG SKIP_LARGE_DOWNLOADS=0
RUN if [ "$SKIP_LARGE_DOWNLOADS" = "1" ]; then echo "Skipping large downloads in dev"; fi
COPY . .

# --- Staging stage ---
FROM base AS staging
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry install --only main --no-interaction --no-ansi && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    pip install --no-cache-dir -r requirements.txt && \
    poetry env remove python || true
COPY . .
# Remove dev files, tests, docs, etc.
RUN rm -rf tests/ docs/ .git/ .github/ .vscode/ || true
# Use a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# --- Production stage ---
FROM staging AS prod


# --- Distroless final image ---
FROM gcr.io/distroless/python3-debian11 AS final
WORKDIR /app
COPY --from=prod /app /app
COPY --from=prod /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=prod /usr/local/bin /usr/local/bin
USER nonroot:nonroot
ARG ENV=prod
ENV ENV=${ENV}
CMD ["-m", "src.main"]

# --- Target selection ---
# docker build --target=dev --build-arg ENV=dev .
# docker build --target=staging --build-arg ENV=staging .
# docker build --target=final --build-arg ENV=prod .
