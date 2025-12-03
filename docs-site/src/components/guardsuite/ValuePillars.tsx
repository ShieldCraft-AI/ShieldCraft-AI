import React from 'react';

const PILLARS = [
    {
        title: 'Deterministic by Design',
        text: 'Output is identical for identical input - zero nondeterminism.',
        icon: '🔁',
    },
    {
        title: 'WASM-Safe Execution',
        text: 'Side-effect-free, sandboxed scanning for CI and production.',
        icon: '🛡️',
    },
    {
        title: 'Canonical Output',
        text: 'Chaotic plans become machine-readable, auditable truth.',
        icon: '📦',
    },
    {
        title: 'Fixpack Hints',
        text: 'Each finding includes a direct remediation hint (fixpack:<ISSUE>).',
        icon: '🧭',
    },
];

export default function ValuePillars() {
    return (
        <section className="vs-pillars container" aria-labelledby="pillars-title">
            <h2 id="pillars-title" className="vs-pillars__title vs-section-title">What VectorScan Guarantees</h2>
            <div className="vs-pillars__grid">
                {PILLARS.map((p) => (
                    <article key={p.title} className="vs-pillars__card vs-card" tabIndex={0}>
                        <div className="vs-pillars__icon vs-icon" aria-hidden>{p.icon}</div>
                        <h3 className="vs-pillars__cardTitle">{p.title}</h3>
                        <p className="vs-pillars__cardText">{p.text}</p>
                    </article>
                ))}
            </div>
        </section>
    );
}
