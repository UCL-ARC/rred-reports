from rred_reports.reports.emails import EmailContent, build_email, send_email


def test_send_email(mock_smtp_server):
    test_server = mock_smtp_server.host.return_value
    test_port = mock_smtp_server.port.return_value

    mail_content = EmailContent(
        sender="sender@domain",
        recipients="recipient@domain",
        subject="Test",
        body="Test",
        attachment=None,
        attachment_filename=None,
        smtp_host=test_server,
        smtp_port=test_port,
    )

    test_email = build_email(mail_content)
    assert f"From: {mail_content.sender}" in test_email.as_string()
    assert f"To: {mail_content.recipients}" in test_email.as_string()

    send_email(test_server, test_port, test_email)
    instance = mock_smtp_server.return_value

    assert instance.send_message.called_once_with(test_email)
