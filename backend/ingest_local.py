"""Standalone ingestion script - reads from local build/ directory, no server needed."""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services import ExtractorService, ChunkerService, EmbedderService, StorageService
from src.models import BookPage
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Path to built HTML files
BUILD_DIR = Path(__file__).parent.parent / "build"
BASE_URL = "http://localhost:3001"  # Used as URL prefix in stored chunks

# Only ingest book content pages (docs/modules/intro)
HTML_FILES = [
    f for f in BUILD_DIR.rglob("*.html")
    if any(part in str(f) for part in ["/modules/", "/intro", "/docs/"])
    and "404" not in str(f)
]


async def run():
    extractor = ExtractorService()
    chunker = ChunkerService()
    embedder = EmbedderService()
    storage = StorageService()

    logger.info(f"Found {len(HTML_FILES)} HTML pages to ingest")

    # Ensure Qdrant collection exists
    storage.ensure_collection()
    logger.info("Qdrant collection ready")

    all_chunks = []
    for html_path in HTML_FILES:
        # Derive URL from file path relative to build dir
        rel = html_path.relative_to(BUILD_DIR)
        url = BASE_URL + "/" + str(rel).replace("\\", "/").replace(".html", "")

        try:
            html = html_path.read_text(encoding="utf-8")
            extracted = extractor.extract(html, url=url)

            if not extracted.extracted_text or len(extracted.extracted_text.strip()) < 50:
                logger.warning(f"Skipping (no content): {url}")
                continue

            chunks = chunker.chunk_page(
                text=extracted.extracted_text,
                source_url=url,
                title=extracted.title,
                sections=extracted.sections,
            )
            all_chunks.extend(chunks)
            logger.info(f"  {len(chunks):3d} chunks  <- {url}")

        except Exception as e:
            logger.error(f"Error processing {html_path}: {e}")

    logger.info(f"\nTotal chunks: {len(all_chunks)} — generating embeddings with Cohere...")

    if not all_chunks:
        logger.error("No chunks to embed. Exiting.")
        return

    # Embed all chunks (Cohere batch API)
    embeddings = await embedder.embed_async(all_chunks)
    logger.info(f"Embeddings generated: {len(embeddings)}")

    # Store in Qdrant
    stored = storage.upsert(all_chunks, embeddings)
    logger.info(f"\nDone! Stored {stored} vectors in Qdrant.")

    # Verify
    stats = storage.get_stats()
    logger.info(f"Qdrant collection '{stats['collection_name']}': {stats['vector_count']} vectors")


if __name__ == "__main__":
    asyncio.run(run())
