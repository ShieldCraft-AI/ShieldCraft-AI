import React, { useRef, useState, useEffect } from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// This test imports the same docusaurus mocks via moduleNameMapper and
// uses the same hooks pattern as UniversalHeader to see if hooks work.
import { useColorMode } from '@docusaurus/theme-common';

function ReproComponent() {
    const { colorMode } = useColorMode();
    const headerRef = useRef<HTMLDivElement | null>(null);
    const [hydrated, setHydrated] = useState(false);

    useEffect(() => setHydrated(true), []);

    return (
        <div ref={headerRef} data-testid="repro">color:{String(colorMode)} hydrated:{String(hydrated)}</div>
    );
}

test('basic hook repro for docusaurus mocks', async () => {
    render(<ReproComponent />);
    expect(screen.getByTestId('repro')).toBeInTheDocument();
});
