from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph


from src.retriever import get_retriever
from src.hitl import human_node
# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3
)


# ----------- Answer Generation -----------

def generate_answer(context, query):
    prompt = f"""
    You are a customer support assistant.

    Answer ONLY from the given context.
    If answer is not in context, say "I don't know".

    Context:
    {context}

    Question:
    {query}
    """

    response = llm.invoke(prompt)
    return response.content


# ----------- Confidence + Intent -----------

def analyze_response(answer, context):
    if not context:
        return 0.0, "unknown"

    if "i don't know" in answer.lower():
        return 0.3, "unknown"

    return 0.85, "faq"


# ----------- Nodes -----------

def process_node(state):
    retriever = get_retriever()

    docs = retriever.invoke(state["query"])
    context = "\n".join([doc.page_content for doc in docs])

    answer = generate_answer(context, state["query"])
    confidence, intent = analyze_response(answer, context)

    return {
        **state,
        "context": context,
        "answer": answer,
        "confidence": confidence,
        "intent": intent
    }


def output_node(state):
    print("\n✅ Answer:\n", state["answer"])
    return state


def route_node(state):
    if state["confidence"] > 0.7:
        return "output"
    return "hitl"


# ----------- Graph Builder -----------

def build_graph():
    graph = StateGraph(dict)

    graph.add_node("process", process_node)
    graph.add_node("output", output_node)
    graph.add_node("hitl", human_node)

    graph.set_entry_point("process")

    graph.add_conditional_edges(
        "process",
        route_node,
        {
            "output": "output",
            "hitl": "hitl"
        }
    )

    graph.add_edge("hitl", "output")

    return graph.compile()