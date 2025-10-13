const webpack = require('webpack');

module.exports = function () {
  return {
    name: 'webpack-polyfills',
    configureWebpack() {
      return {
        resolve: {
          // Workaround: some ESM contexts require fully-specified imports
          // like 'process/browser' which can fail to resolve without an alias.
          alias: {
            'process/browser': require.resolve('process/browser'),
          },
          fallback: {
            crypto: require.resolve('crypto-browserify'),
            process: require.resolve('process/browser'),
            stream: require.resolve('stream-browserify'),
            buffer: require.resolve('buffer/'),
            assert: require.resolve('assert/'),
            // Polyfill Node core 'vm' for libraries that use it (e.g. asn1.js)
            vm: require.resolve('vm-browserify'),
            util: require.resolve('util/'),
          },
        },
        plugins: [
          new webpack.ProvidePlugin({
            Buffer: ['buffer', 'Buffer'],
            process: 'process/browser',
          }),
        ],
      };
    },
  };
};
