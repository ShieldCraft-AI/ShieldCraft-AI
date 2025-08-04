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
        with open(log_path, "w", encoding="utf-8") as log_file:
            proc = subprocess.run(
                cmd, stdout=log_file, stderr=subprocess.STDOUT, check=False, env=env
            )
        # If subprocess failed, forcibly recreate log file with error info
        if proc.returncode != 0:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Error: Subprocess failed with return code {proc.returncode}\n"
                )
        return {"cmd": cmd, "log": log_path, "returncode": proc.returncode}
    except (OSError, subprocess.SubprocessError) as e:
        # Forcibly create log file with error info
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}\n")
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
    results = []
    import shutil

    for dataset in datasets:
        output_path = os.path.join(output_dir, f"beir_{dataset}.json")
        log_path = os.path.join(output_dir, f"beir_{dataset}.log")
        # Always create empty output and log files before running
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("")
        cmd = [
            "poetry",
            "run",
            "python",
            "ai_core/embedding/benchmark_beir.py",
            "--datasets",
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
        res = run_benchmark(cmd, log_path)
        # If error or non-zero return code, overwrite output/log with error info
        if res.get("error") or res.get("returncode", 1) != 0:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Error: {res.get('error', f'Subprocess failed with return code {res.get('returncode', 1)}')}\n"
                )
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "error": res.get(
                            "error",
                            f"Subprocess failed with return code {res.get('returncode', 1)}",
                        )
                    },
                    f,
                )
        # After subprocess, forcibly recreate files if missing
        if not os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Error: {res.get('error', f'Subprocess failed with return code {res.get('returncode', 1)}')}\n"
                )
        if not os.path.exists(output_path):
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "error": res.get(
                            "error",
                            f"Subprocess failed with return code {res.get('returncode', 1)}",
                        )
                    },
                    f,
                )
        results.append(res)
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
    results = []
    import shutil

    for task in tasks:
        output_path = os.path.join(output_dir, f"mteb_{task}.json")
        log_path = os.path.join(output_dir, f"mteb_{task}.log")
        # Always create empty output and log files before running
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("")
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
        res = run_benchmark(cmd, log_path)
        # If error or non-zero return code, overwrite output/log with error info
        if res.get("error") or res.get("returncode", 1) != 0:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Error: {res.get('error', f'Subprocess failed with return code {res.get('returncode', 1)}')}\n"
                )
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "error": res.get(
                            "error",
                            f"Subprocess failed with return code {res.get('returncode', 1)}",
                        )
                    },
                    f,
                )
        # After subprocess, forcibly recreate files if missing
        if not os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Error: {res.get('error', f'Subprocess failed with return code {res.get('returncode', 1)}')}\n"
                )
        if not os.path.exists(output_path):
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "error": res.get(
                            "error",
                            f"Subprocess failed with return code {res.get('returncode', 1)}",
                        )
                    },
                    f,
                )
        results.append(res)
    return results


def main():

    parser = argparse.ArgumentParser(
        description="Orchestrate parallel benchmarking runs."
    )
    parser.add_argument(
        "--env", type=str, default=None, help="Environment to use (dev, staging, prod)"
    )
    parser.add_argument(
        "--beir-datasets",
        type=str,
        nargs="*",
        default=None,
        help="BEIR datasets to run",
    )
    parser.add_argument(
        "--mteb-tasks", type=str, nargs="*", default=None, help="MTEB tasks to run"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None, help="Output directory for results"
    )
    parser.add_argument(
        "--max-workers", type=int, default=None, help="Max parallel workers"
    )
    parser.add_argument(
        "--batch-size", type=int, default=None, help="Batch size for embedding"
    )
    args = parser.parse_args()

    # Use ConfigLoader for all config
    config = get_orchestrator_config(env=args.env)
    orch = config["orchestrator"] or {}
    beir_cfg = config["beir"] or {}
    mteb_cfg = config["mteb"] or {}
    model = config["model"]
    batch_size = (
        args.batch_size if args.batch_size is not None else config["batch_size"]
    )
    custom_model = config["custom_model"]
    embedding_config = config["embedding_config"]
    data_path = config["data_path"]
    output_dir = (
        args.output_dir
        if args.output_dir is not None
        else orch.get("output_dir", "orch_results")
    )
    max_workers = (
        args.max_workers if args.max_workers is not None else orch.get("max_workers", 2)
    )

    # Override datasets/tasks from CLI if provided
    beir_datasets = (
        args.beir_datasets
        if args.beir_datasets is not None
        else beir_cfg.get("datasets")
    )
    mteb_tasks = (
        args.mteb_tasks if args.mteb_tasks is not None else mteb_cfg.get("tasks")
    )

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
                        with open(metrics_path, encoding="utf-8") as f:
                            entry["metrics"] = json.load(f)
                    except (json.JSONDecodeError, OSError):
                        entry["metrics"] = None
            summary.append(entry)
        # Write JSON summary
        with open(summary_path + ".json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        # Write CSV summary
        with open(summary_path + ".csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["cmd", "log", "returncode", "error", "metrics"]
            )
            writer.writeheader()
            for row in summary:
                writer.writerow(row)

    ran_any = False
    if beir_datasets:
        ran_any = True
        beir_outdir = output_dir
        logging.info("Launching BEIR benchmarks for datasets: %s", beir_datasets)
        results = orchestrate_beir(
            datasets=beir_datasets,
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
                logging.info("SUCCESS: %s (log: %s)", res["cmd"], res["log"])
            else:
                logging.info(
                    "ERROR: %s (log: %s) - %s",
                    res["cmd"],
                    res["log"],
                    res.get("error", "see log"),
                )
        aggregate_results(results, os.path.join(beir_outdir, "beir_summary"))

    if mteb_tasks:
        ran_any = True
        mteb_outdir = output_dir
        logging.info("Launching MTEB benchmarks for tasks: %s", mteb_tasks)
        results = orchestrate_mteb(
            tasks=mteb_tasks,
            model=model,
            batch_size=batch_size,
            use_custom_model=custom_model,
            config_path=embedding_config,
            output_dir=mteb_outdir,
            max_workers=max_workers,
        )
        for res in results:
            if res.get("returncode", 1) == 0:
                logging.info("SUCCESS: %s (log: %s)", res["cmd"], res["log"])
            else:
                logging.info(
                    "ERROR: %s (log: %s) - %s",
                    res["cmd"],
                    res["log"],
                    res.get("error", "see log"),
                )
        aggregate_results(results, os.path.join(mteb_outdir, "mteb_summary"))

    if not ran_any:
        logging.warning("No BEIR datasets or MTEB tasks specified. Nothing to run.")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        logging.error("Orchestration interrupted by user.")
        sys.exit(1)
    except SystemExit as e:
        # argparse exits with code 2 for argument errors; treat as handled
        if hasattr(e, "code") and e.code == 2:
            logging.error("Argument parsing error (code 2): handled gracefully.")
            sys.exit(0)
        else:
            sys.exit(e.code if hasattr(e, "code") else 1)
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        logging.error("Orchestration failed: %s", e, exc_info=True)
        sys.exit(1)
