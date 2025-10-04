import React from 'react';
import Link from '@docusaurus/Link';

export const SiteFooter: React.FC = () => {
    // Rely on CSS variables from Docusaurus rather than JS color mode hook for SSR safety
    const headingColor = 'var(--ifm-font-color-base)';
    const textColor = 'var(--ifm-color-emphasis-700)';
    const panelBorder = '1px solid var(--ifm-color-emphasis-300)';
    const gradient = 'linear-gradient(135deg, var(--ifm-background-surface-color) 0%, var(--ifm-background-color) 100%)';

    return (
        <footer style={{
            marginTop: '4rem',
            background: gradient,
            borderTop: panelBorder,
            padding: '3.5rem clamp(1.25rem,4vw,5rem) 2.5rem',
            fontFamily: 'Inter, system-ui, sans-serif'
        }}>
            <div style={{
                display: 'grid',
                gap: '2.5rem clamp(1.5rem,4vw,4rem)',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                alignItems: 'start',
                maxWidth: 1480,
                margin: '0 auto'
            }}>
                {/* Brand / Mission */}
                <div style={{ minWidth: 200 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '.65rem', marginBottom: '.85rem' }}>
                        <img src="/img/logo.png" alt="ShieldCraft AI" style={{ height: 34, width: 'auto', borderRadius: 6 }} />
                        <h3 style={{ margin: 0, fontSize: '1.15rem', color: headingColor }}>ShieldCraft AI</h3>
                    </div>
                    <p style={{ margin: 0, lineHeight: 1.45, fontSize: '.9rem', color: textColor }}>
                        Autonomous, intelligence‑driven cloud defense. Built on AWS. Powered by Generative AI and pragmatic MLOps.
                    </p>
                </div>

                {/* Documentation */}
                <div>
                    <h4 style={{ margin: '0 0 .75rem', fontSize: '.95rem', letterSpacing: '.5px', textTransform: 'uppercase', fontWeight: 600, color: headingColor }}>Documentation</h4>
                    <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '.45rem' }}>
                        <li><Link to="/intro">Getting Started</Link></li>
                        <li><Link to="/checklist">Implementation Checklist</Link></li>
                        <li><Link to="/aws_stack_architecture">AWS Architecture</Link></li>
                        <li><Link to="/generative_ai_core">Generative AI Core</Link></li>
                        <li><Link to="/adrs">ADRs</Link></li>
                    </ul>
                </div>

                {/* Platform */}
                <div>
                    <h4 style={{ margin: '0 0 .75rem', fontSize: '.95rem', letterSpacing: '.5px', textTransform: 'uppercase', fontWeight: 600, color: headingColor }}>Platform</h4>
                    <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '.45rem' }}>
                        <li><Link to="/architecture">Pricing & Tiers</Link></li>
                        <li><Link to="/automated-alert-triage">Automated Triage</Link></li>
                        <li><Link to="/automated-attack-simulation">Attack Simulation</Link></li>
                        <li><Link to="/threat-detection">Threat Intelligence</Link></li>
                        <li><Link to="/spec">Full Platform Spec</Link></li>
                    </ul>
                </div>

                {/* Company / Contact */}
                <div>
                    <h4 style={{ margin: '0 0 .75rem', fontSize: '.95rem', letterSpacing: '.5px', textTransform: 'uppercase', fontWeight: 600, color: headingColor }}>Company</h4>
                    <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '.45rem' }}>
                        <li><a href="https://www.linkedin.com/in/deon-prinsloo-0341b0332" target="_blank" rel="noopener noreferrer">LinkedIn</a></li>
                        <li><a href="https://github.com/Dee66/ShieldCraft-ai" target="_blank" rel="noopener noreferrer">GitHub</a></li>
                        <li><a href="mailto:shieldcraftai@gmail.com">Contact Us</a></li>
                        <li><Link to="/privacy_impact_assessment">Privacy</Link></li>
                        <li><Link to="/security_governance">Security Governance</Link></li>
                    </ul>
                </div>

                {/* Call to Action */}
                <div style={{ minWidth: 220 }}>
                    <h4 style={{ margin: '0 0 .75rem', fontSize: '.95rem', letterSpacing: '.5px', textTransform: 'uppercase', fontWeight: 600, color: headingColor }}>Get Started</h4>
                    <p style={{ margin: '0 0 .85rem', fontSize: '.85rem', lineHeight: 1.5, color: textColor }}>Spin up the Starter tier, explore automated triage & simulation, or review the AI core powering proactive defense.</p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '.55rem' }}>
                        <Link to="/architecture" style={{
                            textDecoration: 'none',
                            padding: '.65rem .9rem',
                            background: 'var(--ifm-color-primary-lightest)',
                            border: '1px solid var(--ifm-color-primary-lighter)',
                            borderRadius: 8,
                            fontSize: '.85rem',
                            fontWeight: 600,
                            color: 'var(--ifm-color-primary-darker)',
                            textAlign: 'center'
                        }}>View Pricing</Link>
                        <Link to="/intro" style={{
                            textDecoration: 'none',
                            padding: '.65rem .9rem',
                            background: 'rgba(16,185,129,0.12)',
                            border: '1px solid rgba(16,185,129,0.35)',
                            borderRadius: 8,
                            fontSize: '.85rem',
                            fontWeight: 600,
                            color: '#047857',
                            textAlign: 'center'
                        }}>Get Started</Link>
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '3rem', borderTop: panelBorder, paddingTop: '1.25rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', justifyContent: 'space-between', alignItems: 'center', fontSize: '.75rem', color: textColor, maxWidth: 1480, marginLeft: 'auto', marginRight: 'auto' }}>
                <span>© {new Date().getFullYear()} ShieldCraft AI. All rights reserved.</span>
            </div>
        </footer>
    );
};

export default SiteFooter;
