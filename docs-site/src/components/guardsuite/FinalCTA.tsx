import React from 'react';

export default function FinalCTA(): React.ReactElement {
    return (
        <section className="vs-finalcta" aria-labelledby="finalcta-title">
            <div className="container vs-finalcta__inner">
                <h2 id="finalcta-title" className="vs-section-title">Ready to make governance deterministic?</h2>
                <p className="vs-lead">Request a pilot, or start a free trial and run VectorScan locally in minutes.</p>
                <div className="vs-finalcta__actions">
                    <a className="vs-btn" href="mailto:contact@guardsuite.ai?subject=Pilot%20Request">Request a Pilot</a>
                    <a className="vs-btn" href="https://github.com/deonprinsloo/guardsuite/releases" target="_blank" rel="noopener noreferrer">Start Free Trial</a>
                </div>
            </div>
        </section>
    );
}
