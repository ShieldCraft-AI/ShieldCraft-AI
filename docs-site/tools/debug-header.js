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
    const page = await browser.newPage();

    await page.addInitScript(({ clientId, username, idToken }) => {
      try {
        const storagePrefix = `CognitoIdentityServiceProvider.${clientId}`;
        const userPrefix = `${storagePrefix}.${username}`;
        window.localStorage.setItem(`${storagePrefix}.LastAuthUser`, username);
        window.localStorage.setItem(`${userPrefix}.idToken`, idToken);
      } catch (e) {
        console.error('initScript error', e);
      }
    }, { clientId: CLIENT_ID, username: USERNAME, idToken });

    const url = 'http://127.0.0.1:3100/';
    console.log('Navigating to', url);
    await page.goto(url, { waitUntil: 'load', timeout: 10000 });
    await page.waitForTimeout(600);

    const storageKeys = await page.evaluate(() => Object.keys(window.localStorage || {}));
    console.log('localStorage keys:', storageKeys);

    const headerHtml = await page.locator('header').innerHTML().catch(() => '');
    console.log('header innerHTML (first 600 chars):', headerHtml.slice(0, 600));

    const userMenu = await page.locator('button[aria-label="User menu"]').count();
    const loginBtn = await page.locator('button[aria-label="Login"]').count();
    console.log('userMenu count:', userMenu, 'loginBtn count:', loginBtn);

    if (userMenu > 0) {
      const text = await page.locator('button[aria-label="User menu"]').innerText();
      console.log('userMenu text:', text);
    } else if (loginBtn > 0) {
      const text = await page.locator('button[aria-label="Login"]').innerText();
      console.log('loginButton text:', text);
    }

    await browser.close();
  } catch (err) {
    console.error('debug script failed', err);
    process.exit(2);
  }
})();
