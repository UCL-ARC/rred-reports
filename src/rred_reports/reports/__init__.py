"""Filling report templates tables with RRED data"""
from dataclasses import dataclass


@dataclass
class ReportEmailConfig:
    """Basic configuration for sending reports as email"""

    sender: str
    recipients: str
    smtp_host: str
    smtp_port: int
