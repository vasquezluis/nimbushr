"""
Entity Extraction Module
Extracts entities and relationships from document chunks using an LLM.
This is the foundation of the knowledge graph — without good extraction,
the graph won't be useful.
"""

import json
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.settings import settings


class Entity(TypedDict):
    name: str  # e.g. "Remote Work Policy"
    type: str  # e.g. "Policy", "Department", "Role", "Benefit"
    description: str  # brief description for context


class Relationship(TypedDict):
    source: str  # entity name
    target: str  # entity name
    relation: str  # e.g. "applies_to", "requires", "belongs_to"


class ExtractionResult(TypedDict):
    entities: list[Entity]
    relationships: list[Relationship]


EXTRACTION_PROMPT = """You are extracting structured knowledge from an HR document chunk.

Identify:
1. ENTITIES — named things like policies, departments, roles, benefits, procedures, dates, requirements
2. RELATIONSHIPS — how those entities connect to each other

Entity types to look for:
- Policy (rules, procedures, guidelines)
- Department (teams, divisions)
- Role (job titles, positions)
- Benefit (insurance, vacation, perks)
- Requirement (conditions, eligibility criteria)
- Process (onboarding, review, approval steps)
- Document (forms, contracts, handbooks)

Relationship types to use:
- applies_to (Policy applies_to Role)
- requires (Benefit requires Requirement)
- belongs_to (Role belongs_to Department)
- managed_by (Department managed_by Role)
- part_of (Process part_of Policy)
- related_to (general connection)

DOCUMENT CHUNK:
{chunk_text}

SOURCE FILE: {source_file}

Respond ONLY with valid JSON in this exact shape, no markdown, no explanation:
{{
  "entities": [
    {{"name": "...", "type": "...", "description": "..."}}
  ],
  "relationships": [
    {{"source": "...", "target": "...", "relation": "..."}}
  ]
}}

Rules:
- Keep entity names concise and consistent (e.g. always "Remote Work Policy" not sometimes "Remote Policy")
- Only extract what is clearly stated, do not infer
- If nothing meaningful found, return {{"entities": [], "relationships": []}}
- Maximum 10 entities and 10 relationships per chunk
"""

QUERY_EXTRACTION_PROMPT = """You are extracting search concepts from a user question to find relevant information in a knowledge graph.

USER QUESTION:
{query}

Extract any concepts, topics, or named things the user is asking about.
Be aggressive — even vague concepts like "Core Philosophy" or "Benefits" are valid.

Respond ONLY with valid JSON, no markdown:
{{
  "entities": [
    {{"name": "...", "type": "...", "description": "..."}}
  ],
  "relationships": []
}}

Rules:
- Extract the main topic even if it's just a concept (e.g. "Core Philosophy", "Remote Work", "Vacation Policy")
- Normalize capitalization (e.g. "core philosophy" → "Core Philosophy")
- Keep names concise (2-4 words max)
- Maximum 5 entities
- Always return at least 1 entity if the question has any topic at all
"""


def extract_entities_from_chunk(
    chunk_text: str,
    source_file: str,
    chunk_index: int,
) -> ExtractionResult:
    """
    Extract entities and relationships from a single chunk using the LLM.

    Args:
        chunk_text: The text content of the chunk
        source_file: Which file this chunk came from (for context)
        chunk_index: Index of the chunk (for logging)

    Returns:
        ExtractionResult with lists of entities and relationships found
    """
    # For very short chunks there's nothing meaningful to extract
    if len(chunk_text.strip()) < 50:
        return {"entities": [], "relationships": []}

    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,  # Deterministic extraction, not creative
    )

    prompt = EXTRACTION_PROMPT.format(
        chunk_text=chunk_text[
            :2000
        ],  # Cap at 2000 chars to control cost, chunk_max_chars is set to 1200
        source_file=source_file,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        # Strip markdown fences if the LLM added them anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result: ExtractionResult = json.loads(raw)

        # Basic validation — ensure expected keys exist
        if "entities" not in result or "relationships" not in result:
            return {"entities": [], "relationships": []}

        print(
            f"    Chunk {chunk_index}: "
            f"{len(result['entities'])} entities, "
            f"{len(result['relationships'])} relationships"
        )
        return result

    except (json.JSONDecodeError, KeyError, Exception) as e:
        # Extraction failing should never crash the ingestion pipeline
        print(f"    Chunk {chunk_index}: extraction failed ({e}), skipping")
        return {"entities": [], "relationships": []}


def extract_entities_from_query(query: str) -> list[dict]:
    """
    Extract entities from a user query for graph traversal.
    Uses a more aggressive prompt than chunk extraction since
    queries are short and often lack explicit named entities.

    Args:
        query: The user's question

    Returns:
        List of entity dicts with name, type, description
    """
    import json

    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model=settings.llm_model, temperature=0)

    prompt = QUERY_EXTRACTION_PROMPT.format(query=query)

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        entities = result.get("entities", [])
        print(
            f"  Graph: extracted entities from query → {[e['name'] for e in entities]}"
        )
        return entities

    except Exception as e:
        print(f"  Graph: query extraction failed ({e})")
        return []


"""
**The flow for one chunk:**

chunk.page_content
       ↓
  LLM prompt (EXTRACTION_PROMPT)
       ↓
  JSON response: { entities: [...], relationships: [...] }
       ↓
  ExtractionResult (typed dict)
"""
