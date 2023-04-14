from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture()
def templates_dir(repo_root) -> Path:
    return repo_root / "input" / "templates"
