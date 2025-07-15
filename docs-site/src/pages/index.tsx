import type { ReactNode } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import LandingHero from '../components/LandingHero';
import StrategicAdvantage from '../components/StrategicAdvantage';
import AdvantageCards from '../components/AdvantageCards';
import ResilienceSection from '../components/ResilienceSection';
import FoundationSection from '../components/FoundationSection';
import CTASection from '../components/CTASection';
import LicenseFooter from '../components/LicenseFooter';

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Secure your future with Shieldcraft AI">
      <main>
        <LandingHero />
        <StrategicAdvantage />
        <AdvantageCards />
        <ResilienceSection />
        <LicenseFooter />
      </main>
    </Layout>
  );
}
