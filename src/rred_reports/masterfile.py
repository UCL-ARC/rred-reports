"""All functionality dealing with the RRED masterfile"""
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal

import pandas as pd
from loguru import logger
from pandas_dataclasses import AsFrame, Data

# hardcode column number so that extra rows can be added, but ignored for our processing
COL_NUMBER_AFTER_SLIMMING = 64


class PandasDataFrame(AsFrame):
    """Custom dataclass definition allowing us to add custom functionality"""

    @classmethod
    def fields(cls):
        """Helper method to get a list of all fields"""
        return [field.name for field in fields(cls)]


@dataclass
class Pupil(PandasDataFrame):
    """Pupil information"""

    pupil_no: Data[str]
    rred_user_id: Data[str]
    assessi_engtest2: Data[str]
    assessi_iretest1: Data[str]
    assessi_iretype1: Data[str]
    assessi_maltest1: Data[str]
    assessi_outcome: Data[str]
    assessi_scotest1: Data[str]
    assessi_scotest2: Data[str]
    assessi_scotest3: Data[str]
    assessii_engcheck1: Data[str]
    assessii_engtest4: Data[str]
    assessii_engtest5: Data[str]
    assessii_engtest6: Data[str]
    assessii_engtest7: Data[str]
    assessii_engtest8: Data[str]
    assessii_scotest4: Data[str]
    assessii_iretest2: Data[str]
    assessii_iretype2: Data[str]
    assessiii_engtest10: Data[str]
    assessiii_engtest11: Data[str]
    assessiii_engtest9: Data[str]
    assessiii_iretest4: Data[str]
    entry_dob: Data[Literal["datetime64[ns]"]]
    summer: Data[str]
    entry_date: Data[Literal["datetime64[ns]"]]
    entry_testdate: Data[Literal["datetime64[ns]"]]
    exit_date: Data[Literal["datetime64[ns]"]]
    exit_outcome: Data[str]
    entry_year: Data[str]
    entry_gender: Data[str]
    entry_ethnicity: Data[str]
    entry_language: Data[str]
    entry_poverty: Data[str]
    entry_sen_status: Data[str]
    entry_special_cohort: Data[str]
    entry_bl_result: Data[pd.Int32Dtype]
    entry_li_result: Data[pd.Int32Dtype]
    entry_cap_result: Data[pd.Int32Dtype]
    entry_wt_result: Data[pd.Int32Dtype]
    entry_wv_result: Data[pd.Int32Dtype]
    entry_hrsw_result: Data[pd.Int32Dtype]
    entry_bas_result: Data[pd.Int32Dtype]
    exit_num_weeks: Data[pd.Int32Dtype]
    exit_num_lessons: Data[pd.Int32Dtype]
    exit_lessons_missed_ca: Data[pd.Int32Dtype]
    exit_lessons_missed_cu: Data[pd.Int32Dtype]
    exit_lessons_missed_ta: Data[pd.Int32Dtype]
    exit_lessons_missed_tu: Data[pd.Int32Dtype]
    exit_bl_result: Data[pd.Int32Dtype]
    exit_li_result: Data[pd.Int32Dtype]
    exit_cap_result: Data[pd.Int32Dtype]
    exit_wt_result: Data[pd.Int32Dtype]
    exit_wv_result: Data[pd.Int32Dtype]
    exit_hrsw_result: Data[pd.Int32Dtype]
    exit_bas_result: Data[pd.Int32Dtype]
    month3_testdate: Data[Literal["datetime64[ns]"]]
    month3_bl_result: Data[pd.Int32Dtype]
    month3_wv_result: Data[pd.Int32Dtype]
    month3_bas_result: Data[pd.Int32Dtype]
    month6_testdate: Data[Literal["datetime64[ns]"]]
    month6_bl_result: Data[pd.Int32Dtype]
    month6_wv_result: Data[pd.Int32Dtype]
    month6_bas_result: Data[pd.Int32Dtype]


@dataclass
class Teacher(PandasDataFrame):
    """Teacher information, can link with Pupil df with rreduserID"""

    rred_user_id: Data[str]
    reg_rr_title: Data[str]
    school_id: Data[str]


@dataclass
class School(PandasDataFrame):
    """School information can link with Teacher df with school_id"""

    school_id: Data[str]
    rrcp_country: Data[str]
    rrcp_area: Data[str]
    rrcp_school: Data[str]


def parse_masterfile(file: Path) -> dict[str, pd.DataFrame]:
    """Create a nested dataframe from an Excel masterfile

    Args:
        file (Path): Path object pointing to Excel masterfile

    Returns:
        dict[str, pd.DataFrame]: Dictionary of dataframes
    """
    full_data = pd.read_excel(file)

    def clmnlist(i, data=full_data):
        return list(data.iloc[:, i])

    all_schools_df = School.new(clmnlist(6), clmnlist(3), clmnlist(4), clmnlist(5))  # pylint: disable=E1121
    all_schools_df = all_schools_df.drop_duplicates()  # pylint: disable=E1101

    teach_df = Teacher.new(clmnlist(1), clmnlist(2), clmnlist(6))  # pylint: disable=E1121
    teach_df = teach_df.drop_duplicates()  # pylint: disable=E1101

    drop_cols = list(all_schools_df.columns.values)
    drop_cols.append(teach_df.columns.values[1])

    df_slimmed = full_data.drop(columns=drop_cols)

    remaining_columns = [clmnlist(x, df_slimmed) for x in range(COL_NUMBER_AFTER_SLIMMING)]

    pupils_df = Pupil.new(*remaining_columns)
    pupils_df.drop_duplicates(inplace=True)  # pylint: disable=E1101

    return {"pupils": pupils_df, "teachers": teach_df, "schools": all_schools_df}


def join_masterfile_dfs(masterfile_dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Helper function to join entire masterfile dataframes together

    Args:
        masterfile_dfs: dict[str, pd.DataFrame]: Dictionary of Dataframes
    Returns:
        pd.DataFrame: joined masterfile
    """
    teacher_schools = pd.merge(masterfile_dfs["teachers"], masterfile_dfs["schools"], on="school_id")
    return pd.merge(teacher_schools, masterfile_dfs["pupils"], on="rred_user_id")


def masterfile_columns():
    """List of all masterfile columns, in the expected order"""
    pupil_no, user_id, *other_pupil_fields = Pupil.fields()
    _school_id, *other_school_fields = School.fields()
    user_id, *other_teacher_fields, school_id = Teacher.fields()

    assert _school_id == school_id, "Sanity check for school ID columns being the same failed, these were not the same"

    return [pupil_no, user_id, *other_teacher_fields, *other_school_fields, school_id, *other_pupil_fields]


def read_and_sort_masterfile(data_path: Path):
    """
    Reads masterfile from path and sort by school, year range and the pupil entry number

    Args:
        data_path (Path): path to masterfile
    Returns:
        pd.DataFrame: masterfile
    Raises:
        FileNotFoundError if the masterfile doesn't exist
    """
    try:
        masterfile_data = parse_masterfile(data_path)
    except FileNotFoundError as processed_data_missing_error:
        logger.error(f"No processed data file found at {data_path}. Exiting.")
        raise processed_data_missing_error
    processed_data = join_masterfile_dfs(masterfile_data)
    # sort data
    processed_data[["entry_number", "period"]] = processed_data["pupil_no"].str.split("_", expand=True)
    processed_data.sort_values(by=["school_id", "period", "entry_number"], inplace=True)
    processed_data.drop(["entry_number", "period"], axis=1, inplace=True)
    return processed_data
