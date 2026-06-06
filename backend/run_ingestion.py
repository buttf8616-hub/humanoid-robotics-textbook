#!/usr/bin/env python3
"""Direct ingestion script - bypasses the API server."""
import asyncio
import os
import sys

# Load environment from .env file
from pathlib import Path
env_path = Path(__file__).parent / '.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            value = value.strip('"').strip("'")
            os.environ[key] = value

# Now import the services
from src.services import CrawlerService, ExtractorService, ChunkerService, EmbedderService, StorageService

async def run_ingestion(base_url: str):
    print("=== Starting Direct Ingestion ===")
    print(f"Base URL: {base_url}")

    crawler = CrawlerService(base_url=base_url)
    extractor = ExtractorService()
    chunker = ChunkerService()
    embedder = EmbedderService()
    storage = StorageService()

    # Ensure collection exists
    storage.ensure_collection()
    print("Collection ready")

    # Step 1: Crawl
    print("\n[1/4] Crawling pages...")
    pages = await crawler.crawl_all()
    print(f"Found {len(pages)} pages")

    if len(pages) == 0:
        print("ERROR: No pages found!")
        await crawler.close()
        return False

    all_chunks = []

    # Step 2: Extract and chunk
    print("\n[2/4] Extracting and chunking...")
    for page in pages:
        try:
            extracted = extractor.extract(page.raw_html, page.url)
            chunks = chunker.chunk_page(
                text=extracted.extracted_text,
                source_url=page.url,
                title=extracted.title,
                sections=extracted.sections,
            )
            all_chunks.extend(chunks)
            print(f"  {extracted.title}: {len(chunks)} chunks")
        except Exception as e:
            print(f"  ERROR: {page.url}: {e}")

    print(f"Total chunks: {len(all_chunks)}")

    if len(all_chunks) == 0:
        print("ERROR: No chunks created!")
        await crawler.close()
        return False

    # Step 3: Embed
    print("\n[3/4] Generating embeddings via Cohere API...")
    texts = [chunk.content for chunk in all_chunks]
    embeddings = await embedder.embed_async(texts)
    print(f"Generated {len(embeddings)} embeddings (dimension: {len(embeddings[0])})")

    # Step 4: Store
    print("\n[4/4] Storing in Qdrant...")
    count = storage.upsert(all_chunks, embeddings)
    print(f"Stored {count} vectors")

    # Verify
    from qdrant_client import QdrantClient
    client = QdrantClient(url=os.environ['QDRANT_URL'], api_key=os.environ['QDRANT_API_KEY'])
    info = client.get_collection(os.environ.get('QDRANT_COLLECTION_NAME', 'embedding-book'))

    print(f"\n=== INGESTION COMPLETE ===")
    print(f"Collection: {os.environ.get('QDRANT_COLLECTION_NAME', 'embedding-book')}")
    print(f"Total vectors: {info.points_count}")

    await crawler.close()
    return True

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3001"
    success = asyncio.run(run_ingestion(base_url))
    sys.exit(0 if success else 1)
