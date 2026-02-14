"""
Enhanced embedding generation with proper offline support.
"""

from __future__ import annotations

import os
from typing import List, Union
import numpy as np
import torch
from PIL import Image
import open_clip


# Global model instances
_text_model = None  # No longer used, kept for backward compatibility
_clip_model: torch.nn.Module | None = None
_clip_preprocess = None
_clip_tokenizer = None

def _get_device() -> torch.device:
    """Get the best available device."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _get_clip_model() -> tuple[torch.nn.Module, any]:
    """Shared internal function to get or initialize CLIP model (unified for Text & Image).
    
    CRITICAL: Must use identical model settings for standardizing the embedding space.
    """
    global _clip_model, _clip_preprocess, _clip_tokenizer
    
    if _clip_model is None:
        device = _get_device()
        print(f"Initializing unified CLIP model (ViT-B-32) on {device}...")
        
        try:
            # Always use the same settings for both text and image!
            # force_quick_gelu=True is standard for OpenAI CLIP weights
            model, preprocess, _ = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="openai",
                device=device,
                jit=False,
                force_quick_gelu=True
            )
            
            # Ensure proper eval mode
            model = model.eval()
            
            # Update globals
            _clip_model = model
            _clip_preprocess = preprocess
            _clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")
            print(f"CLIP model initialized successfully on {device}.")
            
        except Exception as e:
            print(f"Error initializing CLIP model: {e}")
            raise
            
    return _clip_model, _clip_preprocess


def get_text_model() -> torch.nn.Module:
    """Get CLIP model for text encoding."""
    model, _ = _get_clip_model()
    return model


def get_clip() -> tuple[torch.nn.Module, any]:
    """Get CLIP model for image encoding."""
    return _get_clip_model()


def embed_text(text: Union[str, List[str]]) -> np.ndarray:
    """Generate embeddings for text using CLIP text encoder (512-dim).
    
    Optimized for batch processing and reduced latency.
    """
    model = get_text_model()
    global _clip_tokenizer
    
    # Ensure tokenizer is initialized
    if _clip_tokenizer is None:
        _clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")
    
    if isinstance(text, str):
        text = [text]
    
    # Determine device from model
    device = next(model.parameters()).device
    
    # Tokenize text (batch processing)
    text_tokens = _clip_tokenizer(text)
    text_tokens = text_tokens.to(device)
    
    # Generate embeddings using CLIP text encoder
    # Use torch.no_grad() for inference efficiency
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        # Normalize embeddings (same as image embeddings)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    # Convert to numpy efficiently (always move to CPU first)
    result = text_features.cpu().numpy().astype(np.float32)
    # Ensure consistent shape: if single text, return (1, 512), not (512,)
    if result.ndim == 1:
        result = result.reshape(1, -1)
    return result


def embed_image(path: str) -> np.ndarray:
    """Generate embeddings for image using best available device.
    
    Returns:
        numpy array of shape (1, 512) containing normalized CLIP image embedding.
    """
    global _clip_model, _clip_preprocess
    
    try:
        # Get model and preprocess function
        model, preprocess = get_clip()
        
        # Determine device from model
        device = next(model.parameters()).device
        
        # Load and preprocess image
        with Image.open(path) as img:
            # Convert to RGB and preprocess
            image = preprocess(img.convert("RGB"))
            
        # Move to device and create batch
        image = image.to(device)
        batch = torch.stack([image]).to(device)
        
        # Generate embeddings with strict error handling
        with torch.no_grad():
            # Encode image and normalize
            feats = model.encode_image(batch)
            # Normalize: feats shape is (1, 512), normalize per-sample
            feats = feats / feats.norm(dim=-1, keepdim=True)
            result = feats.cpu().numpy().astype(np.float32)
            
            # Ensure shape is (1, 512)
            if result.ndim == 1:
                result = result.reshape(1, -1)
            
            assert result.shape == (1, 512), f"Expected shape (1, 512), got {result.shape}"
            return result
                
    except Exception as e:
        print(f"Error processing image {path}: {str(e)}")
        raise


def embed_audio_segment(transcript: str) -> np.ndarray:
    """Generate embeddings for audio transcript (uses text embedding)."""
    return embed_text(transcript)


# Legacy functions for backward compatibility
def embed_texts(texts: List[str]) -> np.ndarray:
    """Legacy function for backward compatibility."""
    return embed_text(texts)


def embed_image_paths(paths: List[str]) -> np.ndarray:
    """Legacy function for backward compatibility."""
    embeddings = []
    for path in paths:
        emb = embed_image(path)
        embeddings.append(emb[0])  # Remove batch dimension
    return np.array(embeddings)
