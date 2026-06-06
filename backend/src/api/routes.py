"""FastAPI route definitions."""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

from cohere.core.api_error import ApiError as CohereApiError
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from src.config import settings
from src.models import IngestionJob, JobStatus, IngestionError
from src.services import (
    CrawlerService,
    ExtractorService,
    ChunkerService,
    EmbedderService,
    StorageService,
    RetrieverService,
)
from src.agent import AgentService
from .schemas import (
    IngestRequest,
    IngestResponse,
    JobStatusResponse,
    VerifyResponse,
    UrlVerifyResponse,
    ChunkDetail,
    ErrorDetail,
    SearchRequest,
    SearchResponseSchema,
    RetrievalResultResponse,
    ErrorResponse,
    ChatRequest,
    ChatResponse,
    SourceCitationResponse,
    TokenUsage,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory job store (in production, use Redis or database)
_jobs: dict[str, IngestionJob] = {}


def get_storage() -> StorageService:
    """Get storage service instance."""
    return StorageService()


async def run_ingestion(job_id: str, base_url: str, force: bool = False) -> None:  # noqa: RUF029
    """Run the full ingestion pipeline.

    Args:
        job_id: Job identifier.
        base_url: Base URL to crawl.
        force: Force re-ingestion.
    """
    job = _jobs.get(job_id)
    if not job:
        return

    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow()

    try:
        # Initialize services
        crawler = CrawlerService(base_url=base_url)
        extractor = ExtractorService()
        chunker = ChunkerService()
        embedder = EmbedderService()
        storage = StorageService()

        # Ensure collection exists
        storage.ensure_collection()

        # Step 1: Crawl pages
        logger.info(f"Job {job_id}: Starting crawl of {base_url}")
        pages = await crawler.crawl_all()
        job.pages_total = len(pages)
        logger.info(f"Job {job_id}: Found {len(pages)} pages")

        all_chunks = []

        # Step 2: Extract and chunk each page
        for page in pages:
            try:
                # Extract text
                extracted = extractor.extract(page.raw_html, page.url)

                # Chunk the text
                chunks = chunker.chunk_page(
                    text=extracted.extracted_text,
                    source_url=page.url,
                    title=extracted.title,
                    sections=extracted.sections,
                )

                all_chunks.extend(chunks)
                job.pages_processed += 1

            except Exception as e:
                logger.error(f"Error processing {page.url}: {e}")
                job.errors.append(
                    IngestionError(
                        url=page.url,
                        error_type="extraction_error",
                        message=str(e),
                    )
                )

        logger.info(f"Job {job_id}: Created {len(all_chunks)} chunks")

        # Step 3: Generate embeddings
        if all_chunks:
            logger.info(f"Job {job_id}: Generating embeddings")
            embeddings = await embedder.embed_async(all_chunks)

            # Step 4: Store in Qdrant
            logger.info(f"Job {job_id}: Storing vectors")
            stored = storage.upsert(all_chunks, embeddings)
            job.chunks_created = stored

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        logger.info(f"Job {job_id}: Completed successfully")

        # Cleanup
        await crawler.close()

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.errors.append(
            IngestionError(
                url=base_url,
                error_type="pipeline_error",
                message=str(e),
            )
        )


@router.post("/ingest", response_model=IngestResponse, status_code=202)
async def trigger_ingestion(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
) -> IngestResponse:
    """Trigger book ingestion.

    Starts an asynchronous ingestion job for the specified book URL.
    """
    # Check for running jobs
    running_jobs = [j for j in _jobs.values() if j.status == JobStatus.RUNNING]
    if running_jobs:
        raise HTTPException(
            status_code=503,
            detail="Another ingestion job is already running",
        )

    # Create new job
    job_id = str(uuid.uuid4())
    job = IngestionJob(job_id=job_id)
    _jobs[job_id] = job

    # Start ingestion in background
    background_tasks.add_task(run_ingestion, job_id, request.base_url, request.force)

    return IngestResponse(
        job_id=job_id,
        status="pending",
        message="Ingestion job started",
    )


@router.get("/ingest/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get the status of an ingestion job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        started_at=job.started_at,
        completed_at=job.completed_at,
        pages_total=job.pages_total,
        pages_processed=job.pages_processed,
        chunks_created=job.chunks_created,
        errors=[
            ErrorDetail(
                url=e.url,
                error_type=e.error_type,
                message=e.message,
                timestamp=e.timestamp,
            )
            for e in job.errors
        ],
    )


@router.get("/verify", response_model=VerifyResponse)
async def verify_collection() -> VerifyResponse:
    """Get collection statistics."""
    storage = get_storage()

    try:
        stats = storage.get_stats()
        urls = storage.get_unique_urls()

        return VerifyResponse(
            collection_name=stats["collection_name"],
            vector_count=stats["vector_count"],
            indexed_urls=len(urls),
            status=stats["status"],
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/verify/url", response_model=UrlVerifyResponse)
async def verify_url(
    url: str = Query(..., description="URL to verify"),
) -> UrlVerifyResponse:
    """Get chunks for a specific URL."""
    storage = get_storage()

    chunks = storage.get_chunks_by_url(url)
    if not chunks:
        raise HTTPException(status_code=404, detail="URL not found in collection")

    return UrlVerifyResponse(
        url=url,
        chunk_count=len(chunks),
        chunks=[
            ChunkDetail(
                chunk_index=c.get("chunk_index", 0),
                section=c.get("section", ""),
                token_count=0,  # Not stored in payload
                content_preview=c.get("content", "")[:200],
            )
            for c in chunks
        ],
    )


# Retrieval endpoints
def get_retriever() -> RetrieverService:
    """Get retriever service instance."""
    return RetrieverService()


@router.post("/search", response_model=SearchResponseSchema)
async def search(request: SearchRequest) -> SearchResponseSchema:
    """Search for relevant book content.

    Performs semantic search over stored book embeddings.
    Converts query to embedding, searches Qdrant, and returns relevant chunks.
    """
    # Validate empty query
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": "Query must not be empty",
                "details": {"field": "query"},
            },
        )

    retriever = get_retriever()

    try:
        response = await retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            url_filter=request.url_filter,
            section_filter=request.section_filter,
        )

        logger.info(
            f"Search completed: query='{request.query[:30]}...', "
            f"results={response.total_count}, latency={response.latency_ms:.2f}ms"
        )

        return SearchResponseSchema(
            results=[
                RetrievalResultResponse(
                    content=r.content,
                    url=r.url,
                    title=r.title,
                    section=r.section,
                    chunk_index=r.chunk_index,
                    score=r.score,
                )
                for r in response.results
            ],
            total_count=response.total_count,
            latency_ms=response.latency_ms,
            filters_applied=response.filters_applied,
        )

    except ValueError as e:
        # Validation errors (empty query, invalid top_k)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e),
            },
        )

    except CohereApiError as e:
        # Cohere embedding service error
        logger.error(f"Cohere API error during search: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "Embedding service temporarily unavailable",
                "details": {"service": "cohere", "retry_after": 5},
            },
        )

    except Exception as e:
        # Qdrant or other service errors
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "Search service temporarily unavailable",
                "details": {"service": "qdrant", "retry_after": 5},
            },
        )


