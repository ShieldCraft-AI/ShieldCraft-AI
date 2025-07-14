<section>
<div>
  <a href="./checklist.md">⬅️ Back to Checklist</a>
</div>
</section>
<h1 align="center">🐳 Dockerfiles & Compose: Security, Reproducibility, Best Practices</h1>
<div>
  This document details the hardening and best practices applied to all Dockerfiles, Compose files, and related automation for ShieldCraft AI.
</div>

<section>
</section>

## 1. Hardened Dockerfiles

*   **Multiple Dockerfiles:**
    *   `Dockerfile` (base), `Dockerfile.api`, `Dockerfile.ingestion` for separation of concerns
    *   Each service has a minimal, purpose-built image for its function (API, ingestion, etc.)
*   **Distroless & Minimal Images:**
    *   All production images use Google Distroless or Alpine/slim variants for minimal attack surface
    *   No shell or package manager in final images
*   **Multi-Stage Builds:**
    *   Build dependencies and tools are only present in intermediate stages
    *   Final images contain only runtime and app code
*   **Security:**
    *   Non-root users enforced in all images
    *   Drop all Linux capabilities except those required
    *   Regular vulnerability scanning (Trivy, Snyk) in CI/CD
    *   No secrets or credentials in images; use environment variables and secrets management
*   **Reproducibility:**
    *   All base images and dependencies are pinned to specific versions
    *   `.dockerignore` excludes unnecessary files (tests, docs, local configs)
    *   Build args and environment variables for dev, staging, and prod
*   **Best Practices:**
    *   Healthchecks defined for all services (API, ingestion, etc.)
    *   Layer caching optimized for fast builds and CI/CD
    *   Image size minimized for fast deploys and reduced attack surface
    *   Labels and metadata for traceability

***

## 2. Docker Compose & Environments

*   **Three Environments:**
    *   `dev`: Local development with hot-reload, debug tools, and test data
    *   `staging`: Mirrors production, used for integration and pre-release testing
    *   `prod`: Hardened, minimal, and monitored for production workloads
*   **Service Isolation:**
    *   Separate services for API, ingestion, vector DB, etc.
    *   Network segmentation, explicit port mappings, and no unnecessary inter-service communication
*   **Security:**
    *   No privileged containers; drop all unnecessary Linux capabilities
    *   Environment variables and secrets managed via `.env` and external secrets store
    *   Volumes and mounts restricted to only what is needed
    *   Read-only root filesystem where possible
*   **Reproducibility:**
    *   Compose files versioned, peer-reviewed, and environment-specific overrides
    *   Consistent local and CI/CD builds
    *   Automated smoke tests after build/deploy

***

## 3. Nox & Automation

*   **Noxfile orchestrates:**
    *   Linting, testing, building, and running containers for all environments
    *   Automated checks for Dockerfile and Compose best practices
    *   Integration with pre-commit hooks and CI/CD pipelines
    *   Automated vulnerability scans and dependency updates

***

## 4. Continuous Improvement

*   **Regular reviews** of Dockerfiles and Compose for new vulnerabilities and optimizations
*   **Automated dependency updates** and security patching
*   **Documentation** for onboarding, troubleshooting, and environment setup
*   **Incident response:** Documented process for patching and rolling out new images in case of CVEs

<section>
  <em>Related: <a href="./modular_mlops_governance.md">Modular System & MLOps</a> | <a href="./project_structure.md">Project Structure</a> | <a href="./infra_estimate.md">Infrastructure Estimate</a></em>
</section>