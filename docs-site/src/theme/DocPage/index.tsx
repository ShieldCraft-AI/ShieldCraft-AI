import React, { useEffect } from 'react';
import type { ComponentProps } from 'react';
import OriginalDocPage from '@theme-original/DocPage';

type DocPageProps = ComponentProps<typeof OriginalDocPage>;

export default function DocPageWrapper(props: DocPageProps) {
    useEffect(() => {
        if (typeof document === 'undefined') {
            return () => undefined;
        }
        document.body.classList.add('aurora-surface');
        return () => {
            document.body.classList.remove('aurora-surface');
        };
    }, []);

    return <OriginalDocPage {...props} />;
}
