from rred_reports.masterfile import join_masterfile_dfs, parse_masterfile, read_and_process_masterfile


def test_masterfile_read(data_path):
    """
    Given that a masterfile exists with 35 pupils, 10 teachers across 10 schools
    When the masterfile is parsed and then joined
    The nested data should give the expected number of pupils, teachers and schools
    """
    file_path = data_path / "example_masterfile.xlsx"
    nested_data = parse_masterfile(file_path)

    joined_data = join_masterfile_dfs(nested_data)

    assert nested_data["pupils"].shape == (40, 65)
    assert nested_data["teachers"].shape == (11, 3)
    assert nested_data["schools"].shape == (10, 4)
    assert joined_data.shape == (40, 69)  # should be the same number of students as in the pupils df


def test_masterfile_warns_duplicate_school(data_path, loguru_caplog):
    """
    Given a masterfile with two pupils in the same school, but the region is different for each pupil
    When the masterfile is parsed
    The nested data should have two schools, and there should be a loguru message about the duplicate ID
    """
    file_path = data_path / "masterfile_with_school_in_two_regions.xlsx"
    nested_data = parse_masterfile(file_path)
    # two schools, even though same id
    assert nested_data["schools"].shape[0] == 2
    assert "The following School IDs had duplicate information" in loguru_caplog.text


def test_masterfile_no_duplicate_school(data_path, caplog):
    """
    Given a masterfile with no duplicate school details
    When the masterfile is parsed
    There should be no logging about duplicate school IDs
    """
    file_path = data_path / "example_masterfile.xlsx"
    parse_masterfile(file_path)
    assert "The following School IDs had duplicate information" not in caplog.text


def test_masterfile_teacher_moved(data_path):
    """
    Given a masterfile with one teacher who has moved schools, with a single pupil in each school
    When the masterfile is parsed
    The two pupils should remain in their correct school®
    """
    file_path = data_path / "masterfile_teacher_moved_school.xlsx"
    masterfile = read_and_process_masterfile(file_path)
    assert masterfile.shape[0] == 2
    assert all(masterfile.loc[masterfile.pupil_no == "1_2021-22"].get("rrcp_school").values == ["A School"])
    assert all(masterfile.loc[masterfile.pupil_no == "1_2022-23"].get("rrcp_school").values == ["B School"])
