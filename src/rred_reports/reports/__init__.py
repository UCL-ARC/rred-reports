"""Filling report templates tables with RRED data"""
from dataclasses import dataclass


@dataclass
class ReportSettings:
    sender: str
    recipients: str | list[str]
    smtp_host: str
    smtp_port: int
