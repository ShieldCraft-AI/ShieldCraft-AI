const React = require('react');

// Minimal Link shim used in tests. Renders an anchor element.
module.exports = function Link(props) {
  const { to, children, ...rest } = props || {};
  return React.createElement('a', { href: to || rest.href || '#', ...rest }, children);
};
