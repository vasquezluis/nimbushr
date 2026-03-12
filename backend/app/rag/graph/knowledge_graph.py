"""
Knowledge Graph Module
Builds and persists a NetworkX graph from extracted entities and relationships.

Graph structure:
  - Nodes: entities with metadata (type, description, source files, chunk indices)
  - Edges: relationships between entities with metadata (relation, source file)

The same entity appearing in multiple chunks = one node with multiple chunk_indices.
This is what allows us to answer "what chunks are relevant to this concept?"
"""

import json
from itertools import combinations
from pathlib import Path
from typing import Optional

import networkx as nx

from app.rag.graph.entity_extractor import ExtractionResult

# Where the graph is saved — alongside the chroma_db
GRAPH_PATH = Path("graph_db/knowledge_graph.json")

_LOWERCASE_WORDS = {
    "and",
    "or",
    "the",
    "a",
    "an",
    "of",
    "in",
    "for",
    "to",
    "with",
    "at",
    "by",
}


def _normalize_name(name: str) -> str:
    """
    Normalize entity names for consistent storage.
    - Skips filenames (contains '.' or '›')
    - Keeps small connector words lowercase
    - Capitalizes meaningful words only
    """

    name = name.strip()

    # Skip filenames and path-like strings — leave them as-is
    if "." in name or "›" in name:
        return name

    words = name.split()
    normalized = []
    for i, word in enumerate(words):
        if i == 0:
            # Always capitalize first word
            normalized.append(word.capitalize())
        elif word.lower() in _LOWERCASE_WORDS:
            normalized.append(word.lower())
        else:
            normalized.append(word.capitalize())

    return " ".join(normalized)


