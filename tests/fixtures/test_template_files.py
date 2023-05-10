import io
from pathlib import Path

import pandas as pd
import pytest
from docx import Document

from rred_reports.reports.filler import TemplateFiller


@pytest.fixture(scope="module")
def temp_out_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("temp_out_dir")


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


@pytest.fixture()
def template_report_path(data_path) -> Path:
    """
    Returns a Path object representing a test report template docx file
    """
    return data_path / "RRED_Report_Template_Single_Category.docx"


@pytest.fixture()
def template_report_bytes(template_report_path: Path) -> bytes:
    """Return a bytes representation of a template report

    Args:
        template_report_path (Path): Path to the template report file

    Returns:
        bytes: Array of bytes representing the report
    """
    doc = Document(template_report_path)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    return file_stream.getvalue()


@pytest.fixture()
def template_filler(data_path) -> Path:
    """
    Returns a TemplateFiller object to avoid boilerplate in tests
    """
    return TemplateFiller(data_path / "RRED_Report_Template_Single_Category.docx", [1, 1, 2])


@pytest.fixture()
def template_filler_populated_tables(template_filler) -> TemplateFiller:
    """
    Returns a TemplateFiller object to avoid boilerplate in tests
    """

    test_data_table_one = {
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

    test_data_table_two = {
        "RRED User ID": ["1", "2", "3"],
        "Pupil Number": ["1", "2", "3"],
        "SEND Status on Entry": ["1", "2", "3"],
        "Outcome": ["1", "2", "3"],
    }

    test_data_table_three = {
        "RRED User ID": ["1", "2", "3"],
        "Pupil Number": ["1", "2", "3"],
        "Year Group": ["1", "2", "3"],
        "book_entry": ["1", "2", "3"],
        "book_exit": ["1", "2", "3"],
        "Outcome": ["1", "2", "3"],
    }

    test_df_table_one = pd.DataFrame.from_dict(test_data_table_one)
    test_df_table_two = pd.DataFrame.from_dict(test_data_table_two)
    test_df_table_three = pd.DataFrame.from_dict(test_data_table_three)

    template_filler.populate_table(0, test_df_table_one)
    template_filler.populate_table(1, test_df_table_two)
    template_filler.populate_table(2, test_df_table_three)

    return template_filler
