# Lesson 11: A/B experiment, change ONE thing and measure again.
#
# THE PROBLEM: for "What is the overdraft fee and the daily maximum?" keyword_correctness is low.
#   We suspect chunk_size. If we change chunk_size AND top_k AND the prompt, and the score
#   goes up, we will not know which change helped.
# THE FIX: change ONE variable, keep the rest the same, and score both versions:
#   v1: chunk_size=100,  top_k=1        v2: chunk_size=1500, top_k=1
#
# Real project: module_b_evaluation/demo.py, experiments "demo-v1-baseline" and "demo-v2-improved".
# This lesson splits the REAL project/documents/account_fees.md with the same splitter. With
#   top_k=1 the LLM sees ONE chunk; we assume the retriever finds the best one (the chunk
#   with "$35") and score that chunk with lesson 07's keyword check. No API key needed.

import re
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter

DOC = Path(__file__).parent.parent / "fintech-agent-observability-evaluation" / "project" / "documents" / "account_fees.md"
EXPECTED = "The overdraft fee is $35 per transaction, with a maximum of 3 overdraft fees per day ($105 maximum)."

text = DOC.read_text(encoding="utf-8")
key_terms = re.findall(r"\$[\d,.]+|\d+(?:\.\d+)?%?", EXPECTED.lower())   # ex: ["$35", "3", "$105"]

for version, chunk_size in [("v1", 100), ("v2", 1500)]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    chunks = splitter.split_text(text)
    # top_k=1: the LLM gets only the chunk that mentions $35
    for chunk in chunks:
        if "$35" in chunk:
            best_chunk = chunk
            break
    matches = 0
    for term in key_terms:
        if term in best_chunk.lower():
            matches += 1
    print(version + ": chunk_size=" + str(chunk_size) + ", top_k=1 ->", len(chunks), "chunks")
    print("    the LLM sees one chunk of", len(best_chunk), "characters")
    print("    has $35?", "$35" in best_chunk, "  has $105?", "$105" in best_chunk,
          "  best possible keyword score:", round(matches / len(key_terms), 2))

print()
print("Only chunk_size changed, so the jump comes from chunk_size: small chunks split the fee from the daily max.")
print("(The '3' counts in v1 because it appears inside '$35': keyword checks are rough.)")
print()

# Why demo.py uses num_repetitions=3: a real LLM scores differently on each run (slide 31).
v1_runs = [0.72, 0.58, 0.68]
total = 0
for score in v1_runs:
    total += score
print("Same agent, 3 runs:", v1_runs, "-> average", round(total / len(v1_runs), 2))
print("Compare versions by their averages, not by one lucky or unlucky run.")
