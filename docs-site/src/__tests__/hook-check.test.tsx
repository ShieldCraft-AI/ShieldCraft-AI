import React from 'react';
import { render, screen } from '@testing-library/react';

function TestCounter() {
    const [n, setN] = React.useState(0);
    React.useEffect(() => setN(1), []);
    return React.createElement('div', null, `n=${n}`);
}

test('hooks basic sanity check', async () => {
    render(React.createElement(TestCounter));
    expect(await screen.findByText(/n=1/)).toBeTruthy();
});
