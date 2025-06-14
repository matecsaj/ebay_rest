# coding: utf-8

"""
    Metadata API

    The Metadata API has operations that retrieve configuration details pertaining to the different eBay marketplaces. In addition to marketplace information, the API also has operations that get information that helps sellers list items on eBay.  # noqa: E501

    OpenAPI spec version: v1.11.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class GetCurrenciesResponse(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'default_currency': 'Currency',
        'marketplace_id': 'str'
    }

    attribute_map = {
        'default_currency': 'defaultCurrency',
        'marketplace_id': 'marketplaceId'
    }

    def __init__(self, default_currency=None, marketplace_id=None):  # noqa: E501
        """GetCurrenciesResponse - a model defined in Swagger"""  # noqa: E501
        self._default_currency = None
        self._marketplace_id = None
        self.discriminator = None
        if default_currency is not None:
            self.default_currency = default_currency
        if marketplace_id is not None:
            self.marketplace_id = marketplace_id

    @property
    def default_currency(self):
        """Gets the default_currency of this GetCurrenciesResponse.  # noqa: E501


        :return: The default_currency of this GetCurrenciesResponse.  # noqa: E501
        :rtype: Currency
        """
        return self._default_currency

    @default_currency.setter
    def default_currency(self, default_currency):
        """Sets the default_currency of this GetCurrenciesResponse.


        :param default_currency: The default_currency of this GetCurrenciesResponse.  # noqa: E501
        :type: Currency
        """

        self._default_currency = default_currency

    @property
    def marketplace_id(self):
        """Gets the marketplace_id of this GetCurrenciesResponse.  # noqa: E501

        The ID of the eBay marketplace to which the default currency applies. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/metadata/types/bas:MarketplaceIdEnum'>eBay API documentation</a>  # noqa: E501

        :return: The marketplace_id of this GetCurrenciesResponse.  # noqa: E501
        :rtype: str
        """
        return self._marketplace_id

    @marketplace_id.setter
    def marketplace_id(self, marketplace_id):
        """Sets the marketplace_id of this GetCurrenciesResponse.

        The ID of the eBay marketplace to which the default currency applies. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/metadata/types/bas:MarketplaceIdEnum'>eBay API documentation</a>  # noqa: E501

        :param marketplace_id: The marketplace_id of this GetCurrenciesResponse.  # noqa: E501
        :type: str
        """

        self._marketplace_id = marketplace_id

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(GetCurrenciesResponse, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, GetCurrenciesResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
