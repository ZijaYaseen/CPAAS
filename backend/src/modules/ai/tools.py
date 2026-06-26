"""AI tool functions — READ-ONLY ONLY (MVP).

Constitution IV: the AI never accesses the DB directly; it calls these backend
tools. MVP restricts the AI to read-only operations. Write tools (create_ticket,
update_contact, send_broadcast) are intentionally NOT registered and are blocked
by :func:`enforce_read_only`.
"""

from agents import function_tool
from sqlalchemy import select

from src.modules.ai.context import get_tool_context
from src.modules.contacts.models import Contact
from src.modules.knowledge import service as knowledge_service

# Tools the AI is permitted to use in the MVP.
READ_ONLY_TOOLS: set[str] = {"search_knowledge_base", "get_contact_info", "get_order_status"}

# Write tools that must never be exposed to the AI in the MVP.
BLOCKED_WRITE_TOOLS: set[str] = {
    "create_ticket",
    "update_contact",
    "send_message",
    "send_broadcast",
    "delete_contact",
}


def enforce_read_only(tool_name: str) -> None:
    """Raise if a non-read-only tool is requested (defense in depth)."""
    if tool_name in BLOCKED_WRITE_TOOLS or tool_name not in READ_ONLY_TOOLS:
        raise PermissionError(f"Tool '{tool_name}' is not permitted (read-only AI in MVP)")


def _record(tool_name: str, input_: dict, output: dict) -> None:
    get_tool_context().tool_calls.append(
        {"tool_name": tool_name, "input": input_, "output": output}
    )


@function_tool
async def search_knowledge_base(query: str) -> str:
    """Search the organization's knowledge base for information relevant to the query."""
    ctx = get_tool_context()
    results = await knowledge_service.search(ctx.session, query=query, top_k=5)
    _record("search_knowledge_base", {"query": query}, {"count": len(results)})
    if not results:
        return "No relevant information was found in the knowledge base."
    return "\n\n---\n\n".join(r["content"] for r in results)


@function_tool
async def get_contact_info(contact_id: str) -> str:
    """Retrieve basic profile information for a known contact by their id."""
    ctx = get_tool_context()
    contact = await ctx.session.scalar(select(Contact).where(Contact.id == contact_id))
    if contact is None:
        _record("get_contact_info", {"contact_id": contact_id}, {"found": False})
        return "Contact not found."
    info = {
        "full_name": contact.full_name,
        "email": contact.email,
        "phone": contact.phone,
        "lifecycle_stage": contact.lifecycle_stage,
    }
    _record("get_contact_info", {"contact_id": contact_id}, {"found": True})
    return "; ".join(f"{k}: {v}" for k, v in info.items() if v)


@function_tool
async def get_order_status(order_id: str) -> str:
    """Look up the status of an order (stub — integrate with the order system later)."""
    _record("get_order_status", {"order_id": order_id}, {"stub": True})
    return (
        f"Order {order_id}: status lookup is not yet connected to an order system. "
        "Please ask the customer to check their confirmation email, or escalate."
    )


MVP_TOOLS = [search_knowledge_base, get_contact_info, get_order_status]
