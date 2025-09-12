import React from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './recent-activity.module.css';

const mockActivity = [
    { id: 1, user: 'analyst@shieldcraft.ai', action: 'initiated a new attack simulation on "WebApp-Prod"', timestamp: '2 minutes ago' },
    { id: 2, user: 'system', action: 'automatically patched vulnerability CVE-2025-1234 on host "db-server-01"', timestamp: '15 minutes ago' },
    { id: 3, user: 'security.engineer@shieldcraft.ai', action: 'updated the policy for "S3 Bucket Encryption"', timestamp: '1 hour ago' },
    { id: 4, user: 'system', action: 'ingested new threat intelligence feed from "AlienVault OTX"', timestamp: '2 hours ago' },
    { id: 5, user: 'analyst@shieldcraft.ai', action: 'resolved alert #3: "Potential SQL Injection attempt"', timestamp: '3 hours ago' },
];

function RecentActivityPage() {
    return (
        <PortalLayout title="Recent Activity" description="Recent Activity in ShieldCraft AI">
            <h1>Recent Activity</h1>
            <div className={styles.activityFeed} role="list" aria-label="Recent activity feed">
                {mockActivity.map(item => (
                    <div key={item.id} className={styles.activityItem} role="listitem">
                        <div className={styles.activityIcon}></div>
                        <div className={styles.activityContent}>
                            <p><strong>{item.user}</strong> {item.action}</p>
                            <span className={styles.timestamp}>{item.timestamp}</span>
                        </div>
                    </div>
                ))}
            </div>
        </PortalLayout>
    );
}

export default RecentActivityPage;
