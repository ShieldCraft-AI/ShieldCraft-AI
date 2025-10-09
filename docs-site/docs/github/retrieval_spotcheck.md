# Retrieval Relevance Spot-Check Harness

A tiny, dependency-free harness to manually sanity-check retrieval relevance against a few representative queries. It runs locally and prints a JSON report.

## What it does
- Evaluates a small set of `QueryCase` items.
- Uses a simple Jaccard-overlap score over whitespace tokens.
- Reports per-case scores and pass/fail vs a threshold, plus an aggregate pass rate.

## Files
- Library: `ai_core/eval/spotcheck.py` - tokenization, scoring, and runner.
- CLI: `scripts/retrieval_spotcheck.py` - runs a built-in in-memory retriever.
- Tests: `tests/test_retrieval_spotcheck.py` - basic happy-path + empty-set case.

## Run it (local)
```bash
python3 scripts/retrieval_spotcheck.py --pretty
```

Options:
- `--threshold` (default: 0.3) - pass threshold for the overlap score.

## Extending
- Replace the in-memory retriever with a thin wrapper around your local pgvector instance.
- Enrich the score with term weighting or a reranker when you enable those components.

## Notes
- This is a micro-harness meant for quick signal; not a replacement for full evaluation suites.
