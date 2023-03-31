import pytest
from exchangelib import Account


@pytest.fixture()
def mock_ews_account(mocker):
    ews_account_mock = mocker.MagicMock(name="ews_account_mock", spec=Account)
    # host = mocker.PropertyMock(return_value="local_smtp_server")
    # port = mocker.PropertyMock(return_value=99999)

    mocker.patch("rred_reports.reports.emails.Account", new=ews_account_mock)

    return ews_account_mock


@pytest.fixture()
def mock_message(mocker):
    message_mock = mocker.MagicMock(name="message_mock")

    mocker.patch("exchangelib.Message", new=message_mock)

    return message_mock


@pytest.fixture()
def mock_authenticator(mocker):
    auth_mock = mocker.MagicMock(name="auth_mock")

    mocker.patch("rred_reports.reports.auth.RREDAuthenticator", new=auth_mock)
    return auth_mock
