# coding: utf-8

"""
    Analytics API

    The <i>Analytics API</i> provides data and information about a seller and their eBay business.  <br><br>The resources and methods in this API let sellers review information on their listing performance, metrics on their customer service performance, and details on their eBay seller performance rating.  <br><br>The three resources in the Analytics API provide the following data and information: <ul><li><b>Customer Service Metric</b> &ndash; Returns benchmark data and a metric rating pertaining to a seller's customer service performance as compared to other seller's in the same peer group.</li> <li><b>Traffic Report</b> &ndash; Returns data and information that shows how buyers are engaging with a seller's listings.</li> <li><b>Seller Standards Profile</b> &ndash; Returns information pertaining to a seller's profile rating.</li></ul> Sellers can use the data and information returned by the various Analytics API methods to determine where they can make improvements to increase sales and how they might improve their seller status as viewed by eBay buyers.  <br><br>For details on using this API, see <a href=\"/api-docs/sell/static/performance/analyzing-performance.html\" title=\"Selling Integration Guide\">Analyzing seller performance</a>.  # noqa: E501

    OpenAPI spec version: 1.3.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Report(object):
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
        'dimension_metadata': 'list[Metadata]',
        'end_date': 'str',
        'header': 'Header',
        'last_updated_date': 'str',
        'records': 'list[Record]',
        'start_date': 'str',
        'warnings': 'list[Error]'
    }

    attribute_map = {
        'dimension_metadata': 'dimensionMetadata',
        'end_date': 'endDate',
        'header': 'header',
        'last_updated_date': 'lastUpdatedDate',
        'records': 'records',
        'start_date': 'startDate',
        'warnings': 'warnings'
    }

    def __init__(self, dimension_metadata=None, end_date=None, header=None, last_updated_date=None, records=None, start_date=None, warnings=None):  # noqa: E501
        """Report - a model defined in Swagger"""  # noqa: E501
        self._dimension_metadata = None
        self._end_date = None
        self._header = None
        self._last_updated_date = None
        self._records = None
        self._start_date = None
        self._warnings = None
        self.discriminator = None
        if dimension_metadata is not None:
            self.dimension_metadata = dimension_metadata
        if end_date is not None:
            self.end_date = end_date
        if header is not None:
            self.header = header
        if last_updated_date is not None:
            self.last_updated_date = last_updated_date
        if records is not None:
            self.records = records
        if start_date is not None:
            self.start_date = start_date
        if warnings is not None:
            self.warnings = warnings

    @property
    def dimension_metadata(self):
        """Gets the dimension_metadata of this Report.  # noqa: E501

        A complex type containing the header of the report and the type of data containted in the rows of the report.  # noqa: E501

        :return: The dimension_metadata of this Report.  # noqa: E501
        :rtype: list[Metadata]
        """
        return self._dimension_metadata

    @dimension_metadata.setter
    def dimension_metadata(self, dimension_metadata):
        """Sets the dimension_metadata of this Report.

        A complex type containing the header of the report and the type of data containted in the rows of the report.  # noqa: E501

        :param dimension_metadata: The dimension_metadata of this Report.  # noqa: E501
        :type: list[Metadata]
        """

        self._dimension_metadata = dimension_metadata

    @property
    def end_date(self):
        """Gets the end_date of this Report.  # noqa: E501

          <br><br>The time stamp is formatted as an <a href=\"https://www.iso.org/iso-8601-date-and-time-format.html\" target=\"_blank\">ISO 8601</a> string, which is based on the 24-hour Universal Coordinated Time (UTC) clock.  <br><br>If you specify an end date that is beyond the <a href=\"#response.lastUpdatedDate\">lastUpdatedDate</a> value, eBay returns a report that contains data only up to the lastUpdateDate date. <br><br><b>Format:</b> <code>[YYYY]-[MM]-[DD]T[hh]:[mm]:[ss].[sss]Z</code> <br><b>Example:</b> <code>2018-08-20T07:09:00.000Z</code>  # noqa: E501

        :return: The end_date of this Report.  # noqa: E501
        :rtype: str
        """
        return self._end_date

    @end_date.setter
    def end_date(self, end_date):
        """Sets the end_date of this Report.

          <br><br>The time stamp is formatted as an <a href=\"https://www.iso.org/iso-8601-date-and-time-format.html\" target=\"_blank\">ISO 8601</a> string, which is based on the 24-hour Universal Coordinated Time (UTC) clock.  <br><br>If you specify an end date that is beyond the <a href=\"#response.lastUpdatedDate\">lastUpdatedDate</a> value, eBay returns a report that contains data only up to the lastUpdateDate date. <br><br><b>Format:</b> <code>[YYYY]-[MM]-[DD]T[hh]:[mm]:[ss].[sss]Z</code> <br><b>Example:</b> <code>2018-08-20T07:09:00.000Z</code>  # noqa: E501

        :param end_date: The end_date of this Report.  # noqa: E501
        :type: str
        """

        self._end_date = end_date

    @property
    def header(self):
        """Gets the header of this Report.  # noqa: E501


        :return: The header of this Report.  # noqa: E501
        :rtype: Header
        """
        return self._header

    @header.setter
    def header(self, header):
        """Sets the header of this Report.


        :param header: The header of this Report.  # noqa: E501
        :type: Header
        """

        self._header = header

    @property
    def last_updated_date(self):
        """Gets the last_updated_date of this Report.  # noqa: E501

        The date and time, in ISO 8601 format, that indicates the last time the data returned in the report was updated.  # noqa: E501

        :return: The last_updated_date of this Report.  # noqa: E501
        :rtype: str
        """
        return self._last_updated_date

    @last_updated_date.setter
    def last_updated_date(self, last_updated_date):
        """Sets the last_updated_date of this Report.

        The date and time, in ISO 8601 format, that indicates the last time the data returned in the report was updated.  # noqa: E501

        :param last_updated_date: The last_updated_date of this Report.  # noqa: E501
        :type: str
        """

        self._last_updated_date = last_updated_date

    @property
    def records(self):
        """Gets the records of this Report.  # noqa: E501

        A complex type containing the individual data records for the traffic report.  # noqa: E501

        :return: The records of this Report.  # noqa: E501
        :rtype: list[Record]
        """
        return self._records

    @records.setter
    def records(self, records):
        """Sets the records of this Report.

        A complex type containing the individual data records for the traffic report.  # noqa: E501

        :param records: The records of this Report.  # noqa: E501
        :type: list[Record]
        """

        self._records = records

    @property
    def start_date(self):
        """Gets the start_date of this Report.  # noqa: E501

        The start date of the date range used to calculate the report, in ISO 8601 format.  # noqa: E501

        :return: The start_date of this Report.  # noqa: E501
        :rtype: str
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """Sets the start_date of this Report.

        The start date of the date range used to calculate the report, in ISO 8601 format.  # noqa: E501

        :param start_date: The start_date of this Report.  # noqa: E501
        :type: str
        """

        self._start_date = start_date

    @property
    def warnings(self):
        """Gets the warnings of this Report.  # noqa: E501

        An array of any process errors or warnings that were generated during the processing of the call processing.  # noqa: E501

        :return: The warnings of this Report.  # noqa: E501
        :rtype: list[Error]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this Report.

        An array of any process errors or warnings that were generated during the processing of the call processing.  # noqa: E501

        :param warnings: The warnings of this Report.  # noqa: E501
        :type: list[Error]
        """

        self._warnings = warnings

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
        if issubclass(Report, dict):
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
        if not isinstance(other, Report):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
