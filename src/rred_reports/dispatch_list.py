"""Reading and use of the RRED dispatch list"""
from pathlib import Path

import numpy as np
import pandas as pd


class DispatchListException(Exception):
    """Exception for dispatch list processing"""


def get_unique_schools(dispatch_path: Path) -> pd.DataFrame:
    """
    Get unique schools from dispatch file
    Args:
        dispatch_path (Path): path to dispatch file

    Returns:
        pd.DataFrame: of "RRED School ID" and "School Name"
    Raises:
        DispatchListException: Non-unique school name found
    """
    dispatch_list = pd.read_excel(dispatch_path)
    schools = dispatch_list.loc[:, ["School Label", "RRED School ID"]]
    schools.rename({"School Label": "School Name"}, axis=1, inplace=True)
    unique_schools = schools.drop_duplicates()

    _raise_if_school_duplicated(unique_schools)

    return unique_schools


def _raise_if_school_duplicated(schools) -> None:
    """
    Ensures that a school is unique (e.g. the same school ID doesn't have two different names)

    Args:
        schools (Path): path to dispatch file

    Raises:
        DispatchListException: If non-unique school name found
    """
    school_id_check = schools["RRED School ID"].duplicated(keep=False)
    duplicated_schools = schools[school_id_check]
    if not duplicated_schools.empty:
        message = f"Schools of the same ID which have different names:\n{duplicated_schools.sort_values(by='RRED School ID')}"
        raise DispatchListException(message)


def get_mailing_info(rred_school_id: str, dispatch_list: Path) -> dict:
    """Obtain the mailing info for a single school ID

    Args:
        rred_school_id (str): RRED School ID
        dispatch_list (Path): Path to dispatch list excel file

    Raises:
        ReportDispatchException: If no contact email is found

    Returns:
        dict: Dictionary containing mailing information for a single school
    """

    dispatch_df = pd.read_excel(dispatch_list)

    # pare down the DF
    dispatch_df = dispatch_df.loc[dispatch_df["RRED School ID"].str.match(rred_school_id)]
    dispatch_df = dispatch_df.loc[:, ["RRED School ID", "School Label", "Email", "TL Email"]]

    # School doesn't exist in dispatch list
    if len(dispatch_df) == 0:
        message = f"School not found in dispatch list: {rred_school_id}. Try deleting all output reports and generating them again"
        raise DispatchListException(message)

    # Find no teacher email instance - replace with TL if that exists

    dispatch_df.loc[:, "Mailing List"] = np.nan
    dispatch_df.loc[(~dispatch_df["Email"].isna()), "Mailing List"] = dispatch_df["Email"]
    dispatch_df.loc[(dispatch_df["Email"].isna()) & (~dispatch_df["TL Email"].isna()), "Mailing List"] = dispatch_df["TL Email"]

    # Drop any null email instances and report them out
    missing_email = dispatch_df.loc[dispatch_df["Mailing List"].isna()]
    try:
        assert len(missing_email) == 0
    except AssertionError as error:
        missing_ids = missing_email["RRED School ID"].tolist()
        message = f"Missing contact ID for schools with RRED IDs: {missing_ids}. Exiting."
        raise DispatchListException(message) from error

    # Case 2: Find instances of multiple teacher emails
    # Remove any space-delimited lists and replace with comma separated
    cleaned_mailing_list = dispatch_df.loc[:, "Mailing List"].str.replace(" ", ",").str.replace(",,", ",")
    dispatch_df.loc[:, "Mailing List"] = cleaned_mailing_list
    mailing_info = dispatch_df.loc[:, ["RRED School ID", "School Label", "Mailing List"]]

    # Teacher emails may be entered on separate rows, in which case this DF will have multiple rows

    try:
        assert len(mailing_info["School Label"].unique()) == 1
    except AssertionError as error:
        message = "Multiple school labels in resulting DataFrame"
        raise DispatchListException(message) from error

    school_id = mailing_info["RRED School ID"].unique()[0]
    school_label = mailing_info["School Label"].tolist()
    mailing_list = mailing_info["Mailing List"].tolist()

    mailing_info = {"rred_school_id": school_id, "school_label": school_label, "mailing_list": mailing_list}

    return mailing_info
