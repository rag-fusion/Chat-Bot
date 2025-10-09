#!/usr/bin/env python3
"""
Simple command-line interface for the RAG system.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.ingestion import extract_any
from app.embeddings import embed_text, embed_image
from app.vector_store import get_store
from app.retriever import get_retriever
from app.llm import build_adapter, load_config, generate_answer
from app.utils import create_citations


def ingest_file(file_path: str) -> str:
    """Ingest a file from command line."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    try:
        file_name = os.path.basename(file_path)
        chunks = extract_any(file_path, file_name, "")
        
        if not chunks:
            return f"No content extracted from {file_name}"
        
        store = get_store()
        items = []
        
        for chunk in chunks:
            if chunk.file_type == 'image':
                embedding = embed_image(chunk.filepath)
            else:
                embedding = embed_text(chunk.content)
            
            items.append({
                'embedding': embedding[0],
                'metadata': {
                    'content': chunk.content,
                    'file_name': chunk.file_name,
                    'file_type': chunk.file_type,
                    'page_number': chunk.page_number,
                    'timestamp': chunk.timestamp,
                    'filepath': chunk.filepath,
                    'width': getattr(chunk, 'width', None),
                    'height': getattr(chunk, 'height', None),
                    'bbox': getattr(chunk, 'bbox', None),
                    'char_start': getattr(chunk, 'char_start', None),
                    'char_end': getattr(chunk, 'char_end', None),
                    'modality': chunk.file_type
                }
            })
        
        added = store.upsert(items)
        return f"Successfully ingested {file_name}: {added} chunks added to index."
        
    except Exception as e:
        return f"Error ingesting file: {str(e)}"


def query_text(question: str, top_k: int = 5) -> str:
    """Query the system from command line."""
    if not question.strip():
        return "Please enter a question."
    
    try:
        retriever = get_retriever()
        results = retriever.retrieve(question, top_k)
        
        if not results:
            return "I don't have any relevant information to answer this question."
        
        config_path = os.path.join(os.path.dirname(__file__), "backend", "config.yaml")
        config = load_config(config_path)
        adapter = build_adapter(config)
        
        answer = generate_answer(question, results, adapter)
        
        # Add sources
        citations = create_citations(results)
        sources_text = "\n\nSources:\n"
        for i, citation in enumerate(citations, 1):
            sources_text += f"{i}. {citation['file_name']} ({citation['file_type']})\n"
        
        return answer + sources_text
        
    except Exception as e:
        return f"Error processing query: {str(e)}"


def show_status() -> str:
    """Show system status."""
    try:
        store = get_store()
        status = store.status()
        return f"""System Status:
- Total vectors: {status['vectors']}
- Files indexed: {status['files']}
- Embedding dimension: {status['dimension']}
- Modalities: {', '.join(status['modalities']) if status['modalities'] else 'None'}"""
    except Exception as e:
        return f"Error getting status: {str(e)}"


def main():
    """Main CLI interface."""
    print("Offline Multimodal RAG - Command Line Interface")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Ingest file")
        print("2. Ask question")
        print("3. Show status")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            file_path = input("Enter file path: ").strip()
            if file_path:
                result = ingest_file(file_path)
                print(f"\n{result}")
        
        elif choice == "2":
            question = input("Enter your question: ").strip()
            if question:
                top_k = input("Number of sources (default 5): ").strip()
                top_k = int(top_k) if top_k.isdigit() else 5
                result = query_text(question, top_k)
                print(f"\n{result}")
        
        elif choice == "3":
            result = show_status()
            print(f"\n{result}")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
