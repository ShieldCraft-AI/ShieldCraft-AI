import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import type { ReactNode } from 'react';
import AdvantageCards from '../components/AdvantageCards';
import { useHeroScrollProgress } from '../components/hooks/useHeroScrollProgress';
import InfoCardsRow from '../components/InfoCardsRow';
import LandingHero from '../components/LandingHero';
import OutcomePillars from '../components/OutcomePillars';
import PlatformArchitecture from '../components/PlatformArchitecture';
import ResilienceSection from '../components/ResilienceSection';

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
          <AdvantageCards />
          <OutcomePillars />
          <PlatformArchitecture />
          <InfoCardsRow />
          <ResilienceSection />
        </div>
      </main>
    </Layout>
  );
}
