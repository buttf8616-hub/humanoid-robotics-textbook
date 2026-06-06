"""Standalone ingestion script — runs outside FastAPI, shows live progress."""
import asyncio
import logging
import sys
import os

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from src.services import CrawlerService, ExtractorService, ChunkerService, EmbedderService, StorageService

log_file = os.path.join(os.path.dirname(__file__), "ingest.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)
logger.info(f"Log file: {log_file}")


async def main():
    base_url = os.getenv("BOOK_BASE_URL", "http://localhost:3001")
    logger.info(f"Starting ingestion from: {base_url}")

    crawler  = CrawlerService(base_url=base_url)
    extractor = ExtractorService()
    chunker  = ChunkerService()
    embedder = EmbedderService()
    storage  = StorageService()

    # Ensure collection exists
    logger.info("Ensuring Qdrant collection exists...")
    storage.ensure_collection()

    # Step 1: Crawl
    logger.info("Crawling book pages...")
    pages = await crawler.crawl_all()
    logger.info(f"Crawled {len(pages)} pages")

    if not pages:
        logger.error("No pages found — is the book server running on http://localhost:3001?")
        return

    # Step 2: Extract + chunk
    all_chunks = []
    for i, page in enumerate(pages, 1):
        try:
            extracted = extractor.extract(page.raw_html, page.url)
            chunks = chunker.chunk_page(
                text=extracted.extracted_text,
                source_url=page.url,
                title=extracted.title,
                sections=extracted.sections,
            )
            all_chunks.extend(chunks)
            logger.info(f"  [{i}/{len(pages)}] {page.url} → {len(chunks)} chunks")
        except Exception as e:
            logger.warning(f"  [{i}/{len(pages)}] SKIP {page.url}: {e}")

    logger.info(f"Total chunks: {len(all_chunks)}")

    if not all_chunks:
        logger.error("No chunks created — check extraction logic")
        return

    # Step 3: Embed (small batches to stay within trial rate limits)
    logger.info("Generating Cohere embeddings...")
    batch_size = 20  # smaller batches to avoid rate limit timeouts
    all_embeddings = []
    client = embedder._get_client()
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        texts = [c.content for c in batch]
        batch_num = i // batch_size + 1
        total_batches = (len(all_chunks) + batch_size - 1) // batch_size
        try:
            logger.info(f"  Embedding batch {batch_num}/{total_batches} ({len(texts)} chunks)...")
            resp = client.embed(texts=texts, model=embedder.model, input_type="search_document")
            all_embeddings.extend(resp.embeddings)
            logger.info(f"  ✓ batch {batch_num}/{total_batches} done — {min(i + batch_size, len(all_chunks))}/{len(all_chunks)} total")
        except Exception as e:
            logger.error(f"  Embedding batch {batch_num} failed: {type(e).__name__}: {e}")
            raise

    # Step 4: Store in Qdrant
    logger.info("Storing vectors in Qdrant...")
    stored = storage.upsert(all_chunks, all_embeddings)
    logger.info(f"Stored {stored} vectors")

    # Step 5: Verify
    stats = storage.get_stats()
    logger.info(f"Collection stats: {stats}")
    logger.info("Ingestion complete!")

    await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
