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

class ItemGroup(object):
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
        'common_descriptions': 'list[CommonDescriptions]',
        'items': 'list[Item]',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'common_descriptions': 'commonDescriptions',
        'items': 'items',
        'warnings': 'warnings'
    }

    def __init__(self, common_descriptions=None, items=None, warnings=None):  # noqa: E501
        """ItemGroup - a model defined in Swagger"""  # noqa: E501
        self._common_descriptions = None
        self._items = None
        self._warnings = None
        self.discriminator = None
        if common_descriptions is not None:
            self.common_descriptions = common_descriptions
        if items is not None:
            self.items = items
        if warnings is not None:
            self.warnings = warnings

    @property
    def common_descriptions(self):
        """Gets the common_descriptions of this ItemGroup.  # noqa: E501

        An array of containers for a description and the item IDs of all the items that have this exact description. Often the item variations within an item group all have the same description. Instead of repeating this description in the item details of each item, a description that is shared by at least one other item is returned in this container. If the description is unique, it is returned in the <b> items.description</b> field.  # noqa: E501

        :return: The common_descriptions of this ItemGroup.  # noqa: E501
        :rtype: list[CommonDescriptions]
        """
        return self._common_descriptions

    @common_descriptions.setter
    def common_descriptions(self, common_descriptions):
        """Sets the common_descriptions of this ItemGroup.

        An array of containers for a description and the item IDs of all the items that have this exact description. Often the item variations within an item group all have the same description. Instead of repeating this description in the item details of each item, a description that is shared by at least one other item is returned in this container. If the description is unique, it is returned in the <b> items.description</b> field.  # noqa: E501

        :param common_descriptions: The common_descriptions of this ItemGroup.  # noqa: E501
        :type: list[CommonDescriptions]
        """

        self._common_descriptions = common_descriptions

    @property
    def items(self):
        """Gets the items of this ItemGroup.  # noqa: E501

        An array of containers for all the item variation details, excluding the description.  # noqa: E501

        :return: The items of this ItemGroup.  # noqa: E501
        :rtype: list[Item]
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this ItemGroup.

        An array of containers for all the item variation details, excluding the description.  # noqa: E501

        :param items: The items of this ItemGroup.  # noqa: E501
        :type: list[Item]
        """

        self._items = items

    @property
    def warnings(self):
        """Gets the warnings of this ItemGroup.  # noqa: E501

        An array of warning messages. These types of errors do not prevent the method from executing but should be checked.  # noqa: E501

        :return: The warnings of this ItemGroup.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this ItemGroup.

        An array of warning messages. These types of errors do not prevent the method from executing but should be checked.  # noqa: E501

        :param warnings: The warnings of this ItemGroup.  # noqa: E501
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
        if issubclass(ItemGroup, dict):
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
        if not isinstance(other, ItemGroup):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
