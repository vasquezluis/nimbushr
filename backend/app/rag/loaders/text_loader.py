"""
Text/Markdown Loader Module
Loads .txt and .md files, splits them into sections, and returns raw chunks
ready for the ingest pipeline.

Splitting strategy:
  - Markdown (.md): split on headings (# / ## / ###) so each section becomes
    its own chunk, preserving the heading as the section title.
  - Plain text (.txt): split on blank-line paragraph boundaries.
  - If a split exceeds TEXT_CHUNK_CHARS it is further subdivided by character
    count (respecting word boundaries where possible).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from app.settings import settings


@dataclass
class TextChunk:
    """Raw chunk produced by the text loader before Document creation."""

    text: str
    section_title: str | None = None
    # 1-based logical "page" — paragraph index for .txt, heading index for .md
    page_number: int = 1
    source_file: str = ""
    source_type: str = "text"  # "text" | "markdown"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _split_by_size(text: str, max_chars: int) -> List[str]:
    """Further split a text block that exceeds *max_chars*."""
    if len(text) <= max_chars:
        return [text]

    parts: List[str] = []
    while text:
        if len(text) <= max_chars:
            parts.append(text)
            break
        # Try to break at the last whitespace before the limit
        split_at = text.rfind(" ", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        parts.append(text[:split_at].strip())
        text = text[split_at:].strip()
    return [p for p in parts if p]


def _parse_markdown(content: str, filename: str, max_chars: int) -> List[TextChunk]:
    """Split markdown by headings; sub-split oversized sections."""
    # Pattern: a line that starts with 1-3 '#' characters
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

    chunks: List[TextChunk] = []
    section_index = 0

    matches = list(heading_re.finditer(content))

    def _add_section(title: str | None, body: str, idx: int):
        body = body.strip()
        if not body:
            return
        for part in _split_by_size(body, max_chars):
            chunks.append(
                TextChunk(
                    text=part,
                    section_title=title,
                    page_number=idx + 1,
                    source_file=filename,
                    source_type="markdown",
                )
            )

    if not matches:
        # No headings — treat whole file as one section
        _add_section(None, content, 0)
        return chunks

    # Text before the first heading
    preamble = content[: matches[0].start()]
    _add_section("Preamble", preamble, section_index)

    for i, match in enumerate(matches):
        section_index += 1
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]
        _add_section(title, body, section_index)

    return chunks


def _parse_text(content: str, filename: str, max_chars: int) -> List[TextChunk]:
    """Split plain text on blank lines (paragraph boundaries)."""
    paragraphs = re.split(r"\n{2,}", content)
    chunks: List[TextChunk] = []

    para_index = 0
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        for part in _split_by_size(para, max_chars):
            para_index += 1
            chunks.append(
                TextChunk(
                    text=part,
                    section_title=None,
                    page_number=para_index,
                    source_file=filename,
                    source_type="text",
                )
            )

    return chunks


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_text_file(file_path: Path) -> List[TextChunk]:
    """
    Load a single .txt or .md file and return a list of TextChunk objects.
    """
    suffix = file_path.suffix.lower()
    if suffix not in (".txt", ".md"):
        raise ValueError(f"Unsupported file type for text loader: {suffix}")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    max_chars = settings.chunk_max_chars

    if suffix == ".md":
        return _parse_markdown(content, file_path.name, max_chars)
    return _parse_text(content, file_path.name, max_chars)


def load_text_files_from_directory(data_dir: Path) -> Dict[str, List[TextChunk]]:
    """
    Load all .txt and .md files from *data/texts*.

    Returns:
        {filename: [TextChunk, ...]}
    """
    files: List[Path] = []
    for ext in ("*.txt", "*.md"):
        files.extend(data_dir.glob(ext))

    if not files:
        print(f"No .txt / .md files found in {data_dir}")
        return {}

    print(f"Found {len(files)} text file(s)")
    result: Dict[str, List[TextChunk]] = {}
    for fp in files:
        try:
            chunks = load_text_file(fp)
            result[fp.name] = chunks
            print(f"  Loaded {fp.name}: {len(chunks)} chunk(s)")
        except Exception as e:
            print(f"  Error loading {fp.name}: {e}")

    return result
