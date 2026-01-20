import os
import sys
import asyncio
from pathlib import Path

import aiohttp

# This script talks to HTTP API, so no complex imports needed usually.
# But it imports aiohttp.

async def ingest_file(session: aiohttp.ClientSession, path: Path):
  url = "http://localhost:8000/ingest"
  with path.open('rb') as f:
    data = aiohttp.FormData()
    data.add_field('file', f, filename=path.name)
    async with session.post(url, data=data) as resp:
      print(path.name, resp.status, await resp.text())


async def main(folder: str):
  p = Path(folder)
  if not p.exists():
      print(f"Folder {folder} does not exist.")
      return
  files = [x for x in p.iterdir() if x.is_file()]
  async with aiohttp.ClientSession() as session:
    for f in files:
      await ingest_file(session, f)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python scripts/ingest_local.py <folder>")
    sys.exit(1)
  asyncio.run(main(sys.argv[1]))
