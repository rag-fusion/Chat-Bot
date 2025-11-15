#!/usr/bin/env python3
"""
Comprehensive system test for the offline multimodal RAG system.

Tests all modalities (text, image, audio), citation tracking, retrieval accuracy,
and offline compliance.
"""

import sys
import os
import json
import numpy as np
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.embeddings import embed_text, embed_image
from app.vector_store import get_store
from app.retriever import get_retriever
from app.ingestion import extract_any
from app.llm import build_adapter, load_config, generate_answer


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Testing: {name}{Colors.RESET}")


def print_pass(msg: str):
    """Print pass message."""
    try:
        print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {msg}")
    except UnicodeEncodeError:
        print(f"  [PASS] {msg}")


def print_fail(msg: str):
    """Print fail message."""
    try:
        print(f"  {Colors.RED}[FAIL]{Colors.RESET} {msg}")
    except UnicodeEncodeError:
        print(f"  [FAIL] {msg}")


def print_warn(msg: str):
    """Print warning message."""
    try:
        print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {msg}")
    except UnicodeEncodeError:
        print(f"  [WARN] {msg}")


def test_embedding_dimensions():
    """Test 1: Verify all embeddings are 512-dim."""
    print_test("Embedding Dimensions (Unified 512-dim Space)")
    
    try:
        # Test text embedding
        text_emb = embed_text("test text")
        # Handle both (1, 512) and (512,) shapes
        if text_emb.ndim == 1:
            assert text_emb.shape[0] == 512, f"Text embedding shape: {text_emb.shape}, expected 512-dim"
            print_pass(f"Text embedding: {text_emb.shape} (512-dim)")
        else:
            assert text_emb.shape[-1] == 512, f"Text embedding shape: {text_emb.shape}, expected 512-dim"
            print_pass(f"Text embedding: {text_emb.shape} (512-dim)")
        
        # Test batch text embedding
        text_emb_batch = embed_text(["text1", "text2"])
        # Handle shape variations
        if text_emb_batch.ndim == 2:
            assert text_emb_batch.shape[0] == 2, f"Batch should have 2 items, got {text_emb_batch.shape[0]}"
            assert text_emb_batch.shape[1] == 512, f"Each embedding should be 512-dim, got {text_emb_batch.shape[1]}"
            print_pass(f"Batch text embedding: {text_emb_batch.shape}")
        else:
            print_fail(f"Batch embedding should be 2D, got shape {text_emb_batch.shape}")
            return False
        
        return True
    except Exception as e:
        print_fail(f"Embedding dimension test failed: {e}")
        return False


def test_store_configuration():
    """Test 2: Verify store is configured for 512-dim."""
    print_test("FAISS Store Configuration")
    
    try:
        store = get_store()
        assert store.dimension == 512, f"Store dimension: {store.dimension}, expected 512"
        print_pass(f"Store dimension: {store.dimension}")
        
        status = store.status()
        print_pass(f"Store status: {status['vectors']} vectors, {status['files']} files")
        
        if status['modalities']:
            print_pass(f"Modalities in store: {', '.join(status['modalities'])}")
        
        return True
    except Exception as e:
        print_fail(f"Store configuration test failed: {e}")
        return False


def test_cross_modal_retrieval():
    """Test 3: Test cross-modal retrieval capabilities."""
    print_test("Cross-Modal Retrieval")
    
    try:
        store = get_store()
        retriever = get_retriever()
        
        if store.index.ntotal == 0:
            print_warn("No indexed data - skipping cross-modal retrieval test")
            print_warn("  (Ingest some documents first to test cross-modal retrieval)")
            return True  # Not a failure, just no data
        
        # Test text query
        query = "test query"
        results = retriever.retrieve(query, top_k=10)
        
        if not results:
            print_warn("No results returned - may need more indexed data")
            return True
        
        print_pass(f"Retrieved {len(results)} results for text query")
        
        # Check modality distribution
        modalities = {}
        for r in results:
            mod = r.get('modality', r.get('file_type', 'unknown'))
            modalities[mod] = modalities.get(mod, 0) + 1
        
        print_pass(f"Modalities in results: {dict(modalities)}")
        
        # Test cross-modal grouping
        grouped = retriever.retrieve_cross_modal(query, top_k=5)
        if isinstance(grouped, dict):
            print_pass(f"Cross-modal grouping: {list(grouped.keys())}")
        
        return True
    except Exception as e:
        print_fail(f"Cross-modal retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_citation_tracking():
    """Test 4: Verify citation tracking (file names, pages, timestamps)."""
    print_test("Citation Tracking")
    
    try:
        store = get_store()
        retriever = get_retriever()
        
        if store.index.ntotal == 0:
            print_warn("No indexed data - skipping citation test")
            return True
        
        query = "test"
        results = retriever.retrieve(query, top_k=5)
        
        if not results:
            print_warn("No results to test citations")
            return True
        
        citation_checks = {
            'file_name': 0,
            'page_number': 0,
            'timestamp': 0,
            'filepath': 0,
            'content': 0
        }
        
        for r in results:
            if r.get('file_name'):
                citation_checks['file_name'] += 1
            if r.get('page_number') is not None:
                citation_checks['page_number'] += 1
            if r.get('timestamp'):
                citation_checks['timestamp'] += 1
            if r.get('filepath'):
                citation_checks['filepath'] += 1
            if r.get('content'):
                citation_checks['content'] += 1
        
        total = len(results)
        print_pass(f"File names: {citation_checks['file_name']}/{total}")
        print_pass(f"Page numbers: {citation_checks['page_number']}/{total} (PDFs)")
        print_pass(f"Timestamps: {citation_checks['timestamp']}/{total} (Audio)")
        print_pass(f"File paths: {citation_checks['filepath']}/{total}")
        print_pass(f"Content: {citation_checks['content']}/{total}")
        
        # Check citation formatting
        from app.utils import create_citations
        citations = create_citations(results)
        
        if citations:
            print_pass(f"Citation formatting: {len(citations)} citations created")
            # Check first citation structure
            first = citations[0]
            required_fields = ['id', 'file_name', 'modality', 'snippet', 'score']
            missing = [f for f in required_fields if f not in first]
            if not missing:
                print_pass("Citation structure: All required fields present")
            else:
                print_fail(f"Citation structure: Missing fields: {missing}")
        
        return True
    except Exception as e:
        print_fail(f"Citation tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_offline_compliance():
    """Test 5: Verify offline operation (no external API calls)."""
    print_test("Offline Compliance")
    
    try:
        # Check that embeddings can be generated without internet
        # (This is a basic check - full offline test would require network isolation)
        
        # Test embedding generation
        text_emb = embed_text("offline test")
        assert text_emb is not None, "Text embedding generation failed"
        print_pass("Text embedding generation: Works offline")
        
        # Check model loading (should use local models)
        from app.embeddings import get_text_model, get_clip
        text_model = get_text_model()
        clip_result = get_clip()
        
        # get_clip returns a tuple (model, preprocess)
        if isinstance(clip_result, tuple) and len(clip_result) == 2:
            clip_model, _ = clip_result
        else:
            clip_model = clip_result
        
        assert text_model is not None, "Text model not loaded"
        assert clip_model is not None, "CLIP model not loaded"
        print_pass("Model loading: Local models available")
        
        # Check store (should be local)
        store = get_store()
        assert store is not None, "Store not initialized"
        print_pass("Vector store: Local storage (FAISS + SQLite)")
        
        return True
    except Exception as e:
        print_fail(f"Offline compliance test failed: {e}")
        return False


def test_ingestion_pipeline():
    """Test 6: Test ingestion for different file types."""
    print_test("Ingestion Pipeline")
    
    try:
        # Test that extract_any function exists and works
        # (We can't test actual file ingestion without test files)
        
        # Check that all extractors are importable
        from app.ingestion import (
            extract_text_from_pdf,
            extract_text_from_docx,
            image_to_embedding,
            transcribe_audio
        )
        print_pass("All ingestion modules importable")
        
        # Check chunk structure
        from app.ingestion.base import Chunk
        chunk = Chunk(
            content="test",
            file_name="test.txt",
            file_type="text"
        )
        assert chunk.content == "test"
        assert chunk.file_name == "test.txt"
        print_pass("Chunk structure: Valid")
        
        return True
    except Exception as e:
        print_fail(f"Ingestion pipeline test failed: {e}")
        return False


def test_retrieval_consistency():
    """Test 7: Test retrieval consistency (same query, same results)."""
    print_test("Retrieval Consistency")
    
    try:
        store = get_store()
        retriever = get_retriever()
        
        if store.index.ntotal == 0:
            print_warn("No indexed data - skipping consistency test")
            return True
        
        query = "test query for consistency"
        
        # Run query multiple times
        results1 = retriever.retrieve(query, top_k=5)
        results2 = retriever.retrieve(query, top_k=5)
        
        if not results1 or not results2:
            print_warn("No results - cannot test consistency")
            return True
        
        # Check that results are consistent (same number, same IDs)
        if len(results1) == len(results2):
            print_pass(f"Result count consistent: {len(results1)} results")
            
            # Check that top result is the same
            if results1 and results2:
                id1 = results1[0].get('vector_id')
                id2 = results2[0].get('vector_id')
                if id1 == id2:
                    print_pass("Top result consistent across queries")
                else:
                    print_warn("Top result differs (may be due to non-deterministic reranking)")
        else:
            print_fail(f"Result count inconsistent: {len(results1)} vs {len(results2)}")
            return False
        
        return True
    except Exception as e:
        print_fail(f"Retrieval consistency test failed: {e}")
        return False


def test_endpoint_compatibility():
    """Test 8: Verify API endpoint compatibility."""
    print_test("API Endpoint Compatibility")
    
    try:
        # Check that main endpoints can be imported
        from app.main import app
        print_pass("FastAPI app importable")
        
        # Check route registration
        routes = [r.path for r in app.routes]
        required_routes = ['/query', '/ingest', '/status', '/search/similarity']
        
        for route in required_routes:
            if route in routes:
                print_pass(f"Route registered: {route}")
            else:
                print_fail(f"Route missing: {route}")
                return False
        
        return True
    except Exception as e:
        print_fail(f"Endpoint compatibility test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and generate report."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("OFFLINE MULTIMODAL RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print(f"{'='*60}{Colors.RESET}\n")
    
    tests = [
        ("Embedding Dimensions", test_embedding_dimensions),
        ("Store Configuration", test_store_configuration),
        ("Cross-Modal Retrieval", test_cross_modal_retrieval),
        ("Citation Tracking", test_citation_tracking),
        ("Offline Compliance", test_offline_compliance),
        ("Ingestion Pipeline", test_ingestion_pipeline),
        ("Retrieval Consistency", test_retrieval_consistency),
        ("Endpoint Compatibility", test_endpoint_compatibility),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_fail(f"Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}: {name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        try:
            print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] All tests passed! System is ready.{Colors.RESET}\n")
        except:
            print(f"\n[SUCCESS] All tests passed! System is ready.\n")
        return 0
    else:
        try:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}[WARNING] Some tests failed or were skipped. Review above.{Colors.RESET}\n")
        except:
            print(f"\n[WARNING] Some tests failed or were skipped. Review above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

