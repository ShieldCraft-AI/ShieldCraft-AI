import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { getFreeProduct, getPaidProduct } from '@site/src/data/guardSuitePricing';

const computescan = getFreeProduct('computescan');
const computeguard = getPaidProduct('computeguard');
const formatUsd = (value?: number) => (value == null ? 'TBA' : `$${value.toLocaleString()}`);

export default function ComputeScanPage() {
    return (
        <ProductPage
            title="ComputeScan  -  GPU Waste Scanner"
            heroBadge="Free CLI"
            heroDescription={
                computescan?.description ??
                'ComputeScan inspects Terraform/SageMaker plans locally to spot GPU waste, idle compute, and inference drift before spend hits prod.'
            }
            metaDescription="ComputeScan is the free GuardSuite CLI that detects GPU waste, idle compute, and AI pipeline mis-sizing before workloads launch."
            stats={[
                { label: 'Delivery', value: 'Local CLI · tfplan input' },
                { label: 'Outputs', value: 'JSON · Markdown · CSV' },
                { label: 'Upsell', value: `ComputeGuard ${formatUsd(computeguard?.marketplace.direct ?? computeguard?.priceUsd)}` },
            ]}
            ctas={[
                { label: 'Download on GitHub', href: 'https://github.com/Dee66/ShieldCraft-ai' },
                { label: 'Read CLI integration notes', href: '/guard-suite/cli-integration', variant: 'secondary' },
                { label: 'Upgrade to ComputeGuard', href: '/products/computeguard', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'What it catches',
                    body: 'ComputeScan ships with heuristics for GPU oversizing, idle clusters, and mismatched AI pipeline topology so you can fix plans before deployment.',
                    bullets: computescan?.includedFeatures ?? [],
                },
                {
                    title: 'Run everywhere',
                    body: 'There is no service to enroll - run the CLI in CI/CD, on developer laptops, or inside pre-commit hooks and share Markdown or CSV summaries instantly.',
                    bullets: [
                        'Deterministic output for merge gates',
                        'Optional SARIF for GitHub code scanning',
                        'Markdown briefs for FinOps + platform leads',
                    ],
                },
                {
                    title: 'Upgrade path',
                    body: 'Promote recurring findings straight into ComputeGuard to unlock FixPack-Lite, GuardScore-backed ledgers, and GuardBoard dashboards.',
                    bullets: [
                        `Direct license ${formatUsd(computeguard?.marketplace.direct ?? computeguard?.priceUsd)}`,
                        `GitHub Marketplace ${formatUsd(computeguard?.marketplace.githubMarketplace)}`,
                        'Bundles include GuardBoard + GuardScore automation',
                    ],
                },
            ]}
        />
    );
}
