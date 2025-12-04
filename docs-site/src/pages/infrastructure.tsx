// @ts-nocheck
import Layout from '@theme/Layout';
import * as React from 'react';

import styles from './pricing.module.css';
import { ServicePill } from './pricing';

type TierKey = 'starter' | 'growth' | 'enterprise';

// Minimal types and data needed for the infra blueprint and selector.
type InfraGroup = {
    title: string;
    services: string[];
    description?: string;
};

type Subnet = {
    name: string;
    type: 'public' | 'private' | 'isolated' | 'edge' | 'transit';
    cidr?: string;
    notes?: string;
    workloads?: InfraGroup[];
};

type InfraAZ = {
    name: string;
    summary: string;
    groups: InfraGroup[];
    subnets?: Subnet[];
};

type FailoverPlan = { title: string; description: string; services: string[]; azPath: string[]; cadence?: string };

type InfraBlueprint = {
    region: string;
    regionWide: InfraGroup[];
    azs: InfraAZ[];
    perimeter?: InfraGroup[];
    failover?: FailoverPlan;
};

// Lightweight copy of INFRA_BLUEPRINT from pricing.tsx (keeps content in sync visually)
const INFRA_BLUEPRINT: Record<TierKey, InfraBlueprint> = require('./pricing').INFRA_BLUEPRINT;

// Presence map produced by scripts/check_infra_sync.py (keeps UI in sync with config values)
const INFRA_PRESENCE: Record<string, Record<string, boolean>> = require('../data/infra_presence.json');

const TIER_PRICING: Record<TierKey, number> = {
    starter: 800,
    growth: 1900,
    enterprise: 6500,
};
const TIERS: Record<TierKey, { label: string; price: number }> = {
    starter: { label: 'Starter', price: TIER_PRICING.starter },
    growth: { label: 'Growth', price: TIER_PRICING.growth },
    enterprise: { label: 'Enterprise', price: TIER_PRICING.enterprise },
};

