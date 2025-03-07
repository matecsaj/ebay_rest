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

class BulkEbayOfferDetailsWithKeys(object):
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
        'requests': 'list[EbayOfferDetailsWithKeys]'
    }

    attribute_map = {
        'requests': 'requests'
    }

    def __init__(self, requests=None):  # noqa: E501
        """BulkEbayOfferDetailsWithKeys - a model defined in Swagger"""  # noqa: E501
        self._requests = None
        self.discriminator = None
        if requests is not None:
            self.requests = requests

    @property
    def requests(self):
        """Gets the requests of this BulkEbayOfferDetailsWithKeys.  # noqa: E501

        The details of each offer that is being created is passed in under this container. Up to 25 offers can be created with one <strong>bulkCreateOffer</strong> call.  # noqa: E501

        :return: The requests of this BulkEbayOfferDetailsWithKeys.  # noqa: E501
        :rtype: list[EbayOfferDetailsWithKeys]
        """
        return self._requests

    @requests.setter
    def requests(self, requests):
        """Sets the requests of this BulkEbayOfferDetailsWithKeys.

        The details of each offer that is being created is passed in under this container. Up to 25 offers can be created with one <strong>bulkCreateOffer</strong> call.  # noqa: E501

        :param requests: The requests of this BulkEbayOfferDetailsWithKeys.  # noqa: E501
        :type: list[EbayOfferDetailsWithKeys]
        """

        self._requests = requests

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
        if issubclass(BulkEbayOfferDetailsWithKeys, dict):
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
        if not isinstance(other, BulkEbayOfferDetailsWithKeys):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
