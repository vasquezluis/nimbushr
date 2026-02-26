# NimbusHR RAG Assistant

AI-powered document Q&A system. Ingest PDFs, Excel, CSV, and text files into a vector database and chat with them in real time.

## Tech Stack

**Backend:** FastAPI · ChromaDB · LangChain · OpenAI · Unstructured  
**Frontend:** Next.js 14 · React Query · Tailwind CSS · shadcn/ui

---

## Quick Start

### 1. Backend

```bash
cd backend

# Install dependencies (requires uv)
uv venv && uv sync

# Set up environment
cp .env.example .env
# → Add your OPENAI_API_KEY to .env
```

### 2. Add documents

```
backend/data/pdfs/      ← PDF files
backend/data/excels/    ← .xlsx, .xls, .csv files
backend/data/texts/     ← .txt, .md files
```

### 3. Ingest

```bash
cd backend
uv run python -m app.ingest
```

### 4. Run backend

```bash
cd backend
uv run uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 5. Run frontend

```bash
cd frontend
# This project uses pnpm but can use any package manager
pnpm install
pnpm run dev
# http://localhost:3000
```

---

## How It Works

**Ingestion**

```
Files → Load → Chunk → (AI summarize) → Embed → ChromaDB
```

**Query**

```
Question → Embed → Vector search (MMR) → Rerank → GPT-4o → Streamed answer
```

Answers are streamed token-by-token via SSE and rendered as markdown with source citations.

---

## Supported File Types

| Type      | Chunking strategy               |
| --------- | ------------------------------- |
| PDF       | By section/title (unstructured) |
| Excel/CSV | N rows per chunk (default: 50)  |
| TXT       | By paragraph (blank lines)      |
| Markdown  | By heading (#, ##, ###)         |

---

## Configuration

All settings live in `backend/app/settings.py` and can be overridden via `.env`.

| Variable                | Default                  | Description                      |
| ----------------------- | ------------------------ | -------------------------------- |
| `OPENAI_API_KEY`        | —                        | Required                         |
| `LLM_MODEL`             | `gpt-4o`                 | Answer generation model          |
| `EMBEDDING_MODEL`       | `text-embedding-3-small` | Embedding model                  |
| `PDF_STRATEGY`          | `hi_res`                 | `fast` \| `hi_res` \| `ocr_only` |
| `USE_AI_SUMMARIZATION`  | `true`                   | AI summaries for complex chunks  |
| `AI_SUMMARY_MIN_TABLES` | `2`                      | Min tables to trigger AI summary |
| `TOP_K_CHUNKS`          | `3`                      | Chunks retrieved per query       |
| `USE_RERANKING`         | `true`                   | Cross-encoder reranking          |
| `EXCEL_CHUNK_ROWS`      | `50`                     | Rows per Excel chunk             |

### Cost tip

AI summarization uses GPT-4o per chunk and only runs on chunks with images or 2+ tables. Disable it for faster, cheaper ingestion during development:

```
USE_AI_SUMMARIZATION=false
```

---

## API Endpoints

| Method | Path                              | Description                 |
| ------ | --------------------------------- | --------------------------- |
| `POST` | `/api/v1/query`                   | Single query, full response |
| `POST` | `/api/v1/query/stream`            | Streaming query (SSE)       |
| `GET`  | `/api/v1/files`                   | List all ingested files     |
| `GET`  | `/api/v1/files/{filename}`        | Serve original file         |
| `GET`  | `/api/v1/files/{filename}/chunks` | List chunks for a file      |

Rate limit: **5 requests/minute** per IP.

---

## Project Structure

```
backend/app/
├── main.py               # FastAPI app entry point
├── settings.py           # Centralized config
├── ingest.py             # Ingestion CLI
├── api/v1/routes/
│   ├── query.py          # Query endpoints
│   └── files.py          # File endpoints
└── rag/
    ├── loaders/           # File readers (PDF, Excel, text)
    ├── ingest/            # Chunking, AI summarization, vector store
    └── query/             # Retrieval, reranking, answer generation

frontend/
├── app/                   # Next.js pages
├── components/            # Chat UI, PDF/Excel/text viewers
├── hooks/                 # useStreamingQuery, useFiles
└── api/                   # API clients
```
