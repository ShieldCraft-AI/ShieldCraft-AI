"""
ShieldCraft AI - MTEB Benchmarking Harness (Custom Model Integration)
This script allows benchmarking your custom EmbeddingModel (quantized,
config-driven, etc.) with the MTEB suite.
"""

import sys
import logging
from mteb import MTEB
from sentence_transformers import SentenceTransformer
from ai_core.embedding.embedding import EmbeddingModel

logging.basicConfig(level=logging.INFO)


class CustomSentenceTransformer:
    """
    Adapter to wrap your EmbeddingModel for MTEB compatibility.
    Implements encode(texts, **kwargs) -> np.ndarray
    """

    def __init__(self, model_name=None, config=None):
        self.model = EmbeddingModel(config=config)

    def encode(self, sentences, batch_size=32, **kwargs):
        # MTEB expects a list of strings, returns np.ndarray (n_samples, dim)
        result = self.model.encode(sentences)
        if not result["success"]:
            raise RuntimeError(f"Embedding failed: {result['error']}")
        return result["embeddings"]


def run_mteb_custom(tasks=None, output_path="mteb_results_custom.json", config=None):
    """
    Run MTEB benchmark on the custom EmbeddingModel.
    :param tasks: List of MTEB task names (default: all)
    :param output_path: Where to save results
    :param config: Optional config dict for EmbeddingModel
    """
    logging.info(f"Loading custom EmbeddingModel for MTEB...")
    model = CustomSentenceTransformer(config=config)
    suite = MTEB(tasks=tasks)
    logging.info(f"Running MTEB benchmark on custom model (tasks: {tasks or 'all'})")
    results = suite.run(model, output_folder=output_path)
    logging.info(f"MTEB benchmark complete. Results saved to {output_path}")
    return results


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Run MTEB benchmark on custom EmbeddingModel."
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
        default="mteb_results_custom.json",
        help="Output path for results",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config JSON file for EmbeddingModel",
    )
    args = parser.parse_args()

    CONFIG = None
    if args.config:
        with open(args.config, "r") as f:
            CONFIG = json.load(f)
    run_mteb_custom(tasks=args.tasks, output_path=args.output, config=CONFIG)
