from pathlib import Path

import pytest
import tomli
import tomli_w


@pytest.fixture()
def temp_config_file(temp_out_dir: Path) -> Path:
    toml_str = """
    school = "/path/to/data/school"
    centre = "/path/to/data/centre"
    national = "/path/to/data/national"
    """

    test_toml = tomli.loads(toml_str)
    with (temp_out_dir / "test_config.toml").open(mode="w") as outfile:
        outfile.write(tomli_w.dumps(test_toml))
    return temp_out_dir / "test_config.toml"


@pytest.fixture()
def temp_data_directories(tmp_path_factory: pytest.TempPathFactory) -> Path:
    top_level_dir = tmp_path_factory.mktemp("temp_top_level_dir")
    output_dir = top_level_dir / "output"
    output_dir.mkdir()
    processed_dir = output_dir / "processed"
    processed_dir.mkdir()
    year_dir = processed_dir / "2099"
    year_dir.mkdir()

    return {"top_level": top_level_dir, "output": output_dir, "processed": processed_dir, "year": year_dir}
