from typing import Optional

import typer

from rred_reports import __version__
from rred_reports.redcap.interface import app as redcap
from rred_reports.reports.interface import app as reports

app = typer.Typer()
app.add_typer(redcap, name="redcap")
app.add_typer(reports, name="report")


def version_callback(value: bool):
    if value:
        typer.echo(f"rred-reports {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    return
