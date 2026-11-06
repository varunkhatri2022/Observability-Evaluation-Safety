# Lesson 15: the full pipeline, logging every decision, and what to do when a guard breaks.
#
# THE PROBLEM: guards run silently. How many queries did we block today? Which guard?
#   And if the Moderation API is down, do we stop serving customers?
# THE FIX:
#   1. Log every guard decision (guard, decision, reason), but a HASH of the query,
#      never the raw text: it may contain PII.
#   2. Input guard broken -> FAIL-OPEN: let the query through, other guards still run.
#      Output guard broken -> FAIL-CLOSED: send the safe fallback, never an unchecked answer.
#   3. The customer always sees the same fallback, never WHY: that would help attackers.
#
# Real project: guarded_pipeline() in module_c_guardrails/demo.py; slides 48-50.
# Guards and agent are scripted; "moderation_down" pretends the API is unreachable.

import hashlib
import json

SAFE_FALLBACK = "I'm sorry, I can only answer questions about SecureBank's account fees, loans, transfers, and fraud policies."


def log_event(guard, decision, reason, query):
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:12]   # same value every run
    print("    LOG", json.dumps({"guard": guard, "decision": decision, "reason": reason, "query_hash": query_hash}))


def guarded_pipeline(query, moderation_down=False, output_guard_down=False):
    # Input guard (fail-OPEN)
    if moderation_down:
        log_event("moderation", "error", "API unreachable", query)   # keep going
    elif "bomb" in query.lower():
        log_event("moderation", "blocked", "violence", query)
        return SAFE_FALLBACK
    answer = "The overdraft fee is $35 per transaction."              # scripted agent
    # Output guard (fail-CLOSED)
    if output_guard_down:
        log_event("output_guard", "error", "validator crashed", query)
        return SAFE_FALLBACK
    log_event("output_guard", "passed", "", query)
    return answer


print("1. Harmful question")
print("    customer sees:", guarded_pipeline("How do I make a bomb?"))
print("2. Normal question, Moderation API is down (fail-open)")
print("    customer sees:", guarded_pipeline("What is the overdraft fee?", moderation_down=True))
print("3. Normal question, output guard crashes (fail-closed)")
print("    customer sees:", guarded_pipeline("What is the overdraft fee?", output_guard_down=True))
print()
print("Cases 1 and 3 show the customer the same message. Only the log knows why.")
