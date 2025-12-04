import React from 'react';
import Layout from '@theme/Layout';
import PlatformArchitecture from '../components/PlatformArchitecture';
import ButtonPremium from '../components/ButtonPremium';
import DividerLine from '../components/DividerLine';
import AccessibilityHints from '../components/AccessibilityHints';
import '../styles/prose.css';
import '../styles/sc-architecture.css';
import '../styles/sc-layout.css';
import '../styles/sc-motion.css';
import '../styles/typography.css';
import styles from '../styles/index.module.css';
import heroStyles from './HeroPremium.module.css';

type MicroCard = { title: string; body: string };

const contextHighlights: MicroCard[] = [
  { title: 'Evidence-first telemetry', body: 'Normalize events and keep ingestion deterministic before automation acts.' },
  { title: 'Guarded autonomy', body: 'Playbooks + approvals + budgets keep remediation auditable and reversible.' },
  { title: 'Measured outcomes', body: 'FinOps and drift metrics keep ML risk and spend visible.' },
];

export default function IndexPage(): JSX.Element {
  return (
    <Layout title="ShieldCraft AI - Autonomous Security on AWS" description="Govern and scale GenAI on AWS with deterministic, policy-guarded automation.">
      <div className={`${styles.page} scPage`} role="document">
        <header className={`${styles.heroWrap} ${styles.heroSubtleGlow}`}>
          <div className={styles.heroContain}>
            <div className="scContainerWide">
              <section className={heroStyles.heroFrame}>
                <div className={heroStyles.heroHeaderRow}>
                  <div className={heroStyles.brandStack}>
                    <div className={heroStyles.logoMark} aria-hidden="true">▧</div>
                    <div>
                      <div className={heroStyles.brandName}>ShieldCraft</div>
                      <div className={heroStyles.brandKicker}>Autonomous Security · AWS Native</div>
                    </div>
                  </div>
                  <div className={heroStyles.headerActions}>
                    <ButtonPremium className="hero small" variant="secondary">Docs</ButtonPremium>
                  </div>
                </div>

                <div className={`${heroStyles.heroSurface} ${styles.heroSurface} scFadeIn`}>
                  <h1 className={`${heroStyles.heroTitle} ${styles.heroTitle}`}>Trusted Autonomy for AWS Security Teams</h1>
                  <p className={heroStyles.heroSubtitle}>
                    ShieldCraft unifies telemetry, model governance, and reversible playbooks so GenAI initiatives stay evidence-first,
                    observable, and budget-aware from dev through regulated prod.
                  </p>
                  <div className={heroStyles.heroActions}>
                    <ButtonPremium className="hero primaryCTA">Launch the demo</ButtonPremium>
                    <ButtonPremium className="hero" variant="secondary">Review architecture</ButtonPremium>
                  </div>
                  <div className={heroStyles.heroNote}>
                    Key patterns: deterministic ingestion · hybrid retrieval · guardrailed automation with approvals and budgets.
                  </div>
                </div>
              </section>
            </div>
          </div>
        </header>

        <main id="main-content" role="main" aria-labelledby="main-heading">
          <section className={`scSection scBlock ${styles.sectionSurface} ${styles.contextSection}`} aria-labelledby="context-heading">
            <div className="scContainer">
              <div className={styles.contextIntro}>
                <p className={styles.contextEyebrow}>Why teams pick ShieldCraft</p>
                <h2 id="context-heading" className={`${styles.sectionTitle} scSectionTitle`}>Clarity before automation</h2>
                <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                  ShieldCraft aligns telemetry, governance, and GenAI so security teams can trust every automated step.
                </p>
              </div>

              <div className={styles.contextGrid}>
                {contextHighlights.map((c) => (
                  <article className={styles.contextCard} key={c.title}>
                    <h3>{c.title}</h3>
                    <p>{c.body}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>

          <DividerLine />

          {/* Platform architecture contains the single AWS selector + diagram + details */}
          <section className={`scSection scBlock archSectionOverride ${styles.sectionSurface}`} aria-labelledby="platform-arch-heading">
            <div className="scContainerWide">
              <h2 id="platform-arch-heading" className={`${styles.sectionTitle} scSectionTitle`}>Platform Architecture</h2>
              <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                Security data plane, deterministic pipelines, governed execution.
              </p>

              <PlatformArchitecture />

            </div>
          </section>

          <DividerLine />

          <footer className={`scSection scBlock ${styles.sectionSurface}`} aria-label="Site footer" role="contentinfo">
            <div className="scContainer">
              <div className={styles.footer}>
                <ButtonPremium variant="secondary" className={`${styles.scButtonSecondary} ${styles.footerCta}`}>Contact Sales</ButtonPremium>
                <AccessibilityHints />
              </div>
            </div>
          </footer>
        </main>
      </div>
    </Layout>
  );
}
