export const AUTH_KEY = 'sc_logged_in';
const AUTH_EVENT = 'sc-auth-changed';

export function isLoggedIn(): boolean {
    if (typeof window === 'undefined') return false;
    try {
        return localStorage.getItem(AUTH_KEY) === '1';
    } catch {
        return false;
    }
}

export function setLoggedIn(value: boolean) {
    if (typeof window === 'undefined') return;
    try {
        if (value) localStorage.setItem(AUTH_KEY, '1');
        else localStorage.removeItem(AUTH_KEY);
        window.dispatchEvent(new CustomEvent(AUTH_EVENT, { detail: { value } }));
    } catch { }
}

export function onAuthChange(cb: (value: boolean) => void) {
    if (typeof window === 'undefined') return () => { };
    const handler = () => cb(isLoggedIn());
    const custom = (e: Event) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const d = (e as any).detail?.value as boolean | undefined;
        if (typeof d === 'boolean') cb(d);
        else handler();
    };
    window.addEventListener('storage', handler);
    window.addEventListener(AUTH_EVENT, custom as EventListener);
    return () => {
        window.removeEventListener('storage', handler);
        window.removeEventListener(AUTH_EVENT, custom as EventListener);
    };
}
