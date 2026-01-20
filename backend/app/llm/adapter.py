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
        
        if not os.path.exists(model_path):
             raise FileNotFoundError(f"Model file not found at: {model_path}")

        # Initialize Llama model
        # set verbose=False to reduce console noise if desired
        self.llm = Llama(model_path=model_path, n_ctx=4096, verbose=True)
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        # llama-cpp-python generate call
        out = self.llm(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            echo=False 
        )
        return out.get("choices", [{}])[0].get("text", "")


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
    
    # 1. Resolve relative paths to absolute paths
    if path and not os.path.isabs(path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        path = os.path.abspath(os.path.join(backend_dir, path))
    
    # 2. Validate path existence (Required)
    if not path:
        raise ValueError("Configuration error: 'model_path' is required but not set.")

    # 3. Route backends
    if backend == "gpt4all":
        return GPT4AllAdapter(path)
    elif backend in ["llama_cpp", "mistral"]:
        # Mistral GGUF models are run via llama.cpp
        return LlamaCppAdapter(path)
    else:
        raise ValueError(f"Unknown model_backend: {backend}. Supported: 'gpt4all', 'llama_cpp', 'mistral'")


def generate_answer(query: str, context_chunks: List[Dict[str, Any]], 
                   adapter: LLMAdapter, max_tokens: int = 512, 
                   temperature: float = 0.0) -> str:
    """Generate answer using LLM adapter with context."""
    prompt = build_prompt(query, context_chunks)
    return adapter.generate(prompt, max_tokens=max_tokens, temperature=temperature)
