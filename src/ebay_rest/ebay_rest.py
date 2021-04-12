# Standard library imports
import json
import logging
import os

# Third party imports

# Local imports
from oath.credentialutil import credentialutil
from oath.model.model import environment
from oath.oauth2api import oauth2api

import api.buy_feed
from api.buy_feed.rest import ApiException

# Refrain from editing the anchors or in-between code; the script process_api_cache.py generates the code.
# ANCHOR-{er_imports}-START"
# ANCHOR-{er_imports}-END"


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
