from pathlib import Path

import pandas as pd
import pytest

from rred_reports.masterfile import read_and_process_masterfile
from rred_reports.reports.schools import (
    filter_by_entry_and_exit,
    filter_for_three_four,
    filter_six,
    populate_school_data,
    school_filter,
    summary_table,
)


@pytest.fixture(scope="module")
def example_school_data(data_path: Path):
    testing_df = read_and_process_masterfile(data_path / "example_masterfile.xlsx")
    return school_filter(testing_df, "RRS2030220")


def test_summary_table_output(example_school_data: pd.DataFrame):
    """
    Given a masterfile with data for school RRS2030220, where one pupil is filtered by date range, leaving 5 pupils with a different exit outcome
    When a summary table is generated
    Then there should be a single teacher, 5 pupils, and one of each exit outcome
    """
    output = summary_table(example_school_data, 2021)

    assert output.equals(
        pd.DataFrame(
            {
                "number_of_rr_teachers": [1],
                "number_of_pupils_served": [5],
                "po_discontinued": [1],
                "po_referred_to_school": [1],
                "po_incomplete": [1],
                "po_left_school": [1],
                "po_ongoing": [1],
            }
        )
    )


def test_school_tables_filled(example_school_data: pd.DataFrame, templates_dir: Path, temp_out_dir: Path):
    """
    Given a masterfile with data from school RRS2030220, filtered to that school
    When the template for the school is populated using that data
    Then a file should be written with the tables filled in and a file should exist in the output path
    """
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(example_school_data, templates_dir / "2021/2021-22_template.docx", 2021, output_doc)

    assert populated_template.verify_tables_filled()
    assert output_doc.exists()


def test_missing_values_filled(example_school_data: pd.DataFrame, templates_dir: Path, temp_out_dir: Path):
    """
    Given a masterfile with data where the first pupil has missing numeric data in the poverty column
    When the template for the school is populated using that data
    Then the 8th column for povery should have "Missing Data" instead of "nan"
    """
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(example_school_data, templates_dir / "2021/2021-22_template.docx", 2021, output_doc)

    assert populated_template.tables[1].cell(1, 7).text == "Missing Data"


def test_duplicate_student_warning(example_school_data: pd.DataFrame, templates_dir: Path, temp_out_dir: Path, loguru_caplog):
    """
    Given a masterfile dataframe with one duplicated row
    When the school template is populated
    Then the resulting table will have one less row than the input data, and there will be a loguru message for the duplication
    """
    output_doc = temp_out_dir / "school.docx"

    duplicate_school_data = example_school_data.copy()
    duplicate_school_data.iloc[3] = duplicate_school_data.iloc[5]

    populated_template = populate_school_data(duplicate_school_data, templates_dir / "2021/2021-22_template.docx", 2021, output_doc)
    assert (duplicate_school_data.shape[0] - 1) == len(populated_template.tables[1].rows)
    assert "Duplicate students found" in loguru_caplog.text


def test_school_name_replaced_in_paragraphs(example_school_data, templates_dir: Path, temp_out_dir: Path):
    """
    Given a school template with the first non-blank paragraph having a "School A" placeholder
    When the template is populated with redcap data
    Then School A should be replaced by the name of the school
    """
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(example_school_data, templates_dir / "2021/2021-22_template.docx", 2021, output_doc)

    output_paragraphs = []
    for paragraph in populated_template.doc.paragraphs:
        if paragraph.text.strip() != "":
            output_paragraphs.append(paragraph.text)

    assert "School A" not in output_paragraphs[0]


