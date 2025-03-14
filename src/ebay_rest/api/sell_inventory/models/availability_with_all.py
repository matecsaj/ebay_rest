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

class AvailabilityWithAll(object):
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
        'pickup_at_location_availability': 'list[PickupAtLocationAvailability]',
        'ship_to_location_availability': 'ShipToLocationAvailabilityWithAll'
    }

    attribute_map = {
        'pickup_at_location_availability': 'pickupAtLocationAvailability',
        'ship_to_location_availability': 'shipToLocationAvailability'
    }

    def __init__(self, pickup_at_location_availability=None, ship_to_location_availability=None):  # noqa: E501
        """AvailabilityWithAll - a model defined in Swagger"""  # noqa: E501
        self._pickup_at_location_availability = None
        self._ship_to_location_availability = None
        self.discriminator = None
        if pickup_at_location_availability is not None:
            self.pickup_at_location_availability = pickup_at_location_availability
        if ship_to_location_availability is not None:
            self.ship_to_location_availability = ship_to_location_availability

    @property
    def pickup_at_location_availability(self):
        """Gets the pickup_at_location_availability of this AvailabilityWithAll.  # noqa: E501

        This container consists of an array of one or more of the merchant's physical stores where the inventory item is available for in-store pickup.<br><br>The store ID, the quantity available, and the fulfillment time (how soon the item will be ready for pickup after the order occurs) are all returned in this container.  # noqa: E501

        :return: The pickup_at_location_availability of this AvailabilityWithAll.  # noqa: E501
        :rtype: list[PickupAtLocationAvailability]
        """
        return self._pickup_at_location_availability

    @pickup_at_location_availability.setter
    def pickup_at_location_availability(self, pickup_at_location_availability):
        """Sets the pickup_at_location_availability of this AvailabilityWithAll.

        This container consists of an array of one or more of the merchant's physical stores where the inventory item is available for in-store pickup.<br><br>The store ID, the quantity available, and the fulfillment time (how soon the item will be ready for pickup after the order occurs) are all returned in this container.  # noqa: E501

        :param pickup_at_location_availability: The pickup_at_location_availability of this AvailabilityWithAll.  # noqa: E501
        :type: list[PickupAtLocationAvailability]
        """

        self._pickup_at_location_availability = pickup_at_location_availability

    @property
    def ship_to_location_availability(self):
        """Gets the ship_to_location_availability of this AvailabilityWithAll.  # noqa: E501


        :return: The ship_to_location_availability of this AvailabilityWithAll.  # noqa: E501
        :rtype: ShipToLocationAvailabilityWithAll
        """
        return self._ship_to_location_availability

    @ship_to_location_availability.setter
    def ship_to_location_availability(self, ship_to_location_availability):
        """Sets the ship_to_location_availability of this AvailabilityWithAll.


        :param ship_to_location_availability: The ship_to_location_availability of this AvailabilityWithAll.  # noqa: E501
        :type: ShipToLocationAvailabilityWithAll
        """

        self._ship_to_location_availability = ship_to_location_availability

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
        if issubclass(AvailabilityWithAll, dict):
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
        if not isinstance(other, AvailabilityWithAll):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
