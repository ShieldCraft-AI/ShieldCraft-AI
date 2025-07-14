<div style="margin-bottom:1.5em;">
  <a href="../checklist" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<div align="center">
  <img src="https://img.shields.io/badge/Secrets%20Management-AWS%20%7C%20Vault%20%7C%20Best%20Practice-blueviolet?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS Secrets Management" />
</div>
<h1 align="center">🔒 ShieldCraft AI – AWS Secrets Management</h1>

***

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">🗝️</span> What Should Be a Secret?
</h2>
<ul>
</ul>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">📦</span> Organizing Secrets in AWS Secrets Manager
</h2>
<ul>
    <ul>
    </ul>
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

***

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

***

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">💻</span> Local Development: AWS Vault
</h2>
<ul>
</ul>
<pre><code>aws-vault exec shieldcraft-dev -- poetry run python src/main.py
</code></pre>
<ul>
</ul>

***

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">🏗️</span> Production (Kubernetes/EC2)
</h2>
<ul>
</ul>

***

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">🐳</span> .env and Docker
</h2>
<ul>
</ul>

***

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.25em;gap:0.5em;">
  <span style="font-size:1.1em;">✅</span> Key Takeaways
</h2>
<ul>
</ul>
