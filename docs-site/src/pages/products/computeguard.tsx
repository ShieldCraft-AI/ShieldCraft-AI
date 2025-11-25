import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { getPaidProduct, getFreeProduct } from '@site/src/data/guardSuitePricing';

const computeguard = getPaidProduct('computeguard');
const computescan = getFreeProduct('computescan');
const formatUsd = (value?: number) => (value == null ? 'TBA' : `$${value.toLocaleString()}`);
const directPrice = formatUsd(computeguard?.marketplace.direct ?? computeguard?.priceUsd);
const githubPrice = formatUsd(computeguard?.marketplace.githubMarketplace);

export default function ComputeGuardPage() {
    return (
        <ProductPage
            title="ComputeGuard  -  FinOps Enforcement"
            heroBadge={`Direct ${directPrice}`}
            heroDescription="Stop GPU waste and runaway inference costs with FixPack-Lite, GuardScore-backed drift ledgers, and chargeback-ready automation."
            metaDescription="ComputeGuard enforces FinOps guardrails with direct $99 licensing, GitHub Marketplace distribution, and deep GPU governance templates."
            stats={[
                { label: 'Direct', value: directPrice },
                { label: 'GitHub Marketplace', value: githubPrice },
                { label: 'Targets', value: 'GPU · inference · batch jobs' },
            ]}
            ctas={[
                { label: `Purchase on Gumroad (${directPrice})`, href: 'https://shieldcraft-ai.gumroad.com/l/computeguard-lite' },
                { label: 'Bundle with GuardSuite kits', href: '/products/guard-suite', variant: 'secondary' },
                { label: 'Read CLI integration notes', href: '/guard-suite/cli-integration', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'Blueprint scope',
                    body: 'Wire AWS Batch, SageMaker, and custom GPU fleets into a single governance loop that enforces budgets before workloads start.',
                    bullets: [
                        'Admission controls for expensive instance types',
                        'Idle cluster detection with automated suspension',
                        'Chargeback tagging templates for finance',
                    ],
                },
                {
                    title: 'ComputeProbe CLI (free lead magnet)',
                    body: `${computescan?.name ?? 'ComputeScan'} ships for free so FinOps signals flow before any paid seat. Share CLI findings in Slack or Jira instantly.`,
                    bullets: [
                        'Detect GPU nodes without budgets or owners',
                        'Export CSV for finance and Markdown for exec briefs',
                        'Zero accounts required  -  runs locally',
                    ],
                },
                {
                    title: 'GuardBoard-ready telemetry',
                    body: 'Drop-in middleware for inference gateways emits telemetry to GuardScore so GuardBoard can trend spend vs. policy posture.',
                    bullets: [
                        'Language bindings for Python, Node.js, Go',
                        'Signed ledger of every GPU allocation',
                        'Hooks into GuardSuite FinOps dashboards',
                    ],
                },
            ]}
        />
    );
}
