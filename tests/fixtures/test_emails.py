import pytest
from exchangelib import Account

from rred_reports import get_config


@pytest.fixture()
def mock_ews_account(mocker):
    ews_account_mock = mocker.MagicMock(name="ews_account_mock", spec=Account)
    mocker.patch("rred_reports.reports.emails.Account", new=ews_account_mock)

    return ews_account_mock


@pytest.fixture()
def mock_message(mocker):
    message_mock = mocker.MagicMock(name="message_mock")

    mocker.patch("exchangelib.Message", new=message_mock)

    return message_mock


@pytest.fixture()
def mock_mailing_info(mocker):
    info_mock = mocker.MagicMock(name="info_mock")

    mocker.patch("rred_reports.dispatch_list.get_mailing_info", new=info_mock)

    info_mock.return_value = {"rred_school_id": "AAAAA", "school_label": "Test School", "mailing_list": "teacher1@null.com"}

    return info_mock


@pytest.fixture()
def dispatch_list(data_path, repo_root):
    test_config_file = data_path / "report_config.toml"
    return repo_root / get_config(test_config_file)["school"]["dispatch_list"]
