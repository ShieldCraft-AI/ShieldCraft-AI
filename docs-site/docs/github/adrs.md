<section style={{ border: '1px solid #a5b4fc', borderRadius: '10px', margin: '1.5em 0', boxShadow: '0 2px 8px #222', padding: '1.5em', background: '#111', color: '#fff' }}>
<div style={{ marginBottom: '1.5em' }}>
  <a href="./checklist.md" style={{ color: '#a5b4fc', fontWeight: 'bold', textDecoration: 'none', fontSize: '1.1em' }}>⬅️ Back to Checklist</a>
</div>

# <img src="/img/logo.png" alt="ShieldCraft AI" style="height:48px;width:auto;vertical-align:middle;border-radius:8px;" /> Architecture Decision Records (ADRs)

This document tracks key architectural decisions for ShieldCraft AI. Each ADR includes context, decision, and consequences.

---

| ADR                          | Context                                                       | Decision                                                                  | Consequences                                                                           |
| ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Cloud Provider Selection** | Need for scalable, secure, and cost-effective infrastructure. | Use AWS as primary cloud provider; design for future multi-cloud support. | Leverages AWS services, but some vendor lock-in.                                       |
| **Container Orchestration**  | Need for scalable deployment and management of microservices. | Use Amazon ECS/EKS for orchestration.                                     | Simplifies scaling, but requires AWS-specific expertise.                               |
| **Vector Database**          | Need for efficient similarity search for RAG and AI features. | Use Postgres with pgvector extension for MVP.                             | Lower cost and operational complexity for MVP; can migrate to managed vector DB later. |

---

### How to Use

- Add a new ADR for each major technical or architectural decision.
- Reference ADRs in code and documentation where relevant.

---

_Related: [Risk Log](./risk_log.md) | [Threat Modeling](./threat_modeling.md) | [Security & Governance](./security_governance.md)_
