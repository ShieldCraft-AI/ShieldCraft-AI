Conversation logger
===================

This directory contains a small append-only conversation logger used to record
messages exchanged during interactive sessions. The primary script is
`scripts/conversation_log.py` and writes newline-delimited JSON records to
`logs/conversation_history.jsonl`.

Why use it
----------
- Keeps an auditable history of conversations.
- Records a snapshot (sha256) of any local `copilot-instructions` file found.
- Optional `--git-commit` flag to persist the log into git history.

Quick examples
--------------

Append a user message:

```bash
python scripts/conversation_log.py --role user --message "What's the infra plan?"
```

Append assistant reply from stdin:

```bash
echo "Use CDK with environment-aware stacks" | python scripts/conversation_log.py --role assistant --from-stdin
```

Append and commit the change:

```bash
python scripts/conversation_log.py --role assistant --message "..." --git-commit
```

Integration ideas
-----------------
- Wrap this script in a local chat proxy that calls the Chat API, logs both
  request and response, then returns the response to the client.
- Use CI hooks to snapshot `copilot-instructions` during PRs.
