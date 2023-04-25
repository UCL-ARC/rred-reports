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
    """Class to handle MS exchange server authentication"""

    settings: Settings = get_settings()

    def get_credentials(self) -> OAuth2LegacyCredentials:
        """Builds a user credential object for exchangelib

        Returns:
            OAuth2LegacyCredentials: Credentials to authenticate a user
        """
        return OAuth2LegacyCredentials(
            client_id=self.settings.client_id,
            client_secret=self.settings.client_secret,
            tenant_id=self.settings.tenant_id,
            username=f"{self.settings.username}@ucl.ac.uk",
            password=self.settings.password,
        )

    def get_config(self) -> Configuration:
        """Retrieve an exchangelib Configuration object

        Ultimately used to return an exchangelib Account object
        used to send emails

        Returns:
            Configuration: _description_
        """
        return Configuration(server=self.settings.server, credentials=self.get_credentials())

    def get_account(self) -> Account:
        """Return an exchangelib Account object

        Account object necessary for sending emails using OAuth2

        Returns:
            Account: exchangelib Account object for an authenticated user
        """
        return Account(primary_smtp_address=f"{self.settings.send_emails_as}", config=self.get_config(), access_type=DELEGATE)
