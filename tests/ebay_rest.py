# Standard library imports
import unittest
import datetime

# Local imports
from src.ebay_rest import API, DateTime, Error, Reference


# Globals


# *** How to run these unit tests. ***
# 1. (Open a terminal, alternately known as go to the command line.)
# 2. cd .. (Or, somehow make the project root the current directory.)
# 3. python -m unittest tests.ebay_rest


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._api = API(use_sandbox=False, site_id='EBAY-ENCA')

    def test_enum_load(self):
        self.assertIsNotNone(Reference.get_enums(), msg="Failed to load enums.")

    def test_container_load(self):
        self.assertIsNotNone(Reference.get_item_fields(), msg="Failed to load containers.")

    def test_global_id_values_load(self):
        self.assertIsNotNone(Reference.get_global_id_values(), msg="Failed to load global id values.")

    def test_date_time_now(self):
        self.assertTrue(self, isinstance(DateTime.now(), datetime.date), msg="Failed to get a date time value.")

    def test_try_except_else(self):
        try:
            self._api.will_fail()
        except Error as error:
            print(f'Error {error.number} is {error.message}.')
        else:
            self.assertIsNotNone(None, msg="Failed to raise an exception.")

    def test_developer_analytics_get_rate_limits(self):
        self.assertIsNotNone(self._api.developer_analytics_get_rate_limits(),
                             msg="Failed at developer_analytics_get_rate_limits.")

    def test_developer_analytics_get_rate_limits_api_context(self):
        self.assertIsNotNone(self._api.developer_analytics_get_rate_limits(api_context='buy'),
                             msg="Failed at developer_analytics_get_rate_limits.")


if __name__ == '__main__':
    unittest.main()
