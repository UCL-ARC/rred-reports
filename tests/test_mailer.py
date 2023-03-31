from rred_reports.reports.emails import EmailContent, ReportEmailer


def test_build_email_with_report(mock_ews_account, template_report_bytes):
    report_emailer = ReportEmailer()

    mail_content = EmailContent(
        account=mock_ews_account,
        recipients=["recipient@domain.com"],
        cc_recipients=None,
        subject="Test",
        body="Test",
        attachment=template_report_bytes,
        attachment_filename="test_report.docx",
    )

    test_email = report_emailer.build_email(mail_content)

    assert mail_content.subject == test_email.subject
    assert mail_content.recipients[0] == test_email.to_recipients[0].email_address
    assert mail_content.attachment_filename == test_email.attachments[0].name

    # instance = mock_smtp_server.return_value
    # assert instance.send_message.called_once_with(test_email)


def test_build_email_without_report(mock_ews_account):
    report_emailer = ReportEmailer()

    mail_content = EmailContent(
        account=mock_ews_account,
        recipients=["recipient@domain.com"],
        cc_recipients=None,
        subject="Test",
        body="Test",
        attachment=None,
        attachment_filename="test_report.docx",
    )

    test_email = report_emailer.build_email(mail_content)

    assert mail_content.subject == test_email.subject
    assert mail_content.recipients[0] == test_email.to_recipients[0].email_address
    assert len(test_email.attachments) == 0

    # instance = mock_smtp_server.return_value
    # assert instance.send_message.called_once_with(test_email)


def test_send_email_no_save(mocker, mock_message):
    send_mock = mocker.patch("exchangelib.Message.send")

    ReportEmailer.send_email(mock_message)
    send_mock.assert_called_once()


def test_send_email_with_save(mocker, mock_message):
    send_and_save_mock = mocker.patch("exchangelib.Message.send_and_save")
    ReportEmailer.send_email(mock_message, save=True)
    send_and_save_mock.assert_called_once()
