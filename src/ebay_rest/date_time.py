# Standard library imports
from datetime import datetime, timezone

# Local imports
from .error import Error


class DateTime:
    """ Helpers for the specific way that eBay does date-time. """

    _EBAY_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    def now() -> datetime:
        """
        Get the current time, as a python datetime object with eBay's timezone.

        Date-time values are in the ISO 8601 date and time format.
        Hours are in 24-hour format (e.g., 2:00:00pm is 14:00:00).
        Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT),
        also known as Zulu because the time portion of the time stamp ends with a Z.

        :return: datetime
        """
        # TODO Precisely synchronize with eBay's clock.
        # https://ofr.ebay.ca/ws/eBayISAPI.dll?EbayTime  (only accurate to the second)
        # https://developer.ebay.com/Devzone/shopping/docs/CallRef/GeteBayTime.html (not a REST-ful call, old SOAP)

        d_t = datetime.utcnow()
        return d_t.replace(tzinfo=timezone.utc)

    @staticmethod
    def to_string(d_t: datetime) -> str:
        """ convert a python datetime object with eBay's timezone to an Ebay dateTime string

        string YYYY-MM-DDTHH:MM:SS.SSSZ (e.g., 2004-08-04T19:09:02.768Z)

        :param
        date_time (datetime) :

        :return: str
        """
        if not isinstance(d_t, datetime):
            reason = 'The to_string parameter should be a datetime, not a ' + str(type(d_t)) + '.'
            raise Error(number=1, reason=reason)
        else:
            string = d_t.strftime(DateTime._EBAY_DATE_FORMAT)
            return string[0:10] + 'T' + string[11:23] + 'Z'

    @staticmethod
    def from_string(d_t_string: str) -> datetime:
        """ convert an Ebay dateTime string to a python datetime object with eBay's timezone

        string YYYY-MM-DDTHH:MM:SS.SSSZ (e.g., 2004-08-04T19:09:02.768Z)

        :param
        date_time_string (str) :

        :return: datetime
        """
        if not isinstance(d_t_string, str):
            reason = 'The from_string parameter should be a string, not a ' + str(type(d_t_string)) + '.'
            raise Error(number=1, reason=reason)
        else:
            d_t = datetime.strptime(d_t_string, DateTime._EBAY_DATE_FORMAT)
            return d_t.replace(tzinfo=timezone.utc)
