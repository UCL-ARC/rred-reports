from rred_reports.masterfile import join_masterfile_dfs, parse_masterfile


def test_masterfile_read(data_path):
    """
    Given that a masterfile exists with 35 pupils, 10 teachers across 10 schools
    When the masterfile is parsed and then joined
    The nested data should give the expected number of pupils, teachers and schools
    """
    file_path = data_path / "example_masterfile.xlsx"
    nested_data = parse_masterfile(file_path)

    joined_data = join_masterfile_dfs(nested_data)

    assert nested_data["pupils"].shape == (35, 64)
    assert nested_data["teachers"].shape == (10, 3)
    assert nested_data["schools"].shape == (10, 4)
    assert joined_data.shape == (35, 69)  # should be the same number of students as in the pupils df
