"""
Enhanced LLM adapters with improved prompt templates.
"""

from __future__ import annotations

import os
import yaml
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .prompts import build_prompt


class LLMAdapter(ABC):
    """Base class for LLM adapters."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        """Generate text from prompt."""
        pass


class GPT4AllAdapter(LLMAdapter):
    """GPT4All adapter for local inference."""
    
    def __init__(self, model_path: str):
        try:
            from gpt4all import GPT4All
        except Exception as e:
            raise RuntimeError("gpt4all is not installed. pip install gpt4all") from e
        self.model = GPT4All(model_path)
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        return self.model.generate(prompt, max_tokens=max_tokens, temp=temperature)


class LlamaCppAdapter(LLMAdapter):
    """Llama.cpp adapter for local inference."""
    
    def __init__(self, model_path: str):
        try:
            from llama_cpp import Llama
        except Exception as e:
            raise RuntimeError("llama-cpp-python is not installed. pip install llama-cpp-python") from e
        self.llm = Llama(model_path=model_path, n_ctx=4096)
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        out = self.llm(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
        return out.get("choices", [{}])[0].get("text", "")


class MistralAdapter(LLMAdapter):
    """Mistral adapter placeholder."""
    
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        # Placeholder generation - replace with actual Mistral integration
        return f"[Mistral placeholder response] Based on the context: {prompt[:200]}..."


def load_config(path: str) -> dict:
    """Load configuration from YAML file."""
    if not os.path.exists(path):
        return {
            "model_backend": "mistral", 
            "model_path": None, 
            "top_k": 5, 
            "max_tokens": 512, 
            "temperature": 0.2
        }
    return yaml.safe_load(open(path, "r"))


def build_adapter(cfg: dict) -> LLMAdapter:
    """Build LLM adapter from configuration."""
    backend = (cfg.get("model_backend") or "mistral").lower()
    path = cfg.get("model_path")
    
    if backend == "gpt4all":
        return GPT4AllAdapter(path)
    elif backend == "llama_cpp":
        return LlamaCppAdapter(path)
    else:
        return MistralAdapter(path)


def generate_answer(query: str, context_chunks: List[Dict[str, Any]], 
                   adapter: LLMAdapter, max_tokens: int = 512, 
                   temperature: float = 0.0) -> str:
    """Generate answer using LLM adapter with context."""
    prompt = build_prompt(query, context_chunks)
    return adapter.generate(prompt, max_tokens=max_tokens, temperature=temperature)
