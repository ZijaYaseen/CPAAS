"""Support agent — answers product/support questions grounded in the knowledge base.

KB context is pre-fetched and injected into the system prompt so no tool calls are
needed. This avoids the Gemini thinking-model thought_signature requirement that the
OpenAI Agents SDK does not currently support.
"""

from agents import Agent

from src.modules.ai.model_provider import get_chat_model

DEFAULT_SUPPORT_PROMPT = (
    "You are a helpful customer support agent. Use the knowledge base context provided "
    "to answer the customer's question accurately. You CANNOT make account changes, "
    "issue refunds, create tickets, or modify any data. If the answer is not in the "
    "context provided, or the customer needs an action you cannot perform, say you will "
    "escalate to a human agent. Be concise, friendly, and accurate."
)


def build_support_agent(*, system_prompt: str | None = None, kb_context: str = "") -> Agent:
    base = system_prompt or DEFAULT_SUPPORT_PROMPT
    instructions = base
    if kb_context:
        instructions = (
            f"{base}\n\n"
            "## Knowledge Base\n"
            "Use the following information to answer the customer:\n\n"
            f"{kb_context}"
        )
    return Agent(
        name="Support",
        instructions=instructions,
        tools=[],  # No tools — KB pre-injected; avoids thought_signature issue
        model=get_chat_model(),
    )
