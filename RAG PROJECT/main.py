from src.ingestion import load_and_chunk, create_vector_store
from src.graph import build_graph

# STEP 1: Run once to create embeddings
print("Loading and processing PDF...")
chunks = load_and_chunk("data/knowledge1.pdf")
create_vector_store(chunks)
print("Vector DB created!")


# STEP 2: Build graph
graph = build_graph()

print("\n Chatbot ready! Type 'exit' to quit.\n")

# STEP 3: Chat loop
while True:
    query = input("\nAsk your question: ")

    if query.lower() == "exit":
        break

    initial_state = {
        "query": query,
        "context": "",
        "answer": "",
        "confidence": 0.0,
        "intent": "",
        "escalated": False
    }

    # Capture the final state returned by the graph
    final_state = graph.invoke(initial_state)
    
    # Print the answer directly if the node didn't already
    print(f"\nFinal Response: {final_state['answer']}")