"""
ShieldCraft AI Core - Vector Store Scaffold (pgvector, config-driven)
"""

import psycopg2
import numpy as np
from infra.utils.config_loader import get_config_loader


class VectorStore:
    def __init__(self, config=None):
        config_loader = get_config_loader()
        if config is None:
            config = config_loader.get_section("vector_store")
        self.db_host = config.get("db_host", "localhost")
        self.db_port = config.get("db_port", 5432)
        self.db_name = config.get("db_name", "shieldcraft_vectors")
        self.db_user = config.get("db_user", "postgres")
        self.db_password = config.get("db_password", "postgres")
        self.table_name = config.get("table_name", "embeddings")
        self.batch_size = config.get("batch_size", 100)
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
            )
            self._ensure_table()
            print(
                f"[INFO] Connected to pgvector DB: {self.db_name}@{self.db_host}:{self.db_port}"
            )
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            print(f"[ERROR] Vector store DB connection failed: {e}")
            self.conn = None

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    embedding VECTOR(384)
                );
            """
            )
            self.conn.commit()

    def upsert_embeddings(self, texts, embeddings):
        if self.conn is None:
            return "[ERROR] Vector store not connected."
        try:
            with self.conn.cursor() as cur:
                for text, emb in zip(texts, embeddings):
                    cur.execute(
                        f"INSERT INTO {self.table_name} (text, embedding) VALUES (%s, %s)",
                        (text, emb.tolist()),
                    )
                self.conn.commit()
            print(f"[INFO] Upserted {len(texts)} embeddings.")
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            print(f"[ERROR] Upsert failed: {e}")
            return "[ERROR] Upsert failed."

    def query(self, query_embedding, top_k=5):
        if self.conn is None:
            return "[ERROR] Vector store not connected."
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"SELECT text, embedding FROM {self.table_name} ORDER BY embedding <-> %s LIMIT %s",
                    (query_embedding.tolist(), top_k),
                )
                results = cur.fetchall()
            return results
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            print(f"[ERROR] Query failed: {e}")
            return "[ERROR] Query failed."
