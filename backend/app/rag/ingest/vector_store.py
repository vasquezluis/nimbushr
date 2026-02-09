"""
Vector Store Module
Handles ChromaDB vector store creation and operations
"""

from typing import List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def create_vector_store(
    documents: List[Document], persist_directory: str = "chroma_db"
) -> Chroma:
    """
    Create and persist ChromaDB vector store.

    Args:
        documents: List of LangChain Document objects to store
        persist_directory: Directory path to persist the vector store

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
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )
    print("--- Finished creating vector store ---")

    print(f"✅ Vector store created and saved to {persist_directory}")
    return vectorstore
