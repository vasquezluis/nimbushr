"""
Document Processing Module
Handles chunking operations
"""

from unstructured.chunking.title import chunk_by_title


def create_chunks_by_title(elements):
    """
    Create intelligent chunks using title-based strategy.

    Args:
        elements: Parsed PDF elements from partition_document

    Returns:
        List of chunked elements
    """
    print("🔨 Creating smart chunks...")

    chunks = chunk_by_title(
        elements,
        max_characters=3000,  # Hard limit - never exceed 3000 characters per chunk
        new_after_n_chars=2400,  # Try to start a new chunk after 2400 characters
        combine_text_under_n_chars=500,  # Merge tiny chunks under 500 chars
    )

    print(f"✅ Created {len(chunks)} chunks")
    return chunks
