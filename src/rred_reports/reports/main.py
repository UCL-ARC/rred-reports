from datetime import datetime

import pytz

from rred_reports.reports import ReportSettings
from rred_reports.reports.email import Content
from rred_reports.reports.email import send as send_mail


def create():
    # stubbed out for now
    return None


def send(
    settings: ReportSettings,
) -> bool:
    local_datetime = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
    now = local_datetime.strftime("%d/%m/%Y at %H:%M")

    report = create()

    email_content = Content(
        sender=settings.sender,
        recipients=",".join(settings.recipients),
        subject="RRED Processed Report",
        body=f"Report processed on {now}.",
        attachment=report,
        attachment_filename="RRED_Processed_Report.docx",
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
    )

    send_mail(email_content)

    return True
