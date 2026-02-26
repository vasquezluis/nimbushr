# Project Structure

## Overview

NimbusHR RAG Assistant — a document Q&A system. Upload PDFs, Excel, or text files; ask questions; get answers with source citations.

## Stack

- **Backend**: FastAPI + ChromaDB + LangChain + OpenAI
- **Frontend**: Next.js 14 + React Query + Tailwind

## Directory Layout

```
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI app + lifespan (loads vector store on startup)
│   │   ├── settings.py               # All config (env vars, paths, model params)
│   │   ├── ingest.py                 # CLI entry point for ingestion
│   │   ├── limiter.py                # Rate limiting (5 req/min)
│   │   ├── api/v1/routes/
│   │   │   ├── query.py              # POST /query, POST /query/stream
│   │   │   └── files.py              # GET /files, GET /files/{filename}
│   │   └── rag/
│   │       ├── loaders/              # Load raw files (PDF, Excel, text/markdown)
│   │       ├── ingest/               # Chunk, summarize, embed, store
│   │       └── query/                # Retrieve, rerank, generate answer
├── frontend/
│   ├── app/                          # Next.js pages
│   ├── components/                   # UI components
│   ├── hooks/                        # use-streaming-query, use-files
│   ├── api/                          # Axios + fetch wrappers
│   └── types/                        # TypeScript interfaces
└── data/
    ├── pdfs/
    ├── excels/
    └── texts/
```

## Ingestion Flow

```
Files (PDF / Excel / TXT / MD)
        ↓
   Load raw content
        ↓
   Chunk by title / rows / paragraphs
        ↓
   AI summarize (optional — only for chunks with images or 2+ tables)
        ↓
   Embed (text-embedding-3-small)
        ↓
   Store in ChromaDB
```

## Query Flow

```
User question
      ↓
Embed question
      ↓
Vector search (MMR) → top-k chunks
      ↓
Rerank (cross-encoder)
      ↓
Build context + prompt
      ↓
Stream answer tokens (GPT-4o)
      ↓
Frontend renders markdown + sources
```

## Supported File Types

| Type     | Loader       | Chunking strategy             |
| -------- | ------------ | ----------------------------- |
| PDF      | unstructured | By title / section            |
| Excel    | openpyxl     | N rows per chunk (default 50) |
| CSV      | csv stdlib   | N rows per chunk              |
| TXT      | plain read   | By blank-line paragraphs      |
| Markdown | plain read   | By headings (# / ## / ###)    |
