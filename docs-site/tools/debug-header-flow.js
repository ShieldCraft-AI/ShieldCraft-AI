const { chromium } = require('playwright');

(async () => {
  try {
    const CLIENT_ID = 'TEST_CLIENT_ID';
    const USERNAME = 'test-user';
    const NAME = 'Test User';
    const EMAIL = 'test-user@example.test';

    const makeFakeIdToken = (payload) => {
      const header = { alg: 'none', typ: 'JWT' };
      const enc = (obj) => Buffer.from(JSON.stringify(obj)).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
      return `${enc(header)}.${enc(payload)}.`;
    };

    const idToken = makeFakeIdToken({ name: NAME, email: EMAIL, sub: 'sub-123', cognito_username: USERNAME });

    const browser = await chromium.launch();
    const context = await browser.newContext();

    await context.addInitScript(({ clientId, username, idToken }) => {
      try {
        const storagePrefix = `CognitoIdentityServiceProvider.${clientId}`;
        const userPrefix = `${storagePrefix}.${username}`;
        window.localStorage.setItem(`${storagePrefix}.LastAuthUser`, username);
        window.localStorage.setItem(`${userPrefix}.idToken`, idToken);
      } catch (e) {
        console.error('initScript error', e);
      }
    }, { clientId: CLIENT_ID, username: USERNAME, idToken });

    const page = await context.newPage();
    const base = 'http://127.0.0.1:3100/';
    console.log('goto', base);
    await page.goto(base, { waitUntil: 'load', timeout: 10000 });
    await page.waitForTimeout(500);

    const keys1 = await page.evaluate(() => Object.keys(window.localStorage || {}));
    console.log('after load localStorage keys:', keys1);
    const headerHtml1 = await page.locator('header').innerHTML().catch(() => '');
    console.log('header snapshot (1):', headerHtml1.slice(0, 400));
    const userMenuCount1 = await page.locator('button[aria-label="User menu"]').count();
    const loginCount1 = await page.locator('button[aria-label="Login"]').count();
    console.log('userMenuCount1, loginCount1', userMenuCount1, loginCount1);
    if (userMenuCount1 > 0) console.log('userMenu text:', await page.locator('button[aria-label="User menu"]').innerText());

    // click Dashboard link if present
    const dashboard = page.locator('a.sc-nav-pill', { hasText: 'Dashboard' });
    if (await dashboard.count() > 0) {
      console.log('clicking dashboard');
      await dashboard.first().click();
    } else {
      console.log('dashboard link not found');
    }

    await page.waitForTimeout(800);
    console.log('url after click', page.url());
    const keys2 = await page.evaluate(() => Object.keys(window.localStorage || {}));
    console.log('after nav localStorage keys:', keys2);
    const headerHtml2 = await page.locator('header').innerHTML().catch(() => '');
    console.log('header snapshot (2):', headerHtml2.slice(0, 400));
    const userMenuCount2 = await page.locator('button[aria-label="User menu"]').count();
    const loginCount2 = await page.locator('button[aria-label="Login"]').count();
    console.log('userMenuCount2, loginCount2', userMenuCount2, loginCount2);
    if (userMenuCount2 > 0) console.log('userMenu text2:', await page.locator('button[aria-label="User menu"]').innerText());

    if (userMenuCount2 > 0) {
      await page.locator('button[aria-label="User menu"]').click();
      await page.waitForTimeout(200);
      const logout = page.locator('button', { hasText: 'Logout' });
      if (await logout.count() > 0) {
        console.log('clicking logout');
        await logout.first().click();
      } else {
        console.log('logout button not found');
      }
    }

    await page.waitForTimeout(500);
    const keys3 = await page.evaluate(() => Object.keys(window.localStorage || {}));
    console.log('after logout localStorage keys:', keys3);
    const headerHtml3 = await page.locator('header').innerHTML().catch(() => '');
    console.log('header snapshot (3):', headerHtml3.slice(0, 400));

    await browser.close();
  } catch (err) {
    console.error('debug flow failed', err);
    process.exit(2);
  }
})();
