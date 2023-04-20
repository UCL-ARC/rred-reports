import pandas as pd

from rred_reports.masterfile import masterfile_columns
from rred_reports.redcap.main import RedcapReader


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
    redcap = recap_reader.preprocess_wide_data(extract_raw, extract_labelled, "2021-2022")

    # coerced variables filled
    same_coerced_values = redcap.loc[redcap["record_id"] == "AB9234"]
    assert (same_coerced_values.get("rrcp_area") == "Bristol").all()
    assert (same_coerced_values.get("school_id") == "RRS180").all()

    # missing date converted to 0001-01-01
    assert (redcap.loc[redcap["record_id"] == "AB100"].get("_test_timestamp") == pd.Timestamp.date(pd.NaT)).all()
    # missing values filtered out
    assert redcap.loc[redcap["record_id"].isin(["AB101", "AB102", "AB103"])].size == 0


def test_read_recap_extract(data_path):
    """
    Given an extract from redcap with 3 valid rows
    When the extract is processed
    3 rows should exist, and the output columns should match what is in our masterfile definition
    """
    raw_file_path = data_path / "redcap" / "extract.csv"
    labelled_file_path = data_path / "redcap" / "extract_labels.csv"
    school_list = data_path / "redcap" / "school_list.csv"

    recap_reader = RedcapReader(school_list)
    extract = recap_reader.read_recap_extract(raw_file_path, labelled_file_path, "2021-2022")
    assert extract.shape[0] == 3
    assert list(extract.columns.values) == masterfile_columns()
