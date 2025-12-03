import React from 'react';

export default function CLISection(): React.ReactElement {
    return (
        <section className="vs-cli container" aria-labelledby="cli-title">
            <h2 id="cli-title" className="vs-section-title">CLI Experience</h2>
            <div className="vs-cli__grid">
                <div className="vs-cli__example">
                    <pre className="vs-code"><code>vectorscan scan plan.json --explain</code></pre>
                    <p className="vs-cli__note">Explains every transformation step. Perfect for onboarding & audits.</p>
                </div>

                <div className="vs-cli__example">
                    <pre className="vs-code"><code>issue: GS-TF-014
                        hint: fixpack:missing-tags</code></pre>
                    <p className="vs-cli__note">Fixpack hints included inline with findings for quick remediation.</p>
                </div>
            </div>
        </section>
    );
}
