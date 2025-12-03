import React from 'react';

export default function SignatureSection(): React.ReactElement {
    return (
        <section className="vs-signature" aria-labelledby="signature-title">
            <div className="container vs-signature__inner">
                <h2 id="signature-title" className="vs-section-title">Architectural Invariants & Integrity Guarantees</h2>
                <div className="vs-signature__grid">
                    <article className="vs-card">
                        <h3>Deterministic Auditability</h3>
                        <p>You get identical output for identical input - every time.</p>
                    </article>

                    <article className="vs-card">
                        <h3>WASM-Sandboxed Safety</h3>
                        <p>Rules execute inside a safe, isolated runtime with no side effects.</p>
                    </article>

                    <article className="vs-card">
                        <h3>Governance Contracts</h3>
                        <p>Severity, schema, and output format are immutable; governance rules are enforced.</p>
                    </article>
                </div>
            </div>
        </section>
    );
}
