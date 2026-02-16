"""
Query Engine Module
Handles RAG queries, retrieval, and answer generation
"""

from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma
from app.settings import settings


def retrieve_chunks(vectorstore: Chroma, query: str) -> List:
    """
    Retrieve relevant chunks from the vector store.

    Args:
        vectorstore: ChromaDB vector store instance
        query: Query string to search for

    Returns:
        List of retrieved document chunks
    """
    print(f"Retrieving top {settings.top_k_chunks} chunks for query: {query}")

    if settings.use_mmr:
        # Use MMR for diverse results (reduces redundancy)
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.top_k_chunks,
                "fetch_k": settings.top_k_chunks * 3,  # Fetch more, then filter
                "lambda_mult": settings.mmr_lambda,  # Balance between relevance and diversity
            },
        )
    else:
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": settings.top_k_chunks,
                "score_threshold": 0.5,
            },  # filter low relevance chunks
        )

    chunks = retriever.invoke(query)
    print(f"Retrieved {len(chunks)} chunks")

    # Log relevance scores if available
    if hasattr(chunks[0], "metadata") and "score" in chunks[0].metadata:
        for i, chunk in enumerate(chunks):
            score = chunk.metadata.get("score", "N/A")
            print(f"  Chunk {i+1} score: {score}")

    return chunks


def rerank_chunks(chunks: List, query: str, top_n: int = None) -> List:
    """
    Rerank retrieved chunks using cross-encoder for better relevance.

    Args:
        chunks: Retrieved chunks
        query: Original query
        top_n: Number of top chunks to return (default: all)

    Returns:
        Reranked list of chunks
    """
    if not chunks:
        return chunks

    try:
        from sentence_transformers import CrossEncoder

        # Load cross-encoder model for reranking
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        # Prepare pairs for scoring
        pairs = [[query, chunk.page_content] for chunk in chunks]

        # Get relevance scores
        scores = model.predict(pairs)

        # Sort chunks by score
        ranked_indices = scores.argsort()[::-1]
        reranked_chunks = [chunks[idx] for idx in ranked_indices]

        # Optionally limit to top_n
        if top_n:
            reranked_chunks = reranked_chunks[:top_n]

        print(f"Reranked {len(reranked_chunks)} chunks")
        for i, idx in enumerate(ranked_indices[: len(reranked_chunks)]):
            print(f"  Rank {i+1}: Score {scores[idx]:.4f}")

        return reranked_chunks

    except ImportError:
        print("sentence-transformers not installed, skipping reranking")
        print("Install with: pip install sentence-transformers")
        return chunks
    except Exception as e:
        print(f"Reranking failed, using original order: {e}")
        return chunks


def generate_final_answer(chunks: List, query: str) -> str:
    """
    Generate final answer using multimodal content from retrieved chunks.

    Args:
        chunks: List of retrieved document chunks
        query: Original query string
        max_context_length: Maximum characters for context (prevents token overflow)

    Returns:
        Generated answer as string
    """
    try:
        # Initialize LLM (needs vision model for images)
        llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

        # Build context with length management
        context_parts = []
        current_length = 0
        chunks_used = 0

        for i, chunk in enumerate(chunks):
            source_file = chunk.metadata.get("source_file", "Unknown")
            chunk_index = chunk.metadata.get("chunk_index", "?")
            ai_summarized = chunk.metadata.get("ai_summarized", False)
            has_tables = chunk.metadata.get("has_tables", False)
            has_images = chunk.metadata.get("has_images", False)
            num_tables = chunk.metadata.get("num_tables", 0)
            num_images = chunk.metadata.get("num_images", 0)

            # Build context header
            context_header = (
                f"--- Document {i+1} (Source: {source_file}, Chunk: {chunk_index}) ---"
            )

            # Add content type indicators
            content_indicators = []

            if has_tables:
                content_indicators.append(f"{num_tables} table(s)")
            if has_images:
                content_indicators.append(f"{num_images} image(s)")

            if content_indicators:
                context_header += f"\n[Contains: {', '.join(content_indicators)}]"

            if ai_summarized:
                context_header += "\n[AI-enhanced summary of multimodal content]"

            chunk_text = f"{context_header}\n\n{chunk.page_content}\n"
            chunk_length = len(chunk_text)

            # Add the enhanced content
            context_parts.append(f"{context_header}\n\n{chunk.page_content}\n")

            # Check if adding this chunk would exceed limit
            if current_length + chunk_length > settings.max_context_length:
                print(
                    f"Context limit reached at chunk {i+1}, using {chunks_used} chunks"
                )
                break

        # Combine all context
        full_context = "\n".join(context_parts)

        # Build the text prompt
        prompt_text = f"""Based on the following documents, please answer this question: {query}

RETRIEVED DOCUMENTS:
{full_context}

INSTRUCTIONS:
- Provide a clear, comprehensive answer using the information above
- If documents contain tables or images, their content has been analyzed and included
- Cite specific sources by filename when referencing information
- If information is insufficient, clearly state this and explain what's missing
- Be specific and use concrete details from the documents
- If you find conflicting information, acknowledge it and explain the differences

ANSWER:"""

        # Send to AI and get response
        message = HumanMessage(content=prompt_text)
        response = llm.invoke([message])

        return response.content

    except Exception as e:
        print(f"Answer generation failed: {e}")
        import traceback

        traceback.print_exc()
        return "Sorry, I encountered an error while generating the answer."
