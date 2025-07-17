import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import type { ReactNode } from 'react';
import AdvantageCards from '../components/AdvantageCards';
import LandingHero from '../components/LandingHero';
import LicenseFooter from '../components/LicenseFooter';
import ResilienceSection from '../components/ResilienceSection';
import InfoCardsRow from '../components/InfoCardsRow';
import AwsStack from '../components/AwsStack';
import IconCarousel from '../components/IconCarousel';

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Secure your future with Shieldcraft AI">
      <main>
        <LandingHero />
        <AdvantageCards />
        <InfoCardsRow />
        <AwsStack />
        <ResilienceSection />
        <IconCarousel />
        <LicenseFooter />
      </main>
    </Layout>
  );
}
