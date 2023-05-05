from pathlib import Path

from rred_reports.masterfile import join_masterfile_dfs, parse_masterfile
from rred_reports.reports.schools import populate_school_data, school_filter


def test_school_tables_filled(data_path: Path, templates_dir: Path, temp_out_dir: Path):
    """
    Given a masterfile with data from school RRS2030250, filtered to that school
    When the template for the school is populated using that data
    Then a file should be written with the tables filled in and a file should exist in the output path
    """
    nested_data = parse_masterfile(data_path / "example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    school_data = school_filter(testing_df, "RRS2030250")
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(school_data, templates_dir / "2021/2021-22_template.docx", "RRS2030250", 2022, output_doc)

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

    assert (~test_pupils_school_data["reg_rr_title"].isin(["Teacher Leader", "Teacher Leader Only", "Teacher Leader + Support Role"])).any()
    assert (test_pupils_school_data["entry_date"] < "2022-8-1").all()
    assert ((test_pupils_school_data["exit_date"].isna()) | (test_pupils_school_data["exit_date"] > "2021-7-31")).all()

