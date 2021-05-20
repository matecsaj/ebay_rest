# Standard library imports
from datetime import timedelta
import threading
import logging
import math
import time

# Local imports
from .date_time import DateTime
from .error import Error


class Rates:
    """ Manages call limit and utilization data for an eBay application.

    https://developer.ebay.com/api-docs/developer/analytics/resources/rate_limit/methods/getRateLimits
    """
    _lock = threading.Lock()    # secure this lock before updating or reading class variables
    _refresh_date_time = None   # the soonest it is advisable to refresh rates data from eBay
    _cache = None               # cache of the most recent rates re-organized to expedite lookups

    @staticmethod
    def decrement_rate(base_path: str, rate_keys: list) -> None:
        """
        Decrement the remaining count of calls associated with a name.

        Warning, avoid endless recursion, don't merge this with the throttled version of the method.

        :param
        base_path (str) :

        :param
        rate_keys (list) : Strings, keys used to lookup a rate

        :return: None
        """
        with Rates._lock:
            rate_dict = Rates.find_rate_dict(base_path, rate_keys)
            if rate_dict:
                if rate_dict['remaining'] > 0:
                    rate_dict['remaining'] -= 1

    @staticmethod
    def decrement_rate_throttled(base_path: str, rate_keys: list, timeout: float) -> None:
        """
        Decrement the remaining count of calls associated with a name.

        :param
        base_path (str) :

        :param
        rate_keys (list) : Strings, keys used to lookup a rate

        :param
        timeout (float) : When invoked with the floating-point timeout argument set to a positive value,
        throttle for at most the number of seconds specified by timeout and as below the prorated call limit. A timeout
        argument of -1 specifies an unbounded wait.

        :return: None
        """
        # The algorithm relies upon the geometrical properties of right-angled triangles.
        # Threshold is a line that extends from the height of the limit at the period start to zero at the end.
        # Further, imagine lowering the threshold half when throttled.
        # If not throttled, imagine lowering the threshold to 1.
        # It is OK to proceed when the remaining count is above the threshold.
        # If we need to wait, wait in proportion to how far the threshold is out of reach or until period end.

        timeout_used = 0
        redo = True
        while redo:
            Rates._lock.acquire()
            rate_dict = Rates.find_rate_dict(base_path, rate_keys)
            if rate_dict is None:
                redo = False
            else:
                limit = rate_dict['limit']
                reset = rate_dict['reset']
                time_window = rate_dict['time_window']

                delta = abs((DateTime.now() - reset).total_seconds())  # abs covers small clock errors
                threshold = ((delta * limit) / time_window) * 0.5
                if threshold < 1.0:
                    threshold = 1.0  # 1 is as low is it should go, protect against rounding errors

                remaining = rate_dict['remaining']
                if remaining >= math.ceil(threshold):

                    if remaining > 0:
                        rate_dict['remaining'] = remaining - 1
                    Rates._lock.release()
                    redo = False

                else:
                    # if there are no calls left in the current period
                    if remaining <= 0:
                        # then wait until the end of the period
                        wait_seconds = abs((DateTime.now() - reset).total_seconds())
                    else:
                        # otherwise wait for the remaining-threshold delta proportioned by remaining time
                        wait_seconds = ((threshold - remaining) * time_window) / limit

                    if timeout != -1.0:
                        timeout_remaining = timeout - timeout_used
                        if timeout_remaining <= 0:
                            raise Error(number=2, reason="Throttle timeout.")
                        if wait_seconds > timeout_remaining:      # don't wait any longer than the caller wants
                            wait_seconds = timeout_remaining

                    Rates._lock.release()
                    time.sleep(wait_seconds)
                    timeout_used += wait_seconds

    @staticmethod
    def find_rate_dict(base_path: str, rate_keys: list) -> dict or None:
        """
        Get the index so the rate object associated with a name.

        The caller must have a lock.

        https://developer.ebay.com/api-docs/developer/analytics/resources/rate_limit/methods/getRateLimits

        :param
        base_path (str) :

        :param
        rate_keys (list) : Strings, keys used to lookup a rate

        :return: a rates dict or None
        """
        cache = Rates._cache
        if not cache:
            return None
        else:
            [resource_name_base, resource_name_module] = rate_keys

            key = base_path + '|' + resource_name_base

            cache = Rates._cache
            if key in cache:
                result = cache[key]
            else:
                key = key + resource_name_module
                if key in cache:
                    result = cache[key]
                else:
                    logging.debug('Unable to find rates for: ' + key)
                    result = None

            return result

    @staticmethod
    def refresh_developer_analytics(rate_limits) -> None:
        """ Refresh the local Developer Analytics values and when the next refresh is recommended. """

        if not rate_limits:
            cache = None
            refresh_date_time = None

        else:
            cache = dict()      # stores the flattened rates records
            resets = set()      # stores unique reset date-times
            for rate_limit in rate_limits:
                base_path = '/'.join([rate_limit['api_context'], rate_limit['api_name'], rate_limit['api_version']])
                base_path = '/' + base_path.lower()
                for resource in rate_limit['resources']:
                    if resource['rates']:
                        if resource['rates'][0]:
                            if resource['rates'][0]['limit']:
                                key = base_path + '|' + resource['name']
                                rates = resource['rates'][0]
                                reset = DateTime.from_string(rates['reset'])
                                rates['reset'] = reset
                                resets.add(reset)
                                cache[key] = rates

            now = DateTime.now()

            # Another program may also be using up calls, so periodically synchronizing with eBay's counts.
            periodic = now + timedelta(minutes=15)

            # find the soonest reset
            soonest_reset = periodic    # safety, just in case they are no useful resets date-times
            resets = list(resets)
            resets.sort()
            for reset in resets:
                if reset >= now:            # skip when eBay is late to act on a reset
                    soonest_reset = reset
                    break

            # use which ever is sooner
            if periodic <= soonest_reset:
                refresh_date_time = periodic
            else:
                refresh_date_time = soonest_reset

        with Rates._lock:
            Rates._cache = cache
            Rates._rate_limits = rate_limits
            Rates._refresh_date_time = refresh_date_time

    @staticmethod
    def need_refresh() -> bool:
        """ Return True if the rates need refreshing. """
        with Rates._lock:
            if Rates._refresh_date_time:
                if Rates._refresh_date_time > DateTime.now():
                    result = False
                else:
                    result = True
            else:
                result = True
        return result
