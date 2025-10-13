import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

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
            // eslint-disable-next-line no-console
            console.error('[test-diag] react resolved to', require.resolve('react'));
            // eslint-disable-next-line no-console
            console.error('[test-diag] react.version', require('react').version);
            // eslint-disable-next-line no-console
            console.error('[test-diag] react identity equality self-check', require('react') === require('react'));
        } catch (err) {
            // eslint-disable-next-line no-console
            console.error('[test-diag] react dump failed', err);
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
