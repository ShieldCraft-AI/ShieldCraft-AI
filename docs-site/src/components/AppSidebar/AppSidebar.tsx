import React from 'react';
import Link from '@docusaurus/Link';
import styles from './AppSidebar.module.css';
import { isLoggedIn, onAuthChange } from '@site/src/utils/auth-cognito';
import NAV_ITEMS from '@site/src/constants/navItems';

type Props = {
    items?: { label: string; to: string }[];
};

export default function AppSidebar({ items }: Props) {
    // Persistent left sidebar; no toggle. Keep focus handling minimal.
    const firstLinkRef = React.useRef<HTMLAnchorElement | null>(null);
    const [navH, setNavH] = React.useState<number>(60);
    const [loggedIn, setLoggedIn] = React.useState<boolean>(false);
    React.useEffect(() => {
        firstLinkRef.current?.setAttribute('tabindex', '0');
        if (typeof window !== 'undefined') {
            try {
                const v = getComputedStyle(document.documentElement).getPropertyValue('--ifm-navbar-height');
                const px = parseInt(v.replace('px', '').trim(), 10);
                if (!Number.isNaN(px) && px > 0) setNavH(px);
            } catch { }
            (async () => {
                const authenticated = await isLoggedIn();
                setLoggedIn(authenticated);
            })();
            const unsubscribe = onAuthChange((isAuth) => setLoggedIn(isAuth));
            return () => { unsubscribe(); };
        }
    }, []);

    const navItems = items ?? NAV_ITEMS;

    if (!loggedIn) return null;
    const aside = (
        <aside
            className={styles.sidebar}
            aria-label="Primary navigation"
            style={{
                position: 'fixed',
                top: navH,
                left: 0,
                height: `calc(100vh - ${navH}px)`,
                width: 'max(15vw, 220px)',
                zIndex: 4000,
            }}
        >
            <div className={styles.header}>
                <h3 className={styles.title}>ShieldCraft</h3>
            </div>
            <div className={styles.sectionLabel}>Navigation</div>
            <nav className={styles.nav}>
                {navItems.map((it, idx) => (
                    <Link
                        key={it.to}
                        className={styles.item}
                        to={it.to}
                        ref={idx === 0 ? firstLinkRef : undefined}
                    >
                        {it.label}
                    </Link>
                ))}
            </nav>
            <div className={styles.spacer} />
            <div className={styles.footer}>v0.1</div>
        </aside>
    );
    return aside;
}