export default function InfrastructurePage(): React.JSX.Element {
    const [infraTier, setInfraTier] = React.useState<TierKey>('starter');
    const [hoverTier, setHoverTier] = React.useState<TierKey | null>(null);
    const mapRef = React.useRef<HTMLDivElement | null>(null);

    React.useEffect(() => {
        if (typeof document === 'undefined') return undefined;
        document.body.classList.add('infrastructure-page');
        return () => { document.body.classList.remove('infrastructure-page'); };
    }, []);


    // Only one card can be highlighted at a time: hover takes precedence, else selection
    const effectiveTier = hoverTier ?? infraTier;
    // Use the ServicePill component from pricing.tsx for consistent rendering
    const getServicePill = (service: string, key: string, present: boolean = true) => (
        <span key={key} style={{ display: 'inline-flex' }}>
            <ServicePill label={present ? service : `${service} (not present)`} />
        </span>
    );

    const InfraRegionMap: React.FC<{ blueprint: InfraBlueprint }> = ({ blueprint }) => (
        <div className={styles.infraRegionMap}>
            {/* Removed perimeterConnectorLine to eliminate the short vertical line at the top of the region container */}
            {blueprint.perimeter?.length ? (
                <section className={styles.globalPerimeter} aria-label="Global guardrails and shared services">
                    {/* perimeterConnectorLine fully removed */}
                </section>
            ) : null}
            <div className={styles.regionCanvas}>
                <div className={styles.regionHeader}>
                    <div>
                        <h3 className={styles.regionTitle}>{blueprint.region}</h3>
                    </div>
                </div>
                {blueprint.regionWide?.length ? (
                    <div className={styles.regionWideSection}>
                        <div className={styles.regionWideTitle} style={{ marginBottom: 22 }}>Regional platforms &amp; data services</div>
                        <div className={styles.regionWideGroups}>
                            {blueprint.regionWide.map(group => (
                                <div key={`region-${group.title}`} className={styles.infraGroup}>
                                    <div className={styles.groupTitle}>{group.title}</div>
                                    {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                    <div className={styles.servicePillRow}>
                                        {group.services.map(service => (
                                            <React.Fragment key={`region-${group.title}-${service}`}>
                                                {getServicePill(service, `region-${group.title}-${service}`, true)}
                                            </React.Fragment>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : null}
                <div className={styles.vpcFrame}>
                    <div className={styles.vpcBadge}>VPC</div>
                    <div className={styles.azWrapper}>
                        {blueprint.azs.map(az => (
                            <div key={az.name} className={styles.azCard}>
                                <div className={styles.azHeader}>
                                    <div className={styles.azName}>{az.name}</div>
                                    <p className={styles.azSummary}>{az.summary}</p>
                                </div>
                                {az.subnets?.length ? (
                                    <div className={styles.subnetCluster}>
                                        <div className={styles.subnetTitle}>Subnets &amp; workloads</div>
                                        <div className={styles.subnetList}>
                                            {az.subnets.map(subnet => (
                                                <div key={`${az.name}-${subnet.name}`} className={styles.subnetCard} data-subnet-type={subnet.type}>
                                                    <div className={styles.subnetHeader}>
                                                        <span className={styles.subnetPill}>{subnet.name}</span>
                                                        {subnet.notes ? <span className={styles.subnetNotes}>{subnet.notes}</span> : null}
                                                    </div>
                                                    {subnet.workloads?.length ? (
                                                        <div className={styles.subnetWorkloads}>
                                                            {subnet.workloads.map(group => (
                                                                <div key={`${az.name}-${subnet.name}-${group.title}`} className={styles.infraGroup}>
                                                                    <div className={styles.groupTitle}>{group.title}</div>
                                                                    {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                                                    <div className={styles.servicePillRow}>
                                                                        {group.services.map(service => (
                                                                            <React.Fragment key={`${az.name}-${subnet.name}-${group.title}-${service}`}>
                                                                                {getServicePill(service, `${az.name}-${subnet.name}-${group.title}-${service}`)}
                                                                            </React.Fragment>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    ) : null}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : null}
                            </div>
                        ))}
                    </div>
                    {blueprint.failover ? (
                        <div className={styles.failoverRibbon}>
                            <div className={styles.failoverHeader}>
                                <div className={styles.failoverHeadingGroup}>
                                    <span className={styles.failoverBadge}>Multi-AZ failover</span>
                                    <div className={styles.failoverTitle}>{blueprint.failover.title}</div>
                                </div>
                                {blueprint.failover.cadence ? (
                                    <div className={styles.failoverCadence}>{blueprint.failover.cadence}</div>
                                ) : null}
                            </div>
                            <p className={styles.failoverDescription}>{blueprint.failover.description}</p>
                            <div className={styles.servicePillRow}>
                                {blueprint.failover.services.map(service => (
                                    <React.Fragment key={`failover-${service}`}>
                                        {getServicePill(service, `failover-${service}`)}
                                    </React.Fragment>
                                ))}
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
            <div className={styles.perimeterStrip}>
                <div className={styles.perimeterTitle}>Global services</div>
                <div className={styles.perimeterGroups}>
                    {blueprint.perimeter.map(group => (
                        <div key={`perimeter-${group.title}`} className={styles.infraGroup}>
                            <div className={styles.groupTitle}>{group.title}</div>
                            {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                            <div className={styles.servicePillRow}>
                                {group.services.map(service => (
                                    <React.Fragment key={`perimeter-${group.title}-${service}`}>
                                        {getServicePill(service, `perimeter-${group.title}-${service}`)}
                                    </React.Fragment>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    // Tier button copy inspired by /pricing AWS services for each tier
    const tierCopy: Record<TierKey, string> = {
        starter: 'Telemetry, ingestion, and S3 data lake. GuardDuty, Lambda, EventBridge.',
        growth: 'Scale with ML ops, OpenSearch, Step Functions, and cross-account automations.',
        enterprise: 'Global guardrails, auto-scaling compute, advanced security, and compliance.',
    };

    return (
        <Layout title="Infrastructure" description="ShieldCraft AI infrastructure blueprints and global services.">
            <div className={`${styles.pricingPageWrapper} pricing-page-wrapper`}>
                <div className={styles.pricingInner}>
                    <h1 className={styles.pageTitle} style={{ marginTop: 24, marginBottom: 24 }}>Infrastructure Blueprints</h1>
                    <div className={styles.infraHeaderSticky}>
                        <div className={styles.infraHeader}>
                            <div className={styles.infraTierToggle} style={{ justifyContent: 'center', width: '100%' }} role="radiogroup" aria-label="Select infrastructure tier">
                                {Object.keys(TIERS).map(k => {
                                    const t = k as TierKey;
                                    // Only highlight if hovered or selected (hover takes precedence)
                                    const isActive = (hoverTier ?? infraTier) === t;
                                    return (
                                        <button
                                            key={`infra-toggle-${t}`}
                                            type="button"
                                            role="radio"
                                            aria-checked={isActive}
                                            className={isActive ? `${styles.infraToggleButton} ${styles.infraToggleButtonActive}` : styles.infraToggleButton}
                                            onClick={() => setInfraTier(t)}
                                            onMouseEnter={() => setHoverTier(t)}
                                            onMouseLeave={() => setHoverTier(null)}
                                            style={{
                                                display: 'flex',
                                                flexDirection: 'column',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                gap: 8,
                                                padding: '28px 36px',
                                                marginRight: 18,
                                                minWidth: 180,
                                                minHeight: 90,
                                                fontSize: '1.18rem',
                                                fontWeight: 700,
                                                borderRadius: 18,
                                                boxShadow: isActive ? '0 4px 24px rgba(16,185,129,0.10)' : undefined,
                                                transition: 'all .18s',
                                            }}
                                        >
                                            <span style={{ fontWeight: 800, fontSize: '1.18em', marginBottom: 4 }}>{TIERS[t].label}</span>
                                            <span style={{ fontSize: '1.08em', fontWeight: 600, color: '#16a34a', marginBottom: 4 }}>
                                                ${TIERS[t].price.toLocaleString()}/mo
                                            </span>
                                            <span style={{ fontSize: '.98em', fontWeight: 500, color: '#2563eb', opacity: 0.88, textAlign: 'center', lineHeight: 1.3 }}>{tierCopy[t]}</span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    <div ref={mapRef}>
                        <InfraRegionMap blueprint={INFRA_BLUEPRINT[effectiveTier]} />
                    </div>
                </div>
            </div>
        </Layout>
    );
}
