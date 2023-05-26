"""All functionality dealing with the RRED masterfile"""
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal

import pandas as pd
from loguru import logger
from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter
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
    # no type coercion for "assess" columns, as can be both numeric and text, will require error handling if we use these
    assessi_engtest2: Data[None]
    assessi_iretest1: Data[None]
    assessi_iretype1: Data[None]
    assessi_maltest1: Data[None]
    assessi_outcome: Data[None]
    assessi_scotest1: Data[None]
    assessi_scotest2: Data[None]
    assessi_scotest3: Data[None]
    assessii_engcheck1: Data[None]
    assessii_engtest4: Data[None]
    assessii_engtest5: Data[None]
    assessii_engtest6: Data[None]
    assessii_engtest7: Data[None]
    assessii_engtest8: Data[None]
    assessii_scotest4: Data[None]
    assessii_iretest2: Data[None]
    assessii_iretype2: Data[None]
    assessiii_engtest10: Data[None]
    assessiii_engtest11: Data[None]
    assessiii_engtest9: Data[None]
    assessiii_iretest4: Data[None]
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
    # no type coercion so .isna() can be used to drop rows that don't have any school data
    rrcp_country: Data[None]
    rrcp_area: Data[None]
    rrcp_school: Data[None]


def parse_masterfile(file: Path) -> dict[str, pd.DataFrame]:
    """Create a nested dataframe from an Excel masterfile

    Args:
        file (Path): Path object pointing to Excel masterfile

    Returns:
        dict[str, pd.DataFrame]: Dictionary of dataframes
    """
    full_data = pd.read_excel(file)
    # drop out teachers at this point, so that if a teacher has changed title between years, we take the most recent one
    filtered_data = full_data[~full_data["reg_rr_title"].isin(["Teacher Leader", "Teacher Leader in Training"])].copy()

    def clmnlist(i: int, data: pd.DataFrame = filtered_data) -> list:
        return list(data.iloc[:, i])

    all_schools_df = School.new(clmnlist(6), clmnlist(3), clmnlist(4), clmnlist(5))  # pylint: disable=E1121
    all_schools_df = all_schools_df.drop_duplicates()  # pylint: disable=E1101

    teach_df = Teacher.new(clmnlist(1), clmnlist(2), clmnlist(6))  # pylint: disable=E1121
    teach_df.drop_duplicates(subset=["rred_user_id", "school_id"], inplace=True)  # pylint: disable=E1101

    drop_cols = list(all_schools_df.columns.values)
    drop_cols.append(teach_df.columns.values[1])  # pylint: disable=E1101

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


def masterfile_columns() -> list[str]:
    """List of all masterfile columns, in the expected order"""
    pupil_no, user_id, *other_pupil_fields = Pupil.fields()
    _school_id, *other_school_fields = School.fields()
    user_id, *other_teacher_fields, school_id = Teacher.fields()

    assert _school_id == school_id, "Sanity check for school ID columns being the same failed, these were not the same"

    return [pupil_no, user_id, *other_teacher_fields, *other_school_fields, school_id, *other_pupil_fields]


def read_and_process_masterfile(data_path: Path) -> pd.DataFrame:
    """
    Reads masterfile from path, adds in str representation of dates and sort by school, year range and the pupil entry number

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

    date_cols = [x for x in processed_data.columns if x.endswith("_date")]
    date_string_representation = processed_data[date_cols].applymap(lambda x: x.strftime("%d/%m/%Y") if not pd.isnull(x) else "NA")
    date_str_cols = [f"{x}_str" for x in date_cols]

    processed_data[date_str_cols] = date_string_representation

    # sort data
    processed_data[["entry_number", "period"]] = processed_data["pupil_no"].str.split("_", expand=True)
    processed_data.sort_values(by=["school_id", "period", "entry_number"], inplace=True)
    processed_data.drop(["entry_number", "period"], axis=1, inplace=True)
    return processed_data


def write_to_excel(masterfile_data: pd.DataFrame, output_file: Path) -> None:
    """
    Write masterfile dataframe to excel, formatting dates in Excel so they can be edited in excel without type
    conversion

    Parameters:
        masterfile_data (pd.DataFrame): dataframe of masterfile
        output_file (Path): path to write the file to
    """
    date_format_string = "YYYY-MM-DD"
    excel_date_format = NamedStyle(name="date_format", number_format=date_format_string)
    column_names = [column for column in masterfile_data.columns if column.endswith("_date") or column.endswith("_testdate")]  # noqa: PIE810
    column_names.append("entry_dob")

    with pd.ExcelWriter(output_file, date_format=date_format_string, engine="openpyxl") as writer:
        masterfile_data.to_excel(writer, index=False)
        workbook = writer.book
        worksheet = workbook.active
        for pandas_column_name in column_names:
            # convert to the Excel column letters e.g. 'A', 'B', ... 'AA', 'AB' ...
            column_letter = get_column_letter(masterfile_data.columns.get_loc(pandas_column_name) + 1)
            column = worksheet[column_letter]
            # skip the title column formatting
            for cell in column[1:]:
                cell.style = excel_date_format
