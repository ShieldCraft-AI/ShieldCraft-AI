exports.useLocation = function useLocation() {
  return { pathname: '/', search: '', hash: '' };
};
exports.useHistory = function useHistory() {
  return { push: () => {}, replace: () => {} };
};
exports.Redirect = function Redirect() {
  return null;
};
