# coding: utf-8

"""
    Translation API

    This API allows 3rd party developers to translate item titles.  # noqa: E501

    OpenAPI spec version: v1_beta.1.6
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class TranslateRequest(object):
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
        '_from': 'str',
        'text': 'list[str]',
        'to': 'str',
        'translation_context': 'str'
    }

    attribute_map = {
        '_from': 'from',
        'text': 'text',
        'to': 'to',
        'translation_context': 'translationContext'
    }

    def __init__(self, _from=None, text=None, to=None, translation_context=None):  # noqa: E501
        """TranslateRequest - a model defined in Swagger"""  # noqa: E501
        self.__from = None
        self._text = None
        self._to = None
        self._translation_context = None
        self.discriminator = None
        if _from is not None:
            self._from = _from
        if text is not None:
            self.text = text
        if to is not None:
            self.to = to
        if translation_context is not None:
            self.translation_context = translation_context

    @property
    def _from(self):
        """Gets the _from of this TranslateRequest.  # noqa: E501

        The language of the input text to be translated. Not all <b>LanguageEnum</b> values are supported in this field. For a full list of supported language pairings, see the Supported languages table in the <a href=\"/api-docs/commerce/translation/overview.html#supported-languages\">API Overview</a> page. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/translation/types/api:LanguageEnum'>eBay API documentation</a>  # noqa: E501

        :return: The _from of this TranslateRequest.  # noqa: E501
        :rtype: str
        """
        return self.__from

    @_from.setter
    def _from(self, _from):
        """Sets the _from of this TranslateRequest.

        The language of the input text to be translated. Not all <b>LanguageEnum</b> values are supported in this field. For a full list of supported language pairings, see the Supported languages table in the <a href=\"/api-docs/commerce/translation/overview.html#supported-languages\">API Overview</a> page. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/translation/types/api:LanguageEnum'>eBay API documentation</a>  # noqa: E501

        :param _from: The _from of this TranslateRequest.  # noqa: E501
        :type: str
        """

        self.__from = _from

    @property
    def text(self):
        """Gets the text of this TranslateRequest.  # noqa: E501

        The input text to translate. The maximum number of characters permitted is determined by the <b>translationContext</b> value:<ul><li><code>ITEM_TITLE</code>: 1000 characters maximum</li><li><code>ITEM_DESCRIPTION</code>: 20,000 characters maximum.<br><span class=\"tablenote\"><b>Note:</b> When translating <code>ITEM_DESCRIPTION</code> text, HTML/CSS markup and links can be included and will not count toward this 20,000 character limit.</span></li></ul><span class=\"tablenote\"><b>Note:</b> Currently, only one input string can be translated per API call. Support for multiple continuous text strings is expected in the future.</span>  # noqa: E501

        :return: The text of this TranslateRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this TranslateRequest.

        The input text to translate. The maximum number of characters permitted is determined by the <b>translationContext</b> value:<ul><li><code>ITEM_TITLE</code>: 1000 characters maximum</li><li><code>ITEM_DESCRIPTION</code>: 20,000 characters maximum.<br><span class=\"tablenote\"><b>Note:</b> When translating <code>ITEM_DESCRIPTION</code> text, HTML/CSS markup and links can be included and will not count toward this 20,000 character limit.</span></li></ul><span class=\"tablenote\"><b>Note:</b> Currently, only one input string can be translated per API call. Support for multiple continuous text strings is expected in the future.</span>  # noqa: E501

        :param text: The text of this TranslateRequest.  # noqa: E501
        :type: list[str]
        """

        self._text = text

    @property
    def to(self):
        """Gets the to of this TranslateRequest.  # noqa: E501

        The target language for the translation of the input text. Not all <b>LanguageEnum</b> values are supported in this field. For a full list of supported language pairings, see the Supported languages table in the <a href=\"/api-docs/commerce/translation/overview.html#supported-languages\">API Overview</a> page. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/translation/types/api:LanguageEnum'>eBay API documentation</a>  # noqa: E501

        :return: The to of this TranslateRequest.  # noqa: E501
        :rtype: str
        """
        return self._to

    @to.setter
    def to(self, to):
        """Sets the to of this TranslateRequest.

        The target language for the translation of the input text. Not all <b>LanguageEnum</b> values are supported in this field. For a full list of supported language pairings, see the Supported languages table in the <a href=\"/api-docs/commerce/translation/overview.html#supported-languages\">API Overview</a> page. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/translation/types/api:LanguageEnum'>eBay API documentation</a>  # noqa: E501

        :param to: The to of this TranslateRequest.  # noqa: E501
        :type: str
        """

        self._to = to

    @property
    def translation_context(self):
        """Gets the translation_context of this TranslateRequest.  # noqa: E501

        Input the listing entity to be translated.<br><br><b>Valid Values:</b> <code>ITEM_TITLE</code> and <code>ITEM_DESCRIPTION</code></p> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/translation/types/api:TranslationContextEnum'>eBay API documentation</a>  # noqa: E501

        :return: The translation_context of this TranslateRequest.  # noqa: E501
        :rtype: str
        """
        return self._translation_context

    @translation_context.setter
    def translation_context(self, translation_context):
        """Sets the translation_context of this TranslateRequest.

        Input the listing entity to be translated.<br><br><b>Valid Values:</b> <code>ITEM_TITLE</code> and <code>ITEM_DESCRIPTION</code></p> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/translation/types/api:TranslationContextEnum'>eBay API documentation</a>  # noqa: E501

        :param translation_context: The translation_context of this TranslateRequest.  # noqa: E501
        :type: str
        """

        self._translation_context = translation_context

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
        if issubclass(TranslateRequest, dict):
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
        if not isinstance(other, TranslateRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
