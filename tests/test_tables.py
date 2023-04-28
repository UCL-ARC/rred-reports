import os
from pathlib import Path

import pandas as pd
import pytest

from rred_reports.reports.filler import TemplateFiller, TemplateFillerException


def test_load_report(template_filler):
    # Expect the document to have two tables
    assert len(template_filler.tables) == 3


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


def test_verify_new_rows_failure_raises_exception(template_filler):
    tables = template_filler.tables
    first_table = tables[0]
    test_bad_data = {
        "RRED User ID": ["1", "2", "3"],
        "Pupil Number": ["1", "2", "3"],
        "Year Group": ["1", "2", "3"],
        "Gender": ["1", "2", "3"],
        "Summer Birthday": ["1", "2", "3"],
        "Ethnicity": ["1", "2", "3"],
        "First Language": ["1", "2", "3"],
        "Poverty Indicator": ["1", "2", "3"],
        "Special Cohort Group": ["1", "2", "3"],
    }
    test_df = pd.DataFrame.from_dict(test_bad_data)
    with pytest.raises(TemplateFillerException):
        template_filler._verify_new_rows(first_table, test_df)


def test_custom_template_filler_exception_message():
    filler_exception = TemplateFillerException("Scary error")
    assert filler_exception.__repr__() == "Scary error"


def test_verify_new_rows_good_data(template_filler):
    tables = template_filler.tables
    first_table = tables[0]
    test_good_data = {
        "RRED User ID": ["1", "2", "3"],
        "Pupil Number": ["1", "2", "3"],
        "Year Group": ["1", "2", "3"],
        "Gender": ["1", "2", "3"],
        "Summer Birthday": ["1", "2", "3"],
        "Ethnicity": ["1", "2", "3"],
        "First Language": ["1", "2", "3"],
        "Poverty Indicator": ["1", "2", "3"],
        "Special Cohort Group": ["1", "2", "3"],
        "Outcome": ["1", "2", "3"],
    }
    test_df = pd.DataFrame.from_dict(test_good_data)
    template_filler._verify_new_rows(first_table, test_df)


def test_verify_tables_filled(template_filler_populated_tables):
    template_filler = template_filler_populated_tables
    template_filler.verify_tables_filled()


def test_verify_tables_filled_fails_with_missing_data(template_filler):
    test_bad_data = {
        "RRED User ID": ["1", "2", "3"],
        "Pupil Number": ["1", "2", "3"],
        "Year Group": ["1", "2", "3"],
        "Gender": ["1", "2", "3"],
        "Summer Birthday": ["1", "2", "3"],
        "Ethnicity": ["1", "2", "3"],
        "First Language": ["1", "2", "3"],
        "Poverty Indicator": ["1", "2", "3"],
        "Special Cohort Group": ["1", "2", "3"],
        "Outcome": ["1", "2", ""],
    }
    test_df = pd.DataFrame.from_dict(test_bad_data)
    template_filler.populate_table(0, test_df)

    with pytest.raises(TemplateFillerException):
        template_filler.verify_tables_filled()


def test_populate_table(template_filler):
    tables = template_filler.tables
    first_table_before_population = tables[0]
    assert len(first_table_before_population.rows) == 7

    test_data = {
        "RRED User ID": ["1", "2", "3"],
        "Pupil Number": ["1", "2", "3"],
        "Year Group": ["1", "2", "3"],
        "Gender": ["1", "2", "3"],
        "Summer Birthday": ["1", "2", "3"],
        "Ethnicity": ["1", "2", "3"],
        "First Language": ["1", "2", "3"],
        "Poverty Indicator": ["1", "2", "3"],
        "Special Cohort Group": ["1", "2", "3"],
        "Outcome": ["1", "2", "3"],
    }
    test_df = pd.DataFrame.from_dict(test_data)

    template_filler.populate_table(0, test_df)

    first_table = tables[0]
    first_row_contents = [cell.text.strip() for cell in first_table.row_cells(1)]
    assert len(first_table.columns) == len(first_row_contents)
    assert len(first_table.rows) == len(list(test_data.values())[0]) + 1


def test_view_table_header(template_filler):
    first_table = template_filler.tables[0]
    headers = TemplateFiller.view_header(first_table)
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


def test_remove_duplicated_columns(template_filler):
    second_table = template_filler.tables[1]
    columns = len(second_table.columns)
    second_table.cell(0, 0).text = "Outcome"

    template_filler.clean_tables()
    second_table_updated = template_filler.tables[1]

    assert len(second_table_updated.columns) == columns - 1


def test_remove_single_row(template_filler_populated_tables):
    template_filler = template_filler_populated_tables
    second_table = template_filler.tables[1]
    rows_before_removal = len(second_table.rows)
    TemplateFiller.remove_row(second_table, second_table.rows[3])
    rows_after_removal = len(second_table.rows)

    assert rows_before_removal - 1 == rows_after_removal


def test_table_with_merged_header(template_filler):
    """
    Given a table with two header rows, with merged cells
    When the table is populated with two header rows being defined
    Then the header rows should be maintained and values start on the third row
    """
    test_df = pd.DataFrame.from_dict(
        {
            "RRED User ID": ["1", "2", "3"],
            "Pupil Number": ["1", "2", "3"],
            "Year Group": ["1", "2", "3"],
            "book_entry": ["1", "2", "3"],
            "book_exit": ["1", "2", "3"],
            "Outcome": ["1", "2", "3"],
        }
    )

    template_filler.populate_table(2, test_df)

    header_table = template_filler.tables[2]
    first_row = [cell.text.strip() for cell in header_table.row_cells(0)]
    second_row = [cell.text.strip() for cell in header_table.row_cells(1)]
    third_row = [cell.text.strip() for cell in header_table.row_cells(2)]
    # ensure that merged rows are repeated and that the header is maintained
    assert first_row[2:5] == ["Year Group", "Book Level", "Book Level"]
    assert second_row[2:5] == ["Year Group", "Entry", "Exit"]
    # ensure that values start being populated in the correct place
    assert third_row[2:5] == ["1", "1", "1"]


def test_report_bytes(template_filler):
    bytes_out = template_filler.report_bytes()
    assert isinstance(bytes_out, bytes)
