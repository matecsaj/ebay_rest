# coding: utf-8

"""
    Metadata API

    The Metadata API has operations that retrieve configuration details pertaining to the different eBay marketplaces. In addition to marketplace information, the API also has operations that get information that helps sellers list items on eBay.  # noqa: E501

    OpenAPI spec version: v1.8.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class RegulatoryPolicyResponse(object):
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
        'regulatory_policies': 'list[RegulatoryPolicy]',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'regulatory_policies': 'regulatoryPolicies',
        'warnings': 'warnings'
    }

    def __init__(self, regulatory_policies=None, warnings=None):  # noqa: E501
        """RegulatoryPolicyResponse - a model defined in Swagger"""  # noqa: E501
        self._regulatory_policies = None
        self._warnings = None
        self.discriminator = None
        if regulatory_policies is not None:
            self.regulatory_policies = regulatory_policies
        if warnings is not None:
            self.warnings = warnings

    @property
    def regulatory_policies(self):
        """Gets the regulatory_policies of this RegulatoryPolicyResponse.  # noqa: E501

        A list of eBay policies that define whether or not you must include required regulatory information for leaf categories on the given marketplace.  # noqa: E501

        :return: The regulatory_policies of this RegulatoryPolicyResponse.  # noqa: E501
        :rtype: list[RegulatoryPolicy]
        """
        return self._regulatory_policies

    @regulatory_policies.setter
    def regulatory_policies(self, regulatory_policies):
        """Sets the regulatory_policies of this RegulatoryPolicyResponse.

        A list of eBay policies that define whether or not you must include required regulatory information for leaf categories on the given marketplace.  # noqa: E501

        :param regulatory_policies: The regulatory_policies of this RegulatoryPolicyResponse.  # noqa: E501
        :type: list[RegulatoryPolicy]
        """

        self._regulatory_policies = regulatory_policies

    @property
    def warnings(self):
        """Gets the warnings of this RegulatoryPolicyResponse.  # noqa: E501

        A list of the warnings that were generated as a result of the request. This field is not returned if no warnings were generated by the request.  # noqa: E501

        :return: The warnings of this RegulatoryPolicyResponse.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this RegulatoryPolicyResponse.

        A list of the warnings that were generated as a result of the request. This field is not returned if no warnings were generated by the request.  # noqa: E501

        :param warnings: The warnings of this RegulatoryPolicyResponse.  # noqa: E501
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
        if issubclass(RegulatoryPolicyResponse, dict):
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
        if not isinstance(other, RegulatoryPolicyResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other