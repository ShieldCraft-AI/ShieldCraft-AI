import React from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './404.module.css';

export default function NotFound() {
    return (
        <Layout title="Not found">
            <main className={styles.wrapper}>
                <div className={styles.card}>
                    <div className={styles.iconWrapper}>⚠️</div>
                    <h1>We lost signal.</h1>
                    <p>The page you requested does not exist or moved.</p>

                    <div className={styles.linkGrid}>
                        <Link to="/" className={styles.linkCard}>Home</Link>
                        <Link to="/dashboard" className={styles.linkCard}>Dashboard</Link>
                        <Link to="/intro" className={styles.linkCard}>Docs</Link>
                        <Link to="/pricing" className={styles.linkCard}>Pricing</Link>
                    </div>

                    <div className={styles.hint}>If you bookmarked a docs page, use the Docs link above to browse.</div>
                </div>
            </main>
        </Layout>
    );
}
