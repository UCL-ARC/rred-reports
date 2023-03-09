import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
from pandas_dataclasses import AsFrame, Data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Pupil(AsFrame):
    """Pupil information"""

    pupil_no: Data[str]
    rred_user_id: Data[str]
    assessi_engtest2: Data[pd.Int32Dtype]
    assessi_iretest1: Data[float]
    assessi_iretype1: Data[float]
    assessi_maltest1: Data[float]
    assessi_outcome: Data[float]
    assessi_scotest1: Data[float]
    assessi_scotest2: Data[float]
    assessi_scotest3: Data[float]
    assessii_engcheck1: Data[float]
    assessii_engtest4: Data[float]
    assessii_engtest5: Data[float]
    assessii_engtest6: Data[float]
    assessii_engtest7: Data[float]
    assessii_engtest8: Data[float]
    assessii_scotest4: Data[float]
    assessii_iretest2: Data[float]
    assessii_iretype2: Data[float]
    assessiii_engtest10: Data[float]
    assessiii_engtest11: Data[float]
    assessiii_engtest9: Data[float]
    assessiii_iretest4: Data[float]
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
    entry_bl_result: Data[float]
    entry_li_result: Data[float]
    entry_cap_result: Data[float]
    entry_wt_result: Data[float]
    entry_wv_result: Data[float]
    entry_hrsw_result: Data[float]
    entry_bas_result: Data[float]
    exit_num_weeks: Data[float]
    exit_num_lessons: Data[float]
    exit_lessons_missed_ca: Data[float]
    exit_lessons_missed_cu: Data[float]
    exit_lessons_missed_ta: Data[float]
    exit_lessons_missed_tu: Data[float]
    exit_bl_result: Data[float]
    exit_li_result: Data[float]
    exit_cap_result: Data[float]
    exit_wt_result: Data[float]
    exit_wv_result: Data[float]
    exit_hrsw_result: Data[float]
    exit_bas_result: Data[float]
    month3_testdate: Data[Literal["datetime64[ns]"]]
    month3_bl_result: Data[float]
    month3_wv_result: Data[float]
    month3_bas_result: Data[float]
    month6_testdate: Data[Literal["datetime64[ns]"]]
    month6_bl_result: Data[float]
    month6_wv_result: Data[float]
    month6_bas_result: Data[float]
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


# function for getting list from df columns


def createdf(file: Path) -> pd.DataFrame:
    """Create a nested dataframe from an excel file

    Args:
        file (Path): Path object pointing to excel file

    Returns:
        pd.DataFrame: Nested pandas DataFrame
    """
    df = pd.read_excel(file)

    def clmnlist(i):
        return list(df.iloc[:, i])

    all_schools_df = School.new(clmnlist(6), clmnlist(5), clmnlist(4), clmnlist(3))
    all_schools_df = all_schools_df.drop_duplicates()

    teach_df = Teacher.new(clmnlist(1), clmnlist(2), clmnlist(6))
    teach_df = teach_df.drop_duplicates()

    drop_cols = list(all_schools_df.columns.values)
    drop_cols.append(teach_df.columns.values[1])
    df_slimmed = df.drop(columns=drop_cols)
    school_teacher = []
    school_dict = all_schools_df.to_dict("records")
    for school in school_dict:
        school_df = pd.DataFrame.from_dict([school])
        school_teacher.append(pd.merge(school_df["school_id"], teach_df, how="inner", on="school_id"))

    teacher_pupils = []
    for teacher in school_teacher:
        pupil_df = pd.merge(teacher["rred_user_id"], df_slimmed, how="inner", on="rred_user_id")
        teacher_pupils.append(pupil_df)

    school_teacher_df = pd.DataFrame({"school_teacher": school_teacher})
    teacher_pupil_df = pd.DataFrame({"teacher_pupil": teacher_pupils})

    return pd.DataFrame({"dfs": [school_teacher_df, teacher_pupil_df]}, index=["school_teacher", "teacher_pupil"])


def parse_nested_dataframe(nested_df: pd.DataFrame) -> dict[pd.DataFrame]:
    """Helper function to parse the nested dataframe
    Removes a single layer of nesting

    Args:
        nested_df (pd.DataFrame): Nested pandas DataFrame
    Returns:
        dict[pd.DataFrame]: _description_
    """

    school_teacher_df = nested_df.loc["school_teacher"].iloc[0]["school_teacher"]
    teacher_pupil_df = nested_df.loc["teacher_pupil"].iloc[0]["teacher_pupil"]

    return {"school_teacher": school_teacher_df, "teacher_pupil": teacher_pupil_df}


def print_nested_dataframe_contents(nested_df: pd.DataFrame) -> None:
    """Print the contents of a nested dataframe
    Mainly for convenience/debugging. Should be replaced with
    some proper logging if we're going to use this going forward.

    Args:
        nested_df (pd.DataFrame): Nested pandas DataFrame
    """

    for dataframe in nested_df:
        logger.info(dataframe)


def main():
    """Entrypoint for generating nested dataframe"""
    file_path = Path(__file__).resolve().parents[2] / "input" / "templates" / "example_dataset.xlsx"
    full_nested_df = createdf(file_path)

    unravelled_data = parse_nested_dataframe(full_nested_df)

    school_teacher_df = unravelled_data["school_teacher"]
    teacher_pupil_df = unravelled_data["teacher_pupil"]

    print_nested_dataframe_contents(school_teacher_df)
    print_nested_dataframe_contents(teacher_pupil_df)

    return full_nested_df


if __name__ == "__main__":
    main()
