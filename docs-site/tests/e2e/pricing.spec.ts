import { test, expect } from '@playwright/test';

test('pricing page loads and shows pricing header', async ({ page }) => {
    await page.goto('/pricing');
    await expect(page.locator('h1, h2, text=Pricing')).toBeVisible({ timeout: 5000 });
});
