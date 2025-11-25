# GuardSuite Architecture Overview

This repository follows the GuardSuite Master Spec. The canonical reference documents are:

- [GuardSuite Master Spec](docs/Guard%20Suite.txt)
- [GuardSuite Delivery Checklist](docs-site/docs/github/checklist.md)

## Repository Scaffolding

Top-level directories required by the spec:

| Directory   | Purpose                                                      |
| ----------- | ------------------------------------------------------------ |
| `vector/`   | Future vector processing jobs and embeddings.                |
| `compute/`  | Shared compute adapters and orchestration helpers.           |
| `pipeline/` | Data-plane pipelines that stitch GuardSuite stages together. |
| `infra/`    | Infrastructure as code and deployment assets.                |
| `config/`   | Environment-scoped configuration.                            |
| `docs/`     | Source documentation that mirrors the Master Spec.           |
| `scripts/`  | Operational tooling and automation entrypoints.              |
| `tests/`    | Contract, regression, and schema tests.                      |

This file should be updated whenever the GuardSuite Master Spec or checklist is revised so that architecture guidance stays synchronized with the authoritative documents.
