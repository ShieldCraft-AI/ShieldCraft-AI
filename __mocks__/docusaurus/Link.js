module.exports = function Link(props) {
  const { children } = props;
  // simple passthrough for tests
  return children || null;
};
