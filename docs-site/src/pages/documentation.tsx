import React from 'react';
import { useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

export default function DocumentationPage() {
    const history = useHistory();

    useEffect(() => {
        // Redirect to intro page immediately
        history.replace('/intro');
    }, [history]);

    return null;
}
