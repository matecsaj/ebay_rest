# coding: utf-8

"""
    Taxonomy API

    Use the Taxonomy API to discover the most appropriate eBay categories under which sellers can offer inventory items for sale, and the most likely categories under which buyers can browse or search for items to purchase. In addition, the Taxonomy API provides metadata about the required and recommended category aspects to include in listings, and also has two operations to retrieve parts compatibility information.  # noqa: E501

    OpenAPI spec version: v1.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ExpiredCategory(object):
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
        'from_category_id': 'str',
        'to_category_id': 'str'
    }

    attribute_map = {
        'from_category_id': 'fromCategoryId',
        'to_category_id': 'toCategoryId'
    }

    def __init__(self, from_category_id=None, to_category_id=None):  # noqa: E501
        """ExpiredCategory - a model defined in Swagger"""  # noqa: E501
        self._from_category_id = None
        self._to_category_id = None
        self.discriminator = None
        if from_category_id is not None:
            self.from_category_id = from_category_id
        if to_category_id is not None:
            self.to_category_id = to_category_id

    @property
    def from_category_id(self):
        """Gets the from_category_id of this ExpiredCategory.  # noqa: E501

        The unique identifier of the expired eBay leaf category.  # noqa: E501

        :return: The from_category_id of this ExpiredCategory.  # noqa: E501
        :rtype: str
        """
        return self._from_category_id

    @from_category_id.setter
    def from_category_id(self, from_category_id):
        """Sets the from_category_id of this ExpiredCategory.

        The unique identifier of the expired eBay leaf category.  # noqa: E501

        :param from_category_id: The from_category_id of this ExpiredCategory.  # noqa: E501
        :type: str
        """

        self._from_category_id = from_category_id

    @property
    def to_category_id(self):
        """Gets the to_category_id of this ExpiredCategory.  # noqa: E501

        The unique identifier of the currently active eBay leaf category that has replaced the expired leaf category.<br><br><span class=\"tablenote\"><b>Note:</b> More than one <b>fromCategoryID</b> value may map into the same <b>toCategoryID</b> value, as multiple eBay categories may be consolidated into one new, expanded category.</span>  # noqa: E501

        :return: The to_category_id of this ExpiredCategory.  # noqa: E501
        :rtype: str
        """
        return self._to_category_id

    @to_category_id.setter
    def to_category_id(self, to_category_id):
        """Sets the to_category_id of this ExpiredCategory.

        The unique identifier of the currently active eBay leaf category that has replaced the expired leaf category.<br><br><span class=\"tablenote\"><b>Note:</b> More than one <b>fromCategoryID</b> value may map into the same <b>toCategoryID</b> value, as multiple eBay categories may be consolidated into one new, expanded category.</span>  # noqa: E501

        :param to_category_id: The to_category_id of this ExpiredCategory.  # noqa: E501
        :type: str
        """

        self._to_category_id = to_category_id

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
        if issubclass(ExpiredCategory, dict):
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
        if not isinstance(other, ExpiredCategory):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other