import React from 'react';
import { IconFileList, IconBox, IconCheckCircle } from '@site/src/components/guardsuite/icons';

export default function Microflow(): React.ReactElement {
    return (
        <section className="vs-microflow container" aria-labelledby="microflow-title">
            <h2 id="microflow-title" className="vs-microflow__title vs-section-title">How VectorScan Works</h2>
            <div className="vs-microflow__grid">
                <article className="vs-microflow__step vs-card">
                    <div className="vs-microflow__icon vs-icon" aria-hidden>
                        <IconFileList />
                    </div>
                    <h3 className="vs-microflow__stepTitle">Ingest</h3>
                    <p className="vs-microflow__stepText">Raw, inconsistent Terraform plans are read locally.</p>
                </article>

                <article className="vs-microflow__step vs-card">
                    <div className="vs-microflow__icon vs-icon" aria-hidden>
                        <IconBox />
                    </div>
                    <h3 className="vs-microflow__stepTitle">Canonicalize</h3>
                    <p className="vs-microflow__stepText">Deterministic transformation - no nondeterministic I/O.</p>
                </article>

                <article className="vs-microflow__step vs-card">
                    <div className="vs-microflow__icon vs-icon" aria-hidden>
                        <IconCheckCircle />
                    </div>
                    <h3 className="vs-microflow__stepTitle">Score &amp; Govern</h3>
                    <p className="vs-microflow__stepText">Surface what matters. Apply Fixpack hints and guardrails.</p>
                </article>
            </div>
        </section>
    );
}
