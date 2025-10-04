import React from 'react';
import OriginalDefaultNavbarItem from '@theme-original/NavbarItem/DefaultNavbarItem';
import { isLoggedIn, onAuthChange, loginWithHostedUI, signOut } from '@site/src/utils/auth-cognito';

// Wrap the default navbar item to customize the Login/Logout label and behavior.
export default function DefaultNavbarItemWrapper(props: any) {
    const [loggedIn, setLI] = React.useState(false);

    React.useEffect(() => {
        (async () => {
            const authenticated = await isLoggedIn();
            setLI(authenticated);
        })();
        const off = onAuthChange((v) => setLI(v));
        return () => { off && off(); };
    }, []);

    const isLoginLink = (
        (props?.to && (props.to === '/dashboard' || props.to === '/dashboard')) ||
        (props?.href && (props.href === '/dashboard' || props.href === '/dashboard'))
    );

    const label = isLoginLink ? (loggedIn ? 'Logout' : 'Login') : props.label;

    const handleClick = async (e: React.MouseEvent) => {
        if (isLoginLink) {
            e.preventDefault();
            if (loggedIn) {
                // Logout
                await signOut();
                window.location.href = '/';
            } else {
                // Login via Cognito
                await loginWithHostedUI();
            }
        }
        if (typeof props.onClick === 'function') props.onClick(e);
    };

    return <OriginalDefaultNavbarItem {...props} label={label} onClick={handleClick} />;
}
