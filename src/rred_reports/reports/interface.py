from enum import Enum
from pathlib import Path

import typer

from rred_reports.reports.generate import generate_report_school

app = typer.Typer()


class ReportType(str, Enum):
    school = "school"
    centre = "centre"
    national = "national"
    all = "all"


@app.command()
def create(level: ReportType, year: int):
    """Generate a report at the level specified

    Args:
        level (ReportType): school, centre, national
        year (int): Year to process
    """
    typer.echo(f"Creating a report for level: {level.value}")

    selection = level.value

    if selection == "school":
        school_ids = Path("/path/to/data")
        generate_report_school(school_ids, year)

    return


@app.callback()
def main():
    """Run the report generation pipeline"""
    return
