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


class APIBid(unittest.TestCase):
    SANDBOX = True      # WARNING. If you change this to False, you will bid on live items.
    MARKETPLACE_ID = 'EBAY_US'

    def test_bid(self):
        # TODO Stop ignoring the warning and remedy the resource leak.
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        try:
            api = API(sandbox=self.SANDBOX, marketplace_id=self.MARKETPLACE_ID, throttle=True)
        except Error as error:
            self.assertTrue(False, f'Error {error.number} is {error.reason}  {error.detail}.\n')
        else:

            try:
                item_id = None
                item_currency = None
                keywords = 'silver'
                filter_ = 'buyingOptions:{AUCTION}'
                for item in api.buy_browse_search(q=keywords, filter=filter_, sort='price', limit=1):
                    item_id = item['item_id']
                    if item['price']['converted_from_currency']:
                        item_currency = item['price']['converted_from_currency']
                    else:
                        item_currency = item['price']['currency']
            except Error as error:
                self.assertTrue(False, f'Error {error.number} is {error.reason}  {error.detail}.\n')
            else:
                if item_id and item_currency:
                    body = {"maxAmount": {"currency": item_currency, "value": "5.00"}}
                    try:
                        # the marketplace has underscores and is a we bit different
                        # https://developer.ebay.com/api-docs/buy/static/ref-marketplace-supported.html
                        result = api.buy_offer_place_proxy_bid(x_ebay_c_marketplace_id='EBAY_US',
                                                               item_id=item_id, body=body)
                    except Error as error:
                        self.assertTrue(False, f'Error {error.number} is {error.reason}  {error.detail}.\n')
                    else:
                        self.assertTrue(True)
                else:
                    self.assertTrue(False, 'item_id or item_currency are None.')


class APIInitialization(unittest.TestCase):

    def test_uniqueness(self):
        a1 = API(sandbox=True, marketplace_id='EBAY_NL')
        a2 = API(marketplace_id='EBAY_NL', sandbox=True, )
        b = API(sandbox=True, marketplace_id='EBAY_ES')
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)


class APIOther(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # TODO Stop ignoring the warning and remedy the resource leak.
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        cls.sandbox = False    # True is better, eBay wants you to use the sandbox for testing
        if cls.sandbox:        # use keywords that will return >0 and < 10,000 results
            cls.q = 'silver'
        else:
            cls.q = 'silver snail'
        cls._api = API(sandbox=cls.sandbox, marketplace_id='EBAY_US')

    # test paging calls

    def test_paging_no_results(self):
        for item in self._api.buy_browse_search(q='atomic-donkey-kick--this-will-not-be-found-Geraldine'):
            self.assertTrue(isinstance(item['item_id'], str))
            self.assertTrue(False, msg='No items should be returned.')
            break

    def test_paging_limit_over_page_size(self):
        count = 0
        limit = 350
        for item in self._api.buy_browse_search(limit=limit, q=self.q):
            self.assertTrue(isinstance(item['item_id'], str))
            count += 1
            if count >= limit + 500:    # break out if way past the desired limit
                break
        self.assertTrue(count == limit)

    # test positional and kw arguments to ebay api calls

    def test_positional_zero_kw_none(self):
        self.assertIsNotNone(self._api.developer_analytics_get_rate_limits(),
                             msg="A call with zero positional and no kw arguments failed.")

    def test_positional_one_kw_none(self):

        for item in self._api.buy_browse_search(q=self.q):
            self.assertIsNotNone(self._api.buy_browse_get_item(item_id=item['item_id']),
                                 msg="A call with one positional and no kw arguments failed.")
            break

    def test_positional_two_kw_none(self):
        pass    # TODO

    def test_positional_zero_kw_some(self):
        self.assertIsNotNone(self._api.buy_browse_search(q=self.q),
                             msg="A call with zero positional and no kw arguments failed.")

    def test_positional_one_kw_some(self):
        for item in self._api.buy_browse_search(q=self.q):
            self.assertIsNotNone(self._api.buy_browse_get_item(item_id=item['item_id'], fieldgroups='PRODUCT'),
                                 msg="A call with one positional and some kw arguments failed.")
            break

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

    # Test things that have broken in the past

    def test_buying_options(self):
        """ Does buying option filtering work? """
        options = ['FIXED_PRICE', 'BEST_OFFER']
        if not self.sandbox:
            options.append('AUCTION')
        for option in options:
            try:
                success = None
                keywords = 'black'
                filter_ = 'buyingOptions:{' + option + '}'
                for item in self._api.buy_browse_search(q=keywords, filter=filter_, limit=500):
                    if option in item['buying_options']:
                        success = True
                    else:
                        success = False
                        break
            except Error as error:
                self.assertTrue(False, f'Error {error.number} is {error.reason}  {error.detail}.\n')
            else:
                message = 'The search for ' + option + ' items returned no items or a non-auction item.'
                self.assertTrue(success, message)


class APIThrottled(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # TODO Stop ignoring the warning and remedy the resource leak.
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        cls._api = API(sandbox=False, throttle=True, timeout=60.0)

    def test_finding_one_item(self):
        count = 0
        item_id = None
        for item in self._api.buy_browse_search(limit=1, q='lego'):
            self.assertTrue(isinstance(item['item_id'], str))
            item_id = item['item_id']
            count += 1
            break
        self.assertTrue(count == 1)
        if item_id:
            item = self._api.buy_browse_get_item(item_id=item_id)
            self.assertTrue(isinstance(item, dict))

    def test_finding_three_hundred_items(self):
        count = 0
        for item in self._api.buy_browse_search(limit=1, q='lego'):
            self.assertTrue(isinstance(item['item_id'], str))
            count += 1
            break
        self.assertTrue(count == 1)


class DateTimeTests(unittest.TestCase):

    def test_date_time_now(self):
        self.assertTrue(isinstance(DateTime.now(), datetime.date),
                        msg="Unexpected return type from a DateTime member function.")

    def test_date_time_from_string(self):
        self.assertTrue(isinstance(DateTime.from_string('2004-08-04T19:09:02.768Z'), datetime.date),
                        msg="Unexpected return type from a DateTime member function.")

    def test_date_time_to_string(self):
        self.assertTrue(isinstance(DateTime.to_string(DateTime.now()), str),
                        msg="Unexpected return type from a DateTime member function.")


class ReferenceTests(unittest.TestCase):

    def test_enum_load(self):
        self.assertIsNotNone(Reference.get_item_enums_modified(), msg="Failed to load enums.")

    def test_container_load(self):
        self.assertIsNotNone(Reference.get_item_fields_modified(), msg="Failed to load containers.")

    def test_global_id_values_load(self):
        self.assertIsNotNone(Reference.get_global_id_values(), msg="Failed to load global id values.")

    def test_marketplace_id_values_load(self):
        self.assertIsNotNone(Reference.get_marketplace_id_values(), msg="Failed to load marketplace id values.")


if __name__ == '__main__':
    unittest.main()
