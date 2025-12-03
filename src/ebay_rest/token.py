# Standard library imports
from base64 import b64encode, b64decode
import binascii
from datetime import datetime, timedelta, timezone
from json import loads
import logging
from threading import Lock
import time
from typing import List, Optional
from urllib.parse import urlparse, parse_qs, unquote, urlencode
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

    __slots__ = (
        "_lock",
        "_sandbox",
        "_application_scopes",
        "_application_token",
        "_oauth2api_inst",
    )

    def __init__(
        self,
        sandbox: bool,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        ru_name: Optional[str] = None,
        application_scopes: Optional[List[str]] = None,
    ) -> None:
        """
        application/client credentials are optional if you don't make API calls that need an application/client token

        :param sandbox: The system to use, True for Sandbox/Testing and False for Production.
        :param client_id:
        :param client_secret:
        :param ru_name:
        :param application_scopes:
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

        :return: token
        """
        with self._lock:
            if self._application_scopes is None:
                self._determine_application_scopes()

            if self._application_token is None:
                self._refresh_application()
            elif (
                self._application_token.token_expiry.replace(tzinfo=timezone.utc)
                <= DateTime.now()
            ):
                self._refresh_application()

            token = self._application_token.access_token

        return token

    def _determine_application_scopes(self) -> None:
        """
        Determine the application scopes that are currently allowed.
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
        """
        token_application = self._oauth2api_inst.get_application_token(
            self._application_scopes
        )
        if token_application.error is not None:
            reason = "token_application.error " + token_application.error
            raise Error(number=96001, reason=reason)
        if (token_application.access_token is None) or (
            len(token_application.access_token) == 0
        ):
            raise Error(
                number=96002, reason="token_application.access_token is missing."
            )

        self._application_token = token_application


