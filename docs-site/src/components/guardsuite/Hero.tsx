import React from 'react';
import Link from '@docusaurus/Link';

export default function Hero() {
    return (
        <header className="vs-hero" role="banner">
            <div className="vs-hero-glow" aria-hidden />
            <div className="vs-hero__visual" aria-hidden>
                <svg className="vs-hero__svg" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                    <defs>
                        <filter id="blur"><feGaussianBlur stdDeviation="6" /></filter>
                        <linearGradient id="vg" x1="0" x2="1">
                            <stop offset="0%" stopColor="var(--sc-color-primary-soft)" stopOpacity="0.14" />
                            <stop offset="100%" stopColor="var(--sc-color-accent-cyan)" stopOpacity="0.02" />
                        </linearGradient>
                    </defs>

                    {/* Subtle network of nodes */}
                    <g className="stream" stroke="var(--vs-purple)" strokeWidth="1.1" fill="none" opacity="0.9">
                        <line className="s1" x1="60" y1="80" x2="220" y2="60" strokeOpacity="0.14" strokeLinecap="round" />
                        <line className="s2" x1="140" y1="200" x2="360" y2="150" strokeOpacity="0.12" strokeLinecap="round" />
                        <line className="s3" x1="480" y1="220" x2="720" y2="200" strokeOpacity="0.10" strokeLinecap="round" />
                        <circle className="node node1" cx="220" cy="60" r="3.6" fill="var(--vs-purple)" opacity="0.14" />
                        <circle className="node node2" cx="360" cy="150" r="3.6" fill="var(--vs-purple)" opacity="0.14" />
                        <circle className="node node3" cx="720" cy="200" r="3.6" fill="var(--vs-purple)" opacity="0.14" />
                    </g>

                    {/* Central canonical grid (outlined boxes) */}
                    <g className="core" transform="translate(320,110)" opacity="0.95">
                        <rect x="0" y="0" width="160" height="160" rx="12" stroke="var(--vs-purple)" strokeWidth="1.2" fill="none" filter="url(#blur)" />
                        <g className="blocks" transform="translate(12,12)" stroke="var(--vs-purple)" strokeWidth="1.2" fill="none">
                            <rect className="block" x="0" y="0" width="30" height="30" rx="4" />
                            <rect className="block" x="40" y="0" width="30" height="30" rx="4" />
                            <rect className="block" x="80" y="0" width="30" height="30" rx="4" />
                            <rect className="block" x="0" y="40" width="30" height="30" rx="4" />
                            <rect className="block" x="40" y="40" width="30" height="30" rx="4" />
                        </g>
                    </g>
                </svg>
            </div>

            <div className="vs-hero__content container">
                <div className="vs-hero__copy">
                    <span className="vs-badge">Canonical Schema v1.0.0 • WASM-Sandboxed • Deterministic Output • Fixpack Hints</span>
                    <h1 className="vs-hero__title">VectorScan - Deterministic Governance for Your Cloud.</h1>
                    <p className="vs-hero__subtitle">Canonicalize every change. Make every decision reproducible. Eliminate noise. Enforce truth.</p>

                    <div className="vs-hero__ctas">
                        <Link className="button button--primary" to="https://github.com/deonprinsloo/guardsuite/releases">Start Free Trial</Link>
                        <Link className="button button--secondary" to="/docs">Explore Documentation</Link>
                    </div>

                    <div className="vs-hero__trust">
                        <small>Canonical Schema v1.0.0 &nbsp;•&nbsp; WASM-Sandboxed Execution &nbsp;•&nbsp; Deterministic Output Guarantee &nbsp;•&nbsp; Fixpack Hints Included</small>
                    </div>
                </div>
            </div>
        </header>
    );
}
