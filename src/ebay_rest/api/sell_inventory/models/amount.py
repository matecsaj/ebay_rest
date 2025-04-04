# coding: utf-8

"""
    Inventory API

    The Inventory API is used to create and manage inventory, and then to publish and manage this inventory on an eBay marketplace. There are also methods in this API that will convert eligible, active eBay listings into the Inventory API model.  # noqa: E501

    OpenAPI spec version: 1.18.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Amount(object):
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
        'currency': 'str',
        'value': 'str'
    }

    attribute_map = {
        'currency': 'currency',
        'value': 'value'
    }

    def __init__(self, currency=None, value=None):  # noqa: E501
        """Amount - a model defined in Swagger"""  # noqa: E501
        self._currency = None
        self._value = None
        self.discriminator = None
        if currency is not None:
            self.currency = currency
        if value is not None:
            self.value = value

    @property
    def currency(self):
        """Gets the currency of this Amount.  # noqa: E501

        A three-digit string value representing the type of currency being used. Both the <strong>value</strong> and <strong>currency</strong> fields are required/always returned when expressing prices. <br><br>See the <a href=\"/api-docs/sell/inventory/types/ba:CurrencyCodeEnum\" target=\"_blank\">CurrencyCodeEnum</a> type for the full list of currencies and their corresponding three-digit string values.  # noqa: E501

        :return: The currency of this Amount.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this Amount.

        A three-digit string value representing the type of currency being used. Both the <strong>value</strong> and <strong>currency</strong> fields are required/always returned when expressing prices. <br><br>See the <a href=\"/api-docs/sell/inventory/types/ba:CurrencyCodeEnum\" target=\"_blank\">CurrencyCodeEnum</a> type for the full list of currencies and their corresponding three-digit string values.  # noqa: E501

        :param currency: The currency of this Amount.  # noqa: E501
        :type: str
        """

        self._currency = currency

    @property
    def value(self):
        """Gets the value of this Amount.  # noqa: E501

        A string representation of a dollar value expressed in the currency specified in the <strong>currency</strong> field. Both the <strong>value</strong> and <strong>currency</strong> fields are required/always returned when expressing prices.  # noqa: E501

        :return: The value of this Amount.  # noqa: E501
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this Amount.

        A string representation of a dollar value expressed in the currency specified in the <strong>currency</strong> field. Both the <strong>value</strong> and <strong>currency</strong> fields are required/always returned when expressing prices.  # noqa: E501

        :param value: The value of this Amount.  # noqa: E501
        :type: str
        """

        self._value = value

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
        if issubclass(Amount, dict):
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
        if not isinstance(other, Amount):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
