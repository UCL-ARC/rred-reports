from pathlib import Path
from typing import Optional

import typer

from rred_reports import get_config
from rred_reports.masterfile import write_to_excel
from rred_reports.redcap.main import ExtractInput, RedcapReader
from rred_reports.validation import log_school_id_inconsistencies, write_issues_if_exist

top_level_dir = Path(__file__).resolve().parents[3]

app = typer.Typer()


@app.command()
def extract(
    year: int, config_file: Path = "src/rred_reports/redcap/redcap_config.toml", output_dir: Path = "output/", school_aliases: Optional[Path] = None
) -> None:
    """
    Extract files from redcap from wide to long and apply basic processing
    Process wide to long of the files listed under the year-based config toml
    Writes long data to the output directory
    Args:
        year (int): Year to process
        config_file (Path): Path to config file
        output_dir (Path): Path to parent output directory
        school_aliases (Optional[Path]): School alias file, where schools have changed IDs and should be merged
    """
    typer.echo(f"Extracting data for {year} and the previous year's surveys")
    config = get_config(config_file)[str(year)]

    end_year = str(year + 1)[-2:]
    current_period = f"{year}-{end_year}"

    dispatch_path = top_level_dir / config["dispatch_list"]

    parser = RedcapReader(dispatch_path, school_aliases)
    current_year = ExtractInput(
        top_level_dir / config["current_year"]["coded_data_file"],
        top_level_dir / config["current_year"]["label_data_file"],
        current_period,
    )
    previous_year = ExtractInput(
        top_level_dir / config["previous_year"]["coded_data_file"],
        top_level_dir / config["previous_year"]["label_data_file"],
        f"{year - 1}-{str(year)[-2:]}",
    )
    long_data = parser.read_redcap_data(current_year, previous_year)
    issues = log_school_id_inconsistencies(long_data, dispatch_path, year)
    output_file = output_dir / "issues" / f"{current_period}school_id_issues.xlsx"
    write_issues_if_exist(issues, output_file)

    output_file = output_dir / "processed" / f"masterfile_{current_period}.xlsx"
    write_to_excel(long_data, output_file)

    typer.echo(f"Output written to: {output_file}")


@app.callback()
def main():
    """Run the redcap extraction pipeline"""
    return


if __name__ == "__main__":
    extract(2021, top_level_dir / "src/rred_reports/redcap/redcap_config.toml")
