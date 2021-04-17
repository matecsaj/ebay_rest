# coding: utf-8

"""
    Marketing API

    <p>The <i>Marketing API </i> offers two platforms that sellers can use to promote and advertise their products:</p> <ul><li><b>Promoted Listings</b> is an eBay ad service that lets sellers set up <i>ad campaigns </i> for the products they want to promote. eBay displays the ads in search results and in other marketing modules as <b>SPONSORED</b> listings. If an item in a Promoted Listings campaign sells, the seller is assessed a Promoted Listings fee, which is a seller-specified percentage applied to the sales price. For complete details, see <a href=\"/api-docs/sell/static/marketing/promoted-listings.html\">Promoted Listings</a>.</li>  <li><b>Promotions Manager</b> gives sellers a way to offer discounts on specific items as a way to attract buyers to their inventory. Sellers can set up discounts (such as \"20% off\" and other types of offers) on specific items or on an entire customer order. To further attract buyers, eBay prominently displays promotion <i>teasers</i> throughout buyer flows. For complete details, see <a href=\"/api-docs/sell/static/marketing/promotions-manager.html\">Promotions Manager</a>.</li></ul>  <p><b>Marketing reports</b>, on both the Promoted Listings and Promotions Manager platforms, give sellers information that shows the effectiveness of their marketing strategies. The data gives sellers the ability to review and fine tune their marketing efforts.</p> <p class=\"tablenote\"><b>Important!</b> Sellers must have an active eBay Store subscription, and they must accept the <b>Terms and Conditions</b> before they can make requests to these APIs in the Production environment. There are also site-specific listings requirements and restrictions associated with these marketing tools, as listed in the \"requirements and restrictions\" sections for <a href=\"/api-docs/sell/marketing/static/overview.html#PL-requirements\">Promoted Listings</a> and <a href=\"/api-docs/sell/marketing/static/overview.html#PM-requirements\">Promotions Manager</a>.</p> <p>The table below lists all the Marketing API calls grouped by resource.</p>  # noqa: E501

    OpenAPI spec version: v1.8.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class DiscountSpecification(object):
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
        'for_each_amount': 'Amount',
        'for_each_quantity': 'int',
        'min_amount': 'Amount',
        'min_quantity': 'int',
        'number_of_discounted_items': 'int'
    }

    attribute_map = {
        'for_each_amount': 'forEachAmount',
        'for_each_quantity': 'forEachQuantity',
        'min_amount': 'minAmount',
        'min_quantity': 'minQuantity',
        'number_of_discounted_items': 'numberOfDiscountedItems'
    }

    def __init__(self, for_each_amount=None, for_each_quantity=None, min_amount=None, min_quantity=None, number_of_discounted_items=None):  # noqa: E501
        """DiscountSpecification - a model defined in Swagger"""  # noqa: E501
        self._for_each_amount = None
        self._for_each_quantity = None
        self._min_amount = None
        self._min_quantity = None
        self._number_of_discounted_items = None
        self.discriminator = None
        if for_each_amount is not None:
            self.for_each_amount = for_each_amount
        if for_each_quantity is not None:
            self.for_each_quantity = for_each_quantity
        if min_amount is not None:
            self.min_amount = min_amount
        if min_quantity is not None:
            self.min_quantity = min_quantity
        if number_of_discounted_items is not None:
            self.number_of_discounted_items = number_of_discounted_items

    @property
    def for_each_amount(self):
        """Gets the for_each_amount of this DiscountSpecification.  # noqa: E501


        :return: The for_each_amount of this DiscountSpecification.  # noqa: E501
        :rtype: Amount
        """
        return self._for_each_amount

    @for_each_amount.setter
    def for_each_amount(self, for_each_amount):
        """Sets the for_each_amount of this DiscountSpecification.


        :param for_each_amount: The for_each_amount of this DiscountSpecification.  # noqa: E501
        :type: Amount
        """

        self._for_each_amount = for_each_amount

    @property
    def for_each_quantity(self):
        """Gets the for_each_quantity of this DiscountSpecification.  # noqa: E501

        The number of items that must be purchased in order to qualify for the discount. Valid values: &nbsp; 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, &nbsp; 12, 13, 14, 15, 16, 17, 18, 19 &nbsp; 20, 25, 50, 75, 100  # noqa: E501

        :return: The for_each_quantity of this DiscountSpecification.  # noqa: E501
        :rtype: int
        """
        return self._for_each_quantity

    @for_each_quantity.setter
    def for_each_quantity(self, for_each_quantity):
        """Sets the for_each_quantity of this DiscountSpecification.

        The number of items that must be purchased in order to qualify for the discount. Valid values: &nbsp; 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, &nbsp; 12, 13, 14, 15, 16, 17, 18, 19 &nbsp; 20, 25, 50, 75, 100  # noqa: E501

        :param for_each_quantity: The for_each_quantity of this DiscountSpecification.  # noqa: E501
        :type: int
        """

        self._for_each_quantity = for_each_quantity

    @property
    def min_amount(self):
        """Gets the min_amount of this DiscountSpecification.  # noqa: E501


        :return: The min_amount of this DiscountSpecification.  # noqa: E501
        :rtype: Amount
        """
        return self._min_amount

    @min_amount.setter
    def min_amount(self, min_amount):
        """Sets the min_amount of this DiscountSpecification.


        :param min_amount: The min_amount of this DiscountSpecification.  # noqa: E501
        :type: Amount
        """

        self._min_amount = min_amount

    @property
    def min_quantity(self):
        """Gets the min_quantity of this DiscountSpecification.  # noqa: E501

        The minimum quantity of promoted items that needs to be bought in order to qualify for the promotion's discount. Valid values: &nbsp; 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, &nbsp; 12, 13, 14, 15, 16, 17, 18, 19 &nbsp; 20, 25, 50, 75, 100  # noqa: E501

        :return: The min_quantity of this DiscountSpecification.  # noqa: E501
        :rtype: int
        """
        return self._min_quantity

    @min_quantity.setter
    def min_quantity(self, min_quantity):
        """Sets the min_quantity of this DiscountSpecification.

        The minimum quantity of promoted items that needs to be bought in order to qualify for the promotion's discount. Valid values: &nbsp; 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, &nbsp; 12, 13, 14, 15, 16, 17, 18, 19 &nbsp; 20, 25, 50, 75, 100  # noqa: E501

        :param min_quantity: The min_quantity of this DiscountSpecification.  # noqa: E501
        :type: int
        """

        self._min_quantity = min_quantity

    @property
    def number_of_discounted_items(self):
        """Gets the number_of_discounted_items of this DiscountSpecification.  # noqa: E501

        Use this field to configure &quot;Buy One Get One&quot; (or BOGO) promotions. You must couple this field with forEachQuantity and an amountOffItem or percentOffItem field to configure your BOGO promotion. This field is not valid with order-based promotions. The value of this field represents the number of items to be discounted when other promotion criteria is met. For example, when the buyer adds the number of items identified by the forEachQuantity value to their cart, they are then eligible to receive the stated discount from an additional number of like items (the number of which is identified by this field) when they add those items to their cart. To receive the discount, the buyer must purchase the number of items indicated by forEachQuantity plus the number indicated by this field. Valid values: &nbsp; 1, 2, 3, 4, 5, 6, 7, 8, 9, 10  # noqa: E501

        :return: The number_of_discounted_items of this DiscountSpecification.  # noqa: E501
        :rtype: int
        """
        return self._number_of_discounted_items

    @number_of_discounted_items.setter
    def number_of_discounted_items(self, number_of_discounted_items):
        """Sets the number_of_discounted_items of this DiscountSpecification.

        Use this field to configure &quot;Buy One Get One&quot; (or BOGO) promotions. You must couple this field with forEachQuantity and an amountOffItem or percentOffItem field to configure your BOGO promotion. This field is not valid with order-based promotions. The value of this field represents the number of items to be discounted when other promotion criteria is met. For example, when the buyer adds the number of items identified by the forEachQuantity value to their cart, they are then eligible to receive the stated discount from an additional number of like items (the number of which is identified by this field) when they add those items to their cart. To receive the discount, the buyer must purchase the number of items indicated by forEachQuantity plus the number indicated by this field. Valid values: &nbsp; 1, 2, 3, 4, 5, 6, 7, 8, 9, 10  # noqa: E501

        :param number_of_discounted_items: The number_of_discounted_items of this DiscountSpecification.  # noqa: E501
        :type: int
        """

        self._number_of_discounted_items = number_of_discounted_items

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
        if issubclass(DiscountSpecification, dict):
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
        if not isinstance(other, DiscountSpecification):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other