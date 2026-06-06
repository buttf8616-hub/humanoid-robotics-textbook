"""Test full extract+chunk pipeline on pages 7-10."""
import sys, time
import httpx
sys.path.insert(0, "src")

from services.extractor import ExtractorService
from services.chunker import ChunkerService

svc = ExtractorService()
chunker = ChunkerService()

URLS = [
    "https://humanoid-robotics-textbook-nu.vercel.app/modules/module-2/chapter-3-robot-modeling-urdf",
    "https://humanoid-robotics-textbook-nu.vercel.app/modules/module-3/chapter-1-gazebo-simulation-environments",
    "https://humanoid-robotics-textbook-nu.vercel.app/modules/module-3/chapter-2-unity-robotics-integration",
    "https://humanoid-robotics-textbook-nu.vercel.app/modules/module-3/chapter-3-sensor-simulation-integration",
]

for url in URLS:
    name = url.split("/")[-1]
    print(f"\n--- {name} ---", flush=True)

    t_fetch = time.perf_counter()
    r = httpx.get(url, follow_redirects=True, timeout=30)
    print(f"  fetch: {time.perf_counter()-t_fetch:.2f}s, {len(r.text)/1024:.0f}KB", flush=True)

    t_ext = time.perf_counter()
    page = svc.extract(r.text, url)
    print(f"  extract: {time.perf_counter()-t_ext:.3f}s, sections={len(page.sections)}, textlen={len(page.extracted_text)}", flush=True)

    t_chunk = time.perf_counter()
    chunks = chunker.chunk_page(
        text=page.extracted_text,
        source_url=url,
        title=page.title,
        sections=page.sections,
    )
    print(f"  chunk: {time.perf_counter()-t_chunk:.3f}s, chunks={len(chunks)}", flush=True)

print("\nALL DONE", flush=True)
