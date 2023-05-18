from pathlib import Path

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


def test_cli_writes_file(temp_out_dir, set_top_level_dir):
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

    expected_file = temp_out_dir / "masterfile_2021-22.xlsx"
    assert expected_file.exists()
