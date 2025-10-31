const React = require('react');

// Minimal Layout shim for tests. Renders children directly and accepts title/description props.
module.exports = function Layout({ children }) {
  return React.createElement('div', null, children);
};
