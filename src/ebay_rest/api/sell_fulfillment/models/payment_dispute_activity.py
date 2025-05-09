# coding: utf-8

"""
    Fulfillment API

    Use the Fulfillment API to complete the process of packaging, addressing, handling, and shipping each order on behalf of the seller, in accordance with the payment method and timing specified at checkout.  # noqa: E501

    OpenAPI spec version: v1.20.7
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class PaymentDisputeActivity(object):
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
        'activity_date': 'str',
        'activity_type': 'str',
        'actor': 'str'
    }

    attribute_map = {
        'activity_date': 'activityDate',
        'activity_type': 'activityType',
        'actor': 'actor'
    }

    def __init__(self, activity_date=None, activity_type=None, actor=None):  # noqa: E501
        """PaymentDisputeActivity - a model defined in Swagger"""  # noqa: E501
        self._activity_date = None
        self._activity_type = None
        self._actor = None
        self.discriminator = None
        if activity_date is not None:
            self.activity_date = activity_date
        if activity_type is not None:
            self.activity_type = activity_type
        if actor is not None:
            self.actor = actor

    @property
    def activity_date(self):
        """Gets the activity_date of this PaymentDisputeActivity.  # noqa: E501

        The timestamp in this field shows the date/time of the payment dispute activity.<br><br>The timestamps returned here use the ISO-8601 24-hour date and time format, and the time zone used is Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT), or Zulu. The ISO-8601 format looks like this: <em>yyyy-MM-ddThh:mm.ss.sssZ</em>. An example would be <code>2019-08-04T19:09:02.768Z</code>.  # noqa: E501

        :return: The activity_date of this PaymentDisputeActivity.  # noqa: E501
        :rtype: str
        """
        return self._activity_date

    @activity_date.setter
    def activity_date(self, activity_date):
        """Sets the activity_date of this PaymentDisputeActivity.

        The timestamp in this field shows the date/time of the payment dispute activity.<br><br>The timestamps returned here use the ISO-8601 24-hour date and time format, and the time zone used is Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT), or Zulu. The ISO-8601 format looks like this: <em>yyyy-MM-ddThh:mm.ss.sssZ</em>. An example would be <code>2019-08-04T19:09:02.768Z</code>.  # noqa: E501

        :param activity_date: The activity_date of this PaymentDisputeActivity.  # noqa: E501
        :type: str
        """

        self._activity_date = activity_date

    @property
    def activity_type(self):
        """Gets the activity_type of this PaymentDisputeActivity.  # noqa: E501

        This enumeration value indicates the type of activity that occured on the payment dispute. For example, a value of <code>DISPUTE_OPENED</code> is returned when a payment disute is first created,  a value indicating the seller's decision on the dispute, such as <code>SELLER_CONTEST</code>, is returned when seller makes a decision to accept or contest dispute, and a value of <code>DISPUTE_CLOSED</code> is returned when a payment disute is resolved. See <strong>ActivityEnum</strong> for an explanation of each of the values that may be returned here. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/fulfillment/types/api:ActivityEnum'>eBay API documentation</a>  # noqa: E501

        :return: The activity_type of this PaymentDisputeActivity.  # noqa: E501
        :rtype: str
        """
        return self._activity_type

    @activity_type.setter
    def activity_type(self, activity_type):
        """Sets the activity_type of this PaymentDisputeActivity.

        This enumeration value indicates the type of activity that occured on the payment dispute. For example, a value of <code>DISPUTE_OPENED</code> is returned when a payment disute is first created,  a value indicating the seller's decision on the dispute, such as <code>SELLER_CONTEST</code>, is returned when seller makes a decision to accept or contest dispute, and a value of <code>DISPUTE_CLOSED</code> is returned when a payment disute is resolved. See <strong>ActivityEnum</strong> for an explanation of each of the values that may be returned here. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/fulfillment/types/api:ActivityEnum'>eBay API documentation</a>  # noqa: E501

        :param activity_type: The activity_type of this PaymentDisputeActivity.  # noqa: E501
        :type: str
        """

        self._activity_type = activity_type

    @property
    def actor(self):
        """Gets the actor of this PaymentDisputeActivity.  # noqa: E501

        This enumeration value indicates the actor that performed the action. Possible values include the <code>BUYER</code>, <code>SELLER</code>, <code>CS_AGENT</code> (eBay customer service), or <code>SYSTEM</code>. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/fulfillment/types/api:ActorEnum'>eBay API documentation</a>  # noqa: E501

        :return: The actor of this PaymentDisputeActivity.  # noqa: E501
        :rtype: str
        """
        return self._actor

    @actor.setter
    def actor(self, actor):
        """Sets the actor of this PaymentDisputeActivity.

        This enumeration value indicates the actor that performed the action. Possible values include the <code>BUYER</code>, <code>SELLER</code>, <code>CS_AGENT</code> (eBay customer service), or <code>SYSTEM</code>. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/fulfillment/types/api:ActorEnum'>eBay API documentation</a>  # noqa: E501

        :param actor: The actor of this PaymentDisputeActivity.  # noqa: E501
        :type: str
        """

        self._actor = actor

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
        if issubclass(PaymentDisputeActivity, dict):
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
        if not isinstance(other, PaymentDisputeActivity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
