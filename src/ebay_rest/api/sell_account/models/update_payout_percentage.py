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

class UpdatePayoutPercentage(object):
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
        'instrument_id': 'str',
        'payout_percentage': 'str'
    }

    attribute_map = {
        'instrument_id': 'instrumentId',
        'payout_percentage': 'payoutPercentage'
    }

    def __init__(self, instrument_id=None, payout_percentage=None):  # noqa: E501
        """UpdatePayoutPercentage - a model defined in Swagger"""  # noqa: E501
        self._instrument_id = None
        self._payout_percentage = None
        self.discriminator = None
        if instrument_id is not None:
            self.instrument_id = instrument_id
        if payout_percentage is not None:
            self.payout_percentage = payout_percentage

    @property
    def instrument_id(self):
        """Gets the instrument_id of this UpdatePayoutPercentage.  # noqa: E501

        The unique reference identifier for a payout instrument. This value is returned in the <a href=\"/api-docs/sell/account/v2/resources/payout_settings/methods/getPayoutSettings\" target=\"_blank \">getPayoutSettings</a> response and is needed to change split-payout percentages through an <b>updatePayoutPercentage</b> request.  # noqa: E501

        :return: The instrument_id of this UpdatePayoutPercentage.  # noqa: E501
        :rtype: str
        """
        return self._instrument_id

    @instrument_id.setter
    def instrument_id(self, instrument_id):
        """Sets the instrument_id of this UpdatePayoutPercentage.

        The unique reference identifier for a payout instrument. This value is returned in the <a href=\"/api-docs/sell/account/v2/resources/payout_settings/methods/getPayoutSettings\" target=\"_blank \">getPayoutSettings</a> response and is needed to change split-payout percentages through an <b>updatePayoutPercentage</b> request.  # noqa: E501

        :param instrument_id: The instrument_id of this UpdatePayoutPercentage.  # noqa: E501
        :type: str
        """

        self._instrument_id = instrument_id

    @property
    def payout_percentage(self):
        """Gets the payout_percentage of this UpdatePayoutPercentage.  # noqa: E501

        The user-defined payout percentage allocated to this instrument. For example, <code>50</code> indicates that 50% of the payout goes to this instrument.<br/><br/>The split-payout percentage <b>must</b> be a positive integer value from 0-100. The values of two instruments <b>must</b> always add up to 100%. If the values do not equal 100, the call will fail.  # noqa: E501

        :return: The payout_percentage of this UpdatePayoutPercentage.  # noqa: E501
        :rtype: str
        """
        return self._payout_percentage

    @payout_percentage.setter
    def payout_percentage(self, payout_percentage):
        """Sets the payout_percentage of this UpdatePayoutPercentage.

        The user-defined payout percentage allocated to this instrument. For example, <code>50</code> indicates that 50% of the payout goes to this instrument.<br/><br/>The split-payout percentage <b>must</b> be a positive integer value from 0-100. The values of two instruments <b>must</b> always add up to 100%. If the values do not equal 100, the call will fail.  # noqa: E501

        :param payout_percentage: The payout_percentage of this UpdatePayoutPercentage.  # noqa: E501
        :type: str
        """

        self._payout_percentage = payout_percentage

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
        if issubclass(UpdatePayoutPercentage, dict):
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
        if not isinstance(other, UpdatePayoutPercentage):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
