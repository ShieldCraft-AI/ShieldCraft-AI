import React from 'react';
import './vectorscan.css';
import Layout from '@theme/Layout';
import Hero from '@site/src/components/guardsuite/Hero';
import ValuePillars from '@site/src/components/guardsuite/ValuePillars';
import Microflow from '@site/src/components/guardsuite/Microflow';
import Determinism from '@site/src/components/guardsuite/Determinism';
import SignatureSection from '@site/src/components/guardsuite/SignatureSection';
import CLISection from '@site/src/components/guardsuite/CLISection';
import RiskCalculator from '@site/src/components/guardsuite/RiskCalculator';
import IntegrationsGrid from '@site/src/components/guardsuite/IntegrationsGrid';
import PricingCards from '@site/src/components/guardsuite/PricingCards';
import SecurityBand from '@site/src/components/guardsuite/SecurityBand';
import DeploymentSteps from '@site/src/components/guardsuite/DeploymentSteps';
import FAQ from '@site/src/components/guardsuite/FAQ';
import FinalCTA from '@site/src/components/guardsuite/FinalCTA';

export default function VectorScanPage(): JSX.Element {
    return (
        <Layout title="VectorScan - Deterministic Governance" description="VectorScan - Deterministic Governance for Your Cloud.">
            <main className="vs-page">
                <Hero />
                <ValuePillars />
                <Microflow />
                <Determinism />
                <SignatureSection />
                <CLISection />
                <RiskCalculator />
                <IntegrationsGrid />
                <PricingCards />
                <SecurityBand />
                <DeploymentSteps />
                <FAQ />
                <FinalCTA />
            </main>
        </Layout>
    );
}
