import React from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './404.module.css';

export default function NotFound() {
    return (
        <Layout title="Not found">
            <main className={styles.wrapper}>
                <div className={styles.card}>
                    <h1>We lost the signal.</h1>
                    <p>The page you requested doesn’t exist or moved. Try one of these:</p>
                    <ul>
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/dashboard">Dashboard</Link></li>
                        <li><Link to="/intro">Documentation</Link></li>
                    </ul>
                    <div className={styles.hint}>If you bookmarked a docs page, use the Documentation link above to browse.</div>
                </div>
            </main>
        </Layout>
    );
}
