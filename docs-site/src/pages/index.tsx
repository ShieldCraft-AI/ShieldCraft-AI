import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import type { ReactNode } from 'react';
import AdvantageCards from '../components/AdvantageCards';
import { useHeroScrollProgress } from '../components/hooks/useHeroScrollProgress';
import InfoCardsRow from '../components/InfoCardsRow';
import LandingHero from '../components/LandingHero';
import PlatformArchitecture from '../components/PlatformArchitecture';
import ResilienceSection from '../components/ResilienceSection';
import FullWidthFeature from '../components/FullWidthFeature';

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  useHeroScrollProgress();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Secure your future with Shieldcraft AI">
      <main>
        <div>
          <LandingHero />
          <div className="sc-full-bleed sc-minvh-lg-66">
            <AdvantageCards />
          </div>
          <div className="sc-full-bleed sc-minvh-lg-66" style={{ marginTop: '4.5rem', marginBottom: '0.5rem' }}>
            <FullWidthFeature
              heading="Unified Security Data Plane & Governed Deployment Engine on AWS"
              description="The platform utilizes AWS Proton and CDK Constructs to seamlessly ingest, enrich, and correlate security telemetry. Actionable insights are delivered into workflows, fortified by policy-grade guardrails and deterministic cost control."
              primaryHref="/architecture-overview"
              primaryLabel="Review The MLOps Governance (The Proof)"
              secondaryHref="/plugins"
              secondaryLabel="Explore The Full Product Suite"
            />
          </div>
          <div className="sc-wide-content">
            <PlatformArchitecture />
          </div>
          <div className="sc-wide-content sc-minvh-lg-66">
            <InfoCardsRow />
          </div>
          <div className="sc-full-bleed sc-minvh-lg-66">
            <ResilienceSection />
          </div>
        </div>
      </main>
    </Layout>
  );
}
