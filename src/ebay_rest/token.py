# Standard library imports
from datetime import timezone
import os
import threading

# Local imports
from .date_time import DateTime
from .error import Error
from .oath.credentialutil import CredentialUtil
from .oath.model.model import Environment
from .oath.oauth2api import OAuth2Api


class Token:
    """ Initialize, refresh and supply an eBay OAuth application token.

    This is a facade for the oath module. Instantiation is not required.
    """
    _lock = threading.Lock()
    _oauth2api_inst = None
    _app_token = dict()

    @staticmethod
    def get(sandbox: bool):
        """
        Get an eBay Application Token.

        Object instantiation is not required and is discouraged.

        :param
        sandbox (bool): {True, False} For the sandbox True, for production False.
        """

        with Token._lock:
            if Token._oauth2api_inst is None:
                directory = os.getcwd()  # get the current working directory
                CredentialUtil.load(os.path.join(directory, 'ebay_rest.json'))
                Token._oauth2api_inst = OAuth2Api()

            if sandbox not in Token._app_token:
                try:
                    Token._refresh(sandbox)
                except Error:
                    raise

            if Token._app_token[sandbox].token_expiry.replace(tzinfo=timezone.utc) <= DateTime.now():
                try:
                    Token._refresh(sandbox)
                except Error:
                    raise

            token = Token._app_token[sandbox].access_token

        return token

    @staticmethod
    def _refresh(sandbox: bool):
        """
        Refresh the eBay Application Token and update all that comes with it.

        :param
        sandbox (bool): {True, False} For the sandbox True, for production False.
        """

        URL = "https://api.ebay.com/oauth/api_scope"
        if sandbox:
            env = Environment.SANDBOX
        else:
            env = Environment.PRODUCTION

        app_token = Token._oauth2api_inst.get_application_token(env, [URL])
        if app_token.error is not None:
            reason = 'app_token.error ' + app_token.error
            raise Error(number=1, reason=reason)
        if (app_token.access_token is None) or (len(app_token.access_token) == 0):
            raise Error(number=1, reason='app_token.access_token is missing.')

        Token._app_token[sandbox] = app_token
