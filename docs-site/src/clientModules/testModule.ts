// Simple test client module
export default function () {
    if (typeof window === 'undefined') return;

    // Test module loaded (no production logs)

    // Simple DOM manipulation
    setTimeout(() => {
        const loginLink = document.querySelector('a[href="/dashboard"]');
        if (loginLink) {
            // Found login link; annotate for test
            loginLink.setAttribute('data-test', 'client-module-works');
        }
    }, 1000);
}
