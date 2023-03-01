import os
from pathlib import Path

import pandas as pd

from rred_reports.reports.filler import TemplateFiller


def test_load_report(template_report_path):
    document = TemplateFiller(template_report_path)
    # Expect the document to have two tables
    assert len(document.tables) == 2


def test_save_modified_report(temp_out_dir, template_filler):
    assert len(os.listdir(temp_out_dir)) == 0
    template_filler.save_document(Path(temp_out_dir, "demo.docx"))
    assert "demo.docx" in os.listdir(temp_out_dir)


def test_remove_all_rows(template_filler):
    tables = template_filler.tables
    first_table = tables[0]

    # 7 here as template report has an extra blank row
    # under the header. It's based off the actual
    # report template, so assuming other data will
    # look similar.
    assert len(first_table.rows) == 7
    TemplateFiller.remove_all_rows(first_table)
    assert len(first_table.rows) == 1


def test_populate_table(template_filler):
    tables = template_filler.tables
    first_table = tables[0]
    assert len(first_table.rows) == 7
    df = pd.DataFrame()
    template_filler.populate_table(first_table, df)

    row_contents = [cell.text.strip() for cell in first_table.row_cells(1)]
    assert len(first_table.columns) == len(row_contents)
    assert len(first_table.rows) == 2


def test_view_table_header(template_filler):
    first_table = template_filler.tables[0]
    headers = template_filler.view_header(first_table)
    expected_headers = [
        "RRED User ID",
        "Pupil Number",
        "Year Group",
        "Gender",
        "Summer Birthday",
        "Ethnicity",
        "First Language",
        "Poverty Indicator",
        "Special Cohort Group",
        "Outcome",
    ]
    assert expected_headers == [cell.text.strip() for cell in headers]
