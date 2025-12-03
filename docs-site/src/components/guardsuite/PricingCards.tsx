import React from 'react';

const tiers = [
    {
        id: 'starter',
        name: 'Starter',
        price: '$0/yr',
        bullets: ['Free for small projects', 'Deterministic scans', 'Community support'],
        cta: 'Start for free',
    },
    {
        id: 'pro',
        name: 'Pro',
        price: '$79/yr',
        bullets: ['Everything in Starter', 'Priority support', 'CI integrations'],
        cta: 'Get Pro',
    },
    {
        id: 'enterprise',
        name: 'Enterprise',
        price: '$249/yr',
        bullets: ['SLA & SSO', 'Audit-ready reports', 'Onboarding assistance'],
        cta: 'Contact sales',
    },
];

export default function PricingCards(): React.ReactElement {
    return (
        <section className="vs-pricing container" aria-labelledby="pricing-title">
            <h2 id="pricing-title" className="vs-section-title">Pricing</h2>
            <p className="vs-lead">Annual plans tuned for teams. No surprises - transparent, predictable pricing.</p>

            <div className="vs-pricing__grid">
                {tiers.map((t) => (
                    <article key={t.id} className={`vs-tier vs-tier--${t.id} vs-card`}>
                        <div className="vs-card__content">
                            <header className="vs-tier__head">
                                <h3>{t.name}</h3>
                                <div className="vs-tier__price">{t.price}</div>
                            </header>
                            <ul className="vs-tier__bullets">
                                {t.bullets.map((b) => (<li key={b}>{b}</li>))}
                            </ul>
                        </div>
                        <div className="vs-card__cta">
                            <div className="vs-tier__cta">
                                <button className="vs-btn">{t.cta}</button>
                            </div>
                        </div>
                    </article>
                ))}
            </div>
            <p className="vs-pricing__footnote">Marketplace billing and enterprise contracts available on request.</p>
        </section>
    );
}
