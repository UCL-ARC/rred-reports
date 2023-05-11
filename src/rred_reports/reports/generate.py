from pathlib import Path

import pandas as pd
from docx2pdf import convert
from pypdf import PdfMerger, PdfReader
from pypdf.errors import EmptyFileError, PdfReadError

from rred_reports.reports.schools import populate_school_data, school_filter


class ReportConversionException(Exception):
    """Custom exception generator for the TemplateFiller class"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


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


def validate_pdf(pdf_file_path: Path) -> None:
    """Check the validity of a converted PDF report
    Raises an appropriate error if file not valid.

    Args:
        pdf_file_path (Path): Path to PDF report
    """
    if not pdf_file_path.exists():
        message = "Report conversion failed - output PDF does not exist"
        raise ReportConversionException(message)

    with pdf_file_path.open("r") as converted_report:
        try:
            PdfReader(converted_report)
        except EmptyFileError as error:
            message = "Report conversion failed - empty PDF produced"
            raise ReportConversionException(message) from error
        except PdfReadError as error:
            message = "Report conversion failed - error reading resulting PDF"
            raise ReportConversionException(message) from error


def convert_single_report(docx_report_path: Path, output_pdf_path: Path) -> None:
    """Convert a single docx format report to PDF format

    Args:
        docx_report_path (Path): Path to input docx report file
        output_pdf_path (Path): Path to resulting output pdf report file
    """

    convert(input_path=docx_report_path, output_path=output_pdf_path)
    if not validate_pdf(output_pdf_path):
        message = "Report conversion failed - invalid PDF produced"
        raise ReportConversionException(message)


def concatenate_pdf_reports(report_collection: list[Path], output_dir: Path, output_file_name: str = "result") -> None:
    """Concatenate PDF reports and write output to file as a single PDF

    Args:
        report_collection (list[Path]): List of individual PDFs
        output_dir (Path): Output result file directory
        output_file_name (str, optional): Optional output filename. Defaults to "result".
    """
    merger = PdfMerger()

    try:
        for pdf in report_collection:
            merger.append(pdf)
    except FileNotFoundError as error:
        merger.close()
        message = "Concatenation error - one or more provided PDFs does not exist"
        raise ReportConversionException(message) from error
    except EmptyFileError as error:
        pdf.open().close()
        merger.close()
        message = "Concatenation error - empty file included in concatenation"
        raise ReportConversionException(message) from error

    merger.write(output_dir / f"{output_file_name}.pdf")
    merger.close()
