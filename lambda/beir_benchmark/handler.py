"""
AWS Lambda handler for BEIR Benchmarking
- Accepts event with dataset/config info
- Invokes BEIR benchmarking logic
- Returns results/errors for Step Functions orchestration
"""

import json
import logging
from ai_core.embedding.benchmark_beir import run_beir


def handler(event, context):
    """
    Lambda entry point for BEIR benchmarking.
    Expects event to contain:
      - datasets: list of dataset names
      - data_path: path for BEIR datasets
      - output_path: where to save results
      - batch_size: batch size for encoding
    """
    logging.basicConfig(level=logging.INFO)
    try:
        datasets = event.get("datasets", ["scifact"])
        data_path = event.get("data_path", "./beir_datasets")
        output_path = event.get("output_path", "/tmp/beir_results.json")
        batch_size = event.get("batch_size", 32)
        result = run_beir(
            datasets=datasets,
            data_path=data_path,
            output_path=output_path,
            batch_size=batch_size,
        )
        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }
    except Exception as e:
        logging.error(f"BEIR Lambda failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
