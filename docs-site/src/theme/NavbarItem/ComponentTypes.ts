// Extend the default NavbarItem component types with our custom item
import Original from '@theme-original/NavbarItem/ComponentTypes';
import LoginToggle from '@site/src/theme/NavbarItem/LoginToggle';

export default {
    ...Original,
    'custom-login-toggle': LoginToggle,
};
