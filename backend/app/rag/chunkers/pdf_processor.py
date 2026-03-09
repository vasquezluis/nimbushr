"""
Document Processing Module
Handles chunking operations
"""

from typing import List
from app.settings import settings
from unstructured.chunking.title import chunk_by_title


def create_chunks_by_title(elements) -> List:
    """
    Create intelligent chunks using title-based strategy.

    Args:
        elements: Parsed PDF elements from partition_document

    Returns:
        List of chunked elements
    """
    print("Creating smart chunks...")

    chunk_config = settings.get_chunk_config()

    chunks = chunk_by_title(
        elements,
        max_characters=chunk_config["max_characters"],
        new_after_n_chars=chunk_config["new_after_n_chars"],
        combine_text_under_n_chars=chunk_config["combine_text_under_n_chars"],
    )

    print(f"Created {len(chunks)} chunks")
    return chunks
