"""Downloading and processing of redcap data"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from tqdm import tqdm

from rred_reports.dispatch_list import get_unique_schools
from rred_reports.masterfile import masterfile_columns


@dataclass
class ExtractInput:
    """Inputs required for a single year of a redcap extract"""

    coded_data_path: Path
    labelled_data_path: Path
    survey_period: str


class RedcapReader:
    """Reads two years of redcap data, processing the files (wide to long, and others) and filtering to non-empty rows"""

    def __init__(self, school_list: Path):
        """
        Setup for reading from redcap

        Args:
            school_list: path to Excel dispatch list file
        """
        self._school_list = get_unique_schools(school_list)

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
        logger.info("Processing survey period: {period}", period=redcap_fields.survey_period)
        raw_data = pd.read_csv(redcap_fields.coded_data_path, low_memory=False)
        labelled_data = pd.read_csv(redcap_fields.labelled_data_path, low_memory=False)
        processed_wide = self.preprocess_wide_data(raw_data, labelled_data)
        long = self.wide_to_long(processed_wide, redcap_fields.survey_period)
        long_with_names = self._add_school_name_column(long)
        return long_with_names[masterfile_columns()].copy()

    @classmethod
    def preprocess_wide_data(cls, raw_data: pd.DataFrame, labelled_data: pd.DataFrame) -> pd.DataFrame:
        """
        Process wide data before conversion to long.

        - Use labelled data for all columns except for `school_id`, which remains as the code for later processing using the dispatch list
        - Some data is spread across multiple columns, so coalesce this data
        - Type conversion for dates
        - Convert wide columns to consistent format ({column}_v{student_number}
        - Add in row number column for unique indexes
        - Filter responses with no students
        - Filter out test rows - `record_id` starting with 'Sandbox' or 'TEST'

        Args:
            raw_data (pd.DataFrame): survey responses, with data given as codes
            labelled_data (pd.DataFrame): survey responses, with data given as labels

        Returns:
            pd.DataFrame: survey data processed to allow for wide to long conversion, labels used for all data except school id
        """
        logger.info("Pre-processing wide data")
        processed_extract = labelled_data.copy(deep=True)
        # Unify on using the raw_data column names, labelled uses the questions given on the survey as column names
        processed_extract.columns = raw_data.columns
        cls._fill_school_column_with_coalesce(raw_data, processed_extract, "school_id")
        cls._fill_school_column_with_coalesce(processed_extract, processed_extract, "redcap_school_name")
        cls._fill_region_with_coalesce(processed_extract)
        cls._convert_timestamps_to_dates(processed_extract)
        # Making a copy, so we have a de-fragmented frame for adding row number, was getting a performance warning
        converted_data = processed_extract.copy()
        converted_data["_row_number"] = np.arange(converted_data.shape[0])

        filtered = cls._filter_non_entry_and_test_rows(converted_data)
        return cls._rename_wide_cols_with_student_number_suffix(filtered)

    @staticmethod
    def _fill_school_column_with_coalesce(school_data: pd.DataFrame, processed_extract: pd.DataFrame, column_name: str):
        school_id_cols = [col for col in school_data if col.startswith("entry_school_")]
        processed_extract[column_name] = school_data[school_id_cols].bfill(axis=1).iloc[:, 0]

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
    def _filter_non_entry_and_test_rows(extract: pd.DataFrame) -> pd.DataFrame:
        no_children = extract[extract["no_rr_children"].notnull() & extract["no_rr_children"] != 0]
        has_id = no_children[no_children["rrcp_rr_id"].notnull()]
        return has_id[~has_id["record_id"].str.startswith("Sandbox") & ~has_id["record_id"].str.startswith("TEST")]

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
        "non_wide_columns": ["reg_rr_title", "rrcp_country", "rrcp_area", "redcap_school_name", "school_id"],
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
        """
        Convert preprocessed wide extract to long, only keeping rows which have an entry date or exit date

        Args:
            wide_extract [pd.DataFrame]: processed wide extract
            survey_period [str]: survey period to add to the `pupil_no`
        Returns:
            pd.DataFrame: long data
        """
        logger.info("Converting data from wide to long, this can take a couple of minutes")
        entry_year_cols = [f"entry_year_{country}" for country in ["eng", "ire", "mal", "sco"]]

        export_data = self._create_long_data(entry_year_cols, wide_extract)
        self._convert_dates_to_datetime(export_data)
        processed_data = self._process_calculated_columns(entry_year_cols, export_data, survey_period)
        processed_data.rename(columns={"rrcp_rr_id": "rred_user_id"}, inplace=True)

        return processed_data[processed_data["entry_date"].notnull() | processed_data["exit_date"].notnull()]

    def _create_long_data(self, entry_year_cols: list[str], wide_extract: pd.DataFrame) -> pd.DataFrame:
        initial_long = self._long_and_merge(wide_extract, self._parsing_cols["wide_columns"][0])
        export_data = initial_long[[*self._parsing_cols["non_wide_columns"], self._parsing_cols["wide_columns"][0]]]
        remaining_wide_columns = [
            *self._parsing_cols["wide_columns"][1:],
            *entry_year_cols,
        ]
        for wide_column in tqdm(remaining_wide_columns):
            export_data = self._long_and_merge(wide_extract, wide_column, export_data)
        return export_data

    @staticmethod
    def _long_and_merge(wide_df: pd.DataFrame, column_prefix: str, long_df: pd.DataFrame = None):
        index_columns = ["rrcp_rr_id", "_row_number"]
        transformed = pd.wide_to_long(wide_df, stubnames=column_prefix, i=index_columns, j="student_id", sep="_v")
        if long_df is not None:
            return pd.concat([long_df, transformed[column_prefix]], axis=1)
        return transformed

    @staticmethod
    def _convert_dates_to_datetime(extract: pd.DataFrame):
        date_cols = [col for col in extract if col.endswith("_date")]
        dates = extract[date_cols].applymap(pd.to_datetime, format="%Y-%m-%d", errors="coerce")
        extract[date_cols] = dates

    def _process_calculated_columns(self, entry_year_cols: list[str], export_data: pd.DataFrame, survey_period: str) -> pd.DataFrame:
        """
        Calculate columns, explained in section 1.2 of Data managers handbook
        """
        processed_data = export_data.copy()

        entry_year = processed_data[entry_year_cols].bfill(axis=1).iloc[:, 0]
        processed_data["entry_year"] = entry_year

        processed_data["summer"] = "No"
        processed_data[["dob_year", "dob_month", "dob_day"]] = processed_data["entry_dob"].str.split("-", expand=True).apply(pd.to_numeric)
        summer_dob = (processed_data["dob_month"] >= 4) & (processed_data["dob_month"] <= 8) & (processed_data["dob_day"] <= 31)
        processed_data.loc[summer_dob, "summer"] = "Yes"

        # add ongoing exit outcome
        ongoing = processed_data["exit_outcome"].isna() & ~processed_data["entry_date"].isna() & processed_data["exit_date"].isna()
        processed_data.loc[ongoing, "exit_outcome"] = "Ongoing"

        # get the original index columns back and use them to create pupil number
        processed_data.reset_index(inplace=True)
        pupil_no = processed_data["student_id"].astype(str) + f"_{survey_period}"
        processed_data.insert(0, "pupil_no", pupil_no)

        return processed_data

    def _add_school_name_column(self, long_df: pd.DataFrame) -> pd.DataFrame:
        named_schools = long_df.merge(self._school_list, left_on="school_id", right_on="RRED School ID", how="left")
        named_schools.rename({"School Name": "rrcp_school"}, axis=1, inplace=True)
        return named_schools
