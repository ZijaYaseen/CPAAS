"""Email channel adapter.

Inbound: SendGrid Inbound Parse (multipart form) — parsed into a NormalizedInbound.
Outbound: SMTP via aiosmtplib using the channel account's stored credentials.
"""

from email.message import EmailMessage

import aiosmtplib

from src.core.config import settings
from src.core.logging import get_logger
from src.modules.channels.base import ChannelAdapter, NormalizedInbound, OutboundResult

logger = get_logger("channel.email")


class EmailAdapter(ChannelAdapter):
    channel_type = "email"

    def verify_signature(self, *, headers: dict, body: bytes, secret: str | None = None) -> bool:
        # SendGrid Inbound Parse is unsigned by default; restrict via network/allowlist
        # in production. Accept here (hardening adds a shared-secret path param).
        return True

    def parse_inbound(self, payload: dict) -> list[NormalizedInbound]:
        # Supports both Mailgun and SendGrid field names.
        sender = payload.get("from") or payload.get("sender", "")
        email_addr = sender.split("<")[-1].strip(">").strip() if sender else ""
        sender_name = (sender.split("<")[0].strip() if "<" in sender else None) or None
        content = (
            payload.get("plain")         # Cloudmailin
            or payload.get("body-plain") # Mailgun
            or payload.get("text")       # SendGrid
            or payload.get("body-html")  # Mailgun HTML fallback
            or payload.get("html")       # SendGrid HTML fallback
        )
        to_addr = payload.get("recipient") or payload.get("to") or payload.get("To", "")
        msg_id = (
            payload.get("Message-Id")   # Mailgun
            or payload.get("message_id")
            or payload.get("Message-ID")
        )
        return [
            NormalizedInbound(
                channel_type=self.channel_type,
                external_message_id=msg_id,
                sender_identifier=email_addr,
                sender_name=sender_name,
                content=content,
                channel_metadata={
                    "subject": payload.get("subject") or payload.get("Subject"),
                    "to": to_addr,
                },
            )
        ]

    async def send(
        self, *, credentials: dict, recipient: str, content: str, media_urls=None
    ) -> OutboundResult:
        host = credentials.get("smtp_host") or settings.smtp_host
        port = int(credentials.get("smtp_port") or settings.smtp_port)
        user = credentials.get("smtp_user") or settings.smtp_user
        password = credentials.get("smtp_password") or settings.smtp_password
        from_addr = credentials.get("from_address") or user
        if not (host and from_addr):
            logger.warning("email_send_missing_smtp", host=host, from_addr=from_addr)
            return OutboundResult(success=False, error="Missing SMTP configuration")

        message = EmailMessage()
        message["From"] = from_addr
        message["To"] = recipient
        message["Subject"] = credentials.get("default_subject", "Re: your message")
        message.set_content(content)
        try:
            await aiosmtplib.send(
                message,
                hostname=host,
                port=port,
                username=user or None,
                password=password or None,
                start_tls=port == 587,
            )
            return OutboundResult(success=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("email_send_failed", error=str(exc))
            return OutboundResult(success=False, error=str(exc))
