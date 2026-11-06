# Lesson 03: the same graph, traced in LangSmith.
#
# THE PROBLEM (fintech_02.py): app.stream() showed every node, but only in our terminal,
#   only for runs we started ourselves, and it was gone when the terminal closed.
# THE FIX: turn on LangSmith. Same graph, same three bugs, plain app.invoke().
#   We add no logging code: 3 environment variables, and every run is sent to LangSmith.
#   Then open smith.langchain.com -> project "week8-lessons" -> one trace per run.
#
# Needs a LangSmith API key in fintech-agent-observability-evaluation/.env:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=lsv2_pt_...
# No OpenAI key needed: the LLM is still scripted.

import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

# + NEW: read the keys from the project's .env file (never put keys in code)
load_dotenv(Path(__file__).parent.parent / "fintech-agent-observability-evaluation" / ".env")
os.environ["LANGCHAIN_PROJECT"] = "week8-lessons"  # the LangSmith project these traces go to

if os.environ.get("LANGCHAIN_TRACING_V2") != "true" or not os.environ.get("LANGCHAIN_API_KEY"):
    print("Tracing is off. Add LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY to the .env file.")
    raise SystemExit(1)


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

for run, bug in [(1, "routing"), (2, "retrieval"), (3, "hallucination")]:
    # + NEW: run_name labels the trace in LangSmith, so we can tell the 3 runs apart
    result = app.invoke({"query": query, "bug": bug}, config={"run_name": "run " + str(run) + ": " + bug})
    print("run", run, "answer:", result["response"])

print("\nOpen https://smith.langchain.com -> Tracing -> project 'week8-lessons'.")
print("Click 'run 2: retrieval' and 'run 3: hallucination': open policy_agent and compare its output.")
