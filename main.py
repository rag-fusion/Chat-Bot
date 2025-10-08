#!/usr/bin/env python3
"""
Main entry point for the Offline Multimodal RAG system.
Supports both FastAPI and Gradio interfaces.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.ui.gradio_app import launch_gradio_app
from app.main import app as fastapi_app
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Offline Multimodal RAG System")
    parser.add_argument("--interface", choices=["gradio", "fastapi"], default="gradio",
                       help="Choose interface: gradio (default) or fastapi")
    parser.add_argument("--port", type=int, default=7860,
                       help="Port to run the server on")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Host to bind to")
    parser.add_argument("--config", help="Path to config.yaml file")
    
    args = parser.parse_args()
    
    if args.interface == "gradio":
        print(f"Starting Gradio interface on http://{args.host}:{args.port}")
        launch_gradio_app(port=args.port, config_path=args.config)
    else:
        print(f"Starting FastAPI interface on http://{args.host}:{args.port}")
        uvicorn.run(fastapi_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
