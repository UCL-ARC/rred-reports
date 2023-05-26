"""Validation of data used by redcap and for reporting"""
from pathlib import Path

import pandas as pd
from loguru import logger


def log_data_inconsistencies(masterfile_df: pd.DataFrame, dispatch_path: Path) -> None:
    dispatch_df = pd.read_excel(dispatch_path)
    dispatch_df.columns = "DL_" + dispatch_df.columns

    teacher_schools = masterfile_df[["rred_user_id", "school_id"]].copy().drop_duplicates()
    school_counts = teacher_schools.groupby("rred_user_id").count()
    multiple_schools = school_counts[school_counts["school_id"] > 1].copy()
    # Make empty dataframe so that downstream filtering works if there are not duplicated schools
    output_school_changed = pd.DataFrame(columns=["rred_user_id", "DL_RRED School ID", "school_id_1", "school_id_2"])
    if multiple_schools.size != 0:
        multiple_schools.drop("school_id", axis=1, inplace=True)
        multi_school_ids = pd.merge(teacher_schools, multiple_schools, how="inner", on="rred_user_id")
        multi_school_ids["row"] = "school_id_" + (multi_school_ids.groupby("rred_user_id").cumcount() + 1).apply(str)
        multi_school_pivoted = multi_school_ids.pivot(index=["rred_user_id"], columns="row", values="school_id").reset_index()
        multi_school_dispatch_list = pd.merge(dispatch_df, multi_school_pivoted, how="inner", left_on="DL_UserID", right_on="rred_user_id")
        output_school_changed = multi_school_dispatch_list[["rred_user_id", "DL_RRED School ID", "DL_School Label", "school_id_1", "school_id_2"]]

    if output_school_changed.size != 0:
        logger.warning(
            "{count} Users were found with different school IDs in the masterfile:\n {mismatch}",
            count=output_school_changed.shape[0],
            mismatch=output_school_changed.to_string(index=False),
        )

    inner_joined = pd.merge(dispatch_df, masterfile_df, how="inner", left_on="DL_UserID", right_on="rred_user_id")
    schools_differ = inner_joined[inner_joined["rrcp_school"].isna() & (~inner_joined["DL_UserID"].isin(output_school_changed["rred_user_id"]))]
    output_mismatch = schools_differ[["DL_UserID", "DL_RRED School ID", "DL_School Label", "rred_user_id", "school_id"]].copy().drop_duplicates()
    if output_mismatch.size != 0:
        logger.warning(
            "{count} Users were found with different school IDs in dispatch list and masterfile:\n {mismatch}",
            count=output_mismatch.shape[0],
            mismatch=output_mismatch.to_string(index=False),
        )

    outer_joined = pd.merge(dispatch_df, masterfile_df, how="outer", left_on="DL_RRED School ID", right_on="school_id")
    no_match = outer_joined[outer_joined["school_id"] != outer_joined["DL_RRED School ID"]]
    no_match = no_match[["DL_RRED School ID", "DL_School Label", "school_id"]].copy().drop_duplicates()

    not_in_masterfile = no_match[
        (~no_match["DL_RRED School ID"].isin(schools_differ["DL_RRED School ID"]))
        & (~no_match["DL_RRED School ID"].isin(output_school_changed["DL_RRED School ID"]))
        & (no_match["school_id"].isna())
    ]

    if not_in_masterfile.size != 0:
        logger.warning(
            "{count} School IDs were not found in masterfile. Check these have no data in the masterfile:\n {mismatch}",
            count=not_in_masterfile.shape[0],
            mismatch=not_in_masterfile.to_string(index=False),
        )

    not_in_dispatch_list = no_match[
        (~no_match["school_id"].isin(schools_differ["school_id"]))
        & (~no_match["school_id"].isin(output_school_changed["school_id_1"]))
        & (~no_match["school_id"].isin(output_school_changed["school_id_2"]))
        & (no_match["DL_RRED School ID"].isna())
    ]
    if not_in_dispatch_list.size != 0:
        logger.warning(
            "{count} School IDs were not found in dispatch list:\n {mismatch}",
            count=not_in_dispatch_list.shape[0],
            mismatch=not_in_dispatch_list["school_id"].tolist(),
        )
