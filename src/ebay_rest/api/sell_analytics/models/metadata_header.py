# coding: utf-8

"""
    Analytics API

    The <i>Analytics API</i> provides data and information about a seller and their eBay business.  <br><br>The resources and methods in this API let sellers review information on their listing performance, metrics on their customer service performance, and details on their eBay seller performance rating.  <br><br>The three resources in the Analytics API provide the following data and information: <ul><li><b>Customer Service Metric</b> &ndash; Returns benchmark data and a metric rating pertaining to a seller's customer service performance as compared to other seller's in the same peer group.</li> <li><b>Traffic Report</b> &ndash; Returns data and information that shows how buyers are engaging with a seller's listings.</li> <li><b>Seller Standards Profile</b> &ndash; Returns information pertaining to a seller's profile rating.</li></ul> Sellers can use the data and information returned by the various Analytics API methods to determine where they can make improvements to increase sales and how they might improve their seller status as viewed by eBay buyers.  <br><br>For details on using this API, see <a href=\"/api-docs/sell/static/performance/analyzing-performance.html\" title=\"Selling Integration Guide\">Analyzing seller performance</a>.  # noqa: E501

    OpenAPI spec version: 1.3.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class MetadataHeader(object):
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
        'key': 'str',
        'metadata_keys': 'list[Definition]'
    }

    attribute_map = {
        'key': 'key',
        'metadata_keys': 'metadataKeys'
    }

    def __init__(self, key=None, metadata_keys=None):  # noqa: E501
        """MetadataHeader - a model defined in Swagger"""  # noqa: E501
        self._key = None
        self._metadata_keys = None
        self.discriminator = None
        if key is not None:
            self.key = key
        if metadata_keys is not None:
            self.metadata_keys = metadata_keys

    @property
    def key(self):
        """Gets the key of this MetadataHeader.  # noqa: E501

        The key value used for the report. <br><br>For example: <code>\"key\": \"LISTING_ID\"</code>  # noqa: E501

        :return: The key of this MetadataHeader.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this MetadataHeader.

        The key value used for the report. <br><br>For example: <code>\"key\": \"LISTING_ID\"</code>  # noqa: E501

        :param key: The key of this MetadataHeader.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def metadata_keys(self):
        """Gets the metadata_keys of this MetadataHeader.  # noqa: E501

        The list of dimension key values used for the report header. Each list element contains the key name, its data type, and its localized name.  <br><br>For example: <p><code>\"metadataKeys\": [<br>&nbsp;&nbsp;\"key\": \"LISTING_TITLE\",<br>&nbsp;&nbsp;\"localizedName\": \"Listing title\",<br>&nbsp;&nbsp;\"dataType\": \"STRING\"</code></p>  # noqa: E501

        :return: The metadata_keys of this MetadataHeader.  # noqa: E501
        :rtype: list[Definition]
        """
        return self._metadata_keys

    @metadata_keys.setter
    def metadata_keys(self, metadata_keys):
        """Sets the metadata_keys of this MetadataHeader.

        The list of dimension key values used for the report header. Each list element contains the key name, its data type, and its localized name.  <br><br>For example: <p><code>\"metadataKeys\": [<br>&nbsp;&nbsp;\"key\": \"LISTING_TITLE\",<br>&nbsp;&nbsp;\"localizedName\": \"Listing title\",<br>&nbsp;&nbsp;\"dataType\": \"STRING\"</code></p>  # noqa: E501

        :param metadata_keys: The metadata_keys of this MetadataHeader.  # noqa: E501
        :type: list[Definition]
        """

        self._metadata_keys = metadata_keys

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
        if issubclass(MetadataHeader, dict):
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
        if not isinstance(other, MetadataHeader):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
