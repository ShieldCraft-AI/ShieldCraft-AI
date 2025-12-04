import { useEffect } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import type { ReactNode } from 'react';
import { guardSuitePricing } from '@site/src/data/guardSuitePricing';
import React from 'react';

const DOC_LINKS = [
    {
        label: 'GuardSuite Documentation Index',
        description: 'Track required GuardSuite documentation pages and their completion status.',
        href: '/guard-suite',
    },
    {
        label: 'VectorScan Overview',
        description: 'Install, authenticate, and run the free Terraform plan scanner.',
        href: '/guard-suite/vectorscan-overview',
    },
    {
        label: 'VectorGuard Policy Packs',
        description: 'Understand the Zero-Trust blueprint catalog and upgrade path.',
        href: '/guard-suite/vectorguard-blueprints',
    },
    {
        label: 'CLI Guardrail Layer',
        description: 'Wire GuardSuite CLIs into CI/CD and tfplan workflows.',
        href: '/guard-suite/cli-integration',
    },
    {
        label: 'Bundle Playbook',
        description: 'Deploy the full Guard Suite Pack with FinOps and governance guardrails.',
        href: '/guard-suite/bundle-playbook',
    },
];

const FUNNEL_STEPS = [
    {
        label: 'Step 1',
        title: 'Launch & Awareness',
        body: 'Show HN, LinkedIn drops, and marketplace listings point to /launch/vectorscan.',
    },
    {
        label: 'Step 2',
        title: 'VectorScan Adoption',
        body: 'Users download the free CLI, see drift + encryption findings, and tag upgrades.',
    },
    {
        label: 'Step 3',
        title: 'VectorGuard Upgrade',
        body: 'Modal + banner redirect to paid SKUs (Lite $79 · Enterprise $449) and FinOps packs.',
    },
    {
        label: 'Step 4',
        title: 'Full Suite Expansion',
        body: 'Offer GuardSuite bundles ($249+) and $19 pre-flight upsell on confirmation screens.',
    },
];

const formatUsd = (value?: number, suffix = ''): string => {
    if (value == null) return 'Contact us';
    return `$${value.toLocaleString()}${suffix}`;
};

const slugToLabel = (slug: string): string => {
    const collections = [
        guardSuitePricing.freeProducts,
        guardSuitePricing.paidProducts,
        guardSuitePricing.proComponents,
        guardSuitePricing.guardboard,
    ];

    for (const collection of collections) {
        const match = collection.find((item) => item.slug === slug);
        if (match) return match.name;
    }

    return slug;
};

const formatBundleIncludes = (includes: string[]): string[] => {
    return includes.flatMap((entry) => {
        if (entry === 'all_free_products') {
            return [
                `${guardSuitePricing.freeProducts.length} × Free CLIs (${guardSuitePricing.freeProducts.map((p) => p.name).join(', ')})`,
            ];
        }

        return [slugToLabel(entry)];
    });
};

const PricePill = ({ children }: { children: ReactNode }) => <span className="guardSuitePricePill">{children}</span>;

const activePaidProducts = guardSuitePricing.paidProducts.filter((product) => product.status !== 'future');
const futurePaidProducts = guardSuitePricing.paidProducts.filter((product) => product.status === 'future');

const paidDirectPrices = activePaidProducts
    .map((product) => product.marketplace.direct ?? product.priceUsd)
    .filter((value): value is number => typeof value === 'number');

const minPaidPrice = paidDirectPrices.length ? Math.min(...paidDirectPrices) : undefined;
const maxPaidPrice = paidDirectPrices.length ? Math.max(...paidDirectPrices) : undefined;
const bundleNames = guardSuitePricing.bundles.map((bundle) => bundle.name).join(' · ');
const freeCliNames = guardSuitePricing.freeProducts.map((product) => product.name).join(' · ');

const heroStats = [
    { label: 'Free CLIs', value: freeCliNames },
    {
        label: 'Paid guardrails',
        value: `${formatUsd(minPaidPrice)} – ${formatUsd(maxPaidPrice)} (direct)`,
    },
    { label: 'Bundles & kits', value: bundleNames },
];

