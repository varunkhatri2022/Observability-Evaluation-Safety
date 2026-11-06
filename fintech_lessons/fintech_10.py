# Lesson 10: G-Eval, scoring a quality with no right number, and a pass/fail gate.
#
# THE PROBLEM: the escalation agent has no context and no number to check.
#   keyword_correctness and faithfulness cannot tell a kind reply from a cold one.
# THE FIX: G-Eval (from the open-source DeepEval library). You write the criteria in plain
#   English and a judge LLM scores the answer from 0 to 1. A threshold turns the score into
#   PASS or FAIL, so a test can fail a build when quality drops (CI/CD, slide 37).
#
# Real project: module_b_evaluation/solution.py:
#   GEval(name="Empathy", criteria="1) Acknowledge the customer's frustration ...", threshold=0.7)
# Here the judge is a stand-in: it counts how many of the 4 criteria the answer meets,
#   using a few signal words. Same output every run, no API key.

THRESHOLD = 0.7

# The 4 criteria from the project's G-Eval, with signal words for our stand-in judge
criteria = [
    ("acknowledges frustration", ["sorry", "frustrat"]),
    ("validates feelings", ["understand", "concern"]),
    ("offers a clear next step", ["specialist", "follow up"]),
    ("gives contact info", ["1-800", "support@"]),
]

answers = [
    "I'm so sorry this happened, and I understand how worrying it is. A senior specialist will "
    "follow up today. You can also reach us at 1-800-555-0199.",
    "Your request has been logged.",
]


def judge(answer):
    # Stand-in for the G-Eval judge LLM: fraction of criteria met
    met = 0
    for name, words in criteria:
        for word in words:
            if word in answer.lower():
                met += 1
                break
    return met / len(criteria)


for answer in answers:
    score = judge(answer)
    print("answer:", answer)
    if score >= THRESHOLD:
        print("    empathy =", score, " PASS")
    else:
        # DeepEval's assert_test() raises AssertionError here, so the CI build fails
        print("    empathy =", score, " FAIL (below", THRESHOLD, "-> CI build fails, change is not merged)")

print()
print("Same idea for any quality you can describe in words: politeness, no policy claims, clarity.")
