# Lesson 08: MRR, did the retriever put the right document on top?
#
# THE PROBLEM: lesson 07's Q3 got the right agent but only half the numbers.
#   Was it the retriever (brought the wrong document) or the LLM (ignored the right one)?
# THE FIX: score the retriever on its own, with no LLM. For each question we know which
#   document holds the answer. Look where that document sits in the retriever's list:
#     rank 1 -> 1/1 = 1.0     rank 2 -> 1/2 = 0.5     rank 3 -> 1/3 = 0.33     not there -> 0
#   That is the Reciprocal Rank. MRR (Mean Reciprocal Rank) is its average over all questions.
#
# Real project: module_b_evaluation/solution.py runs 10 questions through the real retriever
#   (retriever.invoke) and uses the same rank loop. The lists below are the example from slide 35.


# Example: the relevant document is DocA.
#   retrieved = [DocA, DocB]  -> DocA at rank 1 -> RR = 1/1 = 1.0
#   retrieved = [DocB, DocA]  -> DocA at rank 2 -> RR = 1/2 = 0.5
questions = [
    {"query": "What is the overdraft fee?",
     "relevant_source": "account_fees.md",
     "retrieved": ["account_fees.md", "transfer_policy.md", "loan_policy.md"]},
    {"query": "How much is a wire transfer?",
     "relevant_source": "transfer_policy.md",
     "retrieved": ["account_fees.md", "transfer_policy.md", "fraud_policy.md"]},
    {"query": "What is the late payment fee?",
     "relevant_source": "loan_policy.md",
     "retrieved": ["loan_policy.md", "account_fees.md", "transfer_policy.md"]},
]

reciprocal_ranks = []
for item in questions:
    # find the position (1, 2, 3...) of the relevant document; 0 = not retrieved
    rank = 0
    for i, source in enumerate(item["retrieved"], 1):
        if source == item["relevant_source"]:
            rank = i
            break
    rr = 1.0 / rank if rank > 0 else 0.0
    reciprocal_ranks.append(rr)
    print(item["query"])
    print("    retrieved:", item["retrieved"])
    print("    " + item["relevant_source"], "is at rank", rank, "-> RR =", round(rr, 2))

mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
print()
print("MRR = (" + " + ".join(str(round(r, 2)) for r in reciprocal_ranks) + ") /", len(reciprocal_ranks), "=", round(mrr, 3))
print()
print("1.0 = always rank 1 | above 0.8 = good | 0.5-0.8 = sometimes buried | below 0.5 = unreliable")
print("MRR looks only at the retriever. If MRR is high but answers are wrong, look at the LLM (lesson 09).")
