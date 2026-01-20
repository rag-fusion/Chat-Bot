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

def _ensure_cpu_environment():
    """Force CPU-only environment for PyTorch operations."""
    import os
    import torch
    
    # Environment variables
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['USE_CUDA'] = '0'
    
    # PyTorch settings
    torch.cuda.is_available = lambda: False
    if hasattr(torch.backends, 'cudnn'):
        torch.backends.cudnn.enabled = False
    if hasattr(torch.backends, 'cuda'):
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cuda.is_built = lambda: False
    
    # Set default tensor type to CPU
    torch.set_default_tensor_type(torch.FloatTensor)
    
    # Disable JIT
    try:
        torch.jit.enable_onednn_fusion(False)
    except:
        pass
    try:
        torch._C._jit_set_profiling_executor(False)
    except:
        pass
    
    return torch.device('cpu')


def _get_clip_model() -> torch.nn.Module:
    """Internal function to get or initialize CLIP model (shared by text and image encoders).
    
    Optimized for offline CPU operation. Force CPU mode for compatibility.
    """
    global _clip_model, _clip_preprocess, _clip_tokenizer
    if _clip_model is None:
        # Always use CPU for compatibility
        device = "cpu"
        
        # Try to load from local path first
        env_path = os.getenv("CLIP_MODEL_PATH")
        repo_local = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "models", "clip", "ViT-B-32.pt")
        )
        alt_repo_local = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "models", "clip", "ViT-B-32.pt")
        )
        local_path = next((p for p in [env_path, repo_local, alt_repo_local] if p and os.path.exists(p)), None)

        if local_path:
            # Check file size to detect TorchScript (they're usually small serialized format)
            # TorchScript models may have hardcoded CUDA references, so we skip them by default
            import stat
            try:
                file_size = os.path.getsize(local_path)
                is_likely_torchscript = file_size < 10 * 1024 * 1024  # Less than 10MB is likely TorchScript
                
                if is_likely_torchscript:
                    print(f"Warning: Detected TorchScript model file ({file_size} bytes). Skipping to avoid CUDA hardcoding.")
                    model, preprocess, _ = open_clip.create_model_and_transforms(
                        "ViT-B-32", pretrained="openai"
                    )
                    model = model.to(device)
                else:
                    # Larger files might be state dicts
                    try:
                        checkpoint = torch.load(local_path, map_location="cpu", weights_only=False)
                        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                            # State dict checkpoint
                            model, preprocess, _ = open_clip.create_model_and_transforms(
                                "ViT-B-32", pretrained=False
                            )
                            model.load_state_dict(checkpoint['state_dict'])
                            model = model.to(device)
                            print(f"Loaded model from state dict checkpoint")
                        elif isinstance(checkpoint, dict):
                            # Attempt to load dict as state
                            model, preprocess, _ = open_clip.create_model_and_transforms(
                                "ViT-B-32", pretrained=False
                            )
                            model.load_state_dict(checkpoint)
                            model = model.to(device)
                            print(f"Loaded model from state dict")
                        else:
                            # Unknown format - create fresh model
                            print(f"Unknown checkpoint format. Creating fresh model.")
                            model, preprocess, _ = open_clip.create_model_and_transforms(
                                "ViT-B-32", pretrained="openai"
                            )
                            model = model.to(device)
                    except Exception as e:
                        print(f"Warning: Could not load checkpoint. Creating fresh model. Error: {str(e)[:100]}")
                        model, preprocess, _ = open_clip.create_model_and_transforms(
                            "ViT-B-32", pretrained="openai"
                        )
                        model = model.to(device)
            except Exception as e:
                print(f"Warning: Error checking local model. Creating fresh model. Error: {str(e)[:100]}")
                model, preprocess, _ = open_clip.create_model_and_transforms(
                    "ViT-B-32", pretrained="openai"
                )
                model = model.to(device)
        else:
            # Download from openai (requires internet on first run)
            print("No local CLIP model found. Downloading from OpenAI...")
            model, preprocess, _ = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="openai"
            )
            model = model.to(device)
        
        model.eval()
        _clip_model = model
        _clip_preprocess = preprocess
        _clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")
    
    return _clip_model


def get_text_model() -> torch.nn.Module:
    """Get or initialize CLIP text encoder for unified embeddings (512-dim)."""
    # Use CLIP model for unified embedding space
    return _get_clip_model()


def get_clip() -> tuple[torch.nn.Module, any]:
    """Get or initialize CLIP model for image embeddings (strictly CPU-only mode)."""
    global _clip_model, _clip_preprocess
    
    if _clip_model is None:
        # Force CPU-only environment
        device = _ensure_cpu_environment()
        
        # Create model with strict CPU configuration
        model, preprocess, _ = open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="openai",
            device="cpu",
            jit=False,  # Disable JIT to avoid CUDA issues
            force_quick_gelu=True  # Use CPU-friendly activation
        )
        
        # Force model to CPU mode and eval
        model = model.to("cpu")
        for param in model.parameters():
            param.data = param.data.to("cpu")
        model.eval()
        
        _clip_model = model
        _clip_preprocess = preprocess
    
    return _clip_model, _clip_preprocess


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
    
    # Determine device
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
    """Generate embeddings for image with strict CPU-only mode.
    
    Returns:
        numpy array of shape (1, 512) containing normalized CLIP image embedding.
    """
    global _clip_model, _clip_preprocess
    
    # Force CPU-only environment
    device = _ensure_cpu_environment()
    
    try:
        # Get model and preprocess function
        model, preprocess = get_clip()
        
        # Ensure model is in CPU mode
        model = model.cpu()
        
        # Load and preprocess image
        with Image.open(path) as img:
            # Convert to RGB and preprocess
            image = preprocess(img.convert("RGB"))
            
        # Ensure tensor is on CPU and create batch
        image = image.cpu()
        batch = torch.stack([image]).cpu()
        
        # Generate embeddings with strict error handling
        with torch.no_grad():
            try:
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
                
            except RuntimeError as e:
                error_msg = str(e)
                if "CUDA" in error_msg or "cuda" in error_msg.lower():
                    print("Warning: CUDA operation attempted. Reinitializing in CPU-only mode...")
                    # Reset model to force CPU reinitialization
                    _clip_model = None
                    _clip_preprocess = None
                    # Retry with fresh CPU model
                    model, preprocess = get_clip()
                    image = preprocess(Image.open(path).convert("RGB"))
                    batch = torch.stack([image]).cpu()
                    feats = model.encode_image(batch)
                    feats = feats / feats.norm(dim=-1, keepdim=True)
                    result = feats.cpu().numpy().astype(np.float32)
                    if result.ndim == 1:
                        result = result.reshape(1, -1)
                    return result
                raise  # Re-raise if it's not a CUDA error
                
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
