import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { guardSuitePricing } from '@site/src/data/guardSuitePricing';

const formatUsd = (value?: number, suffix = '') => (value == null ? 'Contact us' : `$${value.toLocaleString()}${suffix}`);

const formatBundleIncludes = (includes: string[]): string[] => {
    const collections = [
        guardSuitePricing.freeProducts,
        guardSuitePricing.paidProducts,
        guardSuitePricing.proComponents,
        guardSuitePricing.guardboard,
    ];

    return includes.flatMap((entry) => {
        if (entry === 'all_free_products') {
            return [`${guardSuitePricing.freeProducts.length} free CLIs (${guardSuitePricing.freeProducts.map((p) => p.name).join(', ')})`];
        }

        for (const collection of collections) {
            const match = collection.find((item) => item.slug === entry);
            if (match) return [match.name];
        }

        return [entry];
    });
};

export default function GuardSuiteBundlePage() {
    return (
        <Layout title="Guard Suite Bundles" description="Guard Suite bundles covering guardrails, GuardBoard, GuardScore, and remediation engines.">
            <main className="guardSuiteBundlePage" id="bundle">
                <section>
                    <p className="sectionTag">GuardSuite Kits</p>
                    <h1>Bundle guardrails, GuardBoard, and pro components.</h1>
                    <p>
                        The GuardSuite pricing universe now exposes every bundle in one place. Choose a one-time bundle (Full or Pro Kit) or subscribe to the
                        Enterprise Kit for GuardBoard Enterprise, GuardScore automation, and monthly SLAs.
                    </p>
                    <ul>
                        <li>Fee awareness: {guardSuitePricing.channels.gumroadFeePercent}% Gumroad · {guardSuitePricing.channels.githubMarketplaceFeePercent}% GitHub Marketplace</li>
                        <li>Affiliate alignment: 20% lifetime share, 70% boosted during launch-week marketplaces</li>
                        <li>Pre-flight Check ($19) upsell template included in every kit</li>
                    </ul>
                    <div className="guardSuiteBundlePage__actions">
                        <Link className="button button--primary" to="mailto:shieldcraftai@gmail.com?subject=GuardSuite%20Bundles">
                            Book procurement review
                        </Link>
                        <Link className="button button--secondary" to="/guard-suite">
                            Back to Guard Suite overview
                        </Link>
                    </div>
                </section>

                <section>
                    <p className="sectionTag">Bundle catalog</p>
                    <h2>Pick the kit that matches your runway.</h2>
                    <div className="guardSuiteProducts__grid">
                        {guardSuitePricing.bundles.map((bundle) => (
                            <article key={bundle.id} className="guardSuiteCard">
                                <div className="guardSuiteCard__badge">Bundle</div>
                                <h3>{bundle.name}</h3>
                                <p className="guardSuiteCard__desc">{bundle.description}</p>
                                <div className="guardSuitePricePills">
                                    {bundle.priceUsd ? <span className="guardSuitePricePill">{formatUsd(bundle.priceUsd)} one-time</span> : null}
                                    {bundle.subscriptionUsdMonth ? <span className="guardSuitePricePill">{formatUsd(bundle.subscriptionUsdMonth, '/mo')}</span> : null}
                                </div>
                                <ul>
                                    {formatBundleIncludes(bundle.includes).map((include) => (
                                        <li key={include}>{include}</li>
                                    ))}
                                </ul>
                                <Link className="button button--link button--block" to="mailto:shieldcraftai@gmail.com?subject=GuardSuite%20Bundle%20Request">
                                    Request invoice
                                </Link>
                            </article>
                        ))}
                    </div>
                </section>
            </main>
        </Layout>
    );
}
