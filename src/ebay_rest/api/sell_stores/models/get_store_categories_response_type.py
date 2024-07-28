# coding: utf-8

"""
    Store API

    <p>This API provides stores-related resources for third-party developers. These resources let you retrieve basic store information such as store name, description, store url, return store category hierarchy, add,rename,move,delete a single user's eBay store category, and retrieve the processing status of these tasks.</p> <p>The stores resource methods require an access token created with the <a href=\"/api-docs/static/oauth-authorization-code-grant.html\">authorization code grant</a> flow, using one or more scopes from the following list (please check your Application Keys page for a list of OAuth scopes available to your application)</p>  # noqa: E501

    OpenAPI spec version: 1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class GetStoreCategoriesResponseType(object):
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
        'store_categories': 'list[StoreCategoryType]'
    }

    attribute_map = {
        'store_categories': 'storeCategories'
    }

    def __init__(self, store_categories=None):  # noqa: E501
        """GetStoreCategoriesResponseType - a model defined in Swagger"""  # noqa: E501
        self._store_categories = None
        self.discriminator = None
        if store_categories is not None:
            self.store_categories = store_categories

    @property
    def store_categories(self):
        """Gets the store_categories of this GetStoreCategoriesResponseType.  # noqa: E501

        An array of top-level categories defined for the eBay store. A childrenCategories array is used for second and third-level categories, if defined for the store.  # noqa: E501

        :return: The store_categories of this GetStoreCategoriesResponseType.  # noqa: E501
        :rtype: list[StoreCategoryType]
        """
        return self._store_categories

    @store_categories.setter
    def store_categories(self, store_categories):
        """Sets the store_categories of this GetStoreCategoriesResponseType.

        An array of top-level categories defined for the eBay store. A childrenCategories array is used for second and third-level categories, if defined for the store.  # noqa: E501

        :param store_categories: The store_categories of this GetStoreCategoriesResponseType.  # noqa: E501
        :type: list[StoreCategoryType]
        """

        self._store_categories = store_categories

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
        if issubclass(GetStoreCategoriesResponseType, dict):
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
        if not isinstance(other, GetStoreCategoriesResponseType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other