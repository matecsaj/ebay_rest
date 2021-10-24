# *** A way to run these unit tests. ***
# 1. (Open a terminal, alternately known as go to the command line.)
# 2. cd .. (Or, somehow make the project root the current directory.)
# 3. python -m unittest tests.ebay_rest

# Don't repeat API calls with the same parameters, because it appears to trigger an "Internal (Server) Error" at eBay.

# Whenever possible, run tests on the sandbox instead of production.

# Standard library imports
import datetime
import json
import os
import unittest
import warnings

# 3rd party libraries
from currency_converter import CurrencyConverter

# Local imports
from src.ebay_rest import API, DateTime, Error, Reference


# TODO Lines like the following should go. Stop ignoring the warning and remedy the resource leak.
# warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

class APIBothEnvironmentsSingleSiteTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

    def test_start(self):  # all initialization options and for each the first and second usage
        for environment in ('production', 'sandbox'):
            for (throttle, timeout) in ((False, None), (True, None), (True, 60.0)):
                try:
                    if timeout is None:
                        api = API(application=environment + '_1', user=environment + '_1',
                                  header='US', throttle=throttle)
                    else:
                        api = API(application=environment + '_1', user=environment + '_1',
                                  header='US', throttle=throttle, timeout=timeout)
                except Error as error:
                    self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
                else:
                    try:
                        item_id = None
                        for record in api.buy_browse_search(limit=1, q='lego'):
                            if 'record' not in record:
                                self.assertTrue('total' in record, f'Unexpected non-record{record}.')
                            else:
                                item = record['record']
                                self.assertTrue(isinstance(item['item_id'], str))
                                item_id = item['item_id']
                                break
                    except Error as error:
                        self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
                    else:
                        if item_id:
                            try:
                                item = api.buy_browse_get_item(item_id=item_id)
                                self.assertTrue(isinstance(item, dict))
                            except Error as error:
                                self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')


class APISandboxMultipleSiteTests(unittest.TestCase):
    """ API test that require multiple marketplaces and that can be done on the sandbox. """

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        cls.currency_converter = CurrencyConverter()  # this is slow, so do it once

    def test_credentials_from_dicts(self):
        """ set credentials via dicts """
        try:
            with open('ebay_rest.json', 'r') as f:
                contents = json.loads(f.read())
        except IOError:
            raise Error(number=1, reason="Unable to open the file ebay_rest.json from the test directory.")
        else:

            application = None
            if 'applications' in contents:
                if 'sandbox_1' in contents['applications']:
                    application = contents['applications']['sandbox_1']
            self.assertIsInstance(application, dict, 'Failed to load application credentials.')

            user = None
            if 'users' in contents:
                if 'sandbox_1' in contents['users']:
                    user = contents['users']['sandbox_1']
            self.assertIsInstance(user, dict, 'Failed to load user credentials.')

            header = None
            if 'headers' in contents:
                if 'US' in contents['headers']:
                    header = contents['headers']['US']
            self.assertIsInstance(header, dict, 'Failed to load header credentials.')

            try:
                api = API(application=application, user=user, header=header)  # params are dicts
            except Error as error:
                self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
            else:
                # Ignore the PyCharm linter bug 'Expected type 'Union[type, Tuple[type, ...]]', got 'Multiton' instead'
                self.assertIsInstance(api, API, 'An API object was not returned.')  # type: ignore

    def test_object_reuse(self):
        """ Do the same parameters return the same API object? """
        a1 = API(application='sandbox_1', user='sandbox_1', header='ENCA')
        a2 = API(application='sandbox_1', user='sandbox_1', header='ENCA')
        b = API(application='sandbox_1', user='sandbox_1', header='GB')
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)

    def test_credential_path(self):
        """ supply a path to ebay_rest.json """
        path = os.getcwd()
        try:
            api = API(path=path, application='sandbox_1', user='sandbox_1', header='US')
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
        else:
            # Ignore the PyCharm linter bug 'Expected type 'Union[type, Tuple[type, ...]]', got 'Multiton' instead'
            self.assertIsInstance(api, API, 'An API object was not returned.')  # type: ignore

    def test_shipping_accuracy(self):
        """ Is closer shipping cheaper? """

        # domestic
        # d_market = 'EBAY_ENCA'    # set in header
        d_country = 'CA'
        d_currency = 'CAD'
        # d_zip = 'K1M 1M4'         # set in header

        # foreign
        # f_market = 'EBAY_GB'      # set in header
        f_country = 'GB'
        # f_currency = 'GBP'
        # f_zip = 'SW1A 1AA'        # set in header

        # more constants
        shipping_currency = 'USD'

        tally = 0  # how many times domestic shipping is cheaper than foreign

        d_api = API(application='production_1', user='production_1', header='ENCA')
        f_api = API(application='production_1', user='production_1', header='GB')

        # in the local marketplace find items located locally that also ship to foreign
        # low priced items are targeted because free shipping for them is unlikely
        # black items are targeted because they are plentiful, and the q parameter is mandatory
        try:
            filter_ = f'deliveryCountry:{f_country},itemLocationCountry:{d_country},price:[1..2],' \
                      f'priceCurrency:{d_currency} '

            for record in d_api.buy_browse_search(q='black', filter=filter_, limit=10):
                if 'record' not in record:
                    self.assertTrue('total' in record, f'Unexpected non-record{record}.')
                else:
                    item = record['record']
                    item_id = item['item_id']
                    if item['item_location']['country'] == d_country:
                        # get the lowest domestic shipping cost
                        try:
                            d_item = d_api.buy_browse_get_item(item_id=item_id, fieldgroups='PRODUCT')
                        except Error as error:
                            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
                        d_shipping = self._get_lowest_shipping(d_item, d_country, shipping_currency)

                        # get the lowest foreign shipping cost
                        try:
                            f_item = f_api.buy_browse_get_item(item_id=item_id, fieldgroups='PRODUCT')
                        except Error as error:
                            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
                        f_shipping = self._get_lowest_shipping(f_item, f_country, shipping_currency)

                        # compare costs, inconclusive when equal or some None
                        if (d_shipping is not None) and (f_shipping is not None):
                            if d_shipping < f_shipping:
                                tally += 1  # what we would expect most of the time
                            elif d_shipping > f_shipping:
                                tally -= 1  # very rare, put a break point here find trouble
                            else:
                                tally = tally  # flat rate world wide shipping is possible
                        else:
                            pass  # self.fail(f'For {item_id} both shipping costs can not be found.')
                    else:
                        self.fail(f'Item {item_id} is supposed to be located in {d_country}.')

        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')

        self.assertTrue(tally > 0, "Domestic shipping should cost less than foreign.")

    def _get_lowest_shipping(self, item, country, currency):

        costs = []

        # is shipping excluded?
        ship_to_locations = item['ship_to_locations']
        if ship_to_locations:
            if self._in_region(ship_to_locations['region_excluded'] or [], country):
                return None
            # if not in either list, then eBay concludes that shipping is allowed, so skip the following
            # elif not self._in_region(ship_to_locations['region_included'], country):
            # return None

        # find all costs
        if not item['shipping_options']:
            return None
        for shipping_option in item['shipping_options']:
            shipping_cost = shipping_option['shipping_cost']
            if shipping_cost['currency'] == currency:
                cost = float(shipping_cost['value'])
            elif shipping_cost['converted_from_currency'] == currency:
                cost = float(shipping_cost['converted_from_value'])
            else:
                cost = self.currency_converter.convert(float(shipping_cost['value']),
                                                       shipping_cost['currency'], currency)
            if cost is not None:
                costs.append(cost)
            else:
                self.fail('A shipping cost, without a cost, should not be possible.')

        if costs:
            costs.sort()
            return costs[0]
        else:
            self.fail('Shipping options without any options, should not be possible.')

    def _in_region(self, regions, country):

        if country in ('CA', 'US'):
            region_ids = ('AMERICAS', 'NORTH_AMERICA')
        elif country in ('GB',):
            region_ids = ('EUROPE',)
        else:
            self.fail('add region ids for your country')

        for region in regions:
            region_type = region['region_type']
            if region_type == 'COUNTRY':
                if region['region_id'] == country:
                    return True
            elif region_type == 'WORLD_REGION':
                if region['region_id'] in region_ids:
                    return True
            elif region_type == 'WORLDWIDE':
                return True
        return False


