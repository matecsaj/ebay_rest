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

class InventoryLocation(object):
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
        'location': 'LocationDetails',
        'location_additional_information': 'str',
        'location_instructions': 'str',
        'location_types': 'list[str]',
        'location_web_url': 'str',
        'name': 'str',
        'operating_hours': 'list[OperatingHours]',
        'phone': 'str',
        'special_hours': 'list[SpecialHours]',
        'time_zone_id': 'str',
        'fulfillment_center_specifications': 'FulfillmentCenterSpecifications'
    }

    attribute_map = {
        'location': 'location',
        'location_additional_information': 'locationAdditionalInformation',
        'location_instructions': 'locationInstructions',
        'location_types': 'locationTypes',
        'location_web_url': 'locationWebUrl',
        'name': 'name',
        'operating_hours': 'operatingHours',
        'phone': 'phone',
        'special_hours': 'specialHours',
        'time_zone_id': 'timeZoneId',
        'fulfillment_center_specifications': 'fulfillmentCenterSpecifications'
    }

    def __init__(self, location=None, location_additional_information=None, location_instructions=None, location_types=None, location_web_url=None, name=None, operating_hours=None, phone=None, special_hours=None, time_zone_id=None, fulfillment_center_specifications=None):  # noqa: E501
        """InventoryLocation - a model defined in Swagger"""  # noqa: E501
        self._location = None
        self._location_additional_information = None
        self._location_instructions = None
        self._location_types = None
        self._location_web_url = None
        self._name = None
        self._operating_hours = None
        self._phone = None
        self._special_hours = None
        self._time_zone_id = None
        self._fulfillment_center_specifications = None
        self.discriminator = None
        if location is not None:
            self.location = location
        if location_additional_information is not None:
            self.location_additional_information = location_additional_information
        if location_instructions is not None:
            self.location_instructions = location_instructions
        if location_types is not None:
            self.location_types = location_types
        if location_web_url is not None:
            self.location_web_url = location_web_url
        if name is not None:
            self.name = name
        if operating_hours is not None:
            self.operating_hours = operating_hours
        if phone is not None:
            self.phone = phone
        if special_hours is not None:
            self.special_hours = special_hours
        if time_zone_id is not None:
            self.time_zone_id = time_zone_id
        if fulfillment_center_specifications is not None:
            self.fulfillment_center_specifications = fulfillment_center_specifications

    @property
    def location(self):
        """Gets the location of this InventoryLocation.  # noqa: E501


        :return: The location of this InventoryLocation.  # noqa: E501
        :rtype: LocationDetails
        """
        return self._location

    @location.setter
    def location(self, location):
        """Sets the location of this InventoryLocation.


        :param location: The location of this InventoryLocation.  # noqa: E501
        :type: LocationDetails
        """

        self._location = location

    @property
    def location_additional_information(self):
        """Gets the location_additional_information of this InventoryLocation.  # noqa: E501

        This text field is used by the merchant to provide/update additional information about an inventory location. Whatever text is passed in this field will replace the current text string defined for this field. If the text will not change, the same text should be passed in once again. <br><br><b>Max length</b>: 256  # noqa: E501

        :return: The location_additional_information of this InventoryLocation.  # noqa: E501
        :rtype: str
        """
        return self._location_additional_information

    @location_additional_information.setter
    def location_additional_information(self, location_additional_information):
        """Sets the location_additional_information of this InventoryLocation.

        This text field is used by the merchant to provide/update additional information about an inventory location. Whatever text is passed in this field will replace the current text string defined for this field. If the text will not change, the same text should be passed in once again. <br><br><b>Max length</b>: 256  # noqa: E501

        :param location_additional_information: The location_additional_information of this InventoryLocation.  # noqa: E501
        :type: str
        """

        self._location_additional_information = location_additional_information

    @property
    def location_instructions(self):
        """Gets the location_instructions of this InventoryLocation.  # noqa: E501

        This text field is generally used by the merchant to provide/update special pickup instructions for a store inventory location. Although this field is optional, it is recommended that merchants provide this field to create a pleasant and easy pickup experience for In-Store Pickup and Click and Collect orders. If this field is not included in the call request payload, eBay will use the default pickup instructions contained in the merchant's profile (if available). Whatever text is passed in this field will replace the current text string defined for this field. If the text will not change, the same text should be passed in once again. <br><br><b>Max length</b>: 1000  # noqa: E501

        :return: The location_instructions of this InventoryLocation.  # noqa: E501
        :rtype: str
        """
        return self._location_instructions

    @location_instructions.setter
    def location_instructions(self, location_instructions):
        """Sets the location_instructions of this InventoryLocation.

        This text field is generally used by the merchant to provide/update special pickup instructions for a store inventory location. Although this field is optional, it is recommended that merchants provide this field to create a pleasant and easy pickup experience for In-Store Pickup and Click and Collect orders. If this field is not included in the call request payload, eBay will use the default pickup instructions contained in the merchant's profile (if available). Whatever text is passed in this field will replace the current text string defined for this field. If the text will not change, the same text should be passed in once again. <br><br><b>Max length</b>: 1000  # noqa: E501

        :param location_instructions: The location_instructions of this InventoryLocation.  # noqa: E501
        :type: str
        """

        self._location_instructions = location_instructions

    @property
    def location_types(self):
        """Gets the location_types of this InventoryLocation.  # noqa: E501

        This container is used to update the location type(s) associated with an inventory location.  # noqa: E501

        :return: The location_types of this InventoryLocation.  # noqa: E501
        :rtype: list[str]
        """
        return self._location_types

    @location_types.setter
    def location_types(self, location_types):
        """Sets the location_types of this InventoryLocation.

        This container is used to update the location type(s) associated with an inventory location.  # noqa: E501

        :param location_types: The location_types of this InventoryLocation.  # noqa: E501
        :type: list[str]
        """

        self._location_types = location_types

    @property
    def location_web_url(self):
        """Gets the location_web_url of this InventoryLocation.  # noqa: E501

        This text field is used by the merchant to provide/update the Website address (URL) associated with the inventory location. The URL that is passed in this field will replace any other URL that may be defined for this field. <br><br><b>Max length</b>: 512  # noqa: E501

        :return: The location_web_url of this InventoryLocation.  # noqa: E501
        :rtype: str
        """
        return self._location_web_url

    @location_web_url.setter
    def location_web_url(self, location_web_url):
        """Sets the location_web_url of this InventoryLocation.

        This text field is used by the merchant to provide/update the Website address (URL) associated with the inventory location. The URL that is passed in this field will replace any other URL that may be defined for this field. <br><br><b>Max length</b>: 512  # noqa: E501

        :param location_web_url: The location_web_url of this InventoryLocation.  # noqa: E501
        :type: str
        """

        self._location_web_url = location_web_url

    @property
    def name(self):
        """Gets the name of this InventoryLocation.  # noqa: E501

        This text field is used by the merchant to update the name of the inventory location. This name should be a human-friendly name as it will be in In-Store Pickup and Click and Collect listings. A name is not required for warehouse locations. For store locations, this field is not immediately required, but will be required before an offer enabled with the In-Store Pickup or Click and Collect capability can be published. So, if the seller omitted this field in the <strong>createInventoryLocation</strong> call, it is required for an <strong>updateInventoryLocation</strong> call. The name that is passed in this field will replace any other name that may be defined for this field.  # noqa: E501

        :return: The name of this InventoryLocation.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this InventoryLocation.

        This text field is used by the merchant to update the name of the inventory location. This name should be a human-friendly name as it will be in In-Store Pickup and Click and Collect listings. A name is not required for warehouse locations. For store locations, this field is not immediately required, but will be required before an offer enabled with the In-Store Pickup or Click and Collect capability can be published. So, if the seller omitted this field in the <strong>createInventoryLocation</strong> call, it is required for an <strong>updateInventoryLocation</strong> call. The name that is passed in this field will replace any other name that may be defined for this field.  # noqa: E501

        :param name: The name of this InventoryLocation.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def operating_hours(self):
        """Gets the operating_hours of this InventoryLocation.  # noqa: E501

        This container is used to provide/update the regular operating hours for a store location during the days of the week. A <strong>dayOfWeekEnum</strong> field and an <strong>intervals</strong> container will be needed for each day of the week that the location is open. Note that if operating hours are already set for a location for a specific day of the week, whatever is set through an <strong>updateInventoryLocation</strong> call will override those existing hours.  # noqa: E501

        :return: The operating_hours of this InventoryLocation.  # noqa: E501
        :rtype: list[OperatingHours]
        """
        return self._operating_hours

    @operating_hours.setter
    def operating_hours(self, operating_hours):
        """Sets the operating_hours of this InventoryLocation.

        This container is used to provide/update the regular operating hours for a store location during the days of the week. A <strong>dayOfWeekEnum</strong> field and an <strong>intervals</strong> container will be needed for each day of the week that the location is open. Note that if operating hours are already set for a location for a specific day of the week, whatever is set through an <strong>updateInventoryLocation</strong> call will override those existing hours.  # noqa: E501

        :param operating_hours: The operating_hours of this InventoryLocation.  # noqa: E501
        :type: list[OperatingHours]
        """

        self._operating_hours = operating_hours

    @property
    def phone(self):
        """Gets the phone of this InventoryLocation.  # noqa: E501

        This text field is used by the merchant to provide/update the phone number for the inventory location. The phone number that is passed in this field will replace any other phone number that may be defined for this field. <br><br><b>Max length</b>: 36  # noqa: E501

        :return: The phone of this InventoryLocation.  # noqa: E501
        :rtype: str
        """
        return self._phone

    @phone.setter
    def phone(self, phone):
        """Sets the phone of this InventoryLocation.

        This text field is used by the merchant to provide/update the phone number for the inventory location. The phone number that is passed in this field will replace any other phone number that may be defined for this field. <br><br><b>Max length</b>: 36  # noqa: E501

        :param phone: The phone of this InventoryLocation.  # noqa: E501
        :type: str
        """

        self._phone = phone

    @property
    def special_hours(self):
        """Gets the special_hours of this InventoryLocation.  # noqa: E501

        This container is used to provide/update the special operating hours for a store location on a specific date, such as a holiday. The special hours specified for the specific date will override the normal operating hours for that particular day of the week. If special hours have already been set up for an inventory location, specifying special hours through an <strong>updateInventoryLocation</strong> call will only add to the list, unless the date(s) used are the same special date(s) already set up, in which case, the special hours set up through the <strong>updateInventoryLocation</strong> call will override the existing special hours.  # noqa: E501

        :return: The special_hours of this InventoryLocation.  # noqa: E501
        :rtype: list[SpecialHours]
        """
        return self._special_hours

    @special_hours.setter
    def special_hours(self, special_hours):
        """Sets the special_hours of this InventoryLocation.

        This container is used to provide/update the special operating hours for a store location on a specific date, such as a holiday. The special hours specified for the specific date will override the normal operating hours for that particular day of the week. If special hours have already been set up for an inventory location, specifying special hours through an <strong>updateInventoryLocation</strong> call will only add to the list, unless the date(s) used are the same special date(s) already set up, in which case, the special hours set up through the <strong>updateInventoryLocation</strong> call will override the existing special hours.  # noqa: E501

        :param special_hours: The special_hours of this InventoryLocation.  # noqa: E501
        :type: list[SpecialHours]
        """

        self._special_hours = special_hours

    @property
    def time_zone_id(self):
        """Gets the time_zone_id of this InventoryLocation.  # noqa: E501

        This field is used to provide/update the time zone of the inventory location being created. This value should be in Olson format (for example <code>America/Vancouver</code>). For supported values, see <a href=\"https://howtodoinjava.com/java/date-time/supported-zone-ids-offsets/#3-java-supported-zone-ids-and-offsets\" target=\"_blank\">Java Supported Zone Ids and Offsets</a>.<br><br><span class=\"tablenote\"><b>Note:</b> If specified, this time zone will be used for all hour related fields. If this field is not specified, the time zone will be calculated from the provided address fields.</span>  # noqa: E501

        :return: The time_zone_id of this InventoryLocation.  # noqa: E501
        :rtype: str
        """
        return self._time_zone_id

    @time_zone_id.setter
    def time_zone_id(self, time_zone_id):
        """Sets the time_zone_id of this InventoryLocation.

        This field is used to provide/update the time zone of the inventory location being created. This value should be in Olson format (for example <code>America/Vancouver</code>). For supported values, see <a href=\"https://howtodoinjava.com/java/date-time/supported-zone-ids-offsets/#3-java-supported-zone-ids-and-offsets\" target=\"_blank\">Java Supported Zone Ids and Offsets</a>.<br><br><span class=\"tablenote\"><b>Note:</b> If specified, this time zone will be used for all hour related fields. If this field is not specified, the time zone will be calculated from the provided address fields.</span>  # noqa: E501

        :param time_zone_id: The time_zone_id of this InventoryLocation.  # noqa: E501
        :type: str
        """

        self._time_zone_id = time_zone_id

    @property
    def fulfillment_center_specifications(self):
        """Gets the fulfillment_center_specifications of this InventoryLocation.  # noqa: E501


        :return: The fulfillment_center_specifications of this InventoryLocation.  # noqa: E501
        :rtype: FulfillmentCenterSpecifications
        """
        return self._fulfillment_center_specifications

    @fulfillment_center_specifications.setter
    def fulfillment_center_specifications(self, fulfillment_center_specifications):
        """Sets the fulfillment_center_specifications of this InventoryLocation.


        :param fulfillment_center_specifications: The fulfillment_center_specifications of this InventoryLocation.  # noqa: E501
        :type: FulfillmentCenterSpecifications
        """

        self._fulfillment_center_specifications = fulfillment_center_specifications

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
        if issubclass(InventoryLocation, dict):
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
        if not isinstance(other, InventoryLocation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
