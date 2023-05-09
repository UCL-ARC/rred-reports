import tomli_w

from rred_reports.redcap.interface import extract, top_level_dir


def test_cli_writes_file(temp_out_dir):
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
    repo_dir = top_level_dir
    dir_contents = list(repo_dir.glob("*"))
    print(dir_contents)
    with config_path.open("wb") as handle:
        tomli_w.dump(test_config, handle)
    extract(2021, config_file=config_path, output_dir=temp_out_dir)

    expected_file = temp_out_dir / "masterfile_2021-22.csv"
    assert expected_file.exists()
