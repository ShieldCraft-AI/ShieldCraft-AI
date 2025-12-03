import React from 'react';

const faqs = [
    { q: 'Is VectorScan open-source?', a: 'Yes - core components are available and can run locally without telemetry.' },
    { q: 'Can I run scans in CI?', a: 'Absolutely - use `vectorscan ci` or the GitHub Actions integration for PR checks.' },
    { q: 'How does deterministic auditing work?', a: 'VectorScan canonicalizes inputs to produce identical outputs for identical inputs, enabling reproducible audits.' },
    { q: 'What platforms are supported?', a: 'We support Terraform plans, OCI artifacts, S3 state, and integrations with major CI and alerting tools.' },
];

export default function FAQ(): React.ReactElement {
    return (
        <section className="vs-faq container" aria-labelledby="faq-title">
            <h2 id="faq-title" className="vs-section-title">Frequently asked questions</h2>
            <div className="vs-faq__grid">
                {faqs.map((f) => (
                    <details key={f.q} className="vs-faq__item vs-card">
                        <summary>{f.q}</summary>
                        <div className="vs-faq__answer">{f.a}</div>
                    </details>
                ))}
            </div>
        </section>
    );
}
