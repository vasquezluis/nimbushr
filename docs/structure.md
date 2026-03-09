# Architecture

## Query flow

```
User Question
     ↓
     ├── Vector Search (ChromaDB + MMR)
     │        ↓
     │   Semantic chunks (by similarity)
     │
     └── Graph Retrieval (NetworkX)
              ↓
         Entity extraction from query
              ↓
         Fuzzy node matching
              ↓
         Neighbor traversal (1 hop)
              ↓
         Chunk indices → fetch from ChromaDB

         Both results
              ↓
         Hybrid Merger
         (scoring + dedup)
               ↓
         Reranker (cross-encoder)
               ↓
         LLM (GPT-4o, streaming)
               ↓
         Answer + Sources + Graph Traversal
```

---

## Hybrid scoring logic

```
Vector result:                    +2  (reliable semantic baseline)
Graph + Vector agree (both):      +4  (highest confidence)
Graph only, NEW source file:      +1  (graph found something vector missed)
Graph only, SAME source file:      0  (likely redundant, excluded)
```

---

## Ingestion flow

```
PDFs                    Excel / CSV             Text / Markdown
  ↓                          ↓                       ↓
partition_pdf           load_excel_file         load_text_file
  ↓                          ↓                       ↓
chunk_by_title          chunk_excel_sheets      parse_markdown /
  ↓                          ↓                  parse_text
AI summarizer                ↓                       ↓
(tables + images)      create_excel_documents  create_text_documents
  ↓                          ↓                       ↓
            all_documents (LangChain Documents)
                             ↓
                  ┌──────────┴───────────┐
                  ↓                      ↓
            Vector Store           Knowledge Graph
            (ChromaDB)             (NetworkX → JSON)
            chroma_db/             graph_db/knowledge_graph.json
```

---

## Project structure

```
backend/
├── app/
│   ├── settings.py                          # Centralized config (Pydantic)
│   ├── main.py                              # FastAPI app + lifespan
│   ├── limiter.py                           # Rate limiting (slowapi)
│   ├── ingest.py                            # Ingestion entry point
│   ├── api/
│   │   └── v1/routes/
│   │       ├── query.py                     # /query and /query/stream endpoints
│   │       └── files.py                     # /files endpoints
│   ├── rag/
│   │   ├── ingest/
│   │   │   ├── ingest_pipeline.py           # Orchestrates full ingestion
│   │   │   ├── document_processor.py        # PDF chunking (chunk_by_title)
│   │   │   ├── content_analyzer.py          # Extracts tables, images, section titles
│   │   │   ├── ai_summarizer.py             # GPT-4o summaries for complex chunks
│   │   │   ├── vector_store.py              # ChromaDB creation
│   │   │   ├── excel_document_processor.py  # Excel chunking
│   │   │   └── text_document_processor.py   # Text chunking
│   │   ├── loaders/
│   │   │   ├── pdf_loader.py                
│   │   │   ├── excel_loader.py              
│   │   │   └── text_loader.py               
│   │   ├── chunkers/
│   │   │   ├── pdf_processor.py                
│   │   │   ├── excel_processor.py              
│   │   │   └── text_processor.py               
│   │   ├── query/
│   │   │   ├── streaming_query_pipeline.py  # Main query orchestrator
│   │   │   ├── streaming_query_engine.py    # Retrieval + LLM streaming
│   │   │   ├── query_pipeline.py            # Non-streaming (CLI/fallback)
│   │   │   ├── query_engine.py              # Non-streaming engine
│   │   │   └── vector_store.py              # ChromaDB loader
│   │   └── graph/
│   │       ├── entity_extractor.py          # LLM entity extraction (chunks + queries)
│   │       ├── knowledge_graph.py           # NetworkX build, save, load, merge
│   │       ├── graph_retriever.py           # Query → entity match → chunk indices
│   │       └── hybrid_retriever.py          # Merges vector + graph results
├── data/
│   ├── pdfs/
│   ├── excels/
│   └── texts/
├── chroma_db/                               # Vector store (auto-created)
├── graph_db/                                # Graph store (auto-created)
│   └── knowledge_graph.json
└── tests/
    └── simple_graph_test.py

frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── chat-area.tsx                      # Main chat orchestrator
│   ├── chat-input.tsx                     # Message input + rate limit UI
│   ├── message-list.tsx                   # Scrollable message list
│   ├── message-bubble.tsx                 # Single message (user + assistant)
│   ├── markdown-renderer.tsx              # Renders LLM markdown responses
│   ├── sources.tsx                        # Collapsible sources section
│   ├── graph-traversal.tsx                # Collapsible graph nodes + edges
│   ├── document-panel.tsx                 # Right panel: file list + viewers
│   ├── pdf-viewer.tsx
│   ├── csv-viewer.tsx
│   ├── excel-viewer.tsx
│   └── text-viewer.tsx
├── hooks/
│   ├── use-streaming-query.ts             # SSE streaming + state management
│   ├── use-files.ts
│   └── use-mobile.ts
├── api/
│   ├── query.ts                           # streamQuery, sendQuery, RateLimitError
│   └── files.ts
└── types/
    ├── chat.ts                            # Message, MessageListProps, etc.
    ├── query.ts                           # StreamEvent, GraphNode, Source, etc.
    └── files.ts
```
