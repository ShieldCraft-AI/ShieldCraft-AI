# 🛡️ ShieldCraft AI: AWS Stack Architecture & Dependency Map

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="../../README.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Project Overview</a>
</div>
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em; color:#a5b4fc;">🛡️ ShieldCraft AI: AWS Stack Architecture & Dependency Map</h1>
<div style="color:#b3b3b3; text-align:center; font-size:1.1em; margin-bottom:1em;">
  This document provides a comprehensive overview of all major infrastructure stacks in ShieldCraft AI, their responsibilities, <br>and how they interact to deliver a secure, modular, and production-grade MLOps platform.
  All relationships <br>are defined in code for full reproducibility and auditability.
</div>
</section>

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
    <tr><td><b>networking</b></td><td>Foundational network isolation and security</td><td>VPC, subnets, security groups</td></tr>
    <tr><td><b>s3</b></td><td>Centralized object storage for all data and artifacts</td><td>S3 buckets</td></tr>
    <tr><td><b>lakeformation</b></td><td>Data governance and fine-grained access control</td><td>Lake Formation resources, permissions</td></tr>
    <tr><td><b>glue</b></td><td>ETL, data cataloging, and analytics</td><td>Glue jobs, crawlers, catalog</td></tr>
    <tr><td><b>lambda</b></td><td>Event-driven compute and orchestration</td><td>Lambda functions, triggers</td></tr>
    <tr><td><b>dataquality</b></td><td>Automated data quality checks and validation</td><td>Quality rules, validation jobs</td></tr>
    <tr><td><b>airbyte</b></td><td>Connector-based data ingestion and movement</td><td>ECS services, connectors</td></tr>
    <tr><td><b>opensearch</b></td><td>Search and analytics for logs and data</td><td>OpenSearch domains</td></tr>
    <tr><td><b>cloud_native_hardening</b></td><td>Cross-cutting security, monitoring, compliance</td><td>CloudWatch alarms, Config rules, IAM boundaries</td></tr>
    <tr><td><b>msk</b></td><td>Managed streaming for Kafka workloads</td><td>MSK clusters</td></tr>
    <tr><td><b>sagemaker</b></td><td>Model training, deployment, and monitoring</td><td>SageMaker endpoints, models, monitoring</td></tr>
  </tbody>
</table>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Dependency Table</h2>
<div style="overflow-x:auto;">
<table style="width:100%; background:#181818; color:#fff; border-radius:8px; border-collapse:collapse;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th style="text-align:left; padding:0.5em 1em;">Stack</th>
      <th style="text-align:left; padding:0.5em 1em;">Depends On</th>
      <th style="text-align:left; padding:0.5em 1em;">Provides</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><b>networking</b></td><td>-</td><td>VPC, subnets, security groups</td></tr>
    <tr><td><b>s3</b></td><td>-</td><td>S3 buckets for data lake, raw/processed data, model artifacts</td></tr>
    <tr><td><b>lakeformation</b></td><td>S3</td><td>Data governance, permissions for Glue, Athena, etc.</td></tr>
    <tr><td><b>glue</b></td><td>S3, Lake Formation</td><td>ETL, crawlers, catalog for analytics</td></tr>
    <tr><td><b>lambda</b></td><td>VPC, IAM, S3, Secrets Manager</td><td>Event-driven ETL, orchestration, data quality</td></tr>
    <tr><td><b>dataquality</b></td><td>Lambda, Glue, IAM, Secrets Manager, S3</td><td>Data quality checks, validation</td></tr>
    <tr><td><b>airbyte</b></td><td>ECS, EC2, VPC, SSM, Secrets Manager, ELBv2, CloudWatch Logs</td><td>Connector-based data ingestion</td></tr>
    <tr><td><b>opensearch</b></td><td>VPC, EC2, IAM</td><td>Search/analytics</td></tr>
    <tr><td><b>cloud_native_hardening</b></td><td>All stacks</td><td>CloudWatch alarms, AWS Config rules, IAM boundaries</td></tr>
    <tr><td><b>msk</b></td><td>VPC, EC2</td><td>Kafka streaming</td></tr>
    <tr><td><b>sagemaker</b></td><td>VPC, S3, IAM</td><td>Model endpoints (real-time/batch), inference, monitoring</td></tr>
  </tbody>
