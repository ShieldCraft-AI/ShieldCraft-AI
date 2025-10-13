import { test, expect, devices } from '@playwright/test';

test.use({ viewport: devices['Pixel 5'].viewport });

test('mobile navigation opens and closes', async ({ page }) => {
    await page.goto('/');
    const menuBtn = page.locator('button[aria-label="Open navigation menu"]');
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();
    // after opening, a link like 'Pricing' should be visible in mobile nav
    await expect(page.locator('text=Pricing')).toBeVisible({ timeout: 3000 });
    // close the menu
    await menuBtn.click();
    await expect(page.locator('text=Pricing')).toHaveCount(0);
});
