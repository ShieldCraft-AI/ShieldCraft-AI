import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Tests exercise the pricing page hover / pin behavior and sessionStorage
// persistence. The pricing page imports @theme/Layout (Docusaurus). We mock
// it to a simple passthrough component so tests can render the page cleanly.
jest.mock('@theme/Layout', () => ({
    __esModule: true,
    default: ({ children }: any) => React.createElement('div', null, children),
}));

describe('Pricing hover / pin behavior', () => {
    beforeEach(() => {
        jest.resetModules();
        // Clean sessionStorage between tests
        if (typeof window !== 'undefined' && window.sessionStorage) {
            window.sessionStorage.removeItem('pricing.pinnedService');
        }
    });

    test('hovering a service sets pinnedService in sessionStorage and shows in debug overlay', async () => {
        const PricingPage = require('@site/src/pages/pricing').default;
        render(React.createElement(PricingPage));

        // Find a visible service label that is present in the starter tier
        const svcText = /EventBridge/i; // displayServiceName('Amazon EventBridge') -> 'EventBridge'
        const svcNode = await screen.findByText(svcText);
        // Fire mouseEnter on the node (bubbles up to row)
        fireEvent.mouseEnter(svcNode);

        // sessionStorage should be populated with the full label (e.g. 'Amazon EventBridge')
        await waitFor(() => {
            const raw = window.sessionStorage.getItem('pricing.pinnedService');
            expect(raw).not.toBeNull();
            const parsed = JSON.parse(raw as string);
            expect(parsed.label).toMatch(/EventBridge/i);
            expect(parsed.tier).toBeDefined();
        });

        // The debug overlay should show the pinned JSON
        expect(screen.getByText(/PRICING DEBUG/i)).toBeInTheDocument();
        expect(screen.getByText(/pinned:/i)).toBeInTheDocument();
        expect(screen.getByText(/pinned:/i).textContent).toMatch(/EventBridge/);
    });

    test('click-to-pin persists across remount (sessionStorage restore)', async () => {
        const PricingPage = require('@site/src/pages/pricing').default;
        render(React.createElement(PricingPage));

        // Click a service (use SageMaker as another example)
        const svcNode = await screen.findByText(/SageMaker/i);
        fireEvent.click(svcNode);

        // Click handler should set sessionStorage
        await waitFor(() => {
            const raw = window.sessionStorage.getItem('pricing.pinnedService');
            expect(raw).not.toBeNull();
            const parsed = JSON.parse(raw as string);
            expect(parsed.label).toMatch(/SageMaker/i);
        });

        // Remount the component to simulate navigation / reload in same tab
        jest.resetModules();
        const PricingPage2 = require('@site/src/pages/pricing').default;
        render(React.createElement(PricingPage2));

        // After mount the overlay should show pinned persisted value
        await waitFor(() => expect(screen.getByText(/pinned:/i).textContent).toMatch(/SageMaker/));
    });

    test('mouse leave does not permanently clear hovered state (debounced restore)', async () => {
        jest.useFakeTimers();
        const PricingPage = require('@site/src/pages/pricing').default;
        render(React.createElement(PricingPage));

        const svcNode = await screen.findByText(/EventBridge/i);
        // Hover
        fireEvent.mouseEnter(svcNode);

        // Immediately leave
        fireEvent.mouseLeave(svcNode);

        // Because the implementation debounces restore by ~80ms, advance timers
        jest.advanceTimersByTime(100);

        // After the debounce runs, the hoveredService should still be visible in the overlay last/hovered text
        await waitFor(() => {
            const hoveredText = screen.getByText(/hovered:/i).textContent || '';
            expect(hoveredText).toMatch(/EventBridge/);
        });

        jest.useRealTimers();
    });

    test('Clear button removes pinnedService and updates overlay', async () => {
        const PricingPage = require('@site/src/pages/pricing').default;
        render(React.createElement(PricingPage));

        const svcNode = await screen.findByText(/EventBridge/i);
        fireEvent.mouseEnter(svcNode);

        await waitFor(() => expect(window.sessionStorage.getItem('pricing.pinnedService')).not.toBeNull());

        // Click the Clear button in the debug overlay
        const clearBtn = screen.getByRole('button', { name: /Clear/i });
        fireEvent.click(clearBtn);

        await waitFor(() => expect(window.sessionStorage.getItem('pricing.pinnedService')).toBeNull());
        expect(screen.getByText(/pinned:/i).textContent).toMatch(/null/);
    });

    test('initial mount restores pinnedService from sessionStorage', async () => {
        // Pre-populate sessionStorage before module load to simulate a persisted choice
        window.sessionStorage.setItem('pricing.pinnedService', JSON.stringify({ label: 'Amazon EventBridge', tier: 'starter' }));
        jest.resetModules();
        const PricingPage = require('@site/src/pages/pricing').default;
        render(React.createElement(PricingPage));

        // The overlay should show the pinned value shortly after mount
        await waitFor(() => expect(screen.getByText(/pinned:/i).textContent).toMatch(/EventBridge/));
        // hovered should also reflect the pinned selection on mount
        expect(screen.getByText(/hovered:/i).textContent).toMatch(/EventBridge/);
    });
});
