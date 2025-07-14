#!/bin/bash
# List all files and folders up to 3 levels deep in the current directory.
# Exclude:
# - Any folder whose name starts with a period (dot), e.g. .nox, .venv, .github, and their contents.
# - Any 'node_modules' folders and their contents.
# Output will be saved to tree.txt in the current directory.

find . -mindepth 1 -maxdepth 3 \
    \( -type d -name '.*' -prune -o -type d -name 'node_modules' -prune \) -o \
    -print | sed 's|^./||' > tree.txt

echo "Output saved to tree.txt"
