"""
Streaming Query Engine Module 
Handles RAG queries with real-time token streaming and metadata
"""

from typing import List, AsyncGenerator, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma
from app.settings import settings


async def retrieve_chunks_async(vectorstore: Chroma, query: str) -> List:
    """
    Retrieve relevant chunks from the vector store (async version).

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
                "fetch_k": settings.top_k_chunks * 3,
                "lambda_mult": settings.mmr_lambda,
            },
        )
    else:
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": settings.top_k_chunks,
                "score_threshold": 0.5,
            },
        )

    # Use ainvoke for async retrieval
    chunks = await retriever.ainvoke(query)
    print(f"Retrieved {len(chunks)} chunks")

    return chunks


async def rerank_chunks_async(chunks: List, query: str, top_n: int = None) -> List:
    """
    Rerank retrieved chunks using cross-encoder (async version).

    Args:
        chunks: Retrieved chunks
        query: Original query
        top_n: Number of top chunks to return

    Returns:
        Reranked list of chunks
    """
    if not chunks:
        return chunks

    try:
        from sentence_transformers import CrossEncoder

        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [[query, chunk.page_content] for chunk in chunks]
        scores = model.predict(pairs)
        ranked_indices = scores.argsort()[::-1]
        reranked_chunks = [chunks[idx] for idx in ranked_indices]

        if top_n:
            reranked_chunks = reranked_chunks[:top_n]

        print(f"Reranked {len(reranked_chunks)} chunks")
        return reranked_chunks

    except ImportError:
        print("sentence-transformers not installed, skipping reranking")
        return chunks
    except Exception as e:
        print(f"Reranking failed: {e}")
        return chunks


def build_context_from_chunks(chunks: List) -> tuple[str, List[Dict[str, Any]]]:
    """
    Build context string from chunks and extract source metadata.

    Args:
        chunks: List of retrieved document chunks

    Returns:
        Tuple of (context_string, sources_list)
    """
    context_parts = []
    sources = []
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

        # Build context header
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
            print(f"Context limit reached at chunk {i+1}, using {chunks_used} chunks")
            break

        context_parts.append(chunk_text)
        current_length += chunk_length
        chunks_used += 1

        # Track source metadata
        source_info = {
            "file": source_file,
            "section": section_title,
            "page": page_number,
            "page_span": page_span,
            "chunk_index": chunk_index,
            "has_tables": has_tables,
            "has_images": has_images,
            "ai_summarized": ai_summarized,
        }
        sources.append(source_info)

    full_context = "\n".join(context_parts)
    return full_context, sources


async def stream_answer(
    chunks: List, query: str
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream answer tokens in real-time from the LLM.

    Args:
        chunks: List of retrieved document chunks
        query: Original query string

    Yields:
        Dictionary with streaming events:
        - {"type": "sources", "data": [...]} - Source information
        - {"type": "token", "data": "..."} - Individual token
        - {"type": "done", "data": None} - Streaming complete
    """

    try:
        # Build context and get sources
        full_context, sources = build_context_from_chunks(chunks)

        # First, yield source information
        yield {"type": "sources", "data": sources, "num_chunks": len(chunks)}

        # Initialize streaming LLM
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            streaming=True,  # Enable streaming
        )

        # Build the prompt with citation instructions
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

        message = HumanMessage(content=prompt_text)

        # Stream tokens from the LLM
        async for chunk in llm.astream([message]):
            if chunk.content:
                yield {"type": "token", "data": chunk.content}

        # Signal completion
        yield {"type": "done", "data": None}

    except Exception as e:
        print(f"Streaming failed: {e}")
        import traceback

        traceback.print_exc()
        yield {
            "type": "error",
            "data": f"Error generating answer: {str(e)}",
        }
