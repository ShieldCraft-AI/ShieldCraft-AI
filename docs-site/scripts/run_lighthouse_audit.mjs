#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import lighthouse from 'lighthouse';
import { launch as launchChrome } from 'chrome-launcher';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(projectRoot, '..');

async function loadConfig() {
    const configPath = path.resolve(__dirname, 'seo-pages.json');
    const configRaw = await fs.readFile(configPath, 'utf8');
    return JSON.parse(configRaw);
}

function parseArgs(defaultBaseUrl) {
    const args = process.argv.slice(2);
    let baseUrl = defaultBaseUrl;
    let outputDir;

    for (let i = 0; i < args.length; i += 1) {
        const arg = args[i];
        if (arg === '--base' && args[i + 1]) {
            baseUrl = args[i + 1];
            i += 1;
        } else if (arg === '--out' && args[i + 1]) {
            outputDir = args[i + 1];
            i += 1;
        } else if (arg === '--help' || arg === '-h') {
            console.log('Usage: node scripts/run_lighthouse_audit.mjs [--base http://localhost:3000] [--out ./analysis/lighthouse/custom]');
            process.exit(0);
        }
    }

    return { baseUrl, outputDir };
}

function sanitizeRoute(route) {
    if (route === '/' || route === '') return 'index';
    return route
        .replace(/[?#].*$/, '')
        .replace(/\/+$/, '')
        .replace(/^\/+/, '')
        .replace(/\//g, '-')
        .replace(/[^a-zA-Z0-9_-]/g, '-');
}

function formatScore(value) {
    if (typeof value !== 'number') return 'n/a';
    return Math.round(value * 100);
}

async function ensureDir(dir) {
    await fs.mkdir(dir, { recursive: true });
}

async function run() {
    const { baseUrl: defaultBaseUrl, routes } = await loadConfig();
    const { baseUrl, outputDir: outArg } = parseArgs(defaultBaseUrl);

    if (!routes || routes.length === 0) {
        throw new Error('No routes defined for Lighthouse audit. Update scripts/seo-pages.json.');
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputDir = path.resolve(repoRoot, outArg ?? path.join('analysis', 'lighthouse', timestamp));
    await ensureDir(outputDir);

    console.log(`[LH] Launching Chrome for audits against ${baseUrl}`);
    const chrome = await launchChrome({ chromeFlags: ['--headless=new', '--no-sandbox'] });

    const summary = [];
    const markdownRows = [];

    try {
        for (const route of routes) {
            const targetUrl = new URL(route, baseUrl).toString();
            console.log(`[LH] Auditing ${targetUrl}`);

            try {
                const runnerResult = await lighthouse(targetUrl, {
                    port: chrome.port,
                    logLevel: 'error',
                    output: ['json', 'html']
                });

                const [jsonReport, htmlReport] = runnerResult.report;
                const { lhr } = runnerResult;
                const slug = sanitizeRoute(route);
                const jsonPath = path.join(outputDir, `${slug}.json`);
                const htmlPath = path.join(outputDir, `${slug}.html`);

                await fs.writeFile(jsonPath, jsonReport, 'utf8');
                await fs.writeFile(htmlPath, htmlReport, 'utf8');

                const categories = lhr?.categories ?? {};
                const metrics = {
                    performance: formatScore(categories?.performance?.score),
                    accessibility: formatScore(categories?.accessibility?.score),
                    'best-practices': formatScore(categories?.['best-practices']?.score),
                    seo: formatScore(categories?.seo?.score),
                    pwa: formatScore(categories?.pwa?.score)
                };

                summary.push({
                    route,
                    finalUrl: lhr?.finalUrl ?? targetUrl,
                    metrics,
                    jsonReport: path.relative(repoRoot, jsonPath),
                    htmlReport: path.relative(repoRoot, htmlPath)
                });

                markdownRows.push(`| ${route} | ${metrics.performance} | ${metrics.accessibility} | ${metrics['best-practices']} | ${metrics.seo} | ${metrics.pwa} |`);
            } catch (auditErr) {
                console.error(`[LH] Failed to audit ${targetUrl}:`, auditErr.message);
                summary.push({ route, finalUrl: targetUrl, error: auditErr.message });
                markdownRows.push(`| ${route} | error | error | error | error | error |`);
            }
        }
    } finally {
        await chrome.kill();
        console.log('[LH] Chrome process closed');
    }

    const summaryJsonPath = path.join(outputDir, 'summary.json');
    const summaryMdPath = path.join(outputDir, 'summary.md');
    const mdContent = [
        `# Lighthouse Audit — ${new Date().toISOString()}`,
        '',
        '| Route | Perf | A11y | Best Practices | SEO | PWA |',
        '| --- | --- | --- | --- | --- | --- |',
        ...markdownRows,
        '',
        '_Scores are percentage values (0–100). PWA only populated when relevant._'
    ].join('\n');

    await fs.writeFile(summaryJsonPath, JSON.stringify({ baseUrl, generatedAt: new Date().toISOString(), summary }, null, 2));
    await fs.writeFile(summaryMdPath, mdContent, 'utf8');

    console.log(`[LH] Reports saved to ${path.relative(repoRoot, outputDir)}`);
}

run().catch((err) => {
    console.error('[LH] Audit failed:', err);
    process.exitCode = 1;
});
