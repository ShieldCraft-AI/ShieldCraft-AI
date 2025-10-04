export type Env = 'dev' | 'staging' | 'prod';

export type ProofKind = 'code' | 'diagram' | 'test' | 'runbook';

export interface ProofLink {
    label: string;
    href: string;
    kind: ProofKind;
}

export type ViewTag = 'data-plane' | 'guardrails' | 'actions' | 'observability';

export interface ServiceRef {
    name: string;
    description?: string;
    awsLink?: string;
    opsNotes?: string;
}

export interface Capability {
    id: string; // must match SVG id when using ID-based hotspots
    title: string;
    summary?: string;
    viewTags: ViewTag[];
    recommendedByEnv: Record<Env, ServiceRef>;
    alternatives?: Array<{ service: string; whenToChoose: string }>;
    finops?: { costTier: 'low' | 'med' | 'high'; notes?: string };
    tradeoffs?: string[];
    failureModes?: string[];
    proofLinks: ProofLink[];
}
