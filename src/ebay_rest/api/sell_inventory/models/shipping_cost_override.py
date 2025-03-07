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

class ShippingCostOverride(object):
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
        'additional_shipping_cost': 'Amount',
        'priority': 'int',
        'shipping_cost': 'Amount',
        'shipping_service_type': 'str',
        'surcharge': 'Amount'
    }

    attribute_map = {
        'additional_shipping_cost': 'additionalShippingCost',
        'priority': 'priority',
        'shipping_cost': 'shippingCost',
        'shipping_service_type': 'shippingServiceType',
        'surcharge': 'surcharge'
    }

    def __init__(self, additional_shipping_cost=None, priority=None, shipping_cost=None, shipping_service_type=None, surcharge=None):  # noqa: E501
        """ShippingCostOverride - a model defined in Swagger"""  # noqa: E501
        self._additional_shipping_cost = None
        self._priority = None
        self._shipping_cost = None
        self._shipping_service_type = None
        self._surcharge = None
        self.discriminator = None
        if additional_shipping_cost is not None:
            self.additional_shipping_cost = additional_shipping_cost
        if priority is not None:
            self.priority = priority
        if shipping_cost is not None:
            self.shipping_cost = shipping_cost
        if shipping_service_type is not None:
            self.shipping_service_type = shipping_service_type
        if surcharge is not None:
            self.surcharge = surcharge

    @property
    def additional_shipping_cost(self):
        """Gets the additional_shipping_cost of this ShippingCostOverride.  # noqa: E501


        :return: The additional_shipping_cost of this ShippingCostOverride.  # noqa: E501
        :rtype: Amount
        """
        return self._additional_shipping_cost

    @additional_shipping_cost.setter
    def additional_shipping_cost(self, additional_shipping_cost):
        """Sets the additional_shipping_cost of this ShippingCostOverride.


        :param additional_shipping_cost: The additional_shipping_cost of this ShippingCostOverride.  # noqa: E501
        :type: Amount
        """

        self._additional_shipping_cost = additional_shipping_cost

    @property
    def priority(self):
        """Gets the priority of this ShippingCostOverride.  # noqa: E501

        The integer value input into this field, along with the <strong>shippingServiceType</strong> value, sets which domestic or international shipping service option in the fulfillment policy will be modified with updated shipping costs. Specifically, the <strong>shippingCostOverrides.shippingServiceType</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.optionType</strong> value in a fulfillment listing policy, and the <strong>shippingCostOverrides.priority</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.shippingServices.sortOrderId</strong> value in a fulfillment listing policy.<br><br>This field is always required when overriding the shipping costs of a shipping service option, and will be always be returned for each shipping service option whose costs are being overridden.  # noqa: E501

        :return: The priority of this ShippingCostOverride.  # noqa: E501
        :rtype: int
        """
        return self._priority

    @priority.setter
    def priority(self, priority):
        """Sets the priority of this ShippingCostOverride.

        The integer value input into this field, along with the <strong>shippingServiceType</strong> value, sets which domestic or international shipping service option in the fulfillment policy will be modified with updated shipping costs. Specifically, the <strong>shippingCostOverrides.shippingServiceType</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.optionType</strong> value in a fulfillment listing policy, and the <strong>shippingCostOverrides.priority</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.shippingServices.sortOrderId</strong> value in a fulfillment listing policy.<br><br>This field is always required when overriding the shipping costs of a shipping service option, and will be always be returned for each shipping service option whose costs are being overridden.  # noqa: E501

        :param priority: The priority of this ShippingCostOverride.  # noqa: E501
        :type: int
        """

        self._priority = priority

    @property
    def shipping_cost(self):
        """Gets the shipping_cost of this ShippingCostOverride.  # noqa: E501


        :return: The shipping_cost of this ShippingCostOverride.  # noqa: E501
        :rtype: Amount
        """
        return self._shipping_cost

    @shipping_cost.setter
    def shipping_cost(self, shipping_cost):
        """Sets the shipping_cost of this ShippingCostOverride.


        :param shipping_cost: The shipping_cost of this ShippingCostOverride.  # noqa: E501
        :type: Amount
        """

        self._shipping_cost = shipping_cost

    @property
    def shipping_service_type(self):
        """Gets the shipping_service_type of this ShippingCostOverride.  # noqa: E501

        This enumerated value indicates whether the shipping service specified in the <strong>priority</strong> field is a domestic or an international shipping service option. To override the shipping costs for a specific domestic shipping service in the fulfillment listing policy, this field should be set to <code>DOMESTIC</code>, and to override the shipping costs for each international shipping service, this field should be set to <code>INTERNATIONAL</code>. This value, along with <strong>priority</strong> value, sets which domestic or international shipping service option in the fulfillment policy that will be modified with updated shipping costs. Specifically, the <strong>shippingCostOverrides.shippingServiceType</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.optionType</strong> value in a fulfillment listing policy, and the <strong>shippingCostOverrides.priority</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.shippingServices.sortOrderId</strong> value in a fulfillment listing policy.<br><br>This field is always required when overriding the shipping costs of a shipping service option, and will be always be returned for each shipping service option whose costs are being overridden. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:ShippingServiceTypeEnum'>eBay API documentation</a>  # noqa: E501

        :return: The shipping_service_type of this ShippingCostOverride.  # noqa: E501
        :rtype: str
        """
        return self._shipping_service_type

    @shipping_service_type.setter
    def shipping_service_type(self, shipping_service_type):
        """Sets the shipping_service_type of this ShippingCostOverride.

        This enumerated value indicates whether the shipping service specified in the <strong>priority</strong> field is a domestic or an international shipping service option. To override the shipping costs for a specific domestic shipping service in the fulfillment listing policy, this field should be set to <code>DOMESTIC</code>, and to override the shipping costs for each international shipping service, this field should be set to <code>INTERNATIONAL</code>. This value, along with <strong>priority</strong> value, sets which domestic or international shipping service option in the fulfillment policy that will be modified with updated shipping costs. Specifically, the <strong>shippingCostOverrides.shippingServiceType</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.optionType</strong> value in a fulfillment listing policy, and the <strong>shippingCostOverrides.priority</strong> value in a <strong>createOffer</strong> or <strong>updateOffer</strong> call must match the <strong>shippingOptions.shippingServices.sortOrderId</strong> value in a fulfillment listing policy.<br><br>This field is always required when overriding the shipping costs of a shipping service option, and will be always be returned for each shipping service option whose costs are being overridden. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:ShippingServiceTypeEnum'>eBay API documentation</a>  # noqa: E501

        :param shipping_service_type: The shipping_service_type of this ShippingCostOverride.  # noqa: E501
        :type: str
        """

        self._shipping_service_type = shipping_service_type

    @property
    def surcharge(self):
        """Gets the surcharge of this ShippingCostOverride.  # noqa: E501


        :return: The surcharge of this ShippingCostOverride.  # noqa: E501
        :rtype: Amount
        """
        return self._surcharge

    @surcharge.setter
    def surcharge(self, surcharge):
        """Sets the surcharge of this ShippingCostOverride.


        :param surcharge: The surcharge of this ShippingCostOverride.  # noqa: E501
        :type: Amount
        """

        self._surcharge = surcharge

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
        if issubclass(ShippingCostOverride, dict):
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
        if not isinstance(other, ShippingCostOverride):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
