# Lesson 09: faithfulness vs correctness, with a judge LLM.
#
# THE PROBLEM: lesson 01's runs 2 and 3 both answered "$25" instead of "$35".
#   keyword_correctness gives both a 0. Same score, but different bugs:
#     run 2: the retriever brought the wrong chunk (fix retrieval)
#     run 3: the LLM had the right chunk and made up a number (fix the prompt or model)
# THE FIX: ask a second LLM, the "judge", two different questions:
#   faithfulness: is the answer supported by the CONTEXT the agent was given?
#   correctness:  does the answer match the EXPECTED answer from the dataset?
#   Together they point at the layer that failed.
#
# Real project: faithfulness_evaluator and correctness_evaluator in module_b_evaluation/solution.py.
#   Each sends a prompt to gpt-4o-mini, e.g. "Score 1.0 = every claim is supported by the
#   context ... Respond ONLY with JSON: {"score": ..., "reason": ...}".
# Here judge() is a stand-in for that LLM: it checks whether the dollar amount in the
#   answer appears in the reference text. Same output every run, no API key.

import re

EXPECTED = "The overdraft fee is $35 per transaction."

# The three runs from lesson 01: the context the agent saw, and its answer.
runs = [
    {"name": "run 1: no bug",
     "context": "Overdraft fee: $35 per transaction", "answer": "The overdraft fee is $35."},
    {"name": "run 2: retrieval bug",
     "context": "Domestic outgoing wire: $25", "answer": "The overdraft fee is $25."},
    {"name": "run 3: hallucination",
     "context": "Overdraft fee: $35 per transaction", "answer": "The overdraft fee is $25."},
]


def judge(answer, reference, reference_name):
    # Stand-in for the judge LLM: is the answer's dollar amount in the reference?
    # Like the real judge, it returns a score AND a one-line reason.
    amount = re.findall(r"\$\d+", answer)[0]               # ex: "$25"
    reference_amount = re.findall(r"\$\d+", reference)[0]  # ex: "$35"
    reason = "answer says " + amount + ", " + reference_name + " says " + reference_amount
    if amount == reference_amount:
        return 1.0, reason
    return 0.0, reason


for run in runs:
    faithfulness, f_reason = judge(run["answer"], run["context"], "context")   # vs what the agent SAW
    correctness, c_reason = judge(run["answer"], EXPECTED, "expected")         # vs the TRUTH
    print(run["name"])
    print("    context:", run["context"], "| answer:", run["answer"])
    print("    faithfulness =", faithfulness, " (" + f_reason + ")")
    print("    correctness  =", correctness, " (" + c_reason + ")")

print()
print("faithful 1, correct 1 -> all good")
print("faithful 1, correct 0 -> the LLM repeated a WRONG context: fix retrieval (check MRR, lesson 08)")
print("faithful 0, correct 0 -> the LLM ignored a right context: hallucination, fix prompt or model")
print()
print("A real judge is an LLM, so it costs one call per answer per evaluator, and its score varies a little.")
