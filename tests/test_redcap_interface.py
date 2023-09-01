from pathlib import Path

import pandas as pd
import pytest
import tomli_w

from rred_reports.redcap import interface
from rred_reports.redcap.interface import extract


@pytest.fixture()
def set_top_level_dir() -> None:
    """
    Manually set the top level directory for running in CI, and revert it on teardown
    """
    original_value = interface.top_level_dir
    interface.top_level_dir = Path(__file__).parents[1]
    yield
    interface.top_level_dir = original_value


def test_cli_writes_file(temp_out_dir: Path, set_top_level_dir: None):
    """
    Given a config file pointing to valid test data
    When the extract CLI command is run, with an output to a temporary directory
    Then a masterfile should be written to the output directory and no errors encountered
    """
    data_path = "tests/data"
    test_config = {
        "2021": {
            "dispatch_list": f"{data_path}/dispatch_list.xlsx",
            "current_year": {
                "coded_data_file": f"{data_path}/redcap/extract.csv",
                "label_data_file": f"{data_path}/redcap/extract_labels.csv",
            },
            "previous_year": {
                "coded_data_file": f"{data_path}/redcap/extract.csv",
                "label_data_file": f"{data_path}/redcap/extract_labels.csv",
            },
        }
    }
    config_path = temp_out_dir / "config.toml"
    with config_path.open("wb") as handle:
        tomli_w.dump(test_config, handle)
    extract(2021, config_file=config_path, output_dir=temp_out_dir)

    expected_file = temp_out_dir / "processed" / "masterfile_2021-22.xlsx"
    assert expected_file.exists()


def test_school_id_aliases(temp_out_dir: Path, set_top_level_dir: None):
    """
    Given a config file pointing to valid test data, and an alias file for school ids for RRS200 -> RRS100
    When the extract command is run, with an output to a temporary directory
    Then a masterfile should be written with the school ID replaced
    """
    # Arrange
    data_path = "tests/data"
    test_config = {
        "2021": {
            "dispatch_list": f"{data_path}/dispatch_list.xlsx",
            "current_year": {
                "coded_data_file": f"{data_path}/redcap/extract.csv",
                "label_data_file": f"{data_path}/redcap/extract_labels.csv",
            },
            "previous_year": {
                "coded_data_file": f"{data_path}/redcap/extract.csv",
                "label_data_file": f"{data_path}/redcap/extract_labels.csv",
            },
        }
    }

    config_path = temp_out_dir / "config.toml"
    with config_path.open("wb") as handle:
        tomli_w.dump(test_config, handle)

    alias_path = temp_out_dir / "alias.toml"
    with alias_path.open("wb") as handle:
        tomli_w.dump({"RRS200": "RRS100"}, handle)

    # Act
    extract(2021, config_file=config_path, output_dir=temp_out_dir, school_aliases=alias_path)

    # Assert
    expected_file = temp_out_dir / "processed" / "masterfile_2021-22.xlsx"
    output = pd.read_excel(expected_file)
    ## old RRS200 shouldn't have any rows
    assert output[output.school_id == "RRS200"].shape[0] == 0
    renamed_school = output[output.school_id == "RRS100"]
    ## new RRS100 should exist in output and those rows should have the correct school from the dispatch list
    assert "RRS100" in renamed_school["school_id"].values
    assert renamed_school.shape[0] > 0
    assert all(renamed_school["rrcp_school"] == "School 100")
