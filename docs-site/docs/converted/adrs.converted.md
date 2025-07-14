[⬅️ Back to Checklist](./checklist.md)

# 🛡️ ShieldCraft AI: Architecture Decision Records (ADRs)

This document tracks key architectural decisions for ShieldCraft AI. Each ADR includes context, decision, and consequences.

***

| ADR                     | Context                                              | Decision                                              | Consequences                                         |
|-------------------------|------------------------------------------------------|-------------------------------------------------------|------------------------------------------------------|
| **Cloud Provider Selection** | Need for scalable, secure, and cost-effective infrastructure. | Use AWS as primary cloud provider; design for future multi-cloud support. | Leverages AWS services, but some vendor lock-in.      |
| **Container Orchestration**  | Need for scalable deployment and management of microservices. | Use Amazon ECS/EKS for orchestration.                 | Simplifies scaling, but requires AWS-specific expertise. |
| **Vector Database**          | Need for efficient similarity search for RAG and AI features. | Use Postgres with pgvector extension for MVP.         | Lower cost and operational complexity for MVP; can migrate to managed vector DB later. |

***

### How to Use

*   Add a new ADR for each major technical or architectural decision.
*   Reference ADRs in code and documentation where relevant.

***

*Related: [Risk Log](./risk_log.md) | [Threat Modeling](./threat_modeling.md) | [Security & Governance](./security_governance.md)*
