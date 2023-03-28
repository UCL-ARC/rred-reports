from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
from loguru import logger
from pandas_dataclasses import AsFrame, Data


@dataclass
class Pupil(AsFrame):
    """Pupil information"""

    pupil_no: Data[str]
    rred_user_id: Data[str]
    assessi_engtest2: Data[pd.Int32Dtype]
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


def create_nested_df(file: Path) -> pd.DataFrame:
    """Create a nested dataframe from an excel file

    Args:
        file (Path): Path object pointing to excel file

    Returns:
        pd.DataFrame: Nested pandas DataFrame
    """
    full_data = pd.read_excel(file)

    def clmnlist(i):
        return list(full_data.iloc[:, i])

    all_schools_df = School.new(clmnlist(6), clmnlist(5), clmnlist(4), clmnlist(3))  # pylint: disable=E1121
    all_schools_df = all_schools_df.drop_duplicates()  # pylint: disable=E1101

    teach_df = Teacher.new(clmnlist(1), clmnlist(2), clmnlist(6))  # pylint: disable=E1121
    teach_df = teach_df.drop_duplicates()  # pylint: disable=E1101

    drop_cols = list(all_schools_df.columns.values)
    drop_cols.append(teach_df.columns.values[1])

    df_slimmed = full_data.drop(columns=drop_cols)

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
    full_nested_df = create_nested_df(file_path)

    unravelled_data = parse_nested_dataframe(full_nested_df)

    school_teacher_df = unravelled_data["school_teacher"]
    teacher_pupil_df = unravelled_data["teacher_pupil"]

    print_nested_dataframe_contents(school_teacher_df)
    print_nested_dataframe_contents(teacher_pupil_df)

    return full_nested_df


if __name__ == "__main__":
    main()

# testing

print_nested_dataframe_contents(parse_nested_dataframe(create_nested_df("example_dataset.xlsx"))["teacher_pupil"])
print_nested_dataframe_contents(parse_nested_dataframe(create_nested_df("example_dataset.xlsx"))["school_teacher"])
