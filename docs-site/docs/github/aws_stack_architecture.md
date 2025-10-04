<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="../../../README.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Project Overview</a>
</div>
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em; color:#a5b4fc;"><img src="/img/logo.png" alt="ShieldCraft AI" style="height:42px;width:auto;vertical-align:middle;border-radius:8px;" /> ShieldCraft AI: AWS Stack Architecture & Dependency Map</h1>
<div style="color:#b3b3b3; text-align:center; font-size:1.1em; margin-bottom:1em;">
</div></section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Stack Roles & Responsibilities</h2>
<table style="width:100%; background:#181818; color:#fff; border-radius:8px; border-collapse:collapse;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th style="text-align:left; padding:0.5em 1em;">Stack</th>
      <th style="text-align:left; padding:0.5em 1em;">Role</th>
      <th style="text-align:left; padding:0.5em 1em;">Key Resources</th>
    </tr>
  </thead>
  <tbody>
<tr><td><b>airbyte</b></td><td>Connector-based data ingestion and movement</td><td>ECS services, connectors, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>attack_simulation</b></td><td>Automated attack simulation and security validation</td><td>Lambda functions, CloudWatch alarms, imported secret ARN, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>budget</b></td><td>Cost guardrails, budget alerts, and multi-channel notifications</td><td>AWS Budgets, SNS topics, email alerts, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>cloud_native_hardening</b></td><td>Cross-cutting security, monitoring, compliance</td><td>CloudWatch alarms, Config rules, IAM boundaries, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>cloudformation</b></td><td>Orchestration and lifecycle management of all AWS stacks</td><td>CloudFormation stacks, stack outputs, cross-stack references</td></tr>
<tr><td><b>dataquality</b></td><td>Automated data quality checks and validation</td><td>Quality rules, validation jobs, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>eventbridge</b></td><td>Central event bus for orchestration and integration</td><td>EventBridge bus, rules, targets</td></tr>
<tr><td><b>glue</b></td><td>ETL, data cataloging, and analytics</td><td>Glue jobs, crawlers, catalog, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>lakeformation</b></td><td>Data governance and fine-grained access control</td><td>Lake Formation resources, permissions, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>lambda</b></td><td>Event-driven compute and orchestration</td><td>Lambda functions, triggers, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>msk</b></td><td>Managed streaming for Kafka workloads</td><td>MSK clusters, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>networking</b></td><td>Foundational network isolation and security</td><td>VPC, subnets, security groups, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>opensearch</b></td><td>Search and analytics for logs and data</td><td>OpenSearch domains, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>s3</b></td><td>Centralized object storage for all data and artifacts</td><td>S3 buckets, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>sagemaker</b></td><td>Model training, deployment, and monitoring</td><td>SageMaker endpoints, models, monitoring, <span style="color:#a5b4fc;">vault secret (imported)</span></td></tr>
<tr><td><b>secrets_manager</b></td><td>Centralized secrets management for all environments</td><td>AWS Secrets Manager secrets, resource policies, cross-stack exports</td></tr>
<tr><td><b>stepfunctions</b></td><td>Workflow orchestration for AI/ML pipelines</td><td>State machines, workflow definitions, IAM roles</td></tr>
  </tbody>
</table></section>


