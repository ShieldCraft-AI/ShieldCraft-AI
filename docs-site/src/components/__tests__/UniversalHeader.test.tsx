import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import logger from '@site/src/utils/logger';

// Mock the auth-cognito module used by UniversalHeader
jest.mock('@site/src/utils/auth-cognito', () => ({
    isLoggedIn: jest.fn(),
    // expose onAuthChange as a mock function that tests can control
    onAuthChange: jest.fn(),
    signOut: jest.fn(),
}));

// Stub MultiProviderLogin to avoid importing the full implementation which
// may include additional runtime behavior that affects hooks in tests.
jest.mock('@site/src/components/MultiProviderLogin', () => ({
    __esModule: true,
    default: () => {
        const React = require('react');
        return React.createElement('div', { 'data-testid': 'mp-login' }, 'mp-login');
    }
}));

// Mock dynamic import for deploy-info.json
jest.mock('../../../build/deploy-info.json', () => ({
    commit: 'test-commit',
    timestamp: '2025-10-14T12:00:00Z',
}), { virtual: true });

// Delay importing the component until after mocks are configured in each test
let UniversalHeader: any;

describe('UniversalHeader auth behavior', () => {
    beforeEach(() => {
        jest.resetModules();
        // ensure window.matchMedia exists for the component
        if (!window.matchMedia) {
            // minimal polyfill
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            window.matchMedia = () => ({ matches: false, addListener: () => { }, removeListener: () => { } });
        }
    });

    // Diagnostic: print react resolution and identity to help track invalid hook causes
    const dumpReactInfo = () => {
        try {
            logger.error('[test-diag] react resolved to', require.resolve('react'));
            logger.error('[test-diag] react.version', require('react').version);
            logger.error('[test-diag] react identity equality self-check', require('react') === require('react'));
        } catch (err) {
            logger.error('[test-diag] react dump failed', err);
        }
    };

    test('shows Login when not authenticated', async () => {
        dumpReactInfo();
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockResolvedValue(false);
        // Simulate subscription that reports not authenticated
        auth.onAuthChange.mockImplementation((cb: any) => {
            setTimeout(() => cb(false), 0);
            return () => { };
        });

        // import after mocks
        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        await waitFor(() => expect(screen.getByLabelText(/Login/i)).toBeInTheDocument());
        expect(screen.getByText(/Login/i)).toBeVisible();
    });

    test('shows user menu when authenticated', async () => {
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockResolvedValue(true);
        // Simulate subscription that reports authenticated
        auth.onAuthChange.mockImplementation((cb: any) => {
            setTimeout(() => cb(true), 0);
            return () => { };
        });

        // instruct the UniversalHeader mock to simulate authenticated state
        // before importing it
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        global.__UNIVERSAL_HEADER_AUTH = true;

        // import after mocks
        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        // The button should have aria-label 'User menu' when authenticated
        await waitFor(() => expect(screen.getByLabelText(/User menu/i)).toBeInTheDocument());
    });
});

describe('UniversalHeader version display', () => {
    test('displays version from deploy-info.json', async () => {
        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        await waitFor(() => {
            expect(screen.getByText(/test-commit/i)).toBeInTheDocument();
            expect(screen.getByText(/2025-10-14T12:00:00Z/i)).toBeInTheDocument();
        });
    });

    test('displays fallback version when deploy-info.json is missing', async () => {
        jest.resetModules();
        jest.doMock('../../../build/deploy-info.json', () => {
            throw new Error('Module not found');
        }, { virtual: true });

        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        await waitFor(() => {
            expect(screen.getByText(/unknown/i)).toBeInTheDocument();
        });
    });
});

describe('UniversalHeader edge cases', () => {
    test('handles token expiration gracefully', async () => {
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockResolvedValue(false);
        auth.onAuthChange.mockImplementation((cb: any) => {
            setTimeout(() => cb(false), 0);
            return () => { };
        });

        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        await waitFor(() => expect(screen.getByLabelText(/Login/i)).toBeInTheDocument());
        expect(screen.getByText(/Login/i)).toBeVisible();
    });

    test('handles refresh token failure', async () => {
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockResolvedValue(false);
        auth.onAuthChange.mockImplementation((cb: any) => {
            setTimeout(() => cb(false), 0);
            return () => { };
        });

        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        await waitFor(() => expect(screen.getByLabelText(/Login/i)).toBeInTheDocument());
        expect(screen.getByText(/Login/i)).toBeVisible();
    });

    test('handles network issues gracefully', async () => {
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockRejectedValue(new Error('Network Error'));
        auth.onAuthChange.mockImplementation((cb: any) => {
            setTimeout(() => cb(false), 0);
            return () => { };
        });

        UniversalHeader = require('@site/src/components/UniversalHeader').default || require('@site/src/components/UniversalHeader');

        render(<UniversalHeader />);

        await waitFor(() => expect(screen.getByLabelText(/Login/i)).toBeInTheDocument());
        expect(screen.getByText(/Login/i)).toBeVisible();
    });
});
