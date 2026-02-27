# NimbusHR — Hybrid GraphRAG System

A full-stack RAG (Retrieval Augmented Generation) system combining **vector search** and **knowledge graph retrieval** for intelligent HR document Q&A.

Built as a learning project to explore GraphRAG concepts — hybrid retrieval, entity extraction, graph traversal, and real-time streaming.

---

## What it does

- Ingests PDFs, Excel/CSV, and text/markdown files into a vector store and a knowledge graph
- Answers questions using both semantic similarity (vector) and structural connections (graph)
- Streams answers token-by-token with cited sources and graph traversal visualization
- Serves a document viewer for all ingested file types

---

## Architecture

```
User Question
     ↓
     ├── Vector Search (ChromaDB)      → semantic similarity
     └── Graph Retrieval (NetworkX)    → entity traversal
                    ↓
             Hybrid Merger             → smart scoring + dedup
                    ↓
             Reranker                  → cross-encoder reranking
                    ↓
             LLM (GPT-4o)              → streaming answer
                    ↓
     Answer + Sources + Graph Traversal
```

See `docs/structure.md` for the full ingestion and query flow diagrams.

---

## Tech stack

**Backend**

- FastAPI — API server with SSE streaming
- ChromaDB — vector store
- NetworkX — knowledge graph
- LangChain — document processing and LLM chains
- OpenAI — embeddings (text-embedding-3-small), LLM (GPT-4o)
- Unstructured — PDF parsing with table and image extraction
- Sentence Transformers — cross-encoder reranking
- slowapi — rate limiting

**Frontend**

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- react-pdf

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/vasquezluis/nimbushr

# Backend
cd backend

# Activate environment (Linux)
source .venv/bin/activate

# Install packages
uv venv
uv sync

# Frontend
cd ../frontend
pnpm install
```

### 2. Configure environment

```bash
cd backend
cp .env.example .env
# Add your OpenAI API key:
# OPENAI_API_KEY=your-key-here
```

### 3. Add documents

```
backend/data/pdfs/        ← PDF files
backend/data/excels/      ← Excel and CSV files
backend/data/texts/       ← .txt and .md files
```

### 4. Run ingestion

```bash
cd backend
uv run python -m app.ingest
```

This will:

1. Parse all documents (PDFs via `unstructured`, Excel via `openpyxl`, text natively)
2. Chunk and optionally AI-summarize complex chunks (tables, images)
3. Build embeddings and store in ChromaDB (`chroma_db/`)
4. Extract entities and relationships via LLM
5. Build and persist the knowledge graph (`graph_db/knowledge_graph.json`)

### 5. Start the backend

```bash
cd backend
uv run uvicorn app.main:app --reload
# http://localhost:8000
# http://localhost:8000/docs
```

### 6. Start the frontend

```bash
cd frontend
npm run dev
# http://localhost:3000
```

---

## Configuration

All settings live in `backend/app/settings.py` and can be overridden via `.env`.

### Key settings

```python
# Models
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL       = "gpt-4o"

# Retrieval
TOP_K_CHUNKS    = 3     # final chunks sent to LLM
RETRIEVAL_K     = 5     # chunks fetched by each retriever before merging
USE_MMR         = True  # Maximal Marginal Relevance for diverse vector results
USE_RERANKING   = True  # cross-encoder reranking after hybrid merge

# Chunking
CHUNK_MAX_CHARS = 1200
CHUNK_NEW_AFTER = 900

# AI Summarization (GPT-4o called per chunk with tables/images)
USE_AI_SUMMARIZATION  = True
AI_SUMMARY_MIN_TABLES = 2     # summarize if chunk has ≥ 2 tables
```

### Cost control

Ingestion makes LLM calls for:

- **AI summarization** — GPT-4o for chunks with tables or images (~$0.02–0.05 per chunk)
- **Entity extraction** — GPT-4o for every chunk to build the graph (~$0.01 per chunk)

For a test run, disable both:

```bash
# .env
USE_AI_SUMMARIZATION=false
```

And swap GPT-4o for GPT-4o-mini for entity extraction in `entity_extractor.py` to reduce cost further.

---

## Hybrid retrieval — how it works

Vector search and graph retrieval run in parallel and are merged using a scoring system:

| Result type                            | Score        |
| -------------------------------------- | ------------ |
| Vector only                            | +2           |
| Graph + Vector agree                   | +4           |
| Graph only, new source file            | +1           |
| Graph only, same source file as vector | 0 (excluded) |

**Vector** is the reliable baseline — good for factual, keyword-rich, and structured queries.
**Graph** adds value for conceptual queries and cross-document relational queries.

See `docs/graph.md` for the full GraphRAG implementation details.

---

## Project structure

```
backend/
├── app/
│   ├── settings.py
│   ├── main.py
│   ├── ingest.py
│   ├── api/v1/routes/       # query.py, files.py
│   └── rag/
│       ├── ingest/          # pipeline, chunking, AI summarizer, vector store
│       ├── loaders/         # pdf, excel, text loaders
│       ├── query/           # streaming pipeline, query engine
│       └── graph/           # entity_extractor, knowledge_graph, graph_retriever, hybrid_retriever
├── data/
│   ├── pdfs/
│   ├── excels/
│   └── texts/
├── chroma_db/               # auto-created
├── graph_db/                # auto-created
└── tests/

frontend/
├── app/
├── components/              # chat, message, sources, graph-traversal, document viewers
├── hooks/                   # use-streaming-query, use-files
├── api/                     # query.ts, files.ts
└── types/                   # chat.ts, query.ts, files.ts
```

Full structure in `docs/structure.md`.

---

## API endpoints

| Method | Endpoint                          | Description                   |
| ------ | --------------------------------- | ----------------------------- |
| POST   | `/api/v1/query`                   | Non-streaming query           |
| POST   | `/api/v1/query/stream`            | Streaming query (SSE)         |
| GET    | `/api/v1/files`                   | List all ingested files       |
| GET    | `/api/v1/files/{filename}`        | Serve a file                  |
| GET    | `/api/v1/files/{filename}/chunks` | Get chunk metadata for a file |

Rate limit: 5 requests/minute per IP.

---

## Docs

| File                | Contents                                                       |
| ------------------- | -------------------------------------------------------------- |
| `docs/commands.md`  | All run commands and data directories                          |
| `docs/structure.md` | Full architecture diagrams                                     |
| `docs/graph.md`     | GraphRAG implementation — steps, design decisions, limitations |

---

## Known limitations

- Entity extraction quality depends on LLM consistency — the same concept can get different names across chunks, mitigated by fuzzy matching and normalization but not eliminated
- Graph adds most value for conceptual/relational queries; vector wins for factual lookups
- No authentication — intended as a learning/portfolio project
- Graph is rebuilt fully on every ingestion run (no incremental updates)
