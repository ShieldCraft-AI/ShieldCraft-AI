module.exports = {
  useLocation: () => ({ pathname: '/', search: '' }),
  useHistory: () => ({ push: () => {} }),
};
