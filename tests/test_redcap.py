import pandas as pd

from rred_reports.redcap.main import preprocess_wide_data, read_recap_extract


def test_preprocess_wide_data(data_path):
    """
    Given a minimal extract file from redcap with an added _test_details and _test_timestamp column
    When the extract is processed
    Then data coerced from multiple columns and data without students or RR id should be filtered out
    """
    file_path = data_path / "redcap" / "extract.csv"
    extract = pd.read_csv(file_path)

    redcap = preprocess_wide_data(extract)

    # coerced variables filled
    same_coerced_values = redcap.loc[redcap["record_id"].isin(["AB9234", "AB9235", "AB9236"])]
    assert (same_coerced_values.get("rccp_area") == 80).all()
    assert (same_coerced_values.get("school_id") == "RRS180").all()

    # missing date converted to 0001-01-01
    assert (redcap.loc[redcap["record_id"] == "AB100"].get("_test_timestamp") == pd.Timestamp.date(pd.NaT)).all()
    # missing values filtered out
    assert redcap.loc[redcap["record_id"].isin(["AB101", "AB102", "AB103"])].size == 0


def test_read_recap_extract(data_path):
    file_path = data_path / "redcap" / "extract.csv"
    extract = read_recap_extract(file_path)
    assert extract.shape[0] == 3
