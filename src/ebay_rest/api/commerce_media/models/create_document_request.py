# coding: utf-8

"""
    Media API

    The <b>Media API</b> lets sellers to create, upload, and retrieve files, including:<ul><li>videos</li><li>documents (for GPSR regulations)</li></ul>  # noqa: E501

    OpenAPI spec version: v1_beta.2.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class CreateDocumentRequest(object):
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
        'document_type': 'str',
        'languages': 'list[str]'
    }

    attribute_map = {
        'document_type': 'documentType',
        'languages': 'languages'
    }

    def __init__(self, document_type=None, languages=None):  # noqa: E501
        """CreateDocumentRequest - a model defined in Swagger"""  # noqa: E501
        self._document_type = None
        self._languages = None
        self.discriminator = None
        if document_type is not None:
            self.document_type = document_type
        if languages is not None:
            self.languages = languages

    @property
    def document_type(self):
        """Gets the document_type of this CreateDocumentRequest.  # noqa: E501

        The type of the document being uploaded. For example, a <code>USER_GUIDE_OR_MANUAL</code> or a <code>SAFETY_DATA_SHEET</code>. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/media/types/api:DocumentTypeEnum'>eBay API documentation</a>  # noqa: E501

        :return: The document_type of this CreateDocumentRequest.  # noqa: E501
        :rtype: str
        """
        return self._document_type

    @document_type.setter
    def document_type(self, document_type):
        """Sets the document_type of this CreateDocumentRequest.

        The type of the document being uploaded. For example, a <code>USER_GUIDE_OR_MANUAL</code> or a <code>SAFETY_DATA_SHEET</code>. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/media/types/api:DocumentTypeEnum'>eBay API documentation</a>  # noqa: E501

        :param document_type: The document_type of this CreateDocumentRequest.  # noqa: E501
        :type: str
        """

        self._document_type = document_type

    @property
    def languages(self):
        """Gets the languages of this CreateDocumentRequest.  # noqa: E501

        This array shows the language(s) used in the document.  # noqa: E501

        :return: The languages of this CreateDocumentRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._languages

    @languages.setter
    def languages(self, languages):
        """Sets the languages of this CreateDocumentRequest.

        This array shows the language(s) used in the document.  # noqa: E501

        :param languages: The languages of this CreateDocumentRequest.  # noqa: E501
        :type: list[str]
        """

        self._languages = languages

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
        if issubclass(CreateDocumentRequest, dict):
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
        if not isinstance(other, CreateDocumentRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other