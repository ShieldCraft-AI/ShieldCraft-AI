/**
 * Ensure data-theme attribute is set on <html> element immediately.
 * This fixes light mode visibility issues where theme CSS selectors depend on html[data-theme='light'].
 */

function getDocusaurusTheme(): string {
    // Docusaurus stores theme in localStorage with key 'theme'
    // It stores the actual value as a JSON string like '"light"' or '"dark"'
    try {
        const stored = localStorage.getItem('theme');
        if (stored) {
            // Remove quotes if present (Docusaurus JSON stringifies the value)
            const parsed = stored.replace(/^"|"$/g, '');
            return parsed;
        }
    } catch (e) {
        // Ignore localStorage errors
    }

    // Fall back to system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
}

function ensureThemeAttribute() {
    const theme = getDocusaurusTheme();
    document.documentElement.setAttribute('data-theme', theme);
}

export function onRouteDidUpdate() {
    ensureThemeAttribute();
}

// Run immediately on module load (before React hydration)
if (typeof document !== 'undefined') {
    ensureThemeAttribute();

    // Also listen for storage changes (theme toggle in another tab)
    window.addEventListener('storage', (e) => {
        if (e.key === 'theme') {
            ensureThemeAttribute();
        }
    });
}
