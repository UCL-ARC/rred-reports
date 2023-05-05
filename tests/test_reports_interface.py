from pathlib import Path

import pytest
import tomli

from rred_reports.reports.interface import ReportType, get_config


def test_report_type_enum():
    report_type_contents = [item.name for item in ReportType]
    expected_contents = ["SCHOOL", "CENTRE", "NATIONAL", "ALL"]
    assert expected_contents == report_type_contents


def test_report_type_enum_not_found():
    incorrect_enum = "beep"
    with pytest.raises(ValueError, match=f"'{incorrect_enum}' is not a valid ReportType"):
        ReportType(incorrect_enum)


def test_validate_data_sources_passes():
    pass


def test_validate_data_sources_fails():
    pass


def test_cli_app_create():
    pass


def test_get_config_success(temp_config_file):
    config = get_config(temp_config_file)
    expected_str = """
    school = "/path/to/data/school"
    centre = "/path/to/data/centre"
    national = "/path/to/data/national"
    """
    expected_toml = tomli.loads(expected_str)

    assert config == expected_toml


def test_get_config_failure():
    incorrect_config_path = Path("/path/to/config/file")
    expected_error_message = f"No report generation config file found at {incorrect_config_path}. Exiting."

    with pytest.raises(FileNotFoundError, match=expected_error_message):
        get_config(incorrect_config_path)
