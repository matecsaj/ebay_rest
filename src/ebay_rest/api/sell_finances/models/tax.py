# coding: utf-8

"""
    Finances API

    This API is used to retrieve seller payouts and monetary transaction details related to those payouts.  # noqa: E501

    OpenAPI spec version: v1.17.3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Tax(object):
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
        'tax_type': 'str',
        'amount': 'Amount'
    }

    attribute_map = {
        'tax_type': 'taxType',
        'amount': 'amount'
    }

    def __init__(self, tax_type=None, amount=None):  # noqa: E501
        """Tax - a model defined in Swagger"""  # noqa: E501
        self._tax_type = None
        self._amount = None
        self.discriminator = None
        if tax_type is not None:
            self.tax_type = tax_type
        if amount is not None:
            self.amount = amount

    @property
    def tax_type(self):
        """Gets the tax_type of this Tax.  # noqa: E501

        The enumeration value returned here indicates the type of tax. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/finances/types/pay:TaxTypeEnum'>eBay API documentation</a>  # noqa: E501

        :return: The tax_type of this Tax.  # noqa: E501
        :rtype: str
        """
        return self._tax_type

    @tax_type.setter
    def tax_type(self, tax_type):
        """Sets the tax_type of this Tax.

        The enumeration value returned here indicates the type of tax. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/finances/types/pay:TaxTypeEnum'>eBay API documentation</a>  # noqa: E501

        :param tax_type: The tax_type of this Tax.  # noqa: E501
        :type: str
        """

        self._tax_type = tax_type

    @property
    def amount(self):
        """Gets the amount of this Tax.  # noqa: E501


        :return: The amount of this Tax.  # noqa: E501
        :rtype: Amount
        """
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the amount of this Tax.


        :param amount: The amount of this Tax.  # noqa: E501
        :type: Amount
        """

        self._amount = amount

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
        if issubclass(Tax, dict):
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
        if not isinstance(other, Tax):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
