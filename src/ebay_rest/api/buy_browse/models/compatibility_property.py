# coding: utf-8

"""
    Browse API

    The Browse API has the following resources:<ul><li><b>item_summary:</b><br>Allows shoppers to search for specific items by keyword, GTIN, category, charity, product, image, or item aspects and refine the results by using filters, such as aspects, compatibility, and fields values, or UI parameters.</li><li><b>item:</b><br>Allows shoppers to retrieve the details of a specific item or all items in an item group, which is an item with variations such as color and size and check if a product is compatible with the specified item, such as if a specific car is compatible with a specific part.<br><br>This resource also provides a bridge between the eBay legacy APIs, such as the <a href=\"/api-docs/user-guides/static/finding-user-guide-landing.html\" target=\"_blank\">Finding</b>, and the RESTful APIs, which use different formats for the item IDs.</li></ul>The <b>item_summary</b>, <b>search_by_image</b>, and <b>item</b> resource calls require an <a href=\"/api-docs/static/oauth-client-credentials-grant.html\" target=\"_blank\">Application access token</a>.  # noqa: E501

    OpenAPI spec version: v1.20.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class CompatibilityProperty(object):
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
        'localized_name': 'str',
        'name': 'str',
        'value': 'str'
    }

    attribute_map = {
        'localized_name': 'localizedName',
        'name': 'name',
        'value': 'value'
    }

    def __init__(self, localized_name=None, name=None, value=None):  # noqa: E501
        """CompatibilityProperty - a model defined in Swagger"""  # noqa: E501
        self._localized_name = None
        self._name = None
        self._value = None
        self.discriminator = None
        if localized_name is not None:
            self.localized_name = localized_name
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value

    @property
    def localized_name(self):
        """Gets the localized_name of this CompatibilityProperty.  # noqa: E501

        The name of the product attribute that as been translated to the language of the site.  # noqa: E501

        :return: The localized_name of this CompatibilityProperty.  # noqa: E501
        :rtype: str
        """
        return self._localized_name

    @localized_name.setter
    def localized_name(self, localized_name):
        """Sets the localized_name of this CompatibilityProperty.

        The name of the product attribute that as been translated to the language of the site.  # noqa: E501

        :param localized_name: The localized_name of this CompatibilityProperty.  # noqa: E501
        :type: str
        """

        self._localized_name = localized_name

    @property
    def name(self):
        """Gets the name of this CompatibilityProperty.  # noqa: E501

        The name of the product attribute, such as Make, Model, Year, etc.  # noqa: E501

        :return: The name of this CompatibilityProperty.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CompatibilityProperty.

        The name of the product attribute, such as Make, Model, Year, etc.  # noqa: E501

        :param name: The name of this CompatibilityProperty.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def value(self):
        """Gets the value of this CompatibilityProperty.  # noqa: E501

        The value for the <code>name</code> attribute, such as <b>BMW</b>, <b>R1200GS</b>, <b>2011</b>, etc.  # noqa: E501

        :return: The value of this CompatibilityProperty.  # noqa: E501
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this CompatibilityProperty.

        The value for the <code>name</code> attribute, such as <b>BMW</b>, <b>R1200GS</b>, <b>2011</b>, etc.  # noqa: E501

        :param value: The value of this CompatibilityProperty.  # noqa: E501
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
        if issubclass(CompatibilityProperty, dict):
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
        if not isinstance(other, CompatibilityProperty):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
