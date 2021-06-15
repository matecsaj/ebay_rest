# Standard library imports
import copy
import json
import os


# TODO Instead of loading stale .json files get real-time reference info using this
# https://developer.ebay.com/devzone/xml/docs/reference/ebay/GeteBayDetails.html

class Reference:
    """ Caches of reference information sourced from eBay's developer website. """

    _cache = {}

    @staticmethod
    def get_application_scopes():
        """ Get eBay **Client Credential/Code** Grant Type Scopes
         that might be permitted when minting **Application** tokens.

         Dictionary keys are the scopes, and data are descriptions.

        Source https://developer.ebay.com/my/keys, Sandbox column, click OAuth Scopes, second section
        """
        return Reference._get('application_scopes')

    @staticmethod
    def get_country_codes():
        """ Get eBay country code information.

        A partial list of ISO 3166 standard two-letter codes that represent countries around the world.

        Source https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/countrycodetype.html.
        """
        return Reference._get('country_codes')

    @staticmethod
    def get_item_fields_modified():
        """ Get eBay item "response" field information.

        The root container is ebay_item.

        Details of a specific item can include description, price, category, all item aspects, condition,
        return policies, seller feedback and score, shipping options, shipping costs, estimated delivery,
        and other information the buyer needs to make a purchasing decision.

        This has been modified in an opinionated way to aid with SQL database storage.

        Source https://developer.ebay.com/api-docs/buy/browse/resources/item/methods/getItem#h2-output.
        """
        return Reference._get('item_fields_modified')

    @staticmethod
    def get_item_enums_modified():
        """ Get eBay enumeration type definitions and SOME of their values.

        Beware that many values are missing; expect to encounter new ones.

        This has been modified in an opinionated way to aid with SQL database storage.

        Source https://developer.ebay.com/api-docs/buy/browse/enums.
        """
        return Reference._get('item_enums_modified')

    @staticmethod
    def get_global_id_values():
        """ Get eBay global id information.

        The Global ID is a unique identifier for combinations of site, language, and territory.
        Global ID values are returned in globalId and are used as input for the X-EBAY-SOA-GLOBAL-ID header.
        The global ID you use must correspond to an eBay site with a valid site ID.
        See https://developer.ebay.com/Devzone/merchandising/docs/Concepts/SiteIDToGlobalID.html
        eBay Site ID to Global ID Mapping for a list of global IDs you can use with the API calls.

        Source https://developer.ebay.com/Devzone/merchandising/docs/CallRef/Enums/GlobalIdList.html.
        """
        return Reference._get('global_id_values')

    @staticmethod
    def get_marketplace_id_values():
        """ Get eBay marketplace id information.

        The following table lists the set of supported Marketplace IDs, their associated countries,
        the URLs to the marketplaces, and the locales supported by each marketplace

        Source https://developer.ebay.com/api-docs/static/rest-request-components.html#marketpl.
        """
        return Reference._get('marketplace_id_values')

    @staticmethod
    def get_user_scopes():
        """ Get eBay **Authorization Code** Grant Type Scopes
        that might be permitted when minting **User Access** tokens.

        Dictionary keys are the scopes, and data are descriptions.

        Source https://developer.ebay.com/my/keys, Sandbox column, click OAuth Scopes, first section
        """
        return Reference._get('user_scopes')

    @staticmethod
    def _get(name):
        """ Get information from the json files. """
        if name not in Reference._cache:
            # get the path to this python file, which is also where the data file directory is
            path, _fn = os.path.split(os.path.realpath(__file__))
            # to the path join the data file name and extension
            path_name = os.path.join(path, 'references', name + '.json')
            with open(path_name) as file_handle:
                Reference._cache[name] = json.load(file_handle)
        return copy.deepcopy(Reference._cache[name])
