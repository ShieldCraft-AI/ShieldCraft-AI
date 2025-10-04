import React from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './404.module.css';

export default function ServerError() {
    return (
        <Layout title="Something went wrong">
            <main className={styles.wrapper}>
                <div className={styles.card}>
                    <h1>Something went wrong.</h1>
                    <p>An unexpected error occurred. You can try these options while we sort it out:</p>
                    <ul>
                        <li><button onClick={() => window.location.reload()} className="button button--primary" style={{ cursor: 'pointer' }}>Reload this page</button></li>
                        <li><Link to="/">Home</Link></li>
                        <li><Link to="/intro">Documentation</Link></li>
                    </ul>
                    <div className={styles.hint}>If the problem persists, please try again later.</div>
                </div>
            </main>
        </Layout>
    );
}
