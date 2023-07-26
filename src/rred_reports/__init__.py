"""
Copyright (c) 2023 UCL ARC. All rights reserved.

rred-reports: Extracts RRED data from REDCap, transforms and populates templates.
Allows automated sending of reports via email
"""

__version__ = "0.1.0"

__all__ = ("__version__", "get_config", "get_report_year_files", "ReportType")

from enum import Enum
from pathlib import Path

import tomli
from loguru import logger


class ReportType(str, Enum):
    """ReportType class

    Provides report types as enums
    """

    SCHOOL = "school"
    CENTRE = "centre"
    NATIONAL = "national"


def get_config(config_toml: Path) -> dict:
    """Load a toml config file

    Args:
        config_toml (Path): Path to config file

    Returns:
        dict: Dictionary of config data
    """
    try:
        with config_toml.open(mode="rb") as config_file:
            return tomli.load(config_file)
    except FileNotFoundError as error:
        logger.error(f"No report generation config file found at {config_toml}. Exiting.")
        raise error


def get_report_year_files(report_config: dict, report_type: ReportType, year: int):
    """
    Extract report files for a specific year of the rred_report config

    Args:
        report_config (dict): config for reports
        report_type (ReportType): type of report to use the config for
        year (int): year to filter by

    Returns:
        paths to dispatch file, masterfile, template file
    """
    try:
        year_config = report_config[report_type.value][str(year)]
    except KeyError as error:
        msg = f"Year not found in config: {year}. Please add this year to the report config file."
        raise KeyError(msg) from error
    template_file_path = year_config["template"]
    masterfile_path = year_config["masterfile"]
    dispatch_path = year_config["dispatch_list"]
    return dispatch_path, masterfile_path, template_file_path
