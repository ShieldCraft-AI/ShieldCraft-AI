Automate Amplify Config Injection (README)

Purpose
-------
Small, safe tooling to help inject a runtime Amplify/Cognito client config into the Docusaurus site at build time without committing secrets.

Files
-----
- `scripts/automate_amplify_config.py` - main interactive script. Dry-run by default.
- `.github/workflows/inject-amplify-config-secretsmanager.yml` - a workflow template (committed by the script or pre-created in repo) that uses GitHub OIDC to assume an IAM role and fetch a secret from AWS Secrets Manager and write `docs-site/static/amplify-config.json`.
- `scripts/setup_cognito_idp.py` - one-stop helper that prompts for Google/Amazon OAuth credentials, updates Cognito IdPs/app clients, and seeds `shieldcraft/amplify-config` in `af-south-1`.

Safety
------
This tooling does NOT create any AWS resources, and will not run any expensive IaC stacks. You must manually create the Secrets Manager secret and the IAM role with OIDC trust before using the workflow. The script will not perform any network operations against AWS; the workflow is what performs the fetch at runtime in GitHub Actions.

Quick start
-----------
1. From the repository root, preview what will be changed:

   ```bash
   python3 scripts/automate_amplify_config.py --audit --patch-auth
   ```

2. If you want to apply changes locally and commit them:

   ```bash
   python3 scripts/automate_amplify_config.py --patch-auth --create-workflow --commit
   ```

3. Create the Secrets Manager secret in AWS and an IAM role for GitHub OIDC (see docs below). Our production secret now lives in `af-south-1`, so leave the script default alone or pass `--region af-south-1` explicitly. Add repository secrets `ROLE_TO_ASSUME` (role ARN) and `SECRET_NAME` (name/ARN of secret).

4. Trigger the workflow from Actions → Inject Amplify Config from Secrets Manager (workflow_dispatch) and set `run_build: yes` if you want the workflow to run the build after injecting config.

If you prefer GitHub Secrets instead of Secrets Manager, you can use the earlier workflow `inject-amplify-config.yml` committed in the repo, or copy the step that writes `docs-site/static/amplify-config.json` from your secrets.

Notes
-----
- Backups: the script backups files before editing with `.bak.TIMESTAMP` suffix.
- Dry-run: by default the script will only show what would change; pass `--commit` to write files and commit them.
- Default region: the workflow template now assumes `af-south-1`. Override with `--region <your-region>` if you clone the setup elsewhere.
- No infra: the script will not create or change AWS resources; you must do that manually.
