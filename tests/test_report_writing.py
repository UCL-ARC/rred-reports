from rred_reports.masterfile import join_masterfile_dfs, parse_masterfile
from rred_reports.reports.schools import populate_school_data, school_filter


def test_school_tables_filled(data_path, templates_dir, temp_out_dir):
    """
    Given a masterfile with data from school RRS2030250, filtered to that school
    When the template for the school is populated using that data
    Then a file should be written with the tables filled in and a file should exist in the output path
    """
    nested_data = parse_masterfile(data_path / "example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    school_data = school_filter(testing_df, "RRS2030250")
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(school_data, templates_dir / "2021/2021-22_template.docx", "RRS2030250", output_doc)

    assert populated_template.verify_tables_filled()
    assert output_doc.exists()


def test_school_name_replaced_in_paragraphs(data_path, templates_dir, temp_out_dir):
    """
    Given a school template with the first non-blank paragraph having a "School A" placeholder
    When the template is populated with redcap data
    Then School A should be replaced by the name of the school
    """
    nested_data = parse_masterfile(data_path / "example_masterfile.xlsx")
    testing_df = join_masterfile_dfs(nested_data)
    school_data = school_filter(testing_df, "RRS2030250")
    output_doc = temp_out_dir / "school.docx"

    populated_template = populate_school_data(school_data, templates_dir / "2021/2021-22_template.docx", "RRS2030250", output_doc)

    output_paragraphs = []
    for paragraph in populated_template.doc.paragraphs:
        if paragraph.text.strip() != "":
            output_paragraphs.append(paragraph.text)

    assert "School A" not in output_paragraphs[0]