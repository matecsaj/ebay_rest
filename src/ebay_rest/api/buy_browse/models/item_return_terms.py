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

class ItemReturnTerms(object):
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
        'extended_holiday_returns_offered': 'bool',
        'refund_method': 'str',
        'restocking_fee_percentage': 'str',
        'return_instructions': 'str',
        'return_method': 'str',
        'return_period': 'TimeDuration',
        'returns_accepted': 'bool',
        'return_shipping_cost_payer': 'str'
    }

    attribute_map = {
        'extended_holiday_returns_offered': 'extendedHolidayReturnsOffered',
        'refund_method': 'refundMethod',
        'restocking_fee_percentage': 'restockingFeePercentage',
        'return_instructions': 'returnInstructions',
        'return_method': 'returnMethod',
        'return_period': 'returnPeriod',
        'returns_accepted': 'returnsAccepted',
        'return_shipping_cost_payer': 'returnShippingCostPayer'
    }

    def __init__(self, extended_holiday_returns_offered=None, refund_method=None, restocking_fee_percentage=None, return_instructions=None, return_method=None, return_period=None, returns_accepted=None, return_shipping_cost_payer=None):  # noqa: E501
        """ItemReturnTerms - a model defined in Swagger"""  # noqa: E501
        self._extended_holiday_returns_offered = None
        self._refund_method = None
        self._restocking_fee_percentage = None
        self._return_instructions = None
        self._return_method = None
        self._return_period = None
        self._returns_accepted = None
        self._return_shipping_cost_payer = None
        self.discriminator = None
        if extended_holiday_returns_offered is not None:
            self.extended_holiday_returns_offered = extended_holiday_returns_offered
        if refund_method is not None:
            self.refund_method = refund_method
        if restocking_fee_percentage is not None:
            self.restocking_fee_percentage = restocking_fee_percentage
        if return_instructions is not None:
            self.return_instructions = return_instructions
        if return_method is not None:
            self.return_method = return_method
        if return_period is not None:
            self.return_period = return_period
        if returns_accepted is not None:
            self.returns_accepted = returns_accepted
        if return_shipping_cost_payer is not None:
            self.return_shipping_cost_payer = return_shipping_cost_payer

    @property
    def extended_holiday_returns_offered(self):
        """Gets the extended_holiday_returns_offered of this ItemReturnTerms.  # noqa: E501

        This indicates if the seller has enabled the Extended Holiday Returns feature on the item. Extended Holiday Returns are only applicable during the US holiday season, and gives buyers extra time to return an item. This 'extra time' will typically extend beyond what is set through the <b> returnPeriod</b> value.  # noqa: E501

        :return: The extended_holiday_returns_offered of this ItemReturnTerms.  # noqa: E501
        :rtype: bool
        """
        return self._extended_holiday_returns_offered

    @extended_holiday_returns_offered.setter
    def extended_holiday_returns_offered(self, extended_holiday_returns_offered):
        """Sets the extended_holiday_returns_offered of this ItemReturnTerms.

        This indicates if the seller has enabled the Extended Holiday Returns feature on the item. Extended Holiday Returns are only applicable during the US holiday season, and gives buyers extra time to return an item. This 'extra time' will typically extend beyond what is set through the <b> returnPeriod</b> value.  # noqa: E501

        :param extended_holiday_returns_offered: The extended_holiday_returns_offered of this ItemReturnTerms.  # noqa: E501
        :type: bool
        """

        self._extended_holiday_returns_offered = extended_holiday_returns_offered

    @property
    def refund_method(self):
        """Gets the refund_method of this ItemReturnTerms.  # noqa: E501

        An enumeration value that indicates how a buyer is refunded when an item is returned. <br><br><b> Valid Values: </b> MONEY_BACK or MERCHANDISE_CREDIT  <br><br>Code so that your app gracefully handles any future changes to this list. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:RefundMethodEnum'>eBay API documentation</a>  # noqa: E501

        :return: The refund_method of this ItemReturnTerms.  # noqa: E501
        :rtype: str
        """
        return self._refund_method

    @refund_method.setter
    def refund_method(self, refund_method):
        """Sets the refund_method of this ItemReturnTerms.

        An enumeration value that indicates how a buyer is refunded when an item is returned. <br><br><b> Valid Values: </b> MONEY_BACK or MERCHANDISE_CREDIT  <br><br>Code so that your app gracefully handles any future changes to this list. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:RefundMethodEnum'>eBay API documentation</a>  # noqa: E501

        :param refund_method: The refund_method of this ItemReturnTerms.  # noqa: E501
        :type: str
        """

        self._refund_method = refund_method

    @property
    def restocking_fee_percentage(self):
        """Gets the restocking_fee_percentage of this ItemReturnTerms.  # noqa: E501

        This string field indicates the restocking fee percentage that the seller has set on the item. Sellers have the option of setting no restocking fee for an item, or they can set the percentage to 10, 15, or 20 percent. So, if the cost of the item was $100, and the restocking percentage was 20 percent, the buyer would be charged $20 to return that item, so instead of receiving a $100 refund, they would receive $80 due to the restocking fee.  # noqa: E501

        :return: The restocking_fee_percentage of this ItemReturnTerms.  # noqa: E501
        :rtype: str
        """
        return self._restocking_fee_percentage

    @restocking_fee_percentage.setter
    def restocking_fee_percentage(self, restocking_fee_percentage):
        """Sets the restocking_fee_percentage of this ItemReturnTerms.

        This string field indicates the restocking fee percentage that the seller has set on the item. Sellers have the option of setting no restocking fee for an item, or they can set the percentage to 10, 15, or 20 percent. So, if the cost of the item was $100, and the restocking percentage was 20 percent, the buyer would be charged $20 to return that item, so instead of receiving a $100 refund, they would receive $80 due to the restocking fee.  # noqa: E501

        :param restocking_fee_percentage: The restocking_fee_percentage of this ItemReturnTerms.  # noqa: E501
        :type: str
        """

        self._restocking_fee_percentage = restocking_fee_percentage

    @property
    def return_instructions(self):
        """Gets the return_instructions of this ItemReturnTerms.  # noqa: E501

        Text written by the seller describing what the buyer needs to do in order to return the item.  # noqa: E501

        :return: The return_instructions of this ItemReturnTerms.  # noqa: E501
        :rtype: str
        """
        return self._return_instructions

    @return_instructions.setter
    def return_instructions(self, return_instructions):
        """Sets the return_instructions of this ItemReturnTerms.

        Text written by the seller describing what the buyer needs to do in order to return the item.  # noqa: E501

        :param return_instructions: The return_instructions of this ItemReturnTerms.  # noqa: E501
        :type: str
        """

        self._return_instructions = return_instructions

    @property
    def return_method(self):
        """Gets the return_method of this ItemReturnTerms.  # noqa: E501

        An enumeration value that indicates the alternative methods for a full refund when an item is returned. This field is returned if the seller offers the buyer an item replacement or exchange instead of a monetary refund. <br><br><b> Valid Values: </b>  <ul><li><b> REPLACEMENT</b> -  Indicates that the buyer has the option of receiving money back for the returned item, or they can choose to have the seller replace the item with an identical item.</li>  <li><b> EXCHANGE</b> - Indicates that the buyer has the option of receiving money back for the returned item, or they can exchange the item for another similar item.</li></ul>  Code so that your app gracefully handles any future changes to this list. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:ReturnMethodEnum'>eBay API documentation</a>  # noqa: E501

        :return: The return_method of this ItemReturnTerms.  # noqa: E501
        :rtype: str
        """
        return self._return_method

    @return_method.setter
    def return_method(self, return_method):
        """Sets the return_method of this ItemReturnTerms.

        An enumeration value that indicates the alternative methods for a full refund when an item is returned. This field is returned if the seller offers the buyer an item replacement or exchange instead of a monetary refund. <br><br><b> Valid Values: </b>  <ul><li><b> REPLACEMENT</b> -  Indicates that the buyer has the option of receiving money back for the returned item, or they can choose to have the seller replace the item with an identical item.</li>  <li><b> EXCHANGE</b> - Indicates that the buyer has the option of receiving money back for the returned item, or they can exchange the item for another similar item.</li></ul>  Code so that your app gracefully handles any future changes to this list. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:ReturnMethodEnum'>eBay API documentation</a>  # noqa: E501

        :param return_method: The return_method of this ItemReturnTerms.  # noqa: E501
        :type: str
        """

        self._return_method = return_method

    @property
    def return_period(self):
        """Gets the return_period of this ItemReturnTerms.  # noqa: E501


        :return: The return_period of this ItemReturnTerms.  # noqa: E501
        :rtype: TimeDuration
        """
        return self._return_period

    @return_period.setter
    def return_period(self, return_period):
        """Sets the return_period of this ItemReturnTerms.


        :param return_period: The return_period of this ItemReturnTerms.  # noqa: E501
        :type: TimeDuration
        """

        self._return_period = return_period

    @property
    def returns_accepted(self):
        """Gets the returns_accepted of this ItemReturnTerms.  # noqa: E501

        Indicates whether the seller accepts returns for the item.  # noqa: E501

        :return: The returns_accepted of this ItemReturnTerms.  # noqa: E501
        :rtype: bool
        """
        return self._returns_accepted

    @returns_accepted.setter
    def returns_accepted(self, returns_accepted):
        """Sets the returns_accepted of this ItemReturnTerms.

        Indicates whether the seller accepts returns for the item.  # noqa: E501

        :param returns_accepted: The returns_accepted of this ItemReturnTerms.  # noqa: E501
        :type: bool
        """

        self._returns_accepted = returns_accepted

    @property
    def return_shipping_cost_payer(self):
        """Gets the return_shipping_cost_payer of this ItemReturnTerms.  # noqa: E501

        This enumeration value indicates whether the buyer or seller is responsible for return shipping costs when an item is returned. <br><br><b> Valid Values: </b> <ul><li><b> SELLER</b> - Indicates the seller will pay for the shipping costs to return the item.</li>  <li><b> BUYER</b> - Indicates the buyer will pay for the shipping costs to return the item.</li>  </ul>  Code so that your app gracefully handles any future changes to this list. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:ReturnShippingCostPayerEnum'>eBay API documentation</a>  # noqa: E501

        :return: The return_shipping_cost_payer of this ItemReturnTerms.  # noqa: E501
        :rtype: str
        """
        return self._return_shipping_cost_payer

    @return_shipping_cost_payer.setter
    def return_shipping_cost_payer(self, return_shipping_cost_payer):
        """Sets the return_shipping_cost_payer of this ItemReturnTerms.

        This enumeration value indicates whether the buyer or seller is responsible for return shipping costs when an item is returned. <br><br><b> Valid Values: </b> <ul><li><b> SELLER</b> - Indicates the seller will pay for the shipping costs to return the item.</li>  <li><b> BUYER</b> - Indicates the buyer will pay for the shipping costs to return the item.</li>  </ul>  Code so that your app gracefully handles any future changes to this list. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/buy/browse/types/gct:ReturnShippingCostPayerEnum'>eBay API documentation</a>  # noqa: E501

        :param return_shipping_cost_payer: The return_shipping_cost_payer of this ItemReturnTerms.  # noqa: E501
        :type: str
        """

        self._return_shipping_cost_payer = return_shipping_cost_payer

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
        if issubclass(ItemReturnTerms, dict):
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
        if not isinstance(other, ItemReturnTerms):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
