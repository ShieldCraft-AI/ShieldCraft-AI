"""
ShieldCraft AI - Benchmark Orchestration Script

This script orchestrates parallel benchmarking runs (BEIR, MTEB, custom) across multiple datasets,
models, and configs. It is designed for extensibility, robust error handling, and future
cloud/distributed execution.
"""

import argparse
import json
import os
import csv
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
import logging
import sys


sys.path.append(str(Path(__file__).parent.parent))
from infra.utils.config_loader import ConfigLoader


def get_orchestrator_config(env=None):
    loader = ConfigLoader(env=env)
    orch = loader.get_section("orchestrator")
    beir = loader.get_section("beir") if "beir" in loader.config else {}
    mteb = loader.get_section("mteb") if "mteb" in loader.config else {}
    # Always prefer config values for model, batch_size, data_path
    model = (
        loader.get("embedding.model_name", None)
        or beir.get("model")
        or mteb.get("model")
    )
    batch_size = (
        loader.get("embedding.batch_size", None)
        or beir.get("batch_size")
        or mteb.get("batch_size")
        or orch.get("batch_size", 32)
    )
    custom_model = (
        loader.get("embedding.custom_model", False)
        or beir.get("custom_model", False)
        or mteb.get("custom_model", False)
    )
    embedding_config = (
        loader.get("embedding.config", None)
        or beir.get("embedding_config")
        or mteb.get("embedding_config")
    )
    data_path = beir.get("data_path") or loader.get("data_path", "./beir_datasets")
    return {
        "orchestrator": orch,
        "beir": beir,
        "mteb": mteb,
        "model": model,
        "batch_size": batch_size,
        "custom_model": custom_model,
        "embedding_config": embedding_config,
        "data_path": data_path,
    }


def run_benchmark(cmd: List[str], log_path: str) -> Dict[str, Any]:
    """Run a single benchmark command, capturing output and errors."""
    try:
        env = os.environ.copy()
        # Ensure project root is in PYTHONPATH for all subprocesses
        project_root = str(Path(__file__).parent.parent.resolve())
        env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
        with open(log_path, "w") as log_file:
            proc = subprocess.run(
                cmd, stdout=log_file, stderr=subprocess.STDOUT, check=False, env=env
            )
        return {"cmd": cmd, "log": log_path, "returncode": proc.returncode}
    except Exception as e:
        return {"cmd": cmd, "log": log_path, "error": str(e), "returncode": -1}


def orchestrate_beir(
    datasets: List[str],
    model: str,
    batch_size: int,
    use_custom_model: bool,
    config_path: str = None,
    data_path: str = "./beir_datasets",
    output_dir: str = "beir_orch_results",
    max_workers: int = 2,
):
    """Orchestrate BEIR runs in parallel across datasets."""
    os.makedirs(output_dir, exist_ok=True)
    futures = []
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for dataset in datasets:
            output_path = os.path.join(output_dir, f"beir_{dataset}.json")
            log_path = os.path.join(output_dir, f"beir_{dataset}.log")
            cmd = [
                "poetry",
                "run",
                "python",
                "ai_core/embedding/benchmark_beir.py",
                "--dataset",
                dataset,
                "--output",
                output_path,
                "--batch-size",
                str(batch_size),
                "--data-path",
                data_path,
            ]
            if use_custom_model:
                cmd.append("--custom-model")
            if config_path:
                cmd.extend(["--config", config_path])
            if model and not use_custom_model:
                cmd.extend(["--model", model])
            futures.append(executor.submit(run_benchmark, cmd, log_path))
        for future in as_completed(futures):
            results.append(future.result())
    return results


def orchestrate_mteb(
    tasks: List[str],
    model: str,
    batch_size: int,
    use_custom_model: bool,
    config_path: str = None,
    output_dir: str = "mteb_orch_results",
    max_workers: int = 2,
):
    """Orchestrate MTEB runs in parallel across tasks."""
    os.makedirs(output_dir, exist_ok=True)
    futures = []
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for task in tasks:
            output_path = os.path.join(output_dir, f"mteb_{task}.json")
            log_path = os.path.join(output_dir, f"mteb_{task}.log")
            if use_custom_model:
                script = "ai_core/embedding/benchmark_mteb_custom.py"
                cmd = [
                    "poetry",
                    "run",
                    "python",
                    script,
                    "--tasks",
                    task,
                    "--output",
                    output_path,
                ]
                if config_path:
                    cmd.extend(["--config", config_path])
            else:
                script = "ai_core/embedding/benchmark_mteb.py"
                cmd = [
                    "poetry",
                    "run",
                    "python",
                    script,
                    "--model",
                    model,
                    "--tasks",
                    task,
                    "--output",
                    output_path,
                ]
            futures.append(executor.submit(run_benchmark, cmd, log_path))
        for future in as_completed(futures):
            results.append(future.result())
    return results


