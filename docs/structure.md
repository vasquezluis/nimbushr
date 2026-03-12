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
    app/
    ├── core/                          ← NEW: abstractions (interfaces/protocols)
    │   ├── interfaces/
    │   │   ├── vector_store.py        # AbstractVectorStore protocol
    │   │   ├── graph_store.py         # AbstractGraphStore protocol
    │   │   └── embedder.py            # AbstractEmbedder protocol
    │   └── models.py                  # Shared domain models (ChunkResult, etc.)
    │
    ├── infrastructure/                ← NEW: concrete implementations
    │   ├── vector_stores/
    │   │   ├── chroma.py              # ChromaVectorStore (current logic moved here)
    │   │   └── postgres.py            # PgVectorStore (future, just skeleton)
    │   ├── graph_stores/
    │   │   ├── networkx_store.py      # NetworkXGraphStore (current logic moved here)
    │   │   └── neo4j_store.py         # Neo4jGraphStore (future skeleton)
    │   └── embedders/
    │       └── openai_embedder.py     # OpenAIEmbedder
    │
    ├── services/                      ← NEW: orchestration (replaces scattered pipeline files)
    │   ├── ingest_service.py          # Calls loaders → chunkers → embedder → vector_store → graph_store
    │   └── query_service.py           # Calls vector_store + graph_store → reranker → LLM
    │
    ├── rag/                           ← KEEP (mostly unchanged internal logic)
    │   ├── loaders/                   # unchanged
    │   ├── chunkers/                  # unchanged
    │   ├── ingest/                    # ai_summarizer.py stays; vector_store.py removed
    │   ├── query/                     # streaming_query_engine.py stays; vector_store.py removed
    │   └── graph/                     # entity_extractor, knowledge_graph internals stay
    │
    ├── api/v1/routes/                 # unchanged — depends on services, not storage
    ├── deps.py                        # UPDATED: returns AbstractVectorStore, not Chroma
    ├── settings.py                    # ADD: VECTOR_STORE_BACKEND = "chroma" | "postgres"
    └── main.py                        # UPDATED: uses factory to init correct stores
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
