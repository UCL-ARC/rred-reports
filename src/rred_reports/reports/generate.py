from pathlib import Path

from rred_reports.reports.schools import populate_school_data, school_filter


def generate_report_school(school_ids: list[str], year: int) -> None:
    data_path = Path("/some/data/input/path")
    output_path = Path("/some/output/path")
    templates_dir = Path("/some/template/input/path")

    for school_id in school_ids:
        school_out_dir = output_path / school_id
        school_data = school_filter(data_path, school_id)
        output_doc = school_out_dir / f"school_report_{school_id}.docx"

        next_year_two_digit = int(str(year)[:2]) + 1
        populated_template = populate_school_data(
            school_data, templates_dir / f"{year}/{year}-{next_year_two_digit}_template.docx", school_id, output_doc
        )

        write_file(populated_template, output_doc)


def write_file():
    pass
