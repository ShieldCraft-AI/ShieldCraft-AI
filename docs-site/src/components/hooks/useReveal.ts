import { useEffect } from 'react';

/**
 * useReveal: Adds intersection observer reveal animation.
 * Apply class 'sc-reveal' to target elements; they get 'is-visible' when in view.
 */
export function useReveal(selector: string = '.sc-reveal', options?: IntersectionObserverInit) {
    useEffect(() => {
        if (typeof window === 'undefined') return;
        const els = Array.from(document.querySelectorAll<HTMLElement>(selector));
        if (!('IntersectionObserver' in window)) {
            els.forEach(el => el.classList.add('is-visible'));
            return;
        }
        const obs = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { rootMargin: '0px 0px -10% 0px', threshold: 0.2, ...(options || {}) });

        els.forEach(el => obs.observe(el));
        return () => obs.disconnect();
    }, [selector, options]);
}
