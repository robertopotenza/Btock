#!/usr/bin/env python3
"""
SMTP mailer for the unattended Seeking Alpha -> Btock -> Gmail workflow.

Uses a Gmail "App Password" (requires 2-Step Verification on the sending
account), read from environment variables so the CI runner never has the
account's real password:

    GMAIL_SENDER_ADDRESS   the Gmail address to send from
    GMAIL_APP_PASSWORD     a 16-character app password generated at
                            https://myaccount.google.com/apppasswords
                            (the account owner creates this themselves;
                            it is never typed into chat)

This is independent of, and does not reuse, this Claude session's own
connected Gmail MCP tool -- a GitHub Actions runner cannot call that tool,
so it needs its own credential.
"""

import os
import smtplib
import ssl
import uuid
from email.message import EmailMessage


class MailerConfigError(RuntimeError):
    pass


def send_email(to_addr: str, subject: str, body: str) -> str:
    sender = os.environ.get("GMAIL_SENDER_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender or not app_password:
        raise MailerConfigError(
            "GMAIL_SENDER_ADDRESS / GMAIL_APP_PASSWORD are not set -- "
            "add them as repo secrets before enabling the schedule"
        )

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    local_message_id = f"<{uuid.uuid4()}@btock-cloud>"
    msg["Message-ID"] = local_message_id
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, app_password)
        server.send_message(msg)

    # SMTP doesn't hand back Gmail's internal message id; the Message-ID
    # header we set is the durable identifier we record instead.
    return local_message_id
