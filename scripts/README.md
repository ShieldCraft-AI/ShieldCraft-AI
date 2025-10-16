Staging refresh check
=====================

This repository includes a small script that validates the Cognito refresh
flow for staging environments where a valid refresh token is available.

Files
- `staging-refresh-check.js`  -  POSTs to the Cognito `/oauth2/token` endpoint
  using the `refresh_token` grant and exits with non-zero on failure.

How to run (staging-only)

Set the required environment variables (do not commit these):

```bash
export AUTH_DOMAIN=shieldcraft-auth.auth.us-east-1.amazoncognito.com
export CLIENT_ID=<your-client-id>
export REFRESH_TOKEN=<refresh-token-for-test-user>
node scripts/staging-refresh-check.js
```

CI-friendly usage

Run the script as a step in staging CI with the env vars provided by the
staging secrets manager. The script will exit 0 on success and non-zero on
failure. Keep the refresh token secret and rotate as needed.

Security
- Keep the REFRESH_TOKEN secret. Limit which CI jobs can access it.
- Only run this against staging or a dedicated test user; do not run against
  production user tokens.
