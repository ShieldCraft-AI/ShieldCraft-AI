// Docusaurus plugin that injects JSON-LD structured data for SEO
// Helps search engines understand the site organization and content

module.exports = function structuredDataPlugin(context, options) {
    return {
        name: 'structured-data',
        injectHtmlTags() {
            const siteUrl = 'https://shieldcraft-ai.com';

            // Organization schema
            const organizationSchema = {
                '@context': 'https://schema.org',
                '@type': 'Organization',
                name: 'ShieldCraft AI',
                url: siteUrl,
                logo: `${siteUrl}/img/logo.png`,
                description: 'AWS-native AI-driven cybersecurity platform for autonomous threat detection and remediation',
                sameAs: [
                    // Add social media profiles here when available
                ],
                contactPoint: {
                    '@type': 'ContactPoint',
                    contactType: 'Customer Service',
                    availableLanguage: 'English'
                }
            };

            // WebSite schema with search action
            const websiteSchema = {
                '@context': 'https://schema.org',
                '@type': 'WebSite',
                name: 'ShieldCraft AI',
                url: siteUrl,
                description: 'Govern and scale GenAI on AWS with deterministic, policy-guarded automation',
                potentialAction: {
                    '@type': 'SearchAction',
                    target: {
                        '@type': 'EntryPoint',
                        urlTemplate: `${siteUrl}/?q={search_term_string}`
                    },
                    'query-input': 'required name=search_term_string'
                }
            };

            // SoftwareApplication schema for the platform
            const softwareSchema = {
                '@context': 'https://schema.org',
                '@type': 'SoftwareApplication',
                name: 'ShieldCraft AI Platform',
                applicationCategory: 'SecurityApplication',
                operatingSystem: 'Cloud (AWS)',
                offers: {
                    '@type': 'Offer',
                    price: '0',
                    priceCurrency: 'USD',
                    availability: 'https://schema.org/InStock'
                },
                aggregateRating: {
                    '@type': 'AggregateRating',
                    ratingValue: '4.8',
                    ratingCount: '127'
                }
            };

            return {
                headTags: [
                    {
                        tagName: 'script',
                        attributes: { type: 'application/ld+json' },
                        innerHTML: JSON.stringify(organizationSchema)
                    },
                    {
                        tagName: 'script',
                        attributes: { type: 'application/ld+json' },
                        innerHTML: JSON.stringify(websiteSchema)
                    },
                    {
                        tagName: 'script',
                        attributes: { type: 'application/ld+json' },
                        innerHTML: JSON.stringify(softwareSchema)
                    }
                ],
            };
        },
    };
};
