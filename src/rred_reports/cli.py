# pylint: disable=W0613
from typing import Optional

import typer

from rred_reports import __version__
from rred_reports.redcap.interface import app as redcap
from rred_reports.reports.interface import app as reports

app = typer.Typer()
app.add_typer(redcap, name="redcap")
app.add_typer(reports, name="reports")


def version_callback(value: bool):
    """Prints the software version

    Args:
        value (bool): Boolean flag

    Raises:
        typer.Exit: Exits the program after printing version
    """
    if value:
        typer.echo(f"rred-reports {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    """RRED-Reports

    Args:
        version (Optional[bool], optional): Optional --version flag to print software version.
    """
    return
