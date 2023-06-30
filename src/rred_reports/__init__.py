"""
Copyright (c) 2023 UCL ARC. All rights reserved.

rred-reports: Extracts RRED data from REDCap, transforms and populates templates.
Allows automated sending of reports via email
"""

__version__ = "0.1.0"

__all__ = ("__version__", "get_config")

from pathlib import Path

import tomli
from loguru import logger


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
