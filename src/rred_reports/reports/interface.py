from enum import Enum

import typer

app = typer.Typer()


class ReportType(str, Enum):
    school = "school"
    centre = "centre"
    national = "national"
    all = "all"


@app.command()
def create(level: ReportType):
    """Generate a report at the level specified

    Args:
        level (ReportType): school, centre, national
    """
    typer.echo(f"Creating a report for level: {level.value}")

    selection = level.value

    if selection == "school":
        # perform school processing
        pass

    return


@app.callback()
def main():
    """Run the report generation pipeline"""
    return
