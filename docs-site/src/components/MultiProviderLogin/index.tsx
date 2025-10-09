import React from 'react';
import {
    loginWithGoogle,
    loginWithAmazon,
    loginWithMicrosoft,
    loginWithGitHub,
    getAvailableProviders
} from '@site/src/utils/auth-cognito';

interface MultiProviderLoginProps {
    onLogin?: (provider: string) => void;
    showText?: boolean;
    vertical?: boolean;
    className?: string;
}

const providerConfig = {
    Google: {
        color: '#4285f4',
        textColor: 'white',
        icon: '🔍',
        handler: loginWithGoogle,
    },
    LoginWithAmazon: {
        color: '#ff9900',
        textColor: 'white',
        icon: '📦',
        handler: loginWithAmazon,
    },
    Microsoft: {
        color: '#00a1f1',
        textColor: 'white',
        icon: '🪟',
        handler: loginWithMicrosoft,
    },
    GitHub: {
        color: '#333',
        textColor: 'white',
        icon: '🐙',
        handler: loginWithGitHub,
    },
};

export default function MultiProviderLogin({
    onLogin,
    showText = true,
    vertical = false,
    className = ''
}: MultiProviderLoginProps) {
    const availableProviders = getAvailableProviders();

    const handleProviderLogin = async (providerId: string) => {
        try {
            const config = providerConfig[providerId];
            if (config) {
                await config.handler();
                onLogin?.(providerId);
            }
        } catch (error) {
            console.error(`Login with ${providerId} failed:`, error);
        }
    };

    const buttonStyle = (providerId: string) => {
        const config = providerConfig[providerId];
        return {
            backgroundColor: config?.color || '#333',
            color: config?.textColor || 'white',
            border: 'none',
            borderRadius: '6px',
            padding: showText ? '10px 16px' : '10px',
            margin: '4px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: showText ? '8px' : '0',
            fontSize: '14px',
            fontWeight: '500',
            transition: 'all 0.2s ease',
            minWidth: showText ? '120px' : '40px',
            justifyContent: 'center',
        };
    };

    const containerStyle: React.CSSProperties = {
        display: 'flex',
        flexDirection: vertical ? 'column' : 'row',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap',
    };

    return (
        <div className={className} style={containerStyle}>
            {availableProviders.map((provider) => (
                <button
                    key={provider.id}
                    style={buttonStyle(provider.id)}
                    onClick={() => handleProviderLogin(provider.id)}
                    onMouseOver={(e) => {
                        e.currentTarget.style.opacity = '0.9';
                        e.currentTarget.style.transform = 'translateY(-1px)';
                    }}
                    onMouseOut={(e) => {
                        e.currentTarget.style.opacity = '1';
                        e.currentTarget.style.transform = 'translateY(0)';
                    }}
                    title={`Sign in with ${provider.name}`}
                >
                    <span>{provider.icon}</span>
                    {showText && <span>Sign in with {provider.name}</span>}
                </button>
            ))}
        </div>
    );
}

// Compact version for navbar/header
export function CompactMultiProviderLogin() {
    return (
        <MultiProviderLogin
            showText={false}
            className="compact-provider-login"
        />
    );
}

// Full version for login pages
export function FullMultiProviderLogin() {
    return (
        <div style={{ textAlign: 'center', padding: '20px' }}>
            <h3 style={{ marginBottom: '20px' }}>Choose your sign-in method</h3>
            <MultiProviderLogin
                vertical={true}
                showText={true}
                className="full-provider-login"
            />
        </div>
    );
}