def merge_duplicate_nodes(graph: nx.DiGraph, threshold: float = 0.85) -> nx.DiGraph:
    """
    Merge nodes that are near-duplicates of each other.
    e.g. 'Pro Plan', 'Pro Plans', 'Pro' → all merged into one node.

    Strategy:
    - Compare all node pairs by name similarity
    - If similarity >= threshold, merge the smaller node into the larger one
      (larger = more chunk_indices, meaning more document coverage)
    - Redirect all edges from merged node to the surviving node
    """

    nodes = list(graph.nodes())
    merged = {}  # maps node_id → surviving node_id

    # Find pairs to merge
    for node_a, node_b in combinations(nodes, 2):
        # Skip filenames — they should never be merged
        if "." in node_a or "." in node_b:
            continue

        # Skip nodes that differ only by an ordinal/number — e.g.
        # "Week 2 Goals" vs "Week 3 Goals" are distinct and must not merge
        import re
        nums_a = set(re.findall(r'\d+', node_a))
        nums_b = set(re.findall(r'\d+', node_b))
        if (nums_a or nums_b) and nums_a != nums_b:
            continue

    if not merged:
        print("  No duplicate nodes found to merge")
        return graph

    print(f"  Merging {len(merged)} duplicate nodes...")

    # Apply merges
    for duplicate, survivor in merged.items():
        if not graph.has_node(duplicate) or not graph.has_node(survivor):
            continue

        # Merge chunk_indices
        survivor_chunks = graph.nodes[survivor].get("chunk_indices", [])
        duplicate_chunks = graph.nodes[duplicate].get("chunk_indices", [])
        merged_chunks = list(set(survivor_chunks + duplicate_chunks))
        graph.nodes[survivor]["chunk_indices"] = merged_chunks

        # Merge source_files
        survivor_sources = graph.nodes[survivor].get("source_files", [])
        duplicate_sources = graph.nodes[duplicate].get("source_files", [])
        graph.nodes[survivor]["source_files"] = list(
            set(survivor_sources + duplicate_sources)
        )

        # Redirect edges from duplicate to survivor
        for pred in list(graph.predecessors(duplicate)):
            if pred != survivor and not graph.has_edge(pred, survivor):
                edge_data = graph.edges[pred, duplicate]
                graph.add_edge(pred, survivor, **edge_data)

        for succ in list(graph.successors(duplicate)):
            if succ != survivor and not graph.has_edge(survivor, succ):
                edge_data = graph.edges[duplicate, succ]
                graph.add_edge(survivor, succ, **edge_data)

        graph.remove_node(duplicate)
        print(f"    '{duplicate}' → '{survivor}'")

    print(
        f"  Graph after merge: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    )
    return graph


def build_graph_from_extractions(
    extractions: list[tuple[ExtractionResult, str, int]],
) -> nx.DiGraph:
    """
    Build a directed graph from all extraction results.

    Args:
        extractions: List of (ExtractionResult, source_file, chunk_index) tuples
                     — one per chunk that was processed

    Returns:
        A directed NetworkX graph
    """

    # DiGraph = Directed Graph, because relationships have direction
    # "Policy applies_to Department" is not the same as "Department applies_to Policy"
    graph = nx.DiGraph()

    for extraction, source_file, chunk_index in extractions:
        # --- Add entity nodes ---
        for entity in extraction["entities"]:
            node_name = _normalize_name(entity["name"])

            if not node_name:
                continue

            if graph.has_node(node_name):
                # Node already exists from another chunk — just enrich it
                # Append this chunk index so we know all chunks that mention this entity
                existing_chunks = graph.nodes[node_name].get("chunk_indices", [])
                if chunk_index not in existing_chunks:
                    existing_chunks.append(chunk_index)
                graph.nodes[node_name]["chunk_indices"] = existing_chunks

                # Accumulate source files too
                existing_sources = graph.nodes[node_name].get("source_files", [])
                if source_file not in existing_sources:
                    existing_sources.append(source_file)
                graph.nodes[node_name]["source_files"] = existing_sources

            else:
                # First time we see this entity — create the node
                graph.add_node(
                    node_name,
                    entity_type=entity["type"],
                    description=entity.get("description", ""),
                    chunk_indices=[chunk_index],
                    source_files=[source_file],
                )

        # --- Add relationship edges ---
        for rel in extraction["relationships"]:
            source = _normalize_name(rel["source"])
            target = _normalize_name(rel["target"])
            relation = rel["relation"].strip()

            if not source or not target or not relation:
                continue

            # If nodes don't exist yet (LLM mentioned them in relationships
            # but not in entities), add them as minimal nodes
            if not graph.has_node(source):
                graph.add_node(
                    source,
                    entity_type="Unknown",
                    description="",
                    chunk_indices=[chunk_index],
                    source_files=[source_file],
                )

            if not graph.has_node(target):
                graph.add_node(
                    target,
                    entity_type="Unknown",
                    description="",
                    chunk_indices=[chunk_index],
                    source_files=[source_file],
                )

            # Add the edge (or update if it already exists)
            if graph.has_edge(source, target):
                existing_relations = graph.edges[source, target].get("relations", [])
                if relation not in existing_relations:
                    existing_relations.append(relation)
                graph.edges[source, target]["relations"] = existing_relations
            else:
                graph.add_edge(
                    source,
                    target,
                    relations=[relation],
                    source_file=source_file,
                )

    print(
        f"Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    )
    return graph


def save_graph(graph: nx.DiGraph, path: Path = GRAPH_PATH) -> None:
    """
    Persist the graph to disk as JSON using NetworkX's node-link format.
    This is human-readable and easy to inspect/debug.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    data = nx.node_link_data(graph)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Graph saved to {path}")


def load_graph(path: Path = GRAPH_PATH) -> Optional[nx.DiGraph]:
    """
    Load a previously saved graph from disk.

    Returns:
        The graph, or None if no graph file exists yet.
    """
    if not path.exists():
        print("No graph file found — graph retrieval will be skipped")
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph = nx.node_link_graph(data, directed=True)
    print(
        f"Graph loaded: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    )
    return graph
