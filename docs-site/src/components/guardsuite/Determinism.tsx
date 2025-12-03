import React from 'react';

export default function Determinism(): React.ReactElement {
    return (
        <section className="vs-determinism container" aria-labelledby="determinism-title">
            <div className="vs-determinism__inner">
                <div className="vs-determinism__left">
                    <h2 id="determinism-title" className="vs-section-title">Why Determinism Matters</h2>
                    <p>
                        Unpredictable infrastructure changes cost time and trust. VectorScan turns chaotic plans into canonical
                        truth so teams can audit, reproduce, and govern changes with confidence.
                    </p>
                </div>

                <aside className="vs-determinism__right" aria-hidden>
                    <ul className="vs-invariants">
                        <li><strong>Repeatable scans</strong><span>Byte-for-byte identical for identical input</span></li>
                        <li><strong>100% auditability</strong><span>Full metadata and deterministic IDs</span></li>
                        <li><strong>CI stability</strong><span>Deterministic behavior across environments</span></li>
                        <li><strong>Zero network access</strong><span>No telemetry leakage; runs locally</span></li>
                        <li><strong>Memory-bounded WASM</strong><span>Safe, sandboxed execution</span></li>
                        <li><strong>Reproducible results</strong><span>Same output everywhere</span></li>
                    </ul>
                </aside>
            </div>
        </section>
    );
}
