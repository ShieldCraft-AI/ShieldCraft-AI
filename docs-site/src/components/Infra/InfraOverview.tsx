import React from 'react';
import styles from './infra.module.css';
import { envs, pipeline, EnvKey, serviceDescriptions } from '../../data/infraEnvs';
import { pasTemplates } from '../../data/pasTemplates';

const chipColor: Record<string, string> = {
    none: '#9997',
    external: '#a86fff',
    local: '#4caf50',
    inline: '#00acc1',
    managed: '#2196f3',
    ecs_scale_to_zero: '#ff9800',
    ecs_managed: '#f44336',
};

export default function InfraOverview() {
    const [env, setEnv] = React.useState<EnvKey>('dev');
    const summary = envs[env];

    return (
        <div className={styles.container}>
            <div className={styles.headerRow}>
                <div>
                    <h2 className={styles.h2}>ShieldCraft AI Infrastructure</h2>
                    <div className={styles.subtle}>Environment-aware view of core services and pipeline.</div>
                </div>
                <div className={styles.envSwitcher}>
                    {(['dev', 'staging', 'prod'] as EnvKey[]).map((e) => (
                        <button
                            key={e}
                            type="button"
                            className={e === env ? styles.envBtnActive : styles.envBtn}
                            onClick={() => setEnv(e)}
                        >
                            {envs[e].label}
                        </button>
                    ))}
                </div>
            </div>

            <section className={styles.grid}>
                <div className={styles.card}>
                    <div className={styles.cardHeader}>Environment</div>
                    <div className={styles.kv}>Account<span>{summary.account}</span></div>
                    <div className={styles.kv}>Region<span>{summary.region}</span></div>
                    {summary.vpcId && <div className={styles.kv}>VPC<span>{summary.vpcId}</span></div>}
                    <div className={styles.kv}>Subnets<span>{summary.subnets}</span></div>
                    <div className={styles.kvLong}>Buckets<div className={styles.bucketList}>{summary.buckets.map((b) => <code key={b}>{b}</code>)}</div></div>
                    <div className={styles.kv}>Step Functions<span>{summary.stepfunctionsType}</span></div>
                </div>

                <div className={styles.card}>
                    <div className={styles.cardHeader}>Service Modes</div>
                    <div className={styles.services}>
                        {Object.entries(summary.services).map(([svc, mode]) => (
                            <div key={svc} className={styles.serviceRow}>
                                <div className={styles.serviceName} data-tooltip={serviceDescriptions[svc as keyof typeof summary.services] || ''}>{svc}</div>
                                <span className={styles.chip} style={{ backgroundColor: chipColor[String(mode)] || '#666' }}>{mode}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className={styles.card}>
                    <div className={styles.cardHeader}>Dependencies</div>
                    <ul className={styles.list}>
                        <li>Networking → All domain stacks (VPC, SG, subnets)</li>
                        <li>IAM → Glue, Lambda, LakeFormation, OpenSearch, SageMaker</li>
                        <li>S3 → Glue (catalog + crawlers)</li>
                        <li>Glue + Lambda → DataQuality</li>
                        <li>MSK + Lambda + OpenSearch → CloudNativeHardening</li>
                    </ul>
                    <div className={styles.callout}>These mirror add_dependency calls in CDK to enforce ordering and cross-stack readiness.</div>
                </div>

                <div className={styles.card}>
                    <div className={styles.cardHeader}>CI/CD Pipeline</div>
                    <div className={styles.pipeline}>
                        {pipeline.map((stg, i) => (
                            <div key={stg.stage} className={styles.stage}>
                                <div className={styles.stageName}>{stg.stage.toUpperCase()}</div>
                                <div className={styles.stageInfo}>acct {stg.account} · {stg.region}</div>
                                {i < pipeline.length - 1 && <div className={styles.arrow} aria-hidden>→</div>}
                            </div>
                        ))}
                    </div>
                    <div className={styles.subtle}>Source: GitHub connection (CodePipeline) → CodeBuild synth → CDK deploy per stage.</div>
                </div>

                <div className={styles.card}>
                    <div className={styles.cardHeader}>Key Config</div>
                    <div className={styles.kv}>Glue DB<span>{summary.details.glue?.databaseName ?? '-'}</span></div>
                    <div className={styles.kv}>Glue Crawler<span>{summary.details.glue?.crawlerSchedule ?? '-'}</span></div>
                    <div className={styles.kv}>Lake Formation<span>{summary.details.lakeformation?.dataLakeLocation ?? '-'}</span></div>
                    <div className={styles.kv}>EventBridge (data)<span>{summary.details.eventbridge?.dataBus ?? '-'}</span></div>
                    <div className={styles.kv}>EventBridge (security)<span>{summary.details.eventbridge?.securityBus ?? '-'}</span></div>
                </div>

                <div className={styles.card}>
                    <div className={styles.cardHeader}>Proton PaS Templates</div>
                    <ul className={styles.listTight}>
                        {pasTemplates.map(t => (
                            <li key={t.id}>
                                <strong>{t.kind === 'environment' ? 'Env' : 'Svc'}:</strong> {t.name}
                                {t.domain ? <> · <em>{t.domain}</em></> : null}
                                <div className={styles.subtle}>{t.file}</div>
                            </li>
                        ))}
                    </ul>
                    <div className={styles.callout}>PaS will publish versioned templates to AWS Proton. Teams can self-serve pipelines and services wired to ShieldCraft guardrails.</div>
                </div>

                <div className={styles.card}>
                    <div className={styles.cardHeader}>Service Details</div>
                    <ul className={styles.listTight}>
                        <li><strong>MSK:</strong> {summary.details.msk?.mode} {summary.details.msk?.clusterName ? `· ${summary.details.msk?.clusterName}` : ''} {summary.details.msk?.brokerNodes ? `· ${summary.details.msk?.brokerNodes} brokers` : ''} {summary.details.msk?.instanceType ? `· ${summary.details.msk?.instanceType}` : ''}</li>
                        <li><strong>OpenSearch:</strong> {summary.details.opensearch?.mode} {summary.details.opensearch?.domainName ? `· ${summary.details.opensearch?.domainName}` : ''} {summary.details.opensearch?.instanceType ? `· ${summary.details.opensearch?.instanceType}` : ''} {summary.details.opensearch?.instanceCount ? `· x${summary.details.opensearch?.instanceCount}` : ''}</li>
                        <li><strong>Airbyte:</strong> {summary.details.airbyte?.mode} {summary.details.airbyte?.deploymentType ? `· ${summary.details.airbyte?.deploymentType}` : ''} {summary.details.airbyte?.minTasks !== undefined ? `· ${summary.details.airbyte?.minTasks}-${summary.details.airbyte?.maxTasks} tasks` : ''}</li>
                        <li><strong>DataQuality:</strong> {summary.details.data_quality?.mode} {summary.details.data_quality?.framework ? `· ${summary.details.data_quality?.framework}` : ''} {summary.details.data_quality?.schedule ? `· ${summary.details.data_quality?.schedule}` : ''}</li>
                        <li><strong>SageMaker:</strong> {summary.details.sagemaker?.mode} {summary.details.sagemaker?.trainingInstanceType ? `· train ${summary.details.sagemaker?.trainingInstanceType}` : ''} {summary.details.sagemaker?.inferenceInstanceType ? `· infer ${summary.details.sagemaker?.inferenceInstanceType}` : ''} {summary.details.sagemaker?.autoscaling ? '· autoscaling' : ''}</li>
                    </ul>
                </div>
            </section>
        </div>
    );
}
