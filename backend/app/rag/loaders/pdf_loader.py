"""
PDF Loader Module
Handles loading and parsing PDF documents
"""

from app.settings import settings
from typing import List, Dict
from unstructured.partition.pdf import partition_pdf


def load_pdfs_from_directory() -> Dict[str, List]:
    """
    Extract elements from all PDFs in the configured directory.

    Returns:
        Dictionary mapping PDF filenames to their extracted elements
    """

    pdf_directory = settings.data_dir

    # Get all PDF files
    pdf_files = list(pdf_directory.glob("*.pdf"))

    # Verify directory exists
    if not pdf_files:
        print(f"Error: PDF directory not found at {pdf_directory}", flush=True)
        return {}

    # Get all PDF files
    pdf_files = list(pdf_directory.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}", flush=True)
        return {}

    print(f"Found {len(pdf_files)} PDF file(s)", flush=True)

    all_elements = {}

    # Process each PDF
    for pdf_path in pdf_files:
        print(f"\nPartitioning document: {pdf_path.name}")
        print(f"Size: {pdf_path.stat().st_size} bytes", flush=True)

        try:
            elements = partition_pdf(
                filename=str(pdf_path),
                strategy=settings.pdf_strategy,
                infer_table_structure=settings.infer_table_structure,
                extract_image_block_types=(
                    ["Image"] if settings.extract_images else None
                ),
                extract_image_block_to_payload=settings.extract_images,
            )

            all_elements[pdf_path.name] = elements
            print(f"Extracted {len(elements)} elements from {pdf_path.name}")

        except Exception as e:
            print(f"Error processing {pdf_path.name}: {str(e)}", flush=True)
            continue

    print(f"\nSuccessfully processed: {len(all_elements)}/{len(pdf_files)} PDFs")
    return all_elements
