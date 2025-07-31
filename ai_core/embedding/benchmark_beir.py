"""
ShieldCraft AI - BEIR Benchmarking Harness

This script runs the BEIR benchmark suite on your embedding model for retrieval evaluation.
"""

import concurrent.futures
import os
import argparse
import json
from datetime import datetime
import logging
from beir import util
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval.evaluation import EvaluateRetrieval
from beir.retrieval.search.dense import DenseRetrievalExactSearch as DRES
from sentence_transformers import SentenceTransformer
from ai_core.embedding.embedding import EmbeddingModel
from infra.utils.config_loader import get_config_loader


class ShieldCraftEmbeddingAdapter:
    """
    Config-driven adapter for BEIR. Uses EmbeddingModel if embedding.use_custom is True, else SentenceTransformer.
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


logging.basicConfig(level=logging.INFO)


def run_beir(
    datasets=["scifact"],
    data_path="./beir_datasets",
    output_path="beir_results.json",
    batch_size=32,
):
    """
    Run BEIR benchmark in parallel for the specified datasets.
    :param datasets: List of BEIR dataset names
    :param data_path: Path to download/load BEIR datasets
    :param output_path: Where to save results
    :param batch_size: Batch size for encoding
    """

    def run_single_dataset(dataset):
        try:
            logging.info(f"Loading BEIR dataset: {dataset}")
            url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset}.zip"
            dataset_path = util.download_and_unzip(url, data_path)
            corpus, queries, qrels = GenericDataLoader(dataset_path).load(split="test")
            logging.info("Loading embedding model via config for BEIR...")
            model = DRES(ShieldCraftEmbeddingAdapter(), batch_size=batch_size)
            retriever = EvaluateRetrieval(model, score_function="cos_sim")
            logging.info(f"Running BEIR retrieval benchmark on {dataset}")
            results = retriever.retrieve(corpus, queries)
            ndcg, _map, recall, precision = retriever.evaluate(
                qrels, results, retriever.k_values
            )
            metrics = {
                "nDCG": ndcg,
                "MAP": _map,
                "Recall": recall,
                "Precision": precision,
            }
            return {"dataset": dataset, "metrics": metrics, "success": True}
        except Exception as e:
            logging.error(f"Dataset {dataset} failed: {e}")
            return {"dataset": dataset, "error": str(e), "success": False}

    results = {}
    errors = {}
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_dataset = {
            executor.submit(run_single_dataset, d): d for d in datasets
        }
        for future in concurrent.futures.as_completed(future_to_dataset):
            dataset = future_to_dataset[future]
            try:
                res = future.result()
                if res["success"]:
                    results[dataset] = res["metrics"]
                else:
                    errors[dataset] = res["error"]
            except Exception as exc:
                errors[dataset] = str(exc)

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
        "errors": errors,
        "datasets": datasets,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    logging.info(f"BEIR parallel benchmark complete. Results saved to {output_path}")
    if errors:
        logging.warning(f"Some datasets failed: {list(errors.keys())}")
    return output


if __name__ == "__main__":
    config_loader = get_config_loader()
    beir_config = (
        config_loader.get_section("beir") if "beir" in config_loader.config else {}
    )

    parser = argparse.ArgumentParser(
        description="Run BEIR benchmark on an embedding model. CLI flags override config."
    )

    parser.add_argument(
        "--datasets",
        type=str,
        nargs="*",
        default=beir_config.get("datasets", ["scifact"]),
        help="List of BEIR dataset names (default: from config)",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default=beir_config.get("data_path", "./beir_datasets"),
        help="Path to download/load BEIR datasets (default: from config)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=beir_config.get("output_path", "beir_results.json"),
        help="Output path for results (default: from config)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=beir_config.get("batch_size", 32),
        help="Batch size for encoding (default: from config)",
    )
    args = parser.parse_args()

    run_beir(
        datasets=args.datasets,
        data_path=args.data_path,
        output_path=args.output,
        batch_size=args.batch_size,
    )
