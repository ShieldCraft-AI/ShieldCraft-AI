import React from 'react';
import { IconIntegration } from '@site/src/components/guardsuite/icons';

const connectors = [
    { name: 'Terraform', desc: 'Native TF plan ingestion', hint: 'vectorscan scan plan.tf.json' },
    { name: 'CloudTrail', desc: 'Telemetry enrichment', hint: 'collect -> vectorscan ingest' },
    { name: 'GitHub', desc: 'Repo-aware scans & PR checks', hint: 'gh actions + vectorscan' },
    { name: 'OCI', desc: 'OCI registry scanning', hint: 'oci scan <repo>' },
    { name: 'S3', desc: 'Artifact & state access', hint: 's3://bucket/path' },
    { name: 'PagerDuty', desc: 'Alert routing & escalation', hint: 'pd integration' },
];

export default function IntegrationsGrid(): React.ReactElement {
    return (
        <section className="vs-integrations container" aria-labelledby="integrations-title">
            <h2 id="integrations-title" className="vs-section-title">Integrations</h2>
            <p className="vs-lead">Plug into your existing toolchain - low-friction connectors and lightweight adapters.</p>

            <div className="vs-integrations__grid">
                {connectors.map((c) => (
                    <article key={c.name} className="vs-integration vs-card">
                        <div className="vs-card__content">
                            <div className="vs-integration__icon vs-icon" aria-hidden>
                                <IconIntegration width={48} height={48} className="vs-icon-svg" />
                            </div>
                            <div className="vs-integration__body">
                                <h3>{c.name}</h3>
                                <p className="vs-small">{c.desc}</p>
                                <div className="vs-integration__hint"><code>{c.hint}</code></div>
                            </div>
                        </div>
                    </article>
                ))}
            </div>
        </section>
    );
}
