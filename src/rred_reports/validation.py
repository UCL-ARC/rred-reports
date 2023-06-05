"""Validation of data used by redcap and for reporting"""
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from loguru import logger

from rred_reports.reports.schools import filter_by_entry_and_exit

KEY_FOR_COLUMNS = "---\nkey:\nDL_ = Dispatch List, MF_ = Master File\n---\n"


@dataclass
class ValidationIssue:
    """Issue type to report for validation, can be logged or exported to file"""

    title: str
    description: str
    dataframe: pd.DataFrame


def log_school_id_inconsistencies(masterfile_df: pd.DataFrame, dispatch_path: Path, year: int) -> list[ValidationIssue]:
    """
    Log inconsistencies in school ids within the masterfile, and between that and the dispatch list

    Args:
        masterfile_df (pd.DataFrame): masterfile data
        dispatch_path (Path): path to dispatch list
        year (int): starting year of the study period
    """
    dispatch_df = pd.read_excel(dispatch_path)
    dispatch_df.columns = "DL_" + dispatch_df.columns

    # only keep rows in the trial period
    masterfile_for_period = filter_by_entry_and_exit(masterfile_df, year)
    school_changed = _schools_changed(dispatch_df, masterfile_for_period)
    # issues encountered, updated in each `_check_..` method
    issues = []

    _check_schools_changed(issues, school_changed)
    schools_differ = _check_schools_differ(dispatch_df, issues, masterfile_for_period, school_changed)

    no_match = _mismatch_schools(dispatch_df, masterfile_for_period)

    _check_not_in_masterfile(issues, no_match, school_changed, schools_differ)
    _check_not_in_dispatch_list(issues, masterfile_for_period, no_match, school_changed, schools_differ, year)

    return issues


def _schools_changed(dispatch_df: pd.DataFrame, masterfile_for_period: pd.DataFrame) -> pd.DataFrame:
    teacher_schools = masterfile_for_period[["rred_user_id", "school_id"]].copy().drop_duplicates()
    school_counts = teacher_schools.groupby("rred_user_id").count()
    multiple_schools = school_counts[school_counts["school_id"] > 1].copy()

    return_columns = ["rred_user_id", "DL_RRED School ID", "DL_School Label", "school_id_1", "school_id_2"]
    if multiple_schools.size == 0:
        return pd.DataFrame(columns=return_columns)
    multiple_schools.drop("school_id", axis=1, inplace=True)
    multi_school_ids = pd.merge(teacher_schools, multiple_schools, how="inner", on="rred_user_id")
    multi_school_ids["row"] = "school_id_" + (multi_school_ids.groupby("rred_user_id").cumcount() + 1).apply(str)
    multi_school_pivoted = multi_school_ids.pivot(index=["rred_user_id"], columns="row", values="school_id").reset_index()
    multi_school_dispatch_list = pd.merge(dispatch_df, multi_school_pivoted, how="inner", left_on="DL_UserID", right_on="rred_user_id")
    return multi_school_dispatch_list[return_columns]


def _check_schools_differ(
    dispatch_df: pd.DataFrame, issues: list[ValidationIssue], masterfile_for_period: pd.DataFrame, school_changed: pd.DataFrame
) -> pd.DataFrame:
    inner_joined = pd.merge(dispatch_df, masterfile_for_period, how="inner", left_on="DL_UserID", right_on="rred_user_id")
    schools_differ = inner_joined[inner_joined["rrcp_school"].isna() & (~inner_joined["DL_UserID"].isin(school_changed["rred_user_id"]))]
    output_mismatch = schools_differ[["DL_UserID", "DL_RRED School ID", "DL_School Label", "rred_user_id", "school_id"]].copy().drop_duplicates()
    if output_mismatch.size != 0:
        output_mismatch.rename({"school_id": "MF_school_id"}, axis=1, inplace=True)
        message = f"{output_mismatch.shape[0]} Users were found with different school IDs in dispatch list compared to masterfile:\n{KEY_FOR_COLUMNS}"
        logger.warning(
            "{message}\n{mismatch}",
            message=message,
            mismatch=output_mismatch.to_string(index=False),
        )
        issues.append(ValidationIssue("school_mismatch", message, output_mismatch))
    return schools_differ


