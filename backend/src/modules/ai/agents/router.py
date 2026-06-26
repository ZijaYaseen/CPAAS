"""Routing agent — classifies intent and hands off to the right specialist.

MVP: only the Support specialist exists (Sales/Billing are post-MVP). The router
hands off support/product questions to Support and escalates anything requiring a
write action or that it is unsure about.
"""

from agents import Agent

from src.modules.ai.model_provider import get_chat_model

DEFAULT_ROUTER_PROMPT = (
    "You are a routing assistant for a customer support inbox. Read the customer's message "
    "and decide how to handle it. For product questions, how-to help, troubleshooting, or "
    "general support, hand off to the Support specialist. If the request requires creating "
    "or changing data (refunds, account changes, new tickets), or you are unsure, do not "
    "attempt it — reply that a human agent will follow up. Never invent information."
)


def build_router_agent(*, support_agent: Agent, system_prompt: str | None = None) -> Agent:
    return Agent(
        name="Router",
        instructions=system_prompt or DEFAULT_ROUTER_PROMPT,
        handoffs=[support_agent],
        model=get_chat_model(),
    )
