# coding: utf-8

"""
    Account v2 API

    This API allows sellers to retrieve and manage their custom shipping rate tables. In addition, this API also provides sellers in mainland China methods to configure split-payouts between two separate payment instruments.  # noqa: E501

    OpenAPI spec version: 2.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Rate(object):
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
        'additional_cost': 'Amount',
        'rate_id': 'str',
        'shipping_category': 'str',
        'shipping_cost': 'Amount',
        'shipping_region_names': 'list[str]',
        'shipping_service_code': 'str'
    }

    attribute_map = {
        'additional_cost': 'additionalCost',
        'rate_id': 'rateId',
        'shipping_category': 'shippingCategory',
        'shipping_cost': 'shippingCost',
        'shipping_region_names': 'shippingRegionNames',
        'shipping_service_code': 'shippingServiceCode'
    }

    def __init__(self, additional_cost=None, rate_id=None, shipping_category=None, shipping_cost=None, shipping_region_names=None, shipping_service_code=None):  # noqa: E501
        """Rate - a model defined in Swagger"""  # noqa: E501
        self._additional_cost = None
        self._rate_id = None
        self._shipping_category = None
        self._shipping_cost = None
        self._shipping_region_names = None
        self._shipping_service_code = None
        self.discriminator = None
        if additional_cost is not None:
            self.additional_cost = additional_cost
        if rate_id is not None:
            self.rate_id = rate_id
        if shipping_category is not None:
            self.shipping_category = shipping_category
        if shipping_cost is not None:
            self.shipping_cost = shipping_cost
        if shipping_region_names is not None:
            self.shipping_region_names = shipping_region_names
        if shipping_service_code is not None:
            self.shipping_service_code = shipping_service_code

    @property
    def additional_cost(self):
        """Gets the additional_cost of this Rate.  # noqa: E501


        :return: The additional_cost of this Rate.  # noqa: E501
        :rtype: Amount
        """
        return self._additional_cost

    @additional_cost.setter
    def additional_cost(self, additional_cost):
        """Sets the additional_cost of this Rate.


        :param additional_cost: The additional_cost of this Rate.  # noqa: E501
        :type: Amount
        """

        self._additional_cost = additional_cost

    @property
    def rate_id(self):
        """Gets the rate_id of this Rate.  # noqa: E501

        The unique identifier for rate information.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> This is a string that is automatically assigned by the system when a rate object is created.</span>  # noqa: E501

        :return: The rate_id of this Rate.  # noqa: E501
        :rtype: str
        """
        return self._rate_id

    @rate_id.setter
    def rate_id(self, rate_id):
        """Sets the rate_id of this Rate.

        The unique identifier for rate information.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> This is a string that is automatically assigned by the system when a rate object is created.</span>  # noqa: E501

        :param rate_id: The rate_id of this Rate.  # noqa: E501
        :type: str
        """

        self._rate_id = rate_id

    @property
    def shipping_category(self):
        """Gets the shipping_category of this Rate.  # noqa: E501

        Indicates the level of shipping service to which the shipping rate information applies.<br/><br/>Available shipping categories are:<ul><li><b>ONE_DAY</b>: <i>This option is not supported when <b>shippingOptionType</b> is INTERNATIONAL.</i> </li><li><b>EXPEDITED</b></li><li><b>STANDARD</b></li><li><b>ECONOMY</b></li><li><b>EXPRESS</b>: <i>This option is supported only when <b>MarketplaceId</b> is <code>EBAY_DE</code> (Germany)</i></li></ul> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/account/types/api:ShippingCategoryEnum'>eBay API documentation</a>  # noqa: E501

        :return: The shipping_category of this Rate.  # noqa: E501
        :rtype: str
        """
        return self._shipping_category

    @shipping_category.setter
    def shipping_category(self, shipping_category):
        """Sets the shipping_category of this Rate.

        Indicates the level of shipping service to which the shipping rate information applies.<br/><br/>Available shipping categories are:<ul><li><b>ONE_DAY</b>: <i>This option is not supported when <b>shippingOptionType</b> is INTERNATIONAL.</i> </li><li><b>EXPEDITED</b></li><li><b>STANDARD</b></li><li><b>ECONOMY</b></li><li><b>EXPRESS</b>: <i>This option is supported only when <b>MarketplaceId</b> is <code>EBAY_DE</code> (Germany)</i></li></ul> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/account/types/api:ShippingCategoryEnum'>eBay API documentation</a>  # noqa: E501

        :param shipping_category: The shipping_category of this Rate.  # noqa: E501
        :type: str
        """

        self._shipping_category = shipping_category

    @property
    def shipping_cost(self):
        """Gets the shipping_cost of this Rate.  # noqa: E501


        :return: The shipping_cost of this Rate.  # noqa: E501
        :rtype: Amount
        """
        return self._shipping_cost

    @shipping_cost.setter
    def shipping_cost(self, shipping_cost):
        """Sets the shipping_cost of this Rate.


        :param shipping_cost: The shipping_cost of this Rate.  # noqa: E501
        :type: Amount
        """

        self._shipping_cost = shipping_cost

    @property
    def shipping_region_names(self):
        """Gets the shipping_region_names of this Rate.  # noqa: E501

        An array of Region names to which the shipping rate information applies.<br/><br/>Returned values may be:<ul><li>Geographical Regions (e.g., <code>Worldwide</code>, <code>Europe</code>, and <code>Middle East</code>)</li><li>Individual countries identified by a two-letter code such as <code>US</code> (United States), <code>CA</code> (Canada), and <code>GB</code> (United Kingdom)</li><li>US states and/or Canadian provinces identified by a two-letter code such as <code>NY</code> (New York) or <code>SK</code> (Saskatchewan)</li><li>Domestic Regions such as <code>AK/HI</code> (Alaska/Hawaii)</li></ul>  # noqa: E501

        :return: The shipping_region_names of this Rate.  # noqa: E501
        :rtype: list[str]
        """
        return self._shipping_region_names

    @shipping_region_names.setter
    def shipping_region_names(self, shipping_region_names):
        """Sets the shipping_region_names of this Rate.

        An array of Region names to which the shipping rate information applies.<br/><br/>Returned values may be:<ul><li>Geographical Regions (e.g., <code>Worldwide</code>, <code>Europe</code>, and <code>Middle East</code>)</li><li>Individual countries identified by a two-letter code such as <code>US</code> (United States), <code>CA</code> (Canada), and <code>GB</code> (United Kingdom)</li><li>US states and/or Canadian provinces identified by a two-letter code such as <code>NY</code> (New York) or <code>SK</code> (Saskatchewan)</li><li>Domestic Regions such as <code>AK/HI</code> (Alaska/Hawaii)</li></ul>  # noqa: E501

        :param shipping_region_names: The shipping_region_names of this Rate.  # noqa: E501
        :type: list[str]
        """

        self._shipping_region_names = shipping_region_names

    @property
    def shipping_service_code(self):
        """Gets the shipping_service_code of this Rate.  # noqa: E501

        An enum value that indicates the shipping service used for the specified shipping rate. These enum values align with <b>ShippingService</b> metadata returned by a <b>GeteBayDetails</b> call with <b>DetailName</b> set to <code>shippingServiceDetails</code>.  # noqa: E501

        :return: The shipping_service_code of this Rate.  # noqa: E501
        :rtype: str
        """
        return self._shipping_service_code

    @shipping_service_code.setter
    def shipping_service_code(self, shipping_service_code):
        """Sets the shipping_service_code of this Rate.

        An enum value that indicates the shipping service used for the specified shipping rate. These enum values align with <b>ShippingService</b> metadata returned by a <b>GeteBayDetails</b> call with <b>DetailName</b> set to <code>shippingServiceDetails</code>.  # noqa: E501

        :param shipping_service_code: The shipping_service_code of this Rate.  # noqa: E501
        :type: str
        """

        self._shipping_service_code = shipping_service_code

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
        if issubclass(Rate, dict):
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
        if not isinstance(other, Rate):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
