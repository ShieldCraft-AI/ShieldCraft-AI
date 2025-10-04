import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

interface ServiceDependency {
    service: string;
    dependencies: string[];
}

interface DependencyGraphProps {
    data: any;
}

const ServiceDependencyGraph: React.FC<DependencyGraphProps> = ({ data }) => {
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const [dependencies, setDependencies] = useState<ServiceDependency[]>([]);

    useEffect(() => {
        if (!data?.service_matrix) return;

        try {
            // Extract dependencies from service matrix
            const deps: ServiceDependency[] = [];
            Object.entries(data.service_matrix).forEach(([serviceName, configs]: [string, any]) => {
                // Get dependencies from any environment (they should be consistent)
                const envConfig = configs?.dev || configs?.staging || configs?.prod;
                if (envConfig?.dependencies && Array.isArray(envConfig.dependencies) && envConfig.dependencies.length > 0) {
                    deps.push({
                        service: serviceName,
                        dependencies: envConfig.dependencies
                    });
                }
            });
            setDependencies(deps);
        } catch (error) {
            console.error('Error extracting service dependencies:', error);
            setDependencies([]);
        }
    }, [data]);

    // Create a simplified dependency map for visualization
    const getDependencyLevels = () => {
        const levels: { [level: number]: string[] } = {};
        const visited = new Set<string>();

        // Foundation services (no dependencies)
        levels[0] = dependencies
            .filter(dep => dep.dependencies.length === 0)
            .map(dep => dep.service);

        levels[0].forEach(service => visited.add(service));

        // Services that depend on foundation services
        levels[1] = dependencies
            .filter(dep =>
                dep.dependencies.length > 0 &&
                !visited.has(dep.service) &&
                dep.dependencies.every(d => visited.has(d))
            )
            .map(dep => dep.service);

        levels[1].forEach(service => visited.add(service));

        // Higher level services
        levels[2] = dependencies
            .filter(dep => !visited.has(dep.service))
            .map(dep => dep.service);

        return levels;
    };

    const dependencyLevels = getDependencyLevels();
    const allServices = Object.keys(data?.service_matrix || {});

    return (
        <div className={styles.dependencyGraph}>
            <h3>Service Dependency Map</h3>
            <p className={styles.description}>
                Click on a service to see its dependencies. Services are arranged by dependency level.
            </p>

            <div className={styles.graphContainer}>
                {/* Foundation Layer */}
                <div className={styles.dependencyLevel}>
                    <h4>Foundation Services</h4>
                    <div className={styles.serviceLevel}>
                        {(dependencyLevels[0] || []).map(service => (
                            <button
                                key={service}
                                className={`${styles.serviceNode} ${styles.foundation} ${selectedNode === service ? styles.selected : ''
                                    }`}
                                onClick={() => setSelectedNode(selectedNode === service ? null : service)}
                            >
                                {service.toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Dependent Services Layer 1 */}
                {dependencyLevels[1] && dependencyLevels[1].length > 0 && (
                    <div className={styles.dependencyLevel}>
                        <h4>Dependent Services</h4>
                        <div className={styles.serviceLevel}>
                            {dependencyLevels[1].map(service => (
                                <button
                                    key={service}
                                    className={`${styles.serviceNode} ${styles.dependent} ${selectedNode === service ? styles.selected : ''
                                        }`}
                                    onClick={() => setSelectedNode(selectedNode === service ? null : service)}
                                >
                                    {service.toUpperCase()}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Higher Level Services */}
                {dependencyLevels[2] && dependencyLevels[2].length > 0 && (
                    <div className={styles.dependencyLevel}>
                        <h4>Application Services</h4>
                        <div className={styles.serviceLevel}>
                            {dependencyLevels[2].map(service => (
                                <button
                                    key={service}
                                    className={`${styles.serviceNode} ${styles.application} ${selectedNode === service ? styles.selected : ''
                                        }`}
                                    onClick={() => setSelectedNode(selectedNode === service ? null : service)}
                                >
                                    {service.toUpperCase()}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Dependency Details */}
            {selectedNode && (
                <div className={styles.dependencyDetails}>
                    <h4>{selectedNode.toUpperCase()} Dependencies</h4>
                    {(() => {
                        const serviceDep = dependencies.find(d => d.service === selectedNode);
                        if (!serviceDep || serviceDep.dependencies.length === 0) {
                            return <p>This is a foundation service with no dependencies.</p>;
                        }
                        return (
                            <div className={styles.dependencyList}>
                                <p>This service depends on:</p>
                                <ul>
                                    {serviceDep.dependencies.map(dep => (
                                        <li key={dep}>
                                            <button
                                                className={styles.dependencyLink}
                                                onClick={() => setSelectedNode(dep)}
                                            >
                                                {dep.toUpperCase()}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        );
                    })()}
                </div>
            )}
        </div>
    );
};

export default ServiceDependencyGraph;
