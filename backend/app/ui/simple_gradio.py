"""
Simplified Gradio UI for the offline multimodal RAG system.
"""

import gradio as gr
import os
import tempfile
import socket
from typing import List, Dict, Any
from ..ingestion import extract_any
from ..embeddings import embed_text, embed_image
from ..vector_store import get_store
from ..retriever import get_retriever
from ..llm import build_adapter, load_config, generate_answer
from ..utils import create_citations, format_source_reference


def find_available_port(start_port: int = 7860, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts - 1}")


def ingest_file(file) -> str:
    """Ingest uploaded file."""
    if file is None:
        return "No file uploaded."
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name
        
        # Extract content
        chunks = extract_any(tmp_path, os.path.basename(file.name), "")
        
        if not chunks:
            return f"No content extracted from {os.path.basename(file.name)}"
        
        # Generate embeddings and store
        store = get_store()
        items = []
        
        for chunk in chunks:
            if chunk.file_type == 'image':
                embedding = embed_image(chunk.filepath)
            else:
                embedding = embed_text(chunk.content)
            
            items.append({
                'embedding': embedding[0],  # Remove batch dimension
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
        
        # Store in vector database
        added = store.upsert(items)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return f"Successfully ingested {os.path.basename(file.name)}: {added} chunks added to index."
        
    except Exception as e:
        return f"Error ingesting file: {str(e)}"


def query(question: str, top_k: int = 5) -> tuple[str, str]:
    """Process user query and return answer with sources."""
    if not question.strip():
        return "Please enter a question.", ""
    
    try:
        # Retrieve relevant chunks
        retriever = get_retriever()
        results = retriever.retrieve(question, top_k)
        
        if not results:
            return "I don't have any relevant information to answer this question.", ""
        
        # Generate answer using LLM
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        config = load_config(config_path)
        adapter = build_adapter(config)
        
        answer = generate_answer(question, results, adapter)
        
        # Create citations
        citations = create_citations(results)
        
        # Format sources for display
        sources_text = "Sources:\n"
        for i, citation in enumerate(citations, 1):
            sources_text += f"{i}. {citation['file_name']} ({citation['file_type']})\n"
            sources_text += f"   {citation['snippet']}\n\n"
        
        return answer, sources_text
        
    except Exception as e:
        return f"Error processing query: {str(e)}", ""


def get_status() -> str:
    """Get system status."""
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


def create_simple_interface() -> gr.Blocks:
    """Create a simplified Gradio interface."""
    
    with gr.Blocks(title="Offline Multimodal RAG", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# Offline Multimodal RAG System")
        gr.Markdown("Upload documents and ask questions about them. All processing happens locally.")
        
        # Upload section
        gr.Markdown("## Upload Documents")
        file_input = gr.File(
            label="Upload Document",
            file_types=[".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".mp3", ".wav", ".m4a"],
            file_count="single"
        )
        ingest_btn = gr.Button("Ingest Document", variant="primary")
        ingest_output = gr.Textbox(label="Ingestion Status", lines=3)
        
        ingest_btn.click(
            ingest_file,
            inputs=[file_input],
            outputs=[ingest_output]
        )
        
        # Query section
        gr.Markdown("## Ask Questions")
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="Ask anything about your documents...",
            lines=2
        )
        top_k_slider = gr.Slider(
            minimum=1,
            maximum=20,
            value=5,
            step=1,
            label="Number of sources to retrieve"
        )
        query_btn = gr.Button("Ask Question", variant="primary")
        
        answer_output = gr.Textbox(label="Answer", lines=8)
        sources_output = gr.Textbox(label="Sources", lines=10)
        
        query_btn.click(
            query,
            inputs=[question_input, top_k_slider],
            outputs=[answer_output, sources_output]
        )
        
        # Status section
        gr.Markdown("## System Status")
        status_btn = gr.Button("Refresh Status", variant="secondary")
        status_output = gr.Textbox(label="System Status", lines=10)
        
        status_btn.click(
            get_status,
            outputs=[status_output]
        )
    
    return interface


def launch_simple_app(port: int = 7860, config_path: str = None):
    """Launch simplified Gradio app."""
    interface = create_simple_interface()
    
    # Try to find an available port if the specified port is not available
    try:
        available_port = find_available_port(port)
        if available_port != port:
            print(f"Port {port} is not available. Using port {available_port} instead.")
        port = available_port
    except RuntimeError as e:
        print(f"Error finding available port: {e}")
        print("Trying to launch on the specified port anyway...")
    
    print(f"Launching Gradio interface on port {port}")
    interface.launch(
        server_port=port, 
        share=False, 
        show_error=True,
        server_name="0.0.0.0",
        inbrowser=False,
        quiet=False
    )


if __name__ == "__main__":
    launch_simple_app()
