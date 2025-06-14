# coding: utf-8

"""
    Metadata API

    The Metadata API has operations that retrieve configuration details pertaining to the different eBay marketplaces. In addition to marketplace information, the API also has operations that get information that helps sellers list items on eBay.  # noqa: E501

    OpenAPI spec version: v1.11.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ListingStructurePolicyResponse(object):
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
        'listing_structure_policies': 'list[ListingStructurePolicy]',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'listing_structure_policies': 'listingStructurePolicies',
        'warnings': 'warnings'
    }

    def __init__(self, listing_structure_policies=None, warnings=None):  # noqa: E501
        """ListingStructurePolicyResponse - a model defined in Swagger"""  # noqa: E501
        self._listing_structure_policies = None
        self._warnings = None
        self.discriminator = None
        if listing_structure_policies is not None:
            self.listing_structure_policies = listing_structure_policies
        if warnings is not None:
            self.warnings = warnings

    @property
    def listing_structure_policies(self):
        """Gets the listing_structure_policies of this ListingStructurePolicyResponse.  # noqa: E501

        Returns a list of category IDs plus a flag indicating whether or not each listed category supports item variations.  # noqa: E501

        :return: The listing_structure_policies of this ListingStructurePolicyResponse.  # noqa: E501
        :rtype: list[ListingStructurePolicy]
        """
        return self._listing_structure_policies

    @listing_structure_policies.setter
    def listing_structure_policies(self, listing_structure_policies):
        """Sets the listing_structure_policies of this ListingStructurePolicyResponse.

        Returns a list of category IDs plus a flag indicating whether or not each listed category supports item variations.  # noqa: E501

        :param listing_structure_policies: The listing_structure_policies of this ListingStructurePolicyResponse.  # noqa: E501
        :type: list[ListingStructurePolicy]
        """

        self._listing_structure_policies = listing_structure_policies

    @property
    def warnings(self):
        """Gets the warnings of this ListingStructurePolicyResponse.  # noqa: E501

        A list of the warnings that were generated as a result of the request. This field is not returned if no warnings were generated by the request.  # noqa: E501

        :return: The warnings of this ListingStructurePolicyResponse.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this ListingStructurePolicyResponse.

        A list of the warnings that were generated as a result of the request. This field is not returned if no warnings were generated by the request.  # noqa: E501

        :param warnings: The warnings of this ListingStructurePolicyResponse.  # noqa: E501
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
        if issubclass(ListingStructurePolicyResponse, dict):
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
        if not isinstance(other, ListingStructurePolicyResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
