# Lesson 01: the PROBLEM, a silent failure. We only see the final answer.
#
# THE PROBLEM: the customer asks "What is the overdraft fee?". The policy says $35.
#   We run the agent three times. Each run has a different bug hidden inside:
#     run 1: the supervisor routes to the wrong agent
#     run 2: the retriever returns the wrong chunk
#     run 3: the LLM gets the right chunk but makes up a number
#   app.invoke() returns only the final state. Runs 2 and 3 both answer "$25",
#   but they need different fixes (fix retrieval vs fix the prompt/model).
# THE FIX: fintech_02.py runs the same graph with app.stream() and sees every node.
#
# Real project: project/fintech_support_agent.py has the same nodes and routing.
# The LLM and the retriever are scripted here, so no API key is needed.

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class SupportState(TypedDict):
    query: str
    intent: str    # "policy" or "escalation"
    context: str   # the chunk the LLM saw
    response: str
    bug: str       # lesson only: which bug to simulate


# Real lines from project/documents/account_fees.md
OVERDRAFT_CHUNK = "Overdraft fee: $35 per transaction"
WIRE_CHUNK = "Domestic outgoing wire: $25"


def classify_intent(state: SupportState) -> dict:
    # Supervisor. Real project: one LLM call that returns the category name.
    if state["bug"] == "routing":
        return {"intent": "escalation"}
    return {"intent": "policy"}


def policy_agent(state: SupportState) -> dict:
    # Real project: retriever -> LLM, both inside this one node.
    if state["bug"] == "retrieval":
        context = WIRE_CHUNK                       # wrong chunk...
        answer = "The overdraft fee is $25."       # ...and the LLM repeats its $25
    elif state["bug"] == "hallucination":
        context = OVERDRAFT_CHUNK                  # right chunk...
        answer = "The overdraft fee is $25."       # ...but the LLM makes up $25
    else:
        context = OVERDRAFT_CHUNK
        answer = "The overdraft fee is $35."
    return {"context": context, "response": answer}


def escalation_agent(state: SupportState) -> dict:
    return {"response": "I'm sorry about '" + state["query"] + "'. A specialist will contact you."}


def route_by_intent(state: SupportState) -> str:
    if state["intent"] == "escalation":
        return "escalation_agent"
    return "policy_agent"


graph = StateGraph(SupportState)
graph.add_node("classify_intent", classify_intent)
graph.add_node("policy_agent", policy_agent)
graph.add_node("escalation_agent", escalation_agent)
graph.add_edge(START, "classify_intent")  # the project writes this as graph.set_entry_point("classify_intent")
graph.add_conditional_edges("classify_intent", route_by_intent)
graph.add_edge("policy_agent", END)
graph.add_edge("escalation_agent", END)
app = graph.compile()


query = "What is the overdraft fee?"
print("Question:", query)
print("Policy says: $35\n")

for run, bug in [(1, "routing"), (2, "retrieval"), (3, "hallucination")]:
    result = app.invoke({"query": query, "bug": bug})
    print("run", run, "answer:", result["response"])

print("\nRuns 2 and 3 look identical. Which one needs a retrieval fix, and which a prompt fix?")
print("From the answer alone, you cannot tell.")
