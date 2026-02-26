"""
Ingestion Pipeline
Orchestrates the complete RAG ingestion for PDFs and Excel/CSV files.
"""

from typing import List

from langchain_core.documents import Document

from app.rag.ingest.ai_summarizer import summarise_chunks
from app.rag.ingest.document_processor import create_chunks_by_title
from app.rag.ingest.excel_document_processor import create_excel_documents
from app.rag.ingest.text_document_processor import create_text_documents
from app.rag.ingest.vector_store import create_vector_store
from app.rag.loaders.excel_loader import load_excel_files_from_directory
from app.rag.loaders.pdf_loader import load_pdfs_from_directory
from app.rag.loaders.text_loader import load_text_files_from_directory
from app.settings import settings


def run_complete_ingestion_pipeline() -> object:
    """
    Run the complete RAG ingestion pipeline.

    Process flow:
    1. Load all PDFs  → unstructured elements → chunk_by_title → AI summarise
    2. Load all Excel/CSV → sheet rows → row-batch chunks (no AI summarise needed,
       tabular data is already structured)
    3. Store everything in the vector database.

    Returns:
        ChromaDB vectorstore instance
    """
    print("🚀 Starting RAG Ingestion Pipeline")
    print("=" * 50)

    all_documents: List[Document] = []

    # ── PDFs ──────────────────────────────────────────────────────────────────
    pdfs = load_pdfs_from_directory()

    if pdfs:
        print(f"\nProcessing {len(pdfs)} PDF file(s)...")
        for filename, elements in pdfs.items():
            print(f"\n  PDF: {filename} ({len(elements)} elements)")

            chunks = create_chunks_by_title(elements)
            summarised_chunks = summarise_chunks(chunks)

            for doc in summarised_chunks:
                doc.metadata["source_file"] = filename
                doc.metadata["source_type"] = "pdf"

            all_documents.extend(summarised_chunks)
            print(f"  → {len(summarised_chunks)} chunks")
    else:
        print("No PDF files found — skipping PDF ingestion.")

    # ── Excel / CSV ───────────────────────────────────────────────────────────
    excel_files = load_excel_files_from_directory(settings.excel_data_dir)

    if excel_files:
        print(f"\nProcessing {len(excel_files)} Excel/CSV file(s)...")
        for filename, sheets in excel_files.items():
            print(f"\n  Excel: {filename} ({len(sheets)} sheet(s))")

            docs = create_excel_documents(sheets, filename)
            all_documents.extend(docs)
    else:
        print("No Excel/CSV files found — skipping Excel ingestion.")

    # ── Text / Markdown ───────────────────────────────────────────────────────
    text_files = load_text_files_from_directory(settings.text_data_dir)

    if text_files:
        print(f"\nProcessing {len(text_files)} text/markdown file(s)...")
        text_docs = create_text_documents(text_files)
        all_documents.extend(text_docs)
    else:
        print("No .txt / .md files found — skipping text ingestion.")

    # ── Guard ─────────────────────────────────────────────────────────────────
    if not all_documents:
        raise ValueError(
            "No documents found to process! Add PDF or Excel files to the data directory."
        )

    # ── Vector Store ──────────────────────────────────────────────────────────
    print(f"\nTotal documents to index: {len(all_documents)}")
    db = create_vector_store(all_documents)

    print(f"\n✅ Vector store created with {len(all_documents)} chunks")
    return db
