"""Downloading and processing of redcap data"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from rred_reports.masterfile import masterfile_columns


@dataclass
class ExtractInput:
    """Inputs required for a single year of a redcap extract"""

    coded_data_path: Path
    labelled_data_path: Path
    survey_period: str


class RedcapReader:
    def __init__(self, school_list: Path):
        """
        Setup for reading from redcap

        Args:
            school_list: path to csv file defining a mapping of all school ids to their names
        """
        self._school_list = pd.read_csv(school_list)

    def read_redcap_data(self, current_year: ExtractInput, previous_year: ExtractInput) -> pd.DataFrame:
        """
        Process two years of redcap data from wide to long, and join them together

        Args:
            current_year (ExtractInput): current surveyed year
            previous_year (ExtractInput): previous surveyed year

        Returns:
            pd.DataFrame: Long data from surveys, combined by rows
        """
        current_extract = self.read_single_redcap_year(current_year)
        previous_extract = self.read_single_redcap_year(previous_year)
        return pd.concat([current_extract, previous_extract], ignore_index=True)

    def read_single_redcap_year(self, redcap_fields: ExtractInput) -> pd.DataFrame:
        """
        Process a single year of redcap data from wide to long, keeping only the columns from the masterfile

        Args:
            redcap_fields (ExtractInput): redcap data for a year of survey
        """
        raw_data = pd.read_csv(redcap_fields.coded_data_path)
        labelled_data = pd.read_csv(redcap_fields.labelled_data_path)
        processed_wide = self.preprocess_wide_data(raw_data, labelled_data)
        long = self.wide_to_long(processed_wide, redcap_fields.survey_period)
        long_with_names = self._add_school_name_column(long)
        return long_with_names[masterfile_columns()].copy()

    @classmethod
    def preprocess_wide_data(cls, raw_data: pd.DataFrame, labelled_file_path: pd.DataFrame) -> pd.DataFrame:
        """
        Process wide data before conversion to long.

        - Some data is spread across multiple columns, so coalesce this data
        - Type conversion for dates
        - Convert wide columns to consistent format ({column}_v{student_number}
        - Add in row number column for unique indexes
        - Filter responses with no students

        Args:
            raw_data (pd.DataFrame): survey responses, with data given as codes
            labelled_file_path (pd.DataFrame): survey responses, with data given as labels

        Returns:
            pd.DataFrame: survey data processed to allow for wide to long conversion, labels used for all data except school id
        """
        processed_extract = labelled_file_path.copy(deep=True)
        cls._fill_school_id_with_coalesce(raw_data, processed_extract)
        cls._fill_region_with_coalesce(processed_extract)
        cls._convert_timestamps_to_dates(processed_extract)
        processed_extract["_row_number"] = np.arange(processed_extract.shape[0])

        filtered = cls._filter_out_no_children_and_no_rr_id(processed_extract)
        return cls._rename_wide_cols_with_student_number_suffix(filtered)

    @staticmethod
    def _fill_school_id_with_coalesce(raw_data, processed_extract):
        school_id_cols = [col for col in raw_data if col.startswith("entry_school_")]
        processed_extract["school_id"] = raw_data[school_id_cols].bfill(axis=1).iloc[:, 0]

    @staticmethod
    def _fill_region_with_coalesce(extract: pd.DataFrame):
        rrcp_area_cols = [col for col in extract if col.startswith("rrcp_area_")]
        extract["rrcp_area"] = extract[rrcp_area_cols].bfill(axis=1).iloc[:, 0]

    @staticmethod
    def _convert_timestamps_to_dates(extract: pd.DataFrame):
        timestamp_cols = [col for col in extract if col.endswith("_timestamp")]
        dates = (
            extract[timestamp_cols].applymap(pd.to_datetime, format="%Y-%m-%d %H:%M:%S", errors="coerce")
            # mapping to date causes NaT to be converted to 2001-01-01
            .applymap(pd.Timestamp.date)
        )
        extract[timestamp_cols] = dates

    @staticmethod
    def _filter_out_no_children_and_no_rr_id(extract: pd.DataFrame) -> pd.DataFrame:
        filtered = extract[extract["no_rr_children"].notnull() & extract["no_rr_children"] != 0]
        return filtered[filtered["rrcp_rr_id"].notnull()]

    @staticmethod
    def _rename_wide_cols_with_student_number_suffix(extract: pd.DataFrame) -> pd.DataFrame:
        pupil_column_rename = {}
        for col in extract:
            if not col.startswith("pupil_"):
                continue
            _, student_number, *col_name_parts = col.split("_")
            pupil_column_rename[col] = "_".join(col_name_parts) + f"_v{student_number}"
        return extract.rename(pupil_column_rename, axis=1)

    # Hardcoded columns for exporting, could finesse this but probably isn't worth the time
    # The final columns output are under unit testing so will catch any changes to input or output data
    _parsing_cols = {
        "non_wide_columns": ["reg_rr_title", "rrcp_country", "rrcp_area", "school_id"],
        "wide_columns": [
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
            "entry_date",
            "entry_testdate",
            "exit_date",
            "exit_outcome",
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
        ],
    }

    def wide_to_long(self, wide_extract: pd.DataFrame, survey_period: str) -> pd.DataFrame:
        entry_year_cols = [f"entry_year_{country}" for country in ["eng", "ire", "mal", "sco"]]

        export_data = self._create_long_data(entry_year_cols, wide_extract)
        processed_data = self._process_calculated_columns(entry_year_cols, export_data, survey_period)
        processed_data.rename(columns={"rrcp_rr_id": "rred_user_id"}, inplace=True)

        return processed_data[processed_data["entry_date"].notnull()]

    def _create_long_data(self, entry_year_cols: list[str], wide_extract: pd.DataFrame) -> pd.DataFrame:
        initial_long = self._long_and_merge(wide_extract, self._parsing_cols["wide_columns"][0])
        export_data = initial_long[[*self._parsing_cols["non_wide_columns"], self._parsing_cols["wide_columns"][0]]]
        remaining_wide_columns = [
            *self._parsing_cols["wide_columns"][1:],
            *entry_year_cols,
        ]
        for wide_column in remaining_wide_columns:
            export_data = self._long_and_merge(wide_extract, wide_column, export_data)
        return export_data

    @staticmethod
    def _long_and_merge(wide_df: pd.DataFrame, column_prefix: str, long_df: pd.DataFrame = None):
        index_columns = ["rrcp_rr_id", "_row_number"]
        transformed = pd.wide_to_long(wide_df, stubnames=column_prefix, i=index_columns, j="student_id", sep="_v")
        if long_df is not None:
            return pd.concat([long_df, transformed[column_prefix]], axis=1)
        return transformed

    def _process_calculated_columns(self, entry_year_cols: list[str], export_data: pd.DataFrame, survey_period: str) -> pd.DataFrame:
        processed_data = export_data.copy()
        entry_year = processed_data[entry_year_cols].bfill(axis=1).iloc[:, 0]
        processed_data["summer"] = pd.Series("")
        processed_data["entry_year"] = entry_year
        processed_data.reset_index(inplace=True)
        pupil_no = processed_data["student_id"].astype(str) + f"_{survey_period}"
        processed_data.insert(0, "pupil_no", pupil_no)
        return processed_data

    def _add_school_name_column(self, long_df: pd.DataFrame) -> pd.DataFrame:
        named_schools = long_df.merge(self._school_list, left_on="school_id", right_on="RRED School ID", how="left")
        named_schools.rename({"School Name": "rrcp_school"}, axis=1, inplace=True)
        return named_schools
