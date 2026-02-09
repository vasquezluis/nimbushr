# NimbusHR - RAG Ingestion System

A production-ready RAG (Retrieval Augmented Generation) ingestion pipeline for processing PDF documents with support for tables, images, and multimodal content.

## Architecture

```
backend/
├── app/
│   ├── settings.py                    # Centralized configuration
│   ├── ingest.py                      # Main ingest entry point
│   ├── loaders/
│   │   └── pdf_loader.py              # PDF parsing
│   ├── rag/
│   │   └── ingest/
│   │       ├── ingest.py              # Pipeline orchestration
│   │       ├── document_processor.py  # Chunking
│   │       ├── content_analyzer.py    # Content type detection
│   │       ├── ai_summarizer.py       # AI summarization
│   │       └── vector_store.py        # ChromaDB storage
│   └── main.py                        # FastAPI server
├── data/
│   └── pdfs/                          # Place your PDFs here
├── chroma_db/                         # Vector database (auto-created)
└── pyproject.toml
```

## Quick Start

### 1. Setup (uv)

```bash
# Create virtual env
uv venv

# Install dependencies
uv sync

# Create .env file
cp .env.example .env
```

### 2. Add PDFs

```bash
# Place PDF files in the data directory
cp your-documents/*.pdf data/pdfs/
```

### 3. Run Ingestion (uv)

```bash
# From the app directory
cd app
uv run ingest.py
```

The pipeline will:

1. Load all PDFs from `data/pdfs/`
2. Chunk them intelligently by title
3. Optionally create AI summaries (configurable)
4. Store embeddings in ChromaDB

## Configuration

All settings are in `app/settings.py` and can be overridden via environment variables.

### Key Settings

```python
# In settings.py or .env file

# Paths
DATA_DIR = "data/pdfs"              # Where to find PDFs
VECTOR_DB_DIR = "chroma_db"         # Where to store vector DB

# Models
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o"

# Chunking
CHUNK_MAX_CHARS = 3000              # Maximum chunk size
CHUNK_NEW_AFTER = 2400              # Preferred chunk size
CHUNK_COMBINE_UNDER = 500           # Merge small chunks

# AI Summarization (Better bu can be expensive!)
USE_AI_SUMMARIZATION = true         # Enable/disable AI summaries
AI_SUMMARY_MIN_TABLES = 2           # Only summarize if ≥2 tables
AI_SUMMARY_REQUIRE_IMAGES = false   # Require images for summarization
```

### Cost Control

AI summarization uses GPT-4o which costs ~$0.02-0.05 per chunk. For 100 chunks, expect $2-5.

**Recommendation:** Start with `USE_AI_SUMMARIZATION=false` and test retrieval quality first.

To disable AI summarization:

```bash
# In .env
USE_AI_SUMMARIZATION=false
```

Or modify `settings.py`:

```python
use_ai_summarization: bool = False
```

## What Gets Stored

Each chunk is stored with rich metadata:

```python
{
    "page_content": "...",           # Text content or AI summary
    "metadata": {
        "source_file": "document.pdf",
        "source_type": "pdf",
        "chunk_index": 0,
        "has_tables": true,
        "has_images": false,
        "num_tables": 2,
        "num_images": 0,
        "ai_summarized": true,
        "content_types": ["text", "table"],
        "original_content": "{...}"   # Raw text, tables, images
    }
}
```

## Testing the setup

```bash
# Check if ChromaDB was created
cd backend

ls -la chroma_db/

# View ingested collection info
uv run --env-file .env python -c "
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

db = Chroma(
    persist_directory='chroma_db',
    embedding_function=OpenAIEmbeddings(model='text-embedding-3-small')
)

collection = db._collection

# Peek at one chunk
peek = collection.peek(limit=1)

print('ID:', peek['ids'][0])
print('Document:', peek['documents'][0])
print('Metadata:', peek['metadatas'][0])
"
```

## Troubleshooting

### "No PDFs found"

- Ensure PDFs are in `data/pdfs/` directory
- Check file permissions

### "OPENAI_API_KEY not found"

- Create `.env` file with your API key
- Or set environment variable: `export OPENAI_API_KEY=your-key`

### "ImportError: pydantic_settings"

```bash
# First, start the venv
uv add pydantic-settings python-dotenv
```

### Slow ingestion

- Reduce `CHUNK_MAX_CHARS` to create fewer chunks
- Set `USE_AI_SUMMARIZATION=false`
- Use `PDF_STRATEGY=fast` instead of `hi_res`

## Performance Tips

1. **Disable AI summarization for initial testing**
   - Modern embeddings work well without it
   - Save costs and time

2. **Adjust chunk size based on your docs**
   - Technical docs: smaller chunks (2000 chars)
   - Narrative docs: larger chunks (4000 chars)

3. **Use hi_res strategy only when needed**
   - `fast`: Quick, good for text-heavy docs
   - `hi_res`: Better for complex layouts, tables, images

## Next Steps

Once ingestion is complete, you can:

1. **Build a query endpoint** to search your documents
2. **Add retrieval with reranking** for better results
3. **Implement hybrid search** (dense + sparse)
4. **Add document filtering** by source, date, etc.

## Tech Stack

- **LangChain**: Document processing and chains
- **ChromaDB**: Vector database
- **OpenAI**: Embeddings and LLM
- **Unstructured**: PDF parsing with multimodal support
- **FastAPI**: API framework (for future query endpoint)
- **Pydantic**: Configuration management

## Contributing

This is a production-ready foundation. Feel free to:

- Add support for more document types (Word, Excel, etc.)
- Implement advanced chunking strategies
- Add monitoring and observability
- Build a query/retrieval system
