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

class OfferPriceQuantity(object):
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
        'available_quantity': 'int',
        'offer_id': 'str',
        'price': 'Amount'
    }

    attribute_map = {
        'available_quantity': 'availableQuantity',
        'offer_id': 'offerId',
        'price': 'price'
    }

    def __init__(self, available_quantity=None, offer_id=None, price=None):  # noqa: E501
        """OfferPriceQuantity - a model defined in Swagger"""  # noqa: E501
        self._available_quantity = None
        self._offer_id = None
        self._price = None
        self.discriminator = None
        if available_quantity is not None:
            self.available_quantity = available_quantity
        if offer_id is not None:
            self.offer_id = offer_id
        if price is not None:
            self.price = price

    @property
    def available_quantity(self):
        """Gets the available_quantity of this OfferPriceQuantity.  # noqa: E501

        This field is used if the seller wants to modify the current quantity of the inventory item that will be available for purchase in the offer (identified by the corresponding <strong>offerId</strong> value).<br><br>This value represents the quantity of the item that is available in the marketplace specified within the offer, not the total quantity available. Because of this, this value should not exceed the value specified in the <a href=\"/api-docs/sell/inventory/resources/inventory_item/methods/bulkUpdatePriceQuantity#request.requests.shipToLocationAvailability.quantity\"><b>quantity</b></a> field of the <b>shipToLocationAvailability</b> container (the total available quantity of the item across all marketplaces).<br><br><span class=\"tablenote\"> <strong>Note:</strong> To ensure that the available quantity allocated to a specific marketplace doesn't exceed the total available stock, the quantity specified on a listing will be the minimum value between this field and the <a href=\"/api-docs/sell/inventory/resources/inventory_item/methods/bulkUpdatePriceQuantity#request.requests.shipToLocationAvailability.quantity\"><b>quantity</b></a> field.</span><br>Either the <strong>availableQuantity</strong> field or the <strong>price</strong> container is required, but not necessarily both.  # noqa: E501

        :return: The available_quantity of this OfferPriceQuantity.  # noqa: E501
        :rtype: int
        """
        return self._available_quantity

    @available_quantity.setter
    def available_quantity(self, available_quantity):
        """Sets the available_quantity of this OfferPriceQuantity.

        This field is used if the seller wants to modify the current quantity of the inventory item that will be available for purchase in the offer (identified by the corresponding <strong>offerId</strong> value).<br><br>This value represents the quantity of the item that is available in the marketplace specified within the offer, not the total quantity available. Because of this, this value should not exceed the value specified in the <a href=\"/api-docs/sell/inventory/resources/inventory_item/methods/bulkUpdatePriceQuantity#request.requests.shipToLocationAvailability.quantity\"><b>quantity</b></a> field of the <b>shipToLocationAvailability</b> container (the total available quantity of the item across all marketplaces).<br><br><span class=\"tablenote\"> <strong>Note:</strong> To ensure that the available quantity allocated to a specific marketplace doesn't exceed the total available stock, the quantity specified on a listing will be the minimum value between this field and the <a href=\"/api-docs/sell/inventory/resources/inventory_item/methods/bulkUpdatePriceQuantity#request.requests.shipToLocationAvailability.quantity\"><b>quantity</b></a> field.</span><br>Either the <strong>availableQuantity</strong> field or the <strong>price</strong> container is required, but not necessarily both.  # noqa: E501

        :param available_quantity: The available_quantity of this OfferPriceQuantity.  # noqa: E501
        :type: int
        """

        self._available_quantity = available_quantity

    @property
    def offer_id(self):
        """Gets the offer_id of this OfferPriceQuantity.  # noqa: E501

        This field is the unique identifier of the offer. If an <strong>offers</strong> container is used to update one or more offers associated to a specific inventory item, the <strong>offerId</strong> value is required in order to identify the offer to update with a modified price and/or quantity.<br><br>The seller can use the <a href=\"/api-docs/sell/inventory/resources/offer/methods/getOffers\" target=\"_blank \">getOffers</a> method (passing in the correct SKU value as a query parameter) to retrieve <strong>offerId</strong> values for offers associated with the SKU.  # noqa: E501

        :return: The offer_id of this OfferPriceQuantity.  # noqa: E501
        :rtype: str
        """
        return self._offer_id

    @offer_id.setter
    def offer_id(self, offer_id):
        """Sets the offer_id of this OfferPriceQuantity.

        This field is the unique identifier of the offer. If an <strong>offers</strong> container is used to update one or more offers associated to a specific inventory item, the <strong>offerId</strong> value is required in order to identify the offer to update with a modified price and/or quantity.<br><br>The seller can use the <a href=\"/api-docs/sell/inventory/resources/offer/methods/getOffers\" target=\"_blank \">getOffers</a> method (passing in the correct SKU value as a query parameter) to retrieve <strong>offerId</strong> values for offers associated with the SKU.  # noqa: E501

        :param offer_id: The offer_id of this OfferPriceQuantity.  # noqa: E501
        :type: str
        """

        self._offer_id = offer_id

    @property
    def price(self):
        """Gets the price of this OfferPriceQuantity.  # noqa: E501


        :return: The price of this OfferPriceQuantity.  # noqa: E501
        :rtype: Amount
        """
        return self._price

    @price.setter
    def price(self, price):
        """Sets the price of this OfferPriceQuantity.


        :param price: The price of this OfferPriceQuantity.  # noqa: E501
        :type: Amount
        """

        self._price = price

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
        if issubclass(OfferPriceQuantity, dict):
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
        if not isinstance(other, OfferPriceQuantity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
