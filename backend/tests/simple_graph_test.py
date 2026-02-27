from dotenv import load_dotenv

from app.rag.graph.graph_retriever import retrieve_chunks_from_graph
from app.rag.graph.knowledge_graph import load_graph

load_dotenv()

graph = load_graph()

query = "what is our pro pricing plan?"

indices = retrieve_chunks_from_graph(query, graph)

print(f"Graph returned chunk indices: {indices}")

print("Nodes containing 'pro':")
for node in graph.nodes():
    if "pro" in node.lower():
        print(f"  '{node}'")

print("\nNodes containing 'pric':")
for node in graph.nodes():
    if "pric" in node.lower():
        print(f"  '{node}'")
