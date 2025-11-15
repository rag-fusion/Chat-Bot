import os
import whisper
from pathlib import Path

# Set up paths
model_dir = Path("backend/models/whisper")
model_dir.mkdir(parents=True, exist_ok=True)

# Download the model
print("Downloading Whisper model...")
model = whisper.load_model("base")
print("Model downloaded successfully!")