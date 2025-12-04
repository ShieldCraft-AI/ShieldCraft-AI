// Lightweight Docusaurus plugin that injects Open Graph and Twitter meta tags
// into the <head>. This avoids using a top-level `metadata` field which some
// versions of Docusaurus validate against and reject.

module.exports = function ogMetaPlugin(context, options) {
  return {
    name: 'og-meta',
    injectHtmlTags() {
      const absoluteImage = 'https://shieldcraft-ai.com/img/ShieldCraftAI.jpeg';
      const ogTitle = 'ShieldCraft AI - Autonomous Security on AWS';
      const shortDescription = 'AWS-native autonomous threat detection and remediation. GenAI-powered security that detects, analyzes, and neutralizes threats in seconds-fully auditable.';
      return {
        headTags: [
          // Twitter Card tags
          { tagName: 'meta', attributes: { name: 'twitter:card', content: 'summary_large_image' } },
          { tagName: 'meta', attributes: { name: 'twitter:title', content: ogTitle } },
          { tagName: 'meta', attributes: { name: 'twitter:description', content: shortDescription } },
          { tagName: 'meta', attributes: { name: 'twitter:image', content: absoluteImage } },
          { tagName: 'meta', attributes: { name: 'twitter:image:alt', content: 'ShieldCraft AI Platform Dashboard' } },
          { tagName: 'meta', attributes: { name: 'twitter:creator', content: '@ShieldCraftAI' } },
          { tagName: 'meta', attributes: { name: 'twitter:site', content: '@ShieldCraftAI' } },

          // Open Graph tags
          { tagName: 'meta', attributes: { property: 'og:title', content: ogTitle } },
          { tagName: 'meta', attributes: { property: 'og:description', content: shortDescription } },
          { tagName: 'meta', attributes: { property: 'og:image', content: absoluteImage } },
          { tagName: 'meta', attributes: { property: 'og:image:alt', content: 'ShieldCraft AI Platform Dashboard' } },
          { tagName: 'meta', attributes: { property: 'og:image:width', content: '1200' } },
          { tagName: 'meta', attributes: { property: 'og:image:height', content: '627' } },
          { tagName: 'meta', attributes: { property: 'og:type', content: 'website' } },
          { tagName: 'meta', attributes: { property: 'og:site_name', content: 'ShieldCraft AI' } },
          { tagName: 'meta', attributes: { property: 'og:url', content: 'https://shieldcraft-ai.com' } },
          { tagName: 'meta', attributes: { property: 'og:locale', content: 'en_US' } },

          // Canonical URL
          { tagName: 'link', attributes: { rel: 'canonical', href: 'https://shieldcraft-ai.com/' } },

          // Additional SEO meta tags
          { tagName: 'meta', attributes: { name: 'keywords', content: 'AWS security, autonomous threat detection, GenAI security, cloud security automation, AWS GuardDuty integration, security orchestration, SOAR, threat remediation, MLOps security, FinOps, compliance automation, AWS native security' } },
          { tagName: 'meta', attributes: { name: 'author', content: 'ShieldCraft AI' } },
          { tagName: 'meta', attributes: { name: 'robots', content: 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1' } },
          { tagName: 'meta', attributes: { name: 'theme-color', content: '#8f7bff' } },
          { tagName: 'meta', attributes: { name: 'apple-mobile-web-app-capable', content: 'yes' } },
          { tagName: 'meta', attributes: { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' } },

          // Performance: DNS prefetch and preconnect for external resources
          { tagName: 'link', attributes: { rel: 'dns-prefetch', href: '//fonts.googleapis.com' } },
          { tagName: 'link', attributes: { rel: 'preconnect', href: 'https://fonts.googleapis.com', crossorigin: 'anonymous' } },
        ],
      };
    },
  };
};
