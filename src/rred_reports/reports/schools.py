from datetime import datetime
from pathlib import Path

import pandas as pd

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

table_three_columns = ["rred_user_id", "pupil_no", "entry_date_str", "exit_date_str", "exit_num_weeks", "exit_num_lessons", "exit_outcome"]

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


def trial_period_dates(report_year):
    """Function to get the start and end dates for reporting

    Args:
        report_year (int): Year of report end

    Returns: start_date and end_date in datetime format

    """
    start_date = datetime(report_year, 7, 31)
    end_date = datetime(report_year + 1, 8, 1)
    return start_date, end_date


def school_filter(whole_dataframe: pd.DataFrame, school_id):
    """Function to filter out the Teacher Leaders and by school

    Args:
        whole_dataframe (pd.DataFrame)
        school_id (string): School ID

    Returns: pd.DataFrame filtered to show only RR teachers data per school

    """
    teacher_filtered = whole_dataframe[~whole_dataframe["reg_rr_title"].isin(["Teacher Leader", "Teacher Leader in Training"])]
    return teacher_filtered[teacher_filtered.school_id == school_id].copy()


def filter_by_entry_and_exit(school_dataframe: pd.DataFrame, report_year):
    """Filter for tables: summary, table one, two and five: <entry_date> OR <exit_date> is after 31/7 and before 1/8

    Args:
        school_dataframe (pd.DataFrame): pd.DataFrame filtered with school_filter()
        report_year (int): Year of report end

    Returns: school_filter(pd.DataFrame) filtered by the reporting year
    """
    report_start, report_end = trial_period_dates(report_year)

    return school_dataframe.loc[
        ((school_dataframe["entry_date"] > report_start) & (school_dataframe["entry_date"] < report_end))
        | ((school_dataframe["exit_date"] > report_start) & (school_dataframe["exit_date"] < report_end))
    ]


def filter_for_three_four(school_dataframe: pd.DataFrame, report_year):
    """Filter for table three and four: ONLY on pupils whose <exit_date> is after 31/7 and before 1/8
    ONLY on data for pupils with 'Discontinued' OR 'Referred to school' in the <exit_outcome> column

    Args:
        school_dataframe (pd.DataFrame): pd.DataFrame filtered with school_filter()
        report_year (int): Year of report end

    Returns: school_filter(pd.DataFrame) filtered by exit_outcome and exit_date
    """
    report_start, report_end = trial_period_dates(report_year)

    outcome_filtered = school_dataframe[(school_dataframe["exit_outcome"].isin(["Discontinued", "Referred to school"]))]

    return outcome_filtered[(outcome_filtered["exit_date"] > report_start) & (outcome_filtered["exit_date"] < report_end)]


def filter_six(school_dataframe: pd.DataFrame, report_year):
    """Filter for table six ONLY those pupils who have 3 or 6 month follow up test dates after 31/7 and before 1/8/
    ONLY on data for pupils with 'Discontinued' OR 'Referred to school'

    Args:
        school_dataframe (pd.DataFrame): pd.DataFrame filtered with school_filter()
        report_year (int): Year of report end

    Returns: school_filter(pd.DataFrame) filtered by month3_testdate and month6_testdate"""

    report_start, report_end = trial_period_dates(report_year)

    outcome_filtered = school_dataframe[(school_dataframe["exit_outcome"].isin(["Discontinued", "Referred to school"]))]

    return outcome_filtered[
        ((outcome_filtered["month3_testdate"] > report_start) & (outcome_filtered["month3_testdate"] < report_end))
        | ((outcome_filtered["month6_testdate"] > report_start) & (outcome_filtered["month6_testdate"] < report_end))
    ]


def summary_table(school_df: pd.DataFrame, report_year: int):
    """
    Args:
        school_df (pd.DataFrame): pd.DataFrame filtered with school_filter()
        report_year (int): starting year for the report

    Returns:
        table with the following columns
            Number of RR teachers
            Number of pupils served
            (Pupil outcomes) Discontinued
            (Pupil outcomes) Referred to school
            (Pupil outcomes) Incomplete
            (Pupil outcomes) Left School
            (Pupil outcomes) Ongoing

    """
    columns_used = ["rred_user_id", "pupil_no", "exit_outcome"]

    def get_outcome_from_summary(school_df, outcome_type):
        try:
            return school_df["exit_outcome"].value_counts()[outcome_type]
        except KeyError:
            return 0

    filtered = filter_by_entry_and_exit(school_df, report_year)
    filtered_summary_table = filtered[columns_used]

    return pd.DataFrame(
        {
            "number_of_rr_teachers": [filtered_summary_table["rred_user_id"].nunique()],
            "number_of_pupils_served": [filtered_summary_table["pupil_no"].nunique()],
            "po_discontinued": get_outcome_from_summary(filtered_summary_table, "Discontinued"),
            "po_referred_to_school": get_outcome_from_summary(filtered_summary_table, "Referred to school"),
            "po_incomplete": get_outcome_from_summary(filtered_summary_table, "Incomplete"),
            "po_left_school": get_outcome_from_summary(filtered_summary_table, "Left school"),
            "po_ongoing": get_outcome_from_summary(filtered_summary_table, "Ongoing"),
        }
    )


def populate_school_tables(school_df: pd.DataFrame, template_path: Path, report_year) -> TemplateFiller:
    """Function to fill the school template tables, saving them the file

    Args:
        school_df (pd.DataFrame): pd.DataFrame filtered with school_filter()
        template_path (Path): Location of template
        report_year (int): Year of report end

    Returns: The template filler with populated data
    """

    # adding a column for table four
    lost_lesson_cols = [col for col in school_df if col.startswith("exit_lessons_missed")]
    school_df["total_lost_lessons"] = school_df[lost_lesson_cols].sum(axis=1)

    columns_and_filters = (
        (table_one_columns, filter_by_entry_and_exit),
        (table_two_columns, filter_by_entry_and_exit),
        (table_three_columns, filter_for_three_four),
        (table_four_columns, filter_for_three_four),
        (table_five_columns, filter_by_entry_and_exit),
        (table_six_columns, filter_six),
    )

    header_rows = [2, 1, 1, 1, 1, 2, 2]

    # adding in summary table first
    template_filler = TemplateFiller(template_path, header_rows)
    add_in_summary_table = summary_table(school_df, report_year)
    template_filler.populate_table(0, add_in_summary_table)

    # now adding other tables
    for index, column_and_filter in enumerate(columns_and_filters):
        columns, filter_function = column_and_filter
        filtered = filter_function(school_df, report_year)
        table_to_write = filtered[columns]
        template_filler.populate_table(index + 1, table_to_write)

    return template_filler


def populate_school_data(school_df: pd.DataFrame, template_path: Path, report_year, output_path, school_placeholder="School A") -> TemplateFiller:
    """Function to populate and save the template with: name of school and filled tables

    Args:
        school_df (pd.DataFrame): pd.DataFrame filtered with school_filter()
        template_path (Path): Location of template
        report_year (int): Year of the report end
        output_path (Path): Location of the report
        school_placeholder (string): Placeholder for test

    Returns: The template filler with populated data and appropriate school name saved in the output path"""

    template_filler = populate_school_tables(school_df, template_path, report_year)

    school_name = school_df["rrcp_school"].iloc[0]

    for paragraph in template_filler.doc.paragraphs:
        for run in paragraph.runs:
            if school_placeholder in run.text:
                run.text = run.text.replace(school_placeholder, school_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    template_filler.save_document(output_path)
    return template_filler
