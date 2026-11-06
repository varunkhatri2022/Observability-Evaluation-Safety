# Lesson 17: before / after. Cut the context, then check quality did not drop.
#
# THE PROBLEM: lesson 16 showed the policy question costs the most, and most of its input
#   is the retrieved chunks (918 of 1,031 agent input tokens).
# THE FIX: the before/after method (slides 60-61):
#   1. measure the baseline   2. change the config   3. measure again   4. check quality
#   Here we change the retrieval: fewer, smaller chunks.
#
# Real project: module_d_cost_optimization/demo.py, Segment 2:
#   BEFORE chunk_size=1000, top_k=5      AFTER chunk_size=400, top_k=3
#   (the demo measures with get_openai_callback(); here we count the context with tiktoken)
# Chunks are made from the REAL policy documents with the project's splitter. No API key.
# Same policy question and same other sizes as lesson 16, so the numbers line up.
# Quality: the 8 questions of Module B's hill-climb dataset. For each one we check how many
#   expected numbers the BEST single chunk still contains (lesson 07's keyword check, with
#   retrieval assumed perfect). If even the best chunk lost a fact, the answer can't have it.

import re
import sys
from pathlib import Path

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

PROJECT = Path(__file__).parent.parent / "fintech-agent-observability-evaluation"
sys.path.insert(0, str(PROJECT / "module_b_evaluation"))
from eval_dataset import HILL_CLIMB_EXAMPLES   # the same 8 questions as Module B's demo

PRICE_IN = 0.15 / 1_000_000    # gpt-4o-mini, $ per input token
PRICE_OUT = 0.60 / 1_000_000   # $ per output token
DOCS = PROJECT / "project" / "documents"
encoder = tiktoken.encoding_for_model("gpt-4o-mini")

# The policy question from lesson 16, everything except the retrieved chunks
SUP_IN, SUP_OUT = 100, 3       # supervisor (typical)
AGENT_PROMPT = 113             # policy prompt + question (measured)
AGENT_OUT = 100                # answer (typical)

def quality(chunks):
    # average over the 8 questions of: share of expected numbers found in the best chunk
    scores = []
    lost = []
    for example in HILL_CLIMB_EXAMPLES:
        terms = re.findall(r"\$[\d,.]+|\d+(?:\.\d+)?%?", example["outputs"]["answer"].lower())
        best = 0
        for chunk in chunks:
            found = 0
            for term in terms:
                if term.rstrip(".,") in chunk.lower():
                    found += 1
            best = max(best, found / len(terms))
        scores.append(best)
        if best < 1:
            lost.append(example["inputs"]["question"])
    return sum(scores) / len(scores), lost


costs = []
for name, chunk_size, overlap, top_k in [("BEFORE", 1000, 100, 5), ("AFTER", 400, 50, 3)]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks = []
    for file in DOCS.glob("*.md"):
        chunks += splitter.split_text(file.read_text(encoding="utf-8"))
    total = 0
    for chunk in chunks:
        total += len(encoder.encode(chunk))
    avg_chunk = total / len(chunks)
    context = round(avg_chunk * top_k)          # retrieved chunks sent to the policy agent

    tokens_in = SUP_IN + AGENT_PROMPT + context
    tokens_out = SUP_OUT + AGENT_OUT
    cost = tokens_in * PRICE_IN + tokens_out * PRICE_OUT
    costs.append(cost)
    print(name + ": chunk_size=" + str(chunk_size) + ", top_k=" + str(top_k))
    print("    chunks: avg", round(avg_chunk), "tokens x", top_k, "=", context, "tokens")
    print("    agent in:", AGENT_PROMPT, "+", context, "=", AGENT_PROMPT + context, "  total: in", tokens_in, "+ out", tokens_out,
          "-> $" + format(cost, ".6f"))
    print("    1,000 questions: $" + format(cost * 1000, ".2f") + "    10,000 questions: $" + format(cost * 10000, ".2f"))
    score, lost = quality(chunks)
    print("    quality (8 Module B questions): " + format(score, ".2f"))
    for question in lost:
        print("        lost a fact:", question)

print()
print("Cost per question cut by", str(round((1 - costs[1] / costs[0]) * 100)) + "%, but quality dropped too.")
print("Smaller chunks split facts that belong together (lesson 11 showed the same with $35 / $105).")
print()
print("So we don't stop here. Try the next config (chunk_size 600? top_k 4?), measure cost AND")
print("quality again, keep the cheapest config whose quality is still acceptable. Repeat.")
print("That is slide 66: there is no single best config, only the best trade-off for YOUR needs.")
