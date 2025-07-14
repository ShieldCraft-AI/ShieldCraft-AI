[⬅️ Back to Checklist](../checklist)

# 🔒 ShieldCraft AI – AWS Secrets Management

Production-grade, environment-specific secrets management for GenAI-driven security platforms

---

## 🗝️What Should Be a Secret?

* DATABASE_URL(RDS, Aurora, etc.)
* REDIS_URL(if using Redis)
* SECRET_KEY(app cryptography)
* AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY(if not using IAM roles)
* OPENAI_API_KEY(or other GenAI provider)
* SENTRY_DSN(error monitoring)
* LOG_LEVEL(optional, runtime config)

## 📦Organizing Secrets in AWS Secrets Manager

* One secret per environment:shieldcraft-devshieldcraft-stagingshieldcraft-prod

Each secret is a JSON object, for example:

```
{
  "DATABASE_URL": "postgresql://user:pass@host:5432/dbname",
  "REDIS_URL": "redis://host:6379/0",
  "SECRET_KEY": "<randomly-generated>",
  "OPENAI_API_KEY": "sk-...",
  "SENTRY_DSN": "https://...",
  "LOG_LEVEL": "INFO"
}
```

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

## 💻Local Development: AWS Vault

* Useaws-vaultto run app with the correct profile:

```
aws-vault exec shieldcraft-dev -- poetry run python src/main.py

```

* For staging/prod, useshieldcraft-stagingorshieldcraft-prodprofiles.

---

## 🏗️Production (Kubernetes/EC2)

* Use IAM roles for service accounts (IRSA) or EC2 instance roles for access.
* Never pass AWS credentials as environment variables in Dockerfiles.
* The app will auto-resolve credentials via the environment or role.

---

## 🐳.env and Docker

* Never copy.envinto Docker images.
* For local dev,.envcan setAWS_PROFILE,AWS_REGION, etc., but never secrets.

---

## ✅Key Takeaways

* All secrets are managed in AWS Secrets Manager, per environment.
* The app loads secrets at runtime, never at build time.
* Useaws-vaultfor local dev, IAM roles for production.

<!-- Unhandled tags: br, em, li -->
