// This plugin suppresses webpack warnings about non-serializable VFileMessage cache items
// See: https://github.com/facebook/docusaurus/issues/7492

import type {Plugin} from '@docusaurus/types';

const suppressWebpackVFileMessageWarnings: Plugin = () => ({
  name: 'suppress-webpack-vfilemessage-warnings',
  configureWebpack() {
    return {
      infrastructureLogging: {
        level: 'warn' as const,
      },
      stats: {
        warningsFilter: [
          /No serializer registered for VFileMessage/,
          /webpack\.cache\.PackFileCacheStrategy/,
        ],
      },
    };
  },
});

export default suppressWebpackVFileMessageWarnings;
