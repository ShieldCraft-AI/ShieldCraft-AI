# --- Base image for all environments ---
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# --- Dev stage ---
FROM base AS dev
# Install dev tools and dependencies
RUN pip install --upgrade pip pipx && \
    pipx install poetry && \
    pipx ensurepath
COPY pyproject.toml poetry.lock ./
RUN poetry install --with dev --no-interaction --no-ansi
# Optionally skip large downloads in dev
ARG SKIP_LARGE_DOWNLOADS=0
RUN if [ "$SKIP_LARGE_DOWNLOADS" = "1" ]; then echo "Skipping large downloads in dev"; fi
COPY . .

# --- Production stage ---
FROM base AS prod
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
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

# --- Final image ---
FROM prod AS final
ENV ENV=prod
CMD ["python", "-m", "src.main"]

# --- Target selection ---
# docker build --target=dev --build-arg ENV=dev .
# docker build --target=final --build-arg ENV=prod .
