import pytest

from rred_reports.reports.interface import ReportType


def test_report_type_enum():
    report_type_contents = [item.name for item in ReportType]
    expected_contents = ["SCHOOL", "CENTRE", "NATIONAL", "ALL"]
    assert expected_contents == report_type_contents


def test_report_type_enum_not_found():
    incorrect_enum = "beep"
    with pytest.raises(ValueError, match=f"'{incorrect_enum}' is not a valid ReportType"):
        ReportType(incorrect_enum)
