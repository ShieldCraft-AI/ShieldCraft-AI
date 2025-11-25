import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { getFreeProduct, getPaidProduct } from '@site/src/data/guardSuitePricing';

const pipelinescan = getFreeProduct('pipelinescan');
const pipelineguard = getPaidProduct('pipelineguard');
const formatUsd = (value?: number) => (value == null ? 'TBA' : `$${value.toLocaleString()}`);

export default function PipelineScanPage() {
    return (
        <ProductPage
            title="PipelineScan  -  Supply Chain Scanner"
            heroBadge="Free CLI"
            heroDescription={
                pipelinescan?.description ??
                'PipelineScan enforces supply chain baselines across CI/CD by running OPA rules locally - no uploads, no SaaS lock-in.'
            }
            metaDescription="PipelineScan is the free GuardSuite CLI for CI/CD supply-chain scans, missing signing enforcement, and embedded secrets detection."
            stats={[
                { label: 'Delivery', value: 'Local CLI · tfplan / pipeline manifest' },
                { label: 'Rules', value: 'OPA snippets · signing coverage' },
                { label: 'Upsell', value: `PipelineGuard ${formatUsd(pipelineguard?.marketplace.direct ?? pipelineguard?.priceUsd)}` },
            ]}
            ctas={[
                { label: 'Download on GitHub', href: 'https://github.com/Dee66/ShieldCraft-ai' },
                { label: 'Review CLI guardrail layer', href: '/guard-suite/cli-integration', variant: 'secondary' },
                { label: 'Upgrade to PipelineGuard', href: '/products/pipelineguard', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'Baseline coverage',
                    body: 'PipelineScan looks for missing signing enforcement, hard-coded secrets, and weak OPA posture inside CI pipelines before artefacts move downstream.',
                    bullets: pipelinescan?.includedFeatures ?? [],
                },
                {
                    title: 'Deterministic findings',
                    body: 'The CLI emits JSON + Markdown so DevSecOps teams can gate merges or drop evidence into GuardBoard without external services.',
                    bullets: [
                        'OPA decision trace for each violation',
                        'Markdown summary for pull requests',
                        'JSON results for automation',
                    ],
                },
                {
                    title: 'Upgrade path',
                    body: 'Promote policies to PipelineGuard for FixPack-Lite, signing templates, and GuardScore integration across environments.',
                    bullets: [
                        `Direct license ${formatUsd(pipelineguard?.marketplace.direct ?? pipelineguard?.priceUsd)}`,
                        `GitHub Marketplace ${formatUsd(pipelineguard?.marketplace.githubMarketplace)}`,
                        'Bundles pair PipelineGuard with VectorGuard + ComputeGuard',
                    ],
                },
            ]}
        />
    );
}
