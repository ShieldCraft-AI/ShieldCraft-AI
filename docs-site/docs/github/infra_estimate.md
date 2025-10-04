<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;"><img src="/img/logo.png" alt="ShieldCraft AI" style="height:42px;width:auto;vertical-align:middle;border-radius:8px;" /> ShieldCraft AI: Baseline Infrastructure & Cloud Usage Estimate</h1>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

## ☁️ Baseline Infrastructure

- **Cloud Provider:** AWS (primary), with multi-cloud/pluggable support in roadmap
- **Core Services:**
  - Amazon ECS/EKS (container orchestration)
  - S3 (object storage)
  - RDS/Postgres (relational DB, vector DB via pgvector)
  - Lambda (serverless tasks)
  - CloudWatch (logging/monitoring)
  - VPC, Security Groups, IAM (networking/security)
  - Bedrock (GenAI/LLM)
  - SQS/SNS (eventing/notifications)
  - Secrets Manager (secrets management)
- **DevOps:**
  - GitHub Actions (CI/CD)
  - Poetry/Nox (Python env & automation)
  - Docker Compose (local/dev)

---


## 💸 Cloud Usage Estimate (MVP Phase)

All pricing is estimated in South African Rand (ZAR/R), based on AWS public pricing as of July 2025. Actual costs may vary by region, usage, and discounts. Exchange rate used: 1 USD ≈ R18.50.

| Service/Resource          | Usage/Notes                            |  Unit Price (R) | Monthly Qty | Est. Monthly (R) |
| ------------------------- | -------------------------------------- | --------------: | ----------: | ---------------: |
| **Compute**               | 2-3 t3.medium EC2/ECS/EKS nodes (24/7) |     R1,200/node |         2.5 |           R3,000 |
| **Storage: S3**           | 100GB (Standard)                       |        R0.45/GB |         100 |              R45 |
| **Storage: RDS/Postgres** | 50GB + db.t3.medium (HA)               |     R1,400/inst |           1 |           R1,400 |
|                           | Storage (50GB)                         |        R0.50/GB |          50 |              R25 |
| **Networking**            | 1TB egress                             |        R1.80/GB |       1,000 |           R1,800 |
| **Bedrock/LLM**           | 100K tokens (pilot)                    | R0.15/1K tokens |         100 |              R15 |
| **Monitoring**            | CloudWatch (basic)                     |            R200 |           1 |             R200 |
| **Lambda**                | 100K invocations                       |        R0.40/1K |         100 |              R40 |
| **SQS/SNS**               | 1M messages                            |       R0.08/10K |         100 |               R8 |
| **Other (IAM, VPC, etc)** | Misc. baseline infra                   |               - |           - |             R150 |
| **Support/Buffer**        | Unforeseen, price fluctuation          |               - |           - |             R300 |
| **Total (Est.)**          |                                        |                 |             |       **R6,991** |

**Notes:**
- Compute: t3.medium on-demand, average 2.5 nodes (mix of ECS/EKS/EC2)
- RDS: Single db.t3.medium instance, 50GB storage, multi-AZ not included
- S3: Standard storage, excludes infrequent access/archive
- Networking: 1TB egress, intra-AWS traffic not included
- Bedrock/LLM: Based on pilot usage, may increase with scale
- Lambda/SQS/SNS: Within free tier for most months, but included for buffer
- Support/Buffer: For minor services, price changes, or overages

---

## 🛠️ DevOps

- **CI/CD:** GitHub Actions for automated testing, build, and deployment
- **Infrastructure as Code:** Terraform (planned), AWS CDK (roadmap)
- **Secrets Management:** AWS Secrets Manager, GitHub OIDC
- **Containerization:** Docker, Docker Compose for local/dev
- **Monitoring & Alerting:** CloudWatch, custom dashboards, Slack/Teams integration (future)
- **Automated Security Scans:** Dependabot, Trivy (container scanning)

## 🤖 MLOps

- **Experiment Tracking:** MLflow (planned), Weights & Biases (optional)
- **Model Registry:** MLflow Model Registry (future)
- **Model Deployment:** CI/CD integration for model serving (ECS/EKS, Lambda)
- **Data Versioning:** DVC (Data Version Control) or S3 versioning
- **Automated Retraining:** Scheduled retraining pipelines (future)
- **Monitoring:** Model drift, data quality, and performance monitoring (roadmap)

---

## 📋 Next Steps

- Set up cost monitoring and alerting
- Proceed to: **Address ethics, safety, and compliance requirements** in the [Checklist](./checklist.md)


<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./infra_estimate.md" style="color:#a5b4fc;">Infrastructure Estimate</a> | <a href="./adrs.md" style="color:#a5b4fc;">ADRs</a> | <a href="./project_structure.md" style="color:#a5b4fc;">Project Structure</a></em>
