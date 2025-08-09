"""
BEIR Benchmark Orchestration Session for ShieldCraft AI
- Runs BEIR benchmarks in parallel for all configured datasets/models
- Surfaces results for CI/CD gating and reporting
- Robust error handling for happy/unhappy paths
- Uses Poetry for dependency management
"""

import nox


@nox.session()
def bier(session):
    """
    Orchestrate BEIR benchmark runs for all configured datasets/models.
    Results are saved and surfaced for CI/CD gating.
    """
    session.run("poetry", "install", external=True)
    session.run(
        "poetry",
        "run",
        "python",
        "-m",
        "ai_core.embedding.benchmark_beir",
        external=True,
    )
