"""Downloading and processing of redcap data"""
from pathlib import Path

import pandas as pd


def read_recap_extract(file_path: Path) -> pd.DataFrame:
    extract = pd.read_csv(file_path)

    return preprocess_wide_data(extract)


def preprocess_wide_data(extract: pd.DataFrame) -> pd.DataFrame:
    processed_extract = extract.copy(deep=True)
    _convert_timestamps_to_dates(processed_extract)
    _fill_region_and_school_with_coersion(processed_extract)
    filtered = _filter_out_no_children_and_no_rr_id(processed_extract)
    return _rename_wide_cols_with_student_number_suffix(filtered)


def _convert_timestamps_to_dates(extract: pd.DataFrame):
    timestamp_cols = [col for col in extract if col.endswith("_timestamp")]
    dates = (
        extract[timestamp_cols].applymap(pd.to_datetime, format="%Y-%m-%d %H:%M:%S", errors="coerce")
        # mapping to date causes NaT to be converted to 2001-01-01
        .applymap(pd.Timestamp.date)
    )
    extract[timestamp_cols] = dates


def _fill_region_and_school_with_coersion(extract: pd.DataFrame):
    rrcp_area_cols = [col for col in extract if col.startswith("rrcp_area_")]
    extract["rrcp_region"] = extract[rrcp_area_cols].bfill(axis=1).iloc[:, 0]
    school_id_cols = [col for col in extract if col.startswith("entry_school_")]
    extract["rrcp_school"] = extract[school_id_cols].bfill(axis=1).iloc[:, 0]


def _filter_out_no_children_and_no_rr_id(extract: pd.DataFrame):
    filtered = extract[extract["no_rr_children"].notnull() & extract["no_rr_children"] != 0]
    return filtered[filtered["rrcp_rr_id"].notnull()]


def _rename_wide_cols_with_student_number_suffix(extract: pd.DataFrame) -> pd.DataFrame:
    pupil_column_rename = {}
    for col in extract:
        if not col.startswith("pupil_"):
            continue
        _, student_number, *col_name_parts = col.split("_")
        pupil_column_rename[col] = "_".join(col_name_parts) + f"v_{student_number}"
    return extract.rename(pupil_column_rename, axis=1)
