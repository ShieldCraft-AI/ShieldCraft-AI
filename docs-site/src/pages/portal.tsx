import React from 'react';
import Link from '@docusaurus/Link';
import styles from './portal.module.css';
import PortalLayout from '../components/PortalLayout';

function PortalPage() {
    return (
        <PortalLayout title="Portal" description="ShieldCraft AI Portal">
            <div className={styles.statsRow} aria-label="Key metrics">
                <div className={styles.statCard}>
                    <div className={styles.statLabel}>Findings (24h)</div>
                    <div className={styles.statValue}>128</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statLabel}>Critical</div>
                    <div className={styles.statValue}>3</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statLabel}>Mean TTR</div>
                    <div className={styles.statValue}>14m</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statLabel}>Coverage</div>
                    <div className={styles.statValue}>92%</div>
                </div>
            </div>

            <div className={styles.sectionTitle}>Explore</div>
            <section className={styles.dashboard} aria-label="Dashboard widgets">
                <div className={styles.widget}>
                    <Link to="/alerts">
                        <h3>Active Alerts</h3>
                        <p>GuardDuty, Security Hub, Inspector findings unified with severity and context.</p>
                        <small>Happy path: zero criticals. Unhappy path: actionable runbooks.</small>
                    </Link>
                </div>
                <div className={styles.widget}>
                    <Link to="/system-status">
                        <h3>System Status</h3>
                        <p>Ingestion, AI Core, Vector DB, and Remediation health at a glance.</p>
                        <small>Designed for resilience; degraded modes visible fast.</small>
                    </Link>
                </div>
                <div className={styles.widget}>
                    <Link to="/recent-activity">
                        <h3>Recent Activity</h3>
                        <p>Analyst actions, automated remediations, and pipeline operations.</p>
                        <small>Full auditability with environment-safe names.</small>
                    </Link>
                </div>
                <div className={styles.widget}>
                    <Link to="/threat-feed">
                        <h3>Threat Intelligence</h3>
                        <p>Feeds plus internal signals; mapped to cloud TTPs and assets.</p>
                        <small>Ready for RAG over curated intel and findings.</small>
                    </Link>
                </div>
            </section>
        </PortalLayout>
    );
}

export default PortalPage;