<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Expanded Dependency Matrix (Outputs & Inputs)</h2>
<div style="overflow-x:auto;">
<table style="width:100%; background:#181818; color:#fff; border-radius:8px; border-collapse:collapse;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th style="text-align:left; padding:0.5em 1em;">Stack</th>
      <th style="text-align:left; padding:0.5em 1em;">Exports (CfnOutput)</th>
      <th style="text-align:left; padding:0.5em 1em;">Consumed By (Fn.import_value)</th>
      <th style="text-align:left; padding:0.5em 1em;">Notes on Parallelism</th>
    </tr>
  </thead>
  <tbody>
  <tr><td><b>AirbyteStack</b></td><td>Endpoints, role ARN, vault secret ARN</td><td>(If needed by other stacks)</td><td></td></tr>
  <tr><td><b>AttackSimulationStack</b></td><td>Lambda ARN, alarm ARN, imported secret ARN</td><td>Security, audit, downstream consumers</td><td>Can run in parallel with other compute stacks</td></tr>
  <tr><td><b>BudgetStack</b></td><td>Budget ARNs, SNS topic ARN, vault secret ARN</td><td>All teams, FinOps, notifications</td><td>Deployed last, depends on all infra</td></tr>
  <tr><td><b>CloudFormationStack</b></td><td>Stack outputs, exported values, orchestration metadata</td><td>All stacks (as orchestrator)</td><td>Runs before/with all stacks, manages dependencies and lifecycle</td></tr>
  <tr><td><b>CloudNativeHardeningStack</b></td><td>Security findings, config rules, vault secret ARN</td><td>(If needed by other stacks)</td><td></td></tr>
  <tr><td><b>ComplianceStack</b></td><td>Compliance reports, Lambda ARNs, vault secret ARN</td><td>(If needed by other stacks)</td><td></td></tr>
  <tr><td><b>DataQualityStack</b></td><td>Metrics, alerts, vault secret ARN</td><td>(If needed by other stacks)</td><td></td></tr>
  <tr><td><b>EventBridgeStack</b></td><td>Event bus ARN, rule ARNs</td><td>LambdaStack, StepFunctionsStack, other integration stacks</td><td>Can run in parallel with other integration stacks</td></tr>
  <tr><td><b>GlueStack</b></td><td>Glue DB/catalog name, vault secret ARN</td><td>LakeFormationStack, DataQualityStack</td><td>GlueStack must finish before dependents</td></tr>
  <tr><td><b>IamRoleStack</b></td><td>All required IAM role ARNs</td><td>All stacks needing roles</td><td>Deploy first or in parallel, outputs must exist before import</td></tr>
  <tr><td><b>LakeFormationStack</b></td><td>Admin role, permissions, vault secret ARN</td><td>(If needed by other stacks)</td><td></td></tr>
  <tr><td><b>LambdaStack</b></td><td>Lambda ARNs, vault secret ARN</td><td>DataQualityStack, ComplianceStack, AttackSimulationStack</td><td></td></tr>
  <tr><td><b>MskStack</b></td><td>Broker info, client/producer/consumer roles, vault secret ARN</td><td>LambdaStack, AirbyteStack, etc.</td><td></td></tr>
  <tr><td><b>NetworkingStack</b></td><td>VPC ID, SG IDs, Flow Logs ARN, vault secret ARN</td><td>All compute/data stacks</td><td>Same as above</td></tr>
  <tr><td><b>OpenSearchStack</b></td><td>Endpoint, role ARN, vault secret ARN</td><td>Analytics, LambdaStack</td><td></td></tr>
  <tr><td><b>S3Stack</b></td><td>data_bucket name/ARN, vault secret ARN</td><td>GlueStack, LakeFormationStack, etc.</td><td>S3Stack must finish before dependent stacks</td></tr>
  <tr><td><b>SageMakerStack</b></td><td>Endpoint, role ARN, vault secret ARN</td><td>ML pipeline, LambdaStack</td><td></td></tr>
  <tr><td><b>SecretsManagerStack</b></td><td>Secret ARNs, resource policies</td><td>All stacks needing secrets</td><td>Deploy first for secret availability</td></tr>
  <tr><td><b>StepFunctionsStack</b></td><td>State machine ARN, workflow outputs</td><td>LambdaStack, SageMakerStack, DataQualityStack</td><td>Can run in parallel with other workflow stacks</td></tr>
  </tbody>
</table>
</div></section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">How the Stacks Interact</h2>


<h3 style="color:#a5b4fc; margin-top:0;">Textual Overview</h3>
<pre style="background:#181818; color:#fff; padding:1em; border-radius:8px; font-size:1em;">
networking_stack
  ├─▶ msk_stack
  ├─▶ lambda_stack
  ├─▶ airbyte_stack
  ├─▶ opensearch_stack
  ├─▶ glue_stack
  ├─▶ sagemaker_stack
  ├─▶ dataquality_stack
  ├─▶ cloud_native_hardening_stack
  └─▶ compliance_stack

cloudformation_stack
  ├─▶ orchestrates all stacks
  ├─▶ manages stack dependencies, outputs, and lifecycle
  └─▶ enables cross-stack references and automation
eventbridge_stack
  ├─▶ lambda_stack
  ├─▶ stepfunctions_stack
  └─▶ other integration consumers

