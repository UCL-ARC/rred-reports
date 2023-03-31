"""Filling report templates tables with RRED data"""
from dataclasses import dataclass

from dynaconf import Dynaconf
from dynaconf.base import Settings


@dataclass
class ReportEmailConfig:
    """Basic configuration for sending reports as email"""

    sender: str
    recipients: str
    smtp_host: str
    smtp_port: int


def get_settings() -> Settings:
    """Retrieve Dynaconf settings
    Looks at environment variables, settings.toml,
    and finally .secrets.toml

    Environment variables should be prefixed with
    the envvar_prefix variable set in config.py

    Returns:
        Settings: Dynaconf settings
    """
    return Dynaconf()
