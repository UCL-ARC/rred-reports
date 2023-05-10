"""Emailing of reports to users"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytz
from exchangelib import Account, FileAttachment, Mailbox, Message

from rred_reports.reports.auth import RREDAuthenticator


class ReportEmailerException(Exception):
    """Custom exception generator for the ReportEmailer class"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


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
        message = Message(
            account=mail_content.account,
            subject=mail_content.subject,
            body=mail_content.body,
            to_recipients=recipients,
            cc_recipients=mail_content.cc_recipients,
        )

        if mail_content.attachment is not None:
            attachment = FileAttachment(name=mail_content.attachment_filename, content=mail_content.attachment)
            message.attach(attachment)
        return message

    @staticmethod
    def send_email(message: Message, save: bool = False) -> bool:
        """Sends the defined email.

        Also can save a copy in the sent mailbox via
        the call to `send_and_save()`

        Args:
            message (Message): Constructed message to send
        Returns:
            process_status (bool): Did the message successfully send?
        """
        process_success = False
        if save:
            try:
                message.send_and_save()
                process_success = True
                return process_success
            except Exception as err:
                message = "An error occurred emailing this report."
                raise ReportEmailerException(message) from err
        else:
            try:
                message.send()
                process_success = True
                return process_success
            except Exception as err:
                message = "An error occurred emailing this report."
                raise ReportEmailerException(message) from err

    def run(self, to_list: list[str], cc_to: Optional[list[str]] = None, report: Optional[bytes] = None, save_email: bool = False) -> bool:
        """Prepare, construct and send an email

        Args:
            report (bytes | None): Optionally attach a report to the email

        Returns:
            bool: Did the message successfully send?
        """
        local_datetime_now = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
        datetime_now_string = local_datetime_now.strftime("%d/%m/%Y at %H:%M")

        if cc_to is None:
            cc_to = []

        authenticator = RREDAuthenticator()
        email_content = EmailContent(
            account=authenticator.get_account(),
            recipients=to_list,
            cc_recipients=cc_to,
            subject="RRED Report",
            body=f"Report processed {datetime_now_string}.",
            attachment=report,
            attachment_filename="RRED_Processed_Report.docx",
        )
        email = self.build_email(email_content)

        return self.send_email(email, save=save_email)
