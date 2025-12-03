import Layout from '@theme/Layout';
import React from 'react';
import ButtonPremium from '../components/ButtonPremium';
import DividerLine from '../components/DividerLine';
import PlatformArchitecture from '../components/PlatformArchitecture';
import '../styles/prose.css';
import '../styles/sc-architecture.css';
import '../styles/sc-layout.css';
import '../styles/sc-motion.css';
import '../styles/typography.css';
import heroStyles from './HeroPremium.module.css';
import styles from './index.module.css';

import AccessibilityHints from '../components/AccessibilityHints';

type MicroCard = {
  title: string;
  body: string;
};

const dataPlaneCards: MicroCard[] = [
  {
    title: 'Ingest • Normalize • Stream',
    body: 'Reliable adapters, schema validation, streaming durability.',
  },
  {
    title: 'Transform • Validate • Index',
    body: 'Deterministic transforms, schema enforcement, indexing services.',
  },
  {
    title: 'Store • Serve • Archive',
    body: 'Multi-tier storage, hot/cold separation, lifecycle policies.',
  },
];

const coreCapabilityCards: MicroCard[] = [
  {
    title: 'Rapid, Audit-Ready Remediation',
    body: 'Actionable guardrails, validated playbooks, deterministic fixes.',
  },
  {
    title: 'Continuous Model Validation',
    body: 'Automated checks, drift alerts, policy-gated releases.',
  },
  {
    title: 'Finesse & Risk Prioritization',
    body: 'Risk matrices, governance tiers, prioritized workflows.',
  },
];

const awsAdvantageCards: MicroCard[] = [
  {
    title: 'AWS-Native Foundation',
    body: 'Secure constructs powered by AWS primitives and IAM-first control.',
  },
  {
    title: 'GenAI Intelligence Layer',
    body: 'Model pipelines instrumented for safety and drift control.',
  },
  {
    title: 'Unified Governance Engine',
    body: 'Policy-as-code, release gating, and immutable audit trails.',
  },
];

const contextHighlights: MicroCard[] = [
  {
    title: 'Evidence-first telemetry',
    body: 'Normalize events, enrich identities, and keep every ingestion path deterministic before automation acts.',
  },
  {
    title: 'Guarded autonomy',
    body: 'Step Functions, budgets, and approvals gate every action so remediation stays auditable and reversible.',
  },
  {
    title: 'Measured outcomes',
    body: 'FinOps, drift, and posture benchmarks stay visible so teams can prove ROI and nudge models with data.',
  },
];

export default function IndexPage(): React.ReactElement {
  return (
    <Layout
      title="ShieldCraft AI - Autonomous Security on AWS"
      description="Govern and scale GenAI on AWS with deterministic, policy-guarded automation."
    >
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
        <main
          id="main-content"
          role="main"
          aria-labelledby="main-heading"
        >
          <section
            className={`scSection scBlock ${styles.sectionSurface} ${styles.contextSection}`}
            aria-labelledby="context-heading"
          >
            <div className="scContainer">
              <div className={styles.contextIntro}>
                <p className={styles.contextEyebrow}>Why teams pick ShieldCraft</p>
                <h2 id="context-heading" className={`${styles.sectionTitle} scSectionTitle`}>Clarity before automation</h2>
                <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                  ShieldCraft aligns telemetry, governance, and GenAI so security teams can trust every automated step.
                </p>
              </div>
              <div className={styles.contextGrid}>
                {contextHighlights.map(card => (
                  <article className={styles.contextCard} key={card.title}>
                    <h3>{card.title}</h3>
                    <p>{card.body}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>

          <DividerLine />

          <section
            className={`scSection scBlock ${styles.sectionSurface}`}
            aria-labelledby="data-plane-heading"
          >
            <div className="scContainerNarrow">
              <h2 id="data-plane-heading" className={`${styles.sectionTitle} scSectionTitle`}>Data Plane</h2>
              <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                High-throughput ingestion, normalization and resilient storage.
              </p>
              <div className={styles.dpGrid}>
                {dataPlaneCards.map(card => (
                  <article className={styles.scCardSm} key={card.title}>
                    <h3 className={styles.scCardSmTitle}>{card.title}</h3>
                    <p className={styles.scCardSmBody}>{card.body}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>

          <DividerLine />

          <section
            className={`scSection scBlock ${styles.sectionSurface}`}
            aria-labelledby="core-ops-heading"
          >
            <div className="scContainerNarrow">
              <h2 id="core-ops-heading" className={`${styles.sectionTitle} scSectionTitle`}>Core Operational Capabilities</h2>
              <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                Operational controls, observability, and governance.
              </p>
              <div className={styles.dpGrid}>
                {coreCapabilityCards.map(card => (
                  <article className={styles.scCardSm} key={card.title}>
                    <h3 className={styles.scCardSmTitle}>{card.title}</h3>
                    <p className={styles.scCardSmBody}>{card.body}</p>
                  </article>
                ))}
              </div>
              <p className={styles.coreOpsDesc}>
                Operational essentials - Observability, Security, Cost controls, Release gating.
              </p>
              <div className={styles.coreOpsActions}>
                <div className={styles.coreOpsCard}>
                  <ButtonPremium variant="secondary" className={styles.scButtonSecondary}>Request Enterprise Demo</ButtonPremium>
                </div>
              </div>
            </div>
          </section>

          <DividerLine />

          {/* PlatformArchitecture keeps its own interactive selector and detail panel.
              We removed the duplicate AwsServiceSelector invocation here so only ONE selector appears on the page.
          */}
          <section
            className={`scSection scBlock archSectionOverride ${styles.sectionSurface}`}
            aria-labelledby="platform-arch-heading"
          >
            <div className="scContainerWide">
              <h2 id="platform-arch-heading" className={`${styles.sectionTitle} scSectionTitle`}>Platform Architecture</h2>
              <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                Security data plane, deterministic pipelines, governed execution.
              </p>

              <PlatformArchitecture />
            </div>
          </section>

          <DividerLine />

          <section
            className={`scSection scBlock ${styles.sectionSurface}`}
            aria-labelledby="aws-native-heading"
          >
            <div className="scContainer">
              <h2 id="aws-native-heading" className={`${styles.sectionTitle} scSectionTitle`}>AWS-Native Security &amp; Generative AI Advantage</h2>
              <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                Secure-by-default, governed inference, and prioritized ROI.
              </p>
              <div className={styles.dpGrid}>
                {awsAdvantageCards.map(card => (
                  <article className={styles.scCardSm} key={card.title}>
                    <h3 className={styles.scCardSmTitle}>{card.title}</h3>
                    <p className={styles.scCardSmBody}>{card.body}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>

          <footer
            className={`scSection scBlock ${styles.sectionSurface}`}
            aria-label="Site footer"
            role="contentinfo"
          >
            <div className="scContainer">
              <div className={styles.footer}>
                <ButtonPremium variant="secondary" className={`${styles.scButtonSecondary} ${styles.footerCta}`}>
                  Contact Sales
                </ButtonPremium>
                <AccessibilityHints />
              </div>
            </div>
          </footer>
        </main>
      </div>
    </Layout>
  );
}
