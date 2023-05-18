import pytest

from rred_reports.dispatch_list import DispatchListException, get_mailing_info, get_unique_schools


def test_non_unique_school_raises_exception(data_path):
    """
    Given a dispatch list with two names for RRS180 and one name for RRS101
    When the dispatch list is processed for unique names
    Then an exception should be raised with only RRS180 appearing in the message
    """
    non_unique_dispatch_list = data_path / "dispatch_list_with_duplicate_school.xlsx"

    with pytest.raises(DispatchListException) as exception:
        get_unique_schools(non_unique_dispatch_list)

    message = exception.value.args[0]
    assert "RRS180" in message
    assert "RRS101" not in message


def test_get_mailing_info_success_single_recipient(data_path):
    dispatch_list = data_path / "dispatch_list.xlsx"
    test_id = "RRS100"
    mailing_info = get_mailing_info(test_id, dispatch_list)
    assert len(mailing_info.keys()) == 3
    assert len(mailing_info["mailing_list"]) == 1


def test_get_mailing_info_success_multiple_recipients(data_path):
    dispatch_list = data_path / "dispatch_list.xlsx"
    test_id = "RRS180"
    mailing_info = get_mailing_info(test_id, dispatch_list)
    assert len(mailing_info.keys()) == 3
    assert len(mailing_info["mailing_list"]) == 2


def test_get_mailing_info_success_null_recipient_replaced_with_tl(data_path):
    dispatch_list = data_path / "dispatch_list.xlsx"
    test_id = "RRS101"
    mailing_info = get_mailing_info(test_id, dispatch_list)
    assert len(mailing_info.keys()) == 3
    assert len(mailing_info["mailing_list"]) == 1
    assert mailing_info["mailing_list"] == ["leader_2@null.com"]


def test_get_mailing_info_failure_no_email_no_tl(data_path):
    dispatch_list = data_path / "dispatch_list_erroneous.xlsx"
    test_id = "RRS103"
    with pytest.raises(DispatchListException) as error:
        get_mailing_info(test_id, dispatch_list)
    expected_message = f"Missing contact ID for schools with RRED IDs: ['{test_id}']. Exiting."
    assert str(error.value) == expected_message


def test_get_mailing_info_failure_multiple_rred_ids(data_path):
    dispatch_list = data_path / "dispatch_list_erroneous.xlsx"
    test_id = "RRS104"
    with pytest.raises(DispatchListException) as error:
        get_mailing_info(test_id, dispatch_list)
    assert str(error.value) == "Multiple school labels in resulting DataFrame"
