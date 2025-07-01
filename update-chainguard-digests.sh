#!/usr/bin/env bash
# update-chainguard-digests.sh
# Usage: ./update-chainguard-digests.sh
# This script finds the current sha256 digest for cgr.dev/chainguard/python:latest
# and updates all Dockerfiles in the current directory to pin to that digest.

set -euo pipefail

IMAGE="cgr.dev/chainguard/python:latest"

# Pull the latest image
echo "Pulling $IMAGE ..."
docker pull "$IMAGE"

# Get the digest
digest=$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE" | sed 's/.*@//')
if [[ -z "$digest" ]]; then
  echo "Could not find digest for $IMAGE. Exiting."
  exit 1
fi

echo "Found digest: $digest"

# Update all Dockerfiles in the current directory (and subdirs)
for file in $(find . -type f -name 'Dockerfile*'); do
  echo "Updating $file ..."
  sed -i.bak "s|cgr.dev/chainguard/python:latest|cgr.dev/chainguard/python@sha256:$digest|g" "$file"
  echo "  -> $file updated."
done

echo "All Dockerfiles updated to use cgr.dev/chainguard/python@$digest"
