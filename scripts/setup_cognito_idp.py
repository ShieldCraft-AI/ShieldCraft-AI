#!/usr/bin/env python3
"""
DOCUMENTED DEPLOY HELPER — Reviewed
Purpose: interactive helper to configure Cognito identity providers and seed runtime secrets.
This script talks to AWS; do not run in CI. Any changes must be reviewed before removal from the whitelist.

Interactive helper to configure Cognito IdPs and runtime config secrets.

The script guides you through:
 - selecting the Cognito user pool and Hosted UI app client
 - (re)creating Google and Login with Amazon identity providers
 - updating Hosted UI callback/logout URLs and supported providers
 - seeding the Amplify runtime config secret in af-south-1

It only prints high-level status messages so secrets stay off the console.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Dict, List, Optional, Sequence

import boto3
from botocore.exceptions import ClientError

DEFAULT_USER_POOL_REGION = "us-east-1"
DEFAULT_SECRET_REGION = "af-south-1"
DEFAULT_SECRET_NAME = "shieldcraft/amplify-config"


@dataclass
class ProviderInput:
    client_id: str
    client_secret: str
    scopes: Sequence[str]


def prompt(text: str, default: Optional[str] = None, secret: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        if secret:
            value = getpass(f"{text}{suffix}: ")
        else:
            value = input(f"{text}{suffix}: ").strip()
        if not value and default is not None:
            return default
        if value:
            return value
        print("Value required. Please try again.")


def pick_user_pool(region: str) -> str:
    client = boto3.client("cognito-idp", region_name=region)
    pools: List[Dict[str, str]] = []
    pagination_token: Optional[str] = None
    while True:
        kwargs = {"MaxResults": 60}
        if pagination_token:
            kwargs["NextToken"] = pagination_token
        resp = client.list_user_pools(**kwargs)
        pools.extend(resp.get("UserPools", []))
        pagination_token = resp.get("NextToken")
        if not pagination_token:
            break

    if not pools:
        print("No user pools found in region", region)
        sys.exit(1)

    print("Available user pools:")
    for idx, pool in enumerate(pools, 1):
        print(f"  {idx:2d}. {pool.get('Name')} ({pool.get('Id')})")
    choice = prompt("Select user pool number", default="1")
    try:
        return pools[int(choice) - 1]["Id"]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)


def pick_user_pool_client(region: str, user_pool_id: str) -> str:
    client = boto3.client("cognito-idp", region_name=region)
    clients: List[Dict[str, str]] = []
    pagination_token: Optional[str] = None
    while True:
        kwargs = {"UserPoolId": user_pool_id, "MaxResults": 60}
        if pagination_token:
            kwargs["NextToken"] = pagination_token
        resp = client.list_user_pool_clients(**kwargs)
        clients.extend(resp.get("UserPoolClients", []))
        pagination_token = resp.get("NextToken")
        if not pagination_token:
            break

    if not clients:
        print("No app clients found for user pool", user_pool_id)
        sys.exit(1)

    print("Hosted UI app clients:")
    for idx, data in enumerate(clients, 1):
        print(f"  {idx:2d}. {data.get('ClientName')} ({data.get('ClientId')})")
    choice = prompt("Select app client number", default="1")
    try:
        return clients[int(choice) - 1]["ClientId"]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)


def describe_pool(region: str, user_pool_id: str) -> Dict[str, str]:
    client = boto3.client("cognito-idp", region_name=region)
    resp = client.describe_user_pool(UserPoolId=user_pool_id)
    return resp.get("UserPool", {})


def describe_client(
    region: str, user_pool_id: str, client_id: str
) -> Dict[str, object]:
    client = boto3.client("cognito-idp", region_name=region)
    resp = client.describe_user_pool_client(UserPoolId=user_pool_id, ClientId=client_id)
    return resp.get("UserPoolClient", {})


def ensure_provider(
    region: str,
    user_pool_id: str,
    provider_name: str,
    provider_type: str,
    provider_input: ProviderInput,
    attribute_mapping: Optional[Dict[str, str]] = None,
) -> None:
    client = boto3.client("cognito-idp", region_name=region)
    details = {
        "client_id": provider_input.client_id,
        "client_secret": provider_input.client_secret,
        "authorize_scopes": " ".join(provider_input.scopes),
    }
    try:
        client.create_identity_provider(
            UserPoolId=user_pool_id,
            ProviderName=provider_name,
            ProviderType=provider_type,
            ProviderDetails=details,
            AttributeMapping=attribute_mapping or {},
        )
        print(f"Created identity provider {provider_name}.")
    except ClientError as exc:
        if exc.response["Error"].get("Code") != "DuplicateProviderException":
            raise
        client.update_identity_provider(
            UserPoolId=user_pool_id,
            ProviderName=provider_name,
            ProviderDetails=details,
            AttributeMapping=attribute_mapping or {},
        )
        print(f"Updated identity provider {provider_name}.")


def update_app_client(
    region: str,
    user_pool_id: str,
    client_id: str,
    redirect_sign_in: Sequence[str],
    redirect_sign_out: Sequence[str],
    providers: Sequence[str],
    scopes: Sequence[str],
) -> None:
    client = boto3.client("cognito-idp", region_name=region)
    providers_list = ["COGNITO"] + [p for p in providers if p != "COGNITO"]
    client.update_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        SupportedIdentityProviders=providers_list,
        CallbackURLs=list(dict.fromkeys(redirect_sign_in)),
        LogoutURLs=list(dict.fromkeys(redirect_sign_out)),
        AllowedOAuthFlows=["code"],
        AllowedOAuthScopes=list(dict.fromkeys(scopes)),
        AllowedOAuthFlowsUserPoolClient=True,
    )
    print("Updated app client with new providers and redirect URLs.")


def upsert_amplify_secret(
    region: str,
    secret_name: str,
    payload: Dict[str, object],
) -> None:
    client = boto3.client("secretsmanager", region_name=region)
    body = json.dumps(payload, indent=2)
    try:
        client.create_secret(Name=secret_name, SecretString=body)
        print(f"Created secret {secret_name} in {region}.")
    except ClientError as exc:
        if exc.response["Error"].get("Code") != "ResourceExistsException":
            raise
        client.put_secret_value(SecretId=secret_name, SecretString=body)
        print(f"Updated secret {secret_name} in {region}.")


def main() -> int:
    print("Cognito IdP bootstrapper")
    print("-------------------------")
    print("This tool will prompt for the values you cannot auto-discover:")
    print(" - Google OAuth client ID / secret (from Google Cloud console)")
    print(" - (Optional) Login with Amazon client ID / secret (Amazon Developer)")
    print("It will fetch pool/app metadata so you do not have to copy IDs manually.")

    user_pool_region = prompt("Cognito user pool region", DEFAULT_USER_POOL_REGION)
    user_pool_id = pick_user_pool(user_pool_region)
    app_client_id = pick_user_pool_client(user_pool_region, user_pool_id)

    pool_details = describe_pool(user_pool_region, user_pool_id)
    client_details = describe_client(user_pool_region, user_pool_id, app_client_id)

    hosted_ui_domain = pool_details.get("Domain") or prompt(
        "Hosted UI domain (e.g. shieldcraft-auth.auth.us-east-1.amazoncognito.com)",
    )

    existing_callbacks = client_details.get("CallbackURLs") or []
    existing_logouts = client_details.get("LogoutURLs") or []
    existing_scopes = client_details.get("AllowedOAuthScopes") or [
        "email",
        "openid",
        "profile",
    ]

    print("Current callback URLs:", ", ".join(existing_callbacks) or "(none)")
    redirect_sign_in = prompt(
        "Comma-separated redirect sign-in URLs",
        (
            ",".join(existing_callbacks)
            if existing_callbacks
            else "https://shieldcraft-ai.com/monitoring"
        ),
    )
    redirect_sign_out = prompt(
        "Comma-separated redirect sign-out URLs",
        (
            ",".join(existing_logouts)
            if existing_logouts
            else "https://shieldcraft-ai.com/"
        ),
    )

    google_client_id = prompt("Google OAuth client ID", secret=False)
    google_client_secret = prompt("Google OAuth client secret", secret=True)

    try:
        amazon_details = (
            boto3.client("cognito-idp", region_name=user_pool_region)
            .describe_identity_provider(
                UserPoolId=user_pool_id,
                ProviderName="LoginWithAmazon",
            )
            .get("IdentityProvider")
        )
        amazon_client_id_default = amazon_details.get("ProviderDetails", {}).get(
            "client_id"
        )
    except ClientError:
        amazon_client_id_default = None

    amazon_client_id = prompt(
        "Login with Amazon client ID",
        amazon_client_id_default,
    )
    amazon_client_secret = prompt("Login with Amazon client secret", secret=True)

    print("Configuring identity providers...")
    ensure_provider(
        user_pool_region,
        user_pool_id,
        "Google",
        "Google",
        ProviderInput(
            client_id=google_client_id,
            client_secret=google_client_secret,
            scopes=["profile", "email", "openid"],
        ),
        attribute_mapping={"email": "email", "name": "name"},
    )
    ensure_provider(
        user_pool_region,
        user_pool_id,
        "LoginWithAmazon",
        "LoginWithAmazon",
        ProviderInput(
            client_id=amazon_client_id,
            client_secret=amazon_client_secret,
            scopes=["profile", "profile:user_id"],
        ),
        attribute_mapping={"email": "email", "name": "name"},
    )

    providers = ["Google", "LoginWithAmazon"]
    update_app_client(
        user_pool_region,
        user_pool_id,
        app_client_id,
        [url.strip() for url in redirect_sign_in.split(",") if url.strip()],
        [url.strip() for url in redirect_sign_out.split(",") if url.strip()],
        providers,
        existing_scopes or ["email", "openid", "profile"],
    )

    secret_region = prompt(
        "Secrets Manager region for Amplify config", DEFAULT_SECRET_REGION
    )
    secret_name = prompt("Secrets Manager secret name", DEFAULT_SECRET_NAME)

    amplify_payload = {
        "Auth": {
            "region": user_pool_region,
            "userPoolId": user_pool_id,
            "userPoolWebClientId": app_client_id,
            "Cognito": {
                "userPoolClientId": app_client_id,
                "loginWith": {
                    "oauth": {
                        "domain": hosted_ui_domain,
                        "providers": providers,
                        "redirectSignIn": [
                            url.strip()
                            for url in redirect_sign_in.split(",")
                            if url.strip()
                        ],
                        "redirectSignOut": [
                            url.strip()
                            for url in redirect_sign_out.split(",")
                            if url.strip()
                        ],
                        "responseType": "code",
                    }
                },
            },
            "oauth": {
                "domain": hosted_ui_domain,
                "scope": list(
                    dict.fromkeys(existing_scopes or ["email", "openid", "profile"])
                ),
                "redirectSignIn": [
                    url.strip() for url in redirect_sign_in.split(",") if url.strip()
                ],
                "redirectSignOut": [
                    url.strip() for url in redirect_sign_out.split(",") if url.strip()
                ],
                "responseType": "code",
            },
        }
    }

    upsert_amplify_secret(secret_region, secret_name, amplify_payload)
    print("All done. The GitHub Actions workflow can now fetch the updated secret.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
