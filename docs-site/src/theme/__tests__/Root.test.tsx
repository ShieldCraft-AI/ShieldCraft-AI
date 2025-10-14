import React from 'react';
import { render, waitFor, act } from '@testing-library/react';
import Root from '../Root';

let mockLocation: { pathname: string; search: string; hash: string } = { pathname: '/', search: '', hash: '' };

jest.mock('@docusaurus/router', () => ({
    useLocation: () => mockLocation,
    useHistory: () => ({ push: jest.fn() }),
}));

jest.mock('@site/src/utils/auth-cognito', () => ({
    initAuth: jest.fn(),
    onAuthChange: jest.fn(() => jest.fn()),
    isLoggedIn: jest.fn(),
    notifyAuthChange: jest.fn(),
    refreshAuthState: jest.fn(),
}));

type AuthModule = typeof import('@site/src/utils/auth-cognito');
const authMocks = jest.requireMock('@site/src/utils/auth-cognito') as jest.Mocked<AuthModule>;

const mockInitAuth = authMocks.initAuth;
const mockOnAuthChange = authMocks.onAuthChange;
const mockIsLoggedIn = authMocks.isLoggedIn;
const mockNotifyAuthChange = authMocks.notifyAuthChange;
const mockRefreshAuthState = authMocks.refreshAuthState;

describe('Root OAuth handling', () => {
    beforeEach(() => {
        jest.resetAllMocks();
        mockLocation = { pathname: '/', search: '', hash: '' };
        mockOnAuthChange.mockReturnValue(jest.fn());
        mockIsLoggedIn.mockResolvedValue(false);
        window.history.replaceState({}, '', '/');
    });

    afterEach(() => {
        jest.useRealTimers();
        jest.restoreAllMocks();
    });

    it('invokes refreshAuthState when OAuth parameters are present', async () => {
        mockLocation = { pathname: '/', search: '?code=abc&state=xyz', hash: '' };
        mockRefreshAuthState.mockResolvedValue(true);
        window.history.replaceState({}, '', `${mockLocation.pathname}${mockLocation.search}`);
        const replaceSpy = jest.spyOn(window.history, 'replaceState');

        render(<Root><div>content</div></Root>);

        await waitFor(() => expect(mockInitAuth).toHaveBeenCalledTimes(1));
        await waitFor(() => expect(mockRefreshAuthState).toHaveBeenCalledTimes(1));
        expect(mockIsLoggedIn).not.toHaveBeenCalled();
        expect(mockNotifyAuthChange).not.toHaveBeenCalled();
        expect(replaceSpy).toHaveBeenCalledTimes(1);
        replaceSpy.mockRestore();
    });

    it('falls back to polling when refreshAuthState does not resolve authentication', async () => {
        jest.useFakeTimers();
        mockLocation = { pathname: '/', search: '?code=abc&state=xyz', hash: '' };
        mockRefreshAuthState.mockResolvedValue(false);
        window.history.replaceState({}, '', `${mockLocation.pathname}${mockLocation.search}`);
        mockIsLoggedIn
            .mockResolvedValueOnce(false)
            .mockResolvedValueOnce(true);
        const replaceSpy = jest.spyOn(window.history, 'replaceState');

        render(<Root><div>content</div></Root>);

        await waitFor(() => expect(mockInitAuth).toHaveBeenCalledTimes(1));
        await waitFor(() => expect(mockRefreshAuthState).toHaveBeenCalledTimes(1));
        expect(mockIsLoggedIn).not.toHaveBeenCalled();

        await act(async () => {
            jest.advanceTimersByTime(500);
            await Promise.resolve();
        });
        expect(mockIsLoggedIn).toHaveBeenCalledTimes(1);

        await act(async () => {
            jest.advanceTimersByTime(500);
            await Promise.resolve();
        });
        expect(mockIsLoggedIn).toHaveBeenCalledTimes(2);
        await waitFor(() => expect(mockNotifyAuthChange).toHaveBeenCalledTimes(1));
        expect(replaceSpy).toHaveBeenCalledTimes(1);
        replaceSpy.mockRestore();
    });
});