export default function GuardSuitePage(): ReactNode {
    useEffect(() => {
        if (typeof document === 'undefined') return undefined;
        const body = document.body;
        body.classList.add('aurora-surface');
        return () => {
            body.classList.remove('aurora-surface');
        };
    }, []);

    return (
        <Layout
            title="Guard Suite"
            description="Guard Suite pricing universe  -  free CLIs, paid guardrails, GuardBoard, pro components, and enterprise bundles.">
            <main className="guardSuitePage">
                <section className="guardSuiteHero">
                    <div className="guardSuiteHero__eyebrow">GuardSuite Pricing Universe</div>
                    <h1>Executable governance across scanners, guardrails, GuardBoard, and bundles.</h1>
                    <p>
                        Every GuardSuite surface now shares a single pricing source of truth: three free lead-magnet CLIs, paid guardrail packs, GuardBoard
                        tiers, pro-grade remediation components, and bundles ready for Gumroad, GitHub Marketplace, or direct procurement.
                    </p>
                    <div className="guardSuiteHero__actions">
                        <Link className="button button--primary" to="/products/vectorscan">
                            Download VectorScan (Free)
                        </Link>
                        <Link className="button button--secondary" to="/guard-suite#paid-guardrails" data-noBrokenLinkCheck>
                            Browse paid guardrails
                        </Link>
                        <Link className="button button--link" to="/guard-suite#bundles" data-noBrokenLinkCheck>
                            View bundles →
                        </Link>
                    </div>
                    <div className="guardSuiteHero__stats">
                        {heroStats.map((stat) => (
                            <div key={stat.label}>
                                <span>{stat.label}</span>
                                {stat.value}
                            </div>
                        ))}
                    </div>
                </section>

                <section className="guardSuiteProducts" id="free-cli">
                    <header>
                        <p className="sectionTag">Free lead magnets</p>
                        <h2>Start with deterministic scanners, no accounts required.</h2>
                        <p>
                            Each CLI runs locally, exports machine-readable findings, and carries upsell cues into the paid guardrails revealed
                            below.
                        </p>
                    </header>
                    <div className="guardSuiteProducts__grid">
                        {guardSuitePricing.freeProducts.map((product) => (
                            <article key={product.id} className="guardSuiteCard">
                                <div className="guardSuiteCard__badge">Free CLI</div>
                                <h3>{product.name}</h3>
                                <p className="guardSuiteCard__desc">{product.description}</p>
                                <div className="guardSuitePricePills">
                                    <PricePill>Runs locally · $0</PricePill>
                                    {product.upsellTo ? <PricePill>Upsell → {slugToLabel(product.upsellTo)}</PricePill> : null}
                                </div>
                                <ul>
                                    {product.includedFeatures.map((bullet) => (
                                        <li key={bullet}>{bullet}</li>
                                    ))}
                                </ul>
                                <p className="guardSuiteCard__limit">Limitations: {product.limitations.join(' · ')}</p>
                                <Link className="button button--primary button--block" to={`/products/${product.slug}`}>
                                    View {product.name}
                                </Link>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="guardSuiteProducts" id="paid-guardrails">
                    <header>
                        <p className="sectionTag">Paid guardrails</p>
                        <h2 id="paid-guardrails">FixPack-backed enforcement packs with channel-aware pricing.</h2>
                        <p>
                            Listed prices represent direct and Gumroad storefronts (fees: {guardSuitePricing.channels.gumroadFeePercent}% Gumroad,{' '}
                            {guardSuitePricing.channels.githubMarketplaceFeePercent}% GitHub Marketplace). Use the cards below to pick the guardrail
                            that matches your operating model.
                        </p>
                    </header>
                    <div className="guardSuiteProducts__grid">
                        {activePaidProducts.map((product) => (
                            <article key={product.id} className="guardSuiteCard">
                                <div className="guardSuiteCard__badge">Paid SKU</div>
                                <h3>{product.name}</h3>
                                <p className="guardSuiteCard__desc">{product.description}</p>
                                <div className="guardSuitePricePills">
                                    {product.marketplace.direct ? <PricePill>Direct {formatUsd(product.marketplace.direct)}</PricePill> : null}
                                    {product.marketplace.gumroad ? <PricePill>Gumroad {formatUsd(product.marketplace.gumroad)}</PricePill> : null}
                                    {product.marketplace.githubMarketplace ? (
                                        <PricePill>GitHub {formatUsd(product.marketplace.githubMarketplace)}</PricePill>
                                    ) : null}
                                </div>
                                <ul>
                                    {product.includes.map((item) => (
                                        <li key={item}>{item}</li>
                                    ))}
                                </ul>
                                <Link className="button button--secondary button--block" to={`/products/${product.slug}`}>
                                    Explore {product.name}
                                </Link>
                            </article>
                        ))}
                    </div>
                    {futurePaidProducts.length ? (
                        <div className="guardSuiteFuture">
                            <p>
                                <strong>Coming soon:</strong> {futurePaidProducts.map((product) => product.name).join(' · ')} are staged for release. Tap
                                the interest links on each product page to join the waitlist.
                            </p>
                        </div>
                    ) : null}
                </section>

                <section className="guardSuiteProducts" id="guardboard">
                    <header>
                        <p className="sectionTag">GuardBoard tiers</p>
                        <h2>Visualize compliance ledgers, FixPack runs, and score trends.</h2>
                        <p>Choose a GuardBoard tier that matches your sharing needs - from local evidence viewers to enterprise RBAC dashboards.</p>
                    </header>
                    <div className="guardSuiteProducts__grid">
                        {guardSuitePricing.guardboard.map((tier) => (
                            <article key={tier.id} className="guardSuiteCard">
                                <div className="guardSuiteCard__badge">{tier.tier === 'enterprise' ? 'Enterprise' : 'Dashboard'}</div>
                                <h3>{tier.name}</h3>
                                <p className="guardSuiteCard__desc">{tier.description}</p>
                                <div className="guardSuitePricePills">
                                    {tier.priceUsd ? <PricePill>One-time {formatUsd(tier.priceUsd)}</PricePill> : null}
                                    {tier.subscriptionUsdMonth ? <PricePill>{formatUsd(tier.subscriptionUsdMonth, '/mo')}</PricePill> : null}
                                    {tier.subscriptionUsdYear ? <PricePill>{formatUsd(tier.subscriptionUsdYear, '/yr')}</PricePill> : null}
                                    {tier.subscriptionUsdMonthPerUser ? (
                                        <PricePill>{formatUsd(tier.subscriptionUsdMonthPerUser, '/mo · user')}</PricePill>
                                    ) : null}
                                    {tier.slaHours ? <PricePill>SLA {tier.slaHours}h</PricePill> : null}
                                </div>
                                <ul>
                                    {tier.features.map((feature) => (
                                        <li key={feature}>{feature}</li>
                                    ))}
                                </ul>
                                <Link className="button button--link button--block" to="/products/guardboard">
                                    GuardBoard details
                                </Link>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="guardSuiteProducts" id="pro-components">
                    <header>
                        <p className="sectionTag">Professional components</p>
                        <h2>Attach remediation engines, scoring, and schemas to any SKU.</h2>
                        <p>Upgrade bundles or individual guardrails with advanced FixPack orchestration and GuardScore automation.</p>
                    </header>
                    <div className="guardSuiteProducts__grid">
                        {guardSuitePricing.proComponents.map((component) => (
                            <article key={component.id} className="guardSuiteCard">
                                <div className="guardSuiteCard__badge">Pro component</div>
                                <h3>{component.name}</h3>
                                <p className="guardSuiteCard__desc">{component.description}</p>
                                <div className="guardSuitePricePills">
                                    {component.oneTimeUsd ? <PricePill>One-time {formatUsd(component.oneTimeUsd)}</PricePill> : null}
                                    {component.subscriptionUsdMonth ? <PricePill>{formatUsd(component.subscriptionUsdMonth, '/mo')}</PricePill> : null}
                                    {component.subscriptionUsdYear ? <PricePill>{formatUsd(component.subscriptionUsdYear, '/yr')}</PricePill> : null}
                                    {component.priceUsd === 0 ? <PricePill>Free schema</PricePill> : null}
                                </div>
                                <Link className="button button--secondary button--block" to="/products/guard-suite">
                                    Bundle availability
                                </Link>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="guardSuiteProducts" id="bundles">
                    <header>
                        <p className="sectionTag">Bundles</p>
                        <h2 id="bundles">One-click packaging for exec-ready guardrails.</h2>
                        <p>
                            Use bundles to shorten procurement cycles: core guardrails start at ${guardSuitePricing.bundles[0].priceUsd}, while the
                            Enterprise kit unlocks monthly SLAs, GuardBoard Enterprise, and every free scanner.
                        </p>
                    </header>
                    <div className="guardSuiteProducts__grid">
                        {guardSuitePricing.bundles.map((bundle) => (
                            <article key={bundle.id} className="guardSuiteCard guardSuiteBundleCard">
                                <div className="guardSuiteCard__badge">Bundle</div>
                                <h3>{bundle.name}</h3>
                                <p className="guardSuiteCard__desc">{bundle.description}</p>
                                <div className="guardSuitePricePills">
                                    {bundle.priceUsd ? <PricePill>{formatUsd(bundle.priceUsd)} one-time</PricePill> : null}
                                    {bundle.subscriptionUsdMonth ? <PricePill>{formatUsd(bundle.subscriptionUsdMonth, '/mo')}</PricePill> : null}
                                </div>
                                <ul className="guardSuiteBundleList">
                                    {formatBundleIncludes(bundle.includes).map((include) => (
                                        <li key={include}>{include}</li>
                                    ))}
                                </ul>
                                <Link className="button button--primary button--block" to="/products/guard-suite">
                                    View bundle playbook
                                </Link>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="guardSuitePhilosophy">
                    <header>
                        <p className="sectionTag">Philosophy</p>
                        <h2>Governance should be executable, auditable, and reversible.</h2>
                    </header>
                    <div className="guardSuitePhilosophy__grid">
                        <article>
                            <h3>Documents → Rego, IaC, SDKs</h3>
                            <p>
                                Policies land as Terraform modules, Rego packs, and Python SDKs so engineers can adopt controls inside their CI/CD
                                systems without waiting for a committee.
                            </p>
                        </article>
                        <article>
                            <h3>Ledger-backed evidence</h3>
                            <p>
                                Scorecards and validation ledgers give executives the receipts: every remediation, every guardrail toggle, and the
                                resulting blast radius reduction.
                            </p>
                        </article>
                        <article>
                            <h3>Human-first copy, operator-ready details</h3>
                            <p>
                                Each SKU ships with trimmed launch copy (HN / LinkedIn ready) plus the deep technical appendix teams need for due
                                diligence.
                            </p>
                        </article>
                    </div>
                </section>

                <section className="guardSuiteDocs">
                    <header>
                        <p className="sectionTag">Documentation</p>
                        <h2>GuardSuite tools in the docs portal</h2>
                        <p>Cross-link product funnels with docs so teams can self-serve upgrades.</p>
                    </header>
                    <div className="guardSuiteDocs__grid">
                        {DOC_LINKS.map((link) => (
                            <Link key={link.label} className="guardSuiteDocCard" to={link.href}>
                                <h3>{link.label}</h3>
                                <p>{link.description}</p>
                                <span>Read the guide →</span>
                            </Link>
                        ))}
                    </div>
                </section>

                <section className="guardSuiteFunnel">
                    <header>
                        <p className="sectionTag">Launch Funnel</p>
                        <h2>HN → Launch → Product → Bundle</h2>
                        <p>Track every conversion with UTM links and marketplace-friendly copy.</p>
                    </header>
                    <div className="guardSuiteFunnel__grid">
                        {FUNNEL_STEPS.map((step) => (
                            <article key={step.title}>
                                <span>{step.label}</span>
                                <h3>{step.title}</h3>
                                <p>{step.body}</p>
                            </article>
                        ))}
                    </div>
                </section>
            </main>
        </Layout>
    );
}
