# coding: utf-8

"""
    Metadata API

    The Metadata API has operations that retrieve configuration details pertaining to the different eBay marketplaces. In addition to marketplace information, the API also has operations that get information that helps sellers list items on eBay.  # noqa: E501

    OpenAPI spec version: v1.9.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class SortOrderProperties(object):
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
        'order': 'str',
        'property_name': 'str'
    }

    attribute_map = {
        'order': 'order',
        'property_name': 'propertyName'
    }

    def __init__(self, order=None, property_name=None):  # noqa: E501
        """SortOrderProperties - a model defined in Swagger"""  # noqa: E501
        self._order = None
        self._property_name = None
        self.discriminator = None
        if order is not None:
            self.order = order
        if property_name is not None:
            self.property_name = property_name

    @property
    def order(self):
        """Gets the order of this SortOrderProperties.  # noqa: E501

        Defines the order of the sort.<br><br><b>Valid values</b>:<ul><li><code>Ascending</code></li><li><code>Descending</code></li></ul>  # noqa: E501

        :return: The order of this SortOrderProperties.  # noqa: E501
        :rtype: str
        """
        return self._order

    @order.setter
    def order(self, order):
        """Sets the order of this SortOrderProperties.

        Defines the order of the sort.<br><br><b>Valid values</b>:<ul><li><code>Ascending</code></li><li><code>Descending</code></li></ul>  # noqa: E501

        :param order: The order of this SortOrderProperties.  # noqa: E501
        :type: str
        """

        self._order = order

    @property
    def property_name(self):
        """Gets the property_name of this SortOrderProperties.  # noqa: E501

        The name of the searchable property to be used for sorting.<br><br>For example, typical vehicle property names are 'Make', 'Model', 'Year', 'Engine', and 'Trim', but will vary based on the eBay marketplace and the eBay category.  # noqa: E501

        :return: The property_name of this SortOrderProperties.  # noqa: E501
        :rtype: str
        """
        return self._property_name

    @property_name.setter
    def property_name(self, property_name):
        """Sets the property_name of this SortOrderProperties.

        The name of the searchable property to be used for sorting.<br><br>For example, typical vehicle property names are 'Make', 'Model', 'Year', 'Engine', and 'Trim', but will vary based on the eBay marketplace and the eBay category.  # noqa: E501

        :param property_name: The property_name of this SortOrderProperties.  # noqa: E501
        :type: str
        """

        self._property_name = property_name

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
        if issubclass(SortOrderProperties, dict):
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
        if not isinstance(other, SortOrderProperties):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other