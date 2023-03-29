from rred_reports.reports import ReportEmailConfig
from rred_reports.reports.emails import EmailContent, ReportEmailer


def test_send_email(mock_smtp_server, template_report_bytes):
    test_server = mock_smtp_server.host.return_value
    test_port = mock_smtp_server.port.return_value

    report_settings = ReportEmailConfig(
        sender="sender@domain",
        recipients=",".join(["recipient@domain"]),
        smtp_host=str(test_server),
        smtp_port=str(test_port),
    )
    report_emailer = ReportEmailer(report_settings)

    mail_content = EmailContent(
        sender=report_settings.sender,
        recipients=report_settings.recipients,
        subject="Test",
        body="Test",
        attachment=template_report_bytes,
        attachment_filename="test_report.docx",
    )

    test_email = report_emailer.build_email(mail_content)
    assert f"From: {mail_content.sender}" in test_email.as_string()
    assert f"To: {mail_content.recipients}" in test_email.as_string()
    assert f"attachment; filename={mail_content.attachment_filename}" in test_email.as_string()
    instance = mock_smtp_server.return_value
    assert instance.send_message.called_once_with(test_email)


def test_send_with_report_bytes(mocker, mock_smtp_server, template_report_bytes):
    test_server = mock_smtp_server.host.return_value
    test_port = mock_smtp_server.port.return_value

    build_email_mock = mocker.patch("rred_reports.reports.emails.ReportEmailer.build_email")
    send_email_mock = mocker.patch("rred_reports.reports.emails.ReportEmailer.send_email")

    report_settings = ReportEmailConfig(
        sender="sender@domain",
        recipients=",".join(["recipient@domain"]),
        smtp_host=str(test_server),
        smtp_port=str(test_port),
    )
    report_emailer = ReportEmailer(report_settings)
    report_emailer.send(template_report_bytes)

    build_email_mock.assert_called_once()
    send_email_mock.assert_called_once()


def test_send_without_report_bytes(mocker, mock_smtp_server):
    test_server = mock_smtp_server.host.return_value
    test_port = mock_smtp_server.port.return_value

    build_email_mock = mocker.patch("rred_reports.reports.emails.ReportEmailer.build_email")
    send_email_mock = mocker.patch("rred_reports.reports.emails.ReportEmailer.send_email")

    report_settings = ReportEmailConfig(
        sender="sender@domain",
        recipients=",".join(["recipient@domain"]),
        smtp_host=str(test_server),
        smtp_port=str(test_port),
    )
    report_emailer = ReportEmailer(report_settings)
    report_emailer.send(report=None)

    build_email_mock.assert_called_once()
    send_email_mock.assert_called_once()
