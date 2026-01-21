
import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.rag import answer_query

def debug_rag(query):
    # Resolve config path
    cfg_path = os.path.abspath(os.path.join("backend", "config.yaml"))
    print(f"Using config: {cfg_path}")
    
    try:
        response = answer_query(cfg_path, query)
        print("\n--- Response ---")
        print(f"Answer: {response.get('answer', '')[:50]}...")
        print("Sources:")
        for s in response.get('sources', []):
            print(f"  [{s.get('id')}] File: {s.get('file_name')}")
            snippet = s.get('snippet', '')
            print(f"      Snippet ({len(snippet)} chars): {snippet[:50]}...")
            if not snippet:
                print("      WARNING: Snippet is empty!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    query = "test"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    debug_rag(query)
