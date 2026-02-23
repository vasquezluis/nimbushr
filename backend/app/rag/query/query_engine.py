"""
Query Engine Module - IMPROVED
Handles RAG queries, retrieval, and answer generation with enhanced metadata
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
    Includes metadata (section titles, page numbers) in context.

    Args:
        chunks: List of retrieved document chunks
        query: Original query string

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
            # Extract metadata
            source_file = chunk.metadata.get("source_file", "Unknown")
            chunk_index = chunk.metadata.get("chunk_index", "?")
            section_title = chunk.metadata.get("section_title", "Unknown Section")
            page_number = chunk.metadata.get("page_number")
            page_span = chunk.metadata.get("page_span")
            ai_summarized = chunk.metadata.get("ai_summarized", False)
            has_tables = chunk.metadata.get("has_tables", False)
            has_images = chunk.metadata.get("has_images", False)

            # Build enhanced context header with section and page info
            context_header = f"--- Document {i+1} ---"
            context_header += f"\nSource: {source_file}"
            context_header += f"\nSection: {section_title}"

            # Add page information
            if page_span:
                context_header += f"\nPages: {page_span}"
            elif page_number:
                context_header += f"\nPage: {page_number}"

            context_header += f"\nChunk: {chunk_index}"

            # Add content type indicators
            content_indicators = []
            if has_tables:
                content_indicators.append("tables")
            if has_images:
                content_indicators.append("images")

            if content_indicators:
                context_header += f"\n[Contains: {', '.join(content_indicators)}]"

            if ai_summarized:
                context_header += "\n[AI-enhanced summary]"

            chunk_text = f"{context_header}\n\n{chunk.page_content}\n"
            chunk_length = len(chunk_text)

            # Check if adding this chunk would exceed limit
            if current_length + chunk_length > settings.max_context_length:
                print(
                    f"Context limit reached at chunk {i+1}, using {chunks_used} chunks"
                )
                break

            # Add the enhanced content
            context_parts.append(chunk_text)
            current_length += chunk_length
            chunks_used += 1

        # Combine all context
        full_context = "\n".join(context_parts)

        # Build the text prompt with enhanced citation instructions
        prompt_text = f"""Based on the following documents, please answer this question: {query}

RETRIEVED DOCUMENTS:
{full_context}

INSTRUCTIONS:
- Provide a clear, comprehensive answer using the information above
- When citing information, include the source file, section name, and page number
  Example: "According to the Employee Handbook (Benefits Section, Page 15)..."
- If documents contain tables or images, their content has been analyzed and included
- Be specific and use concrete details from the documents
- If information is insufficient, clearly state this and explain what's missing
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
