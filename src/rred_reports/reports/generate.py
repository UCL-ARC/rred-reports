from pathlib import Path

import pandas as pd
from docx2pdf import convert
from loguru import logger
from pypdf import PdfMerger, PdfReader
from pypdf.errors import EmptyFileError, PdfReadError
from tqdm import tqdm

from rred_reports.reports.schools import populate_school_data, school_filter


class ReportConversionException(Exception):
    """Custom exception generator for the TemplateFiller class"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


def generate_report_school(processed_data: pd.DataFrame, template_file: Path, output_dir: Path, report_year: int) -> None:
    """Generate a report at the school level given a list of school IDs

    Args:
        processed_data (pd.DataFrame): Pandas dataframe of processed data
        template_file (Path): The template file to be used
        output_dir (Path): Output directory for saved files
    """
    school_ids: list[str] = processed_data.loc[:, "school_id"].sort_values(ascending=True).unique().tolist()
    logger.info("Generating reports for {total_schools} schools", total_schools=len(school_ids))
    schools_with_no_data = []
    schools_with_no_name = []

    for school_id in tqdm(school_ids):
        school_data = school_filter(processed_data, school_id)

        if school_data.size == 0:
            logger.trace("No data remaining after filtering for school {school}", school=school_id)
            schools_with_no_data.append(school_id)
            continue

        if all(school_data["rrcp_school"].isna()):
            logger.trace("No name found for school {school}", school=school_id)
            schools_with_no_name.append(school_id)
            continue

        output_doc = output_dir / f"report_{str(school_id)}.docx"
        populate_school_data(school_data, template_file, report_year, output_path=output_doc)
    if schools_with_no_data:
        logger.warning(
            "{school_count} schools did not have data remaining after filtering: {schools}",
            school_count=len(schools_with_no_data),
            schools=schools_with_no_data,
        )
    if schools_with_no_name:
        logger.warning(
            "{school_count} schools had no name in the masterfile (presumably weren't in the dispatch list at extract): {schools}",
            school_count=len(schools_with_no_name),
            schools=schools_with_no_name,
        )


def validate_pdf(pdf_file_path: Path) -> bool:
    """Check the validity of a converted PDF report
    Raises an appropriate error if file not valid.

    Args:
        pdf_file_path (Path): Path to PDF report
    """
    if not pdf_file_path.exists():
        message = f"Report conversion failed - output PDF does not exist: {pdf_file_path}"
        raise ReportConversionException(message)

    with pdf_file_path.open("rb") as converted_report:
        try:
            PdfReader(converted_report)
        except EmptyFileError as error:
            message = f"Report conversion failed - empty PDF produced: {pdf_file_path}"
            raise ReportConversionException(message) from error
        except PdfReadError as error:
            message = f"Report conversion failed - error reading resulting PDF: {pdf_file_path}"
            raise ReportConversionException(message) from error
    return True


def convert_all_reports(docx_report_paths: list[Path], output_pdf_paths: list[Path]) -> None:
    """Convert all docx format reports in a directory to PDF format

    Doing this all at once means that MS Word on OSX doesn't need to be granted access to each input file directly

    Args:
        docx_report_paths (list[Path]): Paths to input docx report files
        output_pdf_paths (list[Path]): Paths to resulting output pdf report files
    """
    # Removing previous pdfs so OSX doesn't need to grant access to those files
    for path in output_pdf_paths:
        path.unlink(missing_ok=True)

    convert(input_path=docx_report_paths[0].parent)

    logger.info("Validating output PDFs")
    for report_path, output_path in zip(docx_report_paths, output_pdf_paths):
        if not validate_pdf(output_path):
            message = "Report conversion failed - invalid PDF produced"
            logger.error("{message} for docx {report}", message=message, report=report_path)
            raise ReportConversionException(message)


def concatenate_pdf_reports(report_collection: list[Path], output_dir: Path, output_file_name: str = "uat_combined") -> None:
    """Concatenate PDF reports and write output to file as a single PDF

    Args:
        report_collection (list[Path]): List of individual PDFs
        output_dir (Path): Output result file directory
        output_file_name (str, optional): Optional output filename
    """
    logger.info("Combining PDFs for user acceptance")
    merger = PdfMerger()
    if len(report_collection) == 0:
        message = "Concatenation error - no PDFs provided"
        raise ReportConversionException(message)
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

    output_path = output_dir / f"{output_file_name}.pdf"
    merger.write(output_path)
    merger.close()
    logger.success("UAT pdf written to {path} !", path=output_path)
