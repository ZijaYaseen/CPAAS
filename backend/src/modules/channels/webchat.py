"""Web chat widget adapter.

Inbound: messages from the embeddable widget (our own JSON payload).
Outbound: delivered to the widget over the WebSocket gateway (no external provider),
so ``send`` is a no-op success — the realtime event already carries the message.
"""

from src.modules.channels.base import ChannelAdapter, NormalizedInbound, OutboundResult


class WebChatAdapter(ChannelAdapter):
    channel_type = "webchat"

    def verify_signature(self, *, headers: dict, body: bytes, secret: str | None = None) -> bool:
        # Public endpoint; abuse is mitigated by rate limiting (Phase 11), not signatures.
        return True

    def parse_inbound(self, payload: dict) -> list[NormalizedInbound]:
        return [
            NormalizedInbound(
                channel_type=self.channel_type,
                external_message_id=payload.get("client_message_id"),
                sender_identifier=payload["session_id"],
                sender_name=payload.get("visitor_name"),
                content=payload.get("content"),
                channel_metadata={"page_url": payload.get("page_url")},
            )
        ]

    async def send(
        self, *, credentials: dict, recipient: str, content: str, media_urls=None
    ) -> OutboundResult:
        # Outbound webchat delivery happens via the WebSocket event; nothing to call.
        return OutboundResult(success=True)
