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
    _rate_limits = None         # a recent cache of the rates limits from eBay
    _periodic_refresh_date_time = None    # when the next update to _rate_limits is recommended for
    _soonest_reset = None       # the soonest date-time when a daily limit will reset

    @staticmethod
    def decrement_rate(rate_keys: list):
        """
        Decrement the remaining count of calls associated with a name.

        Warning, avoid endless recursion, don't merge this with the throttled version of the method.

        :param
        rate (list) : Strings, keys used to lookup a rate
        """
        with Rates._lock:
            rate_dict = Rates.find_rate_dict(rate_keys)
            if rate_dict:
                if rate_dict['remaining'] > 0:
                    rate_dict['remaining'] -= 1

    @staticmethod
    def decrement_rate_throttled(rate_keys: list, timeout: float):
        """
        Decrement the remaining count of calls associated with a name.

        :param
        name (str): 'buy.browse.item.bulk', 'buy.browse', 'buy.feed.snapshot', 'buy.feed',
                 'buy.marketing', 'buy.order', 'buy.deal.event_item', 'buy.deal.event',
                 'buy.deal.deal_item', 'buy.offer.bidding',
                 'developer.analytics.user_rate_limit', 'developer.analytics.app_rate_limit'

        :param
        rate (list) : Strings, keys used to lookup a rate
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
            rate_dict = Rates.find_rate_dict(rate_keys)
            if rate_dict is None:
                redo = False
            else:
                limit = rate_dict['limit']
                reset = DateTime.from_string(rate_dict['reset'])
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
    def find_rate_dict(rate):
        """
        Get the index so the rate object associated with a name.

        https://developer.ebay.com/api-docs/developer/analytics/resources/rate_limit/methods/getRateLimits
        """
        if not Rates._rate_limits:
            return None

        else:
            [api_context, api_name, api_version, resource_name_base, resource_name_module] = rate
            rates_base = None
            rates_base_module = None
            resource_name_base_module = resource_name_base + '.' + resource_name_module

            rate_limits = Rates._rate_limits    # this debugging aid exposes the class variable
            for rate_limit in rate_limits:
                if rate_limit['api_context'] == api_context and rate_limit['api_name'] == api_name \
                        and rate_limit['api_version'] == api_version:
                    for resource in rate_limit['resources']:
                        name = resource['name']
                        if name == resource_name_base:
                            rates_base = resource['rates'][0]
                        if name == resource_name_base_module:
                            rates_base_module = resource['rates'][0]
                break

            if rates_base_module:
                return rates_base_module
            elif rates_base:
                return rates_base
            else:
                message = 'Unable to find rates for'
                for element in rate:
                    message += message + ' ' + element
                message = message + '.'
                logging.debug(message)
                return None

    @staticmethod
    def soonest_reset():
        """ Get soonest date-time string for when a rate limit down counter will be reset at eBay. """

        resets = set()
        rate_limits = Rates._rate_limits    # this debugging aid exposes the class variable
        if rate_limits:
            for rate_limit in rate_limits:
                for resource in rate_limit['resources']:
                    if resource['rates']:
                        for rate in resource['rates']:
                            resets.add(rate['reset'])

        resets = list(resets)
        resets.sort()

        if resets:
            return resets[0]
        else:
            return None

    @staticmethod
    def refresh_developer_analytics(rate_limits):
        """ Refresh the local Developer Analytics values. """
        with Rates._lock:
            Rates._rate_limits = rate_limits
            Rates._periodic_refresh_date_time = DateTime.now() + timedelta(minutes=15)
            soonest = DateTime.from_string(Rates.soonest_reset())
            Rates._soonest_reset = soonest + timedelta(seconds=5)  # extra 5 in case of clock differences

    @staticmethod
    def need_refresh():
        """ Return True if the rates need refreshing.

        Another program could be running currently, so it is important to periodically re-synchronize.
        """
        with Rates._lock:
            if not Rates._rate_limits or not Rates._periodic_refresh_date_time or not Rates._soonest_reset:
                result = True
            else:
                now = DateTime.now()
                if Rates._periodic_refresh_date_time < now:    # an independent program may be running
                    result = True
                elif Rates._soonest_reset < now:  # an independent program may be running
                    result = True
                else:
                    result = False
        return result
