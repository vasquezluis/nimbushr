"""
Ingestion Pipeline
Orchestrates the complete RAG ingestion
"""

from loaders.pdf_loader import load_pdfs_from_directory
from .document_processor import create_chunks_by_title
from .ai_summarizer import summarise_chunks
from .vector_store import create_vector_store


def run_complete_ingestion_pipeline(persist_directory: str = "chroma_db"):
    """
    Run the complete RAG ingestion pipeline.

    Args:
        persist_directory: Directory to persist the vector store

    Returns:
        ChromaDB vectorstore instance
    """

    print("🚀 Starting RAG Ingestion Pipeline")
    print("=" * 50)

    # Step 1: Partition
    # excels = partition_document(pdf_path)
    pdfs = load_pdfs_from_directory()
    for filename, elements in pdfs.items():
        print(f"{filename}: {len(elements)} elements")
    # texts = partition_document(pdf_path)

    # Step 2: Chunk
    chunks = create_chunks_by_title(elements)

    # Step 3: AI Summarisation
    summarised_chunks = summarise_chunks(chunks)

    # Step 4: Vector Store
    db = create_vector_store(summarised_chunks, persist_directory=persist_directory)

    print("🎉 Pipeline completed successfully!")
    return db
