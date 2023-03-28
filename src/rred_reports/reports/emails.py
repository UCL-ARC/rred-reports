"""Emailing of reports to users"""
from dataclasses import dataclass
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Any

import pytz

from rred_reports.reports import ReportSettings


@dataclass
class EmailContent:
    sender: str
    recipients: str
    subject: str
    body: str
    attachment: bytes | None
    attachment_filename: str | None
    smtp_host: str
    smtp_port: int


def build_email(content: EmailContent) -> MIMEMultipart:
    message = MIMEMultipart("mixed")
    message["From"] = content.sender
    message["To"] = content.recipients
    message["Subject"] = content.subject
    message.attach(MIMEText(content.body))

    if content.attachment is not None:
        mime_application = MIMEApplication(content.attachment)
        mime_application.add_header("Content-Disposition", f"attachment; filename={content.attachment_filename}")
        message.attach(mime_application)

    return message


def send_email(smtp_host: str, smtp_port: int, message: MIMEMultipart) -> None:
    smtp = SMTP(host=smtp_host, port=smtp_port)
    result = smtp.send_message(message)
    smtp.quit()
    return result


def create_and_send():
    # stubbed out for now
    settings = ReportSettings(sender="h.moss@ucl.ac.uk", recipients=["h.moss@ucl.ac.uk"], smtp_host="isd-smtp.ucl.ac.uk", smtp_port="25")

    report = None

    send(settings, report)


def send(settings: ReportSettings, report: Any | None) -> bool:
    local_datetime = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
    now = local_datetime.strftime("%d/%m/%Y at %H:%M")

    email_content = EmailContent(
        sender=settings.sender,
        recipients=",".join(settings.recipients),
        subject="RRED Processed Report",
        body=f"Report processed on {now}.",
        attachment=report,
        attachment_filename="RRED_Processed_Report.docx",
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
    )
    email = build_email(email_content)
    send_email(email_content.smtp_host, email_content.smtp_port, email)

    return True
