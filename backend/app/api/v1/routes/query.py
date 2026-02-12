from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_db
from app.rag.query.query_pipeline import run_query

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
