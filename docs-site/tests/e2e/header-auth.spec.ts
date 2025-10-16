import { test, expect } from '@playwright/test';

// This test simulates a signed-in user by pre-populating localStorage with
// the minimal keys `CognitoIdentityServiceProvider.<clientId>.LastAuthUser` and
// `CognitoIdentityServiceProvider.<clientId>.<username>.idToken` where the idToken
// contains a base64-encoded payload with `name` and `email` claims.

const CLIENT_ID = 'TEST_CLIENT_ID';
const USERNAME = 'test-user';
const NAME = 'Test User';
const EMAIL = 'test-user@example.test';

function makeFakeIdToken(payload: Record<string, unknown>) {
    const header = { alg: 'none', typ: 'JWT' };
    const enc = (obj: any) => Buffer.from(JSON.stringify(obj)).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    return `${enc(header)}.${enc(payload)}.`;
}

test('header shows username after client-side navigation and logout clears storage', async ({ browser }) => {
    // Serve the built docs-site from file:// by using the local build path.
    // Playwright browse file:// can be awkward; instead start at http://localhost:3000 if available.
    // But we can load the built index.html from file://
    const idToken = makeFakeIdToken({ name: NAME, email: EMAIL, sub: 'sub-123', cognito_username: USERNAME });

    // Create a new context and inject localStorage snapshot before any page is created.
    const context = await browser.newContext();
    await context.addInitScript(({ clientId, username, idToken }) => {
        try {
            const storagePrefix = `CognitoIdentityServiceProvider.${clientId}`;
            const userPrefix = `${storagePrefix}.${username}`;
            window.localStorage.setItem(`${storagePrefix}.LastAuthUser`, username);
            window.localStorage.setItem(`${userPrefix}.idToken`, idToken);
        } catch (e) {
            // ignore
        }
    }, { clientId: CLIENT_ID, username: USERNAME, idToken });

    const page = await context.newPage();
    // Navigate to the app root (uses Playwright's baseURL which is the served build)
    await page.goto('/', { waitUntil: 'load' });

    // Wait for the test-injected localStorage to be available to the app.
    // This ensures the app has a chance to read the persisted snapshot.
    await page.waitForFunction(() => {
        try {
            return Object.keys(window.localStorage || {}).some((k) => k.endsWith('.LastAuthUser'));
        } catch (e) {
            return false;
        }
    }, { timeout: 5000 });

    // Give the header a bit more time to hydrate and render the user menu.
    const userMenu = page.locator('button[aria-label="User menu"]');
    const loginBtn = page.locator('button[aria-label="Login"]');

    // Wait for either user menu or login button to appear
    await Promise.race([
        userMenu.waitFor({ state: 'visible', timeout: 8000 }).then(() => 'user'),
        loginBtn.waitFor({ state: 'visible', timeout: 8000 }).then(() => 'login')
    ]).catch(() => null);

    const storageKeys = await page.evaluate(() => Object.keys(window.localStorage || {}));
    const userMenuCount = await userMenu.count();
    const loginCount = await loginBtn.count();

    if (userMenuCount === 0 && loginCount === 0) {
        const headerHtml = await page.locator('header').innerHTML().catch(() => '');
        throw new Error(`Header did not render expected buttons. localStorage keys=${JSON.stringify(storageKeys)}, headerHtml=${headerHtml.slice(0, 300)}`);
    }

    let userButton = page.locator('button[aria-label="User menu"]');
    if (userMenuCount > 0) {
        await expect(userButton).toContainText('Test', { timeout: 5000 });
    } else {
        const loginButton = page.locator('button[aria-label="Login"]');
        const text = await loginButton.innerText();
        throw new Error(`Expected user menu but saw Login button instead (text=${text}). localStorage keys=${JSON.stringify(storageKeys)}`);
    }

    // Click a header internal link to perform client-side navigation
    // Ensure the nav link for Dashboard exists and click it.
    const dashboardLink = page.locator('a.sc-nav-pill', { hasText: 'Dashboard' });
    await expect(dashboardLink).toBeVisible();
    await dashboardLink.click();

    // Wait for the SPA route to change to /dashboard (client-side navigation)
    await page.waitForURL(/\/dashboard/, { timeout: 5000 }).catch(() => null);

    // Re-query the user button because the header may have re-rendered
    userButton = page.locator('button[aria-label="User menu"]');
    await expect(userButton).toBeVisible({ timeout: 5000 });
    // Confirm that after navigation the user menu still shows the first name
    await expect(userButton).toContainText('Test', { timeout: 5000 });

    // Open the user dropdown and click Logout
    await userButton.click();
    const logoutButton = page.locator('button', { hasText: 'Logout' });
    await expect(logoutButton).toBeVisible();
    await logoutButton.click();

    // After logout, header should show Login
    await page.waitForSelector('button[aria-label="Login"]', { timeout: 3000 });
    const loginButton = await page.locator('button[aria-label="Login"]');
    await expect(loginButton).toContainText('Login');

    // Confirm storage cleared
    const keys = await page.evaluate(() => Object.keys(window.localStorage));
    const cognitoKeys = keys.filter((k) => k.includes('CognitoIdentityServiceProvider'));
    expect(cognitoKeys.length).toBe(0);
});