</table>
</div>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">How the Stacks Interact</h2>
<ul style="color:#b3b3b3;">
  <li><b>networking</b> is foundational: all compute, data, and orchestration stacks (lambda, msk, airbyte, opensearch, glue, sagemaker) inject VPC, subnets, and security groups for secure, isolated deployments.</li>
  <li><b>s3</b> provides buckets for all data, model artifacts, and logs. These are referenced by lakeformation, glue, dataquality, sagemaker, and lambda for storage, cataloging, and compliance.</li>
  <li><b>lakeformation</b> registers S3 buckets for fine-grained data lake permissions, enabling secure, auditable access for glue, athena, and other consumers.</li>
  <li><b>glue</b> and <b>dataquality</b> use S3 and VPC resources for ETL, data quality, and cataloging, sharing IAM roles and security groups as needed.</li>
  <li><b>airbyte</b> deploys in ECS, using VPC, security groups, and secrets from other stacks for secure data movement.</li>
  <li><b>sagemaker</b> provisions models, endpoints, and monitoring, using VPC, subnets, security groups, and S3 buckets from networking and storage stacks. Outputs (endpoints, alarms, ARNs) are available for downstream consumers.</li>
  <li><b>opensearch</b> and <b>msk</b> provision search and streaming infrastructure, using VPC and security groups, and are monitored by <b>cloud_native_hardening</b>.</li>
  <li><b>lambda</b> functions use VPC, security groups, and S3 buckets, and are monitored by <b>cloud_native_hardening</b>.</li>
  <li><b>cloud_native_hardening</b> provides cross-cutting monitoring, compliance, and alerting for all critical resources, exporting alarm ARNs and key resources for use in other stacks.</li>
  <li>Each stack exports key resources (e.g., ARNs, endpoints, VPC IDs) for use by others, supporting dependency injection and loose coupling.</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Textual Overview</h2>
<pre style="background:#181818; color:#fff; padding:1em; border-radius:8px; font-size:1em;">
networking_stack
  ├─▶ msk_stack
  ├─▶ lambda_stack
  ├─▶ airbyte_stack
  ├─▶ opensearch_stack
  ├─▶ glue_stack
  └─▶ sagemaker_stack

s3_stack
├─▶ lakeformation_stack
├─▶ glue_stack
├─▶ dataquality_stack
└─▶ sagemaker_stack

sagemaker_stack
(consumes VPC, S3, IAM)

</pre>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Architectural Insights</h2>
<ul style="color:#b3b3b3;">
  <li>Stacks are modular, composable, and parameterized for maximum flexibility and reuse.</li>
  <li>Security, compliance, and monitoring are embedded via cross-stack resource sharing and the hardening stack.</li>
  <li>All relationships are explicit and testable, supporting both happy and unhappy paths.</li>
  <li>Outputs and shared resources are robustly validated in tests, ensuring reliability for downstream consumers.</li>
  <li>Design supports cloud-native, MLOps, and enterprise best practices for production workloads.</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Legend & Guidance</h2>
<ul style="color:#b3b3b3;">
  <li><b>Arrows</b> (<code>▶</code>) indicate dependency or resource consumption.</li>
  <li>Stacks at the top (networking, S3) are foundational; others build on them.</li>
  <li>“Cross-cutting” stacks (like <code>cloud_native_hardening</code>) add security/monitoring to all.</li>
  <li>All relationships are defined in code for full reproducibility and auditability.</li>
</ul>
<p style="color:#b3b3b3;">For a graphical version, consider using Mermaid or PlantUML with this structure as a base.</p>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">IAM Role Management & Config-Driven Permissions</h2>
<ul style="color:#b3b3b3;">
  <li>All IAM roles are created centrally in <b>IamRoleStack</b> and passed to consuming stacks via cross-stack references, ensuring least-privilege, auditable, and environment-specific permissions.</li>
  <li>Stacks no longer create their own roles; instead, they accept role ARNs as constructor arguments, supporting modularity and security best practices.</li>
  <li>Permissions and resource wiring are fully config-driven, enabling rapid environment changes and consistent policy enforcement across dev, staging, and prod.</li>
  <li>Tests validate that all stacks receive the correct role ARNs and that no stack creates ad hoc roles, supporting compliance and traceability.</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Compliance Stack Extensibility</h2>
<ul style="color:#b3b3b3;">
  <li>The <b>compliance</b> stack is designed for extensibility: it accepts a config dict and a Lambda role ARN, enabling both managed and Lambda-backed AWS Config rules.</li>
  <li>Required tag rules and other compliance controls are parameterized via config, supporting organization-wide policy enforcement.</li>
  <li>Future compliance rules can be added by updating the config and wiring in new Lambda-backed rules using the provided role, without changing stack wiring or permissions.</li>
</ul>
</section>
