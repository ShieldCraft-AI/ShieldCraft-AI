"""
ShieldCraft AI Core - Embedding Pipeline Scaffold
"""

import torch
from transformers import AutoTokenizer, AutoModel
from infra.utils.config_loader import get_config_loader

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    def __init__(self, config=None):
        config_loader = get_config_loader()
        if config is None:
            config = config_loader.get_section("embedding")
        self.model_name = config.get("model_name", EMBEDDING_MODEL_NAME)
        self.device = config.get("device") or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.quantize = config.get("quantize", False)
        self.quantization_type = config.get(
            "quantization_type", "float16"
        )  # float16, int8, bitsandbytes
        self.batch_size = config.get("batch_size", 32)
        self.model = None
        self.tokenizer = None
        self._init_error = None
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            quant_kwargs = {}
            quant_status = "none"
            if self.quantize:
                if self.quantization_type == "float16":
                    quant_kwargs["torch_dtype"] = torch.float16
                    quant_status = "float16"
                elif self.quantization_type == "int8":
                    quant_kwargs["torch_dtype"] = torch.qint8
                    quant_status = "int8"
                elif self.quantization_type == "bitsandbytes":
                    try:
                        import bitsandbytes as bnb

                        quant_kwargs["load_in_8bit"] = True
                        quant_status = "bitsandbytes-8bit"
                    except ImportError:
                        print(
                            "[WARN] bitsandbytes not installed, falling back to float16."
                        )
                        quant_kwargs["torch_dtype"] = torch.float16
                        quant_status = "float16-fallback"
                else:
                    print(
                        f"[WARN] Unknown quantization_type: {self.quantization_type}, using float16."
                    )
                    quant_kwargs["torch_dtype"] = torch.float16
                    quant_status = "float16-fallback"
            self.model = AutoModel.from_pretrained(self.model_name, **quant_kwargs)
            self.model.to(self.device)
            env = config_loader.get_section("app").get("env", "unknown")
            print(
                f"[INFO] Loaded embedding model: {self.model_name} | Env: {env} | Device: {self.device} | Quantized: {self.quantize} | Type: {quant_status}"
            )
        except Exception as e:
            print(f"[ERROR] Embedding model or tokenizer loading failed: {e}")
            self.model = None
            self.tokenizer = None
            self._init_error = str(e)

    def encode(self, texts):
        """
        Encode a batch of texts into embeddings. Returns dict with 'success', 'embeddings', 'error'.
        """
        result = {"success": False, "embeddings": None, "error": None}
        if self.model is None or self.tokenizer is None:
            err_msg = self._init_error or "Embedding model not loaded."
            result["error"] = f"Embedding model not loaded: {err_msg}"
            return result
        if isinstance(texts, str):
            texts = [texts]
        if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
            result["error"] = "Input must be a string or list of strings."
            return result
        if len(texts) == 0:
            result["error"] = "Input text list is empty."
            return result
        try:
            # Batch processing for large inputs
            all_embeddings = []
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]
                inputs = self.tokenizer(
                    batch, padding=True, truncation=True, return_tensors="pt"
                ).to(self.device)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                all_embeddings.append(embeddings.cpu().numpy())
            import numpy as np

            embeddings = np.vstack(all_embeddings)
            result["success"] = True
            result["embeddings"] = embeddings
            result["shape"] = embeddings.shape
            result["dtype"] = str(embeddings.dtype)
            print(
                f"[INFO] Embedding batch complete | shape: {embeddings.shape} | dtype: {embeddings.dtype}"
            )
            return result
        except Exception as e:
            result["error"] = f"Embedding failed: {e}"
            print(f"[ERROR] Embedding failed: {e}")
            return result
