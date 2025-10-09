"""
Gradio UI for the offline multimodal RAG system.
"""

import gradio as gr
import os
import tempfile
from typing import List, Dict, Any
from ..ingestion import extract_any
from ..embeddings import embed_text, embed_image
from ..vector_store import get_store
from ..retriever import get_retriever
from ..llm import build_adapter, load_config, generate_answer
from ..utils import create_citations, format_source_reference


class GradioApp:
    """Gradio application for the RAG system."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        self.store = get_store()
        self.retriever = get_retriever()
        self.llm_adapter = None
        self._load_llm_adapter()
    
    def _load_llm_adapter(self):
        """Load LLM adapter from config."""
        try:
            config = load_config(self.config_path)
            self.llm_adapter = build_adapter(config)
        except Exception as e:
            print(f"Warning: Could not load LLM adapter: {e}")
            self.llm_adapter = None
    
    def ingest_file(self, file) -> str:
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
            added = self.store.upsert(items)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return f"Successfully ingested {os.path.basename(file.name)}: {added} chunks added to index."
            
        except Exception as e:
            return f"Error ingesting file: {str(e)}"
    
    def query(self, question: str, top_k: int = 5) -> tuple[str, str, List[Dict[str, Any]]]:
        """Process user query and return answer with sources."""
        if not question.strip():
            return "Please enter a question.", "", []
        
        try:
            # Retrieve relevant chunks
            results = self.retriever.retrieve(question, top_k)
            
            if not results:
                return "I don't have any relevant information to answer this question.", "", []
            
            # Generate answer using LLM
            if self.llm_adapter:
                answer = generate_answer(question, results, self.llm_adapter)
            else:
                # Fallback: simple concatenation
                answer = f"Based on the available information:\n\n"
                for i, result in enumerate(results, 1):
                    answer += f"[{i}] {result.get('content', '')[:200]}...\n\n"
            
            # Create citations
            citations = create_citations(results)
            
            # Format sources for display
            sources_text = "Sources:\n"
            for i, citation in enumerate(citations, 1):
                sources_text += f"{i}. {format_source_reference(citation, i)}\n"
                sources_text += f"   {citation['snippet']}\n\n"
            
            return answer, sources_text, citations
            
        except Exception as e:
            return f"Error processing query: {str(e)}", "", []
    
    def get_status(self) -> str:
        """Get system status."""
        try:
            status = self.store.status()
            return f"""System Status:
- Total vectors: {status['vectors']}
- Files indexed: {status['files']}
- Embedding dimension: {status['dimension']}
- Modalities: {', '.join(status['modalities'])}
- LLM adapter: {'Loaded' if self.llm_adapter else 'Not available'}"""
        except Exception as e:
            return f"Error getting status: {str(e)}"


def create_gradio_interface(config_path: str = None) -> gr.Blocks:
    """Create Gradio interface."""
    app = GradioApp(config_path)
    
    with gr.Blocks(title="Offline Multimodal RAG", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# Offline Multimodal RAG System")
        gr.Markdown("Upload documents and ask questions about them. All processing happens locally.")
        
        with gr.Tab("Upload & Ingest"):
            gr.Markdown("## Upload Documents")
            file_input = gr.File(
                label="Upload Document",
                file_types=[".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".mp3", ".wav", ".m4a"],
                file_count="single"
            )
            ingest_btn = gr.Button("Ingest Document", variant="primary")
            ingest_output = gr.Textbox(label="Ingestion Status", lines=3)
            
            ingest_btn.click(
                app.ingest_file,
                inputs=[file_input],
                outputs=[ingest_output]
            )
        
        with gr.Tab("Query"):
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
                app.query,
                inputs=[question_input, top_k_slider],
                outputs=[answer_output, sources_output]
            )
        
        with gr.Tab("Status"):
            gr.Markdown("## System Status")
            status_btn = gr.Button("Refresh Status", variant="secondary")
            status_output = gr.Textbox(label="System Status", lines=10)
            
            status_btn.click(
                app.get_status,
                outputs=[status_output]
            )
    
    return interface


def launch_gradio_app(port: int = 7860, config_path: str = None):
    """Launch Gradio app."""
    interface = create_gradio_interface(config_path)
    interface.launch(server_port=port, share=False)


if __name__ == "__main__":
    launch_gradio_app()
