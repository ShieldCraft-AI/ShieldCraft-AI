#!/usr/bin/env bash
# Simple wrapper that demonstrates calling the conversation logger from shell.
# Usage: ./scripts/chat_log_wrapper.sh user "Message text"

set -euo pipefail

ROLE=${1:-}
MSG=${2:-}

if [[ -z "$ROLE" || -z "$MSG" ]]; then
  echo "Usage: $0 <role:user|assistant|system> <message>" >&2
  exit 2
fi

python scripts/conversation_log.py --role "$ROLE" --message "$MSG"
