from pathlib import Path

import pandas as pd
import pytest
import tomli

from rred_reports.reports.interface import ReportType, get_config, validate_data_sources


def test_report_type_enum():
    report_type_contents = [item.name for item in ReportType]
    expected_contents = ["SCHOOL", "CENTRE", "NATIONAL", "ALL"]
    assert expected_contents == report_type_contents


def test_report_type_enum_not_found():
    incorrect_enum = "beep"
    with pytest.raises(ValueError, match=f"'{incorrect_enum}' is not a valid ReportType"):
        ReportType(incorrect_enum)


def test_validate_data_sources_passes(temp_data_directories):
    top_level_dir = temp_data_directories["top_level"]
    data_directory = temp_data_directories["year"]

    example_processed_data = {"item 1": 1, "item 2": 2}
    processed_data_path = data_directory / "processed_data.csv"
    template_file_standin_path = top_level_dir / "template_file_standin.csv"
    processed_df = pd.DataFrame.from_dict([example_processed_data])
    processed_df.to_csv(processed_data_path)
    processed_df.to_csv(template_file_standin_path)
    validated_data = validate_data_sources(2099, template_file_standin_path, top_level_dir=top_level_dir)
    assert isinstance(validated_data, dict)
    assert len(validated_data) == 3


def test_validate_data_sources_fails_processed_data_missing(temp_data_directories):
    top_level_dir = temp_data_directories["top_level"]

    example_processed_data = {"item 1": 1, "item 2": 2}
    template_file_standin_path = top_level_dir / "template_file_standin.csv"
    processed_df = pd.DataFrame.from_dict([example_processed_data])
    processed_df.to_csv(template_file_standin_path)

    with pytest.raises(FileNotFoundError):
        validate_data_sources(2099, template_file_standin_path, top_level_dir=top_level_dir)


def test_validate_data_sources_fails_template_file_missing(temp_data_directories):
    top_level_dir = temp_data_directories["top_level"]
    data_directory = temp_data_directories["year"]

    example_processed_data = {"item 1": 1, "item 2": 2}
    processed_data_path = data_directory / "processed_data.csv"
    template_file_standin_path = top_level_dir / "template_file_standin.csv"
    processed_df = pd.DataFrame.from_dict([example_processed_data])
    processed_df.to_csv(processed_data_path)
    with pytest.raises(FileNotFoundError):
        validate_data_sources(2099, template_file_standin_path, top_level_dir=top_level_dir)


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