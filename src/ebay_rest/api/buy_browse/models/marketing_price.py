# coding: utf-8

"""
    Browse API

    The Browse API has the following resources:<ul><li><b>item_summary:</b><br>Allows shoppers to search for specific items by keyword, GTIN, category, charity, product, image, or item aspects and refine the results by using filters, such as aspects, compatibility, and fields values, or UI parameters.</li><li><b>item:</b><br>Allows shoppers to retrieve the details of a specific item or all items in an item group, which is an item with variations such as color and size and check if a product is compatible with the specified item, such as if a specific car is compatible with a specific part.<br><br>This resource also provides a bridge between the eBay legacy APIs, such as the <a href=\"/api-docs/user-guides/static/finding-user-guide-landing.html\" target=\"_blank\">Finding</b>, and the RESTful APIs, which use different formats for the item IDs.</li></ul>The <b>item_summary</b>, <b>search_by_image</b>, and <b>item</b> resource calls require an <a href=\"/api-docs/static/oauth-client-credentials-grant.html\" target=\"_blank\">Application access token</a>.  # noqa: E501

    OpenAPI spec version: v1.20.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class MarketingPrice(object):
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
        'discount_amount': 'ConvertedAmount',
        'discount_percentage': 'str',
        'original_price': 'ConvertedAmount',
        'price_treatment': 'str'
    }

    attribute_map = {
        'discount_amount': 'discountAmount',
        'discount_percentage': 'discountPercentage',
        'original_price': 'originalPrice',
        'price_treatment': 'priceTreatment'
    }

    def __init__(self, discount_amount=None, discount_percentage=None, original_price=None, price_treatment=None):  # noqa: E501
        """MarketingPrice - a model defined in Swagger"""  # noqa: E501
        self._discount_amount = None
        self._discount_percentage = None
        self._original_price = None
        self._price_treatment = None
        self.discriminator = None
        if discount_amount is not None:
            self.discount_amount = discount_amount
        if discount_percentage is not None:
            self.discount_percentage = discount_percentage
        if original_price is not None:
            self.original_price = original_price
        if price_treatment is not None:
            self.price_treatment = price_treatment

    @property
    def discount_amount(self):
        """Gets the discount_amount of this MarketingPrice.  # noqa: E501


        :return: The discount_amount of this MarketingPrice.  # noqa: E501
        :rtype: ConvertedAmount
        """
        return self._discount_amount

    @discount_amount.setter
    def discount_amount(self, discount_amount):
        """Sets the discount_amount of this MarketingPrice.


        :param discount_amount: The discount_amount of this MarketingPrice.  # noqa: E501
        :type: ConvertedAmount
        """

        self._discount_amount = discount_amount

    @property
    def discount_percentage(self):
        """Gets the discount_percentage of this MarketingPrice.  # noqa: E501

        This field expresses the percentage of the seller discount based on the value in the <code>originalPrice</code> container.  # noqa: E501

        :return: The discount_percentage of this MarketingPrice.  # noqa: E501
        :rtype: str
        """
        return self._discount_percentage

    @discount_percentage.setter
    def discount_percentage(self, discount_percentage):
        """Sets the discount_percentage of this MarketingPrice.

        This field expresses the percentage of the seller discount based on the value in the <code>originalPrice</code> container.  # noqa: E501

        :param discount_percentage: The discount_percentage of this MarketingPrice.  # noqa: E501
        :type: str
        """

        self._discount_percentage = discount_percentage

    @property
    def original_price(self):
        """Gets the original_price of this MarketingPrice.  # noqa: E501


        :return: The original_price of this MarketingPrice.  # noqa: E501
        :rtype: ConvertedAmount
        """
        return self._original_price

    @original_price.setter
    def original_price(self, original_price):
        """Sets the original_price of this MarketingPrice.


        :param original_price: The original_price of this MarketingPrice.  # noqa: E501
        :type: ConvertedAmount
        """

        self._original_price = original_price

    @property
    def price_treatment(self):
        """Gets the price_treatment of this MarketingPrice.  # noqa: E501

        Indicates the pricing treatment (discount) that was applied to the price of the item.<br><br><span class=\"tablenote\"><b>Note:</b> The pricing treatment affects the way and where the discounted price can be displayed.</span> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:PriceTreatmentEnum'>eBay API documentation</a>  # noqa: E501

        :return: The price_treatment of this MarketingPrice.  # noqa: E501
        :rtype: str
        """
        return self._price_treatment

    @price_treatment.setter
    def price_treatment(self, price_treatment):
        """Sets the price_treatment of this MarketingPrice.

        Indicates the pricing treatment (discount) that was applied to the price of the item.<br><br><span class=\"tablenote\"><b>Note:</b> The pricing treatment affects the way and where the discounted price can be displayed.</span> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:PriceTreatmentEnum'>eBay API documentation</a>  # noqa: E501

        :param price_treatment: The price_treatment of this MarketingPrice.  # noqa: E501
        :type: str
        """

        self._price_treatment = price_treatment

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
        if issubclass(MarketingPrice, dict):
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
        if not isinstance(other, MarketingPrice):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
