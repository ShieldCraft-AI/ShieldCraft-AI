import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

import MultiProviderLogin, { CompactMultiProviderLogin, FullMultiProviderLogin } from '../index';
import * as auth from '../../../utils/auth-cognito';

jest.mock('../../../utils/auth-cognito', () => ({
    __esModule: true,
    getAvailableProviders: jest.fn(),
    loginWithGoogle: jest.fn(),
    loginWithAmazon: jest.fn(),
    loginWithProvider: jest.fn(),
}));

const getAvailableProvidersMock = auth.getAvailableProviders as jest.Mock;
const loginWithGoogleMock = auth.loginWithGoogle as jest.Mock;
const loginWithAmazonMock = auth.loginWithAmazon as jest.Mock;
const loginWithProviderMock = auth.loginWithProvider as jest.Mock;

describe('MultiProviderLogin', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders a fallback message when providers are missing', () => {
        getAvailableProvidersMock.mockReturnValueOnce([]);

        render(<MultiProviderLogin />);

        expect(screen.getByText(/sign-in options are loading/i)).toBeInTheDocument();
        expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });

    it('filters invalid provider entries before rendering', () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'Google', name: 'Google' },
            { id: '', name: 'MissingId' } as any,
            null as any,
        ]);

        render(<MultiProviderLogin />);

        expect(screen.getByRole('button', { name: /sign in with google/i })).toBeInTheDocument();
        expect(screen.queryByText('MissingId')).not.toBeInTheDocument();
    });

    it('invokes the correct handler when a provider is clicked', async () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'Google', name: 'Google' },
        ]);
        loginWithGoogleMock.mockResolvedValueOnce(undefined);

        const onLogin = jest.fn();
        render(<MultiProviderLogin onLogin={onLogin} />);

        const googleButton = screen.getByRole('button', { name: /sign in with google/i });
        await userEvent.click(googleButton);

        expect(loginWithGoogleMock).toHaveBeenCalledTimes(1);
        expect(onLogin).toHaveBeenCalledWith('Google');
    });

    it('still renders Amazon handler wiring when available', () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'LoginWithAmazon', name: 'Amazon' },
        ]);
        loginWithAmazonMock.mockResolvedValueOnce(undefined);

        render(<MultiProviderLogin />);

        const amazonButton = screen.getByRole('button', { name: /sign in with amazon/i });
        userEvent.click(amazonButton);

        expect(loginWithAmazonMock).toHaveBeenCalledTimes(1);
    });

    it('falls back to generic handler for unknown providers without crashing', async () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'Contoso', name: 'Contoso IDP' },
        ]);
        loginWithProviderMock.mockResolvedValueOnce(undefined);

        const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => undefined);

        render(<MultiProviderLogin />);

        const contosoButton = screen.getByRole('button', { name: /sign in with contoso idp/i });
        await userEvent.click(contosoButton);

        // click should be graceful even though config is missing
        expect(consoleWarnSpy).toHaveBeenCalledWith('Unknown provider:', 'Contoso');
        expect(loginWithProviderMock).not.toHaveBeenCalled();

        consoleWarnSpy.mockRestore();
    });

    it('supports keyboard activation via Enter key', async () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'Google', name: 'Google' },
        ]);
        loginWithGoogleMock.mockResolvedValueOnce(undefined);

        render(<MultiProviderLogin />);

        const googleButton = screen.getByRole('button', { name: /sign in with google/i });
        await userEvent.type(googleButton, '{enter}');

        expect(loginWithGoogleMock).toHaveBeenCalledTimes(1);
    });

    it('renders compact variant without descriptive text', () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'Google', name: 'Google' },
        ]);

        render(<CompactMultiProviderLogin />);

        expect(screen.getByRole('button', { name: /sign in with google/i })).toBeInTheDocument();
        expect(screen.queryByText(/sign in with google/i, { selector: 'div.provider-sub' })).not.toBeInTheDocument();
    });

    it('renders full variant with heading and descriptive text', () => {
        getAvailableProvidersMock.mockReturnValueOnce([
            { id: 'LoginWithAmazon', name: 'Amazon' },
        ]);

        render(<FullMultiProviderLogin />);

        expect(screen.getByRole('heading', { level: 3, name: /choose your sign-in method/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /sign in with amazon/i })).toBeInTheDocument();
    });
});
