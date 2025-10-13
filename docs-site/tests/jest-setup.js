// Test setup: stub browser APIs that plotly or other libs may use in jsdom
const { URL: NodeURL } = require('url');
// Ensure a proper URL constructor is available globally (do not replace with a plain object)
if (typeof global !== 'undefined' && !global.URL) {
  global.URL = NodeURL;
}
if (typeof window !== 'undefined') {
  if (!window.URL) {
    window.URL = NodeURL;
  }
  // If createObjectURL is missing, add it to the constructor, but don't overwrite the constructor itself
  if (!window.URL.createObjectURL) {
    try {
      window.URL.createObjectURL = () => 'blob:mock';
    } catch (e) {
      // some environments may not allow assigning to window.URL; silently ignore
    }
  }

  // Minimal canvas context stub (only if absent)
  if (typeof HTMLCanvasElement !== 'undefined' && !HTMLCanvasElement.prototype.getContext) {
    HTMLCanvasElement.prototype.getContext = function () {
      return {
        fillRect: () => {},
        clearRect: () => {},
        getImageData: (x, y, w, h) => ({ data: new Array(w * h * 4) }),
        putImageData: () => {},
        createImageData: () => [],
        setTransform: () => {},
        drawImage: () => {},
        save: () => {},
        fillText: () => {},
        measureText: () => ({ width: 0 }),
        transform: () => {},
        restore: () => {},
        beginPath: () => {},
        moveTo: () => {},
        lineTo: () => {},
        closePath: () => {},
        stroke: () => {},
      };
    };
  }

  // Stub ResizeObserver for tests that rely on it
  if (typeof global.ResizeObserver === 'undefined' && typeof window.ResizeObserver === 'undefined') {
    // Simple polyfill that calls callback immediately with zero entries
    class FakeResizeObserver {
      constructor(cb) {
        this._cb = cb;
      }
      observe() {
        // no-op
      }
      unobserve() {
        // no-op
      }
      disconnect() {
        // no-op
      }
    }
    global.ResizeObserver = FakeResizeObserver;
    window.ResizeObserver = FakeResizeObserver;
  }
}

// Debug: print resolved paths for react/react-dom so we can detect multiple copies
try {
  try {
    const reactResolved = require.resolve('react');
    const reactDomResolved = require.resolve('react-dom');
    // eslint-disable-next-line no-console
    console.error('[jest-setup] react resolved to', reactResolved);
    // eslint-disable-next-line no-console
    console.error('[jest-setup] react-dom resolved to', reactDomResolved);
  } catch (err) {
    // ignore
  }
} catch (e) {
  // ignore
}
