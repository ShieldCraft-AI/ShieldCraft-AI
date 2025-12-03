import React from 'react';
import { IconLock, IconShieldCheck, IconData } from '@site/src/components/guardsuite/icons';

export default function SecurityBand(): React.ReactElement {
    return (
        <section className="vs-security" aria-labelledby="security-title">
            <div className="container vs-security__inner">
                <h2 id="security-title" className="vs-section-title">Security & Compliance</h2>
                <p className="vs-lead">Designed for high-assurance environments: auditability, least-privilege, and safe execution.</p>

                <div className="vs-security__grid">
                    <article className="vs-card">
                        <div className="vs-security__icon vs-icon" aria-hidden>
                            <IconLock width={40} height={40} className="vs-icon-svg" />
                        </div>
                        <h3>Audit-Ready Reports</h3>
                        <p>Comprehensive, immutable reports for compliance and incident investigation.</p>
                    </article>

                    <article className="vs-card">
                        <div className="vs-security__icon vs-icon" aria-hidden>
                            <IconShieldCheck width={40} height={40} className="vs-icon-svg" />
                        </div>
                        <h3>Least-Privilege First</h3>
                        <p>Guided remediations and fixpacks minimize blast radius from changes.</p>
                    </article>

                    <article className="vs-card">
                        <div className="vs-security__icon vs-icon" aria-hidden>
                            <IconData width={40} height={40} className="vs-icon-svg" />
                        </div>
                        <h3>Data Residency Controls</h3>
                        <p>Run locally or choose regional processing to meet regulatory needs.</p>
                    </article>
                </div>
            </div>
        </section>
    );
}
