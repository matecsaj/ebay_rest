# Standard library imports
from datetime import datetime, timedelta, timezone


class DateTime:
    """ Helpers for the specific way that eBay does date-time. """

    _EBAY_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    def now():
        """ get the current time, as a python datetime object with eBay's timezone and precision
        Date-time values are in the ISO 8601 date and time format.
        Hours are in 24-hour format (e.g., 2:00:00pm is 14:00:00).
        Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT),
        also known as Zulu because the time portion of the time stamp ends with a Z """

        # TODO Precisely synchronize with eBay's clock.
        # https://ofr.ebay.ca/ws/eBayISAPI.dll?EbayTime  (only accurate to the second)
        # https://developer.ebay.com/Devzone/shopping/docs/CallRef/GeteBayTime.html
        # (not a REST-ful call, old SOAP)

        d_t = datetime.utcnow()
        excess_precision = timedelta(0, 0, d_t.microsecond - round(d_t.microsecond, -3))
        return d_t.replace(tzinfo=timezone.utc) - excess_precision

    @staticmethod
    def to_string(date_time):
        """ convert a python datetime object with eBay's timezone to an Ebay dateTime string
        string YYYY-MM-DDTHH:MM:SS.SSSZ (e.g., 2004-08-04T19:09:02.768Z) """
        string = date_time.strftime(DateTime._EBAY_DATE_FORMAT)
        return string[0:10] + 'T' + string[11:23] + 'Z'

    @staticmethod
    def from_string(date_time_string):
        """ convert an Ebay dateTime string string to a python datetime object with eBay's timezone
        string YYYY-MM-DDTHH:MM:SS.SSSZ (e.g., 2004-08-04T19:09:02.768Z) """
        d_t = datetime.strptime(date_time_string, DateTime._EBAY_DATE_FORMAT)
        return d_t.replace(tzinfo=timezone.utc)
