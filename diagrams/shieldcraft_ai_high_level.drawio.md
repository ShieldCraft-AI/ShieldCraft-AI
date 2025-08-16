# ShieldCraft AI High-Level AWS Architecture Diagram (draw.io scaffolding)

## Updated Architecture Overview
This diagram reflects the current ShieldCraft AI AWS stack architecture, aligned with the latest service groupings and dependencies.

## Instructions
- Open this file in VS Code with the Draw.io Integration extension.
- Use AWS official SVG icons (from your repo or AWS icon set) for each component.
- Arrange layers as horizontal bands, top to bottom.
- Connect components with arrows to show relationships and data flow.
- Add brief annotations for clarity.

---

## Layer 1: Networking & IAM (Foundation)
- VPC
- Subnets
- Security Groups
- IAM Roles/Policies

## Layer 2: Storage & Secrets
- S3 (Buckets)
- Lake Formation
- Secrets Manager

## Layer 3: Data Platform
- Glue
- Lake Formation (Data Governance)
- Airbyte (Ingestion)
- DataQuality (Validation)

## Layer 4: Compute & Analytics
- Lambda
- MSK (Kafka)
- SageMaker (ML/AI)
- OpenSearch (Search/Analytics)

## Layer 5: Orchestration
- Step Functions (Workflow Automation)
- EventBridge (Event Routing)

## Layer 6: Security & Compliance
- Cloud Native Hardening
- Attack Simulation
- Compliance Stack

## Layer 7: Cost Management
- Budget Stack

---

## Visual Guidance
- Use color coding for each layer (e.g., blue for Networking, green for Data, orange for Compute, red for Security).
- Place arrows from Networking/IAM to all other layers (foundational dependencies).
- Show data flow: Storage → Data Platform → Compute/Analytics.
- Orchestration triggers to Compute/Analytics and Data Platform.
- Security/Compliance monitor all layers (overlay or boundary).
- Budget stack sits to the side, monitoring all resources (cost governance).

---

## Next Steps
- Add AWS official icons for each service/component.
- Arrange layers as horizontal bands, top to bottom, with clear boundaries.
- Connect components with arrows to show relationships and data flow.
- Add brief annotations for clarity (e.g., "Data flows from Airbyte to S3, then to Glue for ETL").
- Export as SVG/PNG for docs and web.
- Update as architecture evolves and new stacks/services are added.