class UserToken(metaclass=Multiton):
    """
    Initialize, refresh and supply an eBay OAuth ***user*** token.
    This is a facade for the oath module.
    """

    __slots__ = (
        "_lock",
        "_sandbox",
        "_user_id",
        "_user_password",
        "_user_scopes",
        "_user_token",
        "_oauth2api_inst",
        "_user_refresh_token",
        "_user_refresh_token_expiry",
        "_allow_get_user_consent",
    )

    def __init__(
        self,
        sandbox: bool,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        ru_name: Optional[str] = None,
        user_id: Optional[str] = None,
        user_password: Optional[str] = None,
        user_scopes: Optional[List[str]] = None,
        user_refresh_token: Optional[str] = None,
        user_refresh_token_expiry: Optional[str] = None,
    ) -> None:
        """
        :param sandbox: The system to use, True for Sandbox/Testing and False for Production.

        # application/client credentials, optional if you don't make API calls that need an application/client token
        :param client_id:
        :param client_secret:
        :param ru_name:

        # user credentials, optional if you don't make API calls that need a user token
        :param user_id:
        :param user_password:
        :param user_scopes:

        # user token supply, optional if you don't mind a Chrome browser opening when getting a user token
        :param user_refresh_token:
        :param user_refresh_token_expiry:
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
                self._user_refresh_token_expiry = DateTime.from_string(
                    user_refresh_token_expiry
                )
                user_refresh_token_expiry = DateTime.from_string(
                    user_refresh_token_expiry
                )
                if user_refresh_token_expiry <= DateTime.now():
                    raise Error(
                        number=96025,
                        reason="The supplied user refresh token has an expired date.",
                        detail=f"Supplied {user_refresh_token_expiry}. Now {DateTime.now()}.",
                    )

                self._allow_get_user_consent = False
                if self._user_scopes is None:
                    self._determine_user_scopes()
                try:
                    self._user_refresh_token_expiry = user_refresh_token_expiry
                except Error as error:
                    raise Error(
                        number=96003,
                        reason="user_refresh_token_expiry value error",
                        detail=error.reason,
                    )
                self._user_refresh_token = _OAuthToken(
                    refresh_token=self._user_refresh_token,
                    refresh_token_expiry=self._user_refresh_token_expiry,
                )
            else:
                raise Error(
                    number=96004,
                    reason="Must supply refresh token expiry with refresh token!",
                )

    def get(self) -> str:
        """
        Get an eBay User Access Token.

        :return: token
        """
        with self._lock:
            if self._user_scopes is None:
                self._determine_user_scopes()

            if self._user_token is None:
                self._refresh_user()
            elif (
                self._user_token.token_expiry.replace(tzinfo=timezone.utc)
                <= DateTime.now()
            ):
                self._refresh_user()

            token = self._user_token.access_token
        return token

    def _determine_user_scopes(self) -> None:
        """
        Determine the user access scopes that are currently allowed.
        """
        if self._sandbox:
            # permission is always granted for all
            scopes = list(Reference.get_user_scopes().keys())
        else:
            # these are always granted, many more are possible
            scopes = [
                "https://api.ebay.com/oauth/api_scope",
                "https://api.ebay.com/oauth/api_scope/sell.inventory",
                "https://api.ebay.com/oauth/api_scope/sell.marketing",
                "https://api.ebay.com/oauth/api_scope/sell.account",
                "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
            ]
        self._user_scopes = scopes

    def _refresh_user(self) -> None:
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

    def _authorization_flow(self) -> None:
        """
        Get an authorization code by running authorization-flow.
        Exchange that for a refresh token (which also contains a user token).
        """
        if not self._allow_get_user_consent:
            raise Error(
                number=96005, reason="Getting user consent via browser disabled"
            )

        sign_in_url = self._oauth2api_inst.generate_user_authorization_url(
            self._user_scopes
        )
        if sign_in_url is None:
            raise Error(number=96006, reason="sign_in_url is None.")

        code = self._get_authorization_code(sign_in_url)

        refresh_token = self._oauth2api_inst.exchange_code_for_access_token(code)

        if refresh_token.access_token is None:
            raise Error(number=96007, reason="refresh_token.access_token is None.")
        if len(refresh_token.access_token) == 0:
            raise Error(
                number=96008, reason="refresh_token.access_token is of length zero."
            )

        # Split token into refresh token and user token parts
        self._user_refresh_token = _OAuthToken(
            refresh_token=refresh_token.refresh_token,
            refresh_token_expiry=refresh_token.refresh_token_expiry,
        )
        self._user_token = _OAuthToken(
            access_token=refresh_token.access_token,
            token_expiry=refresh_token.token_expiry,
        )

        # Give the user a helpful suggestion.
        expiry = DateTime.to_string(refresh_token.refresh_token_expiry)
        message = (
            f"Edit to your ebay_rest.json file to avoid the browser pop-up.\n"
            f"For the user with an email or username of {self._user_id}.\n"
            f'"refresh_token": "{refresh_token.refresh_token}"\n'
            f'"refresh_token_expiry": "{expiry}"'
        )
        logging.info(message)

    def _get_authorization_code(self, sign_in_url: str) -> str:
        """
        Run the authorization flow to get an authorization code, which can subsequently be exchanged for a refresh (and user) token.

        :param sign_in_url: The redirect URL for gaining user consent.
        :return: Authorization code.
        """
        try:
            from playwright.sync_api import (
                sync_playwright,
                Error as PlaywrightError,
                TimeoutError as PlaywrightTimeoutError,
            )
        except ModuleNotFoundError:
            reason = f"Supply an 'eBay user token' or install the COMPLETE variant of ebay_rest. Refer to the README.md at https://github.com/matecsaj/ebay_rest."  # noqa: E501
            logging.critical(reason)
            raise Error(number=96019, reason=reason)

        # Begin with all Playwright resources set to None.
        playwright = browser = context = page = None

        try:
            # Initialize Playwright
            playwright = sync_playwright().start()
            # Launch the browser in a non-headless mode
            browser = playwright.chromium.launch(headless=False)
            # Open a new browser context (equivalent to an incognito window)
            context = browser.new_context()
            # Open a new page within the context
            page = context.new_page()

            # Load the initial page
            page.goto(sign_in_url)

            # Fill in the username, then click continue
            page.wait_for_selector("input[name='userid']").type(self._user_id)
            page.wait_for_selector("#signin-continue-btn").click()

            # Fill in the password, then submit
            page.wait_for_selector("input[name='pass']").type(self._user_password)
            page.wait_for_selector("#sgnBt").click()

            # Handle additional steps like prompts or 2FA
            seconds = 0
            while seconds < 30:

                selectors = [
                    "#passkeys-cancel-btn",  # "Simplify your sign-in" prompt; skip it for now
                    "#submit",  # "I agree" prompt; agree
                ]
                for selector in selectors:
                    try:
                        page.wait_for_selector(selector, timeout=1)
                        page.click(selector)
                        seconds = 0  # Reset our timer when an interaction happens
                    except PlaywrightTimeoutError:
                        pass

                # Detect if we're on a 2FA input page and wait for user action
                try:
                    page.wait_for_selector(
                        "input[name='otpCode']", timeout=1000
                    )  # eBay's 2FA input field
                    logging.info("Waiting for user to enter 2FA code...")
                    while "AuthSuccessful" not in page.url:
                        time.sleep(1)  # Give the user time to enter the 2FA code
                        seconds = 0  # Reset timeout while waiting
                except PlaywrightTimeoutError:
                    pass  # No 2FA challenge detected, continue as usual

                # Have we reached the final page?
                if "AuthSuccessful" in page.url:
                    code = self.extract_code_from_url(page.url)
                    if code is not None:
                        return code
                    else:
                        reason = f"Authorization failed, check userid & password:{self._user_id} {self._user_password}"
                        raise Error(number=96010, reason=reason)

                seconds += 1  # Increment timeout if we're still waiting

            raise Error(
                number=96027,
                reason="Last page not found.",
                detail="Has eBay's website changed?",
            )

        except PlaywrightError as e:
            detail = str(e)
            # Check for Chromium not installed error
            if "BrowserType.launch" in detail:
                number = 96029
                reason = "Chromium is not installed. Run `playwright install chromium` to install it."
            # Check for an "element not found" error
            elif "No node found for selector" in detail:
                number = 96015
                reason = (
                    "An element was not found on the page. Has eBay's website changed?"
                )
            else:
                number = 96030
                reason = "Playwright encountered an unexpected error."
            logging.critical(reason)
            raise Error(number=number, reason=reason, detail=detail)

        except PlaywrightTimeoutError:
            raise Error(
                number=96016, reason="Timeout.", detail="Slow computer or Internet?"
            )

        finally:
            # Ensure that Playwright resources are cleaned up; don't reorder.
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

    @staticmethod
    def extract_code_from_url(url: str) -> Optional[str]:
        """
        Extract only the 'code' value from an eBay callback URL.
        Returns the extracted 'code' as a string if found, otherwise returns None.
        """
        # 1) Parse the top-level URL
        parsed = urlparse(url)
        qs_top = parse_qs(parsed.query)

        # Check if code is directly in the top-level query
        top_code = qs_top.get("code", [None])[0]
        if top_code:
            return unquote(top_code)

        # 2) Otherwise, look for the nested 'ru' parameter
        ru_encoded = qs_top.get("ru", [""])[0]
        if not ru_encoded:
            # If 'ru' is missing, no code can be extracted
            return None

        # Decode 'ru' once
        ru_decoded = unquote(ru_encoded)

        # Extract the `code` field directly from the query part
        # We can't use parse_qs because some codes contain a '&' which is the start delimiter for a query string's key.
        start_index = ru_decoded.find("&code=") + len("&code=")
        end_index = ru_decoded.find("&expires_in=", start_index)
        if start_index > len("&code=") - 1 and end_index != -1:
            nested_code = unquote(ru_decoded[start_index:end_index])
            return nested_code

        return None

    def _refresh_user_token(self) -> None:
        """
        Exchange a refresh token for a current user token.

        :return: None (None)
        """
        user_token = self._oauth2api_inst.get_access_token(
            self._user_refresh_token.refresh_token, self._user_scopes
        )

        if user_token.access_token is None:
            raise Error(
                number=96011, reason=user_token.token_response["error_description"]
            )
        if len(user_token.access_token) == 0:
            raise Error(
                number=96012, reason="user_token.access_token is of length zero."
            )

        self._user_token = user_token


class _OAuthToken(object):
    __slots__ = (
        "access_token",
        "token_expiry",
        "refresh_token",
        "refresh_token_expiry",
        "error",
        "token_response",
    )

    def __init__(
        self,
        error: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        refresh_token_expiry: Optional[datetime] = None,
        token_expiry: Optional[datetime] = None,
    ) -> None:
        """
        :param error:
        :param access_token:
        :param refresh_token:
        :param refresh_token_expiry: datetime in UTC
        :param token_expiry: datetime in UTC
        """
        self.access_token = access_token
        self.token_expiry = token_expiry
        self.refresh_token = refresh_token
        self.refresh_token_expiry = refresh_token_expiry
        self.error = error
        self.token_response = None

    def __str__(self) -> str:
        """
        :return: token_str:
        """
        token_str = "{"
        if self.error is not None:
            token_str += '"error": "' + self.error + '"'
        elif self.access_token is not None:
            token_str += (
                '"access_token": "'
                + self.access_token
                + '", "expires_in": "'
                + self.token_expiry.strftime("%Y-%m-%dT%H:%M:%S:%f")
                + '"'
            )
            if self.refresh_token is not None:
                token_str += (
                    ', "refresh_token": "'
                    + self.refresh_token
                    + '", "refresh_token_expire_in": "'
                    + self.refresh_token_expiry.strftime("%Y-%m-%dT%H:%M:%S:%f")
                    + '"'
                )
        token_str += "}"
        return token_str


class _OAuth2Api:
    __slots__ = "_sandbox", "_client_id", "_client_secret", "_ru_name"

    def __init__(self, sandbox: bool, client_id: str, client_secret: str, ru_name: str):
        """
        Initialize OAuth2Api instance

        :param sandbox:
        :param client_id:
        :param client_secret:
        :param ru_name:
        """
        self._sandbox = sandbox

        # application/client
        self._client_id = client_id
        self._client_secret = client_secret
        self._ru_name = ru_name

    def generate_user_authorization_url(
        self,
        scopes: List[str],
        state: Optional[str] = None,
    ) -> str:
        """
        :param scopes:
        :param state:
        """
        param = {
            "client_id": self._client_id,
            "redirect_uri": self._ru_name,
            "response_type": "code",
            "prompt": "login",
            "scope": " ".join(scopes),
        }

        if state is not None:
            param.update({"state": state})

        query = urlencode(param)
        if self._sandbox:
            web_endpoint = "https://auth.sandbox.ebay.com/oauth2/authorize"
        else:
            web_endpoint = "https://auth.ebay.com/oauth2/authorize"
        return web_endpoint + "?" + query

    def get_application_token(self, scopes: List[str]) -> _OAuthToken:
        """
        Makes call for application token and stores result in a credential object.

        :param scopes:
        :return: credential_object _OAuthToken
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
        :param code:
        :return: credential_object _OAuthToken
        """
        logging.debug("Trying to get a new user access token ... ")

        headers = self._generate_request_headers()
        body = self._generate_oauth_request_body(code)
        api_endpoint = self._get_endpoint()
        resp = post(api_endpoint, data=body, headers=headers)

        content = loads(resp.content)
        token = _OAuthToken()

        if resp.status_code == codes.ok:
            token.refresh_token = content["refresh_token"]
            token.refresh_token_expiry = (
                datetime.now(timezone.utc)
                + timedelta(seconds=int(content["refresh_token_expires_in"]))
                - timedelta(minutes=5)
            )

        return self._finish(resp, token, content)

    def get_access_token(self, refresh_token: str, scopes: List[str]) -> _OAuthToken:
        """
        refresh token call
        :param refresh_token:
        :param scopes:
        :return: credential_object _OAuthToken
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
        :return: url
        """
        if self._sandbox:
            return "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            return "https://api.ebay.com/identity/v1/oauth2/token"

    def _generate_request_headers(self) -> dict:
        """
        :return: headers
        """
        b64_encoded_credential = b64encode(
            (self._client_id + ":" + self._client_secret).encode()
        )
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + b64_encoded_credential.decode(),
        }
        return headers

    def _generate_application_request_body(self, scopes: List[str]) -> dict:
        """
        :param scopes: list
        :return: body
        """
        body = {
            "grant_type": "client_credentials",
            "redirect_uri": self._ru_name,
            "scope": " ".join(scopes),
        }
        return body

    @staticmethod
    def _generate_refresh_request_body(scopes: List[str], refresh_token: str) -> dict:
        """
        :param scopes: (list(str), required):
        :param refresh_token:
        :return: body (dict):
        """
        if refresh_token is None:
            raise Error(
                number=96013,
                reason="credential object does not contain refresh_token and/or scopes",
            )
        body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": " ".join(scopes),
        }
        return body

    def _generate_oauth_request_body(self, code: str) -> dict:
        """
        :param code:
        :return: body dict:
        """
        body = {
            "grant_type": "authorization_code",
            "redirect_uri": self._ru_name,
            "code": code,
        }
        return body

    @staticmethod
    def _finish(resp: Response, token: _OAuthToken, content: dict) -> _OAuthToken:
        """
        :param resp:
        :param token:
        :param content:
        :return:
        """
        if resp.status_code == codes.ok:
            token.access_token = content["access_token"]
            token.token_expiry = (
                datetime.now(timezone.utc)
                + timedelta(seconds=int(content["expires_in"]))
                - timedelta(minutes=5)
            )
        else:
            token.error = str(resp.status_code)
            key = "error_description"
            if key in content:
                token.error += ": " + content[key]

        return token


class KeyPairToken(metaclass=Multiton):
    """
    An eBay private-public key pair created using the eBay Key Management API.
        Digital signature credentials are optional if you don't make API
        calls that need a public/private key pair.
    """

    __slots__ = (
        "_lock",
        "_creation_time",
        "_expiration_time",
        "_jwe",
        "_private_key",
        "_public_key",
        "_signing_key_cipher",
        "_signing_key_id",
    )

    def __init__(
        self,
        creation_time: Optional[str] = None,
        expiration_time: Optional[str] = None,
        jwe: Optional[str] = None,
        private_key: Optional[str] = None,
        public_key: Optional[str] = None,
        signing_key_cipher: Optional[str] = None,
        signing_key_id: Optional[str] = None,
    ) -> None:
        """
        # eBay key pair details

        :param creation_time:
        :param expiration_time:
        :param jwe:
        :param private_key:
        :param public_key:
        :param signing_key_cipher:
        :param signing_key_id:
        """
        self._lock = Lock()
        # The Multiton decorator wraps this initializer with a thread lock; it is safe to skip using self._lock.
        self._creation_time = (
            DateTime.from_string(creation_time) if creation_time else None
        )
        self._expiration_time = (
            DateTime.from_string(expiration_time) if expiration_time else None
        )
        self._jwe = jwe
        self._private_key = private_key
        self._public_key = public_key
        self._signing_key_cipher = signing_key_cipher
        self._signing_key_id = signing_key_id
        if self._signing_key_cipher:
            self._signing_key_cipher = self._signing_key_cipher.upper()
            if self._signing_key_cipher != "ED25519":
                raise Error(
                    number=96020,
                    reason="Digital Signatures key pair invalid cipher",
                    detail="Only the ED25519 cipher is supported by ebay_rest",
                )

    def key_dict(self):
        """
        Get the public and private key ready for a request
        """
        try:
            decoded = b64decode(self._private_key)
        except binascii.Error as e:
            raise Error(
                number=96028,
                reason="The key is not a valid base64 encoded string.",
                detail=str(e),
                cause=e,
            )
        else:
            pk = load_der_private_key(decoded, password=None)
            return {"jwe": self._jwe, "private_key": pk}

    def _current_key_sufficient(self) -> bool:
        """
        Check if the current key pair are enough to call get_signing_key.

        :return: True if sufficient
        """
        return bool(self._private_key) and bool(self._signing_key_id)

    def _current_key_in_date(self) -> Optional[bool]:
        """
        Check if the current key pair has a date and, if it does, if
                the key pair is in date.
                Returns True if the key has an expiry date and is in date.
                Returns False if the key has and expiry date and is expired.
                Returns None if the key has no expiry date.

        :return: True if it has a date
        """
        if self._expiration_time:
            return (DateTime.now() - timedelta(seconds=90)) < self._expiration_time
        else:
            return None

    def _has_valid_key(self, api) -> bool:
        """
        Check we have enough information to request a new key pair.
        Load the new key-pair and check it is valid.

        :param api: A valid API instance that can be used to make a KeyManagementAPI call
        :return: dict
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
        - If the key is out of date, create a new key pair.
        - If the necessary details for making an API call and the expiration time are provided. Do nothing (assume the key pair is OK).
        - If the private key and the signing key ID are provided but details are incomplete, load the key info.

        :param api: A valid API instance that can be used to make a KeyManagementAPI call
        """

        in_date = self._expiration_time and (
            (DateTime.now() - timedelta(seconds=90)) < self._expiration_time
        )

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
                    reason="Expired key pair",
                    detail="Key {} is expired".format(self._signing_key_id),
                )

        else:
            # Raise an error if no good key pair provided
            raise Error(
                number=96022,
                reason="No valid key pair",
                detail="Generate a new key pair",
            )

    def _get_signing_key(self, api) -> None:
        """
        Use the eBay Key Pair Management API to load an existing eBay public/private key pair.

        :param api: A valid API instance that can be used to make a KeyManagementAPI call
        """
        try:
            key = api.developer_key_management_get_signing_key(
                signing_key_id=self._signing_key_id
            )
        except Error as e:
            raise Error(
                number=96023,
                reason="Key pair not found",
                detail="Key {} not found".format(self._signing_key_id),
                cause=e,
            )
        else:
            self._save_key(key)

    def _create_key_pair(self, api) -> None:
        """
        Use the eBay Key Pair Management API to generate a new eBay public/private key pair

        :param api: A valid API instance that can be used to make a KeyManagementAPI call
        """
        body = CreateSigningKeyRequest(signing_key_cipher="ED25519")
        try:
            key = api.developer_key_management_create_signing_key(
                content_type="application/json", body=body
            )
        except Error as e:
            raise Error(
                number=96024,
                reason="Failed to create key pair",
                detail="Failed to create key pair: {}".format(e),
                cause=e,
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
            "creation_time": creation_time,
            "expiration_time": expiration_time,
            "jwe": self._jwe,
            "private_key": self._private_key,
            "public_key": self._public_key,
            "signing_key_cipher": self._signing_key_cipher,
            "signing_key_id": self._signing_key_id,
        }

    def _save_key(self, key) -> None:
        """
        Save a loaded key dictionary to this KeyPairToken

        :param key: A dict of key properties
        """
        self._creation_time = datetime.fromtimestamp(
            key["creation_time"], tz=timezone.utc
        )
        self._expiration_time = datetime.fromtimestamp(
            key["expiration_time"], tz=timezone.utc
        )
        self._jwe = key["jwe"]
        if key["private_key"]:
            # Only write a private key if supplied (i.e., just created)
            self._private_key = key["private_key"]
        self._public_key = key["public_key"]
        self._signing_key_cipher = key["signing_key_cipher"]
        self._signing_key_id = key["signing_key_id"]
