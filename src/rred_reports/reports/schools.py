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


def school_filter(whole_dataframe: pd.DataFrame, school_id):
    """Function to filter out the Teacher Leaders and by school

    Args: pd.DataFrame, school_id

    Returns: pd.DataFrame filtered to show only RR teachers data per school

    """
    teacher_filtered = whole_dataframe[
        (whole_dataframe.reg_rr_title == "RR Teacher + Support Role") | (whole_dataframe.reg_rr_title == "RR Teacher + Class Leader")
    ]
    return teacher_filtered[teacher_filtered.school_id == school_id].copy()


# specific filter for each table
def filter_for_one_two_five(school_dataframe: pd.DataFrame):
    """Filter for table one, two and five: <entry_date> OR <exit_date> is after 31/7/21 and before 1/8/22

    Args: school_filter(pd.DataFrame)

    Returns: school_filter(pd.DataFrame) filtered by the reporting year
    """
    return school_dataframe.loc[
        ((school_dataframe["entry_date"] > "2021-07-31") & (school_dataframe["entry_date"] < "2022-08-01"))
        | ((school_dataframe["exit_date"] > "2021-07-31") & (school_dataframe["exit_date"] < "2022-08-01"))
    ]


def filter_for_three_four(school_dataframe: pd.DataFrame):
    """Filter for table three and four: ONLY on pupils whose <exit_date> is after 31/7/21 and before 1/8/22.
    ONLY on data for pupils with 'Discontinued' OR 'Referred to school' in the <exit_outcome> column

    Args: school_filter(pd.DataFrame)

    Returns: school_filter(pd.DataFrame) filtered by exit_outcome and exit_date
    """
    outcome_filtered = school_dataframe[
        (school_dataframe["exit_outcome"] == "Discontinued") | (school_dataframe["exit_outcome"] == "Referred to school")
    ]

    return outcome_filtered[(outcome_filtered["exit_date"] > "2021-07-31") & (outcome_filtered["exit_date"] < "2022-08-01")]


def filter_six(school_dataframe: pd.DataFrame):
    """Filter for table six, for later use

    Args: school_filter(pd.DataFrame)"""
    outcome_filtered = school_dataframe[
        (school_dataframe["exit_outcome"] == "Discontinued") | (school_dataframe["exit_outcome"] == "Referred to school")
    ]

    return outcome_filtered[
        ((outcome_filtered["month3_testdate"] > "2021-07-31") & (outcome_filtered["month3_testdate"] < "2022-08-01"))
        | ((outcome_filtered["month6_testdate"] > "2021-07-31") & (outcome_filtered["month6_testdate"] < "2022-08-01"))
    ]


def summary_table(school_df: pd.DataFrame):
    """
    Args:
        school_filter(pd.DataFrame)

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

    def filter_summary_table(school_df):
        """Filter for summary table

        Args: school_filter(pd.DataFrame)
        """
        return school_df

    def get_outcome_from_summary(school_df, outcome_type):
        try:
            return school_df["exit_outcome"].value_counts()[outcome_type]
        except KeyError:
            return 0

    filtered = filter_summary_table(school_df)
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


def populate_school_tables(school_df: pd.DataFrame, template_path: Path) -> TemplateFiller:
    """Function to fill the school template tables, saving them the file

    Args: school_filter(pd.DataFrame), Path, school_id

    Returns: The template filler with populated data
    """

    # adding a column for table four
    lost_lesson_cols = [col for col in school_df if col.startswith("exit_lessons_missed")]
    school_df["total_lost_lessons"] = school_df[lost_lesson_cols].sum(axis=1)

    columns_and_filters = (
        (table_one_columns, filter_for_one_two_five),
        (table_two_columns, filter_for_one_two_five),
        (table_three_columns, filter_for_three_four),
        (table_four_columns, filter_for_three_four),
        (table_five_columns, filter_for_one_two_five),
        (table_six_columns, filter_six),
    )

    header_rows = [2, 1, 1, 1, 1, 2, 2]

    # adding in summary table first
    template_filler = TemplateFiller(template_path, header_rows)
    add_in_summary_table = summary_table(school_df)
    template_filler.populate_table(0, add_in_summary_table)

    # now adding other tables
    for index, column_and_filter in enumerate(columns_and_filters):
        columns, filter_function = column_and_filter
        filtered = filter_function(school_df)
        table_to_write = filtered[columns]
        template_filler.populate_table(index + 1, table_to_write)

    return template_filler


def populate_school_data(school_df: pd.DataFrame, template_path: Path, school_id, output_path=None, school_placeholder="School A") -> TemplateFiller:
    """Function to populate and save the template with: name of school and filled tables

    Args: school_filter(pd.DataFrame), Path, school_id

    Returns: The template filler with populated data and appropriate school name saved in the output path"""

    template_filler = populate_school_tables(school_df, template_path)

    school_name = school_df["rrcp_school"].iloc[0]

    for paragraph in template_filler.doc.paragraphs:
        for run in paragraph.runs:
            if school_placeholder in run.text:
                run.text = run.text.replace(school_placeholder, school_name)

    if not output_path:
        output_path = Path(f"output/reports/{school_id}.docx")
    template_filler.save_document(output_path)
    return template_filler
