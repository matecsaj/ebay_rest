# Standard library imports
import base64
from datetime import datetime, timezone, timedelta
import json
import logging
import requests
import time
import threading
from urllib.parse import parse_qs, urlencode

# Local imports
from .date_time import DateTime
from .error import Error
from .reference import Reference


class _OAuthToken(object):

    def __init__(self, error=None, access_token=None, refresh_token=None, refresh_token_expiry=None, token_expiry=None):
        """
            token_expiry: datetime in UTC
            refresh_token_expiry: datetime in UTC
        """
        self.access_token = access_token
        self.token_expiry = token_expiry
        self.refresh_token = refresh_token
        self.refresh_token_expiry = refresh_token_expiry
        self.error = error

    def __str__(self):
        token_str = '{'
        if self.error is not None:
            token_str += '"error": "' + self.error + '"'
        elif self.access_token is not None:
            token_str += '"access_token": "' \
                         + self.access_token \
                         + '", "expires_in": "' \
                         + self.token_expiry.strftime('%Y-%m-%dT%H:%M:%S:%f') \
                         + '"'
            if self.refresh_token is not None:
                token_str += ', "refresh_token": "' \
                             + self.refresh_token \
                             + '", "refresh_token_expire_in": "' \
                             + self.refresh_token_expiry.strftime('%Y-%m-%dT%H:%M:%S:%f') \
                             + '"'
        token_str += '}'
        return token_str


class _OAuth2Api:
    def __init__(self, sandbox, client_id, client_secret, ru_name):
        """Initialize OAuth2Api instance

        :param sandbox (bool, required):
        :param client_id (str, required):
        :param client_secret (str, required):
        :param ru_name (str, required):
        """
        self._sandbox = sandbox

        # application/client
        self._client_id = client_id
        self._client_secret = client_secret
        self._ru_name = ru_name

    def generate_user_authorization_url(self, scopes, state=None):
        """
            scopes = list of strings
        """
        scopes = ' '.join(scopes)
        param = {
            'client_id': self._client_id,
            'redirect_uri': self._ru_name,
            'response_type': 'code',
            'prompt': 'login',
            'scope': scopes
        }

        if state is not None:
            param.update({'state': state})

        query = urlencode(param)
        if self._sandbox:
            web_endpoint = "https://auth.sandbox.ebay.com/oauth2/authorize"
        else:
            web_endpoint = "https://auth.ebay.com/oauth2/authorize"
        return web_endpoint + '?' + query

    def get_application_token(self, scopes):
        """
            makes call for application token and stores result in credential object
            returns credential object
        """

        logging.debug("Trying to get a new application access token ... ")
        headers = self._generate_request_headers()
        body = self._generate_application_request_body(' '.join(scopes))
        api_endpoint = self._get_endpoint()
        resp = requests.post(api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = _OAuthToken()

        return self._finish(resp, token, content)

    def exchange_code_for_access_token(self, code):
        logging.debug("Trying to get a new user access token ... ")

        headers = self._generate_request_headers()
        body = self._generate_oauth_request_body(code)
        api_endpoint = self._get_endpoint()
        resp = requests.post(api_endpoint, data=body, headers=headers)

        content = json.loads(resp.content)
        token = _OAuthToken()

        if resp.status_code == requests.codes.ok:
            token.refresh_token = content['refresh_token']
            token.refresh_token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content['refresh_token_expires_in']))
                - timedelta(minutes=5)
            )

        return self._finish(resp, token, content)

    def get_access_token(self, refresh_token, scopes):
        """
        refresh token call
        """

        logging.debug("Trying to get a new user access token ... ")

        headers = self._generate_request_headers()
        body = self._generate_refresh_request_body(scopes, refresh_token)
        api_endpoint = self._get_endpoint()
        resp = requests.post(api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = _OAuthToken()
        token.token_response = content

        return self._finish(resp, token, content)

    def _get_endpoint(self):
        if self._sandbox:
            return "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            return "https://api.ebay.com/identity/v1/oauth2/token"

    def _generate_request_headers(self):

        b64_encoded_credential = base64.b64encode((self._client_id + ':'
                                                   + self._client_secret).encode())
        headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + b64_encoded_credential.decode()
        }

        return headers

    def _generate_application_request_body(self, scopes):

        body = {
                'grant_type': 'client_credentials',
                'redirect_uri': self._ru_name,
                'scope': scopes
        }

        return body

    @staticmethod
    def _generate_refresh_request_body(scopes, refresh_token):
        if refresh_token is None:
            raise Error(number=1, reason="credential object does not contain refresh_token and/or scopes")

        body = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'scope': scopes
        }
        return body

    def _generate_oauth_request_body(self, code):
        body = {
                'grant_type': 'authorization_code',
                'redirect_uri': self._ru_name,
                'code': code
        }
        return body

    @staticmethod
    def _finish(resp, token, content):

        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content['expires_in']))
                - timedelta(minutes=5)
            )
        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']

        return token