def main():

    parser = argparse.ArgumentParser(
        description="Orchestrate parallel benchmarking runs."
    )
    parser.add_argument(
        "--env", type=str, default=None, help="Environment to use (dev, staging, prod)"
    )
    args = parser.parse_args()

    # Use ConfigLoader for all config
    config = get_orchestrator_config(env=args.env)
    orch = config["orchestrator"] or {}
    beir_cfg = config["beir"] or {}
    mteb_cfg = config["mteb"] or {}
    model = config["model"]
    batch_size = config["batch_size"]
    custom_model = config["custom_model"]
    embedding_config = config["embedding_config"]
    data_path = config["data_path"]
    output_dir = orch.get("output_dir", "orch_results")
    max_workers = orch.get("max_workers", 2)

    def aggregate_results(results, summary_path):
        summary = []
        for res in results:
            entry = {
                "cmd": " ".join(res.get("cmd", [])),
                "log": res.get("log"),
                "returncode": res.get("returncode"),
                "error": res.get("error", None),
                "metrics": None,
            }
            # Try to load metrics from output file if present
            if res.get("log") and res.get("log").endswith(".log"):
                metrics_path = res["log"].replace(".log", ".json")
                if os.path.exists(metrics_path):
                    try:
                        with open(metrics_path) as f:
                            entry["metrics"] = json.load(f)
                    except Exception:
                        entry["metrics"] = None
            summary.append(entry)
        # Write JSON summary
        with open(summary_path + ".json", "w") as f:
            json.dump(summary, f, indent=2)
        # Write CSV summary
        with open(summary_path + ".csv", "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["cmd", "log", "returncode", "error", "metrics"]
            )
            writer.writeheader()
            for row in summary:
                writer.writerow(row)

    ran_any = False
    if beir_cfg.get("datasets"):
        ran_any = True
        beir_outdir = os.path.join(output_dir, "beir")
        logging.info(f"Launching BEIR benchmarks for datasets: {beir_cfg['datasets']}")
        results = orchestrate_beir(
            datasets=beir_cfg["datasets"],
            model=model,
            batch_size=batch_size,
            use_custom_model=custom_model,
            config_path=embedding_config,
            data_path=data_path,
            output_dir=beir_outdir,
            max_workers=max_workers,
        )
        for res in results:
            if res.get("returncode", 1) == 0:
                logging.info(f"SUCCESS: {res['cmd']} (log: {res['log']})")
            else:
                logging.error(
                    f"FAIL: {res['cmd']} (log: {res['log']}) - {res.get('error', 'see log')}"
                )
        aggregate_results(results, os.path.join(beir_outdir, "beir_summary"))

    if mteb_cfg.get("tasks"):
        ran_any = True
        mteb_outdir = os.path.join(output_dir, "mteb")
        logging.info(f"Launching MTEB benchmarks for tasks: {mteb_cfg['tasks']}")
        results = orchestrate_mteb(
            tasks=mteb_cfg["tasks"],
            model=model,
            batch_size=batch_size,
            use_custom_model=custom_model,
            config_path=embedding_config,
            output_dir=mteb_outdir,
            max_workers=max_workers,
        )
        for res in results:
            if res.get("returncode", 1) == 0:
                logging.info(f"SUCCESS: {res['cmd']} (log: {res['log']})")
            else:
                logging.error(
                    f"FAIL: {res['cmd']} (log: {res['log']}) - {res.get('error', 'see log')}"
                )
        aggregate_results(results, os.path.join(mteb_outdir, "mteb_summary"))

    if not ran_any:
        logging.warning("No BEIR datasets or MTEB tasks specified. Nothing to run.")


if __name__ == "__main__":
    main()
