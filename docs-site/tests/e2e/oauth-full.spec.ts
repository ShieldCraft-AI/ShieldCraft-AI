import { test, expect } from '@playwright/test';

// This test performs a full Hosted UI OAuth login against a real identity provider.
// It requires the following secrets to be set in the environment (or GitHub Actions secrets):
// - E2E_GOOGLE_EMAIL
// - E2E_GOOGLE_PASSWORD
// Set them carefully in a protected environment. The test will skip if they are missing.

const googleEmail = process.env.E2E_GOOGLE_EMAIL;
const googlePassword = process.env.E2E_GOOGLE_PASSWORD;

test.describe('Full OAuth (real provider) - gated', () => {
    test.skip(!googleEmail || !googlePassword, 'E2E provider credentials not provided');

    test('google hosted-ui flow returns to app and shows authenticated UI', async ({ page }) => {
        // Navigate to the site, open the login dropdown and click Google
        await page.goto('/');

        // Open login menu (try both labels)
        const loginBtn = page.locator('button', { hasText: 'Login' }).first();
        await loginBtn.click();

        // Click Google provider row in dropdown
        const googleRow = page.locator('role=button[name="Sign in with Google"]');
        if (await googleRow.count() === 0) {
            // Fallback: click by text
            await page.click('text=Google');
        } else {
            await googleRow.click();
        }

        // Now the browser should navigate to Google's login page (hosted UI -> Google).
        // Google blocks automation frequently; this test may fail in some CI environments.
        // Fill identifier and password.
        await page.waitForLoadState('networkidle');

        // Google login selectors (best-effort) - may be rate-limited by Google.
        try {
            await page.fill('input[type="email"]', googleEmail, { timeout: 8000 });
            await page.click('button:has-text("Next")');
            await page.fill('input[type="password"]', googlePassword, { timeout: 8000 });
            await page.click('button:has-text("Next")');
        } catch (e) {
            // If Google's login UI changed or interaction is blocked, fail the test with a helpful message
            throw new Error('Google login automation failed  -  check selectors and anti-bot protections.');
        }

        // After successful login, verify we return to the app and see the user menu
        await page.waitForURL('**/', { timeout: 20000 });
        await expect(page.locator('button[aria-label="User menu"]')).toBeVisible({ timeout: 10000 });
    });
});
