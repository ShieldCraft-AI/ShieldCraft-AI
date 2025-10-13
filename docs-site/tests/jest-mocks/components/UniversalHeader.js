const React = require('react');

// Tests can set global.__UNIVERSAL_HEADER_AUTH to true to simulate an
// authenticated user. Default is unauthenticated.
module.exports = function UniversalHeaderMock() {
  const authenticated = Boolean(global.__UNIVERSAL_HEADER_AUTH);

  return React.createElement('header', { 'data-testid': 'universal-header-mock' },
    React.createElement('div', null, 'Mock Header'),
    React.createElement('button', { 'aria-label': authenticated ? 'User menu' : 'Login' }, authenticated ? 'User' : 'Login')
  );
};
