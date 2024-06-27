"""Mail server authentication"""
import logging
from dataclasses import dataclass
from pathlib import Path
from urllib import parse

import click
import msal
from dynaconf.base import Settings
from exchangelib import (
    DELEGATE,
    Account,
    Configuration,
    OAuth2AuthorizationCodeCredentials,
)
from oauthlib.oauth2 import OAuth2Token

from rred_reports.reports import get_settings

LOG_FORMAT = "%(levelname)-10s %(asctime)s %(name)-30s %(funcName)-35s %(lineno)-5d: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

CACHE_PATH = Path("my_cache.bin")


@dataclass
class RREDAuthenticator:
    """Class to handle MS Exchange server authentication"""

    settings: Settings = get_settings()

    def _get_app_access_token(self) -> dict:
        """Acquire an access token for the Azure app"""
        authority = f"https://login.microsoftonline.com/{self.settings.tenant_id}"
        global_token_cache = _check_or_set_up_cache()
        app = msal.ClientApplication(
            self.settings.client_id,
            authority=authority,
            token_cache=global_token_cache,
        )

        accounts = app.get_accounts(username=self.settings.username)

        if accounts:
            logger.info("Account(s) exists in cache, probably with token too. Let's try.")
            result = app.acquire_token_silent([self.settings.scope], account=accounts[0])
        else:
            logger.info("No suitable token exists in cache. Let's initiate interactive login.")
            auth_code_flow = app.initiate_auth_code_flow(scopes=[self.settings.scope], login_hint=self.settings.username)
            final_url = click.confirm(
                f"Please follow auth flow by going to this link, then enter in the final redirect URL {auth_code_flow['auth_uri']}\n"
            )
            final_url = (Path(__file__).parents[3] / "access_link.txt").read_text()
            auth_response = self._convert_url_to_auth_dict(final_url)
            result = app.acquire_token_by_auth_code_flow(auth_code_flow, auth_response)

        if "access_token" not in result:
            message = "Access token could not be acquired"
            raise RuntimeError(message, result["error_description"])

        # Save cache if it changed after authentication setup
        _save_cache(global_token_cache, CACHE_PATH)

        return result

    @staticmethod
    def _convert_url_to_auth_dict(auth_url: str) -> dict:
        query_string = parse.urlsplit(auth_url).query
        query_data = parse.parse_qs(query_string)
        # state needs to be a string to match the auth_code_flow
        query_data["state"] = query_data["state"][0]
        return query_data

    def get_credentials(self) -> OAuth2AuthorizationCodeCredentials:
        """Builds a user credential object for exchangelib

        Returns:
            OAuth2AuthorizationCodeCredentials: Credentials to authenticate a user
        """
        token_result = self._get_app_access_token()
        access_token = OAuth2Token(token_result)
        return OAuth2AuthorizationCodeCredentials(access_token=access_token)

    def get_config(self) -> Configuration:
        """Retrieve an exchangelib Configuration object

        Ultimately used to return an exchangelib Account object
        used to send emails

        Returns:
            Configuration: Configuration object for Exchange server
        """
        return Configuration(server=self.settings.server, credentials=self.get_credentials())

    def get_account(self) -> Account:
        """Return an exchangelib Account object

        Account object necessary for sending emails using OAuth2

        Returns:
            Account: exchangelib Account object for an authenticated user
        """
        conf = self.get_config()
        return Account(primary_smtp_address=self.settings.send_emails_as, config=conf, access_type=DELEGATE)


def _check_or_set_up_cache():
    """Set up MSAL token cache and load existing token"""
    cache = msal.SerializableTokenCache()

    if CACHE_PATH.exists():
        with CACHE_PATH.open("rb") as cache_file:
            cache.deserialize(cache_file.read())

    return cache


def _save_cache(cache: msal.SerializableTokenCache, cache_path: Path) -> None:
    if cache.has_state_changed:
        with cache_path.open("w") as cache_file:
            cache_file.write(cache.serialize())
