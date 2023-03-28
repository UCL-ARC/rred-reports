import smtpd

import pytest


class MockSMTPServer(smtpd.SMTPServer):
    def __init__(*args, **kwargs):
        smtpd.SMTPServer.__init__(*args, **kwargs)

    def process_message(*args, **kwargs):
        pass


@pytest.fixture()
def mock_smtp_server(mocker):
    smtp_server_mock = mocker.MagicMock(name="smtp_server_mock")
    host = mocker.PropertyMock(return_value="local_smtp_server")
    port = mocker.PropertyMock(return_value=99999)
    mocker.patch("rred_reports.reports.emails.SMTP", new=smtp_server_mock)
    smtp_server_mock.host = host
    smtp_server_mock.port = port
    return smtp_server_mock
