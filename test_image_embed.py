import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.embeddings.generate import embed_image
import numpy as np

def test_image_embedding():
    """Test image embedding generation with CPU mode."""
    try:
        # Try with a test image
        test_image = Path(__file__).parent / "backend" / "storage" / "Screenshot 2025-11-06 234029.png"
        if not test_image.exists():
            print(f"Test image not found at {test_image}")
            return False
        
        print("Starting image embedding generation...")
        embedding = embed_image(str(test_image))
        
        # Check embedding shape and type
        print(f"Embedding shape: {embedding.shape}")
        print(f"Embedding dtype: {embedding.dtype}")
        print("✅ Successfully generated image embedding!")
        return True
    except Exception as e:
        print(f"❌ Error generating image embedding: {str(e)}")
        return False

if __name__ == "__main__":
    test_image_embedding()