import type * as Preset from '@docusaurus/preset-classic';
import type { Config } from '@docusaurus/types';
import webpack from 'webpack';
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

  // NOTE: `metadata` at the top-level is rejected by the current Docusaurus
  // config validation in this repo's Docusaurus version. To avoid build-time
  // validation errors, meta tags are injected via a small local plugin
  // (docs-site/plugins/og-meta) which adds the Open Graph / Twitter tags at
  // runtime. See that plugin for the exact tags.

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  organizationName: 'facebook',
  projectName: 'docusaurus',
  onBrokenLinks: 'warn',

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
    require.resolve('./src/clientModules/viewportDiagnostics.ts'),
    require.resolve('./src/clientModules/testModule.ts'),
  ],

  scripts: [
    {
      src: '/js/sc-oauth-capture.js',
      async: false,
    },
  ],

  themeConfig: {
    image: 'img/ShieldCraftAI.jpeg',
    navbar: {
      title: 'ShieldCraft AI',
      logo: {
        alt: 'ShieldCraft AI',
        src: 'img/logo.png',
      },
      items: [
        {
          to: '/analyst-dashboard',
          label: 'Analyst Dashboard',
          position: 'left',
          prefetch: false,
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          to: '/plugins',
          label: 'Plugins',
          position: 'left',
        },
        {
          to: '/pricing',
          label: 'Pricing',
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
  plugins: [
    require.resolve('./plugins/suppressWebpackVFileMessageWarnings'),
    // Provide webpack fallbacks via a local plugin that modifies the webpack config.
    require.resolve('./plugins/webpack-polyfills'),
    // Force production source maps for bundle analysis (local only).
    require.resolve('./plugins/force-sourcemap'),
    // Inject Open Graph / Twitter meta tags via a lightweight plugin so the
    // tags are present in the generated HTML without using the top-level
    // `metadata` field (which is rejected by the current config validator).
    require.resolve('./plugins/og-meta'),
  ],
};

export default config;