# Agent/Chat endpoints
def get_agent() -> AgentService:
    """Get agent service instance."""
    return AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat with the AI agent about the textbook.

    The agent retrieves relevant content and generates grounded answers
    with source citations.
    """
    # Validate empty query
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": "Question must not be empty",
                "details": {"field": "question"},
            },
        )

    agent = get_agent()

    # Extract selected_context filters if provided
    url_filter = None
    section_filter = None
    if request.selected_context:
        url_filter = request.selected_context.url
        section_filter = request.selected_context.section

    # Extract conversation history if provided
    conversation_history = None
    if request.conversation_history:
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

    try:
        result = await agent.answer(
            question=request.question,
            top_k=request.top_k,
            url_filter=url_filter,
            section_filter=section_filter,
            conversation_history=conversation_history,
        )

        logger.info(
            f"Chat completed: question='{request.question[:30]}...', "
            f"sources={len(result['sources'])}, "
            f"confidence={result['confidence']}, "
            f"latency={result['latency_ms']:.2f}ms"
        )

        return ChatResponse(
            answer=result["answer"],
            sources=[
                SourceCitationResponse(
                    url=s["url"],
                    title=s["title"],
                    section=s["section"],
                    chunk_index=s["chunk_index"],
                    score=s["score"],
                    excerpt=s["excerpt"],
                )
                for s in result["sources"]
            ],
            confidence=result["confidence"],
            latency_ms=result["latency_ms"],
            tokens_used=TokenUsage(
                prompt=result["tokens_used"]["prompt"],
                completion=result["tokens_used"]["completion"],
                total=result["tokens_used"]["total"],
            ),
        )

    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "AI agent service temporarily unavailable",
                "details": {"service": "groq", "retry_after": 5},
            },
        )
