import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { getPaidProduct } from '@site/src/data/guardSuitePricing';

const vectorguard = getPaidProduct('vectorguard');
const formatUsd = (value?: number) => (value == null ? 'TBA' : `$${value.toLocaleString()}`);
const directPrice = formatUsd(vectorguard?.marketplace.direct ?? vectorguard?.priceUsd);
const gumroadPrice = formatUsd(vectorguard?.marketplace.gumroad);
const githubPrice = formatUsd(vectorguard?.marketplace.githubMarketplace);

export default function VectorGuardPage() {
    return (
        <ProductPage
            title="VectorGuard  -  Zero-Trust Blueprint"
            heroBadge={`Direct ${directPrice}`}
            heroDescription="Convert VectorScan findings into Zero-Trust enforcement packs with FixPack-Lite, GuardScore outputs, and compliance ledgers ready for GuardBoard."
            metaDescription="VectorGuard turns Terraform drift findings into executable guardrails with FixPack-Lite, GuardScore integration, and ledger-backed evidence."
            stats={[
                { label: 'Direct/Gumroad', value: `${directPrice} · ${gumroadPrice}` },
                { label: 'GitHub Marketplace', value: githubPrice },
                { label: 'Delivery', value: 'Terraform · Rego · Python SDK' },
            ]}
            ctas={[
                { label: `Purchase on Gumroad (${gumroadPrice})`, href: 'https://shieldcraft-ai.gumroad.com/l/vectorguard-lite' },
                {
                    label: `GitHub Marketplace interest (${githubPrice})`,
                    href: 'mailto:shieldcraftai@gmail.com?subject=VectorGuard%20GitHub%20Marketplace',
                    variant: 'secondary',
                },
                { label: 'Review policy packs', href: '/guard-suite/vectorguard-blueprints', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'Blueprint contents',
                    body: 'Each pack ships with opinionated Terraform modules, Rego policies, and playbooks so you can enforce guardrails without months of authoring.',
                    bullets: [
                        'Map tfplan drift to remediation modules',
                        'Signed scorecards with executive summaries',
                        'Ledger-backed history for every change',
                    ],
                },
                {
                    title: 'GuardBoard-ready evidence',
                    body: 'VectorGuard ships with GuardScore integration so every FixPack promotion publishes a signed ledger entry plus dashboards inside GuardBoard tiers.',
                    bullets: [
                        'Multi-account AWS deployment guidance',
                        'Budget impact modeling with GuardDuty/Config inputs',
                        'SOC 2 + AI Act control mapping',
                    ],
                },
                {
                    title: 'Upgrade process',
                    body: 'VectorScan findings are tagged with remediation IDs. Run `vectorguard promote <findingId>` to bundle IaC modules and regression tests automatically.',
                    bullets: [
                        'Keeps the free VectorScan CLI in place for detection',
                        'Attaches $19 Pre-flight Check upsells to thank-you pages',
                        'Share ledger-backed results with Security + FinOps leaders',
                    ],
                },
            ]}
            asideNote="Still experimenting? Stay on VectorScan for detection, then upgrade a single policy to see Zero-Trust evidence generation in action."
        />
    );
}
