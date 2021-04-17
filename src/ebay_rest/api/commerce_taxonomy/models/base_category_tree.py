# coding: utf-8

"""
    Taxonomy API

    Use the Taxonomy API to discover the most appropriate eBay categories under which sellers can offer inventory items for sale, and the most likely categories under which buyers can browse or search for items to purchase. In addition, the Taxonomy API provides metadata about the required and recommended category aspects to include in listings, and also has two operations to retrieve parts compatibility information.  # noqa: E501

    OpenAPI spec version: v1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class BaseCategoryTree(object):
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
        'category_tree_id': 'str',
        'category_tree_version': 'str'
    }

    attribute_map = {
        'category_tree_id': 'categoryTreeId',
        'category_tree_version': 'categoryTreeVersion'
    }

    def __init__(self, category_tree_id=None, category_tree_version=None):  # noqa: E501
        """BaseCategoryTree - a model defined in Swagger"""  # noqa: E501
        self._category_tree_id = None
        self._category_tree_version = None
        self.discriminator = None
        if category_tree_id is not None:
            self.category_tree_id = category_tree_id
        if category_tree_version is not None:
            self.category_tree_version = category_tree_version

    @property
    def category_tree_id(self):
        """Gets the category_tree_id of this BaseCategoryTree.  # noqa: E501

        The unique identifier of the eBay category tree for the specified marketplace.  # noqa: E501

        :return: The category_tree_id of this BaseCategoryTree.  # noqa: E501
        :rtype: str
        """
        return self._category_tree_id

    @category_tree_id.setter
    def category_tree_id(self, category_tree_id):
        """Sets the category_tree_id of this BaseCategoryTree.

        The unique identifier of the eBay category tree for the specified marketplace.  # noqa: E501

        :param category_tree_id: The category_tree_id of this BaseCategoryTree.  # noqa: E501
        :type: str
        """

        self._category_tree_id = category_tree_id

    @property
    def category_tree_version(self):
        """Gets the category_tree_version of this BaseCategoryTree.  # noqa: E501

        The version of the category tree identified by categoryTreeId. It's a good idea to cache this value for comparison so you can determine if this category tree has been modified in subsequent calls.  # noqa: E501

        :return: The category_tree_version of this BaseCategoryTree.  # noqa: E501
        :rtype: str
        """
        return self._category_tree_version

    @category_tree_version.setter
    def category_tree_version(self, category_tree_version):
        """Sets the category_tree_version of this BaseCategoryTree.

        The version of the category tree identified by categoryTreeId. It's a good idea to cache this value for comparison so you can determine if this category tree has been modified in subsequent calls.  # noqa: E501

        :param category_tree_version: The category_tree_version of this BaseCategoryTree.  # noqa: E501
        :type: str
        """

        self._category_tree_version = category_tree_version

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
        if issubclass(BaseCategoryTree, dict):
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
        if not isinstance(other, BaseCategoryTree):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other