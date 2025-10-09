// Debug helper
function scDebug(...args: any[]) {
    try {
        if (typeof window !== 'undefined' && (window as any).__SC_AUTH_DEBUG__) {
            // eslint-disable-next-line no-console
            console.debug('[SC-NAVBAR]', ...args);
        }
    } catch { /* ignore */ }
}

// Create a simpler auth check that works in production
async function isLoggedInSimple(): Promise<boolean> {
    try {
        // Check for Cognito tokens in localStorage directly
        const clientId = '2jio5rlqn6r2qe0otrgip4d5bp';
        const tokenKey = `CognitoIdentityServiceProvider.${clientId}.oauthSignIn`;
        const tokenData = localStorage.getItem(tokenKey);
        const hasTokens = !!tokenData;
        scDebug('isLoggedInSimple - tokenKey:', tokenKey, 'hasTokens:', hasTokens);
        return hasTokens;
    } catch (error) {
        scDebug('isLoggedInSimple error:', error);
        return false;
    }
}

async function updateLabel() {
    const isIn = await isLoggedInSimple();
    const sel = 'a[href="/dashboard"],a[href="/dashboard"]';
    const link = document.querySelector<HTMLAnchorElement>(`.navbar ${sel}, .navbar__items ${sel}`) || document.querySelector<HTMLAnchorElement>(sel);
    scDebug('updateLabel - isLoggedIn:', isIn, 'found link:', !!link, 'current text:', link?.textContent);
    if (link) {
        const newText = isIn ? 'Logout' : 'Login';
        if (link.textContent !== newText) {
            scDebug('updating link text from', link.textContent, 'to', newText);
            link.textContent = newText;
        }
        link.setAttribute('aria-label', newText);
    } else {
        scDebug('no navbar link found with selector:', sel);
    }
}

export default function () {
    if (typeof window === 'undefined') return;
    scDebug('navbarLoginLabel module initializing');

    // Initial sync
    requestAnimationFrame(() => {
        scDebug('initial updateLabel call');
        updateLabel().catch(() => undefined);
    });

    // Poll for auth changes (since we can't import the event system)
    const pollInterval = setInterval(() => {
        updateLabel().catch(() => undefined);
    }, 2000); // Check every 2 seconds

    // Also react to route/nav changes; Docusaurus may rerender navbar
    window.addEventListener('popstate', updateLabel);
    window.addEventListener('hashchange', updateLabel);
    document.addEventListener('click', (e) => {
        const t = e.target as HTMLElement | null;
        if (!t) return;
        const a = t.closest('a');
        if (a) setTimeout(() => { updateLabel().catch(() => undefined); }, 0);
    }, true);

    // Listen for storage changes (tokens added/removed)
    window.addEventListener('storage', (e) => {
        if (e.key?.includes('CognitoIdentityServiceProvider')) {
            scDebug('storage change detected for Cognito, updating label');
            updateLabel().catch(() => undefined);
        }
    });

    return () => {
        clearInterval(pollInterval);
    };
}
