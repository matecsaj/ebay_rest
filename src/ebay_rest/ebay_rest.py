# Standard library imports
import json
import logging
import os

# Third party imports

# Local imports
from oath.credentialutil import credentialutil
from oath.model.model import environment
from oath.oauth2api import oauth2api

# Refrain from editing the anchors or in-between code; the script process_api_cache.py generates the code.
# ANCHOR-er_imports-START"
import api.buy_browse
from api.buy_browse.rest import ApiException
import api.buy_deal
from api.buy_deal.rest import ApiException
import api.buy_feed
from api.buy_feed.rest import ApiException
import api.buy_marketing
from api.buy_marketing.rest import ApiException
import api.buy_marketplace_insights
from api.buy_marketplace_insights.rest import ApiException
import api.buy_offer
from api.buy_offer.rest import ApiException
import api.buy_order
from api.buy_order.rest import ApiException
import api.commerce_catalog
from api.commerce_catalog.rest import ApiException
import api.commerce_charity
from api.commerce_charity.rest import ApiException
import api.commerce_identity
from api.commerce_identity.rest import ApiException
import api.commerce_notification
from api.commerce_notification.rest import ApiException
import api.commerce_taxonomy
from api.commerce_taxonomy.rest import ApiException
import api.commerce_translation
from api.commerce_translation.rest import ApiException
import api.developer_analytics
from api.developer_analytics.rest import ApiException
import api.sell_account
from api.sell_account.rest import ApiException
import api.sell_analytics
from api.sell_analytics.rest import ApiException
import api.sell_compliance
from api.sell_compliance.rest import ApiException
import api.sell_feed
from api.sell_feed.rest import ApiException
import api.sell_finances
from api.sell_finances.rest import ApiException
import api.sell_fulfillment
from api.sell_fulfillment.rest import ApiException
import api.sell_inventory
from api.sell_inventory.rest import ApiException
import api.sell_listing
from api.sell_listing.rest import ApiException
import api.sell_logistics
from api.sell_logistics.rest import ApiException
import api.sell_marketing
from api.sell_marketing.rest import ApiException
import api.sell_metadata
from api.sell_metadata.rest import ApiException
import api.sell_negotiation
from api.sell_negotiation.rest import ApiException
import api.sell_recommendation
from api.sell_recommendation.rest import ApiException
# ANCHOR-er_imports-END"


# Globals


class _Error(Exception):
    """An abstract base class for exceptions in this module."""
    pass


class EbayRestError(_Error):

    def __init__(self, number, message):
        self.number = number
        self.message = message

    def __str__(self):
        return f'Error {self.number} is {self.message}.'


class _Singleton(object):
    """ An abstract base class used to make Singletons.
    The singleton software design pattern restricts the instantiation of a class to one "single" instance.
    This is useful when exactly one object is needed to coordinate actions across the system.
    """
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


# class EbayRest(_Singleton):    # TODO If init parameters repeat then use a singleton to conserve resources.
class EbayRest:
    """ """

    def __init__(self, my_string):
        self.my_string = my_string
        self._containers = None
        self._enums = None
        return

    def print(self):
        print(self.my_string)

    def will_fail(self):
        raise EbayRestError(0, "Sample error.")

    def get_containers(self):
        """ """
        # if the data needs caching
        if self._containers is None:
            # get the path to this python file, which is also where the data file is
            path, _fn = os.path.split(os.path.realpath(__file__))
            # to the path join the data file name and extension
            path_name = os.path.join(path, 'containers.json')
            with open(path_name) as f:
                self._containers = json.load(f)
        return self._containers

    def get_enums(self):
        """ """
        # if the data needs caching
        if self._enums is None:
            # get the path to this python file, which is also where the data file is
            path, _fn = os.path.split(os.path.realpath(__file__))
            # to the path join the data file name and extension
            path_name = os.path.join(path, 'enums.json')
            with open(path_name) as f:
                self._enums = json.load(f)
        return self._enums

    @staticmethod
    def true():
        return True
