import React, { useRef, useState, useEffect } from 'react';
import { render, screen } from '@testing-library/react';

test('react hooks smoke test', () => {
    function Smoke() {
        const r = useRef<HTMLDivElement | null>(null);
        const [count, setCount] = useState(0);
        useEffect(() => {
            if (r.current) r.current.setAttribute('data-mounted', 'true');
            setCount(1);
        }, []);
        return <div ref={r}>count:{count}</div>;
    }

    render(<Smoke />);
    const el = screen.getByText(/count:/i);
    expect(el).toBeTruthy();
    // should have updated attribute by effect
    expect(el.getAttribute('data-mounted')).toBe('true');
});
