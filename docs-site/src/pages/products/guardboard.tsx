import React from 'react';
import ProductPage from '@site/src/components/guardsuite/ProductPage';
import { guardSuitePricing } from '@site/src/data/guardSuitePricing';

const guardboardBase = guardSuitePricing.guardboard.find((tier) => tier.slug === 'guardboard');
const guardboardPro = guardSuitePricing.guardboard.find((tier) => tier.slug === 'guardboard-pro');
const guardboardEnterprise = guardSuitePricing.guardboard.find((tier) => tier.slug === 'guardboard-enterprise');
const formatUsd = (value?: number, suffix = '') => (value == null ? 'Contact us' : `$${value.toLocaleString()}${suffix}`);

export default function GuardBoardPage() {
    return (
        <ProductPage
            title="GuardBoard  -  Governance Dashboards"
            heroBadge={`Base ${formatUsd(guardboardBase?.priceUsd)} · Pro ${formatUsd(guardboardPro?.subscriptionUsdMonth, '/mo')}`}
            heroDescription="GuardBoard visualizes compliance ledgers, FixPack runs, GuardScore trends, and Pre-flight upsells across GuardSuite products."
            metaDescription="GuardBoard dashboards turn GuardSuite outputs into exec-ready evidence with tiers for local viewers, team collaboration, and enterprise RBAC."
            stats={[
                { label: 'Base', value: formatUsd(guardboardBase?.priceUsd) },
                { label: 'Pro', value: `${formatUsd(guardboardPro?.subscriptionUsdMonth, '/mo')} · ${formatUsd(guardboardPro?.subscriptionUsdYear, '/yr')}` },
                { label: 'Enterprise', value: `${formatUsd(guardboardEnterprise?.subscriptionUsdMonthPerUser, '/mo · user')} SLA ${guardboardEnterprise?.slaHours}h` },
            ]}
            ctas={[
                { label: 'Bundle with GuardSuite kits', href: '/products/guard-suite' },
                {
                    label: 'Contact for GuardBoard Enterprise',
                    href: 'mailto:shieldcraftai@gmail.com?subject=GuardBoard%20Enterprise',
                    variant: 'secondary',
                },
                { label: 'Review GuardSuite docs', href: '/guard-suite/bundle-playbook', variant: 'ghost' },
            ]}
            sections={[
                {
                    title: 'GuardBoard Base',
                    body:
                        'Local dashboard for compliance teams who want to open FixPack history, score trends, and PDF exports without leaving their laptop.',
                    bullets: guardboardBase?.features ?? [],
                },
                {
                    title: 'GuardBoard Pro',
                    body:
                        'Adds collaboration: multi-project workspaces, change history, diffs, and sharing controls so teams can work the same evidence together.',
                    bullets: guardboardPro?.features ?? [],
                },
                {
                    title: 'GuardBoard Enterprise',
                    body:
                        'Enterprise tenants get SSO, RBAC, report APIs, and analytics pipelines plus dedicated SLA coverage for compliance reviews.',
                    bullets: guardboardEnterprise?.features ?? [],
                },
            ]}
            asideNote="Need bundled pricing? GuardSuite Pro and Enterprise kits include GuardBoard so you can ship dashboards with every FixPack run."
        />
    );
}
