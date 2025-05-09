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

class Items(object):
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
        'items': 'list[CoreItem]',
        'total': 'int',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'items': 'items',
        'total': 'total',
        'warnings': 'warnings'
    }

    def __init__(self, items=None, total=None, warnings=None):  # noqa: E501
        """Items - a model defined in Swagger"""  # noqa: E501
        self._items = None
        self._total = None
        self._warnings = None
        self.discriminator = None
        if items is not None:
            self.items = items
        if total is not None:
            self.total = total
        if warnings is not None:
            self.warnings = warnings

    @property
    def items(self):
        """Gets the items of this Items.  # noqa: E501

        An arraylist of all the items.  # noqa: E501

        :return: The items of this Items.  # noqa: E501
        :rtype: list[CoreItem]
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this Items.

        An arraylist of all the items.  # noqa: E501

        :param items: The items of this Items.  # noqa: E501
        :type: list[CoreItem]
        """

        self._items = items

    @property
    def total(self):
        """Gets the total of this Items.  # noqa: E501

        The total number of items retrieved.  # noqa: E501

        :return: The total of this Items.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this Items.

        The total number of items retrieved.  # noqa: E501

        :param total: The total of this Items.  # noqa: E501
        :type: int
        """

        self._total = total

    @property
    def warnings(self):
        """Gets the warnings of this Items.  # noqa: E501

        An array of warning messages. These types of errors do not prevent the method from executing but should be checked.  # noqa: E501

        :return: The warnings of this Items.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this Items.

        An array of warning messages. These types of errors do not prevent the method from executing but should be checked.  # noqa: E501

        :param warnings: The warnings of this Items.  # noqa: E501
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
        if issubclass(Items, dict):
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
        if not isinstance(other, Items):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
