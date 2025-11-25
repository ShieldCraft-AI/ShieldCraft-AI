import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';

export default function ModelGuardPage() {
    return (
        <ProductPage
            title="ModelGuard  -  Prediction Integrity"
            heroBadge="$199 · $799"
            heroDescription="Validate foundation model outputs, log evidence, and align with EU AI Act obligations using executable governance kits."
            metaDescription="ModelGuard keeps GenAI deployments compliant with Governance Blueprints ($199) and Validation Kits ($799)."
            stats={[
                { label: 'Lite SKU', value: '$199 Blueprint' },
                { label: 'Enterprise SKU', value: '$799 Kit + Ledger' },
                { label: 'Controls', value: 'Bias · safety · audit logging' },
            ]}
            ctas={[
                { label: 'Download sample ledger', href: '/guard-suite/cli-integration', variant: 'secondary' },
                { label: 'Pre-order Governance Blueprint ($199)', href: 'https://shieldcraft-ai.gumroad.com/l/modelguard-lite' },
                { label: 'Contact sales', href: 'mailto:shieldcraftai@gmail.com' },
            ]}
            sections={[
                {
                    title: 'Blueprint deliverables',
                    body: 'Pre-built evaluation notebooks, prompt-run ledgers, and policy mappings so ML teams can prove due diligence.',
                    bullets: [
                        'Guardrails for jailbreak, hallucination, leakage tests',
                        'Templates that align to EU AI Act tiers',
                        'Integration path with ShieldCraft eval harness',
                    ],
                },
                {
                    title: 'ModelCheck CLI (free lead magnet)',
                    body: 'Ship a CLI with every model artifact so teams can reproduce bias/safety checks locally, then attach evidence to ModelGuard ledgers.',
                    bullets: [
                        'Runs alongside shielded datasets  -  no uploads',
                        'Exports JSON for GuardSuite dashboards and PDF briefs for auditors',
                        'Expose CLI telemetry for affiliate partners (20% lifetime)',
                    ],
                },
                {
                    title: 'Enterprise validation kit',
                    body: 'Adds ledger automation, cross-cloud connectors, and automated evidence packaging for auditors.',
                    bullets: [
                        'Signed ledger with immutability hooks',
                        'API for exporting into GRC tooling',
                        'Weekly analyst-ready digest emails',
                    ],
                },
            ]}
        />
    );
}
