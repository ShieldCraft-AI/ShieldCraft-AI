<div align="center">
  <img src="https://img.shields.io/badge/AI%20Security-Shieldcraft%20AI-blueviolet?style=for-the-badge&logo=amazonaws&logoColor=white" alt="Shieldcraft AI" />
</div>

<h1 align="center">🛡️ ShieldCraft AI</h1>
<p align="center"><em>Next-Gen Cybersecurity: Proactive, Adaptive, AI-Driven Defense</em></p>

<div align="center" style="margin-bottom:1em;">
  <a href="https://github.com/Dee66/CodeCraft-AI" style="color:#a5b4fc; font-size:0.98em;">
    <b>✨ See also: CodeCraft AI – My first custom AI implementation</b>
  </a>
</div>

<div align="center" style="margin-bottom:2em;">
  <a href="https://github.com/Dee66/supervised-learning" style="color:#a5b4fc; font-size:0.98em;">
    <b>✨ See also: Supervised ML= ML theory and real-world system design</b>
  </a>
</div>

<div id="progress-bar" align="center" style="margin-bottom:1.5em;">
  <strong>Project Progress</strong>
  <a href="./docs-site/docs/checklist.md" style="margin-left:0.75em; font-size:0.95em; color:#a5b4fc; text-decoration:none;">(checklist)</a><br/>
  <progress id="shieldcraft-progress" value="29" max="100" style="width: 60%; height: 18px;"></progress>
  <div id="progress-label">29% Complete</div>
</div>



<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔎</span> What is ShieldCraft AI?
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
<b>ShieldCraft AI</b> is a modern, AWS-native cybersecurity platform that leverages advanced machine learning, Generative AI (Amazon Bedrock, LangChain), and behavioral analytics to deliver proactive, adaptive threat detection and automated response. Designed for enterprise scale, it empowers security teams to:
<br/>
<ul>
  <li><b>Detect and respond to novel, advanced threats</b> (zero-days, insider risks, AI-driven attacks) in real time</li>
  <li><b>Automate alert triage, investigation, and remediation</b> with GenAI-powered insights and recommendations</li>
  <li><b>Reduce false positives</b> and alert fatigue with deep behavioral analytics and context-aware intelligence</li>
  <li><b>Accelerate incident response</b> and minimize business disruption</li>
</ul>
</div>
</section>




<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">✨</span> Key Capabilities
</h2>
<ul style="margin-bottom:0.5em;">
  <li>Proactive, predictive threat detection (ML, GenAI, UEBA)</li>
  <li>Automated alert triage, investigation, and remediation</li>
  <li>Real-time, actionable dashboards for SOC teams</li>
  <li>Enterprise-grade security, compliance, and modular AWS-native architecture</li>
</ul>
</section>


<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📚</span> Documentation & Deep Dives
</h2>
<ul style="margin-bottom:0.5em;">
  <li><a href="./docs-site/docs/spec.md" style="color:#a5b4fc;"><b>📝 Platform Architecture</b></a> Business case, architecture, and technical blueprint</li>
  <li><a href="./docs-site/docs/poa.md" style="color:#a5b4fc;"><b>🔄 GenAI Implementation Lifecycle</b></a> Step-by-step GenAI buildout</li>
  <li><a href="./docs-site/docs/tooling.md" style="color:#a5b4fc;"><b>🛠️ Tech Stack and Utilities</b></a> Tech, tools and libraries used</li>
  <li><a href="./docs-site/docs/checklist.md" style="color:#a5b4fc;"><b>✅ Project Checklist</b></a> Key milestones and action items</li>
</ul>
</section>


