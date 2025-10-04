import type * as Preset from '@docusaurus/preset-classic';
import type { Config } from '@docusaurus/types';
import { themes as prismThemes } from 'prism-react-renderer';

const config: Config = {
  title: 'ShieldCraft AI',
  tagline: '',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://shieldcraft-ai.com',
  baseUrl: '/',

  organizationName: 'facebook',
  projectName: 'docusaurus',
  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'docs/site',
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl: undefined,
        },
        theme: {
          customCss: [
            require.resolve('./src/css/custom.css'),
            require.resolve('./src/css/docs-theme.css'),
            require.resolve('./static/css/shieldcraft-docs.css'),
            require.resolve('./static/css/shieldcraft-docs-dark.css'),
            require.resolve('./src/css/customTheme.css'),
            require.resolve('./src/css/design-tokens.css'),
            require.resolve('./src/css/utilities.css'),
            require.resolve('./src/css/architecture-fullwidth.css'),
            require.resolve('./src/css/scroll-fix.css'),
          ],
        },
      } satisfies Preset.Options,
    ],
  ],

  clientModules: [
    require.resolve('./src/clientModules/scrollRestoration.ts'),
    require.resolve('./src/clientModules/loginLinkInterceptor.ts'),
    require.resolve('./src/clientModules/navbarLoginLabel.ts'),
    require.resolve('./src/clientModules/closeNavOnRoute.ts'),
    require.resolve('./src/clientModules/prefetchDashboard.ts'),
    require.resolve('./src/clientModules/viewportDiagnostics.ts'),
  ],

  themeConfig: {
    image: 'img/shieldcraft-ai-preview.jpg',
    navbar: {
      title: 'ShieldCraft AI',
      logo: {
        alt: 'ShieldCraft AI',
        src: 'img/logo.png',
      },
      items: [
        {
          to: '/architecture',
          label: '🛡️ Architecture',
          position: 'left',
        },
        { type: 'custom-login-toggle', position: 'right' },
      ],
    },
    colorMode: {
      disableSwitch: false,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    themes: [
      '@docusaurus/theme-mermaid',
    ]
  } satisfies Preset.ThemeConfig,
  plugins: [require.resolve('./plugins/suppressWebpackVFileMessageWarnings')],
};

export default config;
