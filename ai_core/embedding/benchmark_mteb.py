"""
ShieldCraft AI - MTEB Benchmarking Harness

This script runs the MTEB benchmark suite on your embedding model for comprehensive evaluation.
"""

import logging
import concurrent.futures
import json
from datetime import datetime
import argparse
import contextlib
from mteb import MTEB
from sentence_transformers import SentenceTransformer
from ai_core.embedding.embedding import EmbeddingModel
from infra.utils.config_loader import get_config_loader


logging.basicConfig(level=logging.INFO)


class ShieldCraftEmbeddingAdapter:
    """
    Config-driven adapter for MTEB. Uses EmbeddingModel if embedding.use_custom is True, else SentenceTransformer.
    """

    def __init__(self):
        config_loader = get_config_loader()
        config = config_loader.get_section("embedding")
        self.model_name = config.get(
            "model_name", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.use_custom = config.get("use_custom", False)
        if self.use_custom:
            self.model = EmbeddingModel(config=config)
        else:
            self.model = SentenceTransformer(self.model_name)


def encode(self, sentences, batch_size=32, **kwargs):
    if self.use_custom:
        result = self.model.encode(sentences)
        if not result["success"]:
            raise RuntimeError(f"Embedding failed: {result['error']}")
        return result["embeddings"]
    else:
        return self.model.encode(sentences, batch_size=batch_size, **kwargs)


def run_mteb(
    tasks=None,
    output_path="mteb_results.json",
):
    """
    Run MTEB benchmark on the config-driven embedding model and tasks.
    :param tasks: List of MTEB task names (default: all)
    :param output_path: Where to save results
    """

    logging.info("Loading embedding model via config for MTEB...")
    suite = MTEB(tasks=tasks)
    all_tasks = suite.tasks if tasks is None else tasks
    logging.info("Running MTEB benchmark in parallel (tasks: %s)", all_tasks)

    def run_single_task(task_name):
        try:
            # Each process must re-instantiate model for isolation
            local_model = ShieldCraftEmbeddingAdapter()
            local_suite = MTEB(tasks=[task_name])
            result = local_suite.run(local_model, output_folder=None)
            return {"task": task_name, "result": result, "success": True}
        except RuntimeError as e:
            logging.error("Task %s failed: %s", task_name, e)
            return {"task": task_name, "error": str(e), "success": False}
        except Exception as e:
            logging.error("Task %s failed with unexpected error: %s", task_name, e)
            return {"task": task_name, "error": str(e), "success": False}

    results = {}
    errors = {}
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_task = {executor.submit(run_single_task, t): t for t in all_tasks}
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                res = future.result()
                if res["success"]:
                    results[task] = res["result"]
                else:
                    errors[task] = res["error"]
            except RuntimeError as exc:
                errors[task] = str(exc)
            except Exception as exc:
                errors[task] = str(exc)

    # Save results and errors
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
        "errors": errors,
        "tasks": all_tasks,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logging.info("MTEB parallel benchmark complete. Results saved to %s", output_path)
    if errors:
        logging.warning("Some tasks failed: %s", list(errors.keys()))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run MTEB benchmark on an embedding model."
    )
    parser.add_argument(
        "--tasks",
        type=str,
        nargs="*",
        default=None,
        help="List of MTEB task names (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="mteb_results.json",
        help="Output path for results",
    )
    parser.add_argument(
        "--log",
        type=str,
        default="mteb_benchmark.log",
        help="Log file to capture all output",
    )
    args = parser.parse_args()
    with open(args.log, "w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(log_file):
            with contextlib.redirect_stderr(log_file):
                run_mteb(tasks=args.tasks, output_path=args.output)