def _mismatch_schools(dispatch_df: pd.DataFrame, masterfile_for_period: pd.DataFrame):
    outer_joined = pd.merge(dispatch_df, masterfile_for_period, how="outer", left_on="DL_RRED School ID", right_on="school_id")
    no_match = outer_joined[outer_joined["school_id"] != outer_joined["DL_RRED School ID"]]
    return no_match[["DL_RRED School ID", "DL_School Label", "school_id"]].copy().drop_duplicates()


def _check_schools_changed(issues: list[ValidationIssue], school_changed: pd.DataFrame):
    if school_changed.size != 0:
        output_school_changed = school_changed.rename({"school_id_1": "MF_school_id_1", "school_id_2": "MF_school_id_2"}, axis=1)
        message = f"{output_school_changed.shape[0]} Users were found with multiple school IDs in the masterfile:\n{KEY_FOR_COLUMNS}"
        logger.warning("{message}\n{mismatch}", message=message, mismatch=output_school_changed.to_string(index=False))
        issues.append(ValidationIssue("multiple_ids", message, output_school_changed))


def _check_not_in_masterfile(
    issues: list[ValidationIssue], no_match: pd.DataFrame, school_changed: pd.DataFrame, schools_differ: pd.DataFrame
) -> None:
    not_in_masterfile = no_match[
        (~no_match["DL_RRED School ID"].isin(schools_differ["DL_RRED School ID"]))
        & (~no_match["DL_RRED School ID"].isin(school_changed["DL_RRED School ID"]))
        & (no_match["school_id"].isna())
    ].copy()
    if not_in_masterfile.size != 0:
        not_in_masterfile.rename({"school_id": "MF_school_id"}, axis=1, inplace=True)
        message = f"{not_in_masterfile.shape[0]} School IDs were not found in masterfile:\n{KEY_FOR_COLUMNS}"
        logger.warning(
            "{message}\n{mismatch}",
            message=message,
            mismatch=not_in_masterfile.to_string(index=False),
        )
        issues.append(ValidationIssue("not_in_masterfile", message, not_in_masterfile))


def _check_not_in_dispatch_list(
    issues: list[ValidationIssue],
    masterfile_for_period: pd.DataFrame,
    no_match: pd.DataFrame,
    school_changed: pd.DataFrame,
    schools_differ: pd.DataFrame,
    year: int,
) -> None:
    not_in_dispatch_list = no_match[
        (~no_match["school_id"].isin(schools_differ["school_id"]))
        & (~no_match["school_id"].isin(school_changed["school_id_1"]))
        & (~no_match["school_id"].isin(school_changed["school_id_2"]))
        & (no_match["DL_RRED School ID"].isna())
    ]
    if not_in_dispatch_list.size != 0:
        data_in_current_survey = masterfile_for_period.loc[masterfile_for_period["pupil_no"].str.contains(str(year)), ["school_id"]].drop_duplicates()
        data_in_current_survey["in_current_survey"] = True
        output_not_in_dispatch = pd.merge(not_in_dispatch_list, data_in_current_survey, how="left", on="school_id")
        output_not_in_dispatch.loc[output_not_in_dispatch["in_current_survey"].isna(), "in_current_survey"] = False
        output_not_in_dispatch = output_not_in_dispatch[["school_id", "in_current_survey"]]

        message = f"{output_not_in_dispatch.shape[0]} School IDs were not found in dispatch list:"
        logger.warning(
            "{message}\n{mismatch}",
            message=message,
            mismatch=output_not_in_dispatch.to_string(index=False),
        )
        issues.append(ValidationIssue("not_in_dispatch_list", message, output_not_in_dispatch))


def write_issues_if_exist(issues: list[ValidationIssue], issues_path: Path) -> None:
    """
    Writes out issues to Excel file if there are any.

    Args:
        issues (list[ValidationIssues]): List of validation issues, can be empty.
        issues_path (Path): Excel file to write to, parent directories will be created if they don't exist
    """
    if not issues:
        return
    issues_path.parent.mkdir(parents=True, exist_ok=True)
    logger.warning("Writing issues to {path}", path=issues_path)
    with pd.ExcelWriter(issues_path, engine="openpyxl") as writer:
        for issue in issues:
            description_lines = issue.description.split("\n")
            # Write out issue into new sheet, with the description above the table
            issue.dataframe.to_excel(writer, sheet_name=issue.title, startrow=len(description_lines))
            sheet = writer.sheets[issue.title]
            for index, line in enumerate(description_lines):
                sheet.cell(index + 1, 1, value=line)
