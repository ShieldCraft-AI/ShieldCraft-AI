import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';

// Mock the auth-cognito module used by UniversalHeader
jest.mock('@site/src/utils/auth-cognito', () => ({
    isLoggedIn: jest.fn(),
    onAuthChange: jest.fn((cb: any) => {
        // call immediately with false by default
        setTimeout(() => cb(false), 0);
        return () => { };
    }),
    signOut: jest.fn(),
}));

import UniversalHeader from '@site/src/components/UniversalHeader';

describe('UniversalHeader auth behavior', () => {
    beforeEach(() => {
        jest.resetModules();
        // ensure window.matchMedia exists for the component
        if (!window.matchMedia) {
            // minimal polyfill
            (window as any).matchMedia = () => ({ matches: false, addListener: () => { }, removeListener: () => { } });
        }
    });

    test('shows Login when not authenticated', async () => {
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockResolvedValue(false);

        render(<UniversalHeader />);

        await waitFor(() => expect(screen.getByLabelText(/Login/i)).toBeInTheDocument());
        expect(screen.getByText(/Login/i)).toBeVisible();
    });

    test('shows user menu when authenticated', async () => {
        const auth = require('@site/src/utils/auth-cognito');
        auth.isLoggedIn.mockResolvedValue(true);

        render(<UniversalHeader />);

        // The button should have aria-label 'User menu' when authenticated
        await waitFor(() => expect(screen.getByLabelText(/User menu/i)).toBeInTheDocument());
    });
});
