"""
AWS Cognito authentication stack for ShieldCraft AI static site.
Provides OAuth2 social identity provider integration without requiring a backend server.
"""

from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_cognito as cognito,
)
from constructs import Construct


class AuthStack(Stack):
    """
    Cognito User Pool with social identity providers for static site authentication.

    Features:
    - Google, GitHub, Microsoft social login
    - Email/password fallback
    - JWT token-based authentication
    - Client-side OAuth2 flow (no backend required)
    """

    def __init__(
        self, scope: Construct, construct_id: str, domain_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # User Pool - stores authenticated users
        self.user_pool = cognito.UserPool(
            self,
            "ShieldCraftUserPool",
            user_pool_name="shieldcraft-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=False,  # Email-only for simplicity
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True, mutable=True
                ),  # MUST be mutable for OAuth
                given_name=cognito.StandardAttribute(required=False, mutable=True),
                family_name=cognito.StandardAttribute(required=False, mutable=True),
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.RETAIN,  # Don't delete users on stack destroy
        )

        # Cognito Domain for Hosted UI
        # Format: https://<domain-prefix>.auth.<region>.amazoncognito.com
        cognito_domain = self.user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="shieldcraft-auth"  # Must be globally unique
            ),
        )

        # App Client - represents your static site
        # Uses Authorization Code Grant with PKCE (secure for SPAs)
        self.user_pool_client = self.user_pool.add_client(
            "ShieldCraftWebClient",
            user_pool_client_name="shieldcraft-web",
            auth_flows=cognito.AuthFlow(
                user_password=True,  # Allow email/password
                user_srp=True,  # Secure Remote Password (more secure than password)
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,  # Required for social login
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=[
                    f"https://{domain_name}/dashboard",  # Post-login redirect
                    f"https://{domain_name}/auth/callback",  # Alternative callback
                    "http://localhost:3000/dashboard",  # Local development
                    "http://localhost:3001/dashboard",  # Alternative local port
                ],
                logout_urls=[
                    f"https://{domain_name}/",
                    "http://localhost:3000/",
                ],
            ),
            # Note: supported_identity_providers must be added AFTER creating the provider
            # See scripts/setup-google-oauth-temp.sh for how to add Google provider
            prevent_user_existence_errors=True,  # Security: don't reveal if user exists
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
        )

        # Identity Providers - Add after setting up in provider consoles
        # See README section for setup instructions

        # Example: Google Identity Provider
        # google_provider = cognito.UserPoolIdentityProviderGoogle(
        #     self,
        #     "Google",
        #     client_id="YOUR_GOOGLE_CLIENT_ID",
        #     client_secret="YOUR_GOOGLE_CLIENT_SECRET",
        #     user_pool=self.user_pool,
        #     scopes=["email", "profile", "openid"],
        #     attribute_mapping=cognito.AttributeMapping(
        #         email=cognito.ProviderAttribute.GOOGLE_EMAIL,
        #         given_name=cognito.ProviderAttribute.GOOGLE_GIVEN_NAME,
        #         family_name=cognito.ProviderAttribute.GOOGLE_FAMILY_NAME,
        #     ),
        # )
        #
        # self.user_pool_client.node.add_dependency(google_provider)

        # Outputs for frontend configuration
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID for Amplify config",
            export_name="ShieldCraftUserPoolId",
        )

        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito App Client ID for Amplify config",
            export_name="ShieldCraftUserPoolClientId",
        )

        CfnOutput(
            self,
            "CognitoHostedUIDomain",
            value=cognito_domain.domain_name,
            description="Cognito Hosted UI domain prefix",
            export_name="ShieldCraftCognitoDomain",
        )

        CfnOutput(
            self,
            "CognitoHostedUIUrl",
            value=f"https://{cognito_domain.domain_name}.auth.{self.region}.amazoncognito.com",
            description="Full Cognito Hosted UI URL",
        )
