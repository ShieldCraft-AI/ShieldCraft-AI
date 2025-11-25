import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export type ProductCTA = {
    label: string;
    href: string;
    variant?: 'primary' | 'secondary' | 'ghost';
};

export type ProductSection = {
    title: string;
    body: string;
    bullets?: string[];
};

export type ProductPageProps = {
    title: string;
    heroBadge?: string;
    heroDescription: string;
    metaDescription: string;
    stats: { label: string; value: string }[];
    sections: ProductSection[];
    ctas: ProductCTA[];
    comparison?: {
        heading: string;
        rows: { feature: string; vectorscan: string; vectorguard: string }[];
    };
    asideNote?: string;
};

export function ProductPage({
    title,
    heroBadge,
    heroDescription,
    metaDescription,
    stats,
    sections,
    ctas,
    comparison,
    asideNote,
}: ProductPageProps) {
    return (
        <Layout title={title} description={metaDescription}>
            <main className="guardProductPage">
                <section className="guardProductHero">
                    {heroBadge ? <span className="guardProductHero__badge">{heroBadge}</span> : null}
                    <h1>{title}</h1>
                    <p>{heroDescription}</p>
                    <div className="guardProductHero__stats">
                        {stats.map((stat) => (
                            <article key={stat.label}>
                                <span>{stat.value}</span>
                                <p>{stat.label}</p>
                            </article>
                        ))}
                    </div>
                    <div className="guardProductHero__actions">
                        {ctas.map((cta) => {
                            const className = cta.variant === 'ghost'
                                ? 'button button--link'
                                : `button button--${cta.variant ?? 'primary'}`;
                            return (
                                <Link
                                    key={cta.label}
                                    className={className}
                                    to={cta.href}>
                                    {cta.label}
                                </Link>
                            );
                        })}
                    </div>
                </section>

                <section className="guardProductSections">
                    {sections.map((section) => (
                        <article key={section.title}>
                            <h2>{section.title}</h2>
                            <p>{section.body}</p>
                            {section.bullets ? (
                                <ul>
                                    {section.bullets.map((bullet) => (
                                        <li key={bullet}>{bullet}</li>
                                    ))}
                                </ul>
                            ) : null}
                        </article>
                    ))}
                </section>

                {comparison ? (
                    <section className="guardProductComparison">
                        <h2>{comparison.heading}</h2>
                        <div className="guardProductComparison__grid">
                            <div className="guardProductComparison__header">Feature</div>
                            <div className="guardProductComparison__header">VectorScan</div>
                            <div className="guardProductComparison__header">VectorGuard</div>
                            {comparison.rows.map((row) => (
                                <React.Fragment key={row.feature}>
                                    <div>{row.feature}</div>
                                    <div>{row.vectorscan}</div>
                                    <div>{row.vectorguard}</div>
                                </React.Fragment>
                            ))}
                        </div>
                    </section>
                ) : null}

                {asideNote ? (
                    <section className="guardProductAside">
                        <p>{asideNote}</p>
                    </section>
                ) : null}
            </main>
        </Layout>
    );
}

export default ProductPage;
