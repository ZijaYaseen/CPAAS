"""AI guardrails (MVP): input safety, output safety, tool restriction.

Applied by the executor around each run (kept independent of SDK-specific guardrail
hooks for clarity and testability).
"""

import re

from src.modules.ai.tools import enforce_read_only  # re-exported for callers

__all__ = ["check_input", "check_output", "enforce_read_only"]

# Naive prompt-injection / jailbreak signals (MVP heuristic).
_INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"disregard (the|all) (system|previous)",
    r"you are now",
    r"reveal your (system )?prompt",
    r"act as (an? )?(dan|developer mode)",
]

_PROFANITY = {"<add-org-specific-terms>"}  # placeholder; orgs customize via config


def check_input(text: str) -> tuple[bool, str | None]:
    """Return (ok, reason). ok=False means block + escalate to a human."""
    lowered = (text or "").lower()
    for pat in _INJECTION_PATTERNS:
        if re.search(pat, lowered):
            return False, "Possible prompt-injection attempt detected"
    return True, None


def check_output(text: str) -> tuple[bool, str | None]:
    """Validate the AI's response before it is sent to the customer."""
    lowered = (text or "").lower()
    # Block accidental disclosure of internal/system content.
    if "system prompt" in lowered or "as an ai language model" in lowered:
        return False, "Response contained disallowed content"
    # Block any claim of having performed a write action (AI is read-only in MVP).
    if re.search(r"\b(i have|i've|i)\s+(created|updated|deleted|refunded|issued)\b", lowered):
        return False, "AI attempted to claim a write action (not permitted in MVP)"
    return True, None
