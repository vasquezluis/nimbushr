"""
Content Analysis Module
Handles content type separation and analysis
"""

from typing import Dict


def separate_content_types(chunk) -> Dict:
    """
    Analyze what types of content are in a chunk.

    Args:
        chunk: A chunked element to analyze

    Returns:
        Dictionary containing text, tables, images, and content types
    """
    content_data = {"text": chunk.text, "tables": [], "images": [], "types": ["text"]}

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