@pytest.mark.parametrize(
    "pupil_id",
    # test-1_2021-22, Discontinued and within date boundary, no month3 or month 6 results. Should show in table 1,2,3,4,5.
    [
        "test-1_2021-22",
        # test-3_2021-22, Discontinued, entry date IN report date but exit date OUT of report date, no month3 or month 6 results. Should be in 1,2,5.
        "test-3_2021-22",
        # test-4_2021-22, Discontinued, entry date OUT of report date but exit date IN report date, month3 testdate in range. Should be in all tables.
        "test-4_2021-22",
        # test-5_2021-22, Incomplete and within date boundary. Should be in 1,2,5.
        "test-5_2021-22",
        # test-6_2021-22, Ongoing and entry date within boundary and NA exit date. Should be in 1,2,5.
        "test-6_2021-22",
    ],
)
def test_first_filter_kept(example_school_data, pupil_id):
    """
    Given a school that has data that is not within the date range
    When the template is populated with redcap data
    Then this template should be filled with the following:
    Table 1, 2, 5: test-1_2021-22, test-3_2021-22, test-4_2021-22, test-5_2021-22, test-6_2021-22
    """
    test_filter_for_one_two_five = filter_by_entry_and_exit(example_school_data, 2021)
    # first filter test
    assert (~example_school_data["reg_rr_title"].isin(["Teacher Leader", "Teacher Leader Only", "Teacher Leader + Support Role"])).any()
    assert (example_school_data["entry_date"] < "2022-8-1").all()
    assert (
        (example_school_data["exit_date"].isna()) | (example_school_data["exit_date"] > "2021-7-31") | (example_school_data["exit_date"] < "2022-8-1")
    ).all()
    pupil = test_filter_for_one_two_five.loc[test_filter_for_one_two_five.pupil_no == pupil_id]
    assert (
        ((pupil["entry_date"] < "2022-8-1") & (pupil["entry_date"] > "2021-7-31"))
        | ((pupil["exit_date"] < "2022-8-1") & (pupil["exit_date"] > "2021-7-31"))
    ).all()


def test_first_filter_removed(example_school_data):
    """
    Given a school that has data that is not within the date range
    When the template is populated with redcap data
    Then this template should not have pupil test-2_2021-22
    """
    test_filter_for_one_two_five = filter_by_entry_and_exit(example_school_data, 2021)
    # test-2_2021-22, Discontinued, not within date boundary, month3 testdate out of range, no month6. Should not be in any tables.
    pupil_2 = test_filter_for_one_two_five.loc[test_filter_for_one_two_five.pupil_no == "test-2_2021-22"]
    assert ((~pupil_2["entry_date"] < "2022-8-1") & (~pupil_2["entry_date"] > "2021-7-31")).all()
    assert all(((~pupil_2["exit_date"] < "2022-8-1") & (~pupil_2["exit_date"] > "2021-7-31")) | (pupil_2["exit_date"].isna()))


def test_table_3_4_filter(example_school_data):
    """
    Given a school that has data that is not within the date range
    When the template is populated with redcap data
    Then this template should be filled with the following:
    Table 3&4: test-1_2021-22, test-4_2021-22
    """
    test_filter_for_three_four = filter_for_three_four(example_school_data, 2021)
    # testing filter for table 3,4 applied
    assert (~test_filter_for_three_four["pupil_no"].isin(["2_2021-22-test", "3_2021-22-test", "5_2021-22-test", "11_2021-22-test"])).any()
    assert (~test_filter_for_three_four["exit_outcome"].isin(["Incomplete", "Ongoing"])).any()

    pupil_1 = test_filter_for_three_four.loc[test_filter_for_three_four.pupil_no == "1_2021-22-test"]
    assert (~pupil_1["exit_outcome"].isin(["Incomplete", "Ongoing"])).any()

    pupil_4 = test_filter_for_three_four.loc[test_filter_for_three_four.pupil_no == "4_2021-22-test"]
    assert (pupil_4["exit_outcome"].isin(["Discontinued", "Referred to school"])).any()


def test_table_6_filter(example_school_data):
    """
    Given a school that has data that is not within the date range
    When the template is populated with redcap data
    Then this template should be filled with the following:
    Table 6: test-1_2021-22, test-4_2021-22
    """
    test_filter_six = filter_six(example_school_data, 2021)

    six_filter = test_filter_six.loc[test_filter_six.pupil_no.isin(["1_2021-22-test", "4_2021-22-test"])]
    assert six_filter.shape[0] == 2
