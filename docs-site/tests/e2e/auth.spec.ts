import { test, expect, type Page } from '@playwright/test';

test.describe('E2E auth header', () => {
    test('header updates when authenticated and after logout', async ({ page, context, baseURL }) => {
        // Force the app to consider the user authenticated before any code runs.
        await context.addInitScript(() => {
            // @ts-ignore - test-only global
            (window as any).__SC_E2E_FORCED_AUTH__ = true;
        });

        await page.goto('/');

        // Wait for the header to show the user menu
        const userMenu = page.locator('button[aria-label="User menu"]');
        await expect(userMenu).toBeVisible({ timeout: 10_000 });

        // Now simulate logout: clear the forced flag and emit auth-changed
        await context.addInitScript(() => {
            // @ts-ignore
            (window as any).__SC_E2E_FORCED_AUTH__ = false;
        });

        await page.evaluate(() => {
            try {
                window.dispatchEvent(new CustomEvent('sc-auth-changed', { detail: { value: false } }));
            } catch (e) {
                // ignore
            }
        });

        // The header should now show Login text/button
        await expect(page.locator('text=Login')).toBeVisible({ timeout: 5000 });
    });

});

const loginButton = () => ({ name: /login/i });
const googleEmail = process.env.E2E_GOOGLE_EMAIL;
const googlePassword = process.env.E2E_GOOGLE_PASSWORD;

async function resetClientState(page: Page) {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => {
        try { localStorage.clear(); } catch { /* ignore */ }
        try { sessionStorage.clear(); } catch { /* ignore */ }
        try { delete (window as any).__SC_E2E_FORCED_AUTH__; } catch { /* ignore */ }
    });
}

async function clickFirstAvailable(page: Page, selectors: string[]) {
    for (const selector of selectors) {
        const locator = page.locator(selector);
        if (await locator.count()) {
            await locator.first().click();
            return;
        }
    }
    throw new Error(`None of the selectors resolved: ${selectors.join(', ')}`);
}

async function completeGoogleOAuth(popup: Page, email: string, password: string) {
    await popup.waitForLoadState('domcontentloaded', { timeout: 20_000 });

    const useAnotherAccount = popup.getByRole('button', { name: /use another account/i });
    if (await useAnotherAccount.count()) {
        await useAnotherAccount.click();
        await popup.waitForLoadState('domcontentloaded');
    }

    const emailField = popup.locator('input[type="email"], input[name="identifier"]');
    await emailField.waitFor({ state: 'visible', timeout: 20_000 });
    await emailField.fill(email, { timeout: 0 });
    await clickFirstAvailable(popup, ['#identifierNext', 'button:has-text("Next")', 'button:has-text("Weiter")']);

    const passwordField = popup.locator('input[type="password"], input[name="password"]');
    await passwordField.waitFor({ state: 'visible', timeout: 25_000 });
    await passwordField.fill(password, { timeout: 0 });
    await clickFirstAvailable(popup, ['#passwordNext', 'button:has-text("Next")', 'button:has-text("Weiter")']);

    await popup.waitForLoadState('networkidle', { timeout: 30_000 }).catch(() => { /* ignore */ });
}

test.describe('ShieldCraft login entry points', () => {
    test('renders social provider buttons in the menu', async ({ page }) => {
        await resetClientState(page);
        await page.getByRole('button', loginButton()).click();
        await expect(page.getByRole('button', { name: /sign in with google/i })).toBeVisible();
        await expect(page.getByRole('button', { name: /sign in with amazon/i })).toBeVisible();
    });

    test('simulated auth handshake surfaces authenticated navigation', async ({ page }) => {
        await resetClientState(page);
        await page.evaluate(() => {
            (window as any).__SC_E2E_FORCED_AUTH__ = true;
        });
        await page.getByRole('button', loginButton()).click();
        await page.evaluate(() => {
            const event = new CustomEvent('sc-auth-changed', { detail: { value: true } });
            window.dispatchEvent(event);
        });
        await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible();
        await page.evaluate(() => { delete (window as any).__SC_E2E_FORCED_AUTH__; });
    });
});

test.describe('Cognito hosted UI redirects', () => {
    test.describe.configure({ mode: 'serial' });

    test.skip(!googleEmail || !googlePassword, 'E2E Google credentials not provided');

    test('Google hosted UI login completes end-to-end', async ({ page, context, browserName }) => {
        test.skip(browserName !== 'chromium', 'Full hosted UI login validated on Chromium only.');
        test.setTimeout(120_000);

        await context.clearCookies();
        await context.clearPermissions();
        await resetClientState(page);

        await page.getByRole('button', loginButton()).click();

        const [popup] = await Promise.all([
            context.waitForEvent('page'),
            page.getByRole('button', { name: /sign in with google/i }).click(),
        ]);

        await completeGoogleOAuth(popup, googleEmail!, googlePassword!);

        await popup.waitForEvent('close', { timeout: 60_000 }).catch(() => undefined);
        if (!popup.isClosed()) {
            await popup.close({ runBeforeUnload: true }).catch(() => undefined);
        }

        await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible({ timeout: 45_000 });

        await expect.poll(async () => await page.evaluate(() => window.localStorage.getItem('sc_logged_in')), { timeout: 30_000 }).toBe('1');

        await page.getByRole('button', loginButton()).click();
        await expect(page.getByRole('link', { name: /security console/i })).toBeVisible({ timeout: 15_000 });
        await page.getByRole('button', { name: /logout/i }).click();

        await expect.poll(async () => await page.evaluate(() => window.localStorage.getItem('sc_logged_in')), { timeout: 30_000 }).toBeNull();
    });
});
