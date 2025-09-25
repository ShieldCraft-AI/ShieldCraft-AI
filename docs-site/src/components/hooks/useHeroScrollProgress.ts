import { useEffect } from 'react';

/**
 * Sets a root CSS variable --sc-hero-progress in [0,1] representing scroll position
 * relative to first viewport height. Used for smooth hero->section transition.
 */
export function useHeroScrollProgress() {
    useEffect(() => {
        let frame = 0;
        const update = () => {
            frame = 0;
            const h = window.innerHeight || 1;
            const p = Math.min(1, window.scrollY / h);
            document.documentElement.style.setProperty('--sc-hero-progress', p.toString());
        };
        const onScroll = () => { if (frame) return; frame = requestAnimationFrame(update); };
        window.addEventListener('scroll', onScroll, { passive: true });
        update();
        return () => {
            window.removeEventListener('scroll', onScroll);
            if (frame) cancelAnimationFrame(frame);
            document.documentElement.style.removeProperty('--sc-hero-progress');
        };
    }, []);
}
