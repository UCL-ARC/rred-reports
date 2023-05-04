from typer.testing import CliRunner

from rred_reports import __version__
from rred_reports.cli import app

runner = CliRunner()


def test_return_version():
    result = runner.invoke(app, "--version")
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_get_top_level_commands():
    result = runner.invoke(app, "--help")
    assert result.exit_code == 0
    assert "redcap" in result.stdout
    assert "Run the redcap extraction pipeline" in result.stdout
    assert "reports" in result.stdout
    assert "Run the report generation pipeline" in result.stdout


def test_reports_subcommands():
    result = runner.invoke(app, ["reports", "--help"])
    assert result.exit_code == 0
    assert "create" in result.stdout
    assert "Generate a report at the level specified" in result.stdout


def test_reports_create_subcommand_args():
    result = runner.invoke(app, ["reports", "create", "--help"])
    assert result.exit_code == 0
    assert "level" in result.stdout
    assert "LEVEL:{school|centre|national|all}" in result.stdout
    assert "year" in result.stdout


def test_reports_create_subcommand_failure_on_incorrect_level():
    result = runner.invoke(app, ["reports", "create", "beep"])
    assert result.exit_code == 2
    assert "Invalid value for 'LEVEL:{school|centre|national|all}'" in result.stdout
