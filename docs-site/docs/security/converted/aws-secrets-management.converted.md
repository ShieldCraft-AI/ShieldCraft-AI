<div style="margin-bottom:1.5em;">
  <a href="../checklist" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<div align="center">
  <img src="https://img.shields.io/badge/Secrets%20Management-AWS%20%7C%20Vault%20%7C%20Best%20Practice-blueviolet?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS Secrets Management" />
</div>
<br/>
<h1 align="center">🔒 ShieldCraft AI – AWS Secrets Management</h1>
<p align="center"><em>Production-grade, environment-specific secrets management for GenAI-driven security platforms</em></p>

---

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">🗝️</span> What Should Be a Secret?
</h2>
<ul>
  <li><b>DATABASE_URL</b> (RDS, Aurora, etc.)</li>
  <li><b>REDIS_URL</b> (if using Redis)</li>
  <li><b>SECRET_KEY</b> (app cryptography)</li>
  <li><b>AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY</b> (if not using IAM roles)</li>
  <li><b>OPENAI_API_KEY</b> (or other GenAI provider)</li>
  <li><b>SENTRY_DSN</b> (error monitoring)</li>
  <li><b>LOG_LEVEL</b> (optional, runtime config)</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">📦</span> Organizing Secrets in AWS Secrets Manager
</h2>
<ul>
  <li>One secret per environment:
    <ul>
      <li><b>shieldcraft-dev</b></li>
      <li><b>shieldcraft-staging</b></li>
      <li><b>shieldcraft-prod</b></li>
    </ul>
  </li>
</ul>
Each secret is a JSON object, for example:
<pre><code>{
  "DATABASE_URL": "postgresql://user:pass@host:5432/dbname",
  "REDIS_URL": "redis://host:6379/0",
  "SECRET_KEY": "&lt;randomly-generated&gt;",
  "OPENAI_API_KEY": "sk-...",
  "SENTRY_DSN": "https://...",
  "LOG_LEVEL": "INFO"
}</code></pre>
</section>

---

## 3. Loading Secrets in Python

Install the AWS SDK:

```sh
poetry add boto3
```

Sample loader (`src/utils/secrets.py`):

```python
import os
import boto3
import json

def get_secret():
    env = os.environ.get("SHIELDCRAFT_ENV", "dev")
    secret_name = f"shieldcraft-{env}"
    region = os.environ.get("AWS_REGION", "af-south-1")
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)
```

---

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">💻</span> Local Development: AWS Vault
</h2>
<ul>
  <li>Use <a href="https://github.com/99designs/aws-vault" style="color:#a5b4fc;">aws-vault</a> to run app with the correct profile:</li>
</ul>
<pre><code>aws-vault exec shieldcraft-dev -- poetry run python src/main.py
</code></pre>
<ul>
  <li>For staging/prod, use <code>shieldcraft-staging</code> or <code>shieldcraft-prod</code> profiles.</li>
</ul>
</section>

---

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">🏗️</span> Production (Kubernetes/EC2)
</h2>
<ul>
  <li>Use IAM roles for service accounts (IRSA) or EC2 instance roles for access.</li>
  <li>Never pass AWS credentials as environment variables in Dockerfiles.</li>
  <li>The app will auto-resolve credentials via the environment or role.</li>
</ul>
</section>

---

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">🐳</span> .env and Docker
</h2>
<ul>
  <li>Never copy <code>.env</code> into Docker images.</li>
  <li>For local dev, <code>.env</code> can set <code>AWS_PROFILE</code>, <code>AWS_REGION</code>, etc., but never secrets.</li>
</ul>
</section>

---

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">✅</span> Key Takeaways
</h2>
<ul>
  <li>All secrets are managed in AWS Secrets Manager, per environment.</li>
  <li>The app loads secrets at runtime, never at build time.</li>
  <li>Use <code>aws-vault</code> for local dev, IAM roles for production.</li>
</ul>
</section>
