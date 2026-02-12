"""
Test Client for Streaming RAG Query
Run this to test the streaming endpoint from command line
"""

import asyncio
import aiohttp
import json


async def test_streaming_query(query: str):
    """
    Test the streaming query endpoint.

    Args:
        query: Question to ask
    """
    url = "http://localhost:8000/api/v1/query/stream"

    print(f"\n{'='*70}")
    print(f"STREAMING QUERY: {query}")
    print("=" * 70)
    print()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"query": query}, headers={"Content-Type": "application/json"}
        ) as response:

            if response.status != 200:
                print(f"Error: HTTP {response.status}")
                return

            print("Connected to stream...\n")

            sources = None
            answer_text = ""

            # Read the stream line by line
            async for line in response.content:
                line = line.decode("utf-8").strip()

                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix

                        event_type = data.get("type")
                        event_data = data.get("data")

                        if event_type == "status":
                            print(f"{event_data}")

                        elif event_type == "sources":
                            sources = event_data
                            num_chunks = data.get("num_chunks", len(sources))
                            print(f"Retrieved {num_chunks} relevant chunks\n")
                            print("Answer: ", end="", flush=True)

                        elif event_type == "token":
                            # Print token in real-time
                            print(event_data, end="", flush=True)
                            answer_text += event_data

                        elif event_type == "done":
                            print("\n\nStreaming complete!")
                            break

                        elif event_type == "error":
                            print(f"\nError: {event_data}")
                            break

                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                        continue

            # Print sources summary
            if sources:
                print(f"\n{'='*70}")
                print("SOURCES")
                print("=" * 70)
                for i, source in enumerate(sources, 1):
                    print(f"{i}. {source['file']} (chunk {source['chunk_index']})")
                    tags = []
                    if source.get("ai_summarized"):
                        tags.append("AI-summarized")
                    if source.get("has_tables"):
                        tags.append("Contains tables")
                    if source.get("has_images"):
                        tags.append("Contains images")
                    if tags:
                        print(f"   └─ {', '.join(tags)}")
                print("=" * 70)


async def main():
    """Run test queries."""

    # Example queries
    queries = [
        "What are the workspace requirements?",
        "What are the employee benefits?",
        "What is the remote work policy?",
    ]

    # Test first query
    await test_streaming_query(queries[1])

    # Uncomment to test more queries
    # for query in queries[1:]:
    #     await test_streaming_query(query)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
