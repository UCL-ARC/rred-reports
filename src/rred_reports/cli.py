from typing import Optional

import typer

from rred_reports import __version__

app = typer.Typer()

from rred_reports import __version__


@app.command()
def report(level: str):
    """Run the report generation pipeline"""
    typer.echo(f"Creating a report for level: {level}")


def version_callback(value: bool):
    if value:
        typer.echo(f"rred-reports v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    return
