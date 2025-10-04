export function onRouteDidUpdate() {
    try {
        const html = document.documentElement;
        const body = document.body;
        html.classList.remove('navbar-sidebar--show');
        body.classList.remove('navbar-sidebar--show');
        const backdrop = document.querySelector<HTMLElement>('.navbar-sidebar__backdrop');
        if (backdrop) {
            backdrop.style.display = 'none';
            backdrop.style.visibility = 'hidden';
        }
    } catch {
        // no-op
    }
}
