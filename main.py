#!/usr/bin/env python3
"""
Main entry point for the Offline Multimodal RAG system.
Supports both FastAPI and Gradio interfaces.
"""

import argparse
import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    parser = argparse.ArgumentParser(description="Offline Multimodal RAG System")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    print(f"Starting Backend API on http://{args.host}:{args.port}")
    uvicorn.run("backend.app.main:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