class APISandboxSingleSiteTests(unittest.TestCase):
    """" API tests that can be done on a single marketplace and in the sandbox. """

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        try:
            cls._api = API(application='sandbox_1', user='sandbox_1', header='US')
        except Error as error:
            cls.number = error.number
            cls.reason = error.reason
            cls.detail = error.detail
        else:
            cls.number = None

    def setUp(self):
        if self.number is not None:
            self.fail(f'Error {self.number} is {self.reason}  {self.detail}.\n')

    def test_paging_no_results(self):
        for record in self._api.buy_browse_search(q='atomic-donkey-kick--this-will-not-be-found-Geraldine'):
            if 'record' not in record:
                self.assertTrue('total' in record, f'Unexpected non-record{record}.')
                self.assertEqual(record['total']['records_yielded'], 0)
                self.assertEqual(record['total']['records_available'], 0)
            else:
                item = record['record']
                self.assertTrue(isinstance(item['item_id'], str), "Malformed item.")
                self.fail(msg='No items should be returned.')

    def test_positional_none_kw_none(self):
        """ Try a call with no positional arguments and no keyword arguments. """
        try:
            result = self._api.sell_compliance_get_listing_violations_summary()
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
        else:
            msg = "A call with zero positional and no kw arguments failed."
            self.assertIsNotNone('violation_summaries' in result, msg=msg)

    def test_positional_some_kw_none(self):
        # https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getDefaultCategoryTreeId
        try:
            result = self._api.commerce_taxonomy_get_default_category_tree_id('EBAY_US')
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
        else:
            self.assertTrue('category_tree_id' in result, msg="A call with some positional and no kw arguments failed.")

    def test_positional_none_kw_some(self):
        try:
            for record in self._api.buy_browse_search(q='red'):
                if 'record' in record:
                    item = record['record']
                    self.assertTrue('item_id' in item, msg="A call with some positional and no kw arguments failed.")
                    break
                else:
                    self.assertTrue('total' in record, f'Unexpected non-record{record}.')
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')

    def test_positional_some_kw_some(self):
        # https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCompatibilityPropertyValues # noqa: E501
        try:
            result = self._api.commerce_taxonomy_get_compatibility_property_values(0,
                                                                                   compatibility_property='Model',
                                                                                   category_id=33559,
                                                                                   filter='Year:2018,Make:Honda')
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
        else:
            msg = "A call with some positional and no kw arguments failed."
            self.assertTrue('compatibility_property_values' in result, msg=msg)

    def test_try_except_else_api(self):
        """  Test that an exception occurs when expected. """
        try:
            self._api.buy_browse_get_item(item_id='invalid')
        except Error as error:
            self.assertIsNotNone(f'Error {error.number} is {error.reason} with detail {error.detail}.')
        else:
            self.assertIsNotNone(None, msg="Failed to raise an exception.")

    def test_buying_options(self):
        """ Does buying option filtering work? """
        options = ['FIXED_PRICE', 'BEST_OFFER']  # on Production 'AUCTION' is also an option
        for option in options:
            try:
                success = None
                keywords = 'black'
                filter_ = 'buyingOptions:{' + option + '}'
                for record in self._api.buy_browse_search(q=keywords, filter=filter_, limit=500):
                    if 'record' not in record:
                        self.assertTrue('total' in record, f'Unexpected non-record{record}.')
                    else:
                        item = record['record']
                        if option in item['buying_options']:
                            success = True
                        else:
                            success = False
                            break
            except Error as error:
                self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
            else:
                message = 'The search for ' + option + ' items returned no items or a non-auction item.'
                self.assertTrue(success, message)

    def test_get_transaction_summary(self):
        """
        https://developer.ebay.com/api-docs/sell/finances/resources/transaction/methods/getTransactionSummary
        """
        try:
            result = self._api.sell_finances_get_transaction_summary(filter="transactionStatus:{PAYOUT}")
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')
        else:
            self.assertTrue('credit_count' in result)

    @unittest.skip  # TODO solve the permission problem
    def test_sell_account(self):
        """
        It is required that the seller be opted in to Business Policies before being able to create live eBay
        listings through the Inventory API. Sellers can opt-in to Business Policies through My eBay or by using
        the Account API's optInToProgram call. Similarly, payment, return, and fulfillment listing policies may
        be created/managed in My eBay or by using the listing policy calls of the Account API.
        https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/createFulfillmentPolicy
        """
        try:
            body = {"programType": "SELLING_POLICY_MANAGEMENT"}

            self._api.sell_account_opt_in_to_program(body=body)
        except Error as error:
            self.fail(f'Error {error.number} is {error.reason}  {error.detail}.\n')


class APIProductionSingleTests(unittest.TestCase):
    """" API tests that can be done on a single marketplace and must in be in system production. """

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        try:
            cls._api = API(application='production_1', user='production_1', header='US')
        except Error as error:
            cls.number = error.number
            cls.reason = error.reason
            cls.detail = error.detail
        else:
            cls.number = None

    def setUp(self):
        if self.number is not None:
            self.fail(f'Error {self.number} is {self.reason}  {self.detail}.\n')

    def test_hidden_page_boundaries(self):
        """
        Warning, this can't be run in the sandbox, because searches do not return enough results.
        """
        limit_and_keywords = (
            (1, 'red',),  # start at one because zero is not allowed
            (2, 'orange',),
            (198, 'yellow',),
            (199, 'green',),
            (200, 'blue',),  # the biggest page can hold 200 items
            (201, 'indigo',),
            (202, 'violet',),
        )
        for (limit, keywords) in limit_and_keywords:
            counter = 0
            safety = limit + 5
            for record in self._api.buy_browse_search(limit=limit, q=keywords):
                if 'record' not in record:
                    self.assertTrue('total' in record, f'Unexpected non-record{record}.')
                else:
                    item = record['record']
                    self.assertTrue(isinstance(item['item_id'], str), "Malformed item.")
                    counter += 1
                    if counter >= safety:
                        break
            self.assertTrue(counter == limit, f"Page boundary error on limit {limit}.")


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
