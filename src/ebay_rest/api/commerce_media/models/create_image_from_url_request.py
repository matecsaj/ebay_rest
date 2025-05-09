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

class CreateImageFromUrlRequest(object):
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
        'image_url': 'str'
    }

    attribute_map = {
        'image_url': 'imageUrl'
    }

    def __init__(self, image_url=None):  # noqa: E501
        """CreateImageFromUrlRequest - a model defined in Swagger"""  # noqa: E501
        self._image_url = None
        self.discriminator = None
        if image_url is not None:
            self.image_url = image_url

    @property
    def image_url(self):
        """Gets the image_url of this CreateImageFromUrlRequest.  # noqa: E501

        The image URL of the self-hosted picture to upload to eBay Picture Services (EPS). In addition to the picture requirements in <a href=\"https://www.ebay.com/help/policies/listing-policies/picture-policy?id=4370\" target=\"_blank\">Picture policy</a>, the provided URL must be secured using HTTPS (HTTP is not permitted). For more information, see <a href=\"/api-docs/sell/static/inventory/managing-image-media.html#image-requirements\" target=\"_blank\">Image requirements</a>.  # noqa: E501

        :return: The image_url of this CreateImageFromUrlRequest.  # noqa: E501
        :rtype: str
        """
        return self._image_url

    @image_url.setter
    def image_url(self, image_url):
        """Sets the image_url of this CreateImageFromUrlRequest.

        The image URL of the self-hosted picture to upload to eBay Picture Services (EPS). In addition to the picture requirements in <a href=\"https://www.ebay.com/help/policies/listing-policies/picture-policy?id=4370\" target=\"_blank\">Picture policy</a>, the provided URL must be secured using HTTPS (HTTP is not permitted). For more information, see <a href=\"/api-docs/sell/static/inventory/managing-image-media.html#image-requirements\" target=\"_blank\">Image requirements</a>.  # noqa: E501

        :param image_url: The image_url of this CreateImageFromUrlRequest.  # noqa: E501
        :type: str
        """

        self._image_url = image_url

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
        if issubclass(CreateImageFromUrlRequest, dict):
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
        if not isinstance(other, CreateImageFromUrlRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
