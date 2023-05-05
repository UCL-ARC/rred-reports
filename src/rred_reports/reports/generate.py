from pathlib import Path

import pandas as pd

from rred_reports.reports.schools import populate_school_data, school_filter


def generate_report_school(processed_data: pd.DataFrame, template_file: Path, output_dir: Path) -> None:
    """Generate a report at the school level given a list of school IDs

    Args:
        processed_data (pd.DataFrame): Pandas dataframe of processed data
        template_file (Path): The template file to be used
        output_dir (Path): Output directory for saved files
    """
    school_ids = processed_data.loc[:, "school_id"].unique().tolist()

    for school_id in school_ids:
        school_out_dir = output_dir / str(school_id)
        school_data = school_filter(processed_data, school_id)
        output_doc = school_out_dir / f"{str(school_id)}.docx"
        populate_school_data(school_data, template_file, school_id, output_doc)
