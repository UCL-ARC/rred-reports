from __future__ import annotations

import typer
from loguru import logger


@logger.catch
def console(example_input: str):
    """Function to define the CLI interface.
    :param example_input: Silly text to log, just to show that the CLI is working

    Uncaught exceptions logged by loguru which uses `better exceptions`
    """
    logger.info(f"Running command '{example_input}'")
    ...


def main():
    """Entry point of CLI application, wraps the console function with typer"""
    typer.run(console)


if __name__ == "__main__":
    main()
