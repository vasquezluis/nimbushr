"""
Vector Store Module
Handles ChromaDB vector store creation and operations
"""

from typing import List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from settings import settings


def create_vector_store(documents: List[Document]) -> Chroma:
    """
    Create and persist ChromaDB vector store.

    Args:
        documents: List of LangChain Document objects to store

    Returns:
        ChromaDB vectorstore instance
    """
    print("🔮 Creating embeddings and storing in ChromaDB...")

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # Create ChromaDB vector store
    print("--- Creating vector store ---")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=settings.vector_db_dir,
        collection_name=settings.chroma_collection_name,
        collection_metadata={"hnsw:space": settings.chroma_distance_metric},
    )
    print("--- Finished creating vector store ---")

    return vectorstore
