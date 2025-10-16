Injecting Amplify runtime config at deploy

Purpose
-------
Keep runtime Cognito/Amplify configuration out of source control and inject it at build/deploy time so the static site can start federated login flows.

Two safe options
----------------
1) Write `static/amplify-config.json` during CI (recommended for static hosts)
2) Inject a small runtime JS snippet into the served HTML that sets `window.__SC_AMPLIFY_CONFIG__` (preferred when you can template HTML)

GitHub Actions example (writes static file)
------------------------------------------
Add this step before your `npm run build` in the job that publishes the site.

```yaml
- name: Write Amplify config
  env:
    COGNITO_DOMAIN: ${{ secrets.COGNITO_DOMAIN }}
    COGNITO_CLIENT_ID: ${{ secrets.COGNITO_CLIENT_ID }}
    COGNITO_REDIRECT_SIGNIN: ${{ secrets.COGNITO_REDIRECT_SIGNIN }}
    COGNITO_REDIRECT_SIGNOUT: ${{ secrets.COGNITO_REDIRECT_SIGNOUT }}
    AWS_REGION: ${{ secrets.AWS_REGION }}
  run: |
    cat > docs-site/static/amplify-config.json <<'EOF'
    {
      "Auth": {
        "region": "${AWS_REGION}",
        "userPoolId": "${USER_POOL_ID:-us-east-1_EXAMPLE}",
        "userPoolWebClientId": "${COGNITO_CLIENT_ID}",
        "oauth": {
          "domain": "${COGNITO_DOMAIN}",
          "scope": ["email","openid"],
          "redirectSignIn": "${COGNITO_REDIRECT_SIGNIN}",
          "redirectSignOut": "${COGNITO_REDIRECT_SIGNOUT}",
          "responseType": "code"
        }
      }
    }
    EOF
```

Notes
-----
- `COGNITO_DOMAIN` is your Cognito hosted UI domain (e.g. `my-app.auth.us-east-1.amazoncognito.com`).
- `COGNITO_CLIENT_ID` is the app client id (public) — not a secret.
- Keep secrets in GitHub/CI secrets and do not commit them.
- Our AWS Secrets Manager footprint (including the GitHub OAuth client secret) now lives in `af-south-1`; align `aws-region` configuration accordingly.
- Alternatively, inject `window.__SC_AMPLIFY_CONFIG__` by templating your HTML or using a small JS file created in CI.

Local development
-----------------
- Run `python scripts/pull_amplify_config.py` after assuming AWS credentials to fetch the latest secret into `docs-site/static/amplify-config.json`.
- The output file is gitignored; rerun the script whenever Cognito redirect URLs or providers change.
- `docs-site/static/amplify-config.template.json` shows the expected JSON shape if you need to craft a manual payload.

HTML injection example (set global var ahead of app code)

```yaml
- name: Inject runtime config into HTML
  env:
    COGNITO_DOMAIN: ${{ secrets.COGNITO_DOMAIN }}
    COGNITO_CLIENT_ID: ${{ secrets.COGNITO_CLIENT_ID }}
    COGNITO_REDIRECT_SIGNIN: ${{ secrets.COGNITO_REDIRECT_SIGNIN }}
    COGNITO_REDIRECT_SIGNOUT: ${{ secrets.COGNITO_REDIRECT_SIGNOUT }}
    AWS_REGION: ${{ secrets.AWS_REGION }}
  run: |
    cat > docs-site/static/runtime-config.js <<'EOF'
    window.__SC_AMPLIFY_CONFIG__ = {
      Auth: {
        region: "${AWS_REGION}",
        userPoolWebClientId: "${COGNITO_CLIENT_ID}",
        oauth: {
          domain: "${COGNITO_DOMAIN}",
          redirectSignIn: "${COGNITO_REDIRECT_SIGNIN}",
          redirectSignOut: "${COGNITO_REDIRECT_SIGNOUT}",
          responseType: "code"
        }
      }
    };
    EOF

# Ensure `runtime-config.js` is included before app bundle (e.g. via docusaurus `scripts` or template)
```

What I will do next
-------------------
If you confirm, I will:
- Add this guide file (done).
- Optionally add a small GitHub Actions job snippet into `.github/workflows/deploy-site.yml` (only if you want a ready-to-use job).

If you'd like the ready-to-use workflow snippet added to your repo, say "Add workflow" and I'll create it (no secrets included).
