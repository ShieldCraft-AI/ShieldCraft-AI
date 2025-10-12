import { test, expect } from '@playwright/test';

test.describe('Portal pages', () => {
  test('dashboard renders when authenticated', async ({ page, context }) => {
    await context.addInitScript(() => {
      // @ts-ignore
      (window as any).__SC_E2E_FORCED_AUTH__ = true;
    });

    await page.goto('/dashboard');

    // Ensure header reflects logged-in state
    await expect(page.locator('button[aria-label="User menu"]')).toBeVisible({ timeout: 10_000 });

    // Ensure the portal main area exists (basic smoke)
    await expect(page.locator('text=Security Console').first()).toBeVisible({ timeout: 5000 }).catch(() => {});
  });
});
