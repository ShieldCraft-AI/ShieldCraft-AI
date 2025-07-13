#!/usr/bin/env bash
# ShieldCraft AI CDK wrapper: Ensures PYTHONPATH is set for infra/app.py imports
export PYTHONPATH="$(dirname "$(realpath "$0")")/.."
poetry run python -m infra.app
