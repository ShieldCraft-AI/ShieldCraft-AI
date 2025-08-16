import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import styles from './portal.module.css';
import clsx from 'clsx';

function PortalPage() {
    const [activeLink, setActiveLink] = useState('Dashboard');
    const navItems = ['Dashboard', 'Alerts', 'Attack Simulations', 'Threat Intelligence', 'Remediation', 'Analytics', 'Settings'];
    const location = useLocation();

    useEffect(() => {
        const hash = location.hash.replace('#', '');
        const currentItem = navItems.find(item => item.toLowerCase().replace(/ /g, '-') === hash);
        if (currentItem) {
            setActiveLink(currentItem);
        } else {
            setActiveLink('Dashboard');
        }
    }, [location.hash]);


    return (
        <Layout title="Portal" description="ShieldCraft AI Portal" noFooter>
            <div className={styles.container}>
                <aside className={styles.sidebar}>
                    <div className={styles.logo}>
                        <Link to="/portal">ShieldCraft AI</Link>
                    </div>
                    <nav className={styles.navigation}>
                        <ul>
                            {navItems.map(item => (
                                <li key={item} className={clsx({[styles.active]: activeLink === item})} onClick={() => setActiveLink(item)}>
                                    <Link to={`/portal#${item.toLowerCase().replace(/ /g, '-')}`}>{item}</Link>
                                </li>
                            ))}
                        </ul>
                    </nav>
                </aside>
                <main className={styles.mainContent}>
                    <header className={styles.header}>
                        <div className={styles.searchBar}>
                            <input type="text" placeholder="Search..." />
                        </div>
                        <div className={styles.userInfo}>
                            <span>Welcome, Analyst</span>
                            <Link className={clsx('button', 'button--secondary')} to="/login">Logout</Link>
                        </div>
                    </header>
                    <section className={styles.dashboard}>
                        <div className={styles.widget}>
                            <h3>Active Alerts</h3>
                            <p>Placeholder for active alerts widget.</p>
                        </div>
                        <div className={styles.widget}>
                            <h3>System Status</h3>
                            <p>Placeholder for system status widget.</p>
                        </div>
                        <div className={styles.widget}>
                            <h3>Recent Activity</h3>
                            <p>Placeholder for recent activity widget.</p>
                        </div>
                        <div className={styles.widget}>
                            <h3>Threat Feed</h3>
                            <p>Placeholder for threat feed widget.</p>
                        </div>
                    </section>
                </main>
            </div>
        </Layout>
    );
}

export default PortalPage;
