# coding: utf-8

"""
    Finances API

    This API is used to retrieve seller payouts and monetary transaction details related to those payouts.  # noqa: E501

    OpenAPI spec version: v1.17.3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Payouts(object):
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
        'href': 'str',
        'limit': 'int',
        'next': 'str',
        'offset': 'int',
        'payouts': 'list[Payout]',
        'prev': 'str',
        'total': 'int'
    }

    attribute_map = {
        'href': 'href',
        'limit': 'limit',
        'next': 'next',
        'offset': 'offset',
        'payouts': 'payouts',
        'prev': 'prev',
        'total': 'total'
    }

    def __init__(self, href=None, limit=None, next=None, offset=None, payouts=None, prev=None, total=None):  # noqa: E501
        """Payouts - a model defined in Swagger"""  # noqa: E501
        self._href = None
        self._limit = None
        self._next = None
        self._offset = None
        self._payouts = None
        self._prev = None
        self._total = None
        self.discriminator = None
        if href is not None:
            self.href = href
        if limit is not None:
            self.limit = limit
        if next is not None:
            self.next = next
        if offset is not None:
            self.offset = offset
        if payouts is not None:
            self.payouts = payouts
        if prev is not None:
            self.prev = prev
        if total is not None:
            self.total = total

    @property
    def href(self):
        """Gets the href of this Payouts.  # noqa: E501

        The URI of the <b>getPayouts</b> call request that produced the current page of the result set.  # noqa: E501

        :return: The href of this Payouts.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this Payouts.

        The URI of the <b>getPayouts</b> call request that produced the current page of the result set.  # noqa: E501

        :param href: The href of this Payouts.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def limit(self):
        """Gets the limit of this Payouts.  # noqa: E501

        The maximum number of payouts that may be returned per page of the result set. The <strong>limit</strong> value can be passed in as a query parameter, or if omitted, its value defaults to <code>20</code>. <br><br><span class=\"tablenote\"><strong>Note:</strong> If this is the last or only page of the result set, the page may contain fewer payouts than the <strong>limit</strong> value.  To determine the number of pages in a result set, divide the <b>total</b> value (total number of payouts matching input criteria) by this <strong>limit</strong> value, and then round up to the next integer. For example, if the <b>total</b> value was <code>120</code> (120 total payouts) and the <strong>limit</strong> value was <code>50</code> (show 50 payouts per page), the total number of pages in the result set is three, so the seller would have to make three separate <strong>getPayouts</strong> calls to view all payouts matching the input criteria. </span><br><br><b>Maximum:</b> <code>200</code> <br> <b>Default:</b> <code>20</code>  # noqa: E501

        :return: The limit of this Payouts.  # noqa: E501
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        """Sets the limit of this Payouts.

        The maximum number of payouts that may be returned per page of the result set. The <strong>limit</strong> value can be passed in as a query parameter, or if omitted, its value defaults to <code>20</code>. <br><br><span class=\"tablenote\"><strong>Note:</strong> If this is the last or only page of the result set, the page may contain fewer payouts than the <strong>limit</strong> value.  To determine the number of pages in a result set, divide the <b>total</b> value (total number of payouts matching input criteria) by this <strong>limit</strong> value, and then round up to the next integer. For example, if the <b>total</b> value was <code>120</code> (120 total payouts) and the <strong>limit</strong> value was <code>50</code> (show 50 payouts per page), the total number of pages in the result set is three, so the seller would have to make three separate <strong>getPayouts</strong> calls to view all payouts matching the input criteria. </span><br><br><b>Maximum:</b> <code>200</code> <br> <b>Default:</b> <code>20</code>  # noqa: E501

        :param limit: The limit of this Payouts.  # noqa: E501
        :type: int
        """

        self._limit = limit

    @property
    def next(self):
        """Gets the next of this Payouts.  # noqa: E501

        The <b>getPayouts</b> call URI to use if you wish to view the next page of the result set. <br><br>This field is only returned if there is a next page of results to view based on the current input criteria.  # noqa: E501

        :return: The next of this Payouts.  # noqa: E501
        :rtype: str
        """
        return self._next

    @next.setter
    def next(self, next):
        """Sets the next of this Payouts.

        The <b>getPayouts</b> call URI to use if you wish to view the next page of the result set. <br><br>This field is only returned if there is a next page of results to view based on the current input criteria.  # noqa: E501

        :param next: The next of this Payouts.  # noqa: E501
        :type: str
        """

        self._next = next

    @property
    def offset(self):
        """Gets the offset of this Payouts.  # noqa: E501

        This integer value indicates the actual position that the first payout returned on the current page has in the results set. So, if you wanted to view the 11th payout of the result set, you would set the <strong>offset</strong> value in the request to <code>10</code>. <br><br>In the request, you can use the <b>offset</b> parameter in conjunction with the <b>limit</b> parameter to control the pagination of the output. For example, if <b>offset</b> is set to <code>30</code> and <b>limit</b> is set to <code>10</code>, the call retrieves payouts 31 thru 40 from the resulting collection of payouts. <br><br> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first item in the list has an offset of <code>0</code>.</span><br><br><b>Default:</b> <code>0</code> (zero)  # noqa: E501

        :return: The offset of this Payouts.  # noqa: E501
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset):
        """Sets the offset of this Payouts.

        This integer value indicates the actual position that the first payout returned on the current page has in the results set. So, if you wanted to view the 11th payout of the result set, you would set the <strong>offset</strong> value in the request to <code>10</code>. <br><br>In the request, you can use the <b>offset</b> parameter in conjunction with the <b>limit</b> parameter to control the pagination of the output. For example, if <b>offset</b> is set to <code>30</code> and <b>limit</b> is set to <code>10</code>, the call retrieves payouts 31 thru 40 from the resulting collection of payouts. <br><br> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first item in the list has an offset of <code>0</code>.</span><br><br><b>Default:</b> <code>0</code> (zero)  # noqa: E501

        :param offset: The offset of this Payouts.  # noqa: E501
        :type: int
        """

        self._offset = offset

    @property
    def payouts(self):
        """Gets the payouts of this Payouts.  # noqa: E501

        An array of one or more payouts that match the input criteria. Details for each payout include the unique identifier of the payout, the status of the payout, the amount of the payout, and the number of monetary transactions associated with the payout.  # noqa: E501

        :return: The payouts of this Payouts.  # noqa: E501
        :rtype: list[Payout]
        """
        return self._payouts

    @payouts.setter
    def payouts(self, payouts):
        """Sets the payouts of this Payouts.

        An array of one or more payouts that match the input criteria. Details for each payout include the unique identifier of the payout, the status of the payout, the amount of the payout, and the number of monetary transactions associated with the payout.  # noqa: E501

        :param payouts: The payouts of this Payouts.  # noqa: E501
        :type: list[Payout]
        """

        self._payouts = payouts

    @property
    def prev(self):
        """Gets the prev of this Payouts.  # noqa: E501

        The <b>getPayouts</b> call URI to use if you wish to view the previous page of the result set. <br><br>This field is only returned if there is a previous page of results to view based on the current input criteria.  # noqa: E501

        :return: The prev of this Payouts.  # noqa: E501
        :rtype: str
        """
        return self._prev

    @prev.setter
    def prev(self, prev):
        """Sets the prev of this Payouts.

        The <b>getPayouts</b> call URI to use if you wish to view the previous page of the result set. <br><br>This field is only returned if there is a previous page of results to view based on the current input criteria.  # noqa: E501

        :param prev: The prev of this Payouts.  # noqa: E501
        :type: str
        """

        self._prev = prev

    @property
    def total(self):
        """Gets the total of this Payouts.  # noqa: E501

        This integer value is the total number of payouts in the results set based on the current input criteria. Based on the total number of payouts that match the criteria, and on the <strong>limit</strong> and <strong>offset</strong> values, there may be additional pages in the results set.  # noqa: E501

        :return: The total of this Payouts.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this Payouts.

        This integer value is the total number of payouts in the results set based on the current input criteria. Based on the total number of payouts that match the criteria, and on the <strong>limit</strong> and <strong>offset</strong> values, there may be additional pages in the results set.  # noqa: E501

        :param total: The total of this Payouts.  # noqa: E501
        :type: int
        """

        self._total = total

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
        if issubclass(Payouts, dict):
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
        if not isinstance(other, Payouts):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
