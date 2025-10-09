import React from 'react';
import { Redirect } from '@docusaurus/router';

export default function LegacyArchitectureRedirect(): React.JSX.Element {
    return <Redirect to="/pricing" />;
}
