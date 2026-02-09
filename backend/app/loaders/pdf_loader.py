import os
from typing import List, Dict
from pathlib import Path
from unstructured.partition.pdf import partition_pdf


def load_pdfs_from_directory() -> Dict[str, List]:
    """
    Extract elements from all PDFs in the data/pdfs directory.

    Returns:
        Dictionary mapping PDF filenames to their extracted elements
    """

    # Get the project root directory (parent of app/)
    current_file = Path(__file__)  # app/loaders/pdf_loader.py
    project_root = current_file.parent.parent.parent  # Go up to project root
    pdf_directory = project_root / "data" / "pdfs"

    print(f"📁 Looking for PDFs in: {pdf_directory}")

    # Verify directory exists
    if not pdf_directory.exists():
        print(f"❌ Error: PDF directory not found at {pdf_directory}", flush=True)
        print(f"Current working directory: {os.getcwd()}", flush=True)
        return {}

    # Get all PDF files
    pdf_files = list(pdf_directory.glob("*.pdf"))

    if not pdf_files:
        print(f"⚠️ No PDF files found in {pdf_directory}", flush=True)
        return {}

    print(f"✅ Found {len(pdf_files)} PDF file(s)", flush=True)

    all_elements = {}

    # Process each PDF
    for pdf_path in pdf_files:
        print(f"\n📄 Partitioning document: {pdf_path.name}")
        print(f"   File size: {pdf_path.stat().st_size} bytes", flush=True)

        try:
            elements = partition_pdf(
                filename=str(pdf_path),
                strategy="hi_res",  # Use the most accurate (but slower) processing method
                infer_table_structure=True,  # Keep tables as structured HTML
                extract_image_block_types=["Image"],  # Grab images found in the PDF
                extract_image_block_to_payload=True,  # Store images as base64 data
            )

            all_elements[pdf_path.name] = elements
            print(f"   ✅ Extracted {len(elements)} elements from {pdf_path.name}")

        except Exception as e:
            print(f"   ❌ Error processing {pdf_path.name}: {str(e)}", flush=True)
            continue

    print(f"\n🎉 Total PDFs processed: {len(all_elements)}/{len(pdf_files)}")
    return all_elements
