"""
Streaming Query Pipeline
Handles RAG queries with real-time token streaming
"""

from typing import AsyncGenerator, Dict, Any
from langchain_chroma import Chroma
from app.settings import settings
from .streaming_query_engine import (
    retrieve_chunks_async,
    rerank_chunks_async,
    stream_answer,
)


async def run_streaming_query(
    query: str, db: Chroma
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Run streaming query pipeline that yields tokens in real-time.

    Args:
        query: User query string
        db: ChromaDB vector store instance

    Yields:
        Dictionary events:
        - {"type": "status", "data": "..."} - Status updates
        - {"type": "sources", "data": [...]} - Source information
        - {"type": "token", "data": "..."} - Answer tokens
        - {"type": "done", "data": None} - Completion signal
        - {"type": "error", "data": "..."} - Error information
    """
    try:
        # Status update: Starting retrieval
        yield {"type": "status", "data": "Retrieving relevant documents..."}

        # Retrieve chunks
        chunks = await retrieve_chunks_async(db, query)

        if not chunks:
            yield {
                "type": "error",
                "data": "No relevant documents found for your query.",
            }
            return

        # Status update: Reranking
        if settings.use_reranking:
            yield {"type": "status", "data": "Reranking results..."}
            chunks = await rerank_chunks_async(chunks, query)

        # Status update: Generating answer
        yield {"type": "status", "data": "Generating answer..."}

        # Stream the answer (includes sources, tokens, and done events)
        async for event in stream_answer(chunks, query):
            yield event

    except Exception as e:
        print(f"Streaming query pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        yield {"type": "error", "data": f"Error processing query: {str(e)}"}
