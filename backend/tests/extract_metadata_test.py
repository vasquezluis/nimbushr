"""
Test Metadata Extraction
Run this to verify that unstructured is providing page numbers and section titles
"""

from unstructured.chunking.title import chunk_by_title
from unstructured.partition.pdf import partition_pdf

from app.settings import settings


def test_metadata_extraction():
    """Test what metadata unstructured provides for your PDFs."""

    # Adjust this path to your PDF directory
    pdf_directory = settings.pdf_data_dir

    # Get first PDF for testing
    pdf_files = list(pdf_directory.glob("*.pdf"))

    if not pdf_files:
        print("No PDFs found!")
        return

    test_pdf = pdf_files[0]
    print(f"Testing with: {test_pdf.name}")
    print("=" * 70)

    # Partition the PDF
    print("\n1. PARTITIONING PDF...")
    elements = partition_pdf(
        filename=str(test_pdf),
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True,
    )

    print(f"Found {len(elements)} elements")

    # Analyze first 10 elements
    print("\n2. ANALYZING ELEMENTS (first 10)...")
    print("-" * 70)

    for i, element in enumerate(elements[:10]):
        print(f"\nElement {i + 1}:")
        print(f"  Type: {element.category}")
        print(
            f"  Text: {element.text[:100]}..."
            if len(element.text) > 100
            else f"  Text: {element.text}"
        )

        # Check for page number
        if hasattr(element, "metadata") and hasattr(element.metadata, "page_number"):
            print(f"  ✓ Page Number: {element.metadata.page_number}")
        else:
            print(f"  ✗ No page number")

        # Check for parent_id (for hierarchy)
        if hasattr(element, "metadata") and hasattr(element.metadata, "parent_id"):
            print(f"  ✓ Parent ID: {element.metadata.parent_id}")
        else:
            print(f"  ✗ No parent ID")

    # Chunk the elements
    print("\n" + "=" * 70)
    print("3. CHUNKING...")
    chunks = chunk_by_title(
        elements,
        max_characters=1200,
        new_after_n_chars=900,
        combine_text_under_n_chars=300,
    )

    print(f"Created {len(chunks)} chunks")

    # Analyze first 3 chunks
    print("\n4. ANALYZING CHUNKS (first 3)...")
    print("-" * 70)

    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i + 1}:")
        print(f"  Text: {chunk.text[:150]}...")

        # Check for page number in chunk
        if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "page_number"):
            print(f"  ✓ Chunk Page Number: {chunk.metadata.page_number}")
        else:
            print(f"  ✗ No chunk page number")

        # Check for original elements
        if hasattr(chunk, "metadata") and hasattr(chunk.metadata, "orig_elements"):
            print(f"  ✓ Original Elements: {len(chunk.metadata.orig_elements)}")

            # Count titles in original elements
            titles = []
            page_numbers = set()

            for element in chunk.metadata.orig_elements:
                if element.category == "Title":
                    titles.append(element.text)

                if hasattr(element, "metadata") and hasattr(
                    element.metadata, "page_number"
                ):
                    page_numbers.add(element.metadata.page_number)

            if titles:
                print(f"    Titles found: {titles}")
            else:
                print(f"    No titles in this chunk")

            if page_numbers:
                print(f"    Pages spanned: {sorted(page_numbers)}")
            else:
                print(f"    No page numbers in elements")
        else:
            print(f"  ✗ No original elements")

    # Summary
    print("\n" + "=" * 70)
    print("5. SUMMARY")
    print("-" * 70)

    # Check overall page number coverage
    elements_with_pages = sum(
        1
        for e in elements
        if hasattr(e, "metadata") and hasattr(e.metadata, "page_number")
    )

    # Check title coverage
    title_elements = sum(1 for e in elements if e.category == "Title")

    print(
        f"Elements with page numbers: {elements_with_pages}/{len(elements)} ({elements_with_pages / len(elements) * 100:.1f}%)"
    )
    print(
        f"Title elements: {title_elements}/{len(elements)} ({title_elements / len(elements) * 100:.1f}%)"
    )

    if elements_with_pages > 0:
        print("\n✓ GOOD NEWS: Unstructured is providing page numbers!")
    else:
        print("\n✗ WARNING: Unstructured is NOT providing page numbers")
        print("  - Try using strategy='hi_res' or 'ocr_only'")
        print("  - Check if PDF has internal page numbering")

    if title_elements > 0:
        print("✓ GOOD NEWS: Document has Title elements for section detection!")
    else:
        print("✗ WARNING: No Title elements found")
        print("  - PDF might not have proper heading structure")
        print("  - Section detection may not work well")


if __name__ == "__main__":
    test_metadata_extraction()
