from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.routes import files, query
from app.limiter import limiter
from app.rag.graph.knowledge_graph import load_graph
from app.rag.query.vector_store import load_vector_store

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading vector store at startup...")
    app.state.db = load_vector_store()

    print("Loading knowledge graph at startup...")
    app.state.graph = load_graph()

    yield

    print("Shutting down application...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG API",
        version="1.0.2",
        lifespan=lifespan,
    )

    # Rate limiter state and error handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js default port
            "http://127.0.0.1:3000",
            "http://localhost:3001",  # Alternative port
        ],
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    app.include_router(query.router, prefix="/api/v1")
    app.include_router(files.router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
