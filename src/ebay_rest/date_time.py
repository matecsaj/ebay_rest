# Standard library imports
from datetime import datetime
from zoneinfo import ZoneInfo

# Local imports
from .error import Error


class DateTime:
    """Helpers for the specific way that eBay does date-time."""

    _EBAY_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    _UTC = ZoneInfo("UTC")

    @staticmethod
    def now() -> datetime:
        """
        Get the current time as a python datetime object with eBay's timezone.

        Date-time values are in the ISO 8601 date and time format.
        Hours are in 24-hour format (e.g., 2:00:00pm is 14:00:00).
        Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT),
        also known as Zulu because the time portion of the time stamp ends with a Z.

        :return: datetime (datetime)
        """
        # TODO Precisely synchronize with eBay's clock.
        # https://ofr.ebay.ca/ws/eBayISAPI.dll?EbayTime  (only accurate to the second)
        # https://developer.ebay.com/Devzone/shopping/docs/CallRef/GeteBayTime.html (not a REST-ful call, old SOAP)
        return datetime.now(DateTime._UTC)

    @staticmethod
    def to_string(d_t: datetime) -> str:
        """
        Convert a python datetime object with eBay's timezone to an eBay dateTime string.

        Expected format: YYYY-MM-DDTHH:MM:SS.SSSZ (e.g., 2004-08-04T19:09:02.768Z)

        :param d_t: datetime (required)
        :return: dateTime string (str)
        """
        if not isinstance(d_t, datetime):
            reason = (
                "The to_string parameter should be a datetime, not a "
                + str(type(d_t))
                + "."
            )
            raise Error(number=98001, reason=reason)
        else:
            try:
                formatted = d_t.strftime(DateTime._EBAY_DATE_FORMAT)
            except ValueError as e:
                raise Error(number=98002, reason="Value Error.", cause=e)
            # Adjust the formatting to ensure we only include millisecond precision
            return formatted[0:10] + "T" + formatted[11:23] + "Z"

    @staticmethod
    def from_string(d_t_string: str) -> datetime:
        """
        Convert an eBay dateTime string to a python datetime object with eBay's timezone.

        Expected format: YYYY-MM-DDTHH:MM:SS.SSSZ (e.g., 2004-08-04T19:09:02.768Z)

        :param d_t_string: dateTime string (required)
        :return: datetime (datetime)
        """
        if not isinstance(d_t_string, str):
            reason = (
                "The from_string parameter should be a string, not a "
                + str(type(d_t_string))
                + "."
            )
            raise Error(number=98003, reason=reason)
        else:
            try:
                d_t = datetime.strptime(d_t_string, DateTime._EBAY_DATE_FORMAT)
            except ValueError as e:
                raise Error(
                    number=98004,
                    reason="date time string formatting error, should be like 2004-08-04T19:09:02.768Z",
                    detail=e.args[0],
                    cause=e,
                )
            # Ensure the datetime is timezone-aware with UTC using zoneinfo
            return d_t.replace(tzinfo=DateTime._UTC)
