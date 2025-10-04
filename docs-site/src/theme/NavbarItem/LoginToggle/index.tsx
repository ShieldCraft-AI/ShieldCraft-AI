import React from 'react';
import { useHistory } from '@docusaurus/router';
import { isLoggedIn, onAuthChange, loginWithHostedUI, signOut } from '@site/src/utils/auth-cognito';
import { preloadPlotly } from '@site/src/utils/plotlyPreload';

export default function LoginToggleNavbarItem() {
    const history = useHistory();
    const [loggedIn, setLI] = React.useState(false);

    React.useEffect(() => {
        // Subscribe to auth changes - will immediately fire with current state
        const unsubscribe = onAuthChange((isAuth) => {
            console.log('LoginToggle - auth state changed:', isAuth);
            setLI(isAuth);
        });

        // Warm the Plotly chunk so Dashboard charts render instantly
        preloadPlotly();

        return () => {
            unsubscribe();
        };
    }, []);

    const label = loggedIn ? 'Logout' : 'Login';

    const onClick = async (e: React.MouseEvent) => {
        if (loggedIn) {
            e.preventDefault();
            await signOut();
            setLI(false);
            // Delay navigation a tick so subscribers unmount charts before route change
            setTimeout(() => history.push('/'), 0);
            return;
        }
        // Not logged in: redirect to Cognito
        e.preventDefault();
        preloadPlotly();
        await loginWithHostedUI();
    };

    const onMouseEnter = () => { preloadPlotly(); };

    return (
        <a
            href={loggedIn ? '#' : '/dashboard'}
            className="navbar__item navbar__link"
            onClick={onClick}
            aria-label={label}
            onMouseEnter={onMouseEnter}
        >
            {label}
        </a>
    );
}
