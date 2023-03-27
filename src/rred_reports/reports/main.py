from datetime import datetime
from typing import Any

import pytz

from rred_reports.reports import ReportSettings
from rred_reports.reports.emails import Content
from rred_reports.reports.emails import send as send_mail


def create():
    # stubbed out for now
    settings = ReportSettings(sender="h.moss@ucl.ac.uk", recipients=["h.moss@ucl.ac.uk"], smtp_host="isd-smtp.ucl.ac.uk", smtp_port="25")

    report = None

    send(settings, report)


def send(settings: ReportSettings, report: Any | None) -> bool:
    local_datetime = datetime.now(tz=pytz.timezone("EUROPE/LONDON"))
    now = local_datetime.strftime("%d/%m/%Y at %H:%M")

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


def main():
    create()


if __name__ == "__main___":
    main()
