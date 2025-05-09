# coding: utf-8

"""
    EDIS public shipping API

    <div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span> This method is only available for Greater-China based sellers with an active eDIS account.</p></div><br>This API allows 3rd party developers in the Greater-China area to process package shipping details.  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class GetActualCostResponsesData(object):
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
        'actual_weight': 'float',
        'amount': 'Amount',
        'billing_time': 'str',
        'charge_mode': 'str',
        'charge_weight': 'float',
        'cost_type': 'str',
        'message': 'str',
        'remark': 'str',
        'result_code': 'str',
        'size': 'str',
        'tracking_number': 'str'
    }

    attribute_map = {
        'actual_weight': 'actualWeight',
        'amount': 'amount',
        'billing_time': 'billingTime',
        'charge_mode': 'chargeMode',
        'charge_weight': 'chargeWeight',
        'cost_type': 'costType',
        'message': 'message',
        'remark': 'remark',
        'result_code': 'resultCode',
        'size': 'size',
        'tracking_number': 'trackingNumber'
    }

    def __init__(self, actual_weight=None, amount=None, billing_time=None, charge_mode=None, charge_weight=None, cost_type=None, message=None, remark=None, result_code=None, size=None, tracking_number=None):  # noqa: E501
        """GetActualCostResponsesData - a model defined in Swagger"""  # noqa: E501
        self._actual_weight = None
        self._amount = None
        self._billing_time = None
        self._charge_mode = None
        self._charge_weight = None
        self._cost_type = None
        self._message = None
        self._remark = None
        self._result_code = None
        self._size = None
        self._tracking_number = None
        self.discriminator = None
        if actual_weight is not None:
            self.actual_weight = actual_weight
        if amount is not None:
            self.amount = amount
        if billing_time is not None:
            self.billing_time = billing_time
        if charge_mode is not None:
            self.charge_mode = charge_mode
        if charge_weight is not None:
            self.charge_weight = charge_weight
        if cost_type is not None:
            self.cost_type = cost_type
        if message is not None:
            self.message = message
        if remark is not None:
            self.remark = remark
        if result_code is not None:
            self.result_code = result_code
        if size is not None:
            self.size = size
        if tracking_number is not None:
            self.tracking_number = tracking_number

    @property
    def actual_weight(self):
        """Gets the actual_weight of this GetActualCostResponsesData.  # noqa: E501

        The actual weight of the package in grams.  # noqa: E501

        :return: The actual_weight of this GetActualCostResponsesData.  # noqa: E501
        :rtype: float
        """
        return self._actual_weight

    @actual_weight.setter
    def actual_weight(self, actual_weight):
        """Sets the actual_weight of this GetActualCostResponsesData.

        The actual weight of the package in grams.  # noqa: E501

        :param actual_weight: The actual_weight of this GetActualCostResponsesData.  # noqa: E501
        :type: float
        """

        self._actual_weight = actual_weight

    @property
    def amount(self):
        """Gets the amount of this GetActualCostResponsesData.  # noqa: E501


        :return: The amount of this GetActualCostResponsesData.  # noqa: E501
        :rtype: Amount
        """
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the amount of this GetActualCostResponsesData.


        :param amount: The amount of this GetActualCostResponsesData.  # noqa: E501
        :type: Amount
        """

        self._amount = amount

    @property
    def billing_time(self):
        """Gets the billing_time of this GetActualCostResponsesData.  # noqa: E501

        The time the seller was charged for the actual cost of the package in UTC format.  # noqa: E501

        :return: The billing_time of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._billing_time

    @billing_time.setter
    def billing_time(self, billing_time):
        """Sets the billing_time of this GetActualCostResponsesData.

        The time the seller was charged for the actual cost of the package in UTC format.  # noqa: E501

        :param billing_time: The billing_time of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._billing_time = billing_time

    @property
    def charge_mode(self):
        """Gets the charge_mode of this GetActualCostResponsesData.  # noqa: E501

        The two-digit charge mode for the package.<br><br><b>Valid values</b>:<ul><li><code>01</code>: Actual weight</li><li><code>02</code>: Additional dimension weight</li><li><code>03</code>: Charged by lite mode</li></ul>  # noqa: E501

        :return: The charge_mode of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._charge_mode

    @charge_mode.setter
    def charge_mode(self, charge_mode):
        """Sets the charge_mode of this GetActualCostResponsesData.

        The two-digit charge mode for the package.<br><br><b>Valid values</b>:<ul><li><code>01</code>: Actual weight</li><li><code>02</code>: Additional dimension weight</li><li><code>03</code>: Charged by lite mode</li></ul>  # noqa: E501

        :param charge_mode: The charge_mode of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._charge_mode = charge_mode

    @property
    def charge_weight(self):
        """Gets the charge_weight of this GetActualCostResponsesData.  # noqa: E501

        The weight, in grams, charged for when shipping the package.  # noqa: E501

        :return: The charge_weight of this GetActualCostResponsesData.  # noqa: E501
        :rtype: float
        """
        return self._charge_weight

    @charge_weight.setter
    def charge_weight(self, charge_weight):
        """Sets the charge_weight of this GetActualCostResponsesData.

        The weight, in grams, charged for when shipping the package.  # noqa: E501

        :param charge_weight: The charge_weight of this GetActualCostResponsesData.  # noqa: E501
        :type: float
        """

        self._charge_weight = charge_weight

    @property
    def cost_type(self):
        """Gets the cost_type of this GetActualCostResponsesData.  # noqa: E501

        The two-digit cost type of the package. This field indicates any fees associated with the package.<br><br>The following values are the typical cost types returned through this field. If an undocumented cost type is returned, check the logistic provider's website for the latest values:<br><ul><li><code>01</code>: Shipping fee</li><li><code>02</code>: Domestic</li><li><code>03</code>: Return fee</li><li><code>04</code>: Domestic burning fee</li><li><code>05</code>: Custom collected fee</li><li><code>06</code>: Weight gap fee</li><li><code>07</code>: Duplication compensation</li></ul>  # noqa: E501

        :return: The cost_type of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._cost_type

    @cost_type.setter
    def cost_type(self, cost_type):
        """Sets the cost_type of this GetActualCostResponsesData.

        The two-digit cost type of the package. This field indicates any fees associated with the package.<br><br>The following values are the typical cost types returned through this field. If an undocumented cost type is returned, check the logistic provider's website for the latest values:<br><ul><li><code>01</code>: Shipping fee</li><li><code>02</code>: Domestic</li><li><code>03</code>: Return fee</li><li><code>04</code>: Domestic burning fee</li><li><code>05</code>: Custom collected fee</li><li><code>06</code>: Weight gap fee</li><li><code>07</code>: Duplication compensation</li></ul>  # noqa: E501

        :param cost_type: The cost_type of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._cost_type = cost_type

    @property
    def message(self):
        """Gets the message of this GetActualCostResponsesData.  # noqa: E501

        A seller-defined message to the buyer regarding the transaction.<br><br><span class=\"tablenote\"><b>Note:</b> This field is always returned, but will show as null or have an empty value if not defined/applicable.</span>  # noqa: E501

        :return: The message of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this GetActualCostResponsesData.

        A seller-defined message to the buyer regarding the transaction.<br><br><span class=\"tablenote\"><b>Note:</b> This field is always returned, but will show as null or have an empty value if not defined/applicable.</span>  # noqa: E501

        :param message: The message of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._message = message

    @property
    def remark(self):
        """Gets the remark of this GetActualCostResponsesData.  # noqa: E501

        A remark to the seller themselves.<br><br><span class=\"tablenote\"><b>Note:</b> This field is always returned, but will show as null or have an empty value if not defined/applicable.</span>  # noqa: E501

        :return: The remark of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._remark

    @remark.setter
    def remark(self, remark):
        """Sets the remark of this GetActualCostResponsesData.

        A remark to the seller themselves.<br><br><span class=\"tablenote\"><b>Note:</b> This field is always returned, but will show as null or have an empty value if not defined/applicable.</span>  # noqa: E501

        :param remark: The remark of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._remark = remark

    @property
    def result_code(self):
        """Gets the result_code of this GetActualCostResponsesData.  # noqa: E501

        The result code associated with the call.<br><br>For example, a result code of <code>200</code> indicates that the call was a success.  # noqa: E501

        :return: The result_code of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._result_code

    @result_code.setter
    def result_code(self, result_code):
        """Sets the result_code of this GetActualCostResponsesData.

        The result code associated with the call.<br><br>For example, a result code of <code>200</code> indicates that the call was a success.  # noqa: E501

        :param result_code: The result_code of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._result_code = result_code

    @property
    def size(self):
        """Gets the size of this GetActualCostResponsesData.  # noqa: E501

        The size of the package in centimeters. This value is returned in Length*Width*Height format.  # noqa: E501

        :return: The size of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this GetActualCostResponsesData.

        The size of the package in centimeters. This value is returned in Length*Width*Height format.  # noqa: E501

        :param size: The size of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._size = size

    @property
    def tracking_number(self):
        """Gets the tracking_number of this GetActualCostResponsesData.  # noqa: E501

        The tracking number associated with the package.  # noqa: E501

        :return: The tracking_number of this GetActualCostResponsesData.  # noqa: E501
        :rtype: str
        """
        return self._tracking_number

    @tracking_number.setter
    def tracking_number(self, tracking_number):
        """Sets the tracking_number of this GetActualCostResponsesData.

        The tracking number associated with the package.  # noqa: E501

        :param tracking_number: The tracking_number of this GetActualCostResponsesData.  # noqa: E501
        :type: str
        """

        self._tracking_number = tracking_number

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
        if issubclass(GetActualCostResponsesData, dict):
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
        if not isinstance(other, GetActualCostResponsesData):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
