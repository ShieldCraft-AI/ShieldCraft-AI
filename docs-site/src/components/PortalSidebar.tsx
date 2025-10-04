import React from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import portalStyles from '../pages/portal.module.css';
import clsx from 'clsx';
import { usePortalMock } from '../context/PortalMockContext';

const navItems = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Monitoring', path: '/monitoring' },
    { label: 'Alerts', path: '/alerts' },
    { label: 'System Status', path: '/system-status' },
    { label: 'Recent Activity', path: '/recent-activity' },
    { label: 'Threat Intelligence', path: '/threat-feed' },
    // Documentation intentionally omitted from portal sidebar
];

type SidebarProps = {
    id?: string;
    ariaHidden?: boolean;
    onNavigate?: () => void;
};

function PortalSidebar({ id, ariaHidden, onNavigate }: SidebarProps) {
    const location = useLocation();
    const { counts } = usePortalMock();

    return (
        <aside id={id} aria-hidden={ariaHidden} className={portalStyles.sidebar}>
            <div className={portalStyles.sidebarHeader}>Navigation</div>
            <nav className={portalStyles.navigation} aria-label="Portal navigation">
                <ul>
                    {navItems.map(item => {
                        const isActive = location.pathname === item.path;
                        return (
                            <li key={item.label} className={clsx({ [portalStyles.active]: isActive })}>
                                <Link to={item.path} aria-current={isActive ? 'page' : undefined} onClick={onNavigate}>
                                    {item.label}
                                    {item.label === 'Alerts' && counts.total > 0 && (
                                        <span className={portalStyles.badge} aria-label={`Active alerts ${counts.total}`}>{counts.total}</span>
                                    )}
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>
        </aside>
    );
}

export default PortalSidebar;
