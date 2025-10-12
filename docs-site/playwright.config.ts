import { defineConfig, devices } from '@playwright/test';

const DEFAULT_PORT = process.env.E2E_PORT ? Number(process.env.E2E_PORT) : 3100;
const baseURL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${DEFAULT_PORT}`;

export default defineConfig({
    testDir: './tests/e2e',
    snapshotDir: './tests/e2e/__snapshots__',
    timeout: 60_000,
    retries: process.env.CI ? 1 : 0,
    workers: process.env.CI ? 2 : undefined,
    expect: {
        timeout: 5_000,
    },
    use: {
        baseURL,
        trace: 'on-first-retry',
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
    },
    reporter: [
        ['html', { outputFolder: 'playwright-report', open: process.env.CI ? 'never' : 'on-failure' }],
        ['list']
    ],
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        {
            name: 'firefox',
            use: { ...devices['Desktop Firefox'] },
        },
        {
            name: 'webkit',
            use: { ...devices['Desktop Safari'] },
        },
    ],
    webServer: {
        command: `npm run serve -- --dir build --host 127.0.0.1 --port ${DEFAULT_PORT}`,
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        stdout: 'pipe',
        stderr: 'pipe',
        timeout: 120_000,
    },
});
