"""Downloading and processing of redcap data"""
from pathlib import Path

import pandas as pd


def read_recap_extract(file_path: Path) -> pd.DataFrame:
    extract = pd.read_csv(file_path)
    processed_wide = preprocess_wide_data(extract)
    # after long to wide, should populate factor numbers -> strings
    return wide_to_long(processed_wide)


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
    extract["rccp_area"] = extract[rrcp_area_cols].bfill(axis=1).iloc[:, 0]
    school_id_cols = [col for col in extract if col.startswith("entry_school_")]
    extract["school_id"] = extract[school_id_cols].bfill(axis=1).iloc[:, 0]


def _filter_out_no_children_and_no_rr_id(extract: pd.DataFrame):
    filtered = extract[extract["no_rr_children"].notnull() & extract["no_rr_children"] != 0]
    return filtered[filtered["rrcp_rr_id"].notnull()]


def _rename_wide_cols_with_student_number_suffix(extract: pd.DataFrame) -> pd.DataFrame:
    pupil_column_rename = {}
    for col in extract:
        if not col.startswith("pupil_"):
            continue
        _, student_number, *col_name_parts = col.split("_")
        pupil_column_rename[col] = "_".join(col_name_parts) + f"_v{student_number}"
    return extract.rename(pupil_column_rename, axis=1)


def wide_to_long(wide_extract: pd.DataFrame) -> pd.DataFrame:
    non_wide_columns = ["reg_rr_title", "rrcp_country", "rccp_area", "school_id"]

    wide_cols_before_summer = [
        "assessi_engtest2",
        "assessi_iretest1",
        "assessi_iretype1",
        "assessi_maltest1",
        "assessi_outcome",
        "assessi_scotest1",
        "assessi_scotest2",
        "assessi_scotest3",
        "assessii_engcheck1",
        "assessii_engtest4",
        "assessii_engtest5",
        "assessii_engtest6",
        "assessii_engtest7",
        "assessii_engtest8",
        "assessii_scotest4",
        "assessii_iretest2",
        "assessii_iretype2",
        "assessiii_engtest10",
        "assessiii_engtest11",
        "assessiii_engtest9",
        "assessiii_iretest4",
        "entry_dob",
    ]

    wide_cols_between_summer_and_entry_year = [
        "entry_date",
        "entry_testdate",
        "exit_date",
        "exit_outcome",
    ]
    wide_cols_after_entry_year = [
        "entry_gender",
        "entry_ethnicity",
        "entry_language",
        "entry_poverty",
        "entry_sen_status",
        "entry_special_cohort",
        "entry_bl_result",
        "entry_li_result",
        "entry_cap_result",
        "entry_wt_result",
        "entry_wv_result",
        "entry_hrsw_result",
        "entry_bas_result",
        "exit_num_weeks",
        "exit_num_lessons",
        "exit_lessons_missed_ca",
        "exit_lessons_missed_cu",
        "exit_lessons_missed_ta",
        "exit_lessons_missed_tu",
        "exit_bl_result",
        "exit_li_result",
        "exit_cap_result",
        "exit_wt_result",
        "exit_wv_result",
        "exit_hrsw_result",
        "exit_bas_result",
        "month3_testdate",
        "month3_bl_result",
        "month3_wv_result",
        "month3_bas_result",
        "month6_testdate",
        "month6_bl_result",
        "month6_wv_result",
        "month6_bas_result",
    ]

    entry_year_cols = [f"entry_year_{country}" for country in ["eng", "ire", "mal", "sco"]]

    # merge entry year for each country to entry_year_vx
    initial_long = _long_and_merge(wide_extract, wide_cols_before_summer[0])

    export_data = initial_long[[*non_wide_columns, wide_cols_before_summer[0]]]

    remaining_wide_columns = [*wide_cols_before_summer[0:], *wide_cols_between_summer_and_entry_year, *wide_cols_after_entry_year, *entry_year_cols]

    for wide_column in remaining_wide_columns:
        export_data = _long_and_merge(wide_extract, wide_column, export_data)

    entry_year = export_data[entry_year_cols].bfill(axis=1).iloc[:, 0]
    summer_index = len(non_wide_columns) + len(wide_cols_before_summer) + 1
    export_data.insert(summer_index, "Summer", pd.Series(""))
    entry_year_index = summer_index + len(wide_cols_between_summer_and_entry_year) + 1
    export_data.insert(entry_year_index, "entry_year", entry_year)
    export_data.reset_index(inplace=True)
    pupil_no = export_data["student_id"].astype(str) + "_" + export_data["rrcp_rr_id"]
    export_data.insert(0, "pupil_no", pupil_no)
    export_data.rename({"rrcp_rr_id": "rred_user_id"}, inplace=True)

    filtered_export_data = export_data.drop(entry_year_cols, axis=1)

    return filtered_export_data[filtered_export_data["entry_dob"].notnull()]


def _long_and_merge(wide_df: pd.DataFrame, column_prefix: str, long_df: pd.DataFrame = None):
    transformed = pd.wide_to_long(wide_df, stubnames=column_prefix, i=["rrcp_rr_id"], j="student_id", sep="_v")
    if long_df is not None:
        return pd.concat([long_df, transformed[column_prefix]], axis=1)
    return transformed
