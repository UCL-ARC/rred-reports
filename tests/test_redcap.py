import pandas as pd
import pytest

from rred_reports.masterfile import masterfile_columns
from rred_reports.redcap.main import ExtractInput, RedcapReader


@pytest.fixture()
def redcap_extract(data_path):
    school_list = data_path / "redcap" / "school_list.csv"
    recap_reader = RedcapReader(school_list)

    raw_file_path = data_path / "redcap" / "extract.csv"
    labelled_file_path = data_path / "redcap" / "extract_labels.csv"

    current_year = ExtractInput(raw_file_path, labelled_file_path, "2021-2022")
    previous_year = ExtractInput(raw_file_path, labelled_file_path, "2020-2021")

    return recap_reader.read_redcap_data(current_year, previous_year)


def test_preprocess_wide_data(data_path):
    """
    Given a minimal extract file with raw ids and a labelled extract file from redcap with an added _test_details and _test_timestamp column
    When the extract is processed with the corresponding R script for levels
    Then data coerced from multiple columns and data without students or RR id should be filtered out
    """
    raw_data_path = data_path / "redcap" / "extract.csv"
    labelled_data_path = data_path / "redcap" / "extract_labels.csv"
    school_list = data_path / "redcap" / "school_list.csv"

    extract_raw = pd.read_csv(raw_data_path)
    extract_labelled = pd.read_csv(labelled_data_path)
    recap_reader = RedcapReader(school_list)
    redcap = recap_reader.preprocess_wide_data(extract_raw, extract_labelled)

    # coerced variables filled
    same_coerced_values = redcap.loc[redcap["record_id"] == "AB9234"]
    assert (same_coerced_values.get("rrcp_area") == "Bristol").all()
    assert (same_coerced_values.get("school_id") == "RRS180").all()

    # missing date converted to 0001-01-01
    assert (redcap.loc[redcap["record_id"] == "AB100"].get("_test_timestamp") == pd.Timestamp.date(pd.NaT)).all()
    # missing values filtered out
    assert redcap.loc[redcap["record_id"].isin(["AB101", "AB102", "AB103"])].size == 0


def test_read_recap_extract_rows_and_cols(redcap_extract):
    """
    Given an extract from redcap with 3 valid rows
    When the extract is processed, using the same extract as the current year and previous year
    6 rows should exist, and the output columns should match what is in our masterfile definition
    """

    assert redcap_extract.shape[0] == 6
    assert list(redcap_extract.columns.values) == masterfile_columns()


def test_redcap_calculated_columns(redcap_extract):
    """
    Given a redcap extract where the first 2021-2022 student was born in summer and should be ongoing,
        and the second was born in winter and has a set exit outcome
    When the extract is processed
    Then the calculated `summer` and `exit_outcome` columns should be set correctly
    """
    summer_dob_and_ongoing = redcap_extract.loc[redcap_extract.pupil_no == "1_2021-2022"]
    assert (summer_dob_and_ongoing["summer"] == "Yes").all()
    assert (summer_dob_and_ongoing["exit_outcome"] == "Ongoing").all()
    not_summer_dob_and_not_ongoing = redcap_extract.loc[redcap_extract.pupil_no == "2_2021-2022"]
    assert (not_summer_dob_and_not_ongoing["summer"] == "No").all()
    assert (not_summer_dob_and_not_ongoing["exit_outcome"] == "Discontinued").all()
