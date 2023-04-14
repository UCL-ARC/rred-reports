"""All functionality dealing with the RRED masterfile"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
from pandas_dataclasses import AsFrame, Data

# hardcode column number so that extra rows can be added, but ignored for our processing
COL_NUMBER_AFTER_SLIMMING = 65


@dataclass
class Pupil(AsFrame):
    """Pupil information"""

    pupil_no: Data[str]
    rred_user_id: Data[str]
    assessi_engtest2: Data[pd.Int32Dtype]  # surprising that there isn't an engtest1 here, is this an accident?
    assessi_iretest1: Data[pd.Int32Dtype]
    assessi_iretype1: Data[pd.Int32Dtype]
    assessi_maltest1: Data[pd.Int32Dtype]
    assessi_outcome: Data[pd.Int32Dtype]
    assessi_scotest1: Data[pd.Int32Dtype]
    assessi_scotest2: Data[pd.Int32Dtype]
    assessi_scotest3: Data[pd.Int32Dtype]
    assessii_engcheck1: Data[pd.Int32Dtype]
    assessii_engtest4: Data[pd.Int32Dtype]
    assessii_engtest5: Data[pd.Int32Dtype]
    assessii_engtest6: Data[pd.Int32Dtype]
    assessii_engtest7: Data[pd.Int32Dtype]
    assessii_engtest8: Data[pd.Int32Dtype]
    assessii_scotest4: Data[pd.Int32Dtype]
    assessii_iretest2: Data[pd.Int32Dtype]
    assessii_iretype2: Data[pd.Int32Dtype]
    assessiii_engtest10: Data[pd.Int32Dtype]
    assessiii_engtest11: Data[pd.Int32Dtype]
    assessiii_engtest9: Data[pd.Int32Dtype]
    assessiii_iretest4: Data[pd.Int32Dtype]
    entry_dob: Data[Literal["datetime64[ns]"]]
    summer: Data[str]  # if this is used, will need to populate from redcap data, I suspect we may be able to remove it
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
    rred_qc_parameters: Data[str]


@dataclass
class Teacher(AsFrame):
    """Teacher information, can link with Pupil df with rreduserID"""

    rred_user_id: Data[str]
    reg_rr_title: Data[str]
    school_id: Data[str]


@dataclass
class School(AsFrame):
    """School information can link with Teacher df with school_id"""

    school_id: Data[str]
    rrcp_school: Data[str]
    rrcp_area: Data[int]
    rrcp_country: Data[int]


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

    all_schools_df = School.new(clmnlist(6), clmnlist(5), clmnlist(4), clmnlist(3))  # pylint: disable=E1121
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
    pupil_teachers = pd.merge(masterfile_dfs["pupils"], masterfile_dfs["teachers"], on="rred_user_id")
    return pd.merge(pupil_teachers, masterfile_dfs["schools"], on="school_id")
