"""
ShieldCraft AI Data Ingestion Pipeline Scaffold
"""

import os
from infra.utils.config_loader import get_config_loader
from ai_core.chunking.chunking import Chunker, ChunkingConfig


class DataIngestionPipeline:
    def __init__(self, config=None):
        config_loader = get_config_loader()
        if config is None:
            config = config_loader.get_section("data_ingestion")
        self.source_type = config.get("source_type", "local")
        self.source_path = config.get("source_path", "data_prep/assets/")
        self.batch_size = config.get("batch_size", 100)
        self.allowed_extensions = config.get(
            "allowed_extensions", [".txt", ".log", ".json"]
        )
        self.enable_chunking = config.get("enable_chunking", True)
        # Chunking config
        chunking_cfg = config.get(
            "chunking",
            {"chunk_size": 512, "overlap": 32, "strategy": "fixed", "min_length": 128},
        )

        try:
            self.chunker = (
                Chunker(ChunkingConfig(**chunking_cfg))
                if self.enable_chunking
                else None
            )
            if self.enable_chunking:
                print(f"[INFO] Chunker initialized | Config: {chunking_cfg}")
        except (TypeError, ValueError) as e:
            print(f"[ERROR] Chunker initialization failed: {e}")
            self.chunker = None
        print(
            f"[INFO] DataIngestionPipeline initialized | Source: {self.source_type} | Path: {self.source_path} | Batch size: {self.batch_size} | Chunking: {self.enable_chunking}"
        )

    def list_files(self):
        if self.source_type == "local":
            files = [
                os.path.join(self.source_path, f)
                for f in os.listdir(self.source_path)
                if os.path.splitext(f)[1] in self.allowed_extensions
            ]
            print(f"[INFO] Found {len(files)} files for ingestion.")
            return files
        # Add S3, Kafka, or other source logic here as needed
        print("[ERROR] Unsupported source type.")
        return []

    def read_batch(self, files):
        batch = []
        all_chunks = []
        for f in files[: self.batch_size]:
            try:
                with open(f, "r", encoding="utf-8") as infile:
                    text = infile.read()
                    batch.append(text)
                    if self.enable_chunking and self.chunker:
                        try:
                            chunks = self.chunker.chunk(text)
                            all_chunks.extend(chunks)
                        except (ValueError, TypeError) as ce:
                            print(f"[ERROR] Chunking failed for {f}: {ce}")
                    else:
                        all_chunks.append(text)
            except (OSError, UnicodeDecodeError) as e:
                print(f"[ERROR] Failed to read {f}: {e}")
        print(
            f"[INFO] Read {len(batch)} files in batch. Produced {len(all_chunks)} chunks."
        )
        return batch if not self.enable_chunking else all_chunks

    def run(self):
        files = self.list_files()
        if not files:
            print("[ERROR] No files to ingest.")
            return []
        output = self.read_batch(files)
        # Placeholder for downstream processing (embedding, vector store, etc.)
        print(
            f"[INFO] Ingestion pipeline completed for batch. Total output: {len(output)}"
        )
        return output
