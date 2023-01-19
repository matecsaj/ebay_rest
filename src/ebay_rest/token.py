# Standard library imports
from base64 import b64encode, b64decode
from datetime import datetime, timedelta, timezone
from json import loads
import logging
from threading import Lock
from time import sleep
from typing import List
from urllib.parse import parse_qs, urlencode
from cryptography.hazmat.primitives.serialization import load_der_private_key

# 3rd party library imports
from requests import codes, post, Response

# Local imports
from .api.developer_key_management import CreateSigningKeyRequest
from .date_time import DateTime
from .error import Error
from .multiton import Multiton
from .reference import Reference


class ApplicationToken(metaclass=Multiton):
    """
    Initialize, refresh and supply an eBay OAuth ***application*** token.

    This is a facade for the oath module.
    """

    __slots__ = "_lock", "_sandbox", "_application_scopes", "_application_token", "_oauth2api_inst"

    def __init__(self,
                 sandbox: bool,
                 client_id: str or None = None,
                 client_secret: str or None = None,
                 ru_name: str or None = None,
                 application_scopes: List[str] or None = None) -> None:
        """
        :param sandbox (bool, required): The system to use, True for Sandbox/Testing and False for Production.

        # application/client credentials are optional if you don't make API calls that need an application/client token
        :param client_id (str, optional):
        :param client_secret (str, optional):
        :param ru_name (str, optional):
        :param application_scopes (list, optional):
        :return: None (None)
        """
        self._lock = Lock()
        # The Multiton decorator wraps this initializer with a thread lock; it is safe to skip using self._lock.

        self._sandbox = sandbox

        # application/client credentials
        self._application_scopes = application_scopes

        # token object storage
        self._application_token = None

        # instantiate low-level oauth api utilities
        self._oauth2api_inst = _OAuth2Api(sandbox, client_id, client_secret, ru_name)

    def get(self) -> str:
        """
        Get an eBay Application Token.

        :return: token (str)
        """
        with self._lock:
            if self._application_scopes is None:
                self._determine_application_scopes()

            if self._application_token is None:
                self._refresh_application()
            elif self._application_token.token_expiry.replace(tzinfo=timezone.utc) <= DateTime.now():
                self._refresh_application()

            token = self._application_token.access_token

        return token

    def _determine_application_scopes(self) -> None:
        """
        Determine the application scopes that are currently allowed.

        return: None (None)
        """
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

    def _refresh_application(self) -> None:
        """
        Refresh the eBay Application Token and update all that comes with it.

        :return None (None)
        """
        token_application = self._oauth2api_inst.get_application_token(self._application_scopes)
        if token_application.error is not None:
            reason = 'token_application.error ' + token_application.error
            raise Error(number=96001, reason=reason)
        if (token_application.access_token is None) or (len(token_application.access_token) == 0):
            raise Error(number=96002, reason='token_application.access_token is missing.')

        self._application_token = token_application


