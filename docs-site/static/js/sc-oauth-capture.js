(function () {
    try {
        if (typeof window === 'undefined' || typeof sessionStorage === 'undefined') {
            return;
        }
        var search = window.location.search || '';
        var hash = window.location.hash || '';
        if ((search.indexOf('code=') !== -1 && search.indexOf('state=') !== -1) || (hash.indexOf('code=') !== -1 && hash.indexOf('state=') !== -1)) {
            try {
                sessionStorage.setItem('__sc_oauth_search', search);
                sessionStorage.setItem('__sc_oauth_hash', hash);
                sessionStorage.setItem('__sc_oauth_href', window.location.href);
            } catch (err) {
                /* ignore storage errors */
            }
        }
    } catch (err) {
        /* ignore */
    }
})();
