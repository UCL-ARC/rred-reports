from pathlib import Path

import pandas as pd
import pytest
from pypdf import PdfMerger, PdfReader
from pypdf.errors import EmptyFileError, PdfReadError

from rred_reports.reports.generate import (
    ReportConversionException,
    concatenate_pdf_reports,
    convert_single_report,
    generate_report_school,
    validate_pdf,
)


def test_generate_report_school(temp_data_directories, data_path, mocker):
    output_dir = temp_data_directories["output"]

    populate_school_data_mock = mocker.patch("rred_reports.reports.generate.populate_school_data")

    template_file_path = data_path / "RRED_Report_Template_Single_Category.docx"
    example_processed_data = {
        "school_id": [1, 2, 3, 4],
        "reg_rr_title": ["RR Teacher + Support Role", "RR Teacher + Class Leader", "RR Teacher + Support Role", "RR Teacher + Class Leader"],
    }
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


def test_validate_pdf_failure_empty_file(mocker, template_report_pdf_path):
    mocker.patch.object(PdfReader, "__init__", side_effect=EmptyFileError)

    with pytest.raises(ReportConversionException) as error:
        validate_pdf(template_report_pdf_path)

    assert error.value.message == "Report conversion failed - empty PDF produced"


def test_validate_pdf_failure_no_metadata(mocker, template_report_pdf_path):
    mocker.patch.object(PdfReader, "__init__", side_effect=PdfReadError("test"))
    with pytest.raises(ReportConversionException) as error:
        validate_pdf(template_report_pdf_path)
    assert error.value.message == "Report conversion failed - error reading resulting PDF"


def test_concatenate_pdf_reports_success(template_report_pdf_path: Path, temp_out_dir: Path):
    # Original template file is 2 pages long
    files_to_concat = [template_report_pdf_path] * 5
    concatenate_pdf_reports(files_to_concat, temp_out_dir)
    expected_output_file_path = temp_out_dir / "result.pdf"
    assert (expected_output_file_path).is_file()

    # Expect 5 copies of the original file to contain 10 pages
    assert len(PdfReader(expected_output_file_path).pages) == 10


def test_concatenate_pdf_reports_failure_file_not_found(mocker, template_report_pdf_path: Path, temp_out_dir: Path):
    mocker.patch.object(PdfMerger, "append", side_effect=FileNotFoundError)

    files_to_concat = [template_report_pdf_path]

    with pytest.raises(ReportConversionException) as error:
        concatenate_pdf_reports(files_to_concat, temp_out_dir)
    expected_error_message = "Concatenation error - one or more provided PDFs does not exist"
    assert expected_error_message in error.value.message


def test_concatenate_pdf_reports_failure_empty_file(mocker, template_report_pdf_path: Path, temp_out_dir: Path):
    mocker.patch.object(PdfMerger, "append", side_effect=EmptyFileError)

    files_to_concat = [template_report_pdf_path]

    with pytest.raises(ReportConversionException) as error:
        concatenate_pdf_reports(files_to_concat, temp_out_dir)
    expected_error_message = "Concatenation error - empty file included in concatenation"
    assert expected_error_message in error.value.message
