#!/bin/bash
# Enable OAuth on User Pool Client

aws cognito-idp update-user-pool-client \
  --region us-east-1 \
  --user-pool-id us-east-1_H6KHkYeES \
  --client-id 2jio5rlqn6r2qe0otrgip4d5bp \
  --allowed-o-auth-flows "code" \
  --allowed-o-auth-scopes "email" "profile" "openid" \
  --allowed-o-auth-flows-user-pool-client \
  --callback-urls "http://localhost:3000/dashboard" "http://localhost:3001/dashboard" "https://shieldcraft-ai.com/dashboard" "https://shieldcraft-ai.com/auth/callback" \
  --logout-urls "http://localhost:3000/" "https://shieldcraft-ai.com/" \
  --supported-identity-providers "Google" "COGNITO"
