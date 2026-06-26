"""Assemble the MVP agent graph: Router → Support → (human escalation)."""

from agents import Agent

from src.modules.ai.agents.router import build_router_agent
from src.modules.ai.agents.support import build_support_agent


def build_agent_graph(configs: dict[str, dict]) -> Agent:
    """Build the entry (router) agent wired to its specialists.

    ``configs`` maps agent_type -> {system_prompt}. Missing entries fall back to
    defaults. The chat model (Gemini via OpenAI-compat) is supplied by the model
    provider. Returns the router agent (the run entry point).
    """
    support_cfg = configs.get("support", {})
    router_cfg = configs.get("router", {})
    support_agent = build_support_agent(system_prompt=support_cfg.get("system_prompt"))
    return build_router_agent(
        support_agent=support_agent, system_prompt=router_cfg.get("system_prompt")
    )
