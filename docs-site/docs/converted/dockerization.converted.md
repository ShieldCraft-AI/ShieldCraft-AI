# 🐳 ShieldCraft AI Dockerization

Secure, Reproducible, and Production-Ready Container Builds

## 🔎Overview

ShieldCraft AI uses a modern, multi-stage Docker build process for all core services ( main , api , ingestion ), leveraging Chainguard Python images for minimal attack surface and zero-known CVEs. This ensures secure, reproducible, and environment-specific containers for development, staging, and production.

## ⚙️Build Stages & Process

* Base: Chainguard Python image, sets up secure environment and working directory.
* Dev: Installs dev tools (pipx, poetry), all dependencies (with dev extras), and full source for rapid iteration and testing.
* Staging: Installs only main dependencies, exports requirements, removes dev/test files and caches, and switches to a non-root user for security.
* Prod: Inherits from staging, ensuring a clean, production-ready environment.
* Final: Uses Chainguard again for a distroless, secure runtime. Copies only built app and dependencies, sets up healthchecks and entrypoints.

## 🧩Orchestration & CI

* docker-compose.ymlorchestrates all services, mapping volumes for live reload (dev), healthchecks, and resource limits.
* GitHub Actions CIbuilds all images for each service and stage, ensuring reproducibility and security.
* nox_sessions/docker.pyprovides local build and vulnerability scan automation (Trivy, Grype).

## 🔒Security & Best Practices

* All images useChainguardfor minimal, continuously-patched Python runtimes.
* Non-root user enforced in all runtime stages.
* Dev/test files and build artifacts are removed from production images.
* Healthchecks and explicit entrypoints for orchestrator compatibility.
* Automated vulnerability scanning (Trivy, Grype) in local and CI workflows.

## 🚀Quick Reference

* Build (dev):docker build --target=dev -t shieldcraft-main:dev .
* Build (staging):docker build --target=staging -t shieldcraft-main:staging .
* Build (prod/final):docker build --target=final -t shieldcraft-main:prod .
* Compose up:docker-compose up --build
* CI:Seeci.ymlfor full build/test pipeline.

## 📚Further Reading

* Chainguard Python(base image)
* Docker BuildKit(caching, parallelism)
* Trivy&Grype(vulnerability scanning)
* Project README

<!-- Unhandled tags: b, em, li -->
