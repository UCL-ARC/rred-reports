"""Filling report templates tables with RRED data"""

from dynaconf.base import Settings

from rred_reports.config import settings


def get_settings() -> Settings:
    """Retrieve Dynaconf settings
    Looks at environment variables, settings.toml,
    and finally .secrets.toml

    Environment variables should be prefixed with
    the envvar_prefix variable set in config.py

    Returns:
        settings (Settings): Dynaconf settings
    """
    return settings
