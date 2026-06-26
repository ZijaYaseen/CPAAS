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
        # Keys are already lowercased by the webhook router.
        # Cloudmailin "Multipart-Normalized" format nests email headers as flat keys:
        # headers[from], headers[to], headers[message_id], headers[subject], etc.
        # SendGrid/Mailgun use top-level: from, to, message-id, subject.
        logger.info("email_parse_inbound_keys", keys=list(payload.keys()))
        sender = (
            payload.get("headers[from]")      # Cloudmailin
            or payload.get("from")            # SendGrid / Mailgun
            or payload.get("sender")          # Mailgun alt
            or payload.get("envelope[from]")  # SMTP envelope fallback
            or ""
        )
        email_addr = sender.split("<")[-1].strip(">").strip() if "<" in sender else sender.strip()
        sender_name = (sender.split("<")[0].strip() if "<" in sender else None) or None
        logger.info("email_parse_inbound_sender", sender=sender, email_addr=email_addr)
        content = (
            payload.get("plain")         # Cloudmailin / SendGrid
            or payload.get("body-plain") # Mailgun
            or payload.get("text")       # SendGrid alt
            or payload.get("body-html")  # Mailgun HTML fallback
            or payload.get("html")       # Cloudmailin / SendGrid HTML fallback
        )
        to_addr = (
            payload.get("headers[to]")   # Cloudmailin
            or payload.get("recipient")  # Mailgun
            or payload.get("to")         # SendGrid
            or ""
        )
        msg_id = (
            payload.get("headers[message_id]")  # Cloudmailin
            or payload.get("message-id")        # standard lowercased
            or payload.get("message_id")
        )
        subject = (
            payload.get("headers[subject]")  # Cloudmailin
            or payload.get("subject")        # SendGrid / Mailgun
        )
        return [
            NormalizedInbound(
                channel_type=self.channel_type,
                external_message_id=msg_id,
                sender_identifier=email_addr,
                sender_name=sender_name,
                content=content,
                channel_metadata={
                    "subject": subject,
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
