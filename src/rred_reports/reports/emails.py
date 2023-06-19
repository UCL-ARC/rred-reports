"""Emailing of reports to users"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from exchangelib import Account, FileAttachment, HTMLBody, Mailbox, Message

from rred_reports.redcap.interface import top_level_dir
from rred_reports.reports.auth import RREDAuthenticator


def formatted_mail_content(school_name: str, start_year: int, end_year) -> dict:
    """Function to return properly formatted mail subject and content
    Uses exchangelib HTMLBody to properly format bold text, lists and line breaks

    Args:
        school_name (str): Name of relevant school
        start_year (int): Report start year
        end_year (int): Report end year

    Returns:
        dict: Dictionary containing email subject and body
    """
    start_year = str(start_year)
    end_year = str(end_year)
    start_year_short = start_year[2:]
    end_year_short = end_year[2:]
    subject = f"Reading Recovery Annual Report for {school_name} {start_year_short}-{end_year_short}"

    body_html = HTMLBody(
        f"""<html>
    <body>
    Dear Reading Recovery Teacher<br>

    Please find attached the Reading Recovery Annual Report for your school for {start_year}-{end_year_short}.
    The report outlines the progress that pupils have made in Reading Recovery in your school during the year {start_year}-{end_year_short}.<br><br>

    Programmes that offered regular teaching have been recorded as complete, either Discontinued or Referred.
    Programmes that will continue after the summer break are recorded as 'Ongoing'.
    Any programme that <b>will not continue after the summer break</b> but is without exit assessment data has been recorded as 'Incomplete'.
    Any record started last year will still be available in your survey queue for {start_year}-{end_year_short} so that you can complete the pupil's record.<br><br>

    Whilst we have made every effort to ensure the accuracy of the data, which has been fully quality assured,
    if you have significant concerns about the report, please email ioe.rred@ucl.ac.uk in the first instance.<br><br>

    Please note: It will not be possible to correct data input issues such as:
    <ul>
    <li>incorrect programme entry / birth dates</li>
    <li>inputting errors e.g. cases where a programme has been logged as discontinued when the exit data does not meet the required criteria for 'discontinued'</li>
    </ul>
    <br>
    Please use your paper-based records for data which were not logged in RRED surveys in time for this report to correct any inputting errors.<br><br>

    The report includes a summary table and tables presenting:
    <ol>
    <li>Pupil characteristics:</li>
    <ul>
    <li>Table 1 - Demographic Characteristics of pupils receiving Reading Recovery</li>
    <li>Table 2 - SEND status for pupils receiving Reading Recovery</li>
    </ul>
    <br>
    <li>The efficiency of the implementation:</li>
    <ul>
    <li>Table 3 - Length of completed programmes and programme outcomes</li>
    <li>Table 4 - Number of Reading Recovery lessons taught and missed in completed programmes</li>
    </ul>
    <br>
    <li>Pupil outcomes:</li>
    <ul>
    <li>Table 5 - Entry and Exit scores on literacy measures of pupils receiving literacy support</li>
    <li>Table 6 - Follow-up scores collected after pupils completed Reading Recovery</li>
    </ul>
    </ol>
    <br>
    The data in the report is fully anonymised in compliance with GDPR.
    Please share the data in the report with colleagues in school and with your teacher leader.
    The reporting of data enables Reading Recovery Europe to monitor how the programme is being implemented
    and will help the network to reflect on pupil progress in the past year and plan for the future.<br><br>

    Via ioe.rred@ucl.ac.uk, you will shortly receive a document with background information about the data
    collected and some prompts for reviewing the efficiency and effectiveness of your Reading Recovery implementation.<br><br>

    Yours sincerely<br><br>

    The RRED team
        </body>
        </html>
        """
    )

    return {"subject": subject, "body_html": body_html}


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
    attachment_path: Optional[Path]
    attachment_name: Optional[str]


class ReportEmailer:
    """Encapsulation of email data and methods"""

    @staticmethod
    def build_email(mail_content: EmailContent) -> Message:
        """Building the content of the email

        Args:
            mail_content (EmailContent): EmailContent object

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

        if mail_content.attachment_path is not None and mail_content.attachment_name is not None:
            attachment = FileAttachment()
            attachment.name = mail_content.attachment_name
            with mail_content.attachment_path.open(mode="rb") as pdf_attachment:
                attachment.content = pdf_attachment.read()
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

    def run(
        self,
        school_name: str,
        start_year: int,
        end_year: int,
        to_list: list[str],
        cc_to: Optional[list[str]] = None,
        report: Optional[Path] = None,
        report_name: Optional[str] = "RRED_Processed_Report.pdf",
        save_email: bool = False,
    ) -> bool:
        """Prepare, construct and send an email

        Args:
            school_name (str): School name
            start_year (int): Report start year
            end_year (int): Report end year
            to_list (list[str]): List of direct email recipients
            cc_to (Optional[list[str]], optional): List of email recipients in CC. Defaults to None.
            report (Optional[Path], optional): Path to the report to attach. Defaults to None.
            report_name (Optional[str], optional): Name of the attached file as viewed by recipient. Defaults to RRED_Processed_Report.pdf.
            save_email (bool, optional): Adds the email to the 'sent' mailbox of the authenticated account. Defaults to False.

        Returns:
            bool: Message send success status
        """

        if cc_to is None:
            cc_to = []
        content_template = formatted_mail_content(school_name, start_year, end_year)
        authenticator = RREDAuthenticator()
        email_content = EmailContent(
            account=authenticator.get_account(),
            recipients=to_list,
            cc_recipients=cc_to,
            subject=content_template["subject"],
            body=content_template["body_html"],
            attachment_path=report,
            attachment_name=report_name,
        )

        email = self.__class__.build_email(email_content)

        return self.__class__.send_email(email, save=save_email)


def school_mailer(school_id: str, year: int, mail_info: dict, report_name: str, reports_dir: Path = None):
    """Wrapper mailing function

    Args:
        school_id (str): School ID
        year (int): Starting year of report coverage
        mail_info (dict): Details of emails
        report_name (str, optional): Name of attached file. Defaults to "RRED_report.pdf".
        reports_dir (Path, optional): Path where the reports should be found

    Raises:
        ReportEmailerException: Exception raised if report directory does not exist.
    """
    emailer = ReportEmailer()

    if reports_dir is None:
        reports_dir = top_level_dir / "output" / "reports" / str(year) / "schools"

    try:
        assert reports_dir.exists()
    except AssertionError as error:
        message = f"Report directory {reports_dir} not found. Exiting."
        raise ReportEmailerException(message) from error

    report_path = reports_dir / f"report_{school_id}.pdf"

    emailer.run(
        school_name=mail_info["school_label"],
        start_year=year,
        end_year=year + 1,
        to_list=mail_info["mailing_list"],
        cc_to=None,
        report=report_path,
        report_name=report_name,
        save_email=True,
    )