stepfunctions_stack
  ├─▶ lambda_stack
  ├─▶ sagemaker_stack
  ├─▶ dataquality_stack
  └─▶ workflow consumers

s3_stack
  ├─▶ lakeformation_stack
  ├─▶ glue_stack
  ├─▶ dataquality_stack
  └─▶ sagemaker_stack

iam_role_stack
  ├─▶ lambda_stack
  ├─▶ glue_stack
  ├─▶ msk_stack
  ├─▶ airbyte_stack
  ├─▶ opensearch_stack
  ├─▶ lakeformation_stack
  ├─▶ sagemaker_stack
  ├─▶ cloud_native_hardening_stack
  └─▶ compliance_stack

glue_stack
  ├─▶ dataquality_stack
  └─▶ lakeformation_stack

lambda_stack
  ├─▶ dataquality_stack
  └─▶ compliance_stack

msk_stack
  ├─▶ cloud_native_hardening_stack

opensearch_stack
  ├─▶ cloud_native_hardening_stack

cloud_native_hardening_stack
  └─▶ (monitors all critical stacks)

compliance_stack
  └─▶ (reports on all critical stacks)

sagemaker_stack
  (consumes VPC, S3, IAM)

budget_stack
  (depends on all other stacks; provides cost guardrails and notifications)

</pre></section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Template Coverage & Roadmap Services</h2>

<h3 style="color:#a5b4fc;">Active Architecture (14/20 templates, 70% coverage)</h3>
<p style="color:#b3b3b3;">The current production architecture activates 14 core services, representing a cost-optimized and complexity-managed deployment strategy:</p>
<ul style="color:#b3b3b3;">
  <li><strong>Total Cost Progression:</strong> DEV ($44) → STAGING ($1,010) → PROD ($4,500) per month</li>
  <li><strong>Service Coverage:</strong> All essential data ingestion, processing, ML, and security capabilities</li>
  <li><strong>Deployment Strategy:</strong> Conservative activation with proven service combinations</li>
</ul>

<h3 style="color:#a5b4fc;">Available but Not Enabled (6/20 templates)</h3>
<p style="color:#b3b3b3;">The following services have complete Proton templates but are not configured in environment YAMLs. These represent either future roadmap items or environment-specific optional services:</p>

<table style="width:100%; background:#181818; color:#fff; border-radius:8px; border-collapse:collapse;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th style="text-align:left; padding:0.5em 1em;">Service</th>
      <th style="text-align:left; padding:0.5em 1em;">Purpose</th>
      <th style="text-align:left; padding:0.5em 1em;">Template Status</th>
      <th style="text-align:left; padding:0.5em 1em;">Roadmap Notes</th>
    </tr>
  </thead>
  <tbody>
<tr><td><b>attack_simulation</b></td><td>Automated attack simulation and security validation</td><td>✅ Complete template</td><td>Security team roadmap - Lambda-based attack scenarios</td></tr>
<tr><td><b>budget</b></td><td>Cost guardrails, budget alerts, multi-channel notifications</td><td>✅ Complete template</td><td>FinOps enhancement - AWS Budgets with SNS integration</td></tr>
<tr><td><b>compliance</b></td><td>Compliance monitoring and automated reporting</td><td>✅ Complete template</td><td>Governance roadmap - automated compliance validation</td></tr>
<tr><td><b>controltower</b></td><td>AWS Control Tower governance and organizational controls</td><td>✅ Complete template</td><td>Enterprise roadmap - multi-account governance</td></tr>
<tr><td><b>dataquality</b></td><td>Automated data quality checks and validation pipelines</td><td>✅ Complete template</td><td>Data engineering roadmap - quality assurance automation</td></tr>
<tr><td><b>secrets_manager</b></td><td>Centralized secrets management beyond vault integration</td><td>✅ Complete template</td><td>Security enhancement - AWS-native secret rotation</td></tr>
  </tbody>
</table>

<h3 style="color:#a5b4fc;">Activation Strategy</h3>
<p style="color:#b3b3b3;">These templates can be activated by adding configuration sections to environment YAMLs (dev.yml, staging.yml, prod.yml). Estimated additional cost impact: ~$22-102 / month across all environments.</p>

</section>
