export type ChannelPricing = {
    gumroad?: number;
    githubMarketplace?: number;
    direct?: number;
};

export type FreeProduct = {
    id: string;
    slug: string;
    name: string;
    tier: 'free';
    priceUsd: number;
    description: string;
    upsellTo?: string;
    includedFeatures: string[];
    limitations: string[];
};

export type PaidProduct = {
    id: string;
    slug: string;
    name: string;
    tier: 'paid';
    priceUsd: number;
    description: string;
    includes: string[];
    marketplace: ChannelPricing;
    status?: 'future';
};

export type ProComponent = {
    id: string;
    slug: string;
    name: string;
    tier: 'pro';
    description: string;
    oneTimeUsd?: number;
    priceUsd?: number;
    subscriptionUsdMonth?: number;
    subscriptionUsdYear?: number;
};

export type GuardBoardTier = {
    id: string;
    slug: string;
    name: string;
    tier: 'paid' | 'pro' | 'enterprise';
    description: string;
    priceUsd?: number;
    marketplace?: ChannelPricing;
    subscriptionUsdMonth?: number;
    subscriptionUsdYear?: number;
    subscriptionUsdMonthPerUser?: number;
    slaHours?: number;
    features: string[];
};

export type Bundle = {
    id: string;
    slug: string;
    name: string;
    priceUsd?: number;
    subscriptionUsdMonth?: number;
    includes: string[];
    description: string;
};

export type GuardSuitePricing = {
    version: string;
    generatedAt: string;
    channels: {
        gumroadFeePercent: number;
        githubMarketplaceFeePercent: number;
        directDiscountPercent: number;
    };
    freeProducts: FreeProduct[];
    paidProducts: PaidProduct[];
    proComponents: ProComponent[];
    guardboard: GuardBoardTier[];
    bundles: Bundle[];
    internalNotes: {
        currency: string;
        pricingPhilosophy: string;
        futureSkus: string[];
    };
};

