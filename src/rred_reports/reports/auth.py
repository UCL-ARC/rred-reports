"""Mail server authentication"""
from dataclasses import dataclass

from dynaconf.base import Settings
from exchangelib import (
    DELEGATE,
    Account,
    Configuration,
    OAuth2LegacyCredentials,
)

from rred_reports.reports import get_settings


@dataclass
class RREDAuthenticator:
    settings: Settings = get_settings()

    def get_credentials(self) -> OAuth2LegacyCredentials:
        return OAuth2LegacyCredentials(
            client_id=self.settings.client_id,
            client_secret=self.settings.client_secret,
            tenant_id=self.settings.tenant_id,
            username=f"{self.settings.username}@ucl.ac.uk",
            password=self.settings.auth_pass,
        )

    def get_config(self) -> Configuration:
        return Configuration(server=self.settings.server, credentials=self.get_credentials())

    def get_account(self) -> Account:
        return Account(primary_smtp_address=f"{self.settings.send_emails_as}", config=self.get_config(), access_type=DELEGATE)
