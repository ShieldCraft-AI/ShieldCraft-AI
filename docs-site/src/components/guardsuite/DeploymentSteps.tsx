import React from 'react';

export default function DeploymentSteps(): React.ReactElement {
    return (
        <section className="vs-deploy container" aria-labelledby="deploy-title">
            <h2 id="deploy-title" className="vs-section-title">Deployment Quickstart</h2>
            <p className="vs-lead">Get started in minutes - local CLI first, then CI and container options.</p>

            <div className="vs-deploy__grid">
                <article className="vs-card">
                    <div className="vs-card__content">
                        <h3>1. Install</h3>
                        <pre className="vs-code"><code>curl -sSfL https://get.vectorscan.sh | sh</code></pre>
                        <p className="vs-small">Small single-binary install for local use and CI agents.</p>
                    </div>
                </article>

                <article className="vs-card">
                    <div className="vs-card__content">
                        <h3>2. Run</h3>
                        <pre className="vs-code"><code>vectorscan scan plan.json --out report.json</code></pre>
                        <p className="vs-small">Produces deterministic findings and a structured report for automation.</p>
                    </div>
                </article>

                <article className="vs-card">
                    <div className="vs-card__content">
                        <h3>3. Integrate</h3>
                        <pre className="vs-code"><code>vectorscan ci --on-pr --format sarif</code></pre>
                        <p className="vs-small">Integrate with CI, PR checks, or export to your alerting pipeline.</p>
                    </div>
                </article>
            </div>
        </section>
    );
}
