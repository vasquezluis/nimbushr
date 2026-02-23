"""
Content Analysis Module
Handles content type separation and analysis
"""

from typing import Dict, Optional, List


def extract_section_title(chunk) -> Optional[str]:
    """
    Extract the section title that this chunk belongs to.

    Args:
        chunk: A chunked element to analyze

    Returns:
        The section title as string, or None if no title found
    """
    if not (hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements")):
        return None

    titles = []
    for element in chunk.metadata.orig_elements:
        # Check if element is a Title
        if hasattr(element, "category") and element.category == "Title":
            titles.append(element.text)

    # Return the last title (most recent section heading before content)
    return titles[-1] if titles else None


def extract_page_number(chunk) -> Optional[int]:
    """
    Extract the page number from chunk metadata.

    Args:
        chunk: A chunked element to analyze

    Returns:
        Page number as integer, or None if not available
    """
    # Check for page_number in chunk's own metadata
    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "page_number"):
        return chunk.metadata.page_number

    # Check in original elements
    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
        for element in chunk.metadata.orig_elements:
            if hasattr(element, "metadata") and hasattr(
                element.metadata, "page_number"
            ):
                return element.metadata.page_number

    return None


def extract_all_page_numbers(chunk) -> List[int]:
    """
    Extract all unique page numbers that this chunk spans.

    Args:
        chunk: A chunked element to analyze

    Returns:
        List of page numbers (sorted, unique)
    """
    page_numbers = set()

    # Check chunk's own metadata
    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "page_number"):
        page_numbers.add(chunk.metadata.page_number)

    # Check all original elements
    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
        for element in chunk.metadata.orig_elements:
            if hasattr(element, "metadata") and hasattr(
                element.metadata, "page_number"
            ):
                page_numbers.add(element.metadata.page_number)

    return sorted(list(page_numbers))


def separate_content_types(chunk) -> Dict:
    """
    Analyze what types of content are in a chunk.

    Args:
        chunk: A chunked element to analyze

    Returns:
        Dictionary containing text, tables, images, content types, title, and page info
    """
    content_data = {
        "text": chunk.text,
        "tables": [],
        "images": [],
        "types": ["text"],
        "section_title": None,
        "page_number": None,
        "page_numbers": [],  # For multi-page chunks
    }

    # Extract section title and page numbers
    content_data["section_title"] = extract_section_title(chunk)
    content_data["page_number"] = extract_page_number(chunk)
    content_data["page_numbers"] = extract_all_page_numbers(chunk)

    # Check for tables and images in original elements
    if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__

            # Handle tables
            if element_type == "Table":
                content_data["types"].append("table")
                table_html = getattr(element.metadata, "text_as_html", element.text)
                content_data["tables"].append(table_html)

            # Handle images
            elif element_type == "Image":
                if hasattr(element, "metadata") and hasattr(
                    element.metadata, "image_base64"
                ):
                    content_data["types"].append("image")
                    content_data["images"].append(element.metadata.image_base64)

    content_data["types"] = list(set(content_data["types"]))
    return content_data
