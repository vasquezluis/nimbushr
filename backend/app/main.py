from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.rag.query.vector_store import load_vector_store
from app.api.v1.routes import query, files

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading vector store at startup...")
    app.state.db = load_vector_store()

    yield

    print("Shutting down application...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG API",
        version="1.0.1",
        lifespan=lifespan,
    )

    app.include_router(query.router, prefix="/api/v1")
    app.include_router(files.router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
