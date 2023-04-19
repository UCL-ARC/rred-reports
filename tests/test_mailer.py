import pytest
from exchangelib import Message

from rred_reports.reports.auth import RREDAuthenticator
from rred_reports.reports.emails import EmailContent, ReportEmailer, ReportEmailerException


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


def test_send_email_no_save(mocker, mock_message):
    send_mock = mocker.patch("exchangelib.Message.send")

    ReportEmailer.send_email(mock_message)
    send_mock.assert_called_once()


def test_send_email_with_save(mocker, mock_message):
    send_and_save_mock = mocker.patch("exchangelib.Message.send_and_save")
    ReportEmailer.send_email(mock_message, save=True)
    send_and_save_mock.assert_called_once()


def test_run_success(mock_ews_account, template_report_bytes, mocker):
    mocker.patch("exchangelib.Message.send")
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]
    cc_to = ["recipient-in-cc@domain.com"]
    report = template_report_bytes

    output = report_emailer.run(to_list, cc_to, report)
    assert output is True


def test_run_failure_no_email_saving(mock_ews_account, template_report_bytes, mocker):
    mocker.patch.object(Message, "send", side_effect=ReportEmailerException("test exception!"))
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]
    cc_to = ["recipient-in-cc@domain.com"]
    report = template_report_bytes

    with pytest.raises(ReportEmailerException):
        report_emailer.run(to_list, cc_to, report)


def test_run_failure_email_saving(mock_ews_account, template_report_bytes, mocker):
    mocker.patch.object(Message, "send_and_save", side_effect=ReportEmailerException("test exception!"))
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]
    cc_to = ["recipient-in-cc@domain.com"]
    report = template_report_bytes

    with pytest.raises(ReportEmailerException):
        report_emailer.run(to_list, cc_to, report, save_email=True)


def test_run_success_no_cc_list(mock_ews_account, template_report_bytes, mocker):
    mocker.patch("exchangelib.Message.send")
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]

    report = template_report_bytes

    output = report_emailer.run(to_list, report=report)
    assert output is True


def test_custom_report_emailer_exception():
    test_message = "my custom message"
    exception = ReportEmailerException(test_message)

    assert repr(exception) == test_message
