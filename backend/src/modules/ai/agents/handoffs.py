"""Assemble the MVP agent graph: Support agent directly (no router handoff).

MVP has only one specialist (Support). Routing via tool-based handoffs requires
thought_signature support in the Gemini thinking models which the OpenAI Agents
SDK does not provide, causing 400 errors. Skip the router and run Support directly.
Post-MVP: restore multi-agent graph once the SDK adds thought_signature support.
"""

from agents import Agent

from src.modules.ai.agents.support import build_support_agent


def build_agent_graph(configs: dict[str, dict]) -> Agent:
    """Return the Support agent as the single entry point for the MVP.

    ``configs`` maps agent_type -> {system_prompt}. Missing entries fall back to
    defaults defined in build_support_agent.
    """
    support_cfg = configs.get("support", {})
    return build_support_agent(system_prompt=support_cfg.get("system_prompt"))
