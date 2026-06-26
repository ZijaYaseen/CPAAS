"""Channel adapter contract + the unified inbound message schema.

Every channel adapter converts provider-specific webhooks/payloads into a
``NormalizedInbound`` and knows how to send an outbound message. This is the
single seam that keeps the inbox channel-agnostic (constitution V).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedInbound:
    """A channel-agnostic representation of one inbound message."""

    channel_type: str
    external_message_id: str | None
    sender_identifier: str  # phone (whatsapp/sms), email address, or webchat session id
    content: str | None = None
    sender_name: str | None = None
    media_urls: list[str] = field(default_factory=list)
    channel_metadata: dict = field(default_factory=dict)
    timestamp: datetime | None = None


@dataclass
class OutboundResult:
    """Result of an outbound send attempt."""

    success: bool
    external_message_id: str | None = None
    error: str | None = None
    raw: dict = field(default_factory=dict)


class ChannelAdapter(ABC):
    """Base class for all channel adapters."""

    channel_type: str

    @abstractmethod
    def verify_signature(self, *, headers: dict, body: bytes) -> bool:
        """Validate an inbound webhook's authenticity (signature/secret)."""

    @abstractmethod
    def parse_inbound(self, payload: dict) -> list[NormalizedInbound]:
        """Convert a provider webhook payload into normalized inbound messages."""

    @abstractmethod
    async def send(
        self,
        *,
        credentials: dict,
        recipient: str,
        content: str,
        media_urls: list[str] | None = None,
    ) -> OutboundResult:
        """Deliver an outbound message via the provider."""
