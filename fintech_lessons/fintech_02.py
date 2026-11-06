# Lesson 02: the FIX, look inside every node.
#
# THE PROBLEM (fintech_01.py): app.invoke() returns only the final state. Runs 2 and 3
#   both answer "$25", and we cannot tell which step failed.
# THE FIX: same graph, same three bugs. We call app.stream(..., stream_mode="updates")
#   instead of app.invoke(). LangGraph then hands us what EACH node wrote, in order.
#   Read them in order: classify_intent -> agent. The first wrong value is the bug.
#
# Real project: LangGraph already knows every step. With LANGCHAIN_TRACING_V2=true,
#   LangSmith collects the same information (plus prompts, tokens, latency) and shows
#   it as a run tree in the browser. No logging code needed.

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
    print("run", run)
    # + NEW: app.stream() instead of app.invoke(). Same input; we get one update per node.
    for update in app.stream({"query": query, "bug": bug}, stream_mode="updates"):
        # ex: update = {"classify_intent": {"intent": "policy"}}
        for node_name, written in update.items():
            print("   ", node_name, written)
    print()

print("run 1: classify_intent wrote 'escalation'           -> fix the supervisor prompt")
print("run 2: context is the wire chunk ($25)              -> fix retrieval (chunk_size, top_k)")
print("run 3: context says $35, response still says $25    -> hallucination: fix the prompt or model")
