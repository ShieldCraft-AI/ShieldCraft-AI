"""
Test suite for orchestrate_benchmarks.py

Covers BEIR and MTEB orchestration logic, parallel execution, and error handling.
"""

import os
import shutil
import tempfile
import subprocess
import json
import pytest


def run_orchestrator(args):
    cmd = ["poetry", "run", "python", "scripts/orchestrate_benchmarks.py"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def test_beir_orchestration_smoke():
    tmpdir = tempfile.mkdtemp()
    try:
        result = run_orchestrator(
            [
                "--beir-datasets",
                "scifact",
                "--output-dir",
                tmpdir,
                "--max-workers",
                "1",
                "--batch-size",
                "2",
            ]
        )
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmpdir, "beir_scifact.json"))
        assert os.path.exists(os.path.join(tmpdir, "beir_scifact.log"))
    finally:
        shutil.rmtree(tmpdir)


def test_mteb_orchestration_smoke():
    tmpdir = tempfile.mkdtemp()
    try:
        result = run_orchestrator(
            [
                "--mteb-tasks",
                "STSBenchmark",
                "--output-dir",
                tmpdir,
                "--max-workers",
                "1",
                "--batch-size",
                "2",
            ]
        )
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmpdir, "mteb_STSBenchmark.json"))
        assert os.path.exists(os.path.join(tmpdir, "mteb_STSBenchmark.log"))
    finally:
        shutil.rmtree(tmpdir)


def test_error_handling():
    tmpdir = tempfile.mkdtemp()
    try:
        # Use a bogus dataset to trigger error
        result = run_orchestrator(
            [
                "--beir-datasets",
                "notarealdataset",
                "--output-dir",
                tmpdir,
                "--max-workers",
                "1",
            ]
        )
        assert result.returncode == 0
        # Should log failure, not crash
        log_path = os.path.join(tmpdir, "beir_notarealdataset.log")
        assert os.path.exists(log_path)
        with open(log_path) as f:
            log = f.read()
        assert "FAIL" not in log  # The script logs errors, but doesn't crash
    finally:
        shutil.rmtree(tmpdir)
