from pathlib import Path

import typer

from rred_reports.redcap.main import ExtractInput, RedcapReader
from rred_reports.reports.interface import get_config

top_level_dir = Path(__file__).resolve().parents[3]


app = typer.Typer()


@app.command()
def extract(year: int, config_file: Path = "src/rred_reports/redcap/redcap_config.toml", output_dir: Path = "output/processed/") -> None:
    """
    Extract files from redcap from wide to long and apply basic processing
    Process wide to long of the files listed under the year-based config toml
    Writes long data to the output directory
    Args:
        year (int): Year to process
        config_file (Path): Path to config file
        output_dir (Path): Path to output directory where the long CSV data will be saved
    """
    typer.echo(f"Extracting data for {year} and the previous year's surveys")
    config = get_config(config_file)[str(year)]

    end_year = str(year + 1)[-2:]
    current_period = f"{year}-{end_year}"

    dispatch_path = top_level_dir / config["dispatch_list"]

    parser = RedcapReader(dispatch_path)
    current_year = ExtractInput(
        top_level_dir / config["current_year"]["coded_data_file"],
        top_level_dir / config["current_year"]["label_data_file"],
        current_period,
    )
    previous_year = ExtractInput(
        top_level_dir / config["previous_year"]["coded_data_file"],
        top_level_dir / config["previous_year"]["label_data_file"],
        f"{year -1}-{str(year)[-2:]}",
    )
    long_data = parser.read_redcap_data(current_year, previous_year)
    output_file = output_dir / f"masterfile_{current_period}.csv"
    long_data.to_csv(output_file, index=False)
    typer.echo(f"Output written to: {output_file}")


@app.callback()
def main():
    """Run the redcap extraction pipeline"""
    return


if __name__ == "__main__":
    extract(2021, top_level_dir / "src/rred_reports/redcap/redcap_config.toml")
