"""Reading and use of the RRED dispatch list"""
from pathlib import Path

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
