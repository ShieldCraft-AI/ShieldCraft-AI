import React, { JSX } from 'react';
import Layout from '@theme/Layout';
import styles from '../pages/portal.module.css';
import PortalSidebar from './PortalSidebar';

type Props = {
  title?: string;
  description?: string;
  children: React.ReactNode;
};

export default function PortalLayout({
  title = 'Portal',
  description = 'ShieldCraft AI Portal',
  children,
}: Props): JSX.Element {
  return (
    <Layout title={title} description={description} noFooter wrapperClassName="portalWrapper">
      <div className={styles.container}>
        <PortalSidebar />
        <main className={styles.mainContent} role="main">
          <header className={styles.header}>
            <div className={styles.titleArea}>
              <h2 style={{ margin: 0 }}>{title}</h2>
              <span className={styles.envBadge} aria-label="Environment">dev</span>
            </div>
            <div className={styles.searchBar}>
              <input type="text" placeholder="Search…" aria-label="Search portal" />
            </div>
          </header>
          {children}
        </main>
      </div>
    </Layout>
  );
}
