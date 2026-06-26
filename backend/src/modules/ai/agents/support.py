"""Support agent — answers product/support questions grounded in the knowledge base."""

from agents import Agent

from src.modules.ai.model_provider import get_chat_model
from src.modules.ai.tools import MVP_TOOLS

DEFAULT_SUPPORT_PROMPT = (
    "You are a helpful customer support agent. Always use the search_knowledge_base tool "
    "to ground your answers in the organization's documentation before replying. You can "
    "look up contact info and order status (read-only). You CANNOT make account changes, "
    "issue refunds, create tickets, or modify any data. If the answer is not in the "
    "knowledge base, or the customer needs an action you cannot perform, clearly say you "
    "will escalate to a human agent and stop. Be concise, friendly, and accurate."
)


def build_support_agent(*, system_prompt: str | None = None) -> Agent:
    return Agent(
        name="Support",
        instructions=system_prompt or DEFAULT_SUPPORT_PROMPT,
        tools=MVP_TOOLS,
        model=get_chat_model(),
    )
