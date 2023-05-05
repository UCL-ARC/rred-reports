from pathlib import Path

from rred_reports.masterfile import join_masterfile_dfs, parse_masterfile
from rred_reports.reports.schools import filter_for_one_two_five, filter_for_three_four, filter_six, populate_school_data, school_filter


def test_school_tables_filled(data_path: Path, templates_dir: Path, temp_out_dir: Path):
    """
    Given a masterfile with data from school RRS2030250, filtered to that school
    When the template for the school is populated using that data
    Then a file should be written with the tables filled in and a file should exist in the output path
    """
    nested_data = parse_masterfile(data_path / "example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    school_data = school_filter(testing_df, "RRS2030220")
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(school_data, templates_dir / "2021/2021-22_template.docx", "RRS2030220", 2022, output_doc)

    assert populated_template.verify_tables_filled()
    assert output_doc.exists()


def test_school_name_replaced_in_paragraphs(data_path: Path, templates_dir: Path, temp_out_dir: Path):
    """
    Given a school template with the first non-blank paragraph having a "School A" placeholder
    When the template is populated with redcap data
    Then School A should be replaced by the name of the school
    """
    nested_data = parse_masterfile(data_path / "example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    school_data = school_filter(testing_df, "RRS2030250")
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(school_data, templates_dir / "2021/2021-22_template.docx", "RRS2030250", 2022, output_doc)

    output_paragraphs = []
    for paragraph in populated_template.doc.paragraphs:
        if paragraph.text.strip() != "":
            output_paragraphs.append(paragraph.text)

    assert "School A" not in output_paragraphs[0]


def test_school_table_filters_applied(data_path: Path):
    """
    Given a school that has data that is not within the date range
    When the template is populated with redcap data
    Then this template should be filled with the following:
    Table 1, 2, 5: test_1_2021-22, test_3_2021-22, test_4_2021-22, test_5_2021-22, test_6_2021-22
    Table 3&4: test_1_2021-22, test_4_2021-22
    Table 6: No data
    """

    nested_data = parse_masterfile(data_path / "example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    test_pupils_school_data = school_filter(testing_df, "RRS2030220")

    test_filter_for_one_two_five = filter_for_one_two_five(test_pupils_school_data, 2022)

    test_filter_for_three_four = filter_for_three_four(test_pupils_school_data, 2022)

    test_filter_six = filter_six(test_pupils_school_data, 2022)

    # first filter test
    assert (~test_pupils_school_data["reg_rr_title"].isin(["Teacher Leader", "Teacher Leader Only", "Teacher Leader + Support Role"])).any()
    assert (test_pupils_school_data["entry_date"] < "2022-8-1").all()
    assert ((test_pupils_school_data["exit_date"].isna()) | (test_pupils_school_data["exit_date"] > "2021-7-31")).all()

    # testing filter for table 3,4 applied
    assert (~test_filter_for_three_four["pupil_no"].isin(["test_2_2021-22", "test_3_2021-22", "test_5_2021-22", "test_6_2021-22"])).any()
    assert (~test_filter_for_three_four["exit_outcome"].isin(["Incomplete", "Ongoing"])).any()

    # test_1_2021-22, Discontinued and within date boundary, no month3 or month 6 results. Should show in 1,2,3,4,5.
    test_1 = test_filter_for_one_two_five.loc[test_filter_for_one_two_five.pupil_no == "test_1_2021-22"]
    assert (test_1["exit_outcome"] == "Discontinued").all()
    assert ((test_1["entry_date"] < "2022-8-1") & (test_1["exit_date"] < "2022-8-1")).all()

    # test_2_2021-22, Discontinued, not within date boundary, month3 testdate out of range, no month6. Should not be in any tables.
    assert (~test_filter_for_one_two_five["pupil_no"] == "test_2_2021-22").all()
    assert (~test_filter_for_three_four["pupil_no"] == "test_2_2021-22").all()
    # month3 testdate out of boundary
    assert (~test_filter_six["pupil_no"] == "test_2_2021-22").all()

    # test_3_2021-22, Discontinued, entry date IN report date but exit date OUT of report date, no month3 or month 6 results. Should be in 1,2,5.
    assert (test_filter_for_one_two_five["pupil_no"] == "test_3_2021-22").all()
    assert (~test_filter_for_three_four["pupil_no"] == "test_3_2021-22").all()

    # test_4_2021-22, Discontinued, entry date OUT of report date but exit date IN report date, month3 testdate in range. Should be in all tables.
    assert (test_filter_for_one_two_five["pupil_no"] == "test_4_2021-22").all()
    assert (test_filter_for_three_four["pupil_no"] == "test_4_2021-22").all()
    # month3 testdate within boundary
    assert (test_filter_six["pupil_no"] == "test_4_2021-22").all()

    # test_5_2021-22, Incomplete and within date boundary. Should be in 1,2,5.
    assert (test_filter_for_one_two_five["pupil_no"] == "test_5_2021-22").all()
    assert (~test_filter_for_three_four["pupil_no"] == "test_5_2021-22").all()

    # test_6_2021-22, Ongoing and entry date within boundary and NA exit date. Should be in 1,2,5.
    assert (test_filter_for_one_two_five["pupil_no"] == "test_6_2021-22").all()
    assert (~test_filter_for_three_four["pupil_no"] == "test_6_2021-22").all()
