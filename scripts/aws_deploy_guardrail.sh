#!/bin/bash
# Prevent accidental AWS deploys from local/dev environments
# Usage: source this script in your shell or CI before running any CDK/AWS CLI commands

if [[ -z "$SHIELDCRAFT_ALLOW_DEPLOY" ]]; then
  echo "[GUARDRAIL] AWS deploys are DISABLED for ShieldCraft."
  echo "Set SHIELDCRAFT_ALLOW_DEPLOY=1 to enable deploys."
  exit 1
fi

echo "[GUARDRAIL] AWS deploys ENABLED. Proceed with caution."
