# *** How to run these unit tests. ***
# 1. (Open a terminal, alternately known as go to the command line.)
# 2. cd .. (Or, somehow make the project root the current directory.)
# 3. python -m unittest tests.ebay_rest


# Standard library imports
import datetime
import unittest
import warnings

# Local imports
from src.ebay_rest import API, DateTime, Error, Reference


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # TODO Stop ignoring the warning and remedy the resource leak. How?
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        cls._api = API(use_sandbox=True, site_id='EBAY-ENCA')

    # test the load of all references

    def test_enum_load(self):
        self.assertIsNotNone(Reference.get_enums(), msg="Failed to load enums.")

    def test_container_load(self):
        self.assertIsNotNone(Reference.get_item_fields(), msg="Failed to load containers.")

    def test_global_id_values_load(self):
        self.assertIsNotNone(Reference.get_global_id_values(), msg="Failed to load global id values.")

    # check the return types of all date time functions
    def test_date_time_now(self):
        self.assertTrue(isinstance(DateTime.now(), datetime.date),
                        msg="Unexpected return type from a DateTime member function.")

    def test_date_time_from_string(self):
        self.assertTrue(isinstance(DateTime.from_string('2004-08-04T19:09:02.768Z'), datetime.date),
                        msg="Unexpected return type from a DateTime member function.")

    def test_date_time_to_string(self):
        self.assertTrue(isinstance(DateTime.to_string(DateTime.now()), str),
                        msg="Unexpected return type from a DateTime member function.")

    # test positional and kw arguments to ebay api calls

    def test_positional_zero_kw_none(self):
        self.assertIsNotNone(self._api.developer_analytics_get_rate_limits(),
                             msg="A call with zero positional and no kw arguments failed.")

    def test_positional_one_kw_none(self):

        items = self._api.buy_browse_search(q='silver')
        item_id = items['item_summaries'][0]['item_id']
        self.assertIsNotNone(self._api.buy_browse_get_item(item_id=item_id),
                             msg="A call with one positional and no kw arguments failed.")

    def test_positional_two_kw_none(self):
        pass    # TODO

    def test_positional_zero_kw_some(self):
        self.assertIsNotNone(self._api.buy_browse_search(q='gold'),
                             msg="A call with zero positional and no kw arguments failed.")

    def test_positional_one_kw_some(self):
        items = self._api.buy_browse_search(q='silver')
        item_id = items['item_summaries'][0]['item_id']
        self.assertIsNotNone(self._api.buy_browse_get_item(item_id=item_id, fieldgroups='PRODUCT'),
                             msg="A call with one positional and some kw arguments failed.")

    def test_positional_two_kw_some(self):
        pass  # TODO

    # Test that an exception occurs when expected.

    def test_try_except_else_api(self):
        try:
            self._api.buy_browse_get_item(item_id='invalid')
        except Error as error:
            self.assertIsNotNone(f'Error {error.number} is {error.reason} with detail {error.detail}.')
        else:
            self.assertIsNotNone(None, msg="Failed to raise an exception.")


if __name__ == '__main__':
    unittest.main()