class Token:
    """
    Initialize, refresh and supply an eBay OAuth application token.

    This is a facade for the oath module.
    """

    def __init__(self, sandbox,
                 client_id=None, client_secret=None, dev_id=None, ru_name=None,
                 user_id=None, user_password=None, application_scopes=None, user_scopes=None,
                 user_refresh_token=None, user_refresh_token_expiry=None):
        """
        :param sandbox (bool, required): The system to use, True for Sandbox/Testing and False for Production.

        # application/client credentials, optional if you don't make API calls that need an application/client token
        :param client_id (str, optional):
        :param dev_id (str, optional):
        :param client_secret (str, optional):
        :param ru_name (str, optional):
        :param application_scopes (str, optional):

        # user credentials, optional if you don't make API calls that need an user token
        :param user_id (str, optional):
        :param user_password (str, optional):
        :param user_scopes (str, optional):

        # user token supply, optional if don't mind a Chrome browser opening when getting a user token
        :param user_refresh_token (str, optional):
        :param user_refresh_token_expiry (str, optional):
        """

        self._lock = threading.Lock()
        with self._lock:
            self._sandbox = sandbox

            # application/client credentials
            self._client_id = client_id
            self._dev_id = dev_id
            self._client_secret = client_secret
            self._ru_name = ru_name
            self._application_scopes = application_scopes

            # user credentials
            self._user_id = user_id
            self._user_password = user_password
            self._user_scopes = user_scopes

            # token object storage
            self._application_token = None
            self._user_token = None

            # instantiate low-level oauth api utilities
            self._oauth2api_inst = _OAuth2Api(self._sandbox, self._client_id, self._client_secret, self._ru_name)

            # possible user token with expiry
            self._user_refresh_token = user_refresh_token
            self._user_refresh_token_expiry = None
            self._allow_get_user_consent = True
            if user_refresh_token is not None:
                if user_refresh_token_expiry is not None:
                    self._allow_get_user_consent = False
                    self._user_refresh_token_expiry = DateTime.from_string(user_refresh_token_expiry)
                    try:
                        self._user_refresh_token = _OAuthToken(
                            refresh_token=self._user_refresh_token,
                            refresh_token_expiry=self._user_refresh_token_expiry
                        )
                    except Error:
                        raise
                else:
                    raise Error(number=1, reason='Must supply refresh token expiry with refresh token!')

    def get_application(self):
        """ Get an eBay Application Token. """
        with self._lock:
            if self._application_scopes is None:
                self._determine_application_scopes()

            if self._application_token is None:
                self._refresh_application()
            elif self._application_token.token_expiry.replace(tzinfo=timezone.utc) <= DateTime.now():
                self._refresh_application()

            token = self._application_token.access_token

        return token

    def _determine_application_scopes(self):
        """ Determine the application scopes that are currently allowed. """
        if self._sandbox:
            # permission is always granted for all
            scopes = list(Reference.get_application_scopes().keys())
        else:
            scopes = []
            for scope in Reference.get_application_scopes():
                token_application = self._oauth2api_inst.get_application_token([scope])
                if token_application.error is None:
                    if token_application.access_token is not None:
                        if len(token_application.access_token) > 0:
                            scopes.append(scope)

        self._application_scopes = scopes

    def _refresh_application(self):
        """ Refresh the eBay Application Token and update all that comes with it."""
        token_application = self._oauth2api_inst.get_application_token(self._application_scopes)
        if token_application.error is not None:
            reason = 'token_application.error ' + token_application.error
            raise Error(number=1, reason=reason)
        if (token_application.access_token is None) or (len(token_application.access_token) == 0):
            raise Error(number=1, reason='token_application.access_token is missing.')

        self._application_token = token_application

    def get_user(self):
        """ Get an eBay User Access Token. """
        with self._lock:
            if self._user_scopes is None:
                self._determine_user_scopes()

            if self._user_token is None:
                self._refresh_user()
            elif self._user_token.token_expiry.replace(tzinfo=timezone.utc) <= DateTime.now():
                self._refresh_user()

            token = self._user_token.access_token
        return token

    def _determine_user_scopes(self):
        """ Determine the user access scopes that are currently allowed. """
        if self._sandbox:
            # permission is always granted for all
            scopes = list(Reference.get_user_scopes().keys())
        else:
            # these are always granted, many more are possible
            scopes = ["https://api.ebay.com/oauth/api_scope",
                      "https://api.ebay.com/oauth/api_scope/sell.inventory",
                      "https://api.ebay.com/oauth/api_scope/sell.marketing",
                      "https://api.ebay.com/oauth/api_scope/sell.account",
                      "https://api.ebay.com/oauth/api_scope/sell.fulfillment"]
        self._user_scopes = scopes

    def _refresh_user(self):
        """
        Refresh the eBay User Access Token and update all that comes with it.
        If we don't have a current refresh token, run the authorization flow.
        """
        if self._user_refresh_token is None:
            # We don't have a refresh token; run authorization flow
            self._authorization_flow()

        elif self._user_refresh_token.refresh_token_expiry <= DateTime.now():
            # The refresh token has expired; run authorization flow
            self._authorization_flow()

        else:
            # Exchange our still current refresh token for a new user access token
            self._refresh_user_token()

    def _authorization_flow(self):
        """
        Get an authorization code by running the authorization_flow, and
        then exchange that for a refresh token (which also contains a
        user token).
        """
        if not self._allow_get_user_consent:
            raise Error(number=1, reason='Getting user consent via browser disabled')

        sign_in_url = self._oauth2api_inst.generate_user_authorization_url(self._user_scopes)
        if sign_in_url is None:
            raise Error(number=1, reason='sign_in_url is None.')

        code = self._get_authorization_code(sign_in_url)

        refresh_token = self._oauth2api_inst.exchange_code_for_access_token(code)

        if refresh_token.access_token is None:
            raise Error(number=1, reason='refresh_token.access_token is None.')
        if len(refresh_token.access_token) == 0:
            raise Error(number=1, reason='refresh_token.access_token is of length zero.')

        # Split token into refresh token and user token parts
        self._user_refresh_token = _OAuthToken(
            refresh_token=refresh_token.refresh_token,
            refresh_token_expiry=refresh_token.refresh_token_expiry)
        self._user_token = _OAuthToken(
            access_token=refresh_token.access_token,
            token_expiry=refresh_token.token_expiry)

    def _get_authorization_code(self, sign_in_url: str):
        """Run the authorization flow in order to get an authorization code,
        which can subsequently be exchanged for a refresh (and user) token.

        :param
        sign_in_url (str): The redirect URL for gaining user consent
        """

        delay = 5  # delay seconds to give the page an opportunity to render

        # Don't move the import to the top of the file because not everyone uses this method.
        # In README.md note the extra installation steps.
        from selenium import webdriver

        # open browser and load the initial page
        browser = webdriver.Chrome()
        browser.get(sign_in_url)
        time.sleep(delay)

        # fill in the username then click continue
        form_userid = browser.find_element_by_name('userid')
        form_userid.send_keys(self._user_id)
        browser.find_element_by_id('signin-continue-btn').click()
        time.sleep(delay)

        # fill in the password then submit
        form_pw = browser.find_element_by_name('pass')
        form_pw.send_keys(self._user_password)
        browser.find_element_by_id('sgnBt').submit()
        time.sleep(delay)

        # get the result url and then close browser
        qs = browser.current_url.partition('?')[2]
        parsed = parse_qs(qs, encoding='utf-8')
        browser.quit()

        # Assume authorization was successful if isAuthSuccessful missing
        # Check isAuthSuccessful is true, if present
        if 'isAuthSuccessful' not in parsed:
            is_auth_successful = True
        else:
            if 'true' == parsed['isAuthSuccessful'][0]:
                is_auth_successful = True
            else:
                is_auth_successful = False
        if not is_auth_successful:
            reason = (
                f"Authorization unsuccessful, check userid & password:"
                f" {self._user_id} {self._user_password}"
            )
            raise Error(number=1, reason=reason)

        # Check we have the code in the browser URL
        if 'code' in parsed:
            return parsed['code']
        else:
            raise Error(number=1, reason="Unable to obtain code.")

    def _refresh_user_token(self):
        """Exchange a refresh token for a current user token."""

        user_token = self._oauth2api_inst.get_access_token(self._user_refresh_token.refresh_token,
                                                           self._user_scopes)

        if user_token.access_token is None:
            raise Error(number=1, reason='user_token.access_token is None.')
        if len(user_token.access_token) == 0:
            raise Error(number=1, reason='user_token.access_token is of length zero.')

        self._user_token = user_token
