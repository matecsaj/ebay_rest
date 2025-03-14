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

class FeeSummary(object):
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
        'fees': 'list[Fee]',
        'marketplace_id': 'str',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'fees': 'fees',
        'marketplace_id': 'marketplaceId',
        'warnings': 'warnings'
    }

    def __init__(self, fees=None, marketplace_id=None, warnings=None):  # noqa: E501
        """FeeSummary - a model defined in Swagger"""  # noqa: E501
        self._fees = None
        self._marketplace_id = None
        self._warnings = None
        self.discriminator = None
        if fees is not None:
            self.fees = fees
        if marketplace_id is not None:
            self.marketplace_id = marketplace_id
        if warnings is not None:
            self.warnings = warnings

    @property
    def fees(self):
        """Gets the fees of this FeeSummary.  # noqa: E501

        This container is an array of listing fees that can be expected to be applied to an offer on the specified eBay marketplace (<strong>marketplaceId</strong> value). Many fee types will get returned even when they are <code>0.0</code>.<br><br>See the <a href=\"https://pages.ebay.com/help/sell/fees.html \" target=\"_blank\">Standard selling fees</a> help page for more information on listing fees.  # noqa: E501

        :return: The fees of this FeeSummary.  # noqa: E501
        :rtype: list[Fee]
        """
        return self._fees

    @fees.setter
    def fees(self, fees):
        """Sets the fees of this FeeSummary.

        This container is an array of listing fees that can be expected to be applied to an offer on the specified eBay marketplace (<strong>marketplaceId</strong> value). Many fee types will get returned even when they are <code>0.0</code>.<br><br>See the <a href=\"https://pages.ebay.com/help/sell/fees.html \" target=\"_blank\">Standard selling fees</a> help page for more information on listing fees.  # noqa: E501

        :param fees: The fees of this FeeSummary.  # noqa: E501
        :type: list[Fee]
        """

        self._fees = fees

    @property
    def marketplace_id(self):
        """Gets the marketplace_id of this FeeSummary.  # noqa: E501

        This is the unique identifier of the eBay site for which  listing fees for the offer are applicable. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:MarketplaceEnum'>eBay API documentation</a>  # noqa: E501

        :return: The marketplace_id of this FeeSummary.  # noqa: E501
        :rtype: str
        """
        return self._marketplace_id

    @marketplace_id.setter
    def marketplace_id(self, marketplace_id):
        """Sets the marketplace_id of this FeeSummary.

        This is the unique identifier of the eBay site for which  listing fees for the offer are applicable. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:MarketplaceEnum'>eBay API documentation</a>  # noqa: E501

        :param marketplace_id: The marketplace_id of this FeeSummary.  # noqa: E501
        :type: str
        """

        self._marketplace_id = marketplace_id

    @property
    def warnings(self):
        """Gets the warnings of this FeeSummary.  # noqa: E501

        This container will contain an array of errors and/or warnings when a call is made, and errors and/or warnings occur.  # noqa: E501

        :return: The warnings of this FeeSummary.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this FeeSummary.

        This container will contain an array of errors and/or warnings when a call is made, and errors and/or warnings occur.  # noqa: E501

        :param warnings: The warnings of this FeeSummary.  # noqa: E501
        :type: list[Error]
        """

        self._warnings = warnings

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
        if issubclass(FeeSummary, dict):
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
        if not isinstance(other, FeeSummary):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
