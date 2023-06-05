import pytest
from exchangelib import Message

from rred_reports.dispatch_list import get_mailing_info
from rred_reports.reports.auth import RREDAuthenticator
from rred_reports.reports.emails import EmailContent, ReportEmailer, ReportEmailerException, school_mailer


def test_build_email_with_report(mock_ews_account, template_report_path):
    report_emailer = ReportEmailer()

    mail_content = EmailContent(
        account=mock_ews_account,
        recipients=["recipient@domain.com"],
        cc_recipients=None,
        subject="Test",
        body="Test",
        attachment_path=template_report_path,
        attachment_name="test_report.pdf",
    )

    test_email = report_emailer.build_email(mail_content)

    assert mail_content.subject == test_email.subject
    assert mail_content.recipients[0] == test_email.to_recipients[0].email_address
    assert mail_content.attachment_name == test_email.attachments[0].name


def test_build_email_without_report(mock_ews_account):
    report_emailer = ReportEmailer()

    mail_content = EmailContent(
        account=mock_ews_account,
        recipients=["recipient@domain.com"],
        cc_recipients=None,
        subject="Test",
        body="Test",
        attachment_path=None,
        attachment_name="test_report.pdf",
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


def test_run_success(mock_ews_account, template_report_path, mocker):
    mocker.patch("exchangelib.Message.send")
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]
    cc_to = ["recipient-in-cc@domain.com"]
    report = template_report_path
    school_name = "test_school"
    start_year = 3000
    end_year = 3020
    output = report_emailer.run(school_name, start_year, end_year, to_list, cc_to, report)
    assert output is True


def test_run_failure_no_email_saving(mock_ews_account, template_report_path, mocker):
    mocker.patch.object(Message, "send", side_effect=ReportEmailerException("test exception!"))
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]
    cc_to = ["recipient-in-cc@domain.com"]
    report = template_report_path
    school_name = "test_school"
    start_year = 3000
    end_year = 3020

    with pytest.raises(ReportEmailerException):
        report_emailer.run(school_name, start_year, end_year, to_list, cc_to, report)


def test_run_failure_email_saving(mock_ews_account, template_report_path, mocker):
    mocker.patch.object(Message, "send_and_save", side_effect=ReportEmailerException("test exception!"))
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]
    cc_to = ["recipient-in-cc@domain.com"]
    report = template_report_path

    school_name = "test_school"
    start_year = 3000
    end_year = 3020

    with pytest.raises(ReportEmailerException):
        report_emailer.run(school_name, start_year, end_year, to_list, cc_to, report, save_email=True)


def test_run_success_no_cc_list(mock_ews_account, template_report_bytes, mocker):
    mocker.patch("exchangelib.Message.send")
    mocker.patch.object(RREDAuthenticator, "get_account", return_value=mock_ews_account)

    report_emailer = ReportEmailer()

    to_list = ["recipient@domain.com"]

    report = template_report_bytes
    school_name = "test_school"
    start_year = 3000
    end_year = 3020
    output = report_emailer.run(school_name, start_year, end_year, to_list, report)

    assert output is True


def test_custom_report_emailer_exception():
    test_message = "my custom message"
    exception = ReportEmailerException(test_message)

    assert repr(exception) == test_message


def test_school_mailer_success(mocker, data_path, dispatch_list):
    runner = mocker.patch.object(ReportEmailer, "run")
    school_id = "AAAAA"
    year = 2021
    report_name = "test_report_name.pdf"

    reports_dir = data_path / "output" / "reports" / "2021" / "schools"
    email_info = get_mailing_info(school_id, dispatch_list)

    school_mailer(school_id, year, email_info, report_name, reports_dir)

    runner.assert_called_once()


def test_school_mailer_failure(data_path, dispatch_list):
    school_id = "AAAAA"
    year = 2021
    report_name = "test_report_name.pdf"

    reports_dir = data_path / "nothing"

    email_info = get_mailing_info(school_id, dispatch_list)

    with pytest.raises(ReportEmailerException) as error:
        school_mailer(school_id, year, email_info, report_name, reports_dir)

    assert "not found" in error.value.message
