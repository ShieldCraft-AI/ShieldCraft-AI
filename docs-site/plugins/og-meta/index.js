// Lightweight Docusaurus plugin that injects Open Graph and Twitter meta tags
// into the <head>. This avoids using a top-level `metadata` field which some
// versions of Docusaurus validate against and reject.

module.exports = function ogMetaPlugin(context, options) {
  return {
    name: 'og-meta',
    injectHtmlTags() {
      const absoluteImage = 'https://shieldcraft-ai.com/img/ShieldCraftAI.jpeg';
      const ogTitle = 'ShieldCraft AI  -  Secure, Governed GenAI at Enterprise Scale';
      const shortDescription = 'Production-grade AWS reference architecture that automates governance and FinOps guardrails across the MLOps lifecycle.';
      return {
        headTags: [
          { tagName: 'meta', attributes: { name: 'twitter:card', content: 'summary_large_image' } },
          { tagName: 'meta', attributes: { name: 'twitter:title', content: ogTitle } },
          { tagName: 'meta', attributes: { name: 'twitter:description', content: shortDescription } },
          { tagName: 'meta', attributes: { name: 'twitter:image', content: absoluteImage } },

          { tagName: 'meta', attributes: { property: 'og:title', content: ogTitle } },
          { tagName: 'meta', attributes: { property: 'og:description', content: shortDescription } },
          { tagName: 'meta', attributes: { property: 'og:image', content: absoluteImage } },
          { tagName: 'meta', attributes: { property: 'og:image:width', content: '1200' } },
          { tagName: 'meta', attributes: { property: 'og:image:height', content: '627' } },
          { tagName: 'meta', attributes: { property: 'og:type', content: 'website' } },
          { tagName: 'meta', attributes: { property: 'og:site_name', content: 'ShieldCraft AI' } },
          { tagName: 'meta', attributes: { property: 'og:url', content: 'https://shieldcraft-ai.com' } },
          { tagName: 'meta', attributes: { property: 'og:locale', content: 'en_US' } },
        ],
      };
    },
  };
};
