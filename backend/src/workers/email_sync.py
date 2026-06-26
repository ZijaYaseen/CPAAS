"""Email IMAP sync worker (Celery beat, every 30s).

Primary email inbound for the MVP is SendGrid Inbound Parse (the /webhooks/email
route). This periodic task is the IMAP fallback for accounts configured with IMAP
credentials. It is intentionally conservative: accounts without IMAP config are
skipped, so it is safe to run with no configuration.
"""

import imaplib
from email import message_from_bytes
from email.utils import parseaddr

from sqlalchemy import select

from src.celery_app import celery_app
from src.core.logging import get_logger
from src.modules.channels import service as channel_service
from src.modules.channels.models import ChannelAccount, ChannelType
from src.workers.db import run_async

logger = get_logger("worker.email_sync")


@celery_app.task(name="src.workers.email_sync.sync_inboxes")
def sync_inboxes() -> int:
    """Poll IMAP for every email channel account that has IMAP credentials."""
    return run_async(_sync)


async def _sync(db) -> int:
    accounts = (
        await db.scalars(
            select(ChannelAccount).where(
                ChannelAccount.channel_type == ChannelType.email.value,
                ChannelAccount.is_active.is_(True),
            )
        )
    ).all()
    processed = 0
    for account in accounts:
        creds = channel_service.get_credentials(account)
        if not creds.get("imap_host"):
            continue  # webhook-only account; nothing to poll
        try:
            processed += _poll_account(account, creds)
        except Exception as exc:  # noqa: BLE001
            logger.warning("imap_poll_failed", account=str(account.id), error=str(exc))
    return processed


def _poll_account(account: ChannelAccount, creds: dict) -> int:
    imap = imaplib.IMAP4_SSL(creds["imap_host"], int(creds.get("imap_port", 993)))
    imap.login(creds["imap_user"], creds["imap_password"])
    imap.select("INBOX")
    _typ, data = imap.search(None, "UNSEEN")
    ids = data[0].split()
    count = 0
    for num in ids:
        _typ, msg_data = imap.fetch(num, "(RFC822)")
        raw = msg_data[0][1]
        parsed = message_from_bytes(raw)
        name, addr = parseaddr(parsed.get("From", ""))
        payload = {
            "from": parsed.get("From", ""),
            "to": parsed.get("To", ""),
            "subject": parsed.get("Subject", ""),
            "text": _extract_text(parsed),
            "message_id": parsed.get("Message-ID"),
        }
        run_async(
            lambda db, p=payload: channel_service.process_inbound(
                db, channel_type=ChannelType.email.value, payload=p
            )
        )
        count += 1
    imap.logout()
    return count


def _extract_text(parsed) -> str:
    if parsed.is_multipart():
        for part in parsed.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="replace")
        return ""
    return parsed.get_payload(decode=True).decode(errors="replace")
