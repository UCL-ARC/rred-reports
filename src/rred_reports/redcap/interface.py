import typer

app = typer.Typer()


@app.command()
def extract(year: int):
    """Extract files from redcap and apply basic processing
    Process wide to long of the files listed under the year-based config toml
    Writes files to an appropriate output location
    Args:
        year (int): Year to process
    """
    typer.echo(f"Extracting data for year: {year}")
    return


@app.callback()
def main():
    """Run the redcap extraction pipeline"""
    return
