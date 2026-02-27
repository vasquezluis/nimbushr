"""
Graph Retriever Module
Given a user query, extracts entities from it and traverses the graph
to find related chunks. This is the "graph" side of our hybrid retrieval.

The flow:
  1. Extract entities from the query (same extractor we use at ingestion)
  2. Find matching nodes in the graph (fuzzy match on entity names)
  3. Traverse 1-2 hops to find related nodes
  4. Collect chunk_indices from all found nodes
  5. Return those indices so the query engine can fetch the actual chunks
"""

from difflib import SequenceMatcher
from typing import Optional, TypedDict

import networkx as nx

from app.rag.graph.entity_extractor import extract_entities_from_query
from app.rag.graph.knowledge_graph import _normalize_name


class GraphTraversalResult(TypedDict):
    chunk_indices: list[int]
    matched_nodes: list[dict]  # {name, entity_type, chunk_indices, neighbors}


def _similarity(a: str, b: str) -> float:
    """
    Simple string similarity ratio between 0 and 1.
    We use this instead of exact matching because the LLM might extract
    "Remote Work Policy" from the query but the graph has "Remote Work Policy"
    stored with slightly different casing.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_matching_nodes(
    graph: nx.DiGraph,
    entity_name: str,
    entity_type: str = "",
    threshold: float = 0.75,
) -> list[str]:
    """
    Find graph nodes matching an entity name.
    First tries full name match, then falls back to checking
    if either string contains the other (handles 'Pro Pricing Plan' → 'Pro Plan')
    """

    matches = []
    normalized_query = _normalize_name(entity_name).lower()

    for node, data in graph.nodes(data=True):
        normalized_node = node.lower()
        name_score = _similarity(normalized_query, normalized_node)

        # Partial containment fallback:
        # 'pro pricing plan' contains 'pro plan' → still a match
        containment_bonus = 0.0
        query_words = set(normalized_query.split())
        node_words = set(normalized_node.split())
        shared_words = query_words & node_words

        if len(node_words) > 0:
            word_overlap = len(shared_words) / len(node_words)
            if word_overlap >= 0.8:  # 80% of node words appear in query
                containment_bonus = 0.15

        type_bonus = (
            0.1
            if (
                entity_type
                and data.get("entity_type", "").lower() == entity_type.lower()
            )
            else 0.0
        )

        final_score = name_score + containment_bonus + type_bonus

        if final_score >= threshold:
            matches.append(node)

    return matches


def get_neighboring_chunks(
    graph: nx.DiGraph,
    node_id: str,
    hops: int = 1,
) -> set[int]:
    """
    Collect chunk_indices from a node and its neighbors up to `hops` away.

    hops=1 means: the node itself + its direct neighbors
    hops=2 means: the node + neighbors + neighbors of neighbors

    We keep hops low (default 1) to stay focused.
    Higher hops = more chunks but less precision.
    """

    chunk_indices = set()

    # Start with the node itself
    node_data = graph.nodes[node_id]
    for idx in node_data.get("chunk_indices", []):
        chunk_indices.add(idx)

    if hops == 0:
        return chunk_indices

    # Walk outgoing edges (what this entity relates to)
    for neighbor in graph.successors(node_id):
        neighbor_data = graph.nodes[neighbor]
        for idx in neighbor_data.get("chunk_indices", []):
            chunk_indices.add(idx)

    # Walk incoming edges (what relates to this entity)
    for neighbor in graph.predecessors(node_id):
        neighbor_data = graph.nodes[neighbor]
        for idx in neighbor_data.get("chunk_indices", []):
            chunk_indices.add(idx)

    return chunk_indices


def retrieve_chunks_from_graph(
    query: str,
    graph: Optional[nx.DiGraph],
    max_chunks: int = 5,
) -> GraphTraversalResult:
    """
    Main entry point for graph retrieval.
    Returns a list of chunk_indices relevant to the query.

    Args:
        query: The user's question
        graph: The loaded NetworkX graph (can be None — graceful fallback)
        max_chunks: Cap on how many chunk indices to return

    Returns:
        List of chunk_indices to fetch from the vector store.
        Empty list if graph is None or nothing relevant found.
        Traversal metadata for frontend visualization.
    """

    empty_result: GraphTraversalResult = {"chunk_indices": [], "matched_nodes": []}

    # Graceful fallback — if no graph exists yet, return nothing
    # The hybrid merger will just use vector results only
    if graph is None:
        return empty_result

    # Step 1: Extract entities from the query
    # We reuse the same extractor but chunk_index=-1 marks it as a query
    entities = extract_entities_from_query(query)

    if not entities:
        print("  Graph: no entities found in query")
        return empty_result

    print(f"  Graph: found {len(entities)} entities in query")

    # Step 2: Find matching nodes and collect chunk indices
    all_chunk_indices: set[int] = set()
    matched_nodes: list[dict] = []

    for entity in entities:
        entity_name = _normalize_name(entity["name"])
        entity_type = entity.get("type", "")
        matching_nodes = find_matching_nodes(graph, entity_name, entity_type)

        if not matching_nodes:
            print(f"  Graph: no match for '{entity_name}'")
            continue

        for node_id in matching_nodes:
            print(f"  Graph: '{entity_name}' → matched node '{node_id}'")
            indices = get_neighboring_chunks(graph, node_id, hops=1)
            all_chunk_indices.update(indices)

            # Collect neighbor info for visualization
            neighbors = []
            for neighbor in graph.successors(node_id):
                neighbors.append(
                    {
                        "name": neighbor,
                        "relation": graph.edges[node_id, neighbor].get(
                            "relations", ["related_to"]
                        )[0],
                        "direction": "outgoing",
                    }
                )
            for neighbor in graph.predecessors(node_id):
                neighbors.append(
                    {
                        "name": neighbor,
                        "relation": graph.edges[neighbor, node_id].get(
                            "relations", ["related_to"]
                        )[0],
                        "direction": "incoming",
                    }
                )

            matched_nodes.append(
                {
                    "name": node_id,
                    "entity_type": graph.nodes[node_id].get("entity_type", "Unknown"),
                    "query_entity": entity_name,  # what the query asked for
                    "chunk_indices": list(indices),
                    "neighbors": neighbors[:8],  # cap to avoid huge payloads
                }
            )

    result_indices = list(all_chunk_indices)[:max_chunks]
    print(f"  Graph: returning {len(result_indices)} chunk indices → {result_indices}")

    return {"chunk_indices": result_indices, "matched_nodes": matched_nodes}
