# Standard library imports
import unittest

# Third party imports

# Local imports
from src.ebay_rest.ebay_rest import EbayRest, EbayRestError

# Globals


# *** How to run these unit tests. ***
# 1. (Open a terminal, alternately known as go to the command line.)
# 2. cd .. (Or, somehow make the project root the current directory.)
# 3. python -m unittest tests.ebay_rest


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._er = EbayRest('Hello, World!')

    def test_true(self):
        self.assertEqual(self._er.true(), True)

    def test_enum_load(self):
        self.assertIsNotNone(self._er.get_enums(), msg="Failed to load enums.")

    def test_container_load(self):
        self.assertIsNotNone(self._er.get_containers(), msg="Failed to load containers.")

    def test_developer_analytics_get_rate_limits(self):
        self.assertIsNotNone(self._er.developer_analytics_get_rate_limits(),
                             msg="Failed at developer_analytics_get_rate_limits.")


if __name__ == '__main__':
    unittest.main()
