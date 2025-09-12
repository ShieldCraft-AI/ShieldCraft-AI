import React from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './system-status.module.css';

const mockStatus = [
    { component: 'Data Ingestion Pipeline', status: 'Operational', details: 'Last event processed: 2 seconds ago' },
    { component: 'AI Core Model Server', status: 'Operational', details: 'Healthy, 2/2 nodes online' },
    { component: 'Vector Database', status: 'Degraded', details: 'High latency detected on index "threat-intel-prod"' },
    { component: 'Alerting Subsystem', status: 'Operational', details: 'All channels active' },
    { component: 'Remediation Engine', status: 'Maintenance', details: 'Scheduled maintenance until 11:00 UTC' },
];

function SystemStatusPage() {
    return (
        <PortalLayout title="System Status" description="System Status in ShieldCraft AI">
            <h1>System Status</h1>
            <div className={styles.statusGrid}>
                {mockStatus.map(item => (
                    <div key={item.component} className={`${styles.statusCard} ${styles[item.status.toLowerCase() as 'operational' | 'degraded' | 'maintenance' | 'outage']}`}>
                        <h3>{item.component}</h3>
                        <span className={styles.statusBadge}>{item.status}</span>
                        <p className={styles.statusDetails}>{item.details}</p>
                    </div>
                ))}
            </div>
        </PortalLayout>
    );
}

export default SystemStatusPage;
