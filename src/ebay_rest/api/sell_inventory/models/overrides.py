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

class Overrides(object):
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
        'end_date': 'str',
        'start_date': 'str'
    }

    attribute_map = {
        'cut_off_time': 'cutOffTime',
        'end_date': 'endDate',
        'start_date': 'startDate'
    }

    def __init__(self, cut_off_time=None, end_date=None, start_date=None):  # noqa: E501
        """Overrides - a model defined in Swagger"""  # noqa: E501
        self._cut_off_time = None
        self._end_date = None
        self._start_date = None
        self.discriminator = None
        if cut_off_time is not None:
            self.cut_off_time = cut_off_time
        if end_date is not None:
            self.end_date = end_date
        if start_date is not None:
            self.start_date = start_date

    @property
    def cut_off_time(self):
        """Gets the cut_off_time of this Overrides.  # noqa: E501

        This field is used to override the cut-off time(s) specified in the <b>weeklySchedule</b> container. If an order is placed after this time in the specified date or date range, it will be handled by the seller on the following day.<br><br><b>Format:</b> <code>00:00</code>  # noqa: E501

        :return: The cut_off_time of this Overrides.  # noqa: E501
        :rtype: str
        """
        return self._cut_off_time

    @cut_off_time.setter
    def cut_off_time(self, cut_off_time):
        """Sets the cut_off_time of this Overrides.

        This field is used to override the cut-off time(s) specified in the <b>weeklySchedule</b> container. If an order is placed after this time in the specified date or date range, it will be handled by the seller on the following day.<br><br><b>Format:</b> <code>00:00</code>  # noqa: E501

        :param cut_off_time: The cut_off_time of this Overrides.  # noqa: E501
        :type: str
        """

        self._cut_off_time = cut_off_time

    @property
    def end_date(self):
        """Gets the end_date of this Overrides.  # noqa: E501

        The end date of the cut-off time override in <a href=\"https://www.iso.org/iso-8601-date-and-time-format.html \" title=\"https://www.iso.org \" target=\"_blank\">ISO 8601</a> format, which is based on the 24-hour Coordinated Universal Time (UTC) clock.<br><br><span class=\"tablenote\"><b>Note:</b> If the cut-off time override is only for a single day, input the same date in the <b>startDate</b> and <b>endDate</b> fields.</span><br><b>Format:</b> <code>[YYYY]-[MM]-[DD]</code><br><br><b>Example:</b> <code>2024-08-06</code><br><br><span class=\"tablenote\"><b>Note:</b> The time zone for this date is specified from the <b>timeZoneId</b> field. If this field is not used, the time zone will be derived from the provided address.</span>  # noqa: E501

        :return: The end_date of this Overrides.  # noqa: E501
        :rtype: str
        """
        return self._end_date

    @end_date.setter
    def end_date(self, end_date):
        """Sets the end_date of this Overrides.

        The end date of the cut-off time override in <a href=\"https://www.iso.org/iso-8601-date-and-time-format.html \" title=\"https://www.iso.org \" target=\"_blank\">ISO 8601</a> format, which is based on the 24-hour Coordinated Universal Time (UTC) clock.<br><br><span class=\"tablenote\"><b>Note:</b> If the cut-off time override is only for a single day, input the same date in the <b>startDate</b> and <b>endDate</b> fields.</span><br><b>Format:</b> <code>[YYYY]-[MM]-[DD]</code><br><br><b>Example:</b> <code>2024-08-06</code><br><br><span class=\"tablenote\"><b>Note:</b> The time zone for this date is specified from the <b>timeZoneId</b> field. If this field is not used, the time zone will be derived from the provided address.</span>  # noqa: E501

        :param end_date: The end_date of this Overrides.  # noqa: E501
        :type: str
        """

        self._end_date = end_date

    @property
    def start_date(self):
        """Gets the start_date of this Overrides.  # noqa: E501

        The start date of the cut-off time override in <a href=\"https://www.iso.org/iso-8601-date-and-time-format.html \" title=\"https://www.iso.org \" target=\"_blank\">ISO 8601</a> format, which is based on the 24-hour Coordinated Universal Time (UTC) clock.<br><br><span class=\"tablenote\"><b>Note:</b> If the cut-off time override is only for a single day, input the same date in the <b>startDate</b> and <b>endDate</b> fields.</span><br><b>Format:</b> <code>[YYYY]-[MM]-[DD]</code><br><br><b>Example:</b> <code>2024-08-04</code><br><br><span class=\"tablenote\"><b>Note:</b> The time zone for this date is specified from the <b>timeZoneId</b> field. If this field is not used, the time zone will be derived from the provided address.</span>  # noqa: E501

        :return: The start_date of this Overrides.  # noqa: E501
        :rtype: str
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """Sets the start_date of this Overrides.

        The start date of the cut-off time override in <a href=\"https://www.iso.org/iso-8601-date-and-time-format.html \" title=\"https://www.iso.org \" target=\"_blank\">ISO 8601</a> format, which is based on the 24-hour Coordinated Universal Time (UTC) clock.<br><br><span class=\"tablenote\"><b>Note:</b> If the cut-off time override is only for a single day, input the same date in the <b>startDate</b> and <b>endDate</b> fields.</span><br><b>Format:</b> <code>[YYYY]-[MM]-[DD]</code><br><br><b>Example:</b> <code>2024-08-04</code><br><br><span class=\"tablenote\"><b>Note:</b> The time zone for this date is specified from the <b>timeZoneId</b> field. If this field is not used, the time zone will be derived from the provided address.</span>  # noqa: E501

        :param start_date: The start_date of this Overrides.  # noqa: E501
        :type: str
        """

        self._start_date = start_date

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
        if issubclass(Overrides, dict):
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
        if not isinstance(other, Overrides):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
