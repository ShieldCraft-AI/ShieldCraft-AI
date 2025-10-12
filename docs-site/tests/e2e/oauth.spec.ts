import { test, expect } from '@playwright/test';

test('oauth redirect capture and finalize path', async ({ page, context }) => {
  // Simulate that capture script stored the callback parameters
  await context.addInitScript(() => {
    try {
      sessionStorage.setItem('__sc_oauth_search', '?code=FAKECODE&state=FAKESTATE');
      sessionStorage.setItem('__sc_oauth_hash', '');
      sessionStorage.setItem('__sc_oauth_href', window.location.origin + '/?code=FAKECODE&state=FAKESTATE');
    } catch (e) {}
  });

  await page.goto('/');

  // Wait briefly - the auth finalize code should detect stored params and attempt to refresh session
  await page.waitForTimeout(1200);

  // At minimum, the page should not crash and should show the site header
  await expect(page.locator('header')).toBeVisible({ timeout: 3000 });
});
