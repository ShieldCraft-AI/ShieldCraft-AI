#!/usr/bin/env bash
set -e

# ShieldCraft AI: Run key nox sessions in parallel for CI/local speedup
# Only use for sessions that do not share state or write to the same files.
# Usage: ./scripts/nox_parallel.sh

SESSIONS=(lint typecheck tests docs security)

# Run all sessions in parallel, fail fast if any fails
echo "[nox_parallel] Running sessions in parallel: ${SESSIONS[*]}"
parallel --halt now,fail=1 ::: "${SESSIONS[@]/#/poetry run nox -s }"

echo "[nox_parallel] All parallel sessions complete."
