# Lesson 14: output guards, check the answer before the customer sees it.
#
# THE PROBLEM: some questions are fine, but the ANSWER is not. Trap 3 in demo 1 showed the
#   account record (name, SSN digits) going to the LLM. The LLM can repeat it, or mention a
#   competitor, even when the question was harmless.
# THE FIX: check the agent's answer. Two kinds of action:
#   BLOCK the whole answer (SSN number, competitor name) -> send the safe fallback instead
#   REDACT a part (customer name) -> replace it with <PERSON> and send the rest
#
# Real project: module_c_guardrails/demo.py, Part 5 (Guardrails AI: RegexMatch, CompetitorCheck)
#   and Part 6 (Presidio, a local ML model that finds names it has never seen).
# The SSN regex is real. The competitor and name checks are stand-ins (simple word lists),
#   so this runs without installing Guardrails validators or the spaCy model.
#
# What is Presidio? Microsoft's open-source PII library (pip install presidio-analyzer
#   presidio-anonymizer). Not an API: it runs locally, free, no key, nothing leaves the
#   machine. Names come from a spaCy ML model (en_core_web_lg, ~400 MB, downloaded once);
#   emails, phones and IDs come from built-in pattern rules. Anonymizer swaps each hit
#   for a tag: "Alice Johnson" -> "<PERSON>".

import re

SAFE_FALLBACK = "I'm sorry, I can only answer questions about SecureBank's account fees, loans, transfers, and fraud policies."
COMPETITORS = ["Chase", "Wells Fargo", "Citi", "Bank of America", "Capital One"]
CUSTOMER_NAMES = ["Alice Johnson", "Alice"]   # stand-in for Presidio's name detection

answers = [
    "The overdraft fee is $35 per transaction.",
    "Your SSN on file is 123-45-6789.",
    "Unlike Chase Bank, we offer lower overdraft fees.",
    "Hello Alice! Your Premium Checking balance is $12,450.75.",
]

for answer in answers:
    print("agent said:", answer)
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", answer):
        print("    BLOCKED (SSN pattern) -> customer sees:", SAFE_FALLBACK)
        continue
    competitor = None
    for name in COMPETITORS:
        if name in answer:
            competitor = name
    if competitor:
        print("    BLOCKED (competitor: " + competitor + ") -> customer sees:", SAFE_FALLBACK)
        continue
    redacted = answer
    for name in CUSTOMER_NAMES:
        redacted = redacted.replace(name, "<PERSON>")
    if redacted != answer:
        print("    REDACTED -> customer sees:", redacted)
        continue
    print("    passed")
