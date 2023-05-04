from pathlib import Path

import pandas as pd

from rred_reports.reports.schools import populate_school_data, school_filter


def generate_report_school(school_ids: list[str], year: int) -> None:
    """Generate a report at the school level given a list of school IDs

    Args:
        school_ids (list[str]): List of school IDs
        year (int): Year to process
    """

    data_path = Path(__file__).resolve().parents[3] / "output" / "processed" / "year"
    processed_data = pd.read_csv(data_path / "processed_data.csv")

    output_path = Path(__file__).resolve().parents[3] / "output" / "reports" / "year" / "schools"
    templates_dir = Path(__file__).resolve().parents[3] / "input" / "templates" / "year"

    for school_id in school_ids:
        school_out_dir = output_path / school_id
        school_data = school_filter(processed_data, school_id)
        output_doc = school_out_dir / f"school_report_{school_id}.docx"

        next_year_two_digit = int(str(year)[:2]) + 1
        populate_school_data(school_data, templates_dir / f"{year}/{year}-{next_year_two_digit}_template.docx", school_id, output_doc)
