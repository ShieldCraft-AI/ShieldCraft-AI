import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import { useEffect } from 'react';
import { useLocation } from '@docusaurus/router';

// This client module restores the user's scroll position when they navigate back
// to a page, and preserves scroll after in-page interactions (e.g., expanding content).
// It uses sessionStorage to track scroll per pathname + hash.

const KEY_PREFIX = 'sc-scroll:';

function saveScroll(pathKey: string) {
    try {
        sessionStorage.setItem(KEY_PREFIX + pathKey, String(window.scrollY));
    } catch { }
}

function readScroll(pathKey: string): number | undefined {
    try {
        const v = sessionStorage.getItem(KEY_PREFIX + pathKey);
        return v ? Number(v) : undefined;
    } catch {
        return undefined;
    }
}

export function onRouteDidUpdate() {
    if (!ExecutionEnvironment.canUseDOM) return;
    // When route updates complete, try restoring stored scroll for this location
    // Defer to next frame to avoid fighting layout shifts
    requestAnimationFrame(() => {
        const { pathname, hash } = window.location;
        const key = pathname + (hash || '');
        const y = readScroll(key);
        if (typeof y === 'number' && !Number.isNaN(y)) {
            window.scrollTo({ top: y });
        } else if (hash) {
            // Default browser behavior for hash anchors
            const el = document.getElementById(hash.slice(1));
            if (el) el.scrollIntoView();
        }
    });
}

export function onRouteWillChange() {
    if (!ExecutionEnvironment.canUseDOM) return;
    const { pathname, hash } = window.location;
    const key = pathname + (hash || '');
    saveScroll(key);
}

// Also persist on scroll during long content interaction
export default function useScrollPersistence() {
    if (!ExecutionEnvironment.canUseDOM) return;
    const loc = useLocation();
    useEffect(() => {
        const handler = () => saveScroll(loc.pathname + (loc.hash || ''));
        window.addEventListener('scroll', handler, { passive: true });
        return () => window.removeEventListener('scroll', handler);
    }, [loc.pathname, loc.hash]);
}
