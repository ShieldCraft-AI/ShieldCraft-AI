"""
ShieldCraft AI Core - Mistral-7B Model Loader Scaffold
"""

import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_NAME = "mistralai/Mistral-7B-v0.1"


class ShieldCraftAICore:
    def __init__(self, config=None):
        from infra.utils.config_loader import get_config_loader

        config_loader = get_config_loader()
        if config is None:
            config = config_loader.get_section("ai_core")
        self.model_name = config.get("model_name", MODEL_NAME)
        self.device = config.get("device") or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.quantize = config.get("quantize", False)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model_kwargs = {}
        if self.quantize:
            model_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, **model_kwargs
            )
            self.model.to(self.device)
            env = config_loader.get_section("app").get("env", "unknown")
            print(
                f"[INFO] Loaded model: {self.model_name} | Env: {env} | Device: {self.device} | Quantized: {self.quantize}"
            )
        except Exception as e:
            print(f"[ERROR] Model loading failed: {e}")
            self.model = None

    def generate(self, prompt: str, max_new_tokens: int = 64) -> str:
        if self.model is None:
            return "[ERROR] Model not loaded."
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            start = time.time()
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            latency = time.time() - start
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(
                f"[INFO] Inference latency: {latency:.2f}s | Device: {self.device} | Quantized: {self.quantize}"
            )
            return result
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(
                    "[ERROR] Out of memory during inference. Try using quantization or a smaller model."
                )
            else:
                print(f"[ERROR] Inference failed: {e}")
            return "[ERROR] Inference failed."
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return "[ERROR] Unexpected error."


if __name__ == "__main__":
    ai_core = ShieldCraftAICore()
    test_prompt = "Summarize the latest security alert:"
    print(ai_core.generate(test_prompt))
