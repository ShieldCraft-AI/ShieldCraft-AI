import { useEffect } from 'react';

export default function AwsBadge() {
    useEffect(() => {
        if (!document.getElementById('credly-embed-script')) {
            const script = document.createElement('script');
            script.id = 'credly-embed-script';
            script.src = '//cdn.credly.com/assets/utilities/embed.js';
            script.async = true;
            document.body.appendChild(script);
        }
    }, []);

    return (
        <div style={{
            position: 'absolute',
            top: 24,
            right: 24,
            zIndex: 10
        }}>
            <div
                data-iframe-width="150"
                data-iframe-height="270"
                data-share-badge-id="aece6ebf-489a-454c-a66a-0c34412574ea"
                data-share-badge-host="https://www.credly.com"
            ></div>
        </div>
    );
}
