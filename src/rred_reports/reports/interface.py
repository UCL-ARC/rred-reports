from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from rred_reports import get_config
from rred_reports.masterfile import read_and_process_masterfile
from rred_reports.reports.generate import generate_report_school, convert_all_reports, concatenate_pdf_reports
from rred_reports.reports.emails import school_mailer

app = typer.Typer()

TOP_LEVEL_DIR = Path(__file__).resolve().parents[3]


class ReportType(str, Enum):
    """ReportType class

    Provides report types as enums
    """

    SCHOOL = "school"
    CENTRE = "centre"
    NATIONAL = "national"


def validate_data_sources(year: int, template_file: Path, masterfile_path: Path, top_level_dir: Optional[Path] = None) -> dict:
    """Perform some basic data source validation

    Args:
        year (int): Year to process
        template_file (Path): Template file
        masterfile_path (Path): Masterfile file
        top_level_dir (Optional[Path], optional): Non-standard top level directory in which input
            data can be found. Defaults to None.

    Raises:
        processed_data_missing_error: FileNotFound error for missing processed data case
        FileNotFoundError: FileNotFoundError for missing template file

    Returns:
        dict: Dictionary of validated data sources
    """
    if top_level_dir is None:
        top_level_dir = TOP_LEVEL_DIR

    data_path = top_level_dir / masterfile_path
    template_file_path = top_level_dir / template_file
    output_dir = top_level_dir / "output" / "reports" / str(year) / "schools"

    processed_data = read_and_process_masterfile(data_path)

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
    masterfile_path = config[level.value]["masterfile"]
    validated_data = validate_data_sources(year, template_file_path, masterfile_path, top_level_dir=top_level_dir)
    processed_data, template_file, output_dir = validated_data.values()

    if level.value.lower() == "school":
        generate_report_school(processed_data, template_file, output_dir, year)
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
    logger.info("Converting docx reports to pdf reports. ")
    report_paths = list(report_dir.glob("*.docx"))
    pdf_paths = []
    for report_path in sorted(report_paths):
        output_path = report_path.with_suffix(".pdf")
        pdf_paths.append(output_path)

    convert_all_reports(report_paths, pdf_paths)

    concatenate_pdf_reports(pdf_paths, report_dir, output)

    return report_dir


@app.command()
def create(level: ReportType, year: int, config_file: Path = "src/rred_reports/reports/report_config.toml", output: str = "uat_combined"):
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
    attachment_name: str = "RRED_report.pdf",
    config_file: Path = "src/rred_reports/reports/report_config.toml",
    top_level_dir: Optional[Path] = None,
):
    """Send reports to school contacts via RRED school ID

    Args:
        year (int): Report start year
        id_list (Optional[list[str]], optional): List of school IDs from which to send reports. Defaults to None.
        attachment_name (str, optional): Alternative attachment name. Defaults to "RRED_report.pdf".
        config_file (Optional[Path], optional): Non-standard configuration file for processing
        top_level_dir (Optional[Path], optional): Non-standard top level directory in which input
            data can be found. Defaults to None.
    """
    config = get_config(config_file)
    dispatch_list = Path(config["school"]["dispatch_list"]).resolve()

    if top_level_dir is None:
        top_level_dir = TOP_LEVEL_DIR

    if id_list is None:
        id_list = []
        report_directory = top_level_dir / "output" / "reports" / str(year) / "schools"
        for report_path in report_directory.glob("report_*.pdf"):
            id_list.append(report_path.stem.split("_")[-1])

    for school_id in id_list:
        school_mailer(school_id, dispatch_list, year, report_name=attachment_name)


@app.callback()
def main():
    """Run the report generation pipeline"""
    return


if __name__ == "__main__":
    create(ReportType.SCHOOL, 2021, TOP_LEVEL_DIR / "src/rred_reports/reports/report_config.toml")
