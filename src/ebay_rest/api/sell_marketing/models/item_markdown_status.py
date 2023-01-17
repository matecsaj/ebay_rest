# coding: utf-8

"""
    Marketing API

    <p>The <i>Marketing API </i> offers two platforms that sellers can use to promote and advertise their products:</p> <ul><li><b>Promoted Listings</b> is an eBay ad service that lets sellers set up <i>ad campaigns </i> for the products they want to promote. eBay displays the ads in search results and in other marketing modules as <b>SPONSORED</b> listings. If an item in a Promoted Listings campaign sells, the seller is assessed a Promoted Listings fee, which is a seller-specified percentage applied to the sales price. For complete details, refer to the <a href=\"/api-docs/sell/static/marketing/pl-landing.html\">Promoted Listings playbook</a>.</li><li><b>Promotions Manager</b> gives sellers a way to offer discounts on specific items as a way to attract buyers to their inventory. Sellers can set up discounts (such as \"20% off\" and other types of offers) on specific items or on an entire customer order. To further attract buyers, eBay prominently displays promotion <i>teasers</i> throughout buyer flows. For complete details, see <a href=\"/api-docs/sell/static/marketing/promotions-manager.html\">Promotions Manager</a>.</li></ul>  <p><b>Marketing reports</b>, on both the Promoted Listings and Promotions Manager platforms, give sellers information that shows the effectiveness of their marketing strategies. The data gives sellers the ability to review and fine tune their marketing efforts.</p> <p class=\"tablenote\"><b>Important!</b> Sellers must have an active eBay Store subscription, and they must accept the <b>Terms and Conditions</b> before they can make requests to these APIs in the Production environment. There are also site-specific listings requirements and restrictions associated with these marketing tools, as listed in the \"requirements and restrictions\" sections for <a href=\"/api-docs/sell/marketing/static/overview.html#PL-requirements\">Promoted Listings</a> and <a href=\"/api-docs/sell/marketing/static/overview.html#PM-requirements\">Promotions Manager</a>.</p> <p>The table below lists all the Marketing API calls grouped by resource.</p>  # noqa: E501

    OpenAPI spec version: v1.14.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ItemMarkdownStatus(object):
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
        'listing_markdown_status': 'str',
        'status_changed_date': 'str',
        'status_message': 'str'
    }

    attribute_map = {
        'listing_markdown_status': 'listingMarkdownStatus',
        'status_changed_date': 'statusChangedDate',
        'status_message': 'statusMessage'
    }

    def __init__(self, listing_markdown_status=None, status_changed_date=None, status_message=None):  # noqa: E501
        """ItemMarkdownStatus - a model defined in Swagger"""  # noqa: E501
        self._listing_markdown_status = None
        self._status_changed_date = None
        self._status_message = None
        self.discriminator = None
        if listing_markdown_status is not None:
            self.listing_markdown_status = listing_markdown_status
        if status_changed_date is not None:
            self.status_changed_date = status_changed_date
        if status_message is not None:
            self.status_message = status_message

    @property
    def listing_markdown_status(self):
        """Gets the listing_markdown_status of this ItemMarkdownStatus.  # noqa: E501

        Indicates the state assigned to the markdown promotion using one of the <b>status</b> values. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/marketing/types/sme:ItemMarkdownStatusEnum'>eBay API documentation</a>  # noqa: E501

        :return: The listing_markdown_status of this ItemMarkdownStatus.  # noqa: E501
        :rtype: str
        """
        return self._listing_markdown_status

    @listing_markdown_status.setter
    def listing_markdown_status(self, listing_markdown_status):
        """Sets the listing_markdown_status of this ItemMarkdownStatus.

        Indicates the state assigned to the markdown promotion using one of the <b>status</b> values. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/marketing/types/sme:ItemMarkdownStatusEnum'>eBay API documentation</a>  # noqa: E501

        :param listing_markdown_status: The listing_markdown_status of this ItemMarkdownStatus.  # noqa: E501
        :type: str
        """

        self._listing_markdown_status = listing_markdown_status

    @property
    def status_changed_date(self):
        """Gets the status_changed_date of this ItemMarkdownStatus.  # noqa: E501

        Identifies the date the last time the state of the promotion changed. Both both markdown and markup events can trigger a status change.  # noqa: E501

        :return: The status_changed_date of this ItemMarkdownStatus.  # noqa: E501
        :rtype: str
        """
        return self._status_changed_date

    @status_changed_date.setter
    def status_changed_date(self, status_changed_date):
        """Sets the status_changed_date of this ItemMarkdownStatus.

        Identifies the date the last time the state of the promotion changed. Both both markdown and markup events can trigger a status change.  # noqa: E501

        :param status_changed_date: The status_changed_date of this ItemMarkdownStatus.  # noqa: E501
        :type: str
        """

        self._status_changed_date = status_changed_date

    @property
    def status_message(self):
        """Gets the status_message of this ItemMarkdownStatus.  # noqa: E501

        An eBay-assigned text string that describes the status of the promotion.  # noqa: E501

        :return: The status_message of this ItemMarkdownStatus.  # noqa: E501
        :rtype: str
        """
        return self._status_message

    @status_message.setter
    def status_message(self, status_message):
        """Sets the status_message of this ItemMarkdownStatus.

        An eBay-assigned text string that describes the status of the promotion.  # noqa: E501

        :param status_message: The status_message of this ItemMarkdownStatus.  # noqa: E501
        :type: str
        """

        self._status_message = status_message

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
        if issubclass(ItemMarkdownStatus, dict):
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
        if not isinstance(other, ItemMarkdownStatus):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other