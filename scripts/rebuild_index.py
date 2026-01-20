import sys
import os

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

from app.index_store import rebuild_from_db

if __name__ == "__main__":
    # MiniLM-L6-v2 embedding size
    res = rebuild_from_db(384)
    print(res)