class UserToken(metaclass=Multiton):
    """
    Initialize, refresh and supply an eBay OAuth ***user*** token.
    This is a facade for the oath module.
    """

    __slots__ = "_lock", "_sandbox", "_user_id", "_user_password", "_user_scopes", "_user_token", "_oauth2api_inst", \
        "_user_refresh_token", "_user_refresh_token_expiry", "_allow_get_user_consent"

    def __init__(self,
                 sandbox: bool,
                 client_id: str or None = None,
                 client_secret: str or None = None,
                 ru_name: str or None = None,
                 user_id: str or None = None,
                 user_password: str or None = None,
                 user_scopes: List[str] or None = None,
                 user_refresh_token: str or None = None,
                 user_refresh_token_expiry: str or None = None) -> None:
        """
        :param sandbox (bool, required): The system to use, True for Sandbox/Testing and False for Production.

        # application/client credentials, optional if you don't make API calls that need an application/client token
        :param client_id (str, optional):
        :param client_secret (str, optional):
        :param ru_name (str, optional):

        # user credentials, optional if you don't make API calls that need a user token
        :param user_id (str, optional):
        :param user_password (str, optional):
        :param user_scopes (str, optional):

        # user token supply, optional if you don't mind a Chrome browser opening when getting a user token
        :param user_refresh_token (str, optional):
        :param user_refresh_token_expiry (str, optional):

        :return None (None)
        """

        self._lock = Lock()
        # The Multiton decorator wraps this initializer with a thread lock; it is safe to skip using self._lock.

        self._sandbox = sandbox

        self._user_id = user_id
        self._user_password = user_password
        self._user_scopes = user_scopes

        # token object storage
        self._user_token = None

        # instantiate low-level oauth api utilities
        self._oauth2api_inst = _OAuth2Api(sandbox, client_id, client_secret, ru_name)

        # possible user token with expiry
        self._user_refresh_token = user_refresh_token
        self._user_refresh_token_expiry = None
        self._allow_get_user_consent = True
        if user_refresh_token is not None:
            if user_refresh_token_expiry is not None:
                self._allow_get_user_consent = False
                if self._user_scopes is None:
                    self._determine_user_scopes()
                try:
                    self._user_refresh_token_expiry = DateTime.from_string(user_refresh_token_expiry)
                except Error as error:
                    raise Error(number=96003, reason='user_refresh_token_expiry value error', detail=error.reason)
                try:
                    self._user_refresh_token = _OAuthToken(
                        refresh_token=self._user_refresh_token,
                        refresh_token_expiry=self._user_refresh_token_expiry
                    )
                except Error:
                    raise
            else:
                raise Error(number=96004, reason='Must supply refresh token expiry with refresh token!')

    def get(self) -> str:
        """ Get an eBay User Access Token.

        : return token (str)
        """
        with self._lock:
            if self._user_scopes is None:
                self._determine_user_scopes()

            if self._user_token is None:
                self._refresh_user()
            elif self._user_token.token_expiry.replace(tzinfo=timezone.utc) <= DateTime.now():
                self._refresh_user()

            token = self._user_token.access_token
        return token

    def _determine_user_scopes(self) -> None:
        """
        Determine the user access scopes that are currently allowed.
        :return None (None)
        """
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

    def _refresh_user(self) -> None:
        """
        Refresh the eBay User Access Token and update all that comes with it.
        If we don't have a current refresh token, run the authorization flow.

        :return None (None)
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

    def _authorization_flow(self) -> None:
        """
        Get an authorization code by running the authorization_flow, and
        then exchange that for a refresh token (which also contains a
        user token).

        :return None (None)
        """
        if not self._allow_get_user_consent:
            raise Error(number=96005, reason='Getting user consent via browser disabled')

        sign_in_url = self._oauth2api_inst.generate_user_authorization_url(self._user_scopes)
        if sign_in_url is None:
            raise Error(number=96006, reason='sign_in_url is None.')

        try:
            code = self._get_authorization_code(sign_in_url)
        except Error:
            raise

        refresh_token = self._oauth2api_inst.exchange_code_for_access_token(code)

        if refresh_token.access_token is None:
            raise Error(number=96007, reason='refresh_token.access_token is None.')
        if len(refresh_token.access_token) == 0:
            raise Error(number=96008, reason='refresh_token.access_token is of length zero.')

        # Split token into refresh token and user token parts
        self._user_refresh_token = _OAuthToken(
            refresh_token=refresh_token.refresh_token,
            refresh_token_expiry=refresh_token.refresh_token_expiry)
        self._user_token = _OAuthToken(
            access_token=refresh_token.access_token,
            token_expiry=refresh_token.token_expiry)

        # Give the user a helpful suggestion.
        try:
            expiry = DateTime.to_string(refresh_token.refresh_token_expiry)
        except Error:
            raise
        message = f'Edit to your ebay_rest.json file to avoid the browser pop-up.\n' \
                  f'For the user with an email or username of {self._user_id}.\n' \
                  f'"refresh_token": "{refresh_token.refresh_token}"\n' \
                  f'"refresh_token_expiry": "{expiry}"'
        logging.info(message)

    def _get_authorization_code(self, sign_in_url: str) -> str:
        """Run the authorization flow in order to get an authorization code,
        which can subsequently be exchanged for a refresh (and user) token.

        :param sign_in_url (str): The redirect URL for gaining user consent.
        :return code (str): Authorization code.
        """
        try:
            from selenium import webdriver
            from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
        except ModuleNotFoundError:
            reason = f"Supply an 'eBay user token' or install the COMPLETE variant of ebay_rest. Refer to the README.md at https://github.com/matecsaj/ebay_rest."  # noqa: E501
            logging.critical(reason)
            raise Error(number=96019, reason=reason)
        else:

            # open browser
            options = Options()
            # options.add_argument("--headless")      # TODO Put this back in after adding a captcha solver.
            try:
                browser = webdriver.Chrome(options=options)
            except WebDriverException as exc:
                raise Error(number=96014, reason="ChromeDriver instantiation failure.", detail=exc.msg)

            # load the initial page
            browser.get(sign_in_url)

            try:
                # fill in the username then click continue
                # sometimes a captcha appears, so wait an extra 30-seconds for the user to fill it in
                WebDriverWait(browser, 10 + 30).until(lambda x: x.find_element(By.NAME, 'userid')).send_keys(self._user_id)  # noqa: E501
                WebDriverWait(browser, 10).until(lambda x: x.find_element(By.ID, 'signin-continue-btn')).click()

                # fill in the password then submit
                sleep(5)  # Why? Perhaps an element I'm not aware of needs to finish rendering.
                WebDriverWait(browser, 10).until(lambda x: x.find_element(By.NAME, 'pass')).send_keys(self._user_password)  # noqa: E501
                WebDriverWait(browser, 10).until(lambda x: x.find_element(By.ID, 'sgnBt')).submit()

            except NoSuchElementException:
                raise Error(number=96015, reason="ChromeDriver element not found.",
                            detail="Has eBay's website changed?")
            except TimeoutException:
                raise Error(number=96016, reason="ChromeDriver timeout.", detail='Slow computer or Internet?')

            # in some countries an "I agree" prompt interjects
            try:
                element = WebDriverWait(browser, 10).until(lambda x: x.find_element(By.ID, 'submit'))
            except TimeoutException:
                pass
            else:
                element.click()

            # get the result url and then close browser
            # some people enable 2FA, so wait an extra 30-seconds for the user interaction
            try:
                WebDriverWait(browser, 10 + 30).until(lambda x: x.find_element(By.ID, 'thnk-wrap'))
            except NoSuchElementException:
                raise Error(number=96017, reason="ChromeDriver element not found.",
                            detail="Has eBay's website changed?")
            except TimeoutException:
                raise Error(number=96018, reason="ChromeDriver timeout.", detail='Slow computer or Internet?')
            qs = browser.current_url.partition('?')[2]
            parsed = parse_qs(qs, encoding='utf-8')
            browser.quit()

            # Check isAuthSuccessful is true, if present
            is_auth_successful = False
            if 'isAuthSuccessful' in parsed:
                if 'true' == parsed['isAuthSuccessful'][0]:
                    is_auth_successful = True

            if is_auth_successful:
                if 'code' in parsed:
                    return parsed['code'][0]  # recently added [0]
                else:
                    raise Error(number=96009, reason="Unable to obtain code.")
            else:
                reason = f"Authorization unsuccessful, check userid & password:{self._user_id} {self._user_password}"
                raise Error(number=96010, reason=reason)

    def _refresh_user_token(self) -> None:
        """
        Exchange a refresh token for a current user token.
        :return: None (None)
        """
        user_token = self._oauth2api_inst.get_access_token(self._user_refresh_token.refresh_token,
                                                           self._user_scopes)

        if user_token.access_token is None:
            raise Error(number=96011, reason=user_token.token_response['error_description'])
        if len(user_token.access_token) == 0:
            raise Error(number=96012, reason='user_token.access_token is of length zero.')

        self._user_token = user_token


class _OAuthToken(object):
    __slots__ = "access_token", "token_expiry", "refresh_token", "refresh_token_expiry", "error", "token_response"

    def __init__(self,
                 error: str or None = None,
                 access_token: str or None = None,
                 refresh_token: str or None = None,
                 refresh_token_expiry: datetime or None = None,
                 token_expiry: datetime or None = None):
        """
        :param error (str, optional):
        :param access_token (str, optional):
        :param refresh_token (str, optional):
        :param refresh_token_expiry (datetime, optional): datetime in UTC
        :param token_expiry (datetime, optional): datetime in UTC
        :return None (None)
        """
        self.access_token = access_token
        self.token_expiry = token_expiry
        self.refresh_token = refresh_token
        self.refresh_token_expiry = refresh_token_expiry
        self.error = error
        self.token_response = None

    def __str__(self) -> str:
        """
        :return token_str: (str)
        """
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
    __slots__ = "_sandbox", "_client_id", "_client_secret", "_ru_name"

    def __init__(self, sandbox: bool, client_id: str, client_secret: str, ru_name: str):
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

    def generate_user_authorization_url(self, scopes: List[str], state: str or None = None) -> str:
        """
        :param scopes (list(str)), required)
        :param state (str, optional)
        """
        param = {
            'client_id': self._client_id,
            'redirect_uri': self._ru_name,
            'response_type': 'code',
            'prompt': 'login',
            'scope': ' '.join(scopes)
        }

        if state is not None:
            param.update({'state': state})

        query = urlencode(param)
        if self._sandbox:
            web_endpoint = "https://auth.sandbox.ebay.com/oauth2/authorize"
        else:
            web_endpoint = "https://auth.ebay.com/oauth2/authorize"
        return web_endpoint + '?' + query

    def get_application_token(self, scopes: List[str]) -> _OAuthToken:
        """
        Makes call for application token and stores result in credential object.
        :param scopes (list(str)), required)
        :return credential_object (_OAuthToken)
        """
        logging.debug("Trying to get a new application access token ... ")
        headers = self._generate_request_headers()
        body = self._generate_application_request_body(scopes)
        api_endpoint = self._get_endpoint()
        resp = post(api_endpoint, data=body, headers=headers)
        content = loads(resp.content)
        token = _OAuthToken()

        return self._finish(resp, token, content)

    def exchange_code_for_access_token(self, code: str) -> _OAuthToken:
        """
        :param code (str, required)
        :return credential_object (_OAuthToken)
        """
        logging.debug("Trying to get a new user access token ... ")

        headers = self._generate_request_headers()
        body = self._generate_oauth_request_body(code)
        api_endpoint = self._get_endpoint()
        resp = post(api_endpoint, data=body, headers=headers)

        content = loads(resp.content)
        token = _OAuthToken()

        if resp.status_code == codes.ok:
            token.refresh_token = content['refresh_token']
            token.refresh_token_expiry = (
                    datetime.utcnow()
                    + timedelta(seconds=int(content['refresh_token_expires_in']))
                    - timedelta(minutes=5)
            )

        return self._finish(resp, token, content)

    def get_access_token(self, refresh_token: str, scopes: List[str]) -> _OAuthToken:
        """
        refresh token call
        :param refresh_token (str, required)
        :param scopes (list(str)), required)
        :return credential_object (_OAuthToken)
        """
        logging.debug("Trying to get a new user access token ... ")

        headers = self._generate_request_headers()
        body = self._generate_refresh_request_body(scopes, refresh_token)
        api_endpoint = self._get_endpoint()
        resp = post(api_endpoint, data=body, headers=headers)
        content = loads(resp.content)
        token = _OAuthToken()
        token.token_response = content

        return self._finish(resp, token, content)

    def _get_endpoint(self) -> str:
        """
        :return url (str)
        :return:
        """
        if self._sandbox:
            return "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            return "https://api.ebay.com/identity/v1/oauth2/token"

    def _generate_request_headers(self) -> dict:
        """
        :return headers (dict)
        """
        b64_encoded_credential = b64encode((self._client_id + ':' + self._client_secret).encode())
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + b64_encoded_credential.decode()
        }
        return headers

    def _generate_application_request_body(self, scopes: List[str]) -> dict:
        """
        :param scopes list(str)
        :return body (dict)
        """
        body = {
            'grant_type': 'client_credentials',
            'redirect_uri': self._ru_name,
            'scope': ' '.join(scopes)
        }
        return body

    @staticmethod
    def _generate_refresh_request_body(scopes: List[str], refresh_token: str) -> dict:
        """
        :param scopes (list(str), required):
        :param refresh_token (str, required):
        :return body (dict):
        """
        if refresh_token is None:
            raise Error(number=96013, reason="credential object does not contain refresh_token and/or scopes")
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': ' '.join(scopes)
        }
        return body

    def _generate_oauth_request_body(self, code: str) -> dict:
        """
        :param code (str):
        :return body (dict):
        """
        body = {
            'grant_type': 'authorization_code',
            'redirect_uri': self._ru_name,
            'code': code
        }
        return body

    @staticmethod
    def _finish(resp: Response, token: _OAuthToken, content: dict) -> _OAuthToken:
        """
        :param resp (Response, required):
        :param token (_OAuthToken:, required):
        :param content (dict, required):
        :return:
        """
        if resp.status_code == codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = (
                    datetime.utcnow()
                    + timedelta(seconds=int(content['expires_in']))
                    - timedelta(minutes=5)
            )
        else:
            token.error = str(resp.status_code)
            key = 'error_description'
            if key in content:
                token.error += ': ' + content[key]

        return token


class KeyPairToken(metaclass=Multiton):
    """An eBay private/public key pair created using
    the eBay Key Management API.
    Digital signature credentials are optional if you don't make API
    calls that need a public/private key pair.
    """

    __slots__ = (
        "_lock", "_creation_time", "_expiration_time", "_jwe",
        "_private_key", "_public_key", "_signing_key_cipher", "_signing_key_id"
    )

    def __init__(self,
                 creation_time: int or None = None,
                 expiration_time: int or None = None,
                 jwe: str or None = None,
                 private_key: str or None = None,
                 public_key: str or None = None,
                 signing_key_cipher: str or None = None,
                 signing_key_id: str or None = None) -> None:
        """
        # eBay key pair details
        :param creation_time (int, optional):
        :param expiration_time (int, optional):
        :param jwe (str, optional):
        :param private_key (str, optional):
        :param public_key (str, optional):
        :param signing_key_cipher (str, optional):
        :param signing_key_id (str, optional):
        :return: None (None)
        """
        self._lock = Lock()
        # The Multiton decorator wraps this initializer with a thread lock; it is safe to skip using self._lock.
        self._creation_time = DateTime.from_string(creation_time) if creation_time else None
        self._expiration_time = DateTime.from_string(expiration_time) if expiration_time else None
        self._jwe = jwe
        self._private_key = private_key
        self._public_key = public_key
        self._signing_key_cipher = signing_key_cipher
        self._signing_key_id = signing_key_id
        if self._signing_key_cipher:
            self._signing_key_cipher = self._signing_key_cipher.upper()
            if self._signing_key_cipher != 'ED25519':
                raise Error(
                    number=96020,
                    reason='Digital Signatures key pair invalid cipher',
                    detail='Only the ED25519 cipher is supported by ebay_rest'
                )

    def key_dict(self):
        """Get the public and private key ready for a request"""
        pk = load_der_private_key(b64decode(self._private_key), password=None)
        return {
            'jwe': self._jwe,
            'private_key': pk
        }

    def _current_key_sufficient(self) -> bool:
        """Check if the current key pair is sufficient to call get_signing_key.

        Returns True if so, else False

        :return bool
        """
        return self._private_key and self._signing_key_id

    def _current_key_in_date(self) -> bool or None:
        """Check if the current key pair has a date and, if it does, if
        the key pair is in date.
        Returns True if the key has an expiry date and is in date.
        Returns False if the key has and expiry date and is expired.
        Returns None if the key has no expiry date.

        :return bool
        """
        if self._expiration_time:
            return (DateTime.now() - timedelta(seconds=90)) < self._expiration_time
        else:
            return None

    def _has_valid_key(self, api) -> bool:
        """
        Check we have enough information to request a new key pair.
        Load the new key pair, and check it is valid.

        :param api (API): A valid API instance that can be used to make
            a KeyManagementAPI call
        :return dict
        """

        if not self._current_key_sufficient():
            return False

        self._get_signing_key(api)

        if not self._current_key_in_date:
            # An expired key must be replaced
            return False

        return True

    def _ensure_key_pair(self, api) -> None:
        """
        Ensures a valid key pair is available.

        :param api (API): A valid API instance that can be used to make
            a KeyManagementAPI call
        :return None (None)

        - If the key is out of date, create a new key pair.
        - If the necessary details for making an API call and the expiration
            time are provided, do nothing (assume the key pair is OK).
        - If the private key and the signing key ID are provided but details
          are not complete, load the key info.
        """

        in_date = (self._expiration_time and ((DateTime.now() - timedelta(seconds=90)) < self._expiration_time))

        if self._expiration_time and not in_date:
            # An expired key must be replaced
            self._create_key_pair(api)

        elif self._expiration_time and self._jwe and self._private_key:
            # If we have enough information to try an API call plus the
            # (in date) expiration time, assume the details are valid
            return

        elif self._current_key_sufficient():
            # We can reload the key as long as we have the private key
            # and the signing key ID
            self._get_signing_key(api)
            if (DateTime.now() - timedelta(seconds=90)) > self._expiration_time:
                # If the loaded key is out of date, raise an error
                self._create_key_pair(api)
                raise Error(
                    number=96021,
                    reason='Expired key pair',
                    detail='Key {} is expired'.format(self._signing_key_id)
                )

        else:
            # Raise an error if no good key pair provided
            raise Error(
                number=96022,
                reason='No valid key pair',
                detail='Generate a new key pair'
            )

    def _get_signing_key(self, api) -> None:
        """
        Use the eBay Key Pair Management API to load an existing eBay
        public/private key pair.

        :param api (API): A valid API instance that can be used to make
            a KeyManagementAPI call
        :return None (None)
        """
        try:
            key = api.developer_key_management_get_signing_key(signing_key_id=self._signing_key_id)
        except Error:
            raise Error(
                number=96023,
                reason='Key pair not found',
                detail='Key {} not found'.format(self._signing_key_id)
            )
        else:
            self._save_key(key)

    def _create_key_pair(self, api) -> None:
        """
        Use the eBay Key Pair Management API to generate a new eBay
        public/private key pair

        :param api (API): A valid API instance that can be used to make
            a KeyManagementAPI call
        :return None (None)
        """
        body = CreateSigningKeyRequest(signing_key_cipher='ED25519')
        try:
            key = api.developer_key_management_create_signing_key(body=body)
        except Error as e:
            raise Error(
                    number=96024,
                    reason='Failed to create key pair',
                    detail='Failed to create key pair: {}'.format(e)
                )
        else:
            self._save_key(key)

    def _load_key(self) -> dict:
        """
        Load the saved key dictionary.
        """
        creation_time = DateTime.to_string(self._creation_time)
        expiration_time = DateTime.to_string(self._expiration_time)
        return {
            'creation_time': creation_time,
            'expiration_time': expiration_time,
            'jwe': self._jwe,
            'private_key': self._private_key,
            'public_key': self._public_key,
            'signing_key_cipher': self._signing_key_cipher,
            'signing_key_id': self._signing_key_id
        }

    def _save_key(self, key) -> None:
        """
        Save a loaded key dictionary to this KeyPairToken
        :param key (dict): A dict of key properties
        """
        self._creation_time = datetime.fromtimestamp(
            key['creation_time'], tz=timezone.utc)
        self._expiration_time = datetime.fromtimestamp(
            key['expiration_time'], tz=timezone.utc)
        self._jwe = key['jwe']
        if key['private_key']:
            # Only write private key if supplied (i.e. just created)
            self._private_key = key['private_key']
        self._public_key = key['public_key']
        self._signing_key_cipher = key['signing_key_cipher']
        self._signing_key_id = key['signing_key_id']
