module.exports = function forceSourcemap() {
  return {
    name: 'force-sourcemap',
    configureWebpack(config, isServer, utils) {
      // Only enable source maps in analysis runs; honor env var if present.
      if (process.env.FORCE_SOURCEMAP === 'true' || process.env.GENERATE_SOURCEMAP === 'true') {
        return {
          devtool: 'source-map',
        };
      }
      return {};
    },
  };
};
