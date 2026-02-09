"""
AI Summarization Module
Handles AI-enhanced content summarization using multimodal LLM
"""

import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

from settings import settings
from .content_analyzer import separate_content_types


def should_use_ai_summary(content_data):
    """Only use AI for complex multimodal content"""
    has_multiple_tables = len(content_data["tables"]) > 2
    has_images = len(content_data["images"]) > 0
    is_complex = has_multiple_tables or has_images
    return is_complex


def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str:
    """
    Create AI-enhanced summary for mixed content.

    Args:
        text: Text content from the chunk
        tables: List of HTML table strings
        images: List of base64 encoded images

    Returns:
        Enhanced, searchable description of the content
    """
    try:
        # Initialize LLM (needs vision model for images)
        llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)

        # Build the text prompt
        prompt_text = f"""You are creating a searchable description for document content retrieval.

        CONTENT TO ANALYZE:
        TEXT CONTENT:
        {text}

        """

        # Add tables if present
        if tables:
            prompt_text += "TABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"Table {i+1}:\n{table}\n\n"

        prompt_text += """
        YOUR TASK:
        Generate a comprehensive, searchable description that covers:

        1. Key facts, numbers, and data points from text and tables
        2. Main topics and concepts discussed  
        3. Questions this content could answer
        4. Visual content analysis (charts, diagrams, patterns in images)
        5. Alternative search terms users might use

        Make it detailed and searchable - prioritize findability over brevity.

        SEARCHABLE DESCRIPTION:"""

        # Build message content starting with text
        message_content = [{"type": "text", "text": prompt_text}]

        # Add images to the message
        for image_base64 in images:
            message_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                }
            )

        # Send to AI and get response
        message = HumanMessage(content=message_content)
        response = llm.invoke([message])

        return response.content

    except Exception as e:
        print(f"AI summary failed: {e}")
        # Fallback to simple summary
        summary = f"{text[:300]}..."
        if tables:
            summary += f" [Contains {len(tables)} table(s)]"
        if images:
            summary += f" [Contains {len(images)} image(s)]"
        return summary


def summarise_chunks(chunks) -> List[Document]:
    """
    Process all chunks with AI Summaries.

    Args:
        chunks: List of chunked elements to process

    Returns:
        List of LangChain Document objects with enhanced content and metadata
    """
    print("Processing chunks with AI Summaries...")

    langchain_documents = []
    total_chunks = len(chunks)

    # Track AI summarization usage
    ai_summary_count = 0

    for i, chunk in enumerate(chunks):
        current_chunk = i + 1

        # Analyze chunk content
        content_data = separate_content_types(chunk)

        num_tables = len(content_data["tables"])
        num_images = len(content_data["images"])

        # Determine if AI summarization should be used
        should_summarize = settings.should_use_ai_summary(num_tables, num_images)

        # Create enhanced content based on settings
        if should_summarize:
            print(
                f"[{current_chunk}/{total_chunks}] AI summarizing (tables={num_tables}, images={num_images})"
            )

            try:
                enhanced_content = create_ai_enhanced_summary(
                    content_data["text"], content_data["tables"], content_data["images"]
                )
                ai_summary_count += 1
            except Exception as e:
                print(f"AI summary failed, using raw text: {e}")
                enhanced_content = content_data["text"]
        else:
            print(
                f"[{current_chunk}/{total_chunks}] Using raw text (tables={num_tables}, images={num_images})"
            )
            enhanced_content = content_data["text"]

        # Create LangChain Document with rich metadata
        doc = Document(
            page_content=enhanced_content,
            metadata={
                "chunk_index": i,
                "has_tables": num_tables > 0,
                "has_images": num_images > 0,
                "num_tables": num_tables,
                "num_images": num_images,
                "ai_summarized": should_summarize,
                "content_types": ",".join(content_data["types"]),
                "original_content": json.dumps(
                    {
                        "raw_text": content_data["text"],
                        "tables_html": content_data["tables"],
                        "images_base64": content_data["images"],
                    }
                ),
            },
        )

        langchain_documents.append(doc)

    print(f"\nProcessed {len(langchain_documents)} chunks")
    if settings.use_ai_summarization:
        print(f"AI summaries: {ai_summary_count}/{total_chunks} chunks")
        print(f"Cost estimate: ~${ai_summary_count * 0.02:.2f} (rough)")

    return langchain_documents
