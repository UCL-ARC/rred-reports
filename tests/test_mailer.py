from rred_reports.reports import ReportEmailConfig
from rred_reports.reports.emails import EmailContent, ReportEmailer


def test_send_email(mock_smtp_server, template_report_bytes):
    test_server = mock_smtp_server.host.return_value
    test_port = mock_smtp_server.port.return_value

    report_settings = ReportEmailConfig(
        sender="sender@domain",
        recipients="recipient@domain",
        smtp_host=str(test_server),
        smtp_port=str(test_port),
    )
    report_emailer = ReportEmailer(report_settings)

    mail_content = EmailContent(
        sender="sender@domain",
        recipients="recipient@domain",
        subject="Test",
        body="Test",
        attachment=template_report_bytes,
        attachment_filename="test_report.docx",
        smtp_host=test_server,
        smtp_port=test_port,
    )

    test_email = report_emailer.build_email(mail_content)
    assert f"From: {mail_content.sender}" in test_email.as_string()
    assert f"To: {mail_content.recipients}" in test_email.as_string()
    assert f"attachment; filename={mail_content.attachment_filename}" in test_email.as_string()
    report_emailer.send_email(test_server, test_port, test_email)
    instance = mock_smtp_server.return_value

    assert instance.send_message.called_once_with(test_email)
