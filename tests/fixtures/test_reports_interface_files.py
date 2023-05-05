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
