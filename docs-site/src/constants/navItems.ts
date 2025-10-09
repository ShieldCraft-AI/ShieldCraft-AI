export type NavItem = {
    label: string;
    to: string;
};

// Canonical, left-sidebar-first ordering. Use this across header, sidebars and footer to avoid drift.
export const NAV_ITEMS: NavItem[] = [
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Monitoring', to: '/monitoring' },
    { label: 'Alerts', to: '/alerts' },
    { label: 'System Status', to: '/system-status' },
    { label: 'Recent Activity', to: '/recent-activity' },
    { label: 'Threat Intelligence', to: '/threat-feed' },
];

export default NAV_ITEMS;
