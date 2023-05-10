import pandas as pd

from rred_reports.reports.generate import generate_report_school


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
