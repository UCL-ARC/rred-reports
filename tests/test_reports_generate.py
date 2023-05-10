from pathlib import Path

import pandas as pd
import pytest
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from rred_reports.reports.generate import ReportConversionException, convert_single_report, generate_report_school, validate_pdf


def test_generate_report_school(temp_data_directories, data_path, mocker):
    output_dir = temp_data_directories["output"]

    populate_school_data_mock = mocker.patch("rred_reports.reports.generate.populate_school_data")

    template_file_path = data_path / "RRED_Report_Template_Single_Category.docx"
    example_processed_data = {"school_id": [1, 2, 3, 4]}
    test_dataframe = pd.DataFrame.from_dict(example_processed_data)

    generate_report_school(test_dataframe, template_file_path, output_dir)
    assert populate_school_data_mock.call_count == len(example_processed_data["school_id"])


def test_convert_single_report_success(mocker, template_report_path: Path, temp_out_dir: Path):
    output_file_path = temp_out_dir / "converted_report.pdf"
    pdf_conversion_mock = mocker.patch("rred_reports.reports.generate.convert")
    pdf_validity_check_mock = mocker.patch("rred_reports.reports.generate.validate_pdf")
    convert_single_report(template_report_path, output_file_path)
    pdf_conversion_mock.assert_called_once()
    pdf_validity_check_mock.assert_called_once()


def test_validate_pdf_failure_missing_file():
    with pytest.raises(ReportConversionException) as error:
        validate_pdf(Path("/path/to/report.pdf"))

    assert error.value.message == "Report conversion failed - output PDF does not exist"


def test_validate_pdf_failure_empty_file(template_report_empty_pdf_path):
    with pytest.raises(ReportConversionException) as error:
        validate_pdf(template_report_empty_pdf_path)

    assert error.value.message == "Report conversion failed - empty PDF produced"


def test_validate_pdf_failure_no_metadata(mocker, template_report_pdf_path):
    mocker.patch.object(PdfReader, "__init__", side_effect=PdfReadError("test"))
    with pytest.raises(ReportConversionException) as error:
        validate_pdf(template_report_pdf_path)
    assert error.value.message == "Report conversion failed - error reading resulting PDF"
