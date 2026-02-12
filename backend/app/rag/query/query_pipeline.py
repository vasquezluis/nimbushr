"""
Query Pipeline Entry Point
Run this script to query from the vector database
"""

from dotenv import load_dotenv
from app.settings import settings
from .vector_store import load_vector_store
from .query_engine import retrieve_chunks
from .export_chunks import export_chunks_to_json
from .query_engine import generate_final_answer

# Load environment variables
load_dotenv()


def run_query(query: str):
    """Main entry point for query pipeline."""

    try:
        # Load vector store
        print("Loading vector store...", flush=True)
        db = load_vector_store()

        # Retrieve chunks
        print(f"Retrieving top {settings.top_k_value} chunks...", flush=True)
        chunks = retrieve_chunks(db, query)

        if not chunks:
            return {
                "answer": "No relevant documents found for your query.",
                "sources": [],
                "num_chunks": 0,
            }

        # Export chunks
        # export_chunks_to_json(chunks)

        # Rerank if enabled
        if settings.use_reranking:
            from .query_engine import rerank_chunks

            chunks = rerank_chunks(chunks, query)

        # Generate answer
        answer = generate_final_answer(chunks, query)

        # Extract source information
        sources = []
        for chunk in chunks:
            source_info = {
                "file": chunk.metadata.get("source_file", "Unknown"),
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "has_tables": chunk.metadata.get("has_tables", False),
                "has_images": chunk.metadata.get("has_images", False),
                "ai_summarized": chunk.metadata.get("ai_summarized", False),
            }
            sources.append(source_info)

        return {
            "answer": answer,
            "sources": sources,
            "num_chunks": len(chunks),
            "chunks_reranked": settings.use_reranking,
        }

    except Exception as e:
        print(f"Query pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        return {
            "answer": f"Error processing query: {str(e)}",
            "sources": [],
            "num_chunks": 0,
        }


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv

    load_dotenv()

    print("\n" + "=" * 70)
    print("RAG QUERY TEST")
    print("=" * 70)

    result = run_query("What are the workspace requirements?")

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)
    for i, source in enumerate(result["sources"], 1):
        print(f"{i}. {source['file']} (chunk {source['chunk_index']})")
        if source["ai_summarized"]:
            print(f"   - AI-summarized content")
        if source["has_tables"]:
            print(f"   - Contains tables")
        if source["has_images"]:
            print(f"   - Contains images")

    print("=" * 70)
