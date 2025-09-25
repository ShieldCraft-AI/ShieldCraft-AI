#!/usr/bin/env bash
set -euo pipefail

# Simple deploy helper for the docs site (S3 + CloudFront invalidation)
# Requirements: Node 20+, npm, AWS CLI v2.27.50 configured with credentials and region

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [ -z "${REPO_ROOT}" ]; then
  echo "[ERROR] Not in a git repository. Run this from within the repo." >&2
  exit 1
fi
cd "${REPO_ROOT}"

DOCS_DIR="docs-site"
BUILD_DIR="${DOCS_DIR}/build"

# Defaults (can be overridden via env vars BUCKET / CLOUDFRONT_DISTRIBUTION_ID)
DEFAULT_BUCKET="shieldcraft-ai.com"
DEFAULT_CLOUDFRONT_DISTRIBUTION_ID="E2C0Y8M6RGTBD7"
BUCKET="${BUCKET:-${DEFAULT_BUCKET}}"
CLOUDFRONT_DISTRIBUTION_ID="${CLOUDFRONT_DISTRIBUTION_ID:-${DEFAULT_CLOUDFRONT_DISTRIBUTION_ID}}"

echo "[INFO] Using bucket: ${BUCKET}"
echo "[INFO] Using CloudFront distribution: ${CLOUDFRONT_DISTRIBUTION_ID}"

echo "[INFO] Building docs with Docusaurus..."
pushd "${DOCS_DIR}" >/dev/null
npm ci
npm run build
popd >/dev/null

if [ ! -d "${BUILD_DIR}" ]; then
  echo "[ERROR] Build directory not found: ${BUILD_DIR}" >&2
  exit 1
fi

echo "[INFO] Syncing static assets to s3://${BUCKET} (immutable caches for non-HTML)..."
aws s3 sync "${BUILD_DIR}/" "s3://${BUCKET}/" \
  --delete \
  --exclude "*.html" \
  --cache-control "public, max-age=31536000, immutable" \
  --size-only \
  --only-show-errors \
  --no-progress

echo "[INFO] Syncing HTML with short cache (fast refresh)..."
aws s3 sync "${BUILD_DIR}/" "s3://${BUCKET}/" \
  --delete \
  --exclude "*" \
  --include "*.html" \
  --cache-control "public, max-age=60, must-revalidate" \
  --content-type "text/html" \
  --size-only \
  --only-show-errors \
  --no-progress

echo "[INFO] Creating CloudFront invalidation for /* on distribution ${CLOUDFRONT_DISTRIBUTION_ID}..."
aws cloudfront create-invalidation \
  --distribution-id "${CLOUDFRONT_DISTRIBUTION_ID}" \
  --paths "/*" >/dev/null \
  || echo "[WARN] CloudFront invalidation request failed. Please verify the distribution ID and AWS credentials."

echo "[SUCCESS] Deployment complete: https://${BUCKET}"
