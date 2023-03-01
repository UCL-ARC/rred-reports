from pathlib import Path

import pytest

from rred_reports.reports.filler import TemplateFiller


@pytest.fixture(scope="module")
def temp_out_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("temp_out_dir")


@pytest.fixture()
def template_report_path() -> Path:
    """
    Returns a Path object representing a test report template docx file
    """
    return Path(__file__).resolve().parents[2] / "input" / "templates" / "RRED_Report_Template_Single_Category.docx"


@pytest.fixture()
def template_filler(template_report_path) -> Path:
    """
    Returns a TemplateFiller object to avoid boilerplate in tests
    """
    return TemplateFiller(template_report_path)
