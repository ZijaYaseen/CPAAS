"""WhatsApp Business (Meta Cloud API) adapter."""

import hashlib
import hmac

import httpx

from src.core.config import settings
from src.core.logging import get_logger
from src.modules.channels.base import ChannelAdapter, NormalizedInbound, OutboundResult

logger = get_logger("channel.whatsapp")
GRAPH_URL = "https://graph.facebook.com/v21.0"


class WhatsAppAdapter(ChannelAdapter):
    channel_type = "whatsapp"

    def verify_signature(self, *, headers: dict, body: bytes, secret: str | None = None) -> bool:
        app_secret = secret or settings.whatsapp_app_secret
        signature = headers.get("x-hub-signature-256", "")
        if not signature or not app_secret:
            # In dev without a configured secret we skip verification.
            return not settings.is_production
        expected = "sha256=" + hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_inbound(self, payload: dict) -> list[NormalizedInbound]:
        out: list[NormalizedInbound] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                contacts = {c["wa_id"]: c for c in value.get("contacts", [])}
                for msg in value.get("messages", []):
                    wa_id = msg.get("from")
                    profile = contacts.get(wa_id, {}).get("profile", {})
                    out.append(
                        NormalizedInbound(
                            channel_type=self.channel_type,
                            external_message_id=msg.get("id"),
                            sender_identifier=wa_id,
                            sender_name=profile.get("name"),
                            content=msg.get("text", {}).get("body"),
                            channel_metadata={
                                "phone_number_id": phone_number_id,
                                "type": msg.get("type"),
                            },
                        )
                    )
        return out

    async def send(
        self, *, credentials: dict, recipient: str, content: str, media_urls=None
    ) -> OutboundResult:
        access_token = credentials.get("access_token")
        phone_number_id = credentials.get("phone_number_id")
        if not (access_token and phone_number_id):
            return OutboundResult(success=False, error="Missing WhatsApp credentials")
        url = f"{GRAPH_URL}/{phone_number_id}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": content},
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    url, json=body, headers={"Authorization": f"Bearer {access_token}"}
                )
            resp.raise_for_status()
            data = resp.json()
            ext_id = data.get("messages", [{}])[0].get("id")
            return OutboundResult(success=True, external_message_id=ext_id, raw=data)
        except httpx.HTTPError as exc:
            logger.warning("whatsapp_send_failed", error=str(exc))
            return OutboundResult(success=False, error=str(exc))
