import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { getFreeProduct, getPaidProduct, guardSuitePricing } from '@site/src/data/guardSuitePricing';

const vectorscan = getFreeProduct('vectorscan');
const vectorguard = getPaidProduct('vectorguard');
const guardSuiteFull = guardSuitePricing.bundles.find((bundle) => bundle.slug === 'guardsuite-full');

const formatUsd = (value?: number) => (value == null ? 'TBA' : `$${value.toLocaleString()}`);
const vectorguardDirect = formatUsd(vectorguard?.marketplace.direct ?? vectorguard?.priceUsd);
const vectorguardGithub = formatUsd(vectorguard?.marketplace.githubMarketplace);
const bundlePrice = formatUsd(guardSuiteFull?.priceUsd);

export default function VectorScanPage() {
    return (
        <ProductPage
            title="VectorScan  -  Terraform Plan Scanner"
            heroBadge="Free CLI"
            heroDescription="Run `vectorscan tfplan.json` for deterministic drift, encryption, and IAM coverage without uploading plans or creating accounts. Every finding carries IDs that upgrade into paid GuardSuite guardrails."
            metaDescription="VectorScan is ShieldCraft AI's free Terraform plan scanner that spots drift, encryption gaps, and tagging issues in seconds."
            stats={[
                { label: 'Installation time', value: '< 60 seconds' },
                { label: 'Outputs', value: 'JSON · SARIF · Markdown' },
                { label: 'Upsell', value: `VectorGuard ${vectorguardDirect} (Direct) · ${vectorguardGithub} (GitHub)` },
            ]}
            ctas={[
                { label: 'Download on GitHub', href: 'https://github.com/Dee66/ShieldCraft-ai', variant: 'primary' },
                { label: 'View launch notes', href: '/launch/vectorscan', variant: 'secondary' },
                { label: 'Read the VectorScan guide', href: '/guard-suite/vectorscan-overview', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'Why VectorScan',
                    body: 'Engineers need drift visibility without vendor lock-in. VectorScan reads Terraform plan JSON locally and flags gaps before they reach prod.',
                    bullets: [
                        'Detect encryption + logging misconfigurations',
                        'Enforce tagging and cost-center policies automatically',
                        'Emit machine-readable output for CI/CD pipelines',
                    ],
                },
                {
                    title: 'CLI Workflow',
                    body: 'Add VectorScan to CI, merge gates, or ad-hoc reviews. Share SARIF with GitHub code scanning or export Markdown for exec-ready summaries.',
                    bullets: [
                        'vectorscan tfplan.json --format sarif --out findings.sarif',
                        'Attach diff bundles to pull requests for reviewers',
                        'Pipe JSON into VectorGuard + ComputeGuard automations',
                    ],
                },
                {
                    title: 'Outputs engineered for GuardSuite',
                    body: 'Every finding carries IDs and remediation hints. Promote the noisy few into GuardSuite policy packs or ComputeGuard chargeback flows instantly.',
                    bullets: [
                        'Finding IDs map 1:1 with VectorGuard modules',
                        'Optional `--explain` mode describes the blast radius to reviewers',
                        'No telemetry leaves your laptop or CI runner',
                    ],
                },
                {
                    title: 'Upgrade paths',
                    body: `VectorScan is the permanent free tier. Promote critical IDs into VectorGuard ${vectorguardDirect} blueprints or bundle everything inside GuardSuite Full (${bundlePrice}).`,
                    bullets: [
                        'Map findings straight into FixPack-Lite playbooks',
                        'Attach GuardScore outputs to GuardBoard dashboards',
                        'Keep the CLI free forever - no remote execution',
                    ],
                },
            ]}
            comparison={{
                heading: 'VectorScan vs. VectorGuard',
                rows: [
                    {
                        feature: 'Focus',
                        vectorscan: 'Detect drift + misconfigurations',
                        vectorguard: 'Enforce policies + remediate findings',
                    },
                    {
                        feature: 'Delivery',
                        vectorscan: 'CLI · local execution',
                        vectorguard: 'Blueprints, Rego packs, scorecards',
                    },
                    { feature: 'Price', vectorscan: 'Free', vectorguard: `${vectorguardDirect} direct` },
                ],
            }}
            asideNote="Need screenshots or CLI demos? Head to /launch/vectorscan for trimmed assets crafted for Hacker News and marketplaces."
        />
    );
}
