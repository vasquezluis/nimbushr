from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from app.api.deps import get_db
from app.rag.query.query_pipeline import run_query
from app.rag.query.streaming_query_pipeline import run_streaming_query


router = APIRouter(tags=["RAG"])


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: list
    num_chunks: int
    chunks_reranked: bool | None = None


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    db=Depends(get_db),
):
    return run_query(request.query, db)


@router.post("/query/stream")
async def query_rag_stream(
    request: QueryRequest,
    db=Depends(get_db),
):
    """
    Streaming query endpoint using Server-Sent Events (SSE).
    Returns tokens in real-time as they're generated.

    Event types:
    - status: Processing status updates
    - sources: Retrieved source documents metadata
    - token: Individual answer tokens
    - done: Streaming complete
    - error: Error occurred
    """

    async def event_generator():
        """Generate Server-Sent Events from the streaming pipeline."""
        try:
            async for event in run_streaming_query(request.query, db):
                # Format as SSE: data: {json}\n\n
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            error_event = {"type": "error", "data": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
