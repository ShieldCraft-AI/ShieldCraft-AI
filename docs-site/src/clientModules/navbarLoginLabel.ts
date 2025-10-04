import { isLoggedIn, onAuthChange } from '@site/src/utils/auth-cognito';

function updateLabel() {
    const isIn = isLoggedIn();
    const sel = 'a[href="/dashboard"],a[href="/dashboard"]';
    const link = document.querySelector<HTMLAnchorElement>(`.navbar ${sel}, .navbar__items ${sel}`) || document.querySelector<HTMLAnchorElement>(sel);
    if (link) {
        const newText = isIn ? 'Logout' : 'Login';
        if (link.textContent !== newText) link.textContent = newText;
        link.setAttribute('aria-label', newText);
    }
}

export default function () {
    if (typeof window === 'undefined') return;
    // Initial sync
    requestAnimationFrame(updateLabel);
    // React to auth changes
    const off = onAuthChange(() => updateLabel());
    // Also react to route/nav changes; Docusaurus may rerender navbar
    window.addEventListener('popstate', updateLabel);
    window.addEventListener('hashchange', updateLabel);
    document.addEventListener('click', (e) => {
        const t = e.target as HTMLElement | null;
        if (!t) return;
        const a = t.closest('a');
        if (a) setTimeout(updateLabel, 0);
    }, true);
    return () => { off && off(); };
}
