import React, { JSX, useEffect, useRef, useState } from 'react';
import Layout from '@theme/Layout';
import styles from '../pages/portal.module.css';
import PortalSidebar from './PortalSidebar';
import { PortalMockProvider, usePortalMock } from '../context/PortalMockContext';

type Props = {
  title?: string;
  description?: string;
  children: React.ReactNode;
  showEnvSelector?: boolean;
  showSearchBar?: boolean;
};

// Move Content component outside to prevent re-creation on parent re-renders
function PortalContent({ title, children, showEnvSelector = true, showSearchBar = true }: { title: string; children: React.ReactNode; showEnvSelector?: boolean; showSearchBar?: boolean }) {
  const { env, setEnv, searchQuery, setSearchQuery } = usePortalMock();
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
    try { return window.matchMedia('(max-width: 960px)').matches; } catch { return false; }
  });
  const savedSidebarValue = useRef<boolean | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(max-width: 960px)');
    const handleChange = (event: MediaQueryListEvent | MediaQueryList) => {
      const matching = 'matches' in event ? event.matches : (event as MediaQueryList).matches;
      setIsMobile(matching);
    };

    handleChange(mq);
    if (typeof mq.addEventListener === 'function') mq.addEventListener('change', handleChange);
    else if (typeof mq.addListener === 'function') mq.addListener(handleChange);
    return () => {
      if (typeof mq.removeEventListener === 'function') mq.removeEventListener('change', handleChange);
      else if (typeof mq.removeListener === 'function') mq.removeListener(handleChange);
    };
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const path = window.location?.pathname || '';
      // If landing on the monitoring page, always start with the sidebar closed
      if (path === '/monitoring' || path.startsWith('/monitoring/')) {
        savedSidebarValue.current = false;
        if (!isMobile) setSidebarOpen(false);
        try {
          sessionStorage.setItem('portal-sidebar-open', 'false');
        } catch { }
        return;
      }

      const saved = sessionStorage.getItem('portal-sidebar-open');
      if (saved !== null) {
        savedSidebarValue.current = saved === 'true';
        if (!isMobile) setSidebarOpen(savedSidebarValue.current);
      }
    } catch {
      savedSidebarValue.current = null;
    }
  }, [isMobile]);

  useEffect(() => {
    if (!isMobile || savedSidebarValue.current === null) return;
    setSidebarOpen(false);
  }, [isMobile]);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    if (isMobile && sidebarOpen) {
      const previous = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = previous;
      };
    }
    return;
  }, [isMobile, sidebarOpen]);

  const toggleSidebar = React.useCallback(() => {
    setSidebarOpen(v => {
      const newValue = !v;
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('portal-sidebar-open', String(newValue));
      }
      return newValue;
    });
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSidebarOpen(false);
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('portal-sidebar-open', 'false');
        }
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);
  return (
    <div className={`${styles.container} ${sidebarOpen ? '' : styles.collapsed}`}>
      {isMobile && sidebarOpen && (
        <div
          className={styles.mobileBackdrop}
          onClick={() => {
            setSidebarOpen(false);
            if (typeof window !== 'undefined') {
              sessionStorage.setItem('portal-sidebar-open', 'false');
            }
          }}
        />
      )}
      <PortalSidebar id="portal-sidebar" ariaHidden={isMobile && !sidebarOpen} onNavigate={() => {
        setSidebarOpen(false);
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('portal-sidebar-open', 'false');
        }
      }} />
      <main
        className={styles.mainContent}
        role="main"
        onClick={sidebarOpen ? (e) => {
          // Only close sidebar if clicking on the main content itself, not on interactive elements
          if (e.target === e.currentTarget) {
            setSidebarOpen(false);
            if (typeof window !== 'undefined') {
              sessionStorage.setItem('portal-sidebar-open', 'false');
            }
          }
        } : undefined}
      >
        <header className={styles.header}>
          <div className={styles.titleArea}>
            <button
              type="button"
              className={styles.iconButton}
              aria-label={sidebarOpen ? 'Collapse menu' : 'Expand menu'}
              aria-controls="portal-sidebar"
              aria-expanded={sidebarOpen}
              onClick={toggleSidebar}
            >
              ≡
            </button>
            <h2 style={{ margin: 0 }}>{title}</h2>
            {showEnvSelector && <span className={styles.envBadge} aria-label="Environment">{env}</span>}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {showSearchBar && (
              <div className={styles.searchBar}>
                <input
                  type="text"
                  placeholder="Search…"
                  aria-label="Search portal"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            )}
            {showEnvSelector && (
              <select
                aria-label="Select environment"
                className={styles.envSelect}
                value={env}
                onChange={(e) => setEnv(e.target.value as 'dev' | 'staging' | 'prod')}
              >
                <option value="dev">dev</option>
                <option value="staging">staging</option>
                <option value="prod">prod</option>
              </select>
            )}
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}

export default function PortalLayout({
  title = 'Portal',
  description = 'ShieldCraft AI Portal',
  children,
  showEnvSelector = true,
  showSearchBar = true,
}: Props): JSX.Element {
  return (
    <Layout title={title} description={description} noFooter wrapperClassName="portalWrapper">
      <PortalMockProvider>
        <PortalContent title={title} showEnvSelector={showEnvSelector} showSearchBar={showSearchBar}>{children}</PortalContent>
      </PortalMockProvider>
    </Layout>
  );
}
