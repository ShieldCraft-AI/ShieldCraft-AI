# ShieldCraft AI High-Level AWS Architecture Diagram (draw.io scaffolding)

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
- S3
- Lake Formation
- Secrets Manager

## Layer 3: Data Platform
- Glue
- Airbyte
- DataQuality

## Layer 4: Compute & Analytics
- Lambda
- MSK
- SageMaker
- OpenSearch

## Layer 5: Orchestration
- Step Functions
- EventBridge

## Layer 6: Security & Compliance
- Cloud Native Hardening
- Attack Simulation
- Compliance Stack

## Layer 7: Cost Management
- Budget Stack

---

## Visual Guidance
- Use color coding for each layer.
- Place arrows from Networking/IAM to all other layers.
- Show data flow from Storage → Data Platform → Compute/Analytics.
- Orchestration triggers to Compute/Analytics.
- Security/Compliance monitor all layers.
- Budget stack sits to the side, monitoring all resources.

---

## Next Steps
- Add AWS icons and arrange as per above.
- Export as SVG/PNG for docs and web.
- Update as architecture evolves.
