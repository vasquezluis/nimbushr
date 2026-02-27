# GraphRAG — Knowledge Graph Implementation

## What it is

Standard vector RAG retrieves chunks by **semantic similarity** — chunks that sound like the query win.

GraphRAG adds a knowledge graph layer where:

- **Nodes** = entities (policies, departments, roles, benefits, sections)
- **Edges** = relationships between them (`applies_to`, `requires`, `belongs_to`, etc.)

This allows retrieval based on **structural connections**, not just word similarity.

---

## When graph retrieval helps vs. doesn't

| Query type                                                       | Better retrieval              |
| ---------------------------------------------------------------- | ----------------------------- |
| Vague/conceptual ("What is our Core Philosophy?")                | Graph (section title nodes)   |
| Cross-document relational ("Which policies apply to engineers?") | Graph (edge traversal)        |
| Specific factual lookup ("What is the Pro plan price?")          | Vector (keyword-rich content) |
| Excel/structured data queries                                    | Vector (explicit, structured) |

The hybrid merger is designed so each method reinforces the other rather than competing.

---

## Implementation — step by step

### Step 1 — Entity extraction (`entity_extractor.py`)

Two separate prompts handle two different scenarios:

**`extract_entities_from_chunk()`** — used at ingestion time.
Conservative: only extracts clearly named entities from rich document text.

**`extract_entities_from_query()`** — used at query time.
Aggressive: extracts any searchable concept from short vague questions.
e.g. `"What are the Core Philosophy"` → `["Core Philosophy"]`

Both return:

```python
{
  "entities": [{"name": "...", "type": "...", "description": "..."}],
  "relationships": [{"source": "...", "target": "...", "relation": "..."}]
}
```

---

### Step 2 — Building the graph (`knowledge_graph.py`)

Uses a **directed graph** (`nx.DiGraph`) because relationships have direction:
`"Policy applies_to Department"` ≠ `"Department applies_to Policy"`

Key behaviors:

- Same entity appearing in multiple chunks → **one node**, multiple `chunk_indices`
- `chunk_indices` is the bridge back to ChromaDB — how we fetch actual text
- Node names are normalized (`_normalize_name`) to reduce duplicates from LLM inconsistency
- Near-duplicate nodes are merged after build (`merge_duplicate_nodes`, threshold=0.85)
- Filenames (`pricing_plans.xlsx`) are excluded from normalization and merging
- Graph is persisted as human-readable JSON at `graph_db/knowledge_graph.json`

**Section titles as guaranteed nodes** — every chunk's `section_title` metadata is injected
as a `Section` entity during ingestion. This ensures headings like `"Core Philosophy"` are
always findable even if the LLM didn't extract them from chunk content.

---

### Step 3 — Graph retriever (`graph_retriever.py`)

Given a query:

1. Extract entities using `extract_entities_from_query()`
2. Normalize entity names
3. Fuzzy-match against graph nodes (`SequenceMatcher`, threshold=0.75)
4. Apply containment bonus: if 80%+ of node's words appear in query entity → +0.15
5. Apply type bonus: matching entity types → +0.1
6. Traverse 1 hop (direct neighbors in both directions)
7. Collect all `chunk_indices` from matched nodes + neighbors
8. Return indices + traversal metadata for frontend visualization

Returns `GraphTraversalResult`:

```python
{
  "chunk_indices": [32, 4, 8, 9, 10],
  "matched_nodes": [
    {
      "name": "Pro Plan",
      "entity_type": "Benefit",
      "query_entity": "Pro Pricing Plan",  # what the query asked for
      "chunk_indices": [...],
      "neighbors": [
        {"name": "Pro Customers", "relation": "applies_to", "direction": "outgoing"},
        ...
      ]
    }
  ]
}
```

---

### Step 4 — Hybrid merger (`hybrid_retriever.py`)

Scoring:

```
Vector result (any):              +2
Graph + Vector agree:             +2+2 = 4  (highest confidence)
Graph only, NEW source file:      +1   (graph found a file vector missed)
Graph only, SAME source file:      0   (excluded — likely redundant)
```

The key design decision: **vector results are the reliable baseline**.
Graph-only results from the same source file as vector results are excluded
because the vector already found the best chunk from that file — graph finding
a different chunk from the same file is almost always worse.

Graph-only results from a **new source file** are included because they represent
genuine cross-document discovery that vector missed entirely.

Final list is capped at `settings.top_k_chunks` before sending to the LLM.

---

## Known limitations

**Entity name inconsistency** — The ingestion LLM and query LLM are independent calls.
They occasionally express the same concept differently. Fuzzy matching + normalization
mitigates this but doesn't eliminate it. A production system would use a controlled
entity vocabulary or a dedicated NER model.

**Generic nodes** — Short or vague chunks produce low-quality entities like `"Effective Date"`
or `"Requirements"`. These create noise in the graph but don't hurt retrieval significantly
since they tend to have low connectivity.

**`top_k_chunks` cap** — With hybrid retrieval, the cap of 3 final chunks means graph
results can crowd out vector results if not scored carefully. The +2/+1/0 system handles
most cases but edge cases exist.

**Ingestion cost** — Entity extraction adds one LLM call per chunk. For 100 chunks this
is ~100 additional GPT-4o calls. Use `gpt-4o-mini` for extraction to reduce cost if needed
(change `llm_model` in the extraction calls only).

---

## Graph store format

`graph_db/knowledge_graph.json` uses NetworkX node-link format:

```json
{
  "directed": true,
  "multigraph": false,
  "nodes": [
    {
      "id": "Core Philosophy",
      "entity_type": "Section",
      "description": "Section from engineering_guidelines.pdf",
      "chunk_indices": [0, 1],
      "source_files": ["engineering_guidelines.pdf"]
    }
  ],
  "edges": [
    {
      "source": "engineering_guidelines.pdf",
      "target": "Core Philosophy",
      "relations": ["contains_section"],
      "source_file": "engineering_guidelines.pdf"
    }
  ]
}
```

Inspect the graph at any time:

```bash
# from backend/
python -c "
import json
with open('graph_db/knowledge_graph.json') as f:
    data = json.load(f)
print(f'Nodes: {len(data[\"nodes\"])}')
print(f'Edges: {len(data[\"edges\"])}')
"
```

---

## Frontend visualization

Each assistant message that triggered graph retrieval shows a collapsible
**Graph traversal** section below Sources:

```
▶ Graph traversal   1 node, 6 connections
```

Expanding shows matched nodes with their entity type (color-coded by type),
the query entity that triggered the match if different, chunk count, and
expandable neighbor list showing edge direction and relation type.

Entity type colors:

- Policy → blue
- Department → purple
- Role → green
- Benefit → amber
- Requirement → red
- Process → cyan
- Section → indigo
- Document → rose