export const guardSuitePricing: GuardSuitePricing = {
    version: '1.0.0',
    generatedAt: '2025-11-19',
    channels: {
        gumroadFeePercent: 8.5,
        githubMarketplaceFeePercent: 20,
        directDiscountPercent: 0,
    },
    freeProducts: [
        {
            id: 'GS-VS-FREE',
            slug: 'vectorscan',
            name: 'VectorScan',
            tier: 'free',
            priceUsd: 0,
            description: 'Deterministic Terraform scanner for vector workloads.',
            upsellTo: 'vectorguard',
            includedFeatures: [
                'Canonical deterministic output',
                'Vector DB public endpoint detection',
                'Embedding storage encryption checks',
                'IAM wildcard scans',
            ],
            limitations: ['No FixPack', 'No compliance ledger', 'No GuardBoard export'],
        },
        {
            id: 'GS-CS-FREE',
            slug: 'computescan',
            name: 'ComputeScan',
            tier: 'free',
            priceUsd: 0,
            description: 'Compute waste and GPU configuration scanner.',
            upsellTo: 'computeguard',
            includedFeatures: [
                'GPU waste detection',
                'Idle compute checks',
                'Vector/AI pipeline compute mismatches',
            ],
            limitations: ['No FixPack', 'No ledger', 'Limited rule depth'],
        },
        {
            id: 'GS-PS-FREE',
            slug: 'pipelinescan',
            name: 'PipelineScan',
            tier: 'free',
            priceUsd: 0,
            description: 'Supply chain and CI/CD pipeline security scanner.',
            upsellTo: 'pipelineguard',
            includedFeatures: [
                'Basic OPA rules',
                'Detect missing signing enforcement',
                'Hard-coded secrets detection',
            ],
            limitations: ['No FixPack', 'No ledger', 'No remediation templates'],
        },
    ],
    paidProducts: [
        {
            id: 'GS-VG-079',
            slug: 'vectorguard',
            name: 'VectorGuard',
            tier: 'paid',
            priceUsd: 79,
            description: 'Advanced governance + FixPack-Lite for vector workloads.',
            includes: ['FixPack-Lite', 'Compliance ledger', 'GuardScore integration', 'Advanced ruleset', 'Unlimited local scans'],
            marketplace: {
                gumroad: 79,
                githubMarketplace: 99,
                direct: 79,
            },
        },
        {
            id: 'GS-CG-099',
            slug: 'computeguard',
            name: 'ComputeGuard',
            tier: 'paid',
            priceUsd: 99,
            description: 'Compute and GPU waste guardrail suite.',
            includes: ['FixPack-Lite', 'Drift ledger', 'GPU utilization heuristics', 'Cost governance rules', 'GuardScore integration'],
            marketplace: {
                gumroad: 99,
                githubMarketplace: 119,
                direct: 99,
            },
        },
        {
            id: 'GS-PG-089',
            slug: 'pipelineguard',
            name: 'PipelineGuard',
            tier: 'paid',
            priceUsd: 89,
            description: 'OPA rule pack + signing enforcement guardrails.',
            includes: ['FixPack-Lite', 'Compliance ledger', 'Signing templates', 'GuardScore integration'],
            marketplace: {
                gumroad: 89,
                githubMarketplace: 109,
                direct: 89,
            },
        },
        {
            id: 'GS-SG-089',
            slug: 'storageguard',
            name: 'StorageGuard',
            tier: 'paid',
            priceUsd: 89,
            status: 'future',
            description: 'Object storage governance (S3/GCS/MinIO).',
            includes: ['Encryption checks', 'Public bucket detection', 'FixPack-Lite', 'Audit ledger'],
            marketplace: {
                direct: 89,
            },
        },
        {
            id: 'GS-IG-109',
            slug: 'identityguard',
            name: 'IdentityGuard',
            tier: 'paid',
            priceUsd: 109,
            status: 'future',
            description: 'IAM hardening and drift detection.',
            includes: ['IAM risk scoring', 'Privilege escalation checks', 'FixPack-Lite', 'Compliance ledger'],
            marketplace: {
                direct: 109,
            },
        },
    ],
    proComponents: [
        {
            id: 'GS-FXP-149',
            slug: 'fixpack-pro',
            name: 'FixPack-Pro',
            tier: 'pro',
            oneTimeUsd: 149,
            subscriptionUsdMonth: 10,
            description: 'Advanced multi-step remediation engine.',
        },
        {
            id: 'GS-SCORE-129',
            slug: 'guardscore-engine',
            name: 'GuardScore Engine',
            tier: 'pro',
            oneTimeUsd: 129,
            subscriptionUsdMonth: 9,
            description: 'Deterministic security scoring engine.',
        },
        {
            id: 'GS-SCHEMA-FREE',
            slug: 'canonical-schema',
            name: 'Canonical Schema',
            tier: 'pro',
            priceUsd: 0,
            description: 'Public schema for GuardSuite ecosystem.',
        },
    ],
    guardboard: [
        {
            id: 'GS-BOARD-199',
            slug: 'guardboard',
            name: 'GuardBoard Base',
            tier: 'paid',
            priceUsd: 199,
            description: 'Local governance dashboard and report generator.',
            marketplace: {
                gumroad: 199,
                githubMarketplace: 249,
                direct: 199,
            },
            features: ['Compliance ledger viewer', 'FixPack viewer', 'Score trend explorer', 'PDF export'],
        },
        {
            id: 'GS-BOARD-PRO',
            slug: 'guardboard-pro',
            name: 'GuardBoard Pro',
            tier: 'pro',
            subscriptionUsdMonth: 19,
            subscriptionUsdYear: 189,
            description: 'Professional multi-project and team collaboration features.',
            features: ['Multi-project workspace', 'History & diffs', 'Team sharing', 'Project templates'],
        },
        {
            id: 'GS-BOARD-ENT',
            slug: 'guardboard-enterprise',
            name: 'GuardBoard Enterprise',
            tier: 'enterprise',
            subscriptionUsdMonthPerUser: 49,
            slaHours: 48,
            description: 'Enterprise dashboard with SSO, RBAC, report API.',
            features: ['RBAC', 'SSO', 'Analytics API', 'Multi-user compliance ledger', 'Extended history'],
        },
    ],
    bundles: [
        {
            id: 'GS-BUNDLE-FULL-249',
            slug: 'guardsuite-full',
            name: 'GuardSuite Full',
            priceUsd: 249,
            description: 'Core guardrails for security, FinOps, and pipeline readiness.',
            includes: ['vectorguard', 'computeguard', 'pipelineguard'],
        },
        {
            id: 'GS-BUNDLE-PRO-399',
            slug: 'guardsuite-pro',
            name: 'GuardSuite Pro Kit',
            priceUsd: 399,
            description: 'Adds remediation, scoring, and GuardBoard visualization.',
            includes: ['vectorguard', 'computeguard', 'pipelineguard', 'fixpack-pro', 'guardscore-engine', 'guardboard'],
        },
        {
            id: 'GS-BUNDLE-ENT',
            slug: 'guardsuite-enterprise',
            name: 'GuardSuite Enterprise Kit',
            subscriptionUsdMonth: 199,
            description: 'Subscription bundle with enterprise GuardBoard and every free scanner.',
            includes: ['guardboard-enterprise', 'fixpack-pro', 'guardscore-engine', 'vectorguard', 'computeguard', 'pipelineguard', 'all_free_products'],
        },
    ],
    internalNotes: {
        currency: 'USD',
        pricingPhilosophy: 'Simple, predictable one-time pricing; optional pro subscriptions; enterprise monthly.',
        futureSkus: ['CostGuard', 'KubeGuard', 'LLMGuard'],
    },
};

function findBySlug<T extends { slug: string }>(collection: T[], slug: string): T | undefined {
    return collection.find((item) => item.slug === slug);
}

export function getFreeProduct(slug: string): FreeProduct | undefined {
    return findBySlug(guardSuitePricing.freeProducts, slug);
}

export function getPaidProduct(slug: string, options: { includeFuture?: boolean } = {}): PaidProduct | undefined {
    const product = findBySlug(guardSuitePricing.paidProducts, slug);
    if (!product) return undefined;
    if (product.status === 'future' && !options.includeFuture) return undefined;
    return product;
}

export function getProComponent(slug: string): ProComponent | undefined {
    return findBySlug(guardSuitePricing.proComponents, slug);
}

export function getBundle(slug: string): Bundle | undefined {
    return findBySlug(guardSuitePricing.bundles, slug);
}

export function getGuardboardTier(slug: string): GuardBoardTier | undefined {
    return findBySlug(guardSuitePricing.guardboard, slug);
}
