def human_node(state):
    print("\n Escalation triggered!")
    print("User Query:", state["query"])

    human_response = input(" Enter human response: ")

    return {
        **state,
        "answer": human_response,
        "escalated": True
    }