import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function VectorScanLaunchPage() {
    return (
        <Layout
            title="VectorScan Launch"
            description="VectorScan launch landing page for Hacker News and marketplaces.">
            <main className="launchPage">
                <section>
                    <p className="sectionTag">Launch TL;DR</p>
                    <h1>VectorScan  -  Free Terraform Plan Scanner</h1>
                    <p>
                        Scan `tfplan.json` locally, surface drift + encryption gaps, and export policy-ready findings. Zero accounts, zero uploads, zero delay.
                    </p>
                    <div className="launchActions">
                        <Link className="button button--primary" to="https://github.com/Dee66/ShieldCraft-ai">Download CLI</Link>
                        <Link className="button button--secondary" to="/products/vectorscan">Product page</Link>
                    </div>
                </section>

                <section>
                    <h2>Show HN copy</h2>
                    <p>
                        “We built a zero-setup Terraform plan scanner because teams were sharing PDFs instead of guardrails. VectorScan runs locally, flags drift,
                        and exports SARIF/JSON so you can keep CI/CD honest. It is the on-ramp to VectorGuard, a $79 Zero-Trust blueprint that turns findings into
                        executable guardrails. Would love feedback and benchmarks from your infra repos.”
                    </p>
                </section>

                <section>
                    <h2>Install snippet</h2>
                    <pre>
                        <code>pip install vectorscan && vectorscan ./plan/tfplan.json --format markdown</code>
                    </pre>
                </section>

                <section>
                    <h2>Benchmarks</h2>
                    <ul>
                        <li>1.2s average scan time on 1k-resource plans</li>
                        <li>Outputs SARIF for GitHub code scanning + Markdown recap</li>
                        <li>Compatible with Terraform 1.5+ and OpenTofu plans</li>
                    </ul>
                </section>

                <section>
                    <h2>Next step</h2>
                    <p>Guide users to Guard Suite upsells after first run.</p>
                    <Link className="button button--link" to="/guard-suite">Guard Suite overview →</Link>
                </section>
            </main>
        </Layout>
    );
}
