# Lesson 16: tokens -> dollars. Where does the money go?
#
# THE PROBLEM: the bill says "$X this month", but which part of the agent costs money?
#   Every question makes 2 LLM calls (supervisor + agent), and the system prompts are
#   sent again on EVERY call.
# THE FIX: count tokens locally with tiktoken (no API call, $0), multiply by the price.
#   cost = input_tokens x input_price + output_tokens x output_price
#
# Real project: module_d_cost_optimization/demo.py, Segment 1 (same encoder, same prices).
# Token counts are real; the "answer" sizes are typical values from slide 57.
#
# What is a token? The unit an LLM reads, writes and bills by: a word or piece of a word.
#   ex: "What is the overdraft fee?" = 5 words, 7 tokens:
#       | What | is | the | overd | raft | fee | ? |
#   Common words are 1 token; rare words, numbers and IDs are several. You pay per token.
# What is tiktoken? OpenAI's open-source tokenizer library (pip install tiktoken).
#   It splits text into tokens exactly the way the model will, so you can count tokens
#   BEFORE calling the API. Runs locally, free, no API key. On first use it downloads
#   the model's token table once, then works offline.
#   (On average, 1 token is about 4 characters of English text.)
#   It counts any text, prompt or response, but it can't PREDICT the response length
#   before the call. So: tiktoken before the call (fit and trim the prompt, estimate cost);
#   the API's usage numbers after the call (the exact tokens you are billed for, e.g.
#   get_openai_callback() in demo.py, or the token badge in LangSmith).

import tiktoken

PRICE_IN = 0.15 / 1_000_000    # gpt-4o-mini, $ per input token  (slide 58)
PRICE_OUT = 0.60 / 1_000_000   # $ per output token: 4x more expensive

encoder = tiktoken.encoding_for_model("gpt-4o-mini")

# The real supervisor system prompt from project/fintech_support_agent.py
SUPERVISOR_PROMPT = (
    "Classify the customer query into exactly one category:\n"
    "- \"policy\" — general questions about account fees, loans, transfers, "
    "fraud policies, or banking products\n"
    "- \"account_status\" — requests to check balance, view transactions, "
    "or look up a SPECIFIC account (usually contains an account number like ACC-XXXXX)\n"
    "- \"escalation\" — complaints, frustration, requests for a manager, "
    "fraud reports, or complex issues needing human attention\n\n"
    "Respond with ONLY the category name."
)
supervisor_tokens = len(encoder.encode(SUPERVISOR_PROMPT))
print("Supervisor prompt:", supervisor_tokens, "tokens, sent on every question")
print("    at 1,000 questions/day:", supervisor_tokens * 1000, "tokens/day just for this prompt")
print()

# One question per agent, as 2 LLM calls: (supervisor in, supervisor out, agent in, agent out)
# Policy agent input is MEASURED: 113 (its prompt + the question) + 918 (5 retrieved chunks
#   of 1000 chars, real documents, see lesson 17). All other sizes are TYPICAL values from
#   slide 57, not measured: only a live LLM call gives real output sizes.
questions = [
    ("policy      'What is the overdraft fee?'", 100, 3, 113 + 918, 100),   # agent prompt carries the chunks
    ("account     'Balance on ACC-12345?'", 100, 3, 300, 65),               # agent prompt carries the account JSON
    ("escalation  'I'm furious!'", 100, 3, 120, 95),                        # no retrieval
]
print("Cost per question (policy input measured; other sizes typical, from slide 57):")
for name, sup_in, sup_out, agent_in, agent_out in questions:
    tokens_in = sup_in + agent_in
    tokens_out = sup_out + agent_out
    cost = tokens_in * PRICE_IN + tokens_out * PRICE_OUT
    print(name)
    print("    supervisor: in", sup_in, "+ out", sup_out, "   agent: in", agent_in, "+ out", agent_out)
    print("    total: in", tokens_in, "+ out", tokens_out, "tokens -> $" + format(cost, ".6f"))
    print("    = " + str(tokens_in) + " x $0.15/1M + " + str(tokens_out) + " x $0.60/1M")
    print("    1,000 questions: $" + format(cost * 1000, ".2f") + "    10,000 questions: $" + format(cost * 10000, ".2f"))

print()
print("Policy costs the most: the retrieved chunks make its prompt big.")
print("So the first thing to optimise is the context we send (lesson 17).")
