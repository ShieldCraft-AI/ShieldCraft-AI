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

# --- Post-build: create an unversioned CSS fallback and inject into all HTML files ---
# This helps when an edge/cache serves old HTML that references a missing hashed CSS.
echo "[INFO] Preparing fallback asset (unversioned CSS) and patching HTML files..."
CSS_DIR="${BUILD_DIR}/assets/css"
if [ -d "${CSS_DIR}" ]; then
  HASHED_CSS=$(ls "${CSS_DIR}"/styles.*.css 2>/dev/null | head -n1 || true)
  if [ -n "${HASHED_CSS}" ]; then
    cp -f "${HASHED_CSS}" "${CSS_DIR}/styles.css"
    echo "[INFO] Copied hashed CSS $(basename "${HASHED_CSS}") to styles.css"
  else
    echo "[WARN] No hashed styles.*.css file found in ${CSS_DIR}; skipping fallback copy"
  fi
else
  echo "[WARN] CSS directory not found: ${CSS_DIR}; skipping fallback"
fi

# Inject a resilient unversioned stylesheet link into every HTML file in the build
# so that documentation pages (e.g. /adrs, /business_case) will load /assets/css/styles.css
# while CloudFront and browser caches roll forward to the new hashed assets.
find "${BUILD_DIR}" -type f -name "*.html" | while read -r html; do
  if ! grep -q 'href="/assets/css/styles.css"' "${html}"; then
    # Insert the unversioned link immediately after the first stylesheet link
    awk 'BEGIN{added=0}
    /<link rel="stylesheet" href="\/assets\/css\/styles\.[^"]+\.css">/ && !added {
      print $0
      print "<link rel=\"stylesheet\" href=\"/assets/css/styles.css\">"
      added=1
      next
    }
    {print $0}
    END{if(added==0) print ""}' "${html}" > "${html}.patched" && mv "${html}.patched" "${html}"
    echo "[INFO] Injected /assets/css/styles.css fallback into ${html}"
  fi
done


echo "[INFO] Writing deploy metadata (commit + timestamp)..."
DEPLOY_META_FILE="${BUILD_DIR}/deploy-info.json"
printf '{"commit":"%s","timestamp":"%s"}\n' "$(git rev-parse --short HEAD)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${DEPLOY_META_FILE}"

# Rationale: We avoid --delete on the first (asset) sync to prevent a race where
# CloudFront continues serving cached HTML that references old hashed asset filenames
# which have already been deleted. Because assets are content-hashed and cached
# immutably, keeping previous versions is safe and low-cost. Optional pruning can
# be enabled by setting ASSET_DELETE=true for a later cleanup window.
ASSET_DELETE="${ASSET_DELETE:-false}"
echo "[INFO] Syncing static assets to s3://${BUCKET} (immutable) (ASSET_DELETE=${ASSET_DELETE})..."
if [ "${ASSET_DELETE}" = "true" ]; then
  aws s3 sync "${BUILD_DIR}/" "s3://${BUCKET}/" \
    --delete \
    --exclude "*.html" \
    --cache-control "public, max-age=31536000, immutable" \
    --size-only \
    --only-show-errors \
    --no-progress
else
  aws s3 sync "${BUILD_DIR}/" "s3://${BUCKET}/" \
    --exclude "*.html" \
    --cache-control "public, max-age=31536000, immutable" \
    --size-only \
    --only-show-errors \
    --no-progress
fi

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
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id "${CLOUDFRONT_DISTRIBUTION_ID}" \
  --paths "/*" \
  --query 'Invalidation.Id' --output text 2>/dev/null || echo "")
if [ -n "${INVALIDATION_ID}" ]; then
  echo "[INFO] Invalidation submitted (ID=${INVALIDATION_ID}). (Propagation typically < 2 minutes)"
else
  echo "[WARN] CloudFront invalidation request failed. Please verify the distribution ID and AWS credentials."
fi

echo "[SUCCESS] Deployment complete: https://${BUCKET}"
