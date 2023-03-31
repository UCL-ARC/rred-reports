"""Emailing of reports to users"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytz
from exchangelib import Account, FileAttachment, Mailbox, Message

from rred_reports.reports.auth import RREDAuthenticator


@dataclass
class EmailContent:
    """Email content class"""

    account: Account
    recipients: list[str]
    cc_recipients: Optional[list[str]]
    subject: str
    body: str
    attachment: Optional[bytes]
    attachment_filename: Optional[str]


@dataclass
class ReportEmailer:
    """Encapsulation of email data and methods"""

    @staticmethod
    def build_email(mail_content: EmailContent) -> Message:
        """Building the content of the email

        Args:
            content (EmailContent): EmailContent object

        Returns:
            Message: Email (optionally with attachment) as exchangelib Message
        """

        recipients = [Mailbox(email_address=x) for x in mail_content.recipients]
        message = Message(account=mail_content.account, subject=mail_content.subject, body=mail_content.body, to_recipients=recipients)

        if mail_content.attachment is not None:
            attachment = FileAttachment(name=mail_content.attachment_filename, content=mail_content.attachment)
            message.attach(attachment)
        return message

    @staticmethod
    def send_email(message: Message, save: bool = False) -> None:
        """Sends the defined email.

        Also can save a copy in the sent mailbox via
        the call to `send_and_save()`

        Args:
            message (Message): Constructed message to send
        """
        if save:
            message.send_and_save()
        else:
            message.send()

    def run_emails(self, to_list: list[str], cc_to: Optional[list[str]] = None, report: Optional[bytes] = None) -> None:
        """Prepare, construct and send an email

        Args:
            report (bytes | None): Optionally attach a report to the email
        """
        local_datetime = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
        now = local_datetime.strftime("%d/%m/%Y at %H:%M")

        authenticator = RREDAuthenticator()
        email_content = EmailContent(
            account=authenticator.get_account(),
            recipients=to_list,
            cc_recipients=cc_to,
            subject="RRED Report",
            body=f"Report processed {now}.",
            attachment=report,
            attachment_filename="RRED_Processed_Report.docx",
        )
        email = self.build_email(email_content)
        self.send_email(email, save=False)
