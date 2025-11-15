"""
Enhanced LLM adapters with better prompt templates.
"""

from .adapter import LLMAdapter, build_adapter, generate_answer, load_config, MistralAdapter, LlamaCppAdapter, GPT4AllAdapter
from .prompts import build_prompt, SYSTEM_PROMPT_TEMPLATE

__all__ = [
    "LLMAdapter",
    "build_adapter", 
    "generate_answer",
    "load_config",
    "build_prompt",
    "SYSTEM_PROMPT_TEMPLATE",
    "MistralAdapter",
    "LlamaCppAdapter",
    "GPT4AllAdapter"
]
