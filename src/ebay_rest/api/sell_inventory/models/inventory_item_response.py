# coding: utf-8

"""
    Inventory API

    The Inventory API is used to create and manage inventory, and then to publish and manage this inventory on an eBay marketplace. There are also methods in this API that will convert eligible, active eBay listings into the Inventory API model.  # noqa: E501

    OpenAPI spec version: 1.18.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class InventoryItemResponse(object):
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
        'errors': 'list[Error]',
        'locale': 'str',
        'sku': 'str',
        'status_code': 'int',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'errors': 'errors',
        'locale': 'locale',
        'sku': 'sku',
        'status_code': 'statusCode',
        'warnings': 'warnings'
    }

    def __init__(self, errors=None, locale=None, sku=None, status_code=None, warnings=None):  # noqa: E501
        """InventoryItemResponse - a model defined in Swagger"""  # noqa: E501
        self._errors = None
        self._locale = None
        self._sku = None
        self._status_code = None
        self._warnings = None
        self.discriminator = None
        if errors is not None:
            self.errors = errors
        if locale is not None:
            self.locale = locale
        if sku is not None:
            self.sku = sku
        if status_code is not None:
            self.status_code = status_code
        if warnings is not None:
            self.warnings = warnings

    @property
    def errors(self):
        """Gets the errors of this InventoryItemResponse.  # noqa: E501

        This container will be returned if there were one or more errors associated with the creation or update to the inventory item record.  # noqa: E501

        :return: The errors of this InventoryItemResponse.  # noqa: E501
        :rtype: list[Error]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this InventoryItemResponse.

        This container will be returned if there were one or more errors associated with the creation or update to the inventory item record.  # noqa: E501

        :param errors: The errors of this InventoryItemResponse.  # noqa: E501
        :type: list[Error]
        """

        self._errors = errors

    @property
    def locale(self):
        """Gets the locale of this InventoryItemResponse.  # noqa: E501

        This field returns the natural language that was provided in the field values of the request payload (i.e., en_AU, en_GB or de_DE). For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:LocaleEnum'>eBay API documentation</a>  # noqa: E501

        :return: The locale of this InventoryItemResponse.  # noqa: E501
        :rtype: str
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """Sets the locale of this InventoryItemResponse.

        This field returns the natural language that was provided in the field values of the request payload (i.e., en_AU, en_GB or de_DE). For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:LocaleEnum'>eBay API documentation</a>  # noqa: E501

        :param locale: The locale of this InventoryItemResponse.  # noqa: E501
        :type: str
        """

        self._locale = locale

    @property
    def sku(self):
        """Gets the sku of this InventoryItemResponse.  # noqa: E501

        The seller-defined Stock-Keeping Unit (SKU) of the inventory item. The seller should have a unique SKU value for every product that they sell.  # noqa: E501

        :return: The sku of this InventoryItemResponse.  # noqa: E501
        :rtype: str
        """
        return self._sku

    @sku.setter
    def sku(self, sku):
        """Sets the sku of this InventoryItemResponse.

        The seller-defined Stock-Keeping Unit (SKU) of the inventory item. The seller should have a unique SKU value for every product that they sell.  # noqa: E501

        :param sku: The sku of this InventoryItemResponse.  # noqa: E501
        :type: str
        """

        self._sku = sku

    @property
    def status_code(self):
        """Gets the status_code of this InventoryItemResponse.  # noqa: E501

        The HTTP status code returned in this field indicates the success or failure of creating or updating the inventory item record for the inventory item indicated in the <strong>sku</strong> field. See the <strong>HTTP status codes</strong> table to see which each status code indicates.  # noqa: E501

        :return: The status_code of this InventoryItemResponse.  # noqa: E501
        :rtype: int
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        """Sets the status_code of this InventoryItemResponse.

        The HTTP status code returned in this field indicates the success or failure of creating or updating the inventory item record for the inventory item indicated in the <strong>sku</strong> field. See the <strong>HTTP status codes</strong> table to see which each status code indicates.  # noqa: E501

        :param status_code: The status_code of this InventoryItemResponse.  # noqa: E501
        :type: int
        """

        self._status_code = status_code

    @property
    def warnings(self):
        """Gets the warnings of this InventoryItemResponse.  # noqa: E501

        This container will be returned if there were one or more warnings associated with the creation or update to the inventory item record.  # noqa: E501

        :return: The warnings of this InventoryItemResponse.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this InventoryItemResponse.

        This container will be returned if there were one or more warnings associated with the creation or update to the inventory item record.  # noqa: E501

        :param warnings: The warnings of this InventoryItemResponse.  # noqa: E501
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
        if issubclass(InventoryItemResponse, dict):
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
        if not isinstance(other, InventoryItemResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
