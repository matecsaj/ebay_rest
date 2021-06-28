# -*- coding: utf-8 -*-
"""
Copyright 2019 eBay Inc.

Licensed under the Apache License, Version 2.0 (the "License");
You may not use this file except in compliance with the License.
You may obtain a copy of the License at
    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,

WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from urllib.parse import urlencode
import requests
import logging
from .model import util
from datetime import datetime, timedelta
from .credentialutil import CredentialUtil
from .model.model import OAuthToken


class OAuth2Api():
    def __init__(self, credential_store=None):
        """Initialize OAuth2Api instance

        :param credential_store: Typically a CredentialUtil instance.
        """
        self.credential_store = credential_store or CredentialUtil()

    def generate_user_authorization_url(self, env_type, scopes, state=None):
        """
            env_type = environment.SANDBOX or environment.PRODUCTION
            scopes = list of strings
        """

        credential = self.credential_store.get_credentials(env_type)

        scopes = ' '.join(scopes)
        param = {
            'client_id': credential.client_id,
            'redirect_uri': credential.ru_name,
            'response_type': 'code',
            'prompt': 'login',
            'scope': scopes
        }

        if state is not None:
            param.update({'state': state})

        query = urlencode(param)
        return env_type.web_endpoint + '?' + query

    def get_application_token(self, env_type, scopes):
        """
            makes call for application token and stores result in credential object
            returns credential object
        """

        logging.debug("Trying to get a new application access token ... ")
        credential = self.credential_store.get_credentials(env_type)
        headers = util.generate_request_headers(credential)
        body = util.generate_application_request_body(credential, ' '.join(scopes))

        resp = requests.post(env_type.api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = OAuthToken()

        return self._finish(resp, token, content)

    def exchange_code_for_access_token(self, env_type, code):
        logging.debug("Trying to get a new user access token ... ")
        credential = self.credential_store.get_credentials(env_type)

        headers = util.generate_request_headers(credential)
        body = util.generate_oauth_request_body(credential, code)
        resp = requests.post(env_type.api_endpoint, data=body, headers=headers)

        content = json.loads(resp.content)
        token = OAuthToken()

        if resp.status_code == requests.codes.ok:
            token.refresh_token = content['refresh_token']
            token.refresh_token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content['refresh_token_expires_in']))
                - timedelta(minutes=5)
            )

        return self._finish(resp, token, content)

    def get_access_token(self, env_type, refresh_token, scopes):
        """
        refresh token call
        """

        logging.debug("Trying to get a new user access token ... ")

        credential = self.credential_store.get_credentials(env_type)

        headers = util.generate_request_headers(credential)
        body = util.generate_refresh_request_body(' '.join(scopes), refresh_token)
        resp = requests.post(env_type.api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = OAuthToken()
        token.token_response = content

        return self._finish(resp, token, content)

    @staticmethod
    def _finish(resp, token, content):

        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = (
                datetime.utcnow()
                + timedelta(seconds=int(content['expires_in']))
                - timedelta(minutes=5)
            )
        # else:
            # token.error = str(resp.status_code) + ': ' + content['error_description']
            # logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, resp.reason)
            # logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token
