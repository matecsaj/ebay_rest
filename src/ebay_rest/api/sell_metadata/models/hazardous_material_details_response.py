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

class HazardousMaterialDetailsResponse(object):
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
        'signal_words': 'list[SignalWord]',
        'statements': 'list[HazardStatement]',
        'pictograms': 'list[Pictogram]'
    }

    attribute_map = {
        'signal_words': 'signalWords',
        'statements': 'statements',
        'pictograms': 'pictograms'
    }

    def __init__(self, signal_words=None, statements=None, pictograms=None):  # noqa: E501
        """HazardousMaterialDetailsResponse - a model defined in Swagger"""  # noqa: E501
        self._signal_words = None
        self._statements = None
        self._pictograms = None
        self.discriminator = None
        if signal_words is not None:
            self.signal_words = signal_words
        if statements is not None:
            self.statements = statements
        if pictograms is not None:
            self.pictograms = pictograms

    @property
    def signal_words(self):
        """Gets the signal_words of this HazardousMaterialDetailsResponse.  # noqa: E501

        This array contains available hazardous materials signal words for the specified marketplace.  # noqa: E501

        :return: The signal_words of this HazardousMaterialDetailsResponse.  # noqa: E501
        :rtype: list[SignalWord]
        """
        return self._signal_words

    @signal_words.setter
    def signal_words(self, signal_words):
        """Sets the signal_words of this HazardousMaterialDetailsResponse.

        This array contains available hazardous materials signal words for the specified marketplace.  # noqa: E501

        :param signal_words: The signal_words of this HazardousMaterialDetailsResponse.  # noqa: E501
        :type: list[SignalWord]
        """

        self._signal_words = signal_words

    @property
    def statements(self):
        """Gets the statements of this HazardousMaterialDetailsResponse.  # noqa: E501

        This array contains available hazardous materials hazard statements for the specified marketplace.  # noqa: E501

        :return: The statements of this HazardousMaterialDetailsResponse.  # noqa: E501
        :rtype: list[HazardStatement]
        """
        return self._statements

    @statements.setter
    def statements(self, statements):
        """Sets the statements of this HazardousMaterialDetailsResponse.

        This array contains available hazardous materials hazard statements for the specified marketplace.  # noqa: E501

        :param statements: The statements of this HazardousMaterialDetailsResponse.  # noqa: E501
        :type: list[HazardStatement]
        """

        self._statements = statements

    @property
    def pictograms(self):
        """Gets the pictograms of this HazardousMaterialDetailsResponse.  # noqa: E501

        This array contains available hazardous materials hazard pictograms for the specified marketplace.  # noqa: E501

        :return: The pictograms of this HazardousMaterialDetailsResponse.  # noqa: E501
        :rtype: list[Pictogram]
        """
        return self._pictograms

    @pictograms.setter
    def pictograms(self, pictograms):
        """Sets the pictograms of this HazardousMaterialDetailsResponse.

        This array contains available hazardous materials hazard pictograms for the specified marketplace.  # noqa: E501

        :param pictograms: The pictograms of this HazardousMaterialDetailsResponse.  # noqa: E501
        :type: list[Pictogram]
        """

        self._pictograms = pictograms

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
        if issubclass(HazardousMaterialDetailsResponse, dict):
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
        if not isinstance(other, HazardousMaterialDetailsResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
