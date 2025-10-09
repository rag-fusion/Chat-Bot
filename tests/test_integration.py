"""
Enhanced tests for the multimodal RAG system.
"""

import pytest
import tempfile
import os
import numpy as np
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "This is a sample document for testing the RAG system. It contains multiple sentences to test chunking and embedding generation."


@pytest.fixture
def sample_chunks():
    """Sample chunks for testing."""
    from app.ingestion.base import Chunk
    return [
        Chunk(
            content="First chunk of text",
            file_name="test.txt",
            file_type="text",
            filepath="/tmp/test.txt"
        ),
        Chunk(
            content="Second chunk of text",
            file_name="test.txt", 
            file_type="text",
            filepath="/tmp/test.txt"
        )
    ]


class TestIngestion:
    """Test ingestion modules."""
    
    def test_text_chunking(self, sample_text):
        """Test text chunking functionality."""
        from app.ingestion.base import _split_text
        
        chunks = _split_text(sample_text, min_size=20, max_size=50)
        assert len(chunks) > 0
        assert all(len(chunk) <= 50 for chunk in chunks)
        assert all(len(chunk) >= 20 for chunk in chunks)
    
    def test_pdf_extraction(self, temp_dir):
        """Test PDF extraction (requires PyMuPDF)."""
        from app.ingestion.doc_extractor import extract_text_from_pdf
        
        # Create a simple text file as PDF substitute
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Sample PDF content for testing")
        
        # This will fall back to text extraction
        chunks = extract_text_from_pdf(test_file, "test.txt")
        assert len(chunks) > 0
        assert chunks[0].file_name == "test.txt"
    
    def test_docx_extraction(self, temp_dir):
        """Test DOCX extraction."""
        from app.ingestion.doc_extractor import extract_text_from_docx
        
        # Create a simple text file as DOCX substitute
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Sample DOCX content for testing")
        
        chunks = extract_text_from_docx(test_file, "test.txt")
        assert len(chunks) > 0
        assert chunks[0].file_name == "test.txt"


class TestEmbeddings:
    """Test embedding generation."""
    
    def test_text_embedding(self, sample_text):
        """Test text embedding generation."""
        from app.embeddings import embed_text
        
        embedding = embed_text(sample_text)
        assert embedding.shape[0] == 1  # Single text
        assert embedding.shape[1] == 384  # MiniLM-L6-v2 dimension
        assert isinstance(embedding, np.ndarray)
    
    def test_text_embeddings_batch(self):
        """Test batch text embedding generation."""
        from app.embeddings import embed_text
        
        texts = ["First text", "Second text", "Third text"]
        embeddings = embed_text(texts)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == 384
    
    def test_embedding_model_loading(self):
        """Test embedding model loading."""
        from app.embeddings import get_text_model
        
        model = get_text_model()
        assert model is not None
        assert hasattr(model, 'encode')


class TestVectorStore:
    """Test vector store functionality."""
    
    def test_faiss_store_creation(self, temp_dir):
        """Test FAISS store creation."""
        from app.vector_store import FAISSStore
        
        store = FAISSStore(dimension=384, storage_dir=temp_dir)
        assert store.dimension == 384
        assert store.index is not None
        assert store.index.ntotal == 0
    
    def test_faiss_store_upsert(self, temp_dir, sample_chunks):
        """Test FAISS store upsert functionality."""
        from app.vector_store import FAISSStore
        from app.embeddings import embed_text
        
        store = FAISSStore(dimension=384, storage_dir=temp_dir)
        
        items = []
        for chunk in sample_chunks:
            embedding = embed_text(chunk.content)
            items.append({
                'embedding': embedding[0],
                'metadata': {
                    'content': chunk.content,
                    'file_name': chunk.file_name,
                    'file_type': chunk.file_type,
                    'filepath': chunk.filepath,
                    'modality': chunk.file_type
                }
            })
        
        added = store.upsert(items)
        assert added == len(items)
        assert store.index.ntotal == len(items)
    
    def test_faiss_store_search(self, temp_dir, sample_chunks):
        """Test FAISS store search functionality."""
        from app.vector_store import FAISSStore
        from app.embeddings import embed_text
        
        store = FAISSStore(dimension=384, storage_dir=temp_dir)
        
        # Add items
        items = []
        for chunk in sample_chunks:
            embedding = embed_text(chunk.content)
            items.append({
                'embedding': embedding[0],
                'metadata': {
                    'content': chunk.content,
                    'file_name': chunk.file_name,
                    'file_type': chunk.file_type,
                    'filepath': chunk.filepath,
                    'modality': chunk.file_type
                }
            })
        
        store.upsert(items)
        
        # Search
        query_embedding = embed_text("test query")
        results = store.search(query_embedding, top_k=2)
        
        assert len(results) <= 2
        assert all('score' in result for result in results)
        assert all('content' in result for result in results)


class TestRetriever:
    """Test retrieval functionality."""
    
    def test_retriever_creation(self):
        """Test retriever creation."""
        from app.retriever import Retriever
        
        retriever = Retriever()
        assert retriever is not None
        assert retriever.store is not None
    
    def test_retriever_rerank(self):
        """Test retriever reranking."""
        from app.retriever import Retriever
        
        retriever = Retriever()
        
        # Mock results
        results = [
            {'content': 'exact match query', 'score': 0.8, 'file_name': 'test.txt'},
            {'content': 'partial match', 'score': 0.7, 'file_name': 'test.txt'},
            {'content': 'no match', 'score': 0.6, 'file_name': 'test.txt'}
        ]
        
        reranked = retriever.rerank_results('exact match query', results)
        
        assert len(reranked) == len(results)
        assert 'rerank_score' in reranked[0]
        # First result should have highest rerank score due to exact match
        assert reranked[0]['rerank_score'] >= reranked[1]['rerank_score']


class TestLLM:
    """Test LLM functionality."""
    
    def test_llm_adapter_creation(self):
        """Test LLM adapter creation."""
        from app.llm import MistralAdapter
        
        adapter = MistralAdapter()
        assert adapter is not None
    
    def test_prompt_building(self):
        """Test prompt building functionality."""
        from app.llm.prompts import build_prompt
        
        query = "What is the main topic?"
        sources = [
            {
                'content': 'This document discusses machine learning',
                'file_name': 'test.txt',
                'file_type': 'text'
            }
        ]
        
        prompt = build_prompt(query, sources)
        
        assert query in prompt
        assert 'test.txt' in prompt
        assert 'machine learning' in prompt


class TestUtils:
    """Test utility functions."""
    
    def test_cross_modal_linker(self):
        """Test cross-modal linking."""
        from app.utils import CrossModalLinker
        
        linker = CrossModalLinker(similarity_threshold=0.5)
        
        results = [
            {'content': 'same content', 'modality': 'text', 'vector_id': 1},
            {'content': 'same content', 'modality': 'image', 'vector_id': 2},
            {'content': 'different content', 'modality': 'audio', 'vector_id': 3}
        ]
        
        linked = linker.find_links(results)
        
        assert len(linked) == len(results)
        # Should find links between text and image with same content
        text_result = next(r for r in linked if r['vector_id'] == 1)
        assert 'cross_modal_links' in text_result
    
    def test_citation_creation(self):
        """Test citation creation."""
        from app.utils import create_citations
        
        results = [
            {
                'content': 'Sample content',
                'file_name': 'test.txt',
                'file_type': 'text',
                'score': 0.9
            }
        ]
        
        citations = create_citations(results)
        
        assert len(citations) == 1
        assert citations[0]['id'] == 1
        assert citations[0]['file_name'] == 'test.txt'
        assert citations[0]['score'] == 0.9


class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_ingestion(self, temp_dir, sample_text):
        """Test end-to-end ingestion pipeline."""
        from app.ingestion import extract_any
        from app.embeddings import embed_text
        from app.vector_store import FAISSStore
        
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write(sample_text)
        
        # Extract
        chunks = extract_any(test_file, "test.txt", "")
        assert len(chunks) > 0
        
        # Embed and store
        store = FAISSStore(dimension=384, storage_dir=temp_dir)
        items = []
        
        for chunk in chunks:
            embedding = embed_text(chunk.content)
            items.append({
                'embedding': embedding[0],
                'metadata': {
                    'content': chunk.content,
                    'file_name': chunk.file_name,
                    'file_type': chunk.file_type,
                    'filepath': chunk.filepath,
                    'modality': chunk.file_type
                }
            })
        
        added = store.upsert(items)
        assert added > 0
        
        # Search
        query_embedding = embed_text("sample document")
        results = store.search(query_embedding, top_k=1)
        assert len(results) > 0
        assert 'content' in results[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
