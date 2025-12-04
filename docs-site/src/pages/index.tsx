import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
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

type MicroCard = { title: string; body: string; href: string; icon: string; metric?: string };

const contextHighlights: MicroCard[] = [
  {
    title: 'Evidence-first telemetry',
    body: 'Normalize events and keep ingestion deterministic before automation acts.',
    href: '/data_inputs_overview',
    icon: '/aws-icons/Arch_AWS-Glue_48.svg',
    metric: '99.9% uptime'
  },
  {
    title: 'Guarded autonomy',
    body: 'Playbooks + approvals + budgets keep remediation auditable and reversible.',
    href: '/security_governance',
    icon: '/aws-icons/Arch_AWS-Step-Functions_48.svg',
    metric: '< 200ms response'
  },
  {
    title: 'Measured outcomes',
    body: 'FinOps and drift metrics keep ML risk and spend visible.',
    href: '/intro',
    icon: '/aws-icons/Arch_Amazon-CloudWatch_48.svg',
    metric: '40% cost reduction'
  },
];

export default function IndexPage(): JSX.Element {
  return (
    <Layout title="ShieldCraft AI - Autonomous Security on AWS" description="AWS-native autonomous threat detection and remediation. GenAI-powered security that detects, analyzes, and neutralizes threats in seconds-fully auditable.">
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
                    <ButtonPremium href="/intro" className="hero small" variant="secondary">Docs</ButtonPremium>
                  </div>
                </div>

                <div className={`${heroStyles.heroSurface} ${styles.heroSurface} scFadeIn`}>
                  <h1 className={`${heroStyles.heroTitle} ${styles.heroTitle}`}>Trusted Autonomy for AWS Security Teams</h1>
                  <p className={heroStyles.heroSubtitle}>
                    ShieldCraft detects threats, analyzes risk with GenAI, and executes remediation in seconds-fully autonomous, fully auditable.
                  </p>
                  <div className={heroStyles.heroActions}>
                    <ButtonPremium href="/intro" className="hero primaryCTA">See how it works</ButtonPremium>
                    <ButtonPremium href="/dashboard" className="hero" variant="secondary">View live dashboard</ButtonPremium>
                  </div>
                  <div className={heroStyles.heroNote}>
                    Trusted by security teams running regulated workloads on AWS · Deploy in hours, not months
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
                  <Link key={c.title} to={c.href} className={styles.contextCard}>
                    <div className={styles.cardIcon}>
                      <img src={c.icon} alt={`${c.title} icon`} width={32} height={32} />
                    </div>
                    <h3>{c.title}</h3>
                    <p>{c.body}</p>
                    {c.metric && <div className={styles.cardMetric}>{c.metric}</div>}
                  </Link>
                ))}
              </div>
            </div>
          </section>

          <DividerLine />

          {/* How It Works - moved up for prominence */}
          <section className={`scSection scBlock ${styles.sectionSurface}`} aria-labelledby="how-it-works-heading">
            <div className="scContainer">
              <div className={styles.contextIntro}>
                <p className={styles.contextEyebrow}>⚡ AUTONOMOUS SECURITY IN ACTION</p>
                <h2 id="how-it-works-heading" className={`${styles.sectionTitle} scSectionTitle`}>Threat to Action in Seconds</h2>
                <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                  Watch ShieldCraft detect, analyze, and neutralize threats autonomously-no human intervention required.
                </p>
              </div>
              <PlatformArchitecture showOnlyFlow={true} />
            </div>
          </section>

          <DividerLine />

          {/* Platform architecture */}
          <section className={`scSection scBlock ${styles.sectionSurface}`} aria-labelledby="platform-arch-heading">
            <div className={styles.archWrapper}>
              <h2 id="platform-arch-heading" className={`${styles.sectionTitle} scSectionTitle`}>Platform Architecture</h2>
              <p className={`${styles.sectionSubtitle} scSectionSubtitle`}>
                Security data plane, deterministic pipelines, governed execution.
              </p>

              <PlatformArchitecture showOnlySelector={true} />
            </div>
          </section>

          <DividerLine />

          <footer className={`scSection scBlock ${styles.sectionSurface}`} aria-label="Site footer" role="contentinfo">
            <div className="scContainer">
              <div className={styles.footer}>
                <ButtonPremium href="/pricing" variant="secondary" className={`${styles.scButtonSecondary} ${styles.footerCta}`}>View pricing</ButtonPremium>
                <AccessibilityHints />
              </div>
            </div>
          </footer>
        </main>
      </div>
    </Layout>
  );
}
