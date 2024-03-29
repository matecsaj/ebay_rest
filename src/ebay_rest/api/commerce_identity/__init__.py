# coding: utf-8

# flake8: noqa

"""
    Identity API

    <span class=\"tablenote\"><b>Note:</b> Not all the account related fields are returned for an authenticated user. The fields returned in the response are controlled by the scopes and are available only to select developers approved by business units.</span><br /><br />Retrieves the authenticated user's account profile information. It can be used to let users log into your app or site using eBay, which frees you from needing to store and protect user's PII (Personal Identifiable Information) data.  # noqa: E501

    OpenAPI spec version: v2.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

# import apis into sdk package
from ..commerce_identity.api.user_api import UserApi
# import ApiClient
from ..commerce_identity.api_client import ApiClient
from ..commerce_identity.configuration import Configuration
# import models into sdk package
from ..commerce_identity.models.address import Address
from ..commerce_identity.models.business_account import BusinessAccount
from ..commerce_identity.models.contact import Contact
from ..commerce_identity.models.error import Error
from ..commerce_identity.models.error_parameter import ErrorParameter
from ..commerce_identity.models.individual_account import IndividualAccount
from ..commerce_identity.models.phone import Phone
from ..commerce_identity.models.user_response import UserResponse
