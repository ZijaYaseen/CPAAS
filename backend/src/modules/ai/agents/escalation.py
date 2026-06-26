"""Human escalation: detect when the AI should defer to a human and signal it.

Escalation triggers: blocked guardrails, empty/low-confidence output, or the model
explicitly stating it will hand off. The executor records the reason on the AIRun
and drops an internal note on the conversation so an agent can take over with context.
"""

import re

_ESCALATION_SIGNALS = [
    r"escalat",
    r"human (agent|representative|support)",
    r"connect you (to|with) (a|our) (human|team|agent)",
    r"i'?m not able to help",
    r"can'?t help with that",
]


def should_escalate(output: str | None) -> bool:
    if not output or not output.strip():
        return True
    lowered = output.lower()
    return any(re.search(p, lowered) for p in _ESCALATION_SIGNALS)
