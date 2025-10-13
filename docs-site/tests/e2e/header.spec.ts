import { test, expect } from '@playwright/test';

test.describe('Header interactions', () => {
    test('shows correct links when logged out', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('text=Pricing')).toBeVisible({ timeout: 5000 });
        await expect(page.locator('text=Login')).toBeVisible({ timeout: 5000 });
    });

    test('logout flow hides user menu', async ({ page, context }) => {
        await context.addInitScript(() => { (window as any).__SC_E2E_FORCED_AUTH__ = true; });
        await page.goto('/');
        const userBtn = page.locator('button[aria-label="User menu"]');
        await expect(userBtn).toBeVisible({ timeout: 5000 });

        // simulate clicking logout by dispatching auth-changed to false
        await page.evaluate(() => {
            try { window.dispatchEvent(new CustomEvent('sc-auth-changed', { detail: { value: false } })); } catch (e) { }
        });

        await expect(page.locator('text=Login')).toBeVisible({ timeout: 5000 });
    });
});
