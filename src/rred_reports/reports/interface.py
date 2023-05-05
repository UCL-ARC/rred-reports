from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
import tomli
import typer
from loguru import logger

from rred_reports.reports.generate import generate_report_school

app = typer.Typer()


class ReportType(str, Enum):
    """ReportType class

    Provides report types as enums
    """

    SCHOOL = "school"
    CENTRE = "centre"
    NATIONAL = "national"
    ALL = "all"


def validate_data_sources(year: int, template_file: Path, top_level_dir: Optional[Path] = None) -> dict:
    """Perform some basic data source validation

    Args:
        year (int): Year to process
        template_file (Path): Template file
        top_level_dir (Optional[Path], optional): Non-standard top level directory in which input
            data can be found. Defaults to None.

    Raises:
        processed_data_missing_error: FileNotFound error for missing processed data case
        FileNotFoundError: FileNotFoundError for missing template file

    Returns:
        dict: Dictionary of validated data sources
    """
    if top_level_dir is None:
        top_level_dir = Path(__file__).resolve().parents[3]

    data_path = top_level_dir / "output" / "processed" / str(year)
    template_file_path = top_level_dir / template_file
    output_dir = top_level_dir / "output" / "reports" / str(year) / "schools"

    try:
        processed_data = pd.read_csv(data_path / "processed_data.csv")
    except FileNotFoundError as processed_data_missing_error:
        logger.error(f'No processed data file found at {data_path / "processed_data.csv"}. Exiting.')
        raise processed_data_missing_error

    try:
        assert template_file_path.is_file()
    except AssertionError as error:
        logger.error(f"No template file found at {template_file_path}. Exiting.")
        raise FileNotFoundError from error

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    return {"data": processed_data, "template_file": template_file_path, "output_dir": output_dir}


@app.command()
def create(level: ReportType, year: int, config_file: str = "report_config.toml"):
    """Generate a report at the level specified

    Args:
        level (ReportType): school, centre, national
        year (int): Year to process
    """
    typer.echo(f"Creating a report for level: {level.value}")
    config = get_config(Path(config_file))

    template_file_path = config[level.value]["template"]
    validated_data = validate_data_sources(year, template_file_path)
    processed_data, template_file, output_dir = validated_data.values()
    if level.value.lower() == "school":
        generate_report_school(processed_data, template_file, output_dir)


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


@app.callback()
def main():
    """Run the report generation pipeline"""
    return
