"""Emailing of reports to users"""
from dataclasses import dataclass
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

import pytz

from rred_reports.reports import ReportEmailConfig


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


@dataclass
class ReportEmailer:
    settings: ReportEmailConfig

    @staticmethod
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

    @staticmethod
    def send_email(smtp_host: str, smtp_port: int, message: MIMEMultipart) -> None:
        smtp = SMTP(host=smtp_host, port=smtp_port)
        result = smtp.send_message(message)
        smtp.quit()
        return result

    def send(self, report: bytes | None) -> bool:
        local_datetime = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
        now = local_datetime.strftime("%d/%m/%Y at %H:%M")

        email_content = EmailContent(
            sender=self.settings.sender,
            recipients=",".join(self.settings.recipients),
            subject="RRED Processed Report",
            body=f"Report processed {now}.",
            attachment=report,
            attachment_filename="RRED_Processed_Report.docx",
            smtp_host=self.settings.smtp_host,
            smtp_port=self.settings.smtp_port,
        )
        email = self.build_email(email_content)
        self.send_email(email_content.smtp_host, email_content.smtp_port, email)

        return True
