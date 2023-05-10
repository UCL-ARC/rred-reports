import pytest

from rred_reports.dispatch_list import DispatchListException, get_unique_schools


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
