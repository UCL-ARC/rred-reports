import typer

app = typer.Typer()


@app.command()
def create(level: str):
    """Create a report"""
    typer.echo(f"Creating a report for level: {level}")


@app.callback()
def main():
    """Run the report generation pipeline"""
    return
