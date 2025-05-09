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

class ContestPaymentDisputeRequest(object):
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
        'note': 'str',
        'return_address': 'ReturnAddress',
        'revision': 'int'
    }

    attribute_map = {
        'note': 'note',
        'return_address': 'returnAddress',
        'revision': 'revision'
    }

    def __init__(self, note=None, return_address=None, revision=None):  # noqa: E501
        """ContestPaymentDisputeRequest - a model defined in Swagger"""  # noqa: E501
        self._note = None
        self._return_address = None
        self._revision = None
        self.discriminator = None
        if note is not None:
            self.note = note
        if return_address is not None:
            self.return_address = return_address
        if revision is not None:
            self.revision = revision

    @property
    def note(self):
        """Gets the note of this ContestPaymentDisputeRequest.  # noqa: E501

        This field shows information that the seller provides about the dispute, such as the basis for the dispute, any relevant evidence, tracking numbers, and so forth.<br><br><b>Max Length:</b> 1000 characters.  # noqa: E501

        :return: The note of this ContestPaymentDisputeRequest.  # noqa: E501
        :rtype: str
        """
        return self._note

    @note.setter
    def note(self, note):
        """Sets the note of this ContestPaymentDisputeRequest.

        This field shows information that the seller provides about the dispute, such as the basis for the dispute, any relevant evidence, tracking numbers, and so forth.<br><br><b>Max Length:</b> 1000 characters.  # noqa: E501

        :param note: The note of this ContestPaymentDisputeRequest.  # noqa: E501
        :type: str
        """

        self._note = note

    @property
    def return_address(self):
        """Gets the return_address of this ContestPaymentDisputeRequest.  # noqa: E501


        :return: The return_address of this ContestPaymentDisputeRequest.  # noqa: E501
        :rtype: ReturnAddress
        """
        return self._return_address

    @return_address.setter
    def return_address(self, return_address):
        """Sets the return_address of this ContestPaymentDisputeRequest.


        :param return_address: The return_address of this ContestPaymentDisputeRequest.  # noqa: E501
        :type: ReturnAddress
        """

        self._return_address = return_address

    @property
    def revision(self):
        """Gets the revision of this ContestPaymentDisputeRequest.  # noqa: E501

        This integer value indicates the revision number of the payment dispute. This field is required. The current <strong>revision</strong> number for a payment dispute can be retrieved with the <strong>getPaymentDispute</strong> method. Each time an action is taken against a payment dispute, this integer value increases by 1.  # noqa: E501

        :return: The revision of this ContestPaymentDisputeRequest.  # noqa: E501
        :rtype: int
        """
        return self._revision

    @revision.setter
    def revision(self, revision):
        """Sets the revision of this ContestPaymentDisputeRequest.

        This integer value indicates the revision number of the payment dispute. This field is required. The current <strong>revision</strong> number for a payment dispute can be retrieved with the <strong>getPaymentDispute</strong> method. Each time an action is taken against a payment dispute, this integer value increases by 1.  # noqa: E501

        :param revision: The revision of this ContestPaymentDisputeRequest.  # noqa: E501
        :type: int
        """

        self._revision = revision

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
        if issubclass(ContestPaymentDisputeRequest, dict):
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
        if not isinstance(other, ContestPaymentDisputeRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
