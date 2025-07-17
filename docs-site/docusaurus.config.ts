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
            require.resolve('./static/css/shieldcraft-docs.css'),
            require.resolve('./static/css/shieldcraft-docs-dark.css'),
            require.resolve('./src/css/customTheme.css'),
          ],
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/shieldcraft-ai-preview.jpg',
    navbar: {
      title: 'ShieldCraft AI',
      logo: {
        alt: 'My Site Logo',
        src: 'img/logo.png',
      },
      items: [],
    },
    colorMode: {
      disableSwitch: true,
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
