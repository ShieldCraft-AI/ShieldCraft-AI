#!/usr/bin/env node
/**
 * Simple staging check that performs a refresh_token grant against Cognito
 * to validate refresh behavior in staging. Intended to be run in a secure
 * staging environment with environment variables set.
 *
 * Required env vars:
 *  - AUTH_DOMAIN (e.g. shieldcraft-auth.auth.us-east-1.amazoncognito.com)
 *  - CLIENT_ID
 *  - REFRESH_TOKEN
 *
 * Exit codes:
 *  0 - success (access token returned)
 *  2 - missing env
 *  3 - HTTP error / unexpected response
 */

const domain = process.env.AUTH_DOMAIN;
const clientId = process.env.CLIENT_ID;
const refreshToken = process.env.REFRESH_TOKEN;

if (!domain || !clientId || !refreshToken) {
  console.error('Missing required env vars. Please set AUTH_DOMAIN, CLIENT_ID and REFRESH_TOKEN');
  process.exit(2);
}

const url = `https://${domain}/oauth2/token`;
const params = new URLSearchParams();
params.set('grant_type', 'refresh_token');
params.set('client_id', clientId);
params.set('refresh_token', refreshToken);

(async () => {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
      body: params.toString(),
    });
    if (!res.ok) {
      console.error('HTTP error from token endpoint', res.status, await res.text());
      process.exit(3);
    }
    const json = await res.json().catch(() => null);
    if (!json || !json.access_token) {
      console.error('No access_token in response', json);
      process.exit(3);
    }
    console.log('Refresh successful. access_token length=', json.access_token.length);
    process.exit(0);
  } catch (err) {
    console.error('Request failed', String(err));
    process.exit(3);
  }
})();