<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🧰</span> Core Tech Stack
</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Data Ingestion & Streaming:</b> 
    <a href="https://aws.amazon.com/msk/" style="color:#a5b4fc;">Amazon MSK (Kafka)</a>, 
    <a href="https://airbyte.com/" style="color:#a5b4fc;">Airbyte</a>, 
    <a href="https://aws.amazon.com/lambda/" style="color:#a5b4fc;">AWS Lambda</a>, 
    <a href="https://docs.aws.amazon.com/opensearch-service/latest/developerguide/data-ingestion.html" style="color:#a5b4fc;">Amazon OpenSearch Ingestion</a>
  </li>
  <li><b>Data Processing & Storage:</b> 
    <a href="https://aws.amazon.com/glue/" style="color:#a5b4fc;">AWS Glue</a>, 
    <a href="https://aws.amazon.com/s3/" style="color:#a5b4fc;">Amazon S3</a>, 
    <a href="https://aws.amazon.com/lake-formation/" style="color:#a5b4fc;">AWS Lake Formation</a>, 
    <a href="https://greatexpectations.io/" style="color:#a5b4fc;">Great Expectations</a>/<a href="https://github.com/awslabs/deequ" style="color:#a5b4fc;">Deequ</a>
  </li>
  <li><b>Machine Learning & MLOps:</b> 
    <a href="https://aws.amazon.com/sagemaker/" style="color:#a5b4fc;">Amazon SageMaker</a> (incl. <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store.html" style="color:#a5b4fc;">Feature Store</a>), 
    <a href="https://aws.amazon.com/opensearch-service/" style="color:#a5b4fc;">Amazon OpenSearch</a> (vector search), 
    <a href="https://www.promptingguide.ai/" style="color:#a5b4fc;">Prompt Engineering</a>, 
    <a href="https://arize.com/llm-observability/" style="color:#a5b4fc;">LLM Observability</a>
  </li>
  <li><b>Model Deployment & Monitoring:</b> 
    <a href="https://aws.amazon.com/eks/" style="color:#a5b4fc;">Amazon EKS (Kubernetes)</a>, 
    <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html" style="color:#a5b4fc;">SageMaker Model Monitor</a>, 
    <a href="https://evidentlyai.com/" style="color:#a5b4fc;">Evidently AI</a>, 
    <a href="https://aws.amazon.com/cloudwatch/" style="color:#a5b4fc;">Amazon CloudWatch</a>, 
    <a href="https://en.wikipedia.org/wiki/A/B_testing" style="color:#a5b4fc;">A/B Testing</a>
  </li>
  <li><b>Orchestration & Workflow:</b> 
    <a href="https://aws.amazon.com/step-functions/" style="color:#a5b4fc;">AWS Step Functions</a>
  </li>
  <li><b>Infrastructure & Security:</b> 
    <a href="https://aws.amazon.com/cdk/" style="color:#a5b4fc;">AWS CDK</a>/<a href="https://www.terraform.io/" style="color:#a5b4fc;">Terraform</a> (IaC), 
    <a href="https://aws.amazon.com/iam/" style="color:#a5b4fc;">AWS IAM</a>, 
    <a href="https://github.com/features/actions" style="color:#a5b4fc;">GitHub Actions</a>/<a href="https://aws.amazon.com/codepipeline/" style="color:#a5b4fc;">CodePipeline</a>, 
    <a href="https://aws.amazon.com/aws-cost-management/aws-cost-explorer/" style="color:#a5b4fc;">Cost Explorer</a>/<a href="https://www.finops.org/" style="color:#a5b4fc;">FinOps</a>
  </li>
  <li><b>Other Core:</b> 
    <a href="https://aws.amazon.com/eks/" style="color:#a5b4fc;">EKS</a>, 
    <a href="https://aws.amazon.com/ecs/" style="color:#a5b4fc;">ECS</a>, 
    <a href="https://aws.amazon.com/lambda/" style="color:#a5b4fc;">Lambda</a>, 
    <a href="https://aws.amazon.com/s3/" style="color:#a5b4fc;">S3</a>, 
    <a href="https://aws.amazon.com/rds/" style="color:#a5b4fc;">RDS</a>, 
    <a href="https://aws.amazon.com/rds/aurora/" style="color:#a5b4fc;">Aurora</a>, 
    <a href="https://aws.amazon.com/vpc/" style="color:#a5b4fc;">VPC</a>, 
    <a href="https://aws.amazon.com/iam/" style="color:#a5b4fc;">IAM</a>, 
    <a href="https://aws.amazon.com/kms/" style="color:#a5b4fc;">KMS</a>, 
    <a href="https://aws.amazon.com/secrets-manager/" style="color:#a5b4fc;">Secrets Manager</a>, 
    <a href="https://aws.amazon.com/guardduty/" style="color:#a5b4fc;">GuardDuty</a>, 
    <a href="https://aws.amazon.com/security-hub/" style="color:#a5b4fc;">Security Hub</a>, 
    <a href="https://aws.amazon.com/config/" style="color:#a5b4fc;">Config</a>, 
    <a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html" style="color:#a5b4fc;">Audit Trails</a>, 
    <a href="https://prometheus.io/" style="color:#a5b4fc;">Prometheus</a>, 
    <a href="https://grafana.com/" style="color:#a5b4fc;">Grafana</a>, 
    <a href="https://sentry.io/welcome/" style="color:#a5b4fc;">Sentry</a>, 
    <a href="https://www.openpolicyagent.org/" style="color:#a5b4fc;">Policy as Code (OPA)</a>, 
    <a href="https://python-poetry.org/" style="color:#a5b4fc;">Poetry</a>, 
    <a href="https://pre-commit.com/" style="color:#a5b4fc;">pre-commit</a>, 
    <a href="https://docusaurus.io/" style="color:#a5b4fc;">Docusaurus</a>, 
    <a href="https://jupyter.org/" style="color:#a5b4fc;">Jupyter</a>, 
    onboarding scripts
  </li>
</ul>
</section>



<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🛠️</span> Developer Workflow
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
See <a href="./docs-site/docs/developer-workflow.md" style="color:#a5b4fc;"><b>🛠️ Developer Workflow</b></a> for the full, automated, Nox-powered developer workflow, commit script, and CI/CD parity details.
</div>
</section>



<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📄</span> License
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
MIT License
</div>
</section>
