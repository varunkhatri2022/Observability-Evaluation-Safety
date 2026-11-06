# Lesson 07: evaluators, turning "looks right" into a score.
#
# THE PROBLEM: in lessons 01-03 we found bugs by opening traces one at a time.
#   That works for 4 questions, not for 400. And "the answer looks right" is not a number
#   you can compare between two versions of the agent.
# THE FIX: a dataset (each question + the EXPECTED intent and answer) and small functions,
#   called evaluators, that compare what the agent did with what we expected.
#   Each evaluator returns a score from 0 to 1.
#
# Real project: module_b_evaluation/demo.py uses these same two evaluators.
#   There LangSmith's evaluate() calls them for every question; here a plain loop does.
# The agent's outputs are scripted, so no API key is needed.

import re
from types import SimpleNamespace

# The dataset. Real project: module_b_evaluation/eval_dataset.py
dataset = [
    {"inputs": {"question": "What is the overdraft fee and the daily maximum?"},
     "outputs": {"intent": "policy",
                 "answer": "The overdraft fee is $35 per transaction, with a maximum of 3 overdraft fees per day ($105 maximum)."}},
    {"inputs": {"question": "I'm really upset about being charged $105 in one day! What is your overdraft policy?"},
     "outputs": {"intent": "policy",
                 "answer": "The overdraft fee is $35 per transaction, with a maximum of 3 overdraft fees per day ($105 maximum)."}},
    {"inputs": {"question": "What is the APR range for auto loans?"},
     "outputs": {"intent": "policy",
                 "answer": "Auto loan APR ranges from 4.49% to 12.99% for new vehicles and 5.49% to 14.99% for used vehicles."}},
]

# What the agent returned for each question (scripted).
agent_outputs = [
    {"intent": "policy", "answer": "The overdraft fee is $35 per transaction, up to 3 per day ($105 maximum)."},
    {"intent": "escalation", "answer": "I'm so sorry about this. A senior specialist will follow up with you."},
    {"intent": "policy", "answer": "For new vehicles, auto loan APRs range from 4.49% to 12.99%."},
]


def routing_evaluator(run, example):
    # Did the supervisor pick the right agent? 1 or 0.
    predicted = run.outputs.get("intent", "")
    expected = example.outputs.get("intent", "")
    score = 1.0 if predicted == expected else 0.0
    return {"key": "routing_accuracy", "score": score}


def keyword_correctness(run, example):
    # Which numbers from the expected answer also appear in the agent's answer?
    actual = run.outputs.get("answer", "").lower()
    expected = example.outputs.get("answer", "").lower()
    key_terms = re.findall(r"\$[\d,.]+|\d+(?:\.\d+)?%?|acc-\d+", expected)
    # ex: key_terms = ["$35", "3", "$105"]
    if not key_terms:
        return {"key": "keyword_correctness", "score": 0.5}
    found = []
    missing = []
    for term in key_terms:
        if term in actual:
            found.append(term)
        else:
            missing.append(term)
    score = round(len(found) / len(key_terms), 4)
    # + "comment": optional; LangSmith shows it next to the score
    comment = "found " + str(found) + ", missing " + str(missing)
    return {"key": "keyword_correctness", "score": score, "comment": comment}


routing_scores = []
keyword_scores = []
for i in range(len(dataset)):
    # LangSmith hands each evaluator two objects: run (what the agent did) and example (the dataset row)
    run = SimpleNamespace(outputs=agent_outputs[i])
    example = SimpleNamespace(inputs=dataset[i]["inputs"], outputs=dataset[i]["outputs"])

    routing =routing_evaluator(run, example)["score"]
    keyword_result = keyword_correctness(run, example)
    keyword = keyword_result["score"]
    routing_scores.append(routing)
    keyword_scores.append(keyword)
    print("Q" + str(i + 1) + ":", example.inputs["question"][:55])
    print("    agent result   :", run.outputs)       # run = what the agent returned
    print("    expected answer:", example.outputs)   # example = the dataset row
    print("    routing_accuracy    =", routing, "  (expected", example.outputs["intent"] + ", got", run.outputs["intent"] + ")")
    print("    keyword_correctness =", keyword, "  (" + keyword_result["comment"] + ")")

print()
print("routing_accuracy    average:", round(sum(routing_scores) / len(routing_scores), 2))
print("keyword_correctness average:", round(sum(keyword_scores) / len(keyword_scores), 2))
print()
print("Q2: routing = 0 -> the supervisor is the problem (the bug from demo 1, trap 2).")
print("Q3: routing = 1 but keyword = 0.5 -> right agent, half the numbers missing. Retriever or LLM?")
print("    These two evaluators cannot tell. Lessons 08 and 09 can.")
