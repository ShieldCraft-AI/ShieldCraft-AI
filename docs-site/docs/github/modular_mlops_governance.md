<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">🧩 Modular System Layers, MLOps Flow & Security/Data Governance</h1>
<div style="margin-bottom:1.2em; color:#b3b3b3; font-size:1em;">
  This document details the modular architecture, MLOps lifecycle, and security/data governance design for ShieldCraft AI.
</div>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">


## 1. Modular System Architecture & MLOps Diagram

<div style="display:flex; flex-direction:column; align-items:center; margin:2.5em 0 2em 0; padding:1.5em 0 1em 0;">
  <img src="./_assets/mlops_flow.svg" alt="ShieldCraft AI Modular MLOps Flow Diagram" style="max-width:92%; border:1.5px solid #a5b4fc; border-radius:12px; box-shadow:0 4px 18px #222b; background:#181825; padding:1.5em 1.5em 1em 1.5em; margin-bottom:0.5em;" />
  <div style="color:#a5b4fc; font-size:1.05em; margin-top:0.7em; letter-spacing:0.01em;">Figure: Modular MLOps flow showing data, model, and governance layers</div>
</div>

---

## 2. MLOps Flow

- **Automated Pipelines:**
  - Data ingestion, validation, and versioning
  - Model training, evaluation, and registry (SageMaker/MLflow)
  - Continuous integration and deployment (CI/CD) for models and code
  - Canary and shadow deployments for safe model updates

- **Experiment Tracking:**
  - All experiments logged with parameters, metrics, and artifacts
  - Rollback and audit trails for all model changes

- **Monitoring & Feedback:**
  - Automated monitoring for drift, performance, and cost
  - Human-in-the-loop feedback for prompt/model improvement

---

## 3. Security & Data Governance

- **Data Privacy:**
  - Masking, anonymization, and minimization at ingestion and processing
  - Data retention and deletion policies
  - Regular privacy impact assessments ([see doc](./privacy_impact_assessment.md))

- **Access Control:**
  - IAM roles and least-privilege access
  - Centralized secrets management ([see doc](security/aws-secrets-management.md))
  - Audit logging for all access and changes

- **Compliance:**
  - Automated checks for GDPR, SOC2, POPIA, etc.
  - Documentation and evidence collection for audits
  - Regular reviews and updates ([see doc](./ethics_compliance.md))

- **Security Posture:**
  - Threat modeling and adversarial testing ([see doc](./threat_modeling.md))
  - Automated vulnerability scanning in CI/CD
  - Incident response plan and runbooks


<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./infra_estimate.md" style="color:#a5b4fc;">Infrastructure Estimate</a> | <a href="./ethics_compliance.md" style="color:#a5b4fc;">Ethics & Compliance</a> | <a href="./privacy_impact_assessment.md" style="color:#a5b4fc;">Privacy Impact Assessment</a> | <a href="./threat_modeling.md" style="color:#a5b4fc;">Threat Modeling</a></em>
