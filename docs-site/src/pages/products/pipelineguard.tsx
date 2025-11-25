import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { getPaidProduct } from '@site/src/data/guardSuitePricing';

const pipelineguard = getPaidProduct('pipelineguard');
const formatUsd = (value?: number) => (value == null ? 'TBA' : `$${value.toLocaleString()}`);
const directPrice = formatUsd(pipelineguard?.marketplace.direct ?? pipelineguard?.priceUsd);
const gumroadPrice = formatUsd(pipelineguard?.marketplace.gumroad);
const githubPrice = formatUsd(pipelineguard?.marketplace.githubMarketplace);

export default function PipelineGuardPage() {
    return (
        <ProductPage
            title="PipelineGuard  -  Supply Chain Guardrails"
            heroBadge={`Direct ${directPrice}`}
            heroDescription="PipelineGuard adds FixPack-Lite, GuardScore integration, and signing enforcement templates for end-to-end CI/CD hardening."
            metaDescription="PipelineGuard enforces CI/CD supply-chain guardrails with FixPack-Lite, GuardScore integration, and signing templates ready for GuardBoard."
            stats={[
                { label: 'Direct/Gumroad', value: `${directPrice} · ${gumroadPrice}` },
                { label: 'GitHub Marketplace', value: githubPrice },
                { label: 'Includes', value: 'FixPack-Lite · GuardScore · signing templates' },
            ]}
            ctas={[
                { label: `Purchase on Gumroad (${gumroadPrice})`, href: 'https://shieldcraft-ai.gumroad.com/l/pipelineguard' },
                {
                    label: `GitHub Marketplace interest (${githubPrice})`,
                    href: 'mailto:shieldcraftai@gmail.com?subject=PipelineGuard%20GitHub%20Marketplace',
                    variant: 'secondary',
                },
                { label: 'Bundle options', href: '/products/guard-suite', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'FixPack-Lite for pipelines',
                    body: 'Turn every PipelineScan violation into an executable FixPack with remediation metadata, reviewers, and GuardScore weighting.',
                    bullets: pipelineguard?.includes ?? [],
                },
                {
                    title: 'Signing + provenance templates',
                    body: 'Drop in Sigstore/Cosign templates, attestation policies, and drift reports for every build stage.',
                    bullets: [
                        'Reusable Sigstore policy packs',
                        'Provenance attestation modules',
                        'Ledger entries for GuardBoard dashboards',
                    ],
                },
                {
                    title: 'Sharing & bundles',
                    body: 'Bundle PipelineGuard with VectorGuard + ComputeGuard for unified scoring or subscribe to GuardSuite Enterprise for GuardBoard Enterprise access.',
                    bullets: [
                        'GuardSuite Full includes PipelineGuard',
                        'GuardSuite Pro adds FixPack-Pro + GuardBoard Base',
                        'Enterprise kit layers GuardBoard Enterprise + GuardScore engine',
                    ],
                },
            ]}
        />
    );
}
