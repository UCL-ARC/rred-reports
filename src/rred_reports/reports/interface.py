from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from loguru import logger

from rred_reports import get_config
from rred_reports.reports.generate import generate_report_school, convert_single_report, concatenate_pdf_reports
from rred_reports.reports.emails import school_mailer

app = typer.Typer()


class ReportType(str, Enum):
    """ReportType class

    Provides report types as enums
    """

    SCHOOL = "school"
    CENTRE = "centre"
    NATIONAL = "national"


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
        top_level_dir = Path(__file__).resolve().parents[6]

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
def generate(
    level: ReportType, year: int, config_file: Path = "src/rred_reports/reports/report_config.toml", top_level_dir: Optional[Path] = None
) -> Path:
    """Generate a report at the level specified

    Args:
        level (ReportType): school, centre, national
        year (int): Year to process
        top_level_dir (Optional[Path], optional): Non-standard top level directory in which input
            data can be found. Defaults to None.

    Returns:
        Path: Output directory for generated reports
    """
    typer.echo(f"Generating report for level: {level.value}")
    config = get_config(config_file)

    template_file_path = config[level.value]["template"]
    validated_data = validate_data_sources(year, template_file_path, top_level_dir=top_level_dir)
    processed_data, template_file, output_dir = validated_data.values()

    if level.value.lower() == "school":
        generate_report_school(processed_data, template_file, output_dir)
    else:
        typer.echo("Other levels currently not implemented! Please select 'school'.")
        raise typer.Exit()
    return output_dir


@app.command()
def convert(report_dir: Path, output: str = "result") -> Path:
    """Convert multiple docx reports to PDF and concatenate into a single file

    Args:
        report_dir (Path): Directory containing generated docx reports
        output (str): Output file name, without extension

    Returns:
        Path: Path to directory containing PDF reports
    """
    pdf_paths = []
    for report_path in report_dir.glob("*.docx"):
        output_path = report_path.with_suffix(".pdf")
        convert_single_report(docx_report_path=report_dir, output_pdf_path=output_path)
        pdf_paths.append(report_path)

    concatenate_pdf_reports(pdf_paths, report_dir, output)

    return report_dir


@app.command()
def create(level: ReportType, year: int, config_file: Path = "src/rred_reports/reports/report_config.toml", output: str = "result"):
    """Generate reports at the level specified, convert to PDF and concatenate

    Args:
        level (ReportType): school, centre, national
        year (int): Year to process
    """
    typer.echo(f"Creating a report for level: {level.value}")
    report_dir = generate(level, year, config_file)

    convert(report_dir, output)


@app.command()
def send_school(
    year: int,
    id_list: Optional[list[str]] = None,
    attachment: str = "RRED_report.pdf",
    config_file: Path = "src/rred_reports/reports/report_config.toml",
):
    """Send reports to school contacts via RRED school ID

    Args:
        year (int): Report start year
        id_list (Optional[list[str]], optional): List of school IDs from which to send reports. Defaults to None.
        attachment (str, optional): Alternative attachment name. Defaults to "RRED_report.pdf".
    """
    config = get_config(config_file)
    dispatch_list = config["dispatch_list"]

    top_level_dir = Path(__file__).resolve().parents[6]
    if id_list is None:
        id_list = []
        report_directory = top_level_dir / "output" / "reports" / str(year) / "schools"
        for report_path in report_directory.glob("report_*.pdf"):
            id_list.append(report_path.stem.split("_")[-1])

    for school_id in id_list:
        school_mailer(school_id, dispatch_list, year, report_name=attachment)


@app.callback()
def main():
    """Run the report generation pipeline"""
    return
