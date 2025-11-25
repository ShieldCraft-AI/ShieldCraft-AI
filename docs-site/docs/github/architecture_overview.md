---
title: Architecture Overview
---

## Automation Surfaces
- `run_drift_check.py` captures read-only CloudFormation drift evidence for every stack.
- `run_drift_remediation.py` stages reviewable remediation plans without mutating infrastructure.
### Drift Telemetry Channel
- `[telemetry]` prefixes tag every structured detection/remediation log so downstream collectors can filter without parsing noisy streams.
- Set `SHIELDCRAFT_EMIT_TELEMETRY=1` only when you want persisted JSON snapshots; leave it unset for stdout-only diagnostics.
- Optional telemetry artifacts live next to other drift outputs at `artifacts/drift_telemetry/`, completely detached from stack state.
