"""Emailing of reports to users"""
from dataclasses import dataclass
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP


@dataclass
class Content:
    sender: str
    recipients: str
    subject: str
    body: str
    attachment: bytes | None
    attachment_filename: str | None
    smtp_host: str
    smtp_port: int


def send(content: Content) -> None:
    msg = MIMEMultipart("mixed")
    msg["From"] = content.sender
    msg["To"] = content.recipients
    msg["Subject"] = content.subject
    msg.attach(MIMEText(content.body))

    mime_application = MIMEApplication(content.attachment)
    mime_application.add_header("Content-Disposition", f"attachment; filename={content.attachment_filename}")
    msg.attach(mime_application)

    with SMTP(host=content.smtp_host, port=content.smtp_port) as smtp:
        smtp.send_message(msg)
