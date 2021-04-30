# Standard library imports
from datetime import timezone
import logging
import os
import threading

# Local imports
from .date_time import DateTime
from .oath.credentialutil import CredentialUtil
from .oath.model.model import Environment
from .oath.oauth2api import OAuth2Api


class Token:
    """ Initialize, refresh and supply an eBay OAuth application token.

    This is a facade for the oath library.
    """

    def __init__(self, use_sandbox: bool):
        self._token_lock = threading.Lock()
        self._app_token = None  # use when locked

        directory = os.getcwd()  # get the current working directory
        CredentialUtil.load(os.path.join(directory, 'ebay_rest.json'))
        self._oauth2api_inst = OAuth2Api()
        if use_sandbox:
            self._env = Environment.SANDBOX
        else:
            self._env = Environment.PRODUCTION

        self._refresh()

    def get(self):
        """ Get the eBay Application Token. """

        with self._token_lock:
            if self._app_token.token_expiry.replace(tzinfo=timezone.utc) <= DateTime.now():
                self._refresh()
            token = self._app_token.access_token

        return token

    def _refresh(self):
        """ Refresh the eBay Application Token and update all that comes with it. """

        app_token = \
            self._oauth2api_inst.get_application_token(self._env,
                                                       ["https://api.ebay.com/oauth/api_scope"])
        if app_token.error is not None:
            logging.critical(f'app_token.error == {app_token.error}.')
        if (app_token.access_token is None) or (len(app_token.access_token) == 0):
            logging.critical('app_token.access_token is missing.')

        self._app_token = app_token
