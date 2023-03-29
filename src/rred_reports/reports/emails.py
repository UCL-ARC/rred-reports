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
    """Email content class"""

    sender: str
    recipients: str
    subject: str
    body: str
    attachment: bytes | None
    attachment_filename: str | None


@dataclass
class ReportEmailer:
    """Encapsulation of email data and methods"""

    settings: ReportEmailConfig

    @staticmethod
    def build_email(content: EmailContent) -> MIMEMultipart:
        """Static method for building email content

        Args:
            content (EmailContent): EmailContent object

        Returns:
            MIMEMultipart: Email body as MIMEMultipart object
        """
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
    def send_email(smtp_host: str, smtp_port: int, message: MIMEMultipart) -> dict:
        """_summary_

        Args:
            smtp_host (str): SMTP server hostname
            smtp_port (int): SMTP server port
            message (MIMEMultipart): Message to send

        Returns:
            result (dict): dictionary with one entry for each recipient that was refused
                Each entry contains a tuple of an SMTP error code and error message
        """
        smtp = SMTP(host=smtp_host, port=smtp_port)
        result = smtp.send_message(message)
        smtp.quit()
        return result

    def send(self, report: bytes | None) -> dict:
        """Prepare, construct and send an email

        Args:
            report (bytes | None): Optionally attach a report to the email

        Returns:
            dict: Dictionary of SMTP error codes and messages.
                Empty if all email successfully sent to all recipients.
        """
        local_datetime = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
        now = local_datetime.strftime("%d/%m/%Y at %H:%M")

        email_content = EmailContent(
            sender=self.settings.sender,
            recipients=",".join(self.settings.recipients),
            subject="RRED Processed Report",
            body=f"Report processed {now}.",
            attachment=report,
            attachment_filename="RRED_Processed_Report.docx",
        )
        email = self.build_email(email_content)
        return self.send_email(self.settings.smtp_host, self.settings.smtp_port, email)
