# coding: utf-8

"""
    Media API

    The <b>Media API</b> lets sellers to create, upload, and retrieve files, including:<ul><li>images</li><li>videos</li><li>documents (for GPSR regulations)</li></ul>  # noqa: E501

    OpenAPI spec version: v1_beta.4.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class CreateVideoRequest(object):
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
        'classification': 'list[str]',
        'description': 'str',
        'size': 'int',
        'title': 'str'
    }

    attribute_map = {
        'classification': 'classification',
        'description': 'description',
        'size': 'size',
        'title': 'title'
    }

    def __init__(self, classification=None, description=None, size=None, title=None):  # noqa: E501
        """CreateVideoRequest - a model defined in Swagger"""  # noqa: E501
        self._classification = None
        self._description = None
        self._size = None
        self._title = None
        self.discriminator = None
        if classification is not None:
            self.classification = classification
        if description is not None:
            self.description = description
        if size is not None:
            self.size = size
        if title is not None:
            self.title = title

    @property
    def classification(self):
        """Gets the classification of this CreateVideoRequest.  # noqa: E501

        The intended use for this video content. Currently, videos can only be added and associated with eBay listings, so the only supported value is <code>ITEM</code>.  # noqa: E501

        :return: The classification of this CreateVideoRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._classification

    @classification.setter
    def classification(self, classification):
        """Sets the classification of this CreateVideoRequest.

        The intended use for this video content. Currently, videos can only be added and associated with eBay listings, so the only supported value is <code>ITEM</code>.  # noqa: E501

        :param classification: The classification of this CreateVideoRequest.  # noqa: E501
        :type: list[str]
        """

        self._classification = classification

    @property
    def description(self):
        """Gets the description of this CreateVideoRequest.  # noqa: E501

        The description of the video.  # noqa: E501

        :return: The description of this CreateVideoRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateVideoRequest.

        The description of the video.  # noqa: E501

        :param description: The description of this CreateVideoRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def size(self):
        """Gets the size of this CreateVideoRequest.  # noqa: E501

        The size, in bytes, of the video content. <br><br><b>Max:</b> 157,286,400 bytes  # noqa: E501

        :return: The size of this CreateVideoRequest.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this CreateVideoRequest.

        The size, in bytes, of the video content. <br><br><b>Max:</b> 157,286,400 bytes  # noqa: E501

        :param size: The size of this CreateVideoRequest.  # noqa: E501
        :type: int
        """

        self._size = size

    @property
    def title(self):
        """Gets the title of this CreateVideoRequest.  # noqa: E501

        The title of the video.  # noqa: E501

        :return: The title of this CreateVideoRequest.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this CreateVideoRequest.

        The title of the video.  # noqa: E501

        :param title: The title of this CreateVideoRequest.  # noqa: E501
        :type: str
        """

        self._title = title

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
        if issubclass(CreateVideoRequest, dict):
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
        if not isinstance(other, CreateVideoRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
