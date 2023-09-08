from loguru_caplog import loguru_caplog  # noqa: F401

pytest_plugins = [
    "tests.fixtures.test_template_files",
    "tests.fixtures.test_redcap_files",
    "tests.fixtures.test_emails",
    "tests.fixtures.test_reports_interface_files",
]
