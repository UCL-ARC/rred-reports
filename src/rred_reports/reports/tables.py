from pathlib import Path

import pandas as pd

from rred_reports.masterfile import join_masterfile_dfs, parse_masterfile
from rred_reports.reports.filler import TemplateFiller

table_one_columns = [
    "rred_user_id",
    "pupil_no",
    "entry_year",
    "entry_gender",
    "summer",
    "entry_ethnicity",
    "entry_language",
    "entry_poverty",
    "entry_special_cohort",
    "exit_outcome",
]

table_two_columns = ["rred_user_id", "pupil_no", "entry_sen_status", "exit_outcome"]

table_three_columns = ["rred_user_id", "pupil_no", "entry_date", "exit_date", "exit_num_weeks", "exit_num_lessons", "exit_outcome"]

table_four_columns = [
    "rred_user_id",
    "pupil_no",
    "exit_lessons_missed_ca",
    "exit_lessons_missed_cu",
    "exit_lessons_missed_ta",
    "exit_lessons_missed_tu",
    "total_lost_lessons",
    "exit_outcome",
]

table_five_columns = [
    "rred_user_id",
    "pupil_no",
    "entry_year",
    "entry_bl_result",
    "exit_bl_result",
    "entry_li_result",
    "exit_li_result",
    "entry_cap_result",
    "exit_cap_result",
    "entry_wt_result",
    "exit_wt_result",
    "entry_wv_result",
    "exit_wv_result",
    "entry_hrsw_result",
    "exit_hrsw_result",
    "entry_bas_result",
    "exit_bas_result",
    "exit_outcome",
]

table_six_columns = [
    "rred_user_id",
    "pupil_no",
    "exit_bl_result",
    "month3_bl_result",
    "month6_bl_result",
    "exit_wv_result",
    "month3_wv_result",
    "month6_wv_result",
    "exit_bas_result",
    "month3_bas_result",
    "month6_bas_result",
    "exit_outcome",
]


def school_filter(df: pd.DataFrame, school_id):
    """Function to filter school"""
    return df[df.school_id == school_id]


# specific filter for each table
def filter_one(df: pd.DataFrame):
    return df


def filter_two(df: pd.DataFrame):
    return df


def filter_three(df: pd.DataFrame):
    return df


def filter_four(df: pd.DataFrame):
    return df


def filter_five(df: pd.DataFrame):
    return df


def filter_six(df: pd.DataFrame):
    return df


def summary_table(school_df: pd.DataFrame):
    """
    Args:
        pd.DataFrame

    Returns:
        table with the following columns
            Number of RR teachers
            Number of pupils served
            (Pupil outcomes) Discontinued
            (Pupil outcomes) Referred to school
            (Pupil outcomes) Incomplete
            (Pupil outcomes) Left School
            (Pupil outcomes) Ongoining
    """
    columns_used = ["rred_user_id", "pupil_no", "exit_outcome"]

    def filter_summary_table(df):
        """
        Filter for summary table
        """
        return df

    def get_outcome_from_summary(df, outcome_type):
        try:
            return df["exit_outcome"].value_counts()[outcome_type]
        except KeyError:
            return 0

    filtered = filter_summary_table(school_df)
    summary_table = filtered[columns_used]

    return pd.DataFrame(
        {
            "number_of_rr_teachers": [summary_table["rred_user_id"].nunique()],
            "number_of_pupils_served": [summary_table["pupil_no"].nunique()],
            "po_discontinud": get_outcome_from_summary(summary_table, "Discontinued"),
            "po_referred_to_school": get_outcome_from_summary(summary_table, "Referred to school"),
            "po_incomplete": get_outcome_from_summary(summary_table, "Incomplete"),
            "po_left_school": get_outcome_from_summary(summary_table, "Left school"),
            "po_ongoing": get_outcome_from_summary(summary_table, "Ongoing"),
        }
    )


def make_table(school_df: pd.DataFrame, template_path: Path):
    # adding a column for table four
    school_df["total_lost_lessons"] = school_df[list(school_df.columns)[45:49]].sum(axis=1)

    columns_and_filters = (
        (table_one_columns, filter_one),
        (table_two_columns, filter_two),
        (table_three_columns, filter_three),
        (table_four_columns, filter_four),
        (table_five_columns, filter_five),
        (table_six_columns, filter_six),
    )

    header_rows = [2, 1, 1, 1, 1, 2, 2]

    # adding in summary table first
    template_filler = TemplateFiller(template_path, header_rows)
    add_in_summary_table = summary_table(school_df)
    template_filler.populate_table(0, add_in_summary_table)
    template_filler.save_document(r"output/reports/test.docx")

    # now adding other tables
    for index, column_and_filter in enumerate(columns_and_filters):
        template_filler = TemplateFiller("output/reports/test.docx", header_rows)
        columns, filter_function = column_and_filter
        filtered = filter_function(school_df)
        table_to_write = filtered[columns]
        template_filler.populate_table(index + 1, table_to_write)
        template_filler.save_document(r"output/reports/test.docx")


# some tests
if __name__ == "__main__":
    nested_data = parse_masterfile("tests/data/example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    make_table(
        school_filter(testing_df, "RRS2030250"),
        "C:/Users/Katie Buntic/OneDrive - University College London/Projects/RRED/rred-reports/input/templates/2021/2021-22_template.docx",
    )
