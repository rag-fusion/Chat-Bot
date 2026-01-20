import time
import os
import sys

# Add backend to path to allow imports from app
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

from app.rag import answer_query

CFG = os.path.join(backend_dir, 'config.yaml')

EXAMPLES = [
  ("What improves solar panel efficiency?", "solar"),
  ("What converts kinetic energy into electricity?", "Wind turbines"),
]

def run():
  print("Evaluating RAG pipeline...")
  if not os.path.exists(CFG):
      print(f"Config file not found: {CFG}")
      return

  for q, kw in EXAMPLES:
    t0 = time.time()
    out = answer_query(CFG, q)
    dt = (time.time() - t0) * 1000
    ok = (kw.lower() in (out.get('answer') or '').lower()) or any(kw.lower() in (s.get('snippet') or '').lower() for s in out.get('sources', []))
    print(f"Q: {q}\n  ok={ok} time_ms={dt:.1f}\n  answer: {out.get('answer')[:200]}...\n  sources: {[s.get('file_name') for s in out.get('sources', [])]}")

if __name__ == '__main__':
  run()
