// @ts-nocheck
import Layout from '@theme/Layout';
import * as React from 'react';
import styles from './pricing.module.css';

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

const TIERS: Record<TierKey, { label: string }> = {
    starter: { label: 'Starter' },
    growth: { label: 'Growth' },
    enterprise: { label: 'Enterprise' },
};

export default function InfrastructurePage(): React.JSX.Element {
    const [infraTier, setInfraTier] = React.useState<TierKey>('starter');
    const mapRef = React.useRef<HTMLDivElement | null>(null);

    React.useEffect(() => {
        if (typeof document === 'undefined') return undefined;
        document.body.classList.add('infrastructure-page');
        return () => { document.body.classList.remove('infrastructure-page'); };
    }, []);

    const InfraRegionMap: React.FC<{ blueprint: InfraBlueprint }> = ({ blueprint }) => (
        <div className={styles.infraRegionMap}>
            {blueprint.perimeter?.length ? (
                <section className={styles.globalPerimeter} aria-label="Global guardrails and shared services">
                    <div className={styles.perimeterConnector} aria-hidden>
                        <span className={styles.perimeterConnectorLine} />
                    </div>
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
                        <div className={styles.regionWideTitle}>Regional platforms &amp; data services</div>
                        <div className={styles.regionWideGroups}>
                            {/**
                             * For the regional platforms section, shorten service labels by
                             * stripping common vendor prefixes like 'aws' or 'amazon' to save
                             * vertical space. Do this only for the displayed label; the
                             * underlying data is left untouched.
                             */}
                            {blueprint.regionWide.map(group => (
                                <div key={`region-${group.title}`} className={styles.infraGroup}>
                                    <div className={styles.groupTitle}>{group.title}</div>
                                    {group.description && <p className={styles.groupDescription}>{group.description}</p>}
                                    <div className={styles.servicePillRow}>
                                        {group.services.map(service => {
                                            const short = String(service).replace(/\b(?:aws|amazon)[:\-\s]?/ig, '').trim();
                                            const svcKey = String(service).replace(/\s*\(.+\)$/, '').trim();
                                            const present = (INFRA_PRESENCE[infraTier] && INFRA_PRESENCE[infraTier][svcKey]) || false;
                                            return (
                                                <span
                                                    key={`region-${group.title}-${service}`}
                                                    className={`${styles.servicePill} ${!present ? styles.serviceMissing : ''}`}>
                                                    {short}
                                                </span>
                                            );
                                        })}
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
                                                                            <span key={`${az.name}-${subnet.name}-${group.title}-${service}`} className={styles.servicePill}>{service}</span>
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
                                    <span key={`failover-${service}`} className={styles.servicePill}>{service}</span>
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
                                    <span key={`perimeter-${group.title}-${service}`} className={styles.servicePill}>{service}</span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    return (
        <Layout title="Infrastructure" description="ShieldCraft AI infrastructure blueprints and global services.">
            <div className={`${styles.pricingPageWrapper} pricing-page-wrapper`}>
                <div className={styles.pricingInner}>
                    <h1 className={styles.pageTitle}>Infrastructure Blueprints</h1>
                    <div className={styles.infraHeaderSticky}>
                        <div className={styles.infraHeader}>
                            <div className={styles.infraTierToggle} role="radiogroup" aria-label="Select infrastructure tier">
                                {Object.keys(TIERS).map(k => {
                                    const t = k as TierKey;
                                    return (
                                        <button
                                            key={`infra-toggle-${t}`}
                                            type="button"
                                            role="radio"
                                            aria-checked={infraTier === t}
                                            className={`${styles.infraToggleButton} ${infraTier === t ? styles.infraToggleButtonActive : ''}`}
                                            onClick={() => {
                                                setInfraTier(t);
                                            }}
                                        >
                                            {TIERS[t].label}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    <div ref={mapRef}>
                        <InfraRegionMap blueprint={INFRA_BLUEPRINT[infraTier]} />
                    </div>
                </div>
            </div>
        </Layout>
    );
}
