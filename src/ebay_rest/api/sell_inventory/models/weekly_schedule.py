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

class WeeklySchedule(object):
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
        'cut_off_time': 'str',
        'day_of_week_enum': 'list[str]'
    }

    attribute_map = {
        'cut_off_time': 'cutOffTime',
        'day_of_week_enum': 'dayOfWeekEnum'
    }

    def __init__(self, cut_off_time=None, day_of_week_enum=None):  # noqa: E501
        """WeeklySchedule - a model defined in Swagger"""  # noqa: E501
        self._cut_off_time = None
        self._day_of_week_enum = None
        self.discriminator = None
        if cut_off_time is not None:
            self.cut_off_time = cut_off_time
        if day_of_week_enum is not None:
            self.day_of_week_enum = day_of_week_enum

    @property
    def cut_off_time(self):
        """Gets the cut_off_time of this WeeklySchedule.  # noqa: E501

        This field specifies the cut-off times (in 24-hour format) for the business day(s) specified in the <b>dayOfWeekEnum</b> array.<br><br>Cut-off times default to the time zone of the specified address if the <b>timeZoneId</b> is not provided.<br><br><span class=\"tablenote\"><b>Note:</b> If cut-off hours are not specified for a particular day, the fulfillment center is considered to be on holiday for that day.</span><br><b>Format:</b> <code>00:00</code>  # noqa: E501

        :return: The cut_off_time of this WeeklySchedule.  # noqa: E501
        :rtype: str
        """
        return self._cut_off_time

    @cut_off_time.setter
    def cut_off_time(self, cut_off_time):
        """Sets the cut_off_time of this WeeklySchedule.

        This field specifies the cut-off times (in 24-hour format) for the business day(s) specified in the <b>dayOfWeekEnum</b> array.<br><br>Cut-off times default to the time zone of the specified address if the <b>timeZoneId</b> is not provided.<br><br><span class=\"tablenote\"><b>Note:</b> If cut-off hours are not specified for a particular day, the fulfillment center is considered to be on holiday for that day.</span><br><b>Format:</b> <code>00:00</code>  # noqa: E501

        :param cut_off_time: The cut_off_time of this WeeklySchedule.  # noqa: E501
        :type: str
        """

        self._cut_off_time = cut_off_time

    @property
    def day_of_week_enum(self):
        """Gets the day_of_week_enum of this WeeklySchedule.  # noqa: E501

        This comma-separated array defines the days of week for which the specified <b>cutOffTime</b> is used.  # noqa: E501

        :return: The day_of_week_enum of this WeeklySchedule.  # noqa: E501
        :rtype: list[str]
        """
        return self._day_of_week_enum

    @day_of_week_enum.setter
    def day_of_week_enum(self, day_of_week_enum):
        """Sets the day_of_week_enum of this WeeklySchedule.

        This comma-separated array defines the days of week for which the specified <b>cutOffTime</b> is used.  # noqa: E501

        :param day_of_week_enum: The day_of_week_enum of this WeeklySchedule.  # noqa: E501
        :type: list[str]
        """

        self._day_of_week_enum = day_of_week_enum

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
        if issubclass(WeeklySchedule, dict):
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
        if not isinstance(other, WeeklySchedule):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
