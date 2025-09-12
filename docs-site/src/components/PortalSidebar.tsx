import React from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import portalStyles from '../pages/portal.module.css';
import clsx from 'clsx';

const navItems = [
    { label: 'Dashboard', path: '/portal' },
    { label: 'Alerts', path: '/alerts' },
    { label: 'System Status', path: '/system-status' },
    { label: 'Recent Activity', path: '/recent-activity' },
    { label: 'Threat Intelligence', path: '/threat-feed' },
];

function PortalSidebar() {
    const location = useLocation();

    return (
        <aside className={portalStyles.sidebar}>
            <div className={portalStyles.logo}>
                <Link to="/portal">ShieldCraft AI</Link>
            </div>
            <nav className={portalStyles.navigation} aria-label="Portal navigation">
                <ul>
                    {navItems.map(item => {
                        const isActive = location.pathname === item.path;
                        return (
                            <li key={item.label} className={clsx({ [portalStyles.active]: isActive })}>
                                <Link to={item.path} aria-current={isActive ? 'page' : undefined}>{item.label}</Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>
        </aside>
    );
}

export default PortalSidebar;
