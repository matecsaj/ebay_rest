# Standard library imports
import collections
import datetime
from json import loads
import logging
import os
from typing import Callable, Dict, List, Tuple, Union

# Local imports
from .error import Error
from .multiton import Multiton
from .rates import Rates
from .reference import Reference
from .token import ApplicationToken, UserToken

# Don't edit the anchors or in-between; instead, edit and run scripts/generate_code.py.
# ANCHOR-er_imports-START"
from .api import buy_browse
from .api.buy_browse.rest import ApiException as BuyBrowseException
from .api import buy_deal
from .api.buy_deal.rest import ApiException as BuyDealException
from .api import buy_feed
from .api.buy_feed.rest import ApiException as BuyFeedException
from .api import buy_marketing
from .api.buy_marketing.rest import ApiException as BuyMarketingException
from .api import buy_marketplace_insights
from .api.buy_marketplace_insights.rest import ApiException as BuyMarketplaceInsightsException
from .api import buy_offer
from .api.buy_offer.rest import ApiException as BuyOfferException
from .api import buy_order
from .api.buy_order.rest import ApiException as BuyOrderException
from .api import commerce_catalog
from .api.commerce_catalog.rest import ApiException as CommerceCatalogException
from .api import commerce_charity
from .api.commerce_charity.rest import ApiException as CommerceCharityException
from .api import commerce_identity
from .api.commerce_identity.rest import ApiException as CommerceIdentityException
from .api import commerce_media
from .api.commerce_media.rest import ApiException as CommerceMediaException
from .api import commerce_notification
from .api.commerce_notification.rest import ApiException as CommerceNotificationException
from .api import commerce_taxonomy
from .api.commerce_taxonomy.rest import ApiException as CommerceTaxonomyException
from .api import commerce_translation
from .api.commerce_translation.rest import ApiException as CommerceTranslationException
from .api import developer_analytics
from .api.developer_analytics.rest import ApiException as DeveloperAnalyticsException
from .api import sell_account
from .api.sell_account.rest import ApiException as SellAccountException
from .api import sell_analytics
from .api.sell_analytics.rest import ApiException as SellAnalyticsException
from .api import sell_compliance
from .api.sell_compliance.rest import ApiException as SellComplianceException
from .api import sell_feed
from .api.sell_feed.rest import ApiException as SellFeedException
from .api import sell_finances
from .api.sell_finances.rest import ApiException as SellFinancesException
from .api import sell_fulfillment
from .api.sell_fulfillment.rest import ApiException as SellFulfillmentException
from .api import sell_inventory
from .api.sell_inventory.rest import ApiException as SellInventoryException
from .api import sell_listing
from .api.sell_listing.rest import ApiException as SellListingException
from .api import sell_logistics
from .api.sell_logistics.rest import ApiException as SellLogisticsException
from .api import sell_marketing
from .api.sell_marketing.rest import ApiException as SellMarketingException
from .api import sell_metadata
from .api.sell_metadata.rest import ApiException as SellMetadataException
from .api import sell_negotiation
from .api.sell_negotiation.rest import ApiException as SellNegotiationException
from .api import sell_recommendation
from .api.sell_recommendation.rest import ApiException as SellRecommendationException
# ANCHOR-er_imports-END"


@Multiton  # return the same object when the __init__ params are identical
class API:
    """ A wrapper for all of eBay's REST-ful APIs.

    For an overview of the APIs and more see https://developer.ebay.com/docs.
    """

    def __init__(self,
                 path: str or None = None,
                 application: str or dict or None = None,
                 user: str or dict or None = None,
                 header: str or dict or None = None,
                 throttle: bool or None = False,
                 timeout: float or None = -1.0) -> None:
        """
        Instantiate an API object, then use it to call hundreds of eBay APIs.

        Load credentials from an ebay_rest.json file or supply dicts that mimic records in said file.
        See https://github.com/matecsaj/ebay_rest/blob/main/tests/ebay_rest_EXAMPLE.json.
        Warning, hard coding credentials in code is a security risk.

        :param path (str, optional):
        If using a ebay_rest.json file that is not in the current working directory, supply a full path.

        :param application (str or dict, optional) :
        Supply the name of the desired application record in ebay_rest.json or a dict with application credentials.
        Can omit when ebay_rest.json contains only one application record.

        :param user (str or dict, optional) :
        Supply the name of the desired user record in ebay_rest.json or a dict with user credentials.
        Can omit when ebay_rest.json contains only one user record.

        :param header (str or dict, optional) :
        Supply the name of the desired header record in ebay_rest.json or a dict with header credentials.
        Can omit when ebay_rest.json contains only one header record.

        :param
        throttle (bool, optional) : When True block the call if a below the prorated call limit, defaults to False.
                                    Note, the sandbox has no call limits.

        :param
        timeout (float, optional) : When invoked with the floating-point timeout argument set to a positive value,
        throttle for at most the number of seconds specified by timeout and as below the prorated call limit. A timeout
        argument of -1 specifies an unbounded wait. It is forbidden to specify a timeout when the throttle is False.
        Defaults to -1.

        :return (object) : An API object.
        """
        # if present, load the configuration file
        config_contents = None
        if path is None:
            path = os.getcwd()
        self._config_location = os.path.join(path, 'ebay_rest.json')
        if os.path.isfile(self._config_location):
            try:
                with open(self._config_location, 'r') as f:
                    config_contents = loads(f.read())
            except IOError:
                raise Error(number=99001, reason='Unable to open ' + self._config_location)
        else:
            if not(isinstance(application, dict) and isinstance(user, dict) and isinstance(header, dict)):
                detail = 'Either at ' + self._config_location + \
                          ' do this https://github.com/matecsaj/ebay_rest/blob/main/tests/ebay_rest_EXAMPLE.json.' + \
                          ' Or, supply dicts to all of the params application, user, and header.'
                raise Error(number=99015, reason='Missing configuration information.', detail=detail)

        # get configuration sections from parameters or the loaded file
        try:
            self._application = self._process_config_section(config_contents, 'applications', application)
        except Error:
            raise
        try:
            self._user = self._process_config_section(config_contents, 'users', user)
        except Error:
            raise
        try:
            self._header = self._process_config_section(config_contents, 'headers', header)
        except Error:
            raise

        # check the application keys and values
        # True if the dictionary key is required and False when optional.
        # Nothing appears to use dev_id! What should it be used for?
        application_keys = [('app_id', True), ('cert_id', True), ('dev_id', False), ('redirect_uri', True)]
        try:
            self._check_keys(self._application, application_keys, 'application')
        except Error:
            raise

        # check the user keys and values
        user_keys = [('email_or_username', True), ('password', True),
                     ('scopes', False), ('refresh_token', False), ('refresh_token_expiry', False)]
        try:
            self._check_keys(self._user, user_keys, 'user')
        except Error:
            raise

        # Determine if we are using the sandbox. Of course production is the only alternative.
        self._sandbox = self._application['cert_id'].startswith('SBX-')

        # check the header keys and values

        # get valid marketplace ids
        self._marketplace_ids = []
        for global_id_value in Reference.get_global_id_values():
            self._marketplace_ids.append(global_id_value['global_id'].replace('-', '_'))

        # get all the languages that marketplaces use
        marketplace_languages = set()
        for marketplace_id_value in Reference.get_marketplace_id_values().values():
            for key in marketplace_id_value[1]:
                marketplace_languages.add(key)
        marketplace_languages = list(marketplace_languages)

        header_keys_values = [
            ('accept_language', marketplace_languages),
            ('affiliate_campaign_id', None),  # None indicates that any value is acceptable.
            ('affiliate_reference_id', None),
            ('device_id', None),
            ('content_language', marketplace_languages),
            ('country', list(Reference.get_country_codes().keys())),
            ('currency', list(Reference.get_currency_codes().keys())),
            ('marketplace_id', self._marketplace_ids),
            ('zip', None)
        ]
        try:
            self._check_header(header_keys_values)
        except Error:
            raise

        # check the throttle parameters
        detail = None
        if throttle not in (True, False):
            detail = "Parameter throttle must be unspecified, True or False."
        else:
            self._throttle = throttle
        if not isinstance(timeout, float):
            detail = "Parameter timeout must be unspecified or a float."
        elif timeout != -1.0 and timeout <= 0.0:
            detail = "Parameter timeout must be unspecified, -1 or positive."
        else:
            self._timeout = timeout
        if detail:
            raise Error(number=99002, reason="Bad throttling parameters.", detail=detail)

        if self._sandbox:  # The sandbox will not return rates so there is no point to doing throttling.
            self._throttle = False
            self._timeout = -1.0
            self._rates = None
        else:
            try:
                # If sandbox starts return rates, then you will need to add a sandbox param to the Rates constructor.
                self._rates = Rates(app_id=self._application['app_id'])
            except Error:
                raise

        # pre-load the multi-purpose header self._end_user_ctx
        equates = list()
        if 'affiliate_campaign_id' in self._header:
            if len(self._header['affiliate_campaign_id']) > 0:
                equates.append("affiliateCampaignId=" + self._header['affiliate_campaign_id'])
        if 'affiliate_reference_id' in self._header:
            if len(self._header['affiliate_reference_id']) > 0:
                equates.append("affiliateReferenceId=" + self._header['affiliate_reference_id'])
        if 'country' in self._header:
            if len(self._header['country']) > 0:
                equates.append("contextualLocation=country=" + self._header['country'])
                if 'zip' in self._header:
                    if len(self._header['zip']) > 0:
                        equates.append(",zip=" + self._header['zip'])
        if 'device_id' in self._header:
            if len(self._header['device_id']) > 0:
                equates.append("deviceId=" + self._header['device_id'])
        if equates:
            self._end_user_ctx = ''.join(equates)
        else:
            self._end_user_ctx = None

        try:
            self._application_token = ApplicationToken(
                self._sandbox,

                # application/client credentials
                client_id=self._application['app_id'],
                client_secret=self._application['cert_id'],
                ru_name=self._application['redirect_uri']
            )
        except Error:
            raise

        try:
            self._user_token = UserToken(
                self._sandbox,

                # application/client credentials
                client_id=self._application['app_id'],
                client_secret=self._application['cert_id'],
                ru_name=self._application['redirect_uri'],

                # user credentials
                user_id=self._user['email_or_username'],
                user_password=self._user['password'],
                user_scopes=None if 'scopes' not in self._user else self._user['scopes'],

                # user token supply
                user_refresh_token=None if 'refresh_token' not in self._user else self._user['refresh_token'],
                user_refresh_token_expiry=None if 'refresh_token_expiry' not in self._user else self._user[
                    'refresh_token_expiry'],
            )
        except Error:
            raise

        return

    @staticmethod
    def _process_config_section(config_contents: dict,
                                section: str,
                                parameter: str or dict or None
                                ) -> dict or None:
        """
        Get a configuration section from the parameter or the loaded config file.

        :param config_contents (dict, required)
        :param section (str, required)
        :param parameter (str or dict or None, required)
        :return result (dict or None)
        """
        result = None
        detail = None
        param_name = section[:-1]

        if isinstance(parameter, dict):
            result = parameter

        elif isinstance(parameter, str):
            if len(parameter) == 0:
                detail = 'Empty strings are not allowed for the ' + param_name + ' parameter.'

            if config_contents:
                if section in config_contents:
                    if parameter in config_contents[section]:
                        result = config_contents[section][parameter]
                    else:
                        detail = 'Unable to find section ' + parameter + ' in the configuration file.'
                else:
                    detail = 'Section ' + section + ' is missing from the configuration file.'
            else:
                detail = "The parameter " + param_name + \
                         " should not be a string or the configuration file should exist."

        elif parameter is None:
            if config_contents:
                if section in config_contents:
                    sections = config_contents['applications'].keys()
                    if len(sections) == 1:
                        result = config_contents['applications'][sections[0]]
                    else:
                        detail = "Perhaps parameter " + param_name + " should be one of " + ", ".join(sections) + "."
                else:
                    detail = "The parameter " + param_name + " should not be none or section " + section \
                             + " is missing from the configuration file."
            else:
                detail = "The parameter " + param_name + " should not be None or the configuration file should exist."

        else:
            detail = "Parameter " + param_name + " must be a Dict, String or None but it is a "\
                     + str(type(parameter)) + "."

        if result is None:
            raise Error(number=99003, reason="Get configuration for " + param_name + " problem.", detail=detail)
        else:
            # delete blank lines, to eliminate subsequent blank line checks
            to_delete = []
            for key in result:
                if isinstance(result[key], str):
                    if len(result[key].strip()) == 0:
                        to_delete.append(key)
            for key in to_delete:
                del result[key]

            return result

    @staticmethod
    def _check_keys(dict_: dict,
                    keys: List[Tuple[str, bool]],
                    name: str
                    ) -> None:
        """
        True if the dictionary key is required and False when optional.
        :param dict_ (dict, required)
        :param keys (List[Tuple[str, bool]], required)
        :param name (str, required)
        :return None (None)
        """
        valid_keys = []
        for (key, required) in keys:
            valid_keys.append(key)

            if key in dict_:
                if key == "scopes":
                    if not isinstance(dict_[key], list):
                        raise Error(number=99004, reason="The key's value must be a list.",
                                    detail=key + " in " + name)
                else:
                    if not isinstance(dict_[key], str):
                        raise Error(number=99005, reason="The key's value must be a string.",
                                    detail=key + " in " + name)
            if required:
                if key in dict_:
                    if len(dict_[key]) == 0:
                        raise Error(number=99006, reason="The key's value can not be of zero length.",
                                    detail=key + " in " + name)
                else:
                    raise Error(number=99007, reason="A required key missing", detail=key + " in " + name)

        for key in dict_:
            if key not in valid_keys:
                raise Error(number=99008, reason="Found an unexpected key.", detail=key + " in " + name)

    def _check_header(self, keys_values: List[Union[Tuple[str, list], Tuple[str, None]]]) -> None:
        """
        Check header keys and values.
        :param keys_values (List[Union[Tuple[str, list], Tuple[str, None]]], required)
        """
        header = self._header
        valid_keys = []
        for (key, values) in keys_values:
            valid_keys.append(key)
            if key in header:
                if isinstance(header[key], str):
                    if values is not None:
                        if header[key] not in values:
                            values.sort()
                            detail = "Header key " + key + " has value " + header[key] + \
                                     ". Choose from " + ', '.join(values) + '.'
                            raise Error(number=99009, reason='Invalid header value.', detail=detail)
                else:
                    raise Error(number=99010, reason="Header values must be strings.",
                                detail="Check key " + key + ".")

        for key in header:
            if key not in valid_keys:
                raise Error(number=99011, reason="Unexpected header key.", detail=key)

    def _method_single(self,
                       function_configuration: callable,
                       base_path: str,
                       function_instance: type,
                       function_client: callable or type,
                       method: str,
                       object_error: object,
                       user_access_token: bool,
                       rate_keys: List[str],
                       params: Tuple[str] or str or None,
                       **kwargs: Dict[str, int]
                       ) -> collections:
        """ Do the work for method that returns a single object.

        :param function_configuration (callable, required):
        :param base_path (str, required):
        :param function_instance (type, required):
        :param function_client (class or type, required):
        :param method (str, required):
        :param object_error (object, required):
        :param user_access_token (bool, required):
        :param rate_keys (List[str]: required:
        :param params: (Tuple[str] or str or None, required)
        :param kwargs: (Dict[str, int], required)
        :return object: (collections)
        """
        try:
            swagger_method = self._get_swagger_method(function_configuration, base_path, function_instance,
                                                      function_client, method, user_access_token, params)
        except Error:
            raise

        try:
            self._swagger_throttle(base_path=base_path, rate_keys=rate_keys)
        except Error:
            raise

        try:
            result = self._call_swagger(swagger_method, params, kwargs, object_error)
        except Error:
            raise
        else:
            return result

    def _method_paged(self,
                      function_configuration: callable,
                      base_path: str,
                      function_instance: type,
                      function_client: Callable or type,
                      method: str,
                      object_error: object,
                      user_access_token: bool,
                      rate_keys: List[str],
                      params: Tuple[str] or str or None,
                      **kwargs,     # TODO Is it wrong to put Dict[str, int] or is PyCharm's warning system buggy?
                      ) -> collections:
        """ Do the work for method that yields objects from repeated calls which is termed Paging by eBay.

        Across all pages, eBay has a hard limit on how many records it will return. This is subject to change
        and can vary by call. The swagger call will raise an exception at the limit. 10,000 is a common hard limit.

        :param function_configuration (callable, required):
        :param base_path (str, required):
        :param function_instance (type, required):
        :param function_client (Callable or type, required):
        :param method (str, required):
        :param object_error (object, required):
        :param params (Tuple[str] or str or None, required):
        :param kwargs (Dict[str, int], required):
        :return collection (collections):
        """
        page_controls = ['href', 'limit', 'next', 'offset', 'prev', 'total', 'warnings']
        page_limit = 200  # the maximum number of records per page, as dictated by eBay
        yield_record_count = 0
        yielded_info = list()

        # co-opt some parameters
        if 'offset' in kwargs:
            raise Error(number=99012, reason="Don't supply an offset parameter. It is automatically handled.")

        if 'limit' in kwargs:
            if not isinstance(kwargs['limit'], int):
                reason = "The limit must be an integer, you supplied a " + str(type(kwargs['limit'])) + '.'
                raise Error(number=99013, reason=reason)
            records_desired = kwargs['limit']
            if records_desired <= 0:
                reason = "The limit must be greater that zero, you supplied " + str(records_desired) + '.'
                raise Error(number=99014, reason=reason)
            if records_desired < page_limit:
                kwargs['limit'] = records_desired  # just get enough records to satisfy what is desired
            else:
                kwargs['limit'] = page_limit  # fill pages with as many records as possible
        else:
            records_desired = None  # the users wants all possible records
            kwargs['limit'] = page_limit  # fill pages with as many records as possible

        try:
            swagger_method = self._get_swagger_method(function_configuration, base_path, function_instance,
                                                      function_client, method, user_access_token, params)
        except Error:
            raise

        # loop though pages until a reason to stop presents itself
        offset = 0  # start at the first record; yes the record index starts at zero
        record_list_key = None  # a placeholder for the dictionary key that will refer to the list of records
        loop = True
        result = None
        while loop:

            try:
                self._swagger_throttle(base_path=base_path, rate_keys=rate_keys)
            except Error:
                raise

            kwargs['offset'] = offset  # get the next page of results
            try:
                # TODO If the caller does not process all yielded results within five minutes, the token might expire.
                result = self._call_swagger(swagger_method, params, kwargs, object_error)
            except Error:
                raise

            if record_list_key is None:  # if still needed, find the dictionary key to the list of results
                for key in result:
                    if isinstance(result[key], list):
                        record_list_key = key
                        page_controls.append(key)
                        break
                    # it will not be found when the record set is totally empty

            # Yield unique non-record information.
            for key in result:
                if key not in page_controls:
                    if result[key] is not None:
                        yield_info = {key: result[key]}
                        if yield_info not in yielded_info:
                            # TODO For some 'warnings' handle the problem or raise an exception.
                            yield yield_info
                            yielded_info.append(yield_info)

            # Determine the number of records in the current page.
            records_in_page = 0
            if record_list_key is not None:  # is the record set totally empty?
                if record_list_key in result:  # is current page is well formed page?
                    if result[record_list_key] is not None:  # does the current page have > zero results?
                        records_in_page = len(result[record_list_key])  # all good, get the record count

            # Yield each record then stop looping and prepare the next page's offset.
            if records_in_page:
                for element in result[record_list_key]:
                    yield {'record': element}
                    yield_record_count += 1
                    if records_desired is not None:
                        records_desired -= 1
                        if records_desired <= 0:
                            loop = False
                            break
                offset += records_in_page
                if result['total'] <= offset:
                    loop = False
            else:
                loop = False

        # Warning, if the caller stopped this generator prematurely then the following will not happen.
        if result is None:
            yield_max = 0
        else:
            yield_max = result['total']
        yield {'total': {'records_yielded': yield_record_count, 'records_available': yield_max}}

    def _get_swagger_method(self,
                            function_configuration: callable,
                            base_path: str,
                            function_instance: type,
                            function_client: callable or type,
                            method: str,
                            user_access_token: bool,
                            params: Tuple[str] or str or None
                            ) -> callable:
        """
        Get a callable Swagger method that is ready to use.

        :param function_configuration (Callable, required):
        :param base_path (str, required):
        :param function_instance (type, required):
        :param function_client (Callable or type, required):
        :param method (str, required):
        :param user_access_token (bool, required):
        :param params (Tuple[str] or str or None, required):
        :return function (callable)
        """
        # Configure OAuth2 access token for authorization: api_auth
        configuration = function_configuration()
        try:
            if user_access_token:
                configuration.access_token = self._user_token.get()
            else:
                configuration.access_token = self._application_token.get()
        except Error:
            raise

        # Configure the host endpoint
        if self._sandbox:
            configuration.host = configuration.host.replace('.ebay.com',
                                                            '.sandbox.ebay.com')
        # check for host has flaws and then then compensate
        if '{basePath}' in configuration.host:
            configuration.host = configuration.host.replace('{basePath}', base_path)
        else:
            logging.debug('eBay or Swagger has fixed the flaw so remove the compensating code.')

        # create an instance of the API class
        api_instance = function_instance(function_client(configuration))

        # The request headers that eBay accepts are mostly described here.
        # https://developer.ebay.com/api-docs/static/rest-request-components.html#headers

        # Accept, Accept-Charset & Accept-Encoding
        # Do nothing because the Swagger generated code handles them.

        # Accept-Language
        if self._header['accept_language']:
            api_instance.api_client.default_headers['Accept-Language'] = self._header['accept_language']

        # Authorization
        # Do nothing because the Swagger generated code handles it.

        # Content-Language
        if self._header['content_language']:
            api_instance.api_client.default_headers['Content-Language'] = self._header['content_language']

        # X-EBAY-C-MARKETPLACE-ID
        marketplace_id = self._header['marketplace_id']
        # some calls have a positional parameter for this, and the header must use the same value
        if user_access_token:  # all such calls happen to require a user access token
            # TODO instead it would be safer to check if 'method' is in a list of ones that belong
            for param in (params or []):
                if param in self._marketplace_ids:
                    marketplace_id = param
        api_instance.api_client.default_headers['X-EBAY-C-MARKETPLACE-ID'] = marketplace_id

        # X-EBAY-C-ENDUSERCTX
        # beware that the site_id is a bit different for the Buy API
        # https://developer.ebay.com/api-docs/buy/static/ref-marketplace-supported.html

        # header for shipping information accuracy per https://developer.ebay.com/api-docs/buy/static/api-browse.html
        if '/buy/browse' in base_path and self._end_user_ctx:
            api_instance.api_client.default_headers['X-EBAY-C-ENDUSERCTX'] = self._end_user_ctx

        # return the callable function
        return getattr(api_instance, method)

    def _swagger_throttle(self, base_path: str, rate_keys: list) -> None:
        """ Block when the swagger method is below it's prorated call limit.

        Call this just before calling a swagger method. Only do for the first paging call.

        :param base_path (str, required):
        :param rate (list, required) : Strings, keys used to lookup a rate
        """
        if not self._sandbox:  # eBay does not limit calls to the sandbox

            # the base_path check prevents endless recursive calls to self.developer_analytics_get_rate_limits()
            if not self._throttle or base_path.startswith('/developer/analytics'):
                self._rates.decrement_rate(base_path=base_path, rate_keys=rate_keys)
            else:

                # if rates need to be refreshed, then do so.
                if self._rates.need_refresh():
                    try:
                        limits = self.developer_analytics_get_rate_limits()
                    except Error:
                        raise
                    else:
                        self._rates.refresh_developer_analytics(rate_limits=limits['rate_limits'])

                # decrement the rate, throttling if needed
                try:
                    self._rates.decrement_rate_throttled(base_path=base_path, rate_keys=rate_keys,
                                                         timeout=self._timeout)
                except Error:
                    raise

    def _call_swagger(self,
                      swagger_method: Callable,
                      params: Tuple[str] or str or None,
                      kwargs: Dict[str, Dict[str, int]],
                      object_error: object
                      ) -> collections:
        """
        Call the API method generated by Swagger and tidy the result.

        :param swagger_method (Callable, required)
        :param params (Tuple[str] or str or None, required)
        :param kwargs (Dict[str, Dict[str, int]], required)
        :param object_error (object, required)
        :return collection (collections)
        """
        try:
            if params:
                if isinstance(params, tuple):
                    if kwargs:
                        api_response = swagger_method(*params, **kwargs)
                    else:
                        api_response = swagger_method(*params)
                else:
                    if kwargs:
                        api_response = swagger_method(params, **kwargs)
                    else:
                        api_response = swagger_method(params)
            else:
                if kwargs:
                    api_response = swagger_method(**kwargs)
                else:
                    api_response = swagger_method()

        except object_error as error:
            # error.status will be 100 to 599, see https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
            raise Error(number=99000 + error.status, reason=error.reason, detail=error.body)

        else:
            return self._de_swagger(api_response)

    def _de_swagger(self, obj: collections):
        """ Take a Swagger data object and return the Python styled equivalent.

        There is a Java vibe to objects returned from Swagger generated code and other issues:
        1. non-eBay attributes are meaningless Swagger artifacts,
        2. public attributes should not have leading underscores,
        3. the class objects are effectively dicts,
        4. class names are in CamelCase.

        Do a "deep copy" and fix problems along the way.

        To learn more about Swagger, visit https://swagger.io.

        :param obj (collections, required): The object returned by a Swagger call.
        :return obj (collections)
        """
        basic_types = (bool, bytes, datetime.date, datetime.datetime,
                       float, int, type(None), str)  # omitted ones that are unlikely to ever be used

        if type(obj) in basic_types:  # leaf node
            return obj

        elif obj.__class__.__module__ != 'builtins':  # a user defined class object?
            new_dict = dict()
            for attr, value in obj.__dict__.items():
                if attr not in ['attribute_map', 'discriminator', 'swagger_types']:  # skip Swagger specific

                    success = True

                    # cope with Swagger presenting public attributes as private
                    if not attr.startswith('_') or attr.startswith('__'):
                        logging.debug('A public or dunder is not anticipated, did Swagger fix the problem?')
                        new_value = None  # this pointless line is here to avoid a lint warning
                        success = False
                    else:
                        attr = attr[1:]  # remove the single leading underscore

                        if type(value) in basic_types:
                            new_value = value

                        elif isinstance(value, list):
                            new_value = list()
                            for element in value:
                                new_value.append(self._de_swagger(element))

                        elif value.__class__.__module__ != 'builtins':  # a user defined class object?
                            new_value = self._de_swagger(value)

                        else:
                            logging.debug("Need to handle attribute " + attr + " of type " + type(value) + ".")
                            new_value = None  # this pointless line is here to avoid a lint warning
                            success = False

                    if success:
                        new_dict[attr] = new_value

            return new_dict

        else:
            logging.debug("Unexpected object of type " + type(obj) + ".")
            return obj  # something needs to be returned, hopefully it is useful as is

    # Don't edit the anchors or in-between; instead, edit and run scripts/generate_code.py.
    # ANCHOR-er_methods-START"

    def buy_browse_check_compatibility(self, x_ebay_c_marketplace_id, item_id, **kwargs):  # noqa: E501
        """check_compatibility  # noqa: E501

        This method checks if a product is compatible with the specified item. You can use this method to check the compatibility of cars, trucks, and motorcycles with a specific part listed on eBay. <br /><br />For example, to check the compatibility of a part, you pass in the item ID of the part as a URI parameter and specify all the attributes used to define a specific car in the <b> compatibilityProperties</b> container. If the call is successful, the response will be <b> COMPATIBLE</b>, <b> NOT_COMPATIBLE</b>, or <b> UNDETERMINED</b>. See <a href=\"/api-docs/buy/browse/resources/item/methods/checkCompatibility#response.compatibilityStatus\">compatibilityStatus</a> for details.   <br /><br /> <span class=\"tablenote\"><b> Note: </b> The only products supported are cars, trucks, and motorcycles. </span><p>  To find the attributes and values for a specific marketplace, you can use the compatibility methods in the <a href=\"/api-docs/commerce/taxonomy/resources/methods\">Taxonomy API</a>. You can use this data to create menus to help buyers specify the product, such as their car.</p> <p> For more details and a list of the required attributes for the US marketplace that describe motor vehicles, see <a href=\"/api-docs/buy/static/api-browse.html#Check\">Check compatibility</a> in the Buy Integration Guide</a>.</p>   <p>For an example, see the <a href=\"/api-docs/buy/browse/resources/item/methods/checkCompatibility#h2-samples\">Samples</a> section. </p>    <h3>URLs for this method</h3>  <p><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item/{item_id}/check_compatibility</code> </p>         <p><span class=\"tablenote\"><b> Note: </b> This method is supported only on Production. </span></p>         <h3><b> Restrictions </b></h3> <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p>   # noqa: E501

        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace you want to use. <b> Note: </b> This value is case sensitive.<br /><br />For example: <br />&nbsp;&nbsp;<code>X-EBAY-C-MARKETPLACE-ID = EBAY_US</code>  <br /><br /> For a list of supported sites see, <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>. (required)
        :param str item_id: The eBay RESTful identifier of an item (such as a part you want to check). This ID is returned by the <b> Browse</b> and <b> Feed</b> API methods.  <br /><br /> <b> RESTful Item ID Format: </b><code>v1</code>|<code><i>#</i></code>|<code><i>#</i></code> <br />For example: <code>v1|2**********2|0</code> or <code>v1|1**********2|4**********2</code> <br /><br />For more information about item ID for RESTful APIs, see the <a href=\"/api-docs/buy/static/api-browse.html#Legacy\">Legacy API compatibility</a> section of the <i>Buy APIs Overview</i>. (required)
        :param CompatibilityPayload body:
        :return: CompatibilityResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'check_compatibility', BuyBrowseException, False, ['buy.browse', 'item'], (x_ebay_c_marketplace_id, item_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_item(self, item_id, **kwargs):  # noqa: E501
        """get_item  # noqa: E501

        <p>This method retrieves the details of a specific item, such as description, price, category, all item aspects, condition, return policies, seller feedback and score, shipping options, shipping costs, estimated delivery, and other information the buyer needs to make a purchasing decision.</p><p>The Buy APIs are designed to let you create an eBay shopping experience in your app or website. This means you will need to know when something, such as the availability, quantity, etc., has changed in any eBay item you are offering. You can do this easily by setting the <b> fieldgroups</b> URI parameter. This parameter lets you control what is returned in the response.</p>        <p>Setting <b> fieldgroups</b> to <code>COMPACT</code> reduces the response to only those fields that you need in order to check if any item detail has changed.  Setting <b> fieldgroups</b> to <code>PRODUCT</code>, adds additional fields to the default response that return information about the product of the item. You can use either <code>COMPACT</code> or <code>PRODUCT</code> but not both. For more information, see <a href=\"/api-docs/buy/browse/resources/item/methods/getItem#uri.fieldgroups\">fieldgroups</a>.</p>      <h3>URLs for this method</h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item/{item_id}</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/item/{item_id}</code></li>           </ul>    </p>                   <h3><b> Request headers</b></h3> This method uses the  <b>X-EBAY-C-ENDUSERCTX</b> request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.  For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the Buying Integration Guide.     <h3><b> Restrictions </b></h3> <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p> <span class=\"tablenote\"><b>eBay Partner Network: </b> In order to be commissioned for your sales, you must use the URL returned in the <code>itemAffiliateWebUrl</code> field to forward your buyer to the ebay.com site. </span>  # noqa: E501

        :param str item_id: The eBay RESTful identifier of an item. This ID is returned by the <b> Browse</b> and <b> Feed</b> API methods.  <br /><br /> <b> RESTful Item ID Format: </b><code>v1</code>|<code><i>#</i></code>|<code><i>#</i></code> <br />For example: <code>v1|2**********2|0</code> or <code>v1|1**********2|4**********2</code> <br /><br />For more information about item ID for RESTful APIs, see the <a href=\"/api-docs/buy/static/api-browse.html#Legacy\">Legacy API compatibility</a> section of the <i>Buy APIs Overview</i>. (required)
        :param str fieldgroups: This parameter lets you control what is returned in the response. If you do not set this field, the method returns all the details of the item.   <br /> <br /> <b> Valid Values: </b> <ul>  <li> <b> PRODUCT</b> - This adds the <code>additionalImages</code>, <code>additionalProductIdentities</code>, <code>aspectGroups</code>, <code>description</code>, <code>gtins</code>, <code>image</code>, and <code>title</code> product fields to the response, which describe the product associated with the item. See <a href=\"/api-docs/buy/browse/resources/item/methods/getItem#response.product\">Product</a> for more information about these fields.</li>          <li><b> COMPACT</b> -  This returns only the following fields, which let you quickly check if the availability or price of the item has changed, if the item has been revised by the seller, or if an item's top-rated plus status has changed for items you have stored.  <ul> <li> <b> itemId</b> - The identifier of the item.</li> <li><b>bidCount</b> - This integer value indicates the total number of bids that have been placed against an auction item.</li> <li><b>currentBidPrice</b> - This container shows the current highest bid for an auction item. This container will only be returned for auction items.</li>  <li><b>eligibleForInlineCheckout</b> - This parameter returns items based on whether or not the items can be purchased using the Buy <a href=\"/api-docs/buy/order/resources/methods\">Order API</a>. <ul> <li>If the value of this field is <code>true</code>, this indicates that the item can be purchased using the <b> Order API</b>. </li>  <li>If the value of this field is <code>false</code>, this indicates that the item cannot be purchased using the <b> Order API</b> and must be purchased on the eBay site.</li> </ul> <li><b> estimatedAvailabilities</b> -  Returns the item availability information, which is based on the item's quantity. <b> Note:</b> Changes in quantity are not tracked by <b>sellerItemRevision</b>.</li> <li><b>itemAffiliateWebURL</b> - The URL of the View Item page of the item, which includes the affiliate tracking ID. This field is only returned if the eBay partner enables affiliate tracking for the item by including the <code>X-EBAY-C-ENDUSERCTX</code> request header in the method.</li> <li><b>itemEndDate</b> - This is the scheduled end time of the listing.</li> <li><b>ItemWebURL</b> - The URL of the View Item page of the item. This enables you to include a \"Report Item on eBay\" link that takes the buyer to the View Item page on eBay. From there they can report any issues regarding this item to eBay.</li> <li><b>legacyItemId</b> - The unique identifier of the eBay listing that contains the item. This is the traditional/legacy ID that is often seen in the URL of the listing View Item page.</li> <li><b>minimumPriceToBid</b> - This container shows the minimum bid amount that would be accepted as a qualifying bid in an auction listing. This container will only be returned for auction items.</li> <li><b>price</b> - This is tracked by the revision ID but is returned here to enable you to quickly verify the price of the item.</li> <li><b>priorityListing</b> - This field is returned as <code>true</code> if the listing is part of a Promoted Listing campaign. Promoted Listings are available to Above Standard and Top Rated sellers with recent sales activity.</li> <li><b>reservePriceMet</b> - This field indicates whether or not an auction's reserve price (if set by the seller) has been met yet. This field will only be returned for auction items.</li> <li><b> sellerItemRevision</b> - An identifier generated/incremented when a seller revises the item. The following are the two types of item revisions:   <ul>  <li><b> Seller changes</b>, such as changing the title</li>  <li>  <b> eBay system changes</b>, such as changing the quantity when an item is purchased.</li>  </ul> This ID is changed <em>only</em> when the seller makes a change to the item. This means you cannot use this value to determine if the quantity has changed. To check if the quantity has changed, use <b> estimatedAvailabilities.</b></li> <li><b>taxes</b> - A container for the tax information for the item, such as the tax jurisdiction, the tax percentage, and the tax type.</li> <li><b> topRatedBuyingExperience</b> - A boolean value indicating if this item is a top-rated plus item. A change in the item's top rated plus standing is not tracked by the revision ID. See <a href=\"/api-docs/buy/browse/resources/item/methods/getItem#response.topRatedBuyingExperience\">topRatedBuyingExperience</a> for more information.</li> <li><b>uniqueBidderCount</b> - This integer value indicates the number of different eBay users who have placed one or more bids on an auction item. This field is only applicable to auction items.</li></ul>    <b> For Example</b> <br /> <br />To check if a stored item's information is current, do following.  <ol>    <li>Pass in the item ID and set <b> fieldgroups</b> to COMPACT. <br /> <br /><code>item/v1|4**********8|0?fieldgroups=COMPACT</code> </li>     <li>Do one of the following:    <ul>     <li>If the <b> sellerItemRevision</b> field is returned and you <em>haven't</em> stored a revision number for this item, record the number and pass in the item ID in the <b> getItem</b> method to get the latest information.</li>   <li>If the revision number is different from the value you have stored, update the value and pass in the item ID in the <b> getItem</b> method to get the latest information.</li>     <li>If the <b> sellerItemRevision</b> field is <em>not</em> returned or has not changed, where needed, update the item information with the information returned in the response.</li>  </ul>  </li> </ol></li> </ul>  </ul>    <p><b> Maximum value: </b> 1 <br />If more than one values is specified, the first value will be used.
        :return: Item
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_item', BuyBrowseException, False, ['buy.browse', 'item'], item_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_item_by_legacy_id(self, legacy_item_id, **kwargs):  # noqa: E501
        """get_item_by_legacy_id  # noqa: E501

          <p>This method is a bridge between the eBay legacy APIs, such as  <b> Shopping</b>, and <b> Finding</b> and the eBay Buy APIs. There are differences between how legacy APIs and RESTful APIs return the identifier of an \"item\" and what the item ID represents. This method lets you use the legacy item ids retrieve the details of a specific item, such as description, price, and other information the buyer needs to make a purchasing decision. It also returns the RESTful item ID, which you can use with all the Buy API  methods.</p>  <p>For more information about how to use legacy ids with the Buy APIs, see <a href=\"/api-docs/buy/static/api-browse.html#Legacy\">Legacy API compatibility</a> in the Buying Integration guide.</p>  <p>This method returns the item details and requires you to pass in either the item ID of a non-variation item or the item ids of both the parent and child of an item group. An item group is an item that has various aspect differences, such as color, size, storage capacity, etc.</p> <p>When an item group is created, one of the item variations, such as the red shirt size L, is chosen as the \"parent\". All the other items in the group are the children, such as the blue shirt size L, red shirt size M, etc.</p>    <p>The <b> fieldgroups</b> URI parameter lets you control what is returned in the response. Setting <b> fieldgroups</b> to <code>PRODUCT</code>, adds additional fields to the default response that return information about the product of the item. For more information, see <a href=\"/api-docs/buy/browse/resources/item/methods/getItemByLegacyItem#uri.fieldgroups\">fieldgroups</a>.</p>       <h3>URLs for this method</h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item/get_item_by_legacy_id?</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/item/get_item_by_legacy_id?</code></li>           </ul>    </p>              <h3><b> Request headers</b></h3> This method uses the  <b>X-EBAY-C-ENDUSERCTX</b> request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.   For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the Buying Integration Guide.    <h3><b> Restrictions </b></h3> <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p> <span class=\"tablenote\"><b>eBay Partner Network: </b> In order to be commissioned for your sales, you must use the URL returned in the <code>itemAffiliateWebUrl</code> field to forward your buyer to the ebay.com site. </span>  # noqa: E501

        :param str legacy_item_id: Specifies either: <ul> <li>The legacy item ID of an item that is <em>not</em> part of a group. </li> <li>The legacy item ID of a group, which is the ID of the \"parent\" of the group of items. <br /> <br /><span class=\"tablenote\"> <b> Note: </b> If you pass in a group ID, you must also use the <b> legacy_variation_id</b> field and pass in the legacy ID of the specific item variation (child ID).</span></li></ul>  Legacy ids are returned by APIs, such as the <a href=\"https://developer.ebay.com/devzone/finding/callref/index.html\" target=\"_blank\">Finding API</a>.  <br /><br />The following is an example of using the value of the <b> ItemID</b> field for a specific item from Finding to get the RESTful <b> itemId</b> value. <br /> <br />&nbsp;&nbsp;&nbsp;<code> browse/v1/item/get_item_by_legacy_id?legacy_item_id=1**********9  </code><br /><br /><b> Maximum: </b> 1 (required)
        :param str fieldgroups: This field lets you control what is returned in the response. If you do not set this field, the method returns all the details of the item. <b> Note</b>: In this method, the only value supported is <code>PRODUCT</code>. <p><b> Valid Values: </b><br /><br /> <b> PRODUCT</b> - This adds the <code>additionalImages</code>, <code>additionalProductIdentities</code>, <code>aspectGroups</code>, <code>description</code>, <code>gtins</code>, <code>image</code>, and <code>title</code> fields to the response, which describe the item's product.  See <a href=\"/api-docs/buy/browse/resources/item/methods/getItemByLegacyItem#response.product\">Product</a> for more information about these fields. <br /><br />Code so that your app gracefully handles any future changes to this list.
        :param str legacy_variation_id: Specifies the legacy item ID of a specific item in an item group, such as the red shirt size L. <br /><br />Legacy ids are returned by APIs, such as the <a href=\"https://developer.ebay.com/devzone/finding/callref/index.html\" target=\"_blank\">Finding API</a>.     <br /><br /><b> Maximum: </b> 1 <br /><b> Requirement: </b> You must <b> always</b> pass in the <b> legacy_item_id </b> with the <b> legacy_variation_id</b>
        :param str legacy_variation_sku: Specifics the legacy SKU of the item. SKU are item ids created by the seller. <br /><br />Legacy SKUs are returned by eBay the  <a href=\"https://developer.ebay.com/Devzone/shopping/docs/CallRef/index.html\" target=\"_blank\">Shopping API</a>. <br /><br />The following is an example of using the value of the <b> ItemID</b> and <b> SKU</b> fields to get the RESTful <b> itemId</b> value. <br /> <br />&nbsp;&nbsp;&nbsp;<code> browse/v1/item/get_item_by_legacy_id?legacy_item_id=1**********9&amp;legacy_variation_sku=V**********M</code><br /><br /><b> Maximum: </b> 1 <br /><b> Requirement: </b> You must <b> always</b> pass in the <b> legacy_item_id </b> with the <b> legacy_variation_sku</b>
        :return: Item
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_item_by_legacy_id', BuyBrowseException, False, ['buy.browse', 'item'], legacy_item_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_items(self, **kwargs):  # noqa: E501
        """get_items  # noqa: E501

        This method retrieves the details of specific items that the buyer needs to make a purchasing decision.  <br><br><span class=\"tablenote\"> <b>Note:</b> This is a <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"> <img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\" title=\"Limited Release\"  alt=\"Limited Release\" />(Limited Release)</a> available only to select Partners. <br><br>For this method, only the following fields are returned: <code>bidCount</code>, <code>currentBidPrice</code>, <code>eligibleForInlineCheckout</code>, <code>enabledForGuestCheckout</code>, <code>estimatedAvailabilities</code>, <code>itemAffiliateWebUrl</code>, <code>itemId</code>, <code>itemWebUrl</code>, <code>legacyItemId</code>, <code>minimumPriceToBid</code>, <code>price</code>, <code>priorityListing</code>, <code>reservePriceMet</code>, <code>sellerItemRevision</code>, <code>taxes</code>, <code>topRatedBuyingExperience</code>, and <code>uniqueBidderCount</code>.</span> <h3>URLs for this method</h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item?</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/item?</code></li>           </ul>    </p>            <h3><b> Request headers</b></h3> This method uses the  <b>X-EBAY-C-ENDUSERCTX</b> request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.   For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the Buying Integration Guide.   <h3><b> Restrictions </b></h3> <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p> <span class=\"tablenote\"><b>eBay Partner Network:</b> In order to be commissioned for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.   # noqa: E501

        :param str item_ids: A list of item IDs. Item IDs are the eBay RESTful identifier of items. <br><br><b> RESTful Item ID Format: </b><code>v1</code>|<code><i>#</i></code>|<code><i>#</i></code><br>For example: <code>v1|2**********2|0</code> or <code>v1|1**********2|4**********2</code> <br><br>In any given request, either item_ids or item_group_ids can be retrieved. Attempting to retrieve both will result in an error. <br><br> In a request, multiple item_ids can be passed as comma separated values.<br><br><b> Maximum allowed itemIDs: </b> 20 <br><br>For more information about item IDs for RESTful APIs, see the <a href=\"/api-docs/buy/static/api-browse.html#Legacy\">Legacy API compatibility</a> section of the <i>Buy APIs Overview</i>.
        :param str item_group_ids: A list of item group IDs. Item group IDs are the eBay RESTful identifier of item groups. <br><br><b> RESTful Group Item ID Format: </b><code>############</code><br>For example: <code>3**********9</code><br><br>In any given request, either item_ids or item_group_ids can be retrieved. Attempting to retrieve both will result in an error.<br><br>In a request, multiple item_group_ids can be passed as comma separated values.<br><br><b> Maximum allowed itemGroupIDs: </b> 10 <br><br>
        :return: Items
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_items', BuyBrowseException, False, ['buy.browse', 'item'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_items_by_item_group(self, item_group_id, **kwargs):  # noqa: E501
        """get_items_by_item_group  # noqa: E501

         <p>This method retrieves the details of the individual items in an item group. An item group is an item that has various aspect differences, such as color, size, storage capacity, etc. </p>  <p>You pass in the item group ID as a URI parameter. You use this method to show the item details of items with multiple aspects, such as color, size, storage capacity, etc.  </p>  <p>This method returns two main containers;  <b> items</b> and <b> commonDescriptions</b>. The <b> items</b> container has an array of  containers with the details of each item in the group. The <b> commonDescriptions</b> container has an array of containers for a description and the item ids of all the items that have this exact description. Because items within an item group often have the same description, this decreases the size of the response. </p>         <h3>URLs for this method</h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item/get_items_by_item_group?</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/item/get_items_by_item_group?</code></li>           </ul>    </p>            <h3><b> Request headers</b></h3> This method uses the  <b>X-EBAY-C-ENDUSERCTX</b> request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.   For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the Buying Integration Guide.   <h3><b> Restrictions </b></h3> <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p> <span class=\"tablenote\"><b>eBay Partner Network: </b> In order to be commissioned for your sales, you must use the URL returned in the <code>itemAffiliateWebUrl</code> field to forward your buyer to the ebay.com site. </span>   # noqa: E501

        :param str item_group_id: Identifier of the item group to return.  An item group is an item that has various aspect differences, such as color, size, storage capacity, etc. </p> <p>This ID is returned in the <b> itemGroupHref</b> field of the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search\">search</a> and <a href=\"/api-docs/buy/browse/resources/item/methods/getItem\">getItem</a> methods. <br /><br /><b> For Example: </b><code> https://api.ebay.com/buy/browse/v1/item/get_items_by_item_group?item_group_id=3**********6</code> (required)
        :return: ItemGroup
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_items_by_item_group', BuyBrowseException, False, ['buy.browse', 'item'], item_group_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_search(self, **kwargs):  # noqa: E501
        """search  # noqa: E501

        <p>This method searches for eBay items by various query parameters and retrieves summaries of the items. You can search by keyword, category, eBay product ID (ePID), or GTIN, charity ID, or a combination of these. </p><p><span class=\"tablenote\"><b> Note: </b>Only FIXED_PRICE (Buy It Now) items are returned by default. However, this method does return items where both FIXED_PRICE and AUCTION are available as a buying option. After a bid has been placed, items become active auction items and are no longer returned by default, but they remain accessible by filtering for the AUCTION buying option.</span></p><p>This method also supports the following:  <ul> <li>Filtering by the value of one or multiple fields, such as listing format, item condition, price range, location, and more.  For the fields supported by this method, see the <a href=\"#uri.filter\">filter</a> parameter.</li> <li>Retrieving the refinements (metadata) of an item , such as item aspects (color, brand), condition, category, etc. using the <a href=\"#uri.fieldgroups\">fieldgroups</a> parameter. </li>  <li>Filtering by item aspects and other refinements using the <a href=\"#uri.aspect_filter\">aspect_filter</a> parameter. </li> <li>Filtering for items that are compatible with a specific product, using the <a href=\"#uri.compatibility_filter\">compatibility_filter</a> parameter. </li><li>Creating aspects histograms, which enables shoppers to drill down in each refinement narrowing the search results.  </li>  </ul></p>  <p>For details and examples of these capabilities, see <a href=\"/api-docs/buy/static/api-browse.html\">Browse API</a> in the Buying Integration Guide.</p>     <h3><b> Pagination and sort controls</b></h3>  <p>There are pagination controls (<b>limit</b> and <b>offset</b> fields) and <b> sort</b> query parameters that control/sort the data that is returned. By default, the results are sorted by &quot;Best Match&quot;. For more information about  Best Match, see the eBay help page <a href=\"https://pages.ebay.com/help/sell/searchstanding.html\" target=\"_blank\">Best Match</a>.  </p>    <h3><b>URLs for this method</b></h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item_summary/search?</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search?</code></li>           </ul>    </p>             <h3><b> Request headers</b></h3> This method uses the  <b>X-EBAY-C-ENDUSERCTX</b> request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the Buying Integration Guide.      <h3><b>Restrictions </b></h3> <p>This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p>    <span class=\"tablenote\"><b>eBay Partner Network: </b> In order to receive a commission for your sales, you must use the URL returned in the <code>itemAffiliateWebUrl</code> field to forward your buyer to the ebay.com site. </span>  # noqa: E501

        :param str aspect_filter: This field lets you filter by item aspects. The aspect name/value pairs and category, which is required, is used to limit the results to specific aspects of the item. For example, in a clothing category one aspect pair would be Color/Red. <br /><br />For example, the method below uses the category ID for Women's Clothing. This will return only items for a woman's red shirt.<br /><br /><code>/buy/browse/v1/item_summary/search?q=shirt&category_ids=15724&aspect_filter=categoryId:15724,Color:{Red}</code> <br /><br />To get a list of the aspects pairs and the category, which is returned in the <b> dominantCategoryId</b> field, set <b> fieldgroups</b> to <code>ASPECT_REFINEMENTS</code>.   <br /><br /> <code>/buy/browse/v1/item_summary/search?q=shirt&amp;fieldgroups=ASPECT_REFINEMENTS</code> <br /><br /><b>Required: </b> The category ID is required <i>twice</i>; once as a URI parameter and as part of the <b> aspect_filter</b>. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/gct:AspectFilter
        :param str auto_correct: A query parameter that enables auto correction.<br /><br /><b>Valid Values:</b> <code>KEYWORD</code>
        :param str category_ids: <a name=\"category_ids\"></a>The category ID is used to limit the results. This field can have one category ID or a comma separated list of IDs.<br /><br /><b> For example: </b><br/><code>/buy/browse/v1/item_summary/search?category_ids=29792</code> <br /><br /><span class=\"tablenote\"><b> Note: </b>Currently, you can pass in only one category ID per request.</span> <br /> <br />You can also use any combination of the <b> category_Ids</b>, <b> epid</b>, and <b> q</b> fields. This gives you additional control over the result set. <br /><br />For example, let's say you are looking of a toy phone. If you search for \"phone\", the result set will be mobile phones because this is the \"Best Match\" for this search. But if you also include the toy category ID, the results will be what you wanted. <br /><br /><b> For example: </b><br /><code>/buy/browse/v1/item_summary/search?q=phone&category_ids=220</code><br /> <br />The list of eBay category IDs is not published and category IDs are not the same across all the eBay marketplaces. You can use the following techniques to find a category by site: <ul> <li>Use the <a href=\"https://pages.ebay.com/sellerinformation/news/categorychanges.html\" target=\"_blank\">Category Changes page</a>.</li> <li>Use the Taxonomy API. For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  <li>Submit the following method to get the <b> dominantCategoryId</b> for an item. <br /><br /><code>/buy/browse/v1/item_summary/search?q=<em> keyword</em>&fieldgroups=ASPECT_REFINEMENTS  </code></li></ul>  <span class=\"tablenote\"> <b> Note:</b> If a top-level (L1) category is specified, you <b> must</b> also include the <b> q</b> query parameter.</span> <br /><br /><b> Required: </b> The method must have <b> category_ids</b>, <b> epid</b>, <b> gtin</b>, or <b> q</b>  (or any combination of these)
        :param str charity_ids: The charity ID is used to limit the results to only items associated with the specified charity. This field can have one charity ID or a comma separated list of IDs. The method will return all the items associated with the specified charities.<br /><br /> <b>For example:</b><br /><code>/buy/browse/v1/item_summary/search?charity_ids=13-1788491,300108469</code><br /><br />The charity ID is the charity's registration ID, also known as the Employer Identification Number (EIN). In GB, it is the Charity Registration Number (CRN), commonly called \"Charity Number\".   <ul><li>To find the charities eBay supports, you can search for a charity at <a href=\"https://charity.ebay.com/search\" target=\"_blank\">Charity Search </a> or go to <a href=\"https://www.ebay.com/b/Charity/bn_7114598164\" target=\"_blank\">Charity Shop</a>.</li>   <li>To find the charity ID of a specific charity, click on a charity and use the EIN number. For example, the charity ID for  <a href=\"https://charity.ebay.com/charity/American-Red-Cross/3843\" target=\"_blank\">American Red Cross</a>, is <code>530196605</code>.</li></ul> You  can also use any combination of the <code>category_Ids</code> and <code>q</code> fields with a <code>charity_Ids</code> to filter the result set. This gives you additional control over the result set. <br /><br /><b>Restriction: </b> This is supported only on the US and GB marketplaces.<br /><br /><b>Maximum: </b> 20 IDs <br /><br /><b>Required:</b> One ID
        :param str compatibility_filter: This field specifies the attributes used to define a specific product. The service searches for items matching the keyword or matching the keyword and a product attribute value in the title of the item.  <br /><br />For example, if the keyword is <code>brakes</code> and <code>compatibility-filter=Year:2018;Make:Honda</code>, the items returned are items with brakes, 2018, or Honda in the title.  <br /><br />The service uses the product attributes to determine if the item is compatible.    The service returns the attributes that are compatible and the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search#response.itemSummaries.compatibilityMatch\"> CompatibilityMatchEnum</a> value that indicates how well the item matches the attributes.  <br /><br />For the best compatibility results, submit all the attributes used to define the product. <br /><br /><b>Best Practice: </b> Submit all the <a href=\"/api-docs/buy/static/api-browse.html#product-attributes\">product attributes</a> for the specific product.   <br /><br />For more details, see <a href=\"/api-docs/buy/static/api-browse.html#Check\">Check compatibility</a> in the Buy Integration Guide.  <br /><br /> <span class=\"tablenote\"><b>Note: </b> The only products supported are cars, trucks, and motorcycles. </span>  <br /><br /> <p>For an example, see the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search#w4-w1-w5-ReturnItemsthatareCompatiblewiththeKeywordandVehicle-9\">Samples</a> section. <br /><br /> <span class=\"tablenote\"><b>Note: </b> Testing in Sandbox is only supported using mock data. See <a href=\"/api-docs/buy/static/api-browse.html#sbox-test\">Testing search in the Sandbox</a> for details. </span>   <br /><br /><b>Required: </b><ul> <li><b> q</b> (keyword)</li>  <li> one fitment supported category ID (such as <code>33559</code> Brakes)</li>  <li> a least one <a href=\"/api-docs/buy/static/api-browse.html#product-attributes\">product attribute name/value pair</a></li></ul> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/gct:CompatibilityFilter
        :param str epid: The ePID is the eBay product identifier of a product from the eBay product catalog. This field limits the results to only items in the specified ePID. <br /><br />The <b> Marketing</b> API <b>getMerchandisedProducts</b> method and the <b>Browse</b> API <b> getItem</b>, <b> getItemByLegacyId</b>, and <b> getItemsByItemGroup</b> calls return the ePID of the product.  You can also use the <a href=\"/api-docs/commerce/catalog/resources/product_summary/methods/search\">product_summary/search</a> method in the <b>Catalog</b> API to search for the ePID of the product. <br /><br /><b> For example: </b><br/><code>/buy/browse/v1/item_summary/search?epid=15032</code> <br /><br /><b> Maximum: </b> 1    <br /><br /><b> Required: </b> The method must have  <b> category_ids</b>, <b> epid</b>,  <b> gtin</b>,  or <b> q</b>  (or any combination of these)
        :param str fieldgroups: This field is a comma separated list of values that lets you control what is returned in the response. The default is <b> MATCHING_ITEMS</b>, which returns the items that match the keyword or category specified. The other values return data that can be used to create histograms or provide additional information.  <br /><br /><b> Valid Values: </b> <ul>    <li><b> ASPECT_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.aspectDistributions\">aspectDistributions</a> container, which has the <b> dominantCategoryId</b>, <b> matchCount</b>, and <b> refinementHref</b> for the various aspects of the items found. For example, if you searched for 'Mustang', some of the aspect would be <b> Model Year</b>,  <b> Exterior Color</b>, <b> Vehicle Mileage</b>, etc. <br /> <br /><span class=\"tablenote\"> <b>Note: </b> ASPECT_REFINEMENTS are category specific.</span> <br /><br /></li>   <li><b> BUYING_OPTION_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.buyingOptionDistributions\">buyingOptionDistributions</a>  container, which has the <b> matchCount</b> and <b> refinementHref</b> for <b> AUCTION</b> and <b> FIXED_PRICE</b> (Buy It Now) items. <br /><br /><span class=\"tablenote\"> <b>Note: </b>Classified items are not supported and only \"Buy It Now\" (non-auction) items are returned.</span> <br /><br /> </li>   <li><b> CATEGORY_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.categoryDistributions\">categoryDistributions</a> container, which has the categories that the item is in.   </li>   <li><b> CONDITION_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.conditionDistributions\">conditionDistributions</a>  container, such as <b> NEW</b>, <b> USED</b>, etc. Within these groups are multiple states of the condition. For example, <b> New </b> can be New without tag, New in box, New without box, etc. </li>   <li><b> EXTENDED</b> - This returns the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search#response.itemSummaries.shortDescription\">shortDescription</a> field, which provides condition and item aspect information and the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search#response.itemSummaries.itemLocation.city\">itemLocation.city</a> field.   </li>  <li><b> MATCHING_ITEMS</b> - This is meant to be used with one or more of the refinement values above. You use this to return the specified refinements and all the matching items. </li> <li><b> FULL </b> - This returns all the refinement containers and all the matching items.</li>   </ul> Code so that your app gracefully handles any future changes to this list.  <br /><br /><b>Default: </b> MATCHING_ITEMS
        :param str filter: This field supports multiple field filters that can be used to limit/customize the result set. <br /><br /><b> For example: </b><br /><code>/buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50]</code><br /><br />You can also combine filters. <br /><code>/buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50],sellers:{rpseller|bigSal} </code>   <br /><br />The following are the supported filters. For details and examples for all the filters, see <a href=\"/api-docs/buy/static/ref-buy-browse-filters.html\">Buy API Field Filters</a>. <div style=\"overflow-x:auto;\"> <table>  <tr>  <td>  <ul>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#bidCount\">bidCount</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#buyingOptions\">buyingOptions</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#charityOnly\">charityOnly</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#conditionIds\">conditionIds</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#conditions\">conditions</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#deliveryCountry\">deliveryCountry</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#deliveryOptions\">deliveryOptions</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#deliveryPostalCode\">deliveryPostalCode</a> </li>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#excludeCategoryIds\">excludeCategoryIds</a> </li>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#excludeSellers\">excludeSellers</a> </li>  </ul></td> <td>  <ul> <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#guaranteedDeliveryInDays\">guaranteedDeliveryInDays</a> </li>     <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemEndDate\">itemEndDate</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemLocationCountry\">itemLocationCountry</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemStartDate\">itemStartDate</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#maxDeliveryCost\">maxDeliveryCost</a></li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#paymentMethods\">paymentMethods</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupCountry\">pickupCountry</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupPostalCode\">pickupPostalCode</a> </li>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupRadius\">pickupRadius</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupRadiusUnit\">pickupRadiusUnit</a> </li>  </ul></td> <td>  <ul>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#price\">price</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#priceCurrency\">priceCurrency</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#priorityListing\">priorityListing</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#qualifiedPrograms\">qualifiedPrograms</a> </li>          <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#returnsAccepted\">returnsAccepted</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#searchInDescription\">searchInDescription</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#sellerAccountTypes\">sellerAccountTypes</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#sellers\">sellers</a> </li>  </ul></td>  </tr>  </table>  </div> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:FilterField
        :param str gtin: This field lets you search by the Global Trade Item Number of the item as defined by <a href=\"https://www.gtin.info\" target=\"_blank\">https://www.gtin.info</a>. You can search only by UPC (Universal Product Code). If you have other formats of GTIN, you need to search by keyword.  <br /><br /><b> For example: </b><br/><code> /buy/browse/v1/item_summary/search?gtin=099482432621</code> <br /><br /> <b> Maximum: </b> 1     <br /><br /><b> Required: </b> The method must have <b> category_ids</b>, <b> epid</b>, <b> gtin</b>, or <b> q</b> (or any combination of these)
        :param str limit: The number of items, from the result set, returned in a single page.  <br /><br /><b> Default:</b> 50    <br /><br /><b> Maximum number of items per page (limit): </b>200     <br /><br /> <b> Maximum number of items in a result set: </b> 10,000
        :param str offset: Specifies the number of items to skip in the result set. This is used with the <b> limit</b> field to control the pagination of the output.  <br /><br />If <b> offset</b> is 0 and <b> limit</b> is 10, the method will retrieve items 1-10 from the list of items returned, if <b> offset</b> is 10 and <b> limit</b> is 10, the method will retrieve items 11 thru 20 from the list of items returned.  <br /><br /><b> Valid Values</b>: 0-10,000 (inclusive)   <br /> <br /> <b> Default:</b> 0    <br /> <br /> <b> Maximum number of items returned: </b> 10,000  
        :param str q: A string consisting of one or more keywords that are used to search for items on eBay. The keywords are handled as follows:<ul><li>If the keywords are separated by a space, it is treated as an AND. In the following example, the query returns items that have iphone <b>AND</b> ipad.<br /><br /><code>/buy/browse/v1/item_summary/search?q=iphone ipad</code><br/><br /></li><li>If the keywords are input using parentheses and separated by a comma, or if they are URL-encoded, it is treated as an OR. In the following examples, the query returns items that have iphone <b>OR</b> ipad.<br /><br /><code>/buy/browse/v1/item_summary/search?q=(iphone, ipad)</code><br /><br /><code>/buy/browse/v1/item_summary/search?q=%28iphone%2c%20ipad%29</code><br /><br /></li></ul><b>Restriction:</b> The <code>*</code> wildcard character is <b>not</b> allowed in this field.<br /><br /><b>Required:</b> The method must have <b>category_ids</b>, <b>epid</b>, <b>gtin</b>, or <b>q</b> (or any combination of these). 
        :param str sort: Specifies the order and the field name to use to sort the items. <br /><br />You can sort items by price (in ascending or descending order) or by distance (only applicable if the <a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupCountry\">\"pickup\" filters</a> are used, and only ascending order is supported). You can also sort items by listing date, with the most recently listed (newest) items appearing first.<br /><br /><span class=\"tablenote\"><b>Note: </b> To sort in descending order, insert a hyphen (<code>-</code>) before the field name. If no <b>sort</b> parameter is submitted, the result set is sorted by &quot;<a href=\"https://pages.ebay.com/help/sell/searchstanding.html\" target=\"_blank\">Best Match</a>&quot;.</span><br /><br />The following are examples of using the <b> sort</b> query parameter.<br /><br /><table><tr><th>Sort</th><th>Result</th>  </tr> <tr> <td><code>sort=price</code></td>  <td> Sorts by <b> price</b> in ascending order (lowest price first)</td> </tr>   <tr>  <td><code>sort=-price</code></td>  <td> Sorts by <b> price</b> in descending order (highest price first)</td> </tr>   <tr>  <td><code>sort=distance</code></td>  <td> Sorts by <b> distance</b> in ascending order (shortest distance first)</td> </tr> <tr> <td><code>sort=newlyListed</code></td>  <td>Sorts by <b>listing date</b> (most recently listed/newest items first)</td> </tr> <tr> <td><code>sort=endingSoonest</code></td>  <td>Sorts by <b>date/time</b> the listing ends (listings nearest to end date/time first)</td> </tr></table>  <br /><b> Default: </b> Ascending For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:SortField
        :return: SearchPagedCollection
        """
        try:
            return self._method_paged(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemSummaryApi, buy_browse.ApiClient, 'search', BuyBrowseException, False, ['buy.browse', 'item_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_search_by_image(self, **kwargs):  # noqa: E501
        """search_by_image  # noqa: E501

        <img src=\"/cms/img/docs/experimental-icon.svg\" class=\"legend-icon experimental-icon\" alt=\"Experimental Release\" title=\"Experimental Release\">  This is an <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#experimental\">Experimental</a> method. <p>This method searches for eBay items based on a image and retrieves summaries of the items. You pass in a Base64 image in the request payload and can refine the search by category, or eBay product ID (ePID), or a combination of these using URI parameters.  <br /><br />To get the Base64 image string, you can use sites such as <a href=\"https://codebeautify.org/image-to-base64-converter\" target=\"_blank\">https://codebeautify.org/image-to-base64-converter</a>. </p>      <p>This method also supports the following:  <ul> <li>Filtering by the value of one or multiple fields, such as listing format, item condition, price range, location, and more.  For the fields supported by this method, see the <a href=\"#uri.filter\">filter</a> parameter.</li>   <li>Filtering by item aspects using the <a href=\"#uri.aspect_filter\">aspect_filter</a> parameter. </li>  </ul></p>  <p>For details and examples of these capabilities, see <a href=\"/api-docs/buy/static/api-browse.html\">Browse API</a> in the Buying Integration Guide.</p>     <h3><b>Pagination and sort controls</b></h3>  <p>There are pagination controls (<b>limit</b> and <b>offset</b> fields) and <b> sort</b> query parameters that control/sort the data that is returned. By default, the results are sorted by &quot;Best Match&quot;. For more information about  Best Match, see the eBay help page <a href=\"https://pages.ebay.com/help/sell/searchstanding.html\" target=\"_blank\">Best Match</a>.  </p>    <h3><b> URLs for this method</b></h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/item_summary/search_by_image?</code></li>            <li><b> Sandbox URL:  </b>Due to the data available, this method is not supported in the eBay Sandbox.  To test your integration, use the Production URL.</li>           </ul>    </p>              <h3><b> Request headers</b></h3> This method uses the  <b>X-EBAY-C-ENDUSERCTX</b> request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.    For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the Buying Integration Guide.   <h3><b>URL Encoding for Parameters</b></h3>            <p>Query parameter values need to be URL encoded. For details, see <a href=\"/api-docs/static/rest-request-components.html#parameters\">URL encoding query parameter values</a>.  For readability, code examples in this document have not been URL encoded.</p>  <h3><b>Restrictions </b></h3> <p>This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p> <span class=\"tablenote\"><b>eBay Partner Network: </b> In order to receive a commission for your sales, you must use the URL returned in the <code>itemAffiliateWebUrl</code> field to forward your buyer to the ebay.com site. </span>   # noqa: E501

        :param SearchByImageRequest body: The container for the image information fields.
        :param str aspect_filter: This field lets you filter by item aspects. The aspect name/value pairs and category, which is required, is used to limit the results to specific aspects of the item. For example, in a clothing category one aspect pair would be Color/Red. <br /><br />For example, the method below uses the category ID for Women's Clothing. This will return only items for a woman's red shirt.<br /><br /><code>category_ids=15724&aspect_filter=categoryId:15724,Color:{Red}</code>  <br /><br /><b>Required: </b> The category ID is required <i>twice</i>; once as a URI parameter and as part of the <b> aspect_filter</b>. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/gct:AspectFilter
        :param str category_ids: The category ID is used to limit the results. This field can have one category ID or a comma separated list of IDs.    <br /><br /><span class=\"tablenote\"><b> Note: </b>Currently, you can pass in only one category ID per request.</span> <br /> <br />You can also use any combination of the <b> category_Ids</b> and <b> epid</b> fields. This gives you additional control over the result set.<br /> <br />The list of eBay category IDs is not published and category IDs are not the same across all the eBay marketplaces. You can use the following techniques to find a category by site: <ul> <li>Use the <a href=\"https://pages.ebay.com/sellerinformation/news/categorychanges.html\" target=\"_blank\">Category Changes page</a>.</li> <li>Use the Taxonomy API. For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  <li>Submit the following method to get the <b> dominantCategoryId</b> for an item. <br /><code>/buy/browse/v1/item_summary/search?q=<em > keyword</em>&fieldgroups=ASPECT_REFINEMENTS  </code></li></ul>   <b> Required: </b> The method must have <b> category_ids</b> or <b> epid</b> (or any combination of these)
        :param str charity_ids: The charity ID is used to limit the results to only items associated with the specified charity. This field can have one charity ID or a comma separated list of IDs. The method will return all the items associated with the specified charities.<br /><br /> <b>For example:</b><br /><code>/buy/browse/v1/item_summary/search?charity_ids=13-1788491,300108469</code><br /><br />The charity ID is the charity's registration ID, also known as the Employer Identification Number (EIN). In GB, it is the Charity Registration Number (CRN), commonly called \"Charity Number\".   <ul><li>To find the charities eBay supports, you can search for a charity at <a href=\"https://charity.ebay.com/search\" target=\"_blank\">Charity Search </a> or go to <a href=\"https://www.ebay.com/b/Charity/bn_7114598164\" target=\"_blank\">Charity Shop</a>.</li>   <li>To find the charity ID of a specific charity, click on a charity and use the EIN number. For example, the charity ID for  <a href=\"https://charity.ebay.com/charity/American-Red-Cross/3843\" target=\"_blank\">American Red Cross</a>, is <code>530196605</code>.</li></ul> You  can also use any combination of the <code>category_Ids</code> and <code>q</code> fields with a <code>charity_Ids</code> to filter the result set. This gives you additional control over the result set. <br /><br /><b>Restriction: </b> This is supported only on the US and GB marketplaces.<br /><br /><b>Maximum: </b> 20 IDs <br /><br /><b>Required:</b> One ID
        :param str fieldgroups: This field is a comma separated list of values that lets you control what is returned in the response. The default is <b> MATCHING_ITEMS</b>, which returns the items that match the keyword or category specified. The other values return data that can be used to create histograms or provide additional information.  <br /><br /><b> Valid Values: </b> <ul>    <li><b> ASPECT_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.aspectDistributions\">aspectDistributions</a> container, which has the <b> dominantCategoryId</b>, <b> matchCount</b>, and <b> refinementHref</b> for the various aspects of the items found. For example, if you searched for 'Mustang', some of the aspect would be <b> Model Year</b>,  <b> Exterior Color</b>, <b> Vehicle Mileage</b>, etc. <br /> <br /><span class=\"tablenote\"> <b>Note: </b> ASPECT_REFINEMENTS are category specific.</span> <br /><br /></li>   <li><b> BUYING_OPTION_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.buyingOptionDistributions\">buyingOptionDistributions</a>  container, which has the <b> matchCount</b> and <b> refinementHref</b> for <b> AUCTION</b> and <b> FIXED_PRICE</b> (Buy It Now) items. <br /><br /><span class=\"tablenote\"> <b>Note: </b>Classified items are not supported and only \"Buy It Now\" (non-auction) items are returned.</span> <br /><br /> </li>   <li><b> CATEGORY_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.categoryDistributions\">categoryDistributions</a> container, which has the categories that the item is in.   </li>   <li><b> CONDITION_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.conditionDistributions\">conditionDistributions</a>  container, such as <b> NEW</b>, <b> USED</b>, etc. Within these groups are multiple states of the condition. For example, <b> New </b> can be New without tag, New in box, New without box, etc. </li>   <li><b> EXTENDED</b> - This returns the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search#response.itemSummaries.shortDescription\">shortDescription</a> field, which provides condition and item aspect information and the <a href=\"/api-docs/buy/browse/resources/item_summary/methods/search#response.itemSummaries.itemLocation.city\">itemLocation.city</a> field.   </li>  <li><b> MATCHING_ITEMS</b> - This is meant to be used with one or more of the refinement values above. You use this to return the specified refinements and all the matching items. </li> <li><b> FULL </b> - This returns all the refinement containers and all the matching items.</li>   </ul> Code so that your app gracefully handles any future changes to this list.  <br /><br /><b>Default: </b> MATCHING_ITEMS
        :param str filter: This field supports multiple field filters that can be used to limit/customize the result set. <br /><br /><b> For example: </b><br /><code>/buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50]</code><br /><br />You can also combine filters. <br /><code>/buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50],sellers:{rpseller|bigSal} </code>   <br /><br />The following are the supported filters. For details and examples for all the filters, see <a href=\"/api-docs/buy/static/ref-buy-browse-filters.html\">Buy API Field Filters</a>. <div style=\"overflow-x:auto;\"> <table>  <tr>  <td>  <ul>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#bidCount\">bidCount</a> </li><li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#buyingOptions\">buyingOptions</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#charityOnly\">charityOnly</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#conditionIds\">conditionIds</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#conditions\">conditions</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#deliveryCountry\">deliveryCountry</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#deliveryOptions\">deliveryOptions</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#deliveryPostalCode\">deliveryPostalCode</a> </li>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#excludeCategoryIds\">excludeCategoryIds</a> </li>  </ul></td> <td>  <ul>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#excludeSellers\">excludeSellers</a> </li> <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#guaranteedDeliveryInDays\">guaranteedDeliveryInDays</a> </li>     <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemEndDate\">itemEndDate</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemLocationCountry\">itemLocationCountry</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemStartDate\">itemStartDate</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#maxDeliveryCost\">maxDeliveryCost</a></li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#paymentMethods\">paymentMethods</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupCountry\">pickupCountry</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupPostalCode\">pickupPostalCode</a> </li>  </ul> </td>   <td>  <ul>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupRadius\">pickupRadius</a> </li>   <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupRadiusUnit\">pickupRadiusUnit</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#price\">price</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#priceCurrency\">priceCurrency</a> </li>  <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#qualifiedPrograms\">qualifiedPrograms</a> </li>          <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#returnsAccepted\">returnsAccepted</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#sellerAccountTypes\">sellerAccountTypes</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#sellers\">sellers</a> </li>  </ul></td>  </tr>  </table>  </div> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:FilterField
        :param str limit: The number of items, from the result set, returned in a single page.  <br /><br /><b> Default:</b> 50   <br /> <br /><b> Maximum number of items per page (limit): </b>200  <br /> <br /> <b> Maximum number of items in a result set: </b> 10,000
        :param str offset: The number of items to skip in the result set. This is used with the <b> limit</b> field to control the pagination of the output.  <br /><br />If <b> offset</b> is 0 and <b> limit</b> is 10, the method will retrieve items 1-10 from the list of items returned, if <b> offset</b> is 10 and <b> limit</b> is 10, the method will retrieve items 11 thru 20 from the list of items returned.  <br /><br /><b> Valid Values</b>: 0-10,000 (inclusive)   <br /> <br /> <b> Default:</b> 0    <br /> <br /> <b> Maximum number of items returned: </b> 10,000  
        :param str sort: Specifies the order and the field name to use to sort the items. <br /><br />You can sort items by price (in ascending or descending order) or by distance (only applicable if the <a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#pickupCountry\">\"pickup\" filters</a> are used, and only ascending order is supported). You can also sort items by listing date, with the most recently listed (newest) items appearing first.<br /><br /><span class=\"tablenote\"><b>Note: </b> To sort in descending order, insert a hyphen (<code>-</code>) before the field name. If no <b>sort</b> parameter is submitted, the result set is sorted by &quot;<a href=\"https://pages.ebay.com/help/sell/searchstanding.html\" target=\"_blank\">Best Match</a>&quot;.</span><br /><br />The following are examples of using the <b> sort</b> query parameter.<br /><br /><table><tr><th>Sort</th><th>Result</th>  </tr> <tr> <td><code>sort=price</code></td>  <td> Sorts by <b> price</b> in ascending order (lowest price first)</td> </tr>   <tr>  <td><code>sort=-price</code></td>  <td> Sorts by <b> price</b> in descending order (highest price first)</td> </tr>   <tr>  <td><code>sort=distance</code></td>  <td> Sorts by <b> distance</b> in ascending order (shortest distance first)</td> </tr> <tr> <td><code>sort=newlyListed</code></td>  <td>Sorts by <b>listing date</b> (most recently listed/newest items first)</td> </tr>  <tr> <td><code>sort=endingSoonest</code></td>  <td>Sorts by <b>date/time</b> the listing ends (listings nearest to end date/time first)</td> </tr> </table>  <br /><b> Default: </b> Ascending For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:SortField
        :return: SearchPagedCollection
        """
        try:
            return self._method_paged(buy_browse.Configuration, '/buy/browse/v1', buy_browse.SearchByImageApi, buy_browse.ApiClient, 'search_by_image', BuyBrowseException, False, ['buy.browse', 'search_by_image'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_add_item(self, **kwargs):  # noqa: E501
        """add_item  # noqa: E501

        <span class=\"tablenote\"><b>Note: </b><img src=\"/cms/img/docs/experimental-icon.svg\" class=\"legend-icon experimental-icon\" alt=\"Experimental Release\" title=\"Experimental Release\" alt=\"Experimental Release\" title=\"Experimental Release\" />  This is an <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#experimental\">Experimental</a> method that is available as a <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"> <img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\" title=\"Limited Release\"  alt=\"Limited Release\" />(Limited Release)</a> to select developers approved by business units.</span>  <p>This method creates an eBay cart for the eBay member, if one does not exist, and adds items to that cart. Because a cart never expires, any item added to the cart will remain in the cart until it is removed.  <br /><br />To use this method, you must submit a RESTful item ID and the quantity of the item. If the <b> quantity</b> value is greater than the number of available, the <b> quantity</b> value is changed to the number available and a warning is returned. For example, if there are 15 baseballs available and you set the <b> quantity</b> value to 50, the service automatically changes the value of <b>quantity</b> to 15.    <br /><br />The response returns all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API.   The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, when the listing has ended or the item is out of stock, whether it has just been added to the cart or has been in the cart for some time, the item will be returned in the <b> unavailableCartItems</b> container.</p>       <p span class=\"tablenote\"><b>Note: </b>There are differences between how legacy APIs, such as Finding, and RESTful APIs, such as Browse, return the identifier of an \"item\" and what the item ID represents. If you have an item ID from one of the legacy APIs, you can use the legacy item ID with the <a href=\"/api-docs/buy/browse/resources/item/methods/getItemByLegacyId\"> getItemByLegacyId</a> method to retrieve the RESTful ID for that item. For more information about how to use legacy IDs with the Buy APIs, see <a href=\"/api-docs/buy/static/api-browse.html#Legacy\">Legacy API compatibility</a> in the Buying Integration guide.</p>           <h3><b>URLs for this method</b></h3>           <p><ul>  <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/shopping_cart/add_item</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/add_item</code>  <br /><br /><b>Note: </b>This method is not available in the eBay API Explorer.</li>    </ul>    </p>            <h3><b>Restrictions </b></h3> <ul> <li>This method can be used only for eBay members.</li>  <li>You can add only items with a FIXED_PRICE that accept PayPal as a payment.  </li> </ul> <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p>    # noqa: E501

        :param AddCartItemInput body:
        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'add_item', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_shopping_cart(self, **kwargs):  # noqa: E501
        """get_shopping_cart  # noqa: E501

        <span class=\"tablenote\"><b>Note: </b><img src=\"/cms/img/docs/experimental-icon.svg\" class=\"legend-icon experimental-icon\" alt=\"Experimental Release\" title=\"Experimental Release\" />  This is an <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#experimental\">experimental</a> method that is available as a <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"> <img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\" title=\"Limited Release\"  alt=\"Limited Release\" />(Limited Release)</a> to select developers approved by business units.</span>    <p>This method retrieves all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API. There are no URI parameters or request payload.  <br /><br />The response returns the summary details of all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API. If the cart is empty, the response is HTTP 204. </p>   <br /><br /> The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, when the listing has ended or the item is out of stock, the item will be returned in the <b> unavailableCartItems</b> container.                         <h3><b>URLs for this method</b></h3>           <p><ul>  <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/shopping_cart/</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/</code>  <br /><br /><b>Note: </b>This method is not available in the eBay API Explorer.</li>    </ul>    </p>         <h3><b>Restrictions </b></h3> <p>This method can be used only for eBay members. For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p>  # noqa: E501

        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'get_shopping_cart', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_remove_item(self, **kwargs):  # noqa: E501
        """remove_item  # noqa: E501

        <span class=\"tablenote\"><b>Note: </b><img src=\"/cms/img/docs/experimental-icon.svg\" class=\"legend-icon experimental-icon\" alt=\"Experimental Release\" title=\"Experimental Release\" />  This is an <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#experimental\">experimental</a> method that is available as a <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"> <img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\" title=\"Limited Release\"  alt=\"Limited Release\" />(Limited Release)</a> to select developers approved by business units.</span>  <p>This method removes a specific item from the eBay member's cart. You specify the ID of the item in the cart (<b>cartItemId</b>) that you want to remove.   <br /><br />The response returns all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API. If you remove the last item in the cart, the response is HTTP 204.<br /><br />  The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, when the listing has ended or the item is out of stock, the item will be returned in the <b> unavailableCartItems</b> container.</p>  <p span class=\"tablenote\"><b>Note: </b> The  <b> cartItemId</b> is not the same as the item ID. The <b> cartItemId</b> is the identifier of a specific item <i>in</i> the cart and is generated when the item was added to the cart.</span></p>               <h3><b>URLs for this method</b></h3>           <p><ul>  <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/shopping_cart/remove_item</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/remove_item</code>  <br /><br /><b>Note: </b>This method is not available in the eBay API Explorer.</li>    </ul>    </p>         <h3><b>Restrictions </b></h3> <p>This method can be used only for eBay members. For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p>  # noqa: E501

        :param RemoveCartItemInput body:
        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'remove_item', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_update_quantity(self, **kwargs):  # noqa: E501
        """update_quantity  # noqa: E501

        <span class=\"tablenote\"><b>Note: </b><img src=\"/cms/img/docs/experimental-icon.svg\" class=\"legend-icon experimental-icon\" alt=\"Experimental Release\" title=\"Experimental Release\" />  This is an <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#experimental\">experimental</a> method that is available as a <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"> <img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\" title=\"Limited Release\"  alt=\"Limited Release\" />(Limited Release)</a> to select developers approved by business units.</span>  <p>This method updates the quantity value of a specific item in the eBay member's cart. You specify the ID of the item in the cart (<b>cartItemId</b>) and the new value for the quantity. If the <b> quantity</b> value is greater than the number of available, the <b> quantity</b> value is changed to the number available and a warning is returned. For example, if there are 15 baseballs available and you set the <b> quantity</b> value to 50, the service automatically changes the value of <b>quantity</b> to 15.   <br /><br />The response returns all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API.   The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, the listing has ended or the item is out of stock, the item will be returned in the <b> unavailableCartItems</b> container.</p>  <p span class=\"tablenote\"><b>Note: </b> The  <b> cartItemId</b> is not the same as the item ID. The <b> cartItemId</b> is the identifier of a specific item <i>in</i> the cart and is generated when the item was added to the cart.</span></p>                 <h3><b>URLs for this method</b></h3>           <p><ul>  <li><b> Production URL: </b> <code>https://api.ebay.com/buy/browse/v1/shopping_cart/update_quantity</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/update_quantity</code>  <br /><br /><b>Note: </b>This method is not available in the eBay API Explorer.</li>    </ul>    </p>         <h3><b>Restrictions </b></h3> <p>This method can be used only for eBay members. For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/browse/overview.html#API\">API Restrictions</a>.</p>  # noqa: E501

        :param UpdateCartItemInput body:
        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'update_quantity', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_deal_get_deal_items(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_deal_items  # noqa: E501

        This method retrieves a paginated set of deal items. The result set contains all deal items associated with the specified search criteria and marketplace ID. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID. (required)
        :param str category_ids: The unique identifier of the eBay category for the search.
        :param str commissionable: A filter for commissionable deals. Restriction: This filter is currently only supported for the US marketplace.
        :param str delivery_country: A filter for items that can be shipped to the specified country.
        :param str limit: The maximum number of items, from the current result set, returned on a single page.
        :param str offset: The number of items that will be skipped in the result set. This is used with the limit field to control the pagination of the output. For example, if the offset is set to 0 and the limit is set to 10, the method will retrieve items 1 through 10 from the list of items returned. If the offset is set to 10 and the limit is set to 10, the method will retrieve items 11 through 20 from the list of items returned. Default: 0
        :return: DealItemSearchResponse
        """
        try:
            return self._method_paged(buy_deal.Configuration, '/buy/deal/v1', buy_deal.DealItemApi, buy_deal.ApiClient, 'get_deal_items', BuyDealException, False, ['buy.deal', 'deal_item'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_deal_get_event(self, x_ebay_c_marketplace_id, event_id, **kwargs):  # noqa: E501
        """get_event  # noqa: E501

        This method retrieves the details for an eBay event. The result set contains detailed information associated with the specified event ID, such as applicable coupons, start and end dates, and event terms. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID. (required)
        :param str event_id: The unique identifier for the eBay event. (required)
        :return: Event
        """
        try:
            return self._method_single(buy_deal.Configuration, '/buy/deal/v1', buy_deal.EventApi, buy_deal.ApiClient, 'get_event', BuyDealException, False, ['buy.deal', 'event'], (x_ebay_c_marketplace_id, event_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_deal_get_events(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_events  # noqa: E501

        This method returns paginated results containing all eBay events for the specified marketplace. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID. (required)
        :param str limit: The maximum number of items, from the current result set, returned on a single page. Default: 20 Maximum Value: 100
        :param str offset: The number of items that will be skipped in the result set. This is used with the limit field to control the pagination of the output. For example, if the offset is set to 0 and the limit is set to 10, the method will retrieve items 1 through 10 from the list of items returned. If the offset is set to 10 and the limit is set to 10, the method will retrieve items 11 through 20 from the list of items returned. Default: 0
        :return: EventSearchResponse
        """
        try:
            return self._method_paged(buy_deal.Configuration, '/buy/deal/v1', buy_deal.EventApi, buy_deal.ApiClient, 'get_events', BuyDealException, False, ['buy.deal', 'event'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_deal_get_event_items(self, event_ids, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_event_items  # noqa: E501

        This method returns a paginated set of event items. The result set contains all event items associated with the specified search criteria and marketplace ID. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  # noqa: E501

        :param str event_ids: The unique identifiers for the eBay events. Maximum Value: 1 (required)
        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID. (required)
        :param str category_ids: The unique identifier of the eBay category for the search. Maximum Value: 1
        :param str delivery_country: A filter for items that can be shipped to the specified country.
        :param str limit: The maximum number of items, from the current result set, returned on a single page. Default: 20
        :param str offset: The number of items that will be skipped in the result set. This is used with the limit field to control the pagination of the output. For example, if the offset is set to 0 and the limit is set to 10, the method will retrieve items 1 through 10 from the list of items returned. If the offset is set to 10 and the limit is set to 10, the method will retrieve items 11 through 20 from the list of items returned. Default: 0
        :return: EventItemSearchResponse
        """
        try:
            return self._method_paged(buy_deal.Configuration, '/buy/deal/v1', buy_deal.EventItemApi, buy_deal.ApiClient, 'get_event_items', BuyDealException, False, ['buy.deal', 'event_item'], (event_ids, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_feed(self, accept, x_ebay_c_marketplace_id, range, feed_scope, category_id, **kwargs):  # noqa: E501
        """get_item_feed  # noqa: E501

        <p>This method lets you download a TSV_GZIP (tab separated value gzip) <b> Item</b> feed file. The feed file contains all the items from <b> all</b> the child categories of the specified category.  The first line of the file is the header, which labels the columns and indicates the order of the values on each line.  Each header is described in the <a href=\"/api-docs/buy/feed/resources/item/methods/getItemFeed#h3-response-fields\">Response fields</a> section.  </p> <p> There are two types of item feed files generated: <ul> <li>A daily <b>Item</b> feed file containing all the newly listed items for a specific category, date, and marketplace (<b>feed_scope</b> = <code>NEWLY_LISTED</code>)</li>  <li>A weekly <b>Item Bootstrap</b> feed file containing <i> all</i> the items in a specific category and marketplace (<b>feed_scope</b> = <code>ALL_ACTIVE</code>)</li>  </ul>  </p>   <p><span class=\"tablenote\"><b>Note: </b>  Filters are applied to the feed files. For details, see <a href=\"/api-docs/buy/static/api-feed.html#feed-filters\">Feed File Filters</a>. When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future.</span></p>                                   <h3><b>URLs for this method</b></h3>   <p><ul>    <li><b> Production URL: </b> <code>https://api.ebay.com/buy/feed/v1_beta/item?</code></li>    <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/feed/v1_beta/item?</code></li>   </ul> </p>              <h3><b>Downloading feed files </b></h3>             <p>Item feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the <a href=\"#range-header\">Range</a> request header. The <a href=\"#content-range\">Content-range</a> response header indicates where in the full resource this partial chunk of data belongs  and the total number of bytes in the file.       For more information about using these headers, see <a href=\"/api-docs/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>.    </p>    <p>In addition to the API, there is an open source <a href=\"https://github.com/eBay/FeedSDK\" target=\"_blank\">Feed SDK</a> written in Java that downloads, combines files into a single file when needed, and unzips the entire feed file. It also lets you specify field filters to curate the items in the file.</p>              <p><span class=\"tablenote\">  <b> Note:</b> A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.</span>  </p>                <h3><b>Restrictions </b></h3>                <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/feed/overview.html#API\">API Restrictions</a>.</p>  # noqa: E501

        :param str accept: The formats that the client accepts for the response.<br /><br />A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format.<br /><br /><b>Default:</b> <code>application/json,text/tab-separated-values</code> (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. <b>Note: </b> This value is case sensitive.<br /><br />For example: <br />&nbsp;&nbsp;<code>X-EBAY-C-MARKETPLACE-ID = EBAY_US</code>  <br /><br /> For a list of supported sites see, <a href=\"/api-docs/buy/feed/overview.html#API\">API Restrictions</a>. (required)
        :param str range: <a name=\"range-header\"></a>This header specifies the range in bytes of the chunks of the gzip file being returned. <br /><br /><b> Format:</b> <code >bytes=<em>startpos</em>-<em>endpos</em></code><br /><br />  For example, the following retrieves the first 10 MBs of the feed file. <br /><br />&nbsp;&nbsp;<code>Range bytes=0-10485760</code> <br /><br />For more information about using this header, see <a href=\"/api-docs/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>. <br /><br /><b>Maximum:</b> 100 MB (10MB in the Sandbox) (required)
        :param str feed_scope: Specifies the type of feed file to return. <br /><br /><b>Valid Values: </b>   <ul> <li><b> NEWLY_LISTED</b> - Returns the daily <b>Item</b> feed file containing all Good 'Til Cancelled items that were listed on the day specified by the <b> date</b> parameter in the category specified by the <b> category_id</b> parameter.  <br /><br /><code>/item?feed_scope=NEWLY_LISTED&category_id=15032&date=20170925</code></li>  <li><b>ALL_ACTIVE</b> - Returns the weekly <b>Item Bootstrap</b> feed file containing all the Good 'Til Cancelled items in the category specified by the <b> category_id</b> parameter.  <br /><br /><span class=\"tablenote\"><b>Note:</b> Bootstrap files are generated every Tuesday and the file is available on Wednesday. However, the exact time the file is available can vary so we recommend you download the Bootstrap file on Thursday. The items in the file are the items that were in the specified category on Sunday.</span> <br /><br /><code>/item?feed_scope=ALL_ACTIVE&category_id=15032</code>  </ul> (required)
        :param str category_id: An eBay top-level category ID of the items to be returned in the feed file. <br /> <br />The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplace, you can use the Taxonomy API <a href=\"/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategoryTree\">getCategoryTree</a> method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the <b> categoryTreeNodeLevel </b> field. <br /><br /><b>For example: </b><br />&nbsp;&nbsp;<code>\"categoryTreeNodeLevel\": 1</code> <br /><br />For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  </ul> <br /><br />   <b>Restriction: </b> Must be a top-level (L1) category </b> (required)
        :param str _date: The date of the daily <b>Item</b> feed file (<b>feed_scope</b>=<code>NEWLY_LISTED</code>) you want. <p>The <b> date</b> is required only for the daily <b>Item</b> feed file. If you specify a date for the <b>Item Bootstrap</b> file (<b>feed_scope</b>=<code>ALL_ACTIVE</code>), the date is ignored and the latest file is returned. The date the <b>Item Bootstrap</b> feed file was generated is returned in the <b>Last-Modified</b> response header.</code></p>    <p>The <b> Item</b> feed files are generated every day and there are 14 daily files available.</p>  <span class=\"tablenote\"> <b>Note: </b><ul>  <li>The daily <b>Item</b> feed files are available each day after 9AM MST (US Mountain Standard Time), which is -7 hours UTC time.</li>    <li>There is a 48 hour latency when generating the <b> Item</b> feed files. This means you can download the file for July 10th on July 12 after 9AM MST. <br /><br /><b>Note: </b> For categories with a large number of items, the latency can be up to 72 hours.</li> </ul></span> <p><b> Format: </b><code>yyyyMMdd</code><br /><br /><b> Requirements: </b> <ul>  <li>Required when <b>feed_scope</b>=<code>NEWLY_LISTED</code> </li>  <li>Must be within 3-14 days in the past</li></ul>
        :return: ItemResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemApi, buy_feed.ApiClient, 'get_item_feed', BuyFeedException, False, ['buy.feed', 'item'], (accept, x_ebay_c_marketplace_id, range, feed_scope, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_group_feed(self, accept, x_ebay_c_marketplace_id, feed_scope, category_id, **kwargs):  # noqa: E501
        """get_item_group_feed  # noqa: E501

        <p>This method lets you download a TSV_GZIP (tab separated value gzip) <b> Item Group</b> feed file. An item group is an item that has various aspect differences, such as color, size, storage capacity, etc. </p> <p>There are two types of item group feed files generated: <ul> <li>A daily <b>Item Group</b> feed file containing the item group variation information associated with items returned in the <a href=\"/api-docs/buy/feed/resources/item/methods/getItemFeed\">Item</a> feed file for a specific day, category, and marketplace. (<b>feed_scope</b> = <code>NEWLY_LISTED</code>)</li>  <li>A weekly <b>Item Group Bootstrap</b> feed file containing all the item group variation information associated with items returned in the <a href=\"/api-docs/buy/feed/resources/item/methods/getItemFeed\">Item Bootstrap</a> feed file for all the items in a specific category.  (<b>feed_scope</b> = <code>ALL_ACTIVE</code>)</li>  </ul></p>  <p><span class=\"tablenote\"><b>Note: </b>  Filters are applied to the feed files. For details, see <a href=\"/api-docs/buy/static/api-feed.html#feed-filters\">Feed File Filters</a>.  When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future.</span></p>    <p>The contents of these feed files are based on the contents of the corresponding daily <b> Item</b> or <b>Item Bootstrap</b> feed file. When a new <b> Item</b> or <b>Item Bootstrap</b> feed file is generated, the service reads the file and if an item in the file has a <b> primaryItemGroupId</b> value, which indicates the item is part of an item group, it uses that value to return the item group (parent item) information for that item in the corresponding <b> Item Group</b> or <b> Item Group Bootstrap</b> feed file.</p>  <p>  This information includes the  name/value pair of the aspects of the items in this group returned in the <b> variesByLocalizedAspects </b> column. For example, if the item was a shirt some of the variation names could be Size, Color, etc. Also the images for the various aspects are returned in the <b>additionalImageUrls</b> column.</p>              <p>The first line in any feed file is the header, which labels the columns and indicates the order of the values on each line.  Each header is described in the <a href=\"/api-docs/buy/feed/resources/item_group/methods/getItemGroupFeed#h3-response-fields\">Response fields</a> section.</p>                                  <h3><b>Combining the Item Group and Item feed files</b></h3>              <p>The <b> Item Group</b> or <b> Item Group Bootstrap</b> feed file contains details about the item group (parent item), including the item group ID <b> itemGroupId</b>.  You match the value of <b> itemGroupId</b> from the <b> Item Group</b> feed file with the value of <b> primaryItemGroupId</b> from the corresponding daily <b> Item</b> or <b>Item Bootstrap</b> feed file.           </p>      <h3><b>URLs for this method</b></h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/feed/v1_beta/item_group?</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/feed/v1_beta/item_group?</code></li>           </ul>  </p>      <h3><b>Downloading feed files </b></h3>                          <p>Item Group feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the <a href=\"#range-header\">Range</a> request header. The <a href=\"#content-range\">content-range</a> response header indicates where in the full resource this partial chunk of data belongs  and the total number of bytes in the file.       For more information about using these headers, see <a href=\"/api-docs/{swift-folder}/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>. </p>                 <p><span class=\"tablenote\">  <b> Note:</b>  A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.</span>          </p>                        <h3><b>Restrictions </b></h3>                        <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/{swift-folder}/buy/feed/overview.html#API\">API Restrictions</a>.  </p>  # noqa: E501

        :param str accept: The formats that the client accepts for the response.<br /><br />A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate error codes that are returned in JSON format.<br /><br /><b>Default:</b> <code>application/json,text/tab-separated-values</code> (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. <b>Note: </b> This value is case sensitive.<br /><br />For example: <br />&nbsp;&nbsp;<code>X-EBAY-C-MARKETPLACE-ID = EBAY_US</code>  <br /><br /> For a list of supported sites see, <a href=\"/api-docs/buy/feed/overview.html#API\">API Restrictions</a>. (required)
        :param str feed_scope: Specifies the type of file to return. <br /><br /><b>Valid Values: </b>   <ul> <li><b> NEWLY_LISTED</b> - Returns the <b>Item Group</b> feed file containing the  item group variation information for items in the daily <a href=\"/api-docs/buy/feed/resources/item/methods/getItemFeed\">Item</a> feed file that were associated with an item group. <br /><br />The items in this type of <b>Item</b> feed file are items that were listed on the day specified by the <b> date</b> parameter in the category specified by the <b> category_id</b> parameter. <br /><br /><code>/item_group?feed_scope=NEWLY_LISTED&category_id=15032&date=20170925</code></li> <li><b>ALL_ACTIVE</b> - Returns the weekly <b>Item Group Bootstrap</b> file containing the item group  variation information for items in the weekly <a href=\"/api-docs/buy/feed/resources/item/methods/getItemFeed\">Item Bootstrap</a> feed file that were associated with an item group. The items are Good 'Til Cancelled items in the category specified by the <b> category_id</b> parameter.  <br /><br />  <span class=\"tablenote\"><b>Note: </b> Bootstrap files are generated every Tuesday and the file is available on Wednesday. However, the exact time the file is available can vary so we recommend you download the Bootstrap file on Thursday. The item groups in the file are for the items that were in the specified category on Sunday.</span><br /><br /><code>/item_group?feed_scope=ALL_ACTIVE&category_id=15032</code> <br /><br />  (required)
        :param str category_id: An eBay top-level category ID of the items to be returned in the feed file. <br /> <br />The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplaces, you can use the Taxonomy API <a href=\"/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategoryTree\">getCategoryTree</a> method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the <b> categoryTreeNodeLevel </b> field. <br /><br /><b>For example: </b><br />&nbsp;&nbsp;<code>\"categoryTreeNodeLevel\": 1</code> <br /><br />For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  </ul> <br /><br />   <b>Restriction: </b> Must be a top-level category </b> (required)
        :param str range: <a name=\"range-header\"></a>This header specifies the range in bytes of the chunks of the gzip file being returned. <br /><br /><b> Format:</b> <code>bytes=<em>startpos</em>-<em>endpos</em></code><br /><br />  For example, the following retrieves the first 10 MBs of the feed file. <br /><br />&nbsp;&nbsp;<code>Range bytes=0-10485760</code> <br /><br />For more information about using this header, see <a href=\"/api-docs/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>. <br /><br /><b>Maximum:</b> 100 MB (10MB in the Sandbox)
        :param str _date:  The date of the daily <b>Item Group</b> feed file (<b>feed_scope</b>=<code>NEWLY_LISTED</code>) you want. <p>The <b> date</b> is required only for the daily <b>Item Group</b> feed file. If you specify a date for the <b>Item Group Bootstrap</b> file (<b>feed_scope</b>=<code>ALL_ACTIVE</code>), the date is ignored and the latest file is returned. The date the <b>Item Group Bootstrap</b> feed file was generated is returned in the <b>Last-Modified</b> response header.</code></p>    <p>The <b> Item Group</b> feed files are generated every day and there are 14 daily files available.</p> <p>There is a 48 hour latency when generating the files. This means on July 10, the latest feed file you can download is July 8.</p>  <span class=\"tablenote\"><b>Note: </b> The generated files are stored using MST (US Mountain Standard Time), which is -7 hours UTC time.</span><br /> <br /><b> Format: </b><code>yyyyMMdd</code><br /><br /><b> Requirement: Requirements: </b> <ul>  <li>Required only when <b>feed_scope</b>=<code>NEWLY_LISTED</code> </li>   <li>Must be within 3-14 days in the past</li>    </ul>  
        :return: ItemGroupResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemGroupApi, buy_feed.ApiClient, 'get_item_group_feed', BuyFeedException, False, ['buy.feed', 'item_group'], (accept, x_ebay_c_marketplace_id, feed_scope, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_priority_feed(self, accept, x_ebay_c_marketplace_id, range, category_id, _date, **kwargs):  # noqa: E501
        """get_item_priority_feed  # noqa: E501

        <p>Using this method, you can download a TSV_GZIP (tab separated value gzip) <b>Item Priority</b> feed file, which allows you to track changes (deltas) in the status of your priority items, such as when an item is added or removed from a campaign.  The delta feed tracks the changes to the status of items within a category you specify in the input URI. You can also specify a specific date for the feed you want returned.</p><p><span class=\"tablenote\"><span style=\"color:#FF0000\"> <b> Important:</b> </span> You must consume the daily feeds (<b>Item</b>, <b>Item Group</b>) before consuming the <b>Item Priority</b> feed. This ensures that your inventory is up to date.</span></p>                                   <h3><b>URLs for this method</b></h3>   <p><ul>    <li><b> Production URL: </b> <code>https://api.ebay.com/buy/feed/v1_beta/item_priority?</code></li>    <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/feed/v1_beta/item_priority?</code></li>   </ul> </p>              <h3><b>Downloading feed files </b></h3>             <p><span class=\"tablenote\"><b>Note: </b> Filters are applied to the feed files. For details, see <a href=\"/api-docs/buy/static/api-feed.html#feed-filters\">Feed File Filters</a>. When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future.</span></p><p>Priority Item feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the <a href=\"#range-header\">Range</a> request header. The <a href=\"#content-range\">Content-range</a> response header indicates where in the full resource this partial chunk of data belongs  and the total number of bytes in the file.       For more information about using these headers, see <a href=\"/api-docs/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>.    </p>    <p>In addition to the API, there is an open source <a href=\"https://github.com/eBay/FeedSDK\" target=\"_blank\">Feed SDK</a> written in Java that downloads, combines files into a single file when needed, and unzips the entire feed file. It also lets you specify field filters to curate the items in the file.</p>              <p><span class=\"tablenote\">  <b> Note:</b>  A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.</span>  </p>                <h3><b>Restrictions </b></h3>                <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/feed/overview.html#API\">API Restrictions</a>.</p>  # noqa: E501

        :param str accept: The formats that the client accepts for the response.<br /><br />A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate error codes that are returned in JSON format.<br /><br /><b>Default:</b> <code>application/json,text/tab-separated-values</code> (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. <b>Note: </b> This value is case sensitive.<br /><br />For example: <br />&nbsp;&nbsp;<code>X-EBAY-C-MARKETPLACE-ID = EBAY_US</code>  <br /><br /> For a list of supported sites see, <a href=\"/api-docs/buy/static/ref-marketplace-supported.html\">Buy API Support by Marketplace</a>. (required)
        :param str range: Header specifying content range to be retrieved. Only supported range is bytes.<br /> <br /><b>Example</b> : <code>bytes = 0-102400</code>. (required)
        :param str category_id: An eBay top-level category ID of the items to be returned in the feed file. <br /> <br />The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplaces, you can use the Taxonomy API <a href=\"/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategoryTree\">getCategoryTree</a> method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the <b> categoryTreeNodeLevel </b> field. <br /><br /><b>For example: </b><br />&nbsp;&nbsp;<code>\"categoryTreeNodeLevel\": 1</code> <br /><br />For details see <a href=\"/api-docs/buy/api-feed.html#Getcat\">Get the eBay categories of a marketplace</a>. </li>  </ul> <br /><br />   <b>Restriction: </b> Must be a top-level category (required)
        :param str _date: The date of the feed you want returned. This can be up to 14 days in the past but cannot be set to a date in the future.<br /> <br /><b>Format:</b> <code>yyyyMMdd</code><br ><br /><span class=\"tablenote\"> <b>Note: </b><ul>  <li>The daily <b>Item</b> feed files are available each day after 9AM MST (US Mountain Standard Time), which is -7 hours UTC time.</li>    <li>There is a 48 hour latency when generating the <b> Item</b> feed files. This means you can download the file for July 10th on July 12 after 9AM MST. <br /><br /><b>Note: </b> For categories with a large number of items, the latency can be up to 72 hours.</li> </ul></span> (required)
        :return: ItemPriorityResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemPriorityApi, buy_feed.ApiClient, 'get_item_priority_feed', BuyFeedException, False, ['buy.feed', 'item_priority'], (accept, x_ebay_c_marketplace_id, range, category_id, _date), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_snapshot_feed(self, accept, x_ebay_c_marketplace_id, range, category_id, snapshot_date, **kwargs):  # noqa: E501
        """get_item_snapshot_feed  # noqa: E501

         <p>The <b> Hourly Snapshot</b> feed file is generated each hour every day for most categories. This method lets you download an <b> Hourly Snapshot</b> TSV_GZIP (tab-separated value gzip) feed file containing the details of all the items that have <a href=\"/api-docs/buy/static/api-feed.html#changed-items\">changed</a> <i> within</i> the specified day and hour for a specific category.  This means to generate the 8AM file of items that have changed from 8AM and 8:59AM, the service starts at 9AM. You can retrieve the 8AM snapshot file at 10AM.</p>    <p>Snapshot feeds now include new listings. You can check <a href=\"/api-docs/buy/feed/resources/item_snapshot/methods/getItemSnapshotFeed#response.items.itemCreationDate\">itemCreationDate</a> to identify listings that were newly created within the specified hour.</p>     <p><span class=\"tablenote\"><b>Note: </b>  Filters are applied to the feed files. For details, see <a href=\"/api-docs/buy/static/api-feed.html#feed-filters\">Feed File Filters</a>.  When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future.</span></p>                  <p>You can use the response from this method to update the item details of items stored in your database. By looking at the value of <a href=\"/api-docs/buy/feed/resources/item_snapshot/methods/getItemSnapshotFeed#response.items.itemSnapshotDate\">itemSnapshotDate</a> for a given item, you will be able to tell which information is the latest.</p>   <p><span class=\"tablenote\"><span style=\"color:#FF0000\"> <b> Important:</b> </span> When the value of the <b> availability</b> column is <code>UNAVAILABLE</code>, only the <b>itemId</b> and <b> availability</b> columns are populated. </span>  </p>                    <h3><b>URLs for this method</b></h3>          <p><ul>           <li><b> Production URL: </b> <code>https://api.ebay.com/buy/feed/v1_beta/item_snapshot?</code></li>           <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/feed/v1_beta/item_snapshot?</code></li>          </ul>   </p>                                 <h3><b>Downloading feed files </b></h3>                         <p>Hourly snapshot feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the <a href=\"#range-header\">Range</a> request header. The <a href=\"#content-range\">Content-range</a> response header indicates where in the full resource this partial chunk of data belongs and the total number of bytes in the file.       For more information about using these headers, see <a href=\"/api-docs/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>.  </p>                                <p><span class=\"tablenote\">  <b> Note:</b> A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.</span></p>                               <h3><b>Restrictions </b></h3>            <p>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/feed/overview.html#API\">API Restrictions</a>.</p>    # noqa: E501

        :param str accept: The formats that the client accepts for the response.<br /><br />A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate error codes that are returned in JSON format.<br /><br /><b>Default:</b> <code>application/json,text/tab-separated-values</code> (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. <b>Note: </b> This value is case sensitive.<br /><br />For example: <br />&nbsp;&nbsp;<code>X-EBAY-C-MARKETPLACE-ID = EBAY_US</code>  <br /><br /> For a list of supported sites see, <a href=\"/api-docs/buy/feed/overview.html#API\">API Restrictions</a>. (required)
        :param str range: <a name=\"range-header\"></a>This header specifies the range in bytes of the chunks of the gzip file being returned. <br /><br /><b> Format:</b> <code>bytes=<em>startpos</em>-<em>endpos</em></code><br /><br />  For example, the following retrieves the first 10 MBs of the feed file. <br /><br />&nbsp;&nbsp;<code>Range bytes=0-10485760</code> <br /><br />For more information about using this header, see <a href=\"/api-docs/buy/static/api-feed.html#retrv-gzip\">Retrieving a gzip feed file</a>. <br /><br /><b>Maximum:</b> 100 MB (10MB in the Sandbox) (required)
        :param str category_id: An eBay top-level category ID  of the items to be returned in the feed file. <br /> <br />The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplace, you can use the Taxonomy API <a href=\"/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategoryTree\">getCategoryTree</a> method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the <b> categoryTreeNodeLevel </b> field. <br /><br /><b>For example: </b><br />&nbsp;&nbsp;<code>\"categoryTreeNodeLevel\": 1</code> <br /><br />For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  </ul> <br /><br />   <b>Restriction: </b> Must be a top-level category </b> (required)
        :param str snapshot_date: The date and hour of the snapshot feed file you want. Each file contains the items that changed within the hour in the specified category. So, the 9AM file contains the items that changed between 9AM and 9:59AM on the day specified.  It takes 2 hours to generate a snapshot file, which means to get the file for 9AM the earliest you could submit the call is at 11AM.<br /><br />There are 7 days of <b> Hourly Snapshot</b> feed files available.      <p><span class=\"tablenote\"><b>Note: </b> The Feed API uses GMT, so you must convert your local time to GMT. For example, if you lived in California and wanted the September 15th 7pm file, you would submit the following call: <br /> <br /><code>item_snapshot?category_id=625&snapshot_date=2017-09-16T02:00:00.000Z</code> </span></p>  <b>Format: </b>UTC format (yyyy-MM-ddThh:00:00.000Z) <br /><br />Files are generated on the hour, so minutes and seconds are <em> always</em> zeros. (required)
        :return: ItemSnapshotResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemSnapshotApi, buy_feed.ApiClient, 'get_item_snapshot_feed', BuyFeedException, False, ['buy.feed', 'item_snapshot'], (accept, x_ebay_c_marketplace_id, range, category_id, snapshot_date), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_marketing_get_merchandised_products(self, category_id, metric_name, **kwargs):  # noqa: E501
        """get_merchandised_products  # noqa: E501

        This method returns an array of products based on the category and metric specified. This includes details of the product, such as the eBay product ID (EPID), title, and user reviews and ratings for the product. You can use the <code>epid</code> returned by this method in the Browse API <b>search</b> method to retrieve items for this product. <h3><b>Restrictions </b></h3> <ul><li>To test <b> getMerchandisedProducts</b> in Sandbox, you must use category ID 9355 and the response will be mock data.  </li>   <li>For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/marketing/overview.html#API\">API Restrictions</a>.</li>  </ul>  # noqa: E501

        :param str category_id: This query parameter limits the products returned to a specific eBay category.  <br /> <br />The list of eBay category IDs is not published and category IDs are not all the same across all the eBay marketplace. You can use the following techniques to find a category by site: <ul> <li>Use the <a href=\"https://pages.ebay.com/sellerinformation/news/categorychanges.html\" target=\"_blank\">Category Changes page</a>.</li> <li>Use the Taxonomy API. For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  <li>Use the Browse API and submit the following method to get the <b> dominantCategoryId</b> for an item. <br /><code>/buy/browse/v1/item_summary/search?q=<em>keyword</em>&fieldgroups=ASPECT_REFINEMENTS  </code></li></ul>  <b> Maximum: </b> 1 <br /> <b> Required: </b> 1  (required)
        :param str metric_name: This value filters the result set by the specified metric. Only products in this metric are returned. Currently, the only metric supported is <code> BEST_SELLING</code>. <br /><br /><b> Default: </b>BEST_SELLING <br /> <b> Maximum: </b> 1 <br /> <b> Required: </b> 1 (required)
        :param str aspect_filter: The aspect name/value pairs used to further refine product results. <br /><br /> For example: <br />&nbsp;&nbsp;&nbsp;<code>/buy/marketing/v1_beta/merchandised_product?category_id=31388&metric_name=BEST_SELLING&aspect_filter=Brand:Canon</code>  <br /><br />You can use the Browse API <b>search</b> method with the <code>fieldgroups=ASPECT_REFINEMENTS</code> field to return the aspects of a product. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketing/types/gct:MarketingAspectFilter
        :param str limit: This value specifies the maximum number of products to return in a result set. <br /> <br /><span class=\"tablenote\"> <b>Note:</b> Maximum value means the method will return up <em>to</em> that many products per set, but it can be less than this value. If the number of products found is less than this value, the method will return all of the products matching the criteria.</span>  <br /><br /><b> Default:</b> 8<br /><b> Maximum: </b>100
        :return: BestSellingProductResponse
        """
        try:
            return self._method_single(buy_marketing.Configuration, '/buy/marketing/v1_beta', buy_marketing.MerchandisedProductApi, buy_marketing.ApiClient, 'get_merchandised_products', BuyMarketingException, False, ['buy.marketing', 'merchandised_product'], (category_id, metric_name), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_marketplace_insights_search(self, **kwargs):  # noqa: E501
        """search  # noqa: E501

        <a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a>   <p>This method searches for sold eBay items by various URI query parameters and retrieves the sales history of the items for the last 90 days. You can search by keyword, category, eBay product ID (ePID), or GTIN, or a combination of these.    </p>      <p>This method also supports the following:  <ul> <li>Filtering by the value of one or multiple fields, such as listing format, item condition, price range, location, and more.  For the fields supported by this method, see the <a href=\"#uri.filter\">filter</a> parameter.</li> <li>Retrieving the refinements (metadata) of an item , such as item aspects (color, brand), condition, category, etc. using the <a href=\"#uri.fieldgroups\">fieldgroups</a> parameter. </li>  <li>Filtering by item aspects and other refinements using the <a href=\"#uri.aspect_filter\">aspect_filter</a> parameter. </li> <li>Creating aspects histograms, which enables shoppers to drill down in each refinement narrowing the search results.  </li>  </ul></p>  <p>For details and examples of these capabilities, see <a href=\"/api-docs/buy/static/api-browse.html\">Browse API</a> in the Buying Integration Guide.</p>     <h3><b>Pagination and sort controls</b></h3><p>There are pagination controls (<b>limit</b> and <b>offset</b> fields) and <b> sort</b> query parameters that  control/sort the data that is returned. By default, the results are sorted by &quot;Best Match&quot;. For more information about  Best Match, see the eBay help page <a href=\"https://pages.ebay.com/help/sell/searchstanding.html\" target=\"_blank\">Best Match</a>.  </p>                             <h3><b>URLs for this method</b></h3>           <p><ul>            <li><b> Production URL: </b> <code>https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search?</code></li>            <li><b> Sandbox URL:  </b><code>https://api.sandbox.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search?</code></li>           </ul>    </p>     <h3><b> Request headers</b></h3> <p>You will want to use the <b> X-EBAY-C-ENDUSERCTX</b> request header with this method. If you are an <b>eBay Network Partner</b> you <b> must</b> use <code>affiliateCampaignId=<em>ePNCampaignId</em>,affiliateReferenceId=<em>referenceId</em></code> in the header in order to be paid for selling eBay items on your site . For details see, <a href=\"/api-docs/buy/static/api-browse.html#Headers\">Request headers</a> in the <em> Buy APIs Overview</em>.</p>   <h3><b>URL Encoding for Parameters</b></h3>            <p>Query parameter values need to be URL encoded. For details, see <a href=\"/api-docs/static/rest-request-components.html#parameters\">URL encoding query parameter values</a>.</p>            <h3><b>Restrictions </b></h3> <p> For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/marketplace-insights/overview.html#API\">API Restrictions</a>.</p>   # noqa: E501

        :param str aspect_filter: This field lets you filter by item aspects. The aspect name/value pairs and category, which is required, is used to limit the results to specific aspects of the item. For example, in a clothing category one aspect pair would be Color/Red. The results are returned in the <b>refinement</b> container.   <br /><br />For example, the method below uses the category ID for Women's Clothing. This will return only sold items for a woman's red or blue shirt.   <br /><br /><code>/buy/marketplace_insights/v1_beta/item_sales/search?q=shirt&category_ids=15724&aspect_filter=categoryId:15724,Color:{Red|Blue}</code> <br /><br />To get a list of the aspects pairs and the category, which is returned in the <b> dominantCategoryId</b> field, set <b> fieldgroups</b> to <code>ASPECT_REFINEMENTS</code>.   <br /><br /> <code>/buy/marketplace_insights/v1_beta/item_sales/search?q=shirt&category_ids=15724&fieldgroups=ASPECT_REFINEMENTS</code>  <br /><br /><b>Format: </b> <code><i>aspectName</i>:{<i>value1</i>|<i>value2</i>}</code>    <br /><br /><b>Required: </b> The category ID is required <i>twice</i>; once as a URI parameter and as part of the <b> aspect_filter</b> parameter. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketplace_insights/types/gct:AspectFilter
        :param str category_ids: The category ID is required and is used to limit the results. For example, if you search for 'shirt' the result set will be very large. But if you also include the category ID <code>137084</code>, the results will be limited to 'Men's Athletic Apparel'. For example: <br /><br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?q=shirt&category_ids=137084</code>                <p>The list of eBay category IDs is not published and category IDs are not the same across all the eBay marketplaces. You can use the following techniques to find a category by site: </p>     <ul> <li>For the US marketplace, use the <a href=\"https://pages.ebay.com/sellerinformation/news/categorychanges.html\" target=\"_blank\">Category Changes page</a>.</li> <li>Use the Taxonomy API. For details see <a href=\"/api-docs/buy/buy-categories.html\">Get Categories for Buy APIs</a>. </li>  </ul>  <b> Usage:</b>  <ul><li>This field can have one category ID or a comma separated list of IDs.</li>    <li>You can use <b>category_ids</b> by itself or use it with any combination of the <b> gtin</b>, <b> epid</b>, and <b> q</b> fields, which gives you additional control over the result set.</li> </ul> <b>Restrictions: </b> <ul>  <li>Partners will be given a list of categories they can use.  </li>  <li>To use a top-level (L1) category, you <b> must</b> also include the <b> q</b>, or <b> gtin</b>, or <b> epid</b>  query parameter.  </li>  </ul> <b>Maximum number of categories:</b> 4
        :param str epid: The ePID is the eBay product identifier of a product from the eBay product catalog. This field limits the results to only items in the specified ePID. <br /><br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?epid=241986085&category_ids=168058</code>  <br /><br />You can use the <a href=\"/api-docs/commerce/catalog/resources/product_summary/methods/search\">product_summary/search</a> method in the <b>Catalog</b> API to search for the ePID of the product.   <br /><br /><b> Required: </b> At least 1 <b> category_ids</b>  <br /><b> Maximum: </b> 1 <b>epid</b>    <br /><b>Optional: </b>Any combination of <b> epid</b>,  <b> gtin</b>,  or <b> q</b>
        :param str fieldgroups: This field lets you control what is to be returned in the response and accepts a comma separated list of values. <br /><br />The default is <b> MATCHING_ITEMS</b>, which returns the items that match the keyword or category specified. The other values return data that can be used to create histograms. For code examples see, <a href=\"#request.aspect_filter\">aspect_filter</a>. <br /><br /><b> Valid Values: </b> <ul>    <li><b> ASPECT_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.aspectDistributions\">aspectDistributions</a> container, which has the <b> dominantCategoryId</b>, <b> matchCount</b>, and <b> refinementHref</b> for the various aspects of the items found. For example, if you searched for 'Mustang', some of the aspect would be <b> Model Year</b>,  <b> Exterior Color</b>, <b> Vehicle Mileage</b>, etc. <br /> <br /><span class=\"tablenote\"> <b>Note: </b> ASPECT_REFINEMENTS are category specific.</span> <br /><br /></li>   <li><b> BUYING_OPTION_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.buyingOptionDistributions\">buyingOptionDistributions</a>  container, which has the <b> matchCount</b> and <b> refinementHref</b> for <b> AUCTION</b> and <b> FIXED_PRICE</b> (Buy It Now) items. <br /><br /><span class=\"tablenote\"> <b>Note: </b>Classified items are not supported. </span> <br /><br /> </li>   <li><b> CATEGORY_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.categoryDistributions\">categoryDistributions</a> container, which has the categories that the item is in.   </li>   <li><b> CONDITION_REFINEMENTS</b> - This returns the <a href=\"#response.refinement.conditionDistributions\">conditionDistributions</a>  container, such as <b> NEW</b>, <b> USED</b>, etc. Within these groups are multiple states of the condition. For example, <b> New </b> can be New without tag, New in box, New without box, etc. </li>   <li><b> MATCHING_ITEMS</b> - This is meant to be used with one or more of the refinement values above. You use this to return the specified refinements and all the matching items. </li> <li><b> FULL </b> - This returns all the refinement containers and all the matching items.</li>   </ul> Code so that your app gracefully handles any future changes to this list.  <br /><br /><b>Default: </b> MATCHING_ITEMS  
        :param str filter: This field supports multiple field filters that can be used to limit/customize the result set. <br /><br />The following lists the supported filters. For details and examples for all the filters, see <a href=\"/api-docs/buy/static/ref-buy-browse-filters.html\">Buy API Field Filters</a>.  <table> <tr> <td><ul>     <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#buyingOptions\">buyingOptions</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#conditionIds\">conditionIds</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#conditions\">conditions</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#itemLocationCountry\">itemLocationCountry</a> </li> </ul> </td>      <td> <ul><li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#lastSoldDate\">lastSoldDate</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#price\">price</a> </li>    <li><a href=\"/api-docs/buy/static/ref-buy-browse-filters.html#priceCurrency\">priceCurrency</a> </li>  </ul></td>  </tr> </table> <br />The following example filters the result set by price. <b>Note: </b>To filter by price, <b>price</b> and <b>priceCurrency</b> must always be used together.   <br /><br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?q=iphone&category_ids=15724&filter=price:[50..500],priceCurrency:USD</code> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketplace_insights/types/cos:FilterField
        :param str gtin: This field lets you search by the Global Trade Item Number of the item as defined by <a href=\"https://www.gtin.info\" target=\"_blank\">https://www.gtin.info</a>. This can be a UPC (Universal Product Code), EAN (European Article Number), or an ISBN (International Standard Book Number) value.        <br /><br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?gtin=241986085&category_ids=9355</code> <br /><br /><b> Required: </b> At least 1 <b> category_ids</b>  <br /><b> Maximum: </b> 1 <b>gtin</b>    <br /><b>Optional: </b>Any combination of <b> epid</b>,  <b> gtin</b>,  or <b> q</b>
        :param str limit: The number of items, from the result set, returned in a single page.  <br /><br /><b> Default:</b> 50<br /><b> Maximum number of items per page (limit): </b>200  <br /> <b> Maximum number of items in a result set: </b> 10,000
        :param str offset: Specifies the number of items to skip in the result set. This is used with the <b> limit</b> field to control the pagination of the output.  <br /><br />If <b> offset</b> is 0 and <b> limit</b> is 10, the method will retrieve items 1-10 from the list of items returned, if <b> offset</b> is 10 and <b> limit</b> is 10, the method will retrieve items 11 thru 20 from the list of items returned.  <br /><br /><b> Valid Values</b>: 0-10,000 (inclusive) <br /> <b> Default:</b> 0 <br /> <b> Maximum number of items returned: </b> 10,000
        :param str q: A string consisting of one or more keywords that are used to search for items on eBay. The keywords are handled as follows: <ul><li>If the keywords are separated by a comma, it is treated as an AND. In the following example, the query returns items that have iphone <b> AND</b> ipad.<br /><br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?q=iphone,ipad&category_ids=15724</code>  <br/> </li>  <li> If the keywords are separated by a space, it is treated as an OR.  In the following examples, the query returns items that have iphone <b> OR</b> ipad.   <br /><br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?q=iphone&category_ids=15724&nbsp;ipad</code> <br /><code>/buy/marketplace-insights/v1_beta/item_sales/search?q=iphone,&nbsp;ipad&category_ids=15724</code> <br />   </li></ul> <b> Restriction: </b>The <code>*</code> wildcard character is <b> not</b> allowed in this field. <br /><br /><b> Required: </b> At least 1 <b> category_ids</b>  <br /><b>Optional: </b>Any combination of <b> epid</b>,  <b> gtin</b>,  or <b> q</b>     
        :param str sort: This field specifies the order and the field name to use to sort the items. To sort in descending order use <code>-</code> before the field name.  Currently, you can only sort by price (in ascending or descending order).     <br /><br />If no sort parameter is submitted, the result set is sorted by  &quot;<a href=\"https://pages.ebay.com/help/sell/searchstanding.html\" target=\"_blank\">Best Match</a>&quot;.     <br /><br />The following are examples of using the <b> sort</b> query parameter.    <br /><br /><table><tr><th>Sort</th><th>Result</th></tr><tr><td><code>&sort=price</code></td><td> Sorts by <b> price</b> in ascending order (lowest price first)</td></tr><tr><td><code>&sort=-price</code></td><td> Sorts by <b> price</b> in descending order (highest price first)</td></tr></table><br /><b> Default: </b> ascending For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketplace_insights/types/cos:SortField
        :return: SalesHistoryPagedCollection
        """
        try:
            return self._method_paged(buy_marketplace_insights.Configuration, '/buy/marketplace_insights/v1_beta', buy_marketplace_insights.ItemSalesApi, buy_marketplace_insights.ApiClient, 'search', BuyMarketplaceInsightsException, False, ['buy.marketplace.insights', 'item_sales'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_offer_get_bidding(self, item_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_bidding  # noqa: E501

        This method retrieves the bidding details that are specific to the buyer of the specified auction. This must be an auction where the buyer has already placed a bid. To retrieve the bidding information you use a user access token and pass in the item ID of the auction. You can also retrieve general bidding details about the auction, such as minimum bid price and the count of unique bidders, using the Browse API getItem method. URLs for this method Production URL: https://api.ebay.com/buy/offer/v1_beta/bidding/{item_id} Sandbox URL: https://api.sandbox.ebay.com/buy/offer/v1_beta/bidding/{item_id} Restrictions For a list of supported sites and other restrictions, see API Restrictions.  # noqa: E501

        :param str item_id: The eBay RESTful identifier of an item that you want the buyer's bidding information. This ID is returned by the Browse and Feed API methods. RESTful Item ID example: v1|2**********2|0 For more information about item ID for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview. Restriction: The buyer must have placed a bid for this item. (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the buyer is based. Note: This value is case sensitive. For example: &nbsp;&nbsp;X-EBAY-C-MARKETPLACE-ID = EBAY_US For a list of supported sites see, API Restrictions. (required)
        :return: Bidding
        """
        try:
            return self._method_single(buy_offer.Configuration, '/buy/offer/v1_beta', buy_offer.BiddingApi, buy_offer.ApiClient, 'get_bidding', BuyOfferException, True, ['buy.offer', 'bidding'], (item_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_offer_place_proxy_bid(self, x_ebay_c_marketplace_id, item_id, **kwargs):  # noqa: E501
        """place_proxy_bid  # noqa: E501

        This method uses a user access token to place a proxy bid for the buyer on a specific auction item. The item must offer AUCTION as one of the buyingOptions. To place a bid, you pass in the item ID of the auction as a URI parameter and the buyer's maximum bid amount (maxAmount ) in the payload. By placing a proxy bid, the buyer is agreeing to purchase the item if they win the auction. After this bid is placed, if someone else outbids the buyer a bid, eBay automatically bids again for the buyer up to the amount of their maximum bid. When the bid exceeds the buyer's maximum bid, eBay will notify them that they have been outbid. To find auctions, you can use the Browse API to search for items and use a filter to return only auction items. For example: /buy/browse/v1/item_summary/search?q=iphone&amp;filter=buyingOptions:{AUCTION} URLs for this method Production URL: https://api.ebay.com/buy/offer/v1_beta/bidding/{item_id}/place_proxy_bid Sandbox URL: https://api.sandbox.ebay.com/buy/offer/v1_beta/bidding/{item_id}/place_proxy_bid Restrictions For a list of supported sites and other restrictions, see API Restrictions.  # noqa: E501

        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the buyer is based. Note: This value is case sensitive. For example: &nbsp;&nbsp;X-EBAY-C-MARKETPLACE-ID = EBAY_US For a list of supported sites see, API Restrictions. (required)
        :param str item_id: The eBay RESTful identifier of an item you want to bid on. This ID is returned by the Browse and Feed API methods. RESTful Item ID Example: v1|2**********2|0 For more information about item ID for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview. (required)
        :param PlaceProxyBidRequest body:
        :return: PlaceProxyBidResponse
        """
        try:
            return self._method_single(buy_offer.Configuration, '/buy/offer/v1_beta', buy_offer.BiddingApi, buy_offer.ApiClient, 'place_proxy_bid', BuyOfferException, True, ['buy.offer', 'bidding'], (x_ebay_c_marketplace_id, item_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_apply_guest_coupon(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """apply_guest_coupon  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method adds a coupon to an eBay guest checkout session and applies it to all the eligible items in the order.<br /><br />The <b>checkoutSessionId</b> is passed in as a URI parameter and is required. The redemption code of the coupon is in the payload and is also required.<br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/apply_coupon</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/apply_coupon</code></li></ul>  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the <b> initiateGuestCheckoutSession</b> method.<br /><br /><span class=\"tablenote\"><b>Note:</b> When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See <a href=\"/api-docs/buy/order/overview.html#checkout-restriction\">Checkout session restrictions</a> in the Buy Integration Guide for details.</span> (required)
        :param CouponRequest body: The container for the fields used to apply a coupon to a guest checkout session.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'apply_guest_coupon', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_get_guest_checkout_session(self, checkout_session_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_guest_checkout_session  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method returns the details of the specified guest checkout session. The <b>checkoutSessionId</b> is passed in as a URI parameter and is required. This method has no request payload.<br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}</code></li></ul>  # noqa: E501

        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the <b> initiateGuestCheckoutSession</b> method.<br /><br /><span class=\"tablenote\"><b>Note:</b> When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See <a href=\"/api-docs/buy/order/overview.html#checkout-restriction\">Checkout session restrictions</a> in the Buy Integration Guide for details.</span> (required)
        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'get_guest_checkout_session', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (checkout_session_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_initiate_guest_checkout_session(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """initiate_guest_checkout_session  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method creates an eBay guest checkout session, which is the first step in performing a checkout. The method returns a <b>checkoutSessionId</b> that you use as a URI parameter in subsequent guest checkout methods.<br /><br />Also see <a href=\"/api-docs/buy/static/ref-buy-negative-testing.html\">Negative Testing Using Stubs</a> for information on how to emulate error conditions for this  method using stubs.<br /><br /><span class=\"tablenote\"><font color=\"006600\"><b>TIP:</b></font> To test the entire checkout flow, you might need a \"test\" credit card. You can generate a credit card number from <a href=\"https://www.getcreditcardnumbers.com\" target=\"_blank\">https://www.getcreditcardnumbers.com</a>.</span><br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/initiate</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/initiate</code></li></ul>  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :param CreateGuestCheckoutSessionRequestV2 body: The container for the fields used by the <b>initiateGuestCheckoutSession</b> method.
        :param str x_ebay_c_enduserctx: A header that is used to specify the <b>affiliateCampaignId</b>, and optionally the <b>affiliateReferenceId</b>, to enable revenue sharing when the buyer purchases items.<br /><br /><span class=\"tablenote\"><font color=\"006600\"><b>TIP:</b></font> See <a href=\"/api-docs/buy/static/api-browse.html#Headers\" target=\"_blank\">Request headers</a> in the Buying Integration Guide for more information.</span>
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'initiate_guest_checkout_session', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_remove_guest_coupon(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """remove_guest_coupon  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method removes a coupon from an eBay guest checkout session. The <b>checkoutSessionId</b> is passed in as a URI parameter and is required. The redemption code of the coupon is specified in the payload and is also required.<br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/remove_coupon</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/remove_coupon</code></li></ul>  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the <b> initiateGuestCheckoutSession</b> method.<br /><br /><span class=\"tablenote\"><b>Note:</b> When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See <a href=\"/api-docs/buy/order/overview.html#checkout-restriction\">Checkout session restrictions</a> in the Buy Integration Guide for details.</span> (required)
        :param CouponRequest body: The container for the fields used by the <b>removeGuestCoupon</b> method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'remove_guest_coupon', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_update_guest_quantity(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """update_guest_quantity  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method changes the quantity of the specified line item in an eBay guest checkout session.<br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_quantity</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_quantity</code></li></ul>  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the <b> initiateGuestCheckoutSession</b> method.<br /><br /><span class=\"tablenote\"><b>Note:</b> When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See <a href=\"/api-docs/buy/order/overview.html#checkout-restriction\">Checkout session restrictions</a> in the Buy Integration Guide for details.</span> (required)
        :param UpdateQuantity body: The container for the fields used by the <b>updateGuestQuantity</b> method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'update_guest_quantity', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_update_guest_shipping_address(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """update_guest_shipping_address  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method changes the shipping address for the order in an eBay guest checkout session. All the line items in an order must be shipped to the same address, but the shipping method can be specific to the line item.<br /><br /><span class=\"tablenote\"><b>Note:</b> If the address submitted cannot be validated, a warning message will be returned. This does not prevent the method from executing, but you may want to verify the address.</span><br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_address</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_address</code></li></ul>  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the <b> initiateGuestCheckoutSession</b> method.<br /><br /><span class=\"tablenote\"><b>Note:</b> When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See <a href=\"/api-docs/buy/order/overview.html#checkout-restriction\">Checkout session restrictions</a> in the Buy Integration Guide for details.</span> (required)
        :param ShippingAddressImpl body: The container for the fields used by the <b>updateGuestShippingAddress</b> method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'update_guest_shipping_address', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_update_guest_shipping_option(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """update_guest_shipping_option  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method changes the shipping method for the specified line item in an eBay guest checkout session. The shipping option can be set for each line item. This gives the shopper the ability choose the cost of shipping for each line item.<br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL: </b> <code>https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_option</code></li><li><b>Sandbox URL:</b> <code>https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_option</code></li> </ul>  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.<br /><br /><span class=\"tablenote\"><b>Note:</b> This header does <i>not</i> indicate a language preference or consumer location.</span><br /><br />See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Marketplace ID values</a> for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the <b> initiateGuestCheckoutSession</b> method.<br /><br /><span class=\"tablenote\"><b>Note:</b> When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See <a href=\"/api-docs/buy/order/overview.html#checkout-restriction\">Checkout session restrictions</a> in the Buy Integration Guide for details.</span> (required)
        :param UpdateShippingOption body: The container for the fields used by the <b>updateGuestShippingOption</b> method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'update_guest_shipping_option', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_get_guest_purchase_order(self, purchase_order_id, **kwargs):  # noqa: E501
        """get_guest_purchase_order  # noqa: E501

        <span class=\"tablenote\"><b>Note:</b> This version of the Order API (v2) currently only supports the guest payment flow for eBay managed payments. To view the v1_beta version of the Order API, which includes both member and guest checkout payment flows, refer to the <a href=\"/api-docs/buy/order_v1/resources/methods\">Order_v1 API</a> documentation.</span><br /><br /><a href=\"https://developer.ebay.com/api-docs/static/versioning.html#limited\" target=\"_blank\"><img src=\"/cms/img/docs/partners-api.svg\" class=\"legend-icon partners-icon\"  alt=\"Limited Release\" title=\"Limited Release\" />(Limited Release)</a> This method is only available to select developers approved by business units.<br /><br />This method retrieves the details about a specific guest purchase order. It returns the line items, including purchase  order status, dates created and modified, item quantity and listing data, payment and shipping information, and prices, taxes, discounts and credits.<br /><br />The <b>purchaseOrderId</b> is passed in as a URI parameter and is required.<br /><br /><span class=\"tablenote\"><b>Note:</b> The <b>purchaseOrderId</b> value is returned in the call-back URL that is sent through the new eBay pay widget. For more information about eBay managed payments and the new Order API payment flow, see <a href=\"/api-docs/buy/static/api-order.html\">Order API</a> in the Buying Integration Guide.</span><br /><br />You can use this method to not only get the details of a purchase order, but to check the value of the <a href=\"#response.purchaseOrderPaymentStatus\">purchaseOrderPaymentStatus</a> field to determine if the order has been paid for. If the order has been paid for, this field will return <code>PAID</code>.<br /><br />For a list of supported sites and other restrictions, see <a href=\"/api-docs/buy/order/overview.html#API\">API Restrictions</a> in the Order API overview.<br /><br />The URLs for this method are:<ul><li><b>Production URL:</b> <code>https://api.ebay.com/buy/order/v2/guest_purchase_order/{purchaseOrderId}</code></li><li><b>Sandbox URL:</b> <code>https://api.sandbox.ebay.com/buy/order/v2/guest_purchase_order/{purchaseOrderId}</code></li></ul>  # noqa: E501

        :param str purchase_order_id: The unique identifier of a purchase order made by a guest buyer, for which details are to be retrieved.<br /><br /><span class=\"tablenote\"><b>Note:</b> This value is returned in the response URL that is sent through the new eBay pay widget. For more information about eBay managed payments and the new Order API payment flow, see <a href=\"/api-docs/buy/static/api-order.html\">Order API</a> in the Buying Integration Guide.</span> (required)
        :return: GuestPurchaseOrderV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestPurchaseOrderApi, buy_order.ApiClient, 'get_guest_purchase_order', BuyOrderException, False, ['buy.order', 'guest_purchase_order'], purchase_order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_catalog_get_product(self, epid, **kwargs):  # noqa: E501
        """get_product  # noqa: E501

        This call retrieves details of the catalog product identified by the eBay product identifier (ePID) specified in the request. These details include the product's title and description, aspects and their values, associated images, applicable category IDs, and any recognized identifiers that apply to the product. For a new listing, you can use the search call to identify candidate products on which to base the listing, then use the getProduct call to present the full details of those candidate products to the seller to make a a final selection.  # noqa: E501

        :param str epid: The ePID of the product being requested. This value can be discovered by issuing the search call and examining the value of the productSummaries.epid field for the desired returned product summary. (required)
        :return: Product
        """
        try:
            return self._method_single(commerce_catalog.Configuration, '/commerce/catalog/v1_beta', commerce_catalog.ProductApi, commerce_catalog.ApiClient, 'get_product', CommerceCatalogException, True, ['commerce.catalog', 'product'], epid, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_catalog_search(self, **kwargs):  # noqa: E501
        """search  # noqa: E501

        This call searches for and retrieves summaries of one or more products in the eBay catalog that match the search criteria provided by a seller. The seller can use the summaries to select the product in the eBay catalog that corresponds to the item that the seller wants to offer for sale. When a corresponding product is found and adopted by the seller, eBay will use the product information to populate the item listing. The criteria supported by search include keywords, product categories, and category aspects. To see the full details of a selected product, use the getProduct call. In addition to product summaries, this call can also be used to identify refinements, which help you to better pinpoint the product you're looking for. A refinement consists of one or more aspect values and a count of the number of times that each value has been used in previous eBay listings. An aspect is a property (e.g. color or size) of an eBay category, used by sellers to provide details about the items they're listing. The refinement container is returned when you include the fieldGroups query parameter in the request with a value of ASPECT_REFINEMENTS or FULL. Example A seller wants to find a product that is &quot;gray&quot; in color, but doesn't know what term the manufacturer uses for that color. It might be Silver, Brushed Nickel, Pewter, or even Grey. The returned refinement container identifies all aspects that have been used in past listings for products that match your search criteria, along with all of the values those aspects have taken, and the number of times each value was used. You can use this data to present the seller with a histogram of the values of each aspect. The seller can see which color values have been used in the past, and how frequently they have been used, and selects the most likely value or values for their product. You issue the search call again with those values in the aspect_filter parameter to narrow down the collection of products returned by the call. Although all query parameters are optional, this call must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value. If you provide more than one of these parameters, they will be combined with a logical AND to further refine the returned collection of matching products. Note: This call requires that certain special characters in the query parameters be percent-encoded: &nbsp;&nbsp;&nbsp;&nbsp;(space) = %20 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;, = %2C &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: = %3A &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ = %5B &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;] = %5D &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{ = %7B &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| = %7C &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;} = %7D This requirement applies to all query parameter values. However, for readability, call examples and samples in this documentation will not use the encoding. This call returns product summaries rather than the full details of the products. To retrieve the full details of a product, use the getProduct call with an ePID.  # noqa: E501

        :param str aspect_filter: An eBay category and one or more aspects of that category, with the values that can be used to narrow down the collection of products returned by this call. Aspects are product attributes that can represent different types of information for different products. Every product has aspects, but different products have different sets of aspects. You can determine appropriate values for the aspects by first submitting this call without this parameter. It will return either the productSummaries.aspects container, the refinement.aspectDistributions container, or both, depending on the value of the fieldgroups parameter in the request. The productSummaries.aspects container provides the category aspects and their values that are associated with each returned product. The refinement.aspectDistributions container provides information about the distribution of values of the set of category aspects associated with the specified categories. In both cases sellers can select from among the returned aspects to use with this parameter. Note: You can also use the Taxonomy API's getItemAspectsForCategory call to retrieve detailed information about aspects and their values that are appropriate for your selected category. The syntax for the aspect_filter parameter is as follows (on several lines for readability; categoryId is required): aspect_filter=categoryId:category_id, aspect1:{valueA|valueB|...}, aspect2:{valueC|valueD|...},... A matching product must be within the specified category, and it must have least one of the values identified for every specified aspect. Note: Aspect names and values are case sensitive. Here is an example of an aspect_filter parameter in which 9355 is the category ID, Color is an aspect of that category, and Black and White are possible values of that aspect (on several lines for readability): GET https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search? aspect_filter=categoryId:9355,Color:{White|Black} Here is the aspect_filter with required URL encoding and a second aspect (on several lines for readability): GET https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search? aspect_filter=categoryId:9355,Color:%7BWhite%7CBlack%7D, Storage%20Capacity:%128GB%7C256GB%7D Note: You cannot use the aspect_filter parameter in the same call with either the gtin parameter or the mpn parameter. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/commerce/catalog/types/catal:AspectFilter
        :param str category_ids: Important: Currently, only the first category_id value is accepted. One or more comma-separated category identifiers for narrowing down the collection of products returned by this call. Note: This parameter requires a valid category ID value. You can use the Taxonomy API's getCategorySuggestions call to retrieve appropriate category IDs for your product based on keywords. The syntax for this parameter is as follows: category_ids=category_id1,category_id2,... Here is an example of a call with the category_ids parameter: GET https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search? category_ids=178893 Note: Although all query parameters are optional, this call must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value. If you provide only the category_ids parameter, you cannot specify a top-level (L1) category.
        :param str fieldgroups: The type of information to return in the response. Important: This parameter may not produce valid results if you also provide more than one value for the category_ids parameter. It is recommended that you avoid using this combination. Valid Values: ASPECT_REFINEMENTS &mdash; This returns the refinement container, which includes the category aspect and aspect value distributions that apply to the returned products. For example, if you searched for Ford Mustang, some of the category aspects might be Model Year, Exterior Color, Vehicle Mileage, and so on. Note: Aspects are category specific. FULL &mdash; This returns all the refinement containers and all the matching products. This value overrides the other values, which will be ignored. MATCHING_PRODUCTS &mdash; This returns summaries for all products that match the values you provide for the q and category_ids parameters. This does not affect your use of the ASPECT_REFINEMENTS value, which you can use in the same call. Code so that your app gracefully handles any future changes to this list. Default: MATCHING_PRODUCTS
        :param str gtin: A string consisting of one or more comma-separated Global Trade Item Numbers (GTINs) that identify products to search for. Currently the GTIN values can include EAN, ISBN, and UPC identifier types. Note: Although all query parameters are optional, this call must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value. You cannot use the gtin parameter in the same call with either the q parameter or the aspect_filter parameter.
        :param str limit: The number of product summaries to return. This is the result set, a subset of the full collection of products that match the search or filter criteria of this call. Maximum: 200 Default: 50
        :param str mpn: A string consisting of one or more comma-separated Manufacturer Part Numbers (MPNs) that identify products to search for. This call will return all products that have one of the specified MPNs. MPNs are defined by manufacturers for their own products, and are therefore certain to be unique only within a given brand. However, many MPNs do turn out to be globally unique. Note: Although all query parameters are optional, this call must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value. You cannot use the mpn parameter in the same call with either the q parameter or the aspect_filter parameter.
        :param str offset: This parameter is reserved for internal or future use.
        :param str q: A string consisting of one or more keywords to use to search for products in the eBay catalog. Note: This call searches the following product record fields: title, description, brand, and aspects.localizedName, which do not include product IDs. Wildcard characters (e.g. *) are not allowed. The keywords are handled as follows: If the keywords are separated by a comma (e.g. iPhone,256GB), the query returns products that have iPhone AND 256GB. If the keywords are separated by a space (e.g. &quot;iPhone&nbsp;ipad&quot; or &quot;iPhone,&nbsp;ipad&quot;), the query ignores any commas and returns products that have iPhone OR iPad. Note: Although all query parameters are optional, this call must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value. You cannot use the q parameter in the same call with either the gtin parameter or the mpn parameter.
        :return: ProductSearchResponse
        """
        try:
            return self._method_paged(commerce_catalog.Configuration, '/commerce/catalog/v1_beta', commerce_catalog.ProductSummaryApi, commerce_catalog.ApiClient, 'search', CommerceCatalogException, True, ['commerce.catalog', 'product_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_charity_get_charity_org(self, charity_org_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_charity_org  # noqa: E501

        This call is used to retrieve detailed information about supported charitable organizations. It allows users to retrieve the details for a specific charitable organization using its charity organization ID.<br /><br />The call returns the full details for the charitable organization that matches the specified ID.  # noqa: E501

        :param str charity_org_id: The unique ID of the charitable organization. (required)
        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID.<br /><br /><b>Valid Values:</b> <code>EBAY_GB</code> and <code>EBAY_US</code> (required)
        :return: CharityOrg
        """
        try:
            return self._method_single(commerce_charity.Configuration, '/commerce/charity/v1', commerce_charity.CharityOrgApi, commerce_charity.ApiClient, 'get_charity_org', CommerceCharityException, False, ['commerce.charity', 'charity_org'], (charity_org_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_charity_get_charity_org_by_legacy_id(self, x_ebay_c_marketplace_id, legacy_charity_org_id, **kwargs):  # noqa: E501
        """get_charity_org_by_legacy_id  # noqa: E501

        This call allows users to retrieve the details for a specific charitable organization using its legacy charity ID, which has also been referred to as the charity number, external ID, and PayPal Giving Fund ID. The legacy charity ID is separate from eBay’s generic charity ID.  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID.<br /><br /><b>Valid Values:</b> <code>EBAY_GB</code> and <code>EBAY_US</code> (required)
        :param str legacy_charity_org_id: The legacy ID of the charitable organization.<br /><br /><span class=\"tablenote\"><b>Note: </b>The legacy charity ID is the identifier assigned to an organization upon registration with the PayPal Giving Fund (PPGF). It has also been referred to as the external ID/charity number.</span> (required)
        :return: CharityOrg
        """
        try:
            return self._method_single(commerce_charity.Configuration, '/commerce/charity/v1', commerce_charity.CharityOrgApi, commerce_charity.ApiClient, 'get_charity_org_by_legacy_id', CommerceCharityException, False, ['commerce.charity', 'charity_org'], (x_ebay_c_marketplace_id, legacy_charity_org_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_charity_get_charity_orgs(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_charity_orgs  # noqa: E501

        This call is used to search for supported charitable organizations. It allows users to search for a specific charitable organization, or for multiple charitable organizations, from a particular charitable domain and/or geographical region, or by using search criteria.<br /><br />The call returns paginated search results containing the charitable organizations that match the specified criteria.  # noqa: E501

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID.<br /><br /><b>Valid Values:</b> <code>EBAY_GB</code> and <code>EBAY_US</code> (required)
        :param str limit: The number of items, from the result set, returned in a single page.<br /><br /><b>Valid Values:</b> <code>1-100</code><br /><br /><b>Default:</b> <code>20</code>
        :param str offset: The number of items that will be skipped in the result set. This is used with the <b>limit</b> field to control the pagination of the output.<br /><br />For example, if the <b>offset</b> is set to <code>0</code> and the <b>limit</b> is set to <code>10</code>, the method will retrieve items 1 through 10 from the list of items returned. If the <b>offset</b> is set to <code>10</code> and the <b>limit</b> is set to <code>10</code>, the method will retrieve items 11 through 20 from the list of items returned.<br /><br /><b>Valid Values:</b> <code>0-10,000</code><br /><br /><b>Default:</b> <code>0</code>
        :param str q: A query string that matches the keywords in name, mission statement, or description.
        :param str registration_ids: A comma-separated list of charitable organization registration IDs.<br /><br /><span class=\"tablenote\"><b>Note: </b>Do not specify this parameter for query-based searches. Specify either the <b>q</b> or <b>registration_ids</b> parameter, but not both.</span><br /><br /><b>Maximum Limit:</b> <code>20</code>
        :return: CharitySearchResponse
        """
        try:
            return self._method_paged(commerce_charity.Configuration, '/commerce/charity/v1', commerce_charity.CharityOrgApi, commerce_charity.ApiClient, 'get_charity_orgs', CommerceCharityException, False, ['commerce.charity', 'charity_org'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_identity_get_user(self, **kwargs):  # noqa: E501
        """get_user  # noqa: E501

        This method retrieves the account profile information for an authenticated user, which requires a User access token. What is returned is controlled by the scopes. For a business account you use the default scope commerce.identity.readonly, which returns all the fields in the businessAccount container. These are returned because this is all public information. For an individual account, the fields returned in the individualAccount container are based on the scope you use. Using the default scope, only public information, such as eBay user ID, are returned. For details about what each scope returns, see the Identity API Overview. URLs for this method Production URL: https://apiz.ebay.com/commerce/identity/v1/user/ Sandbox URL: https://apiz.sandbox.ebay.com/commerce/identity/v1/user/ In the Sandbox, this method returns mock data. Note: You must use the correct scope or scopes for the data you want returned.  # noqa: E501

        :return: UserResponse
        """
        try:
            return self._method_single(commerce_identity.Configuration, '/commerce/identity/v1', commerce_identity.UserApi, commerce_identity.ApiClient, 'get_user', CommerceIdentityException, True, ['commerce.identity', 'user'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_media_create_video(self, **kwargs):  # noqa: E501
        """create_video  # noqa: E501

        This method creates a video. When using this method, specify the <b>title</b>, <b>size</b>, and <b>classification</b> of the video to be created. <b>Description</b> is an optional field for this method.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> See <a href=\"https://www.ebay.com/help/selling/listings/creating-managing-listings/add-video-to-listing?id=5272#section3\" target=\"_blank\">Adding a video to your listing</a> in the eBay Seller Center for details about video formatting requirements and restrictions, or visit the relevant eBay site help pages for the region in which the listings will be posted.</span><br /><br />When a video is successfully created, the method returns the HTTP Status Code <code>201 Created.</code>The method also returns the location response header containing the <b>video ID</b>, which you can use to retrieve the video.<br /><br /><span class=\"tablenote\"><span style=\"color:#004680\"><strong>Note:</strong></span> There is no ability to edit metadata on videos at this time. There is also no method to delete videos.</span><br /><br />To upload a created video, use the <a href=\" /api-docs/commerce/media/resources/video/methods/uploadVideo\" target=\"_blank\">uploadVideo</a> method.  # noqa: E501

        :param CreateVideoRequest body:
        :return: None
        """
        try:
            return self._method_single(commerce_media.Configuration, '/commerce/media/v1_beta', commerce_media.VideoApi, commerce_media.ApiClient, 'create_video', CommerceMediaException, True, ['commerce.media', 'video'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_media_get_video(self, video_id, **kwargs):  # noqa: E501
        """get_video  # noqa: E501

        This method retrieves a video's metadata and content given a specified <b>video ID</b>. The method returns the <b>title</b>, <b>size</b>, <b>classification</b>, <b>description</b>, <b>video ID</b>, <b>playList</b>, <b>status</b>, <b>status message</b> (if any), <b>expiration  date</b>, and <b>thumbnail</b> image of the retrieved video. <p>The video’s <b>title</b>, <b>size</b>, <b>classification</b>, and <b>description</b> are set using the <a href=\" /api-docs/commerce/media/resources/video/methods/createVideo\" target=\"_blank\">createVideo</a> method.</p> <p>The video's <b>playList</b> contains two URLs that link to instances of the streaming video based on the supported protocol.</p><p>The <b>status</b> field contains the current status of the video. After a video upload is successfully completed, the video's <b>status</b> will show as <code>PROCESSING</code> until the video reaches one of the terminal states of <code>LIVE</code>, <code>BLOCKED</code> or <code>PROCESSING_FAILED</code>.<p> If a video's processing fails, it could be because the file is corrupted, is too large, or its size doesn’t match what was provided in the metadata. Refer to the error messages to determine the cause of the video’s failure to upload.</p> <p> The <b>status message</b> will indicate why a video was blocked from uploading.</p><p>The video’s <b>expiration date</b> is automatically set to 365 days (one year) after the video’s initial creation.<p>The video's <b>thumbnail</b> image is automatically generated when the video is created.  # noqa: E501

        :param str video_id: The <b>video ID</b> for the video to be retrieved. (required)
        :return: Video
        """
        try:
            return self._method_single(commerce_media.Configuration, '/commerce/media/v1_beta', commerce_media.VideoApi, commerce_media.ApiClient, 'get_video', CommerceMediaException, True, ['commerce.media', 'video'], video_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_media_upload_video(self, content_type, video_id, **kwargs):  # noqa: E501
        """upload_video  # noqa: E501

        This method associates the specified file with the specified <b>video ID</b> and uploads the input file. After the file has been uploaded the processing of the file begins.<br /><br /><span class=\"tablenote\"><span style=\"color:#004680\"><strong>Note:</strong></span> The size of the video to be uploaded must exactly match the size of the video's input stream that was set in the <a href=\" /api-docs/commerce/media/resources/video/methods/createVideo\" target=\"_blank\">createVideo</a> method. If the sizes do not match, the video will not upload successfully.</span><br /><br />When a video is successfully uploaded, it returns the HTTP Status Code <code>200 OK</code>.<br /><br />The status flow is <code>PENDING_UPLOAD</code> > <code>PROCESSING</code> > <code>LIVE</code>,  <code>PROCESSING_FAILED</code>, or <code>BLOCKED</code>. After a video upload is successfully completed, the status will show as <code>PROCESSING</code> until the video reaches one of the terminal states of <code>LIVE</code>, <code>BLOCKED</code>, or <code>PROCESSING_FAILED</code>. If the size information (in bytes) provided is incorrect, the API will throw an error.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> See <a href=\"https://www.ebay.com/help/selling/listings/creating-managing-listings/add-video-to-listing?id=5272#section3\" target=\"_blank\">Adding a video to your listing</a> in the eBay Seller Center for details about video formatting requirements and restrictions, or visit the relevant eBay site help pages for the region in which the listings will be posted.</span><br /><br />To retrieve an uploaded video, use the <a href=\"/api-docs/commerce/media/resources/video/methods/getVideo\" target=\"_blank\">getVideo</a> method.  # noqa: E501

        :param str content_type: Use this header to specify the content type for the upload. The Content-Type should be set to <code>application/octet-stream</code>. (required)
        :param str video_id: The <b>video ID</b> for the uploaded video. (required)
        :param InputStream body: The request payload for this method is the input stream for the video source. The input source must be an .mp4 file of the type MPEG-4 Part 10 or Advanced Video Coding (MPEG-4 AVC).
        :param str content_length: Use this header to specify the content length for the upload. Use Content-Range: bytes {1}-{2}/{3} and Content-Length:{4} headers.<br /><br /><span class=\"tablenote\"><span style=\"color:#004680\"><strong>Note:</strong></span> This header is optional and is only required for <i>resumable</i> uploads (when an upload is interrupted and must be resumed from a certain point).</span>
        :param str content_range: Use this header to specify the content range for the upload. The Content-Range should be of the following bytes ((?:[0-9]+-[0-9]+)|\\\\\\\\*)/([0-9]+|\\\\\\\\*) pattern.<br /><br /><span class=\"tablenote\"><span style=\"color:#004680\"><strong>Note:</strong></span> This header is optional and is only required for <i>resumable</i> uploads (when an upload is interrupted and must be resumed from a certain point).</span>
        :return: None
        """
        try:
            return self._method_single(commerce_media.Configuration, '/commerce/media/v1_beta', commerce_media.VideoApi, commerce_media.ApiClient, 'upload_video', CommerceMediaException, True, ['commerce.media', 'video'], (content_type, video_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_config(self, **kwargs):  # noqa: E501
        """get_config  # noqa: E501

        This method allows applications to retrieve a previously created configuration.  # noqa: E501

        :return: Config
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.ConfigApi, commerce_notification.ApiClient, 'get_config', CommerceNotificationException, False, ['commerce.notification', 'config'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_update_config(self, **kwargs):  # noqa: E501
        """update_config  # noqa: E501

        This method allows applications to create a new configuration or update an existing configuration. This app-level configuration allows developers to set up alerts.  # noqa: E501

        :param Config body: The configurations for this application.
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.ConfigApi, commerce_notification.ApiClient, 'update_config', CommerceNotificationException, False, ['commerce.notification', 'config'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_create_destination(self, **kwargs):  # noqa: E501
        """create_destination  # noqa: E501

        This method allows applications to create a destination. A destination is an endpoint that receives HTTP push notifications.<br /><br />A single destination for all topics is valid, as is individual destinations for each topic.<br /><br />To update a destination, use the <strong>updateDestination</strong> call.<br /><br />The destination created will need to be referenced while creating or updating a subscription to a topic.<br/><br/><span class=\"tablenote\"><b>Note:</b> The destination should be created and ready to respond with the expected <b>challengeResponse</b> for the endpoint to be registered successfully. Refer to the <a href=\"/api-docs/commerce/notification/overview.html\">Notification API overview</a> for more information.</span>  # noqa: E501

        :param DestinationRequest body: The create destination request.
        :return: object
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'create_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_delete_destination(self, destination_id, **kwargs):  # noqa: E501
        """delete_destination  # noqa: E501

        This method provides applications a way to delete a destination.<br /><br />The same destination ID can be used by many destinations.<br /><br />Trying to delete an active destination results in an error. You can disable a subscription, and when the destination is no longer in use, you can delete it.  # noqa: E501

        :param str destination_id: The unique identifier for the destination. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'delete_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], destination_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_destination(self, destination_id, **kwargs):  # noqa: E501
        """get_destination  # noqa: E501

        This method allows applications to fetch the details for a destination. The details include the destination name, status, and configuration, including the endpoint and verification token.  # noqa: E501

        :param str destination_id: The unique identifier for the destination. (required)
        :return: Destination
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'get_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], destination_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_destinations(self, **kwargs):  # noqa: E501
        """get_destinations  # noqa: E501

        This method allows applications to retrieve a paginated collection of destination resources and related details. The details include the destination names, statuses, and configurations, including the endpoints and verification tokens.  # noqa: E501

        :param str limit: The number of items, from the result set, returned in a single page. Range is from 10-100. If this parameter is omitted, the default value is used.<br/><br/><b>Default:</b> 20<br/><br/><b>Maximum:</b> 100 items per page
        :param str continuation_token: The continuation token for the next set of results.
        :return: DestinationSearchResponse
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'get_destinations', CommerceNotificationException, False, ['commerce.notification', 'destination'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_update_destination(self, destination_id, **kwargs):  # noqa: E501
        """update_destination  # noqa: E501

        This method allows applications to update a destination.<br/><br/><span class=\"tablenote\"><b>Note:</b> The destination should be created and ready to respond with the expected <b>challengeResponse</b> for the endpoint to be registered successfully. Refer to the <a href=\"/api-docs/commerce/notification/overview.html\">Notification API overview</a> for more information.</span>  # noqa: E501

        :param str destination_id: The unique identifier for the destination. (required)
        :param DestinationRequest body: The create subscription request.
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'update_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], destination_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_public_key(self, public_key_id, **kwargs):  # noqa: E501
        """get_public_key  # noqa: E501

        This method allows users to retrieve a public key using a specified key ID. The public key that is returned in the response payload is used to process and validate eBay notifications.<br /><br />The public key ID, which is a required request parameter for this method, is retrieved from the Base64-encoded <b>X-EBAY-SIGNATURE</b> header that is included in the eBay notification.<br /><br /><span class=\"tablenote\"><b>Note:</b> For more details about how to process eBay push notifications and validate notification message payloads, see the <a href=\"/api-docs/commerce/notification/overview.html\">Notification API overview</a>.</span>  # noqa: E501

        :param str public_key_id: The unique key ID that is used to retrieve the public key.<br /><br /><span class=\"tablenote\"><b>Note: </b>This is retrieved from the <b>X-EBAY-SIGNATURE</b> header that is included with the push notification.</span> (required)
        :return: PublicKey
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.PublicKeyApi, commerce_notification.ApiClient, 'get_public_key', CommerceNotificationException, False, ['commerce.notification', 'public_key'], public_key_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_create_subscription(self, **kwargs):  # noqa: E501
        """create_subscription  # noqa: E501

        This method allows applications to create a subscription for a topic and supported schema version. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.<br/><br/>Each application and topic-schema pairing to a subscription should have a 1:1 cardinality.<br/><br/>You can create the subscription in disabled mode, test it (see the <b>test</b> method), and when everything is ready, you can enable the subscription (see the <b>enableSubscription</b> method).<br /><br /><span class=\"tablenote\"><b>Note:</b> If an application is not authorized to subscribe to a topic, for example, if your authorization does not include the list of scopes required for the topic, an error code of 195011 is returned.</span>  # noqa: E501

        :param CreateSubscriptionRequest body: The create subscription request.
        :return: object
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'create_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_delete_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """delete_subscription  # noqa: E501

        This method allows applications to delete a subscription. Subscriptions can be deleted regardless of status.  # noqa: E501

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'delete_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_disable_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """disable_subscription  # noqa: E501

        This method disables a subscription, which prevents the subscription from providing notifications. To restart a subscription, call <strong>enableSubscription</strong>.  # noqa: E501

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'disable_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_enable_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """enable_subscription  # noqa: E501

        This method allows applications to enable a disabled subscription. To pause (or disable) an enabled subscription, call <strong>disableSubscription</strong>.  # noqa: E501

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'enable_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """get_subscription  # noqa: E501

        This method allows applications to retrieve subscription details for the specified subscription.<br /><br />Specify the subscription to retrieve using the <strong>subscription_id</strong>. Use the <strong>getSubscriptions</strong> method to browse all subscriptions if you do not know the <strong>subscription_id</strong>.<br /><br />Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  # noqa: E501

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: Subscription
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'get_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_subscriptions(self, **kwargs):  # noqa: E501
        """get_subscriptions  # noqa: E501

        This method allows applications to retrieve a list of all subscriptions. The list returned is a paginated collection of subscription resources.<br /><br />Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  # noqa: E501

        :param str limit: The number of items, from the result set, returned in a single page. Range is from 10-100. If this parameter is omitted, the default value is used.<br/><br/><b>Default:</b> 20<br/><br/><b>Maximum:</b> 100 items per page
        :param str continuation_token: The continuation token for the next set of results.
        :return: SubscriptionSearchResponse
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'get_subscriptions', CommerceNotificationException, False, ['commerce.notification', 'subscription'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_test(self, subscription_id, **kwargs):  # noqa: E501
        """test  # noqa: E501

        This method triggers a mocked test payload that includes a notification ID, publish date, and so on. Use this method to test your subscription end-to-end.<br /><br />You can create the subscription in disabled mode, test it using this method, and when everything is ready, you can enable the subscription (see the <strong>enableSubscription</strong> method).<br /><br /><span class=\"tablenote\"><b>Note:</b> Use the <strong>notificationId</strong> to tell the difference between a test payload and a real payload.</span>  # noqa: E501

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'test', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_update_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """update_subscription  # noqa: E501

        This method allows applications to update a subscription. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.<br /><br /><span class=\"tablenote\"><b>Note:</b> This call returns an error if an application is not authorized to subscribe to a topic.</span><br/><br/>You can pause and restart a subscription. See the <b>disableSubscription</b> and <b>enableSubscription</b> methods.  # noqa: E501

        :param str subscription_id: The unique identifier for the subscription. (required)
        :param UpdateSubscriptionRequest body: The create subscription request.
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'update_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_topic(self, topic_id, **kwargs):  # noqa: E501
        """get_topic  # noqa: E501

        This method allows applications to retrieve details for the specified topic. This information includes supported schema versions, formats, and other metadata for the topic.<br /><br />Applications can subscribe to any of the topics for a supported schema version and format, limited by the authorization scopes required to subscribe to the topic.<br /><br />A topic specifies the type of information to be received and the data types associated with an event. An event occurs in the eBay system, such as when a user requests deletion or revokes access for an application. An event is an instance of an event type (topic).<br /><br />Specify the topic to retrieve using the <b>topic_id</b> URI parameter.<br /><br /><span class=\"tablenote\"><b>Note:</b> Use the <a href=\"/api-docs/commerce/notification/resources/topic/methods/getTopics\">getTopics</a> method to find a topic if you do not know the topic ID.</span>  # noqa: E501

        :param str topic_id: The ID of the topic for which to retrieve the details. (required)
        :return: Topic
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.TopicApi, commerce_notification.ApiClient, 'get_topic', CommerceNotificationException, False, ['commerce.notification', 'topic'], topic_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_topics(self, **kwargs):  # noqa: E501
        """get_topics  # noqa: E501

        This method returns a paginated collection of all supported topics, along with the details for the topics. This information includes supported schema versions, formats, and other metadata for the topics.<br /><br />Applications can subscribe to any of the topics for a supported schema version and format, limited by the authorization scopes required to subscribe to the topic.<br /><br />A topic specifies the type of information to be received and the data types associated with an event. An event occurs in the eBay system, such as when a user requests deletion or revokes access for an application. An event is an instance of an event type (topic).  # noqa: E501

        :param str limit: The maximum number of items to return per page from the result set. A result set is the complete set of results returned by the method. Range is from 10-100. <br /><br />If this parameter is omitted, the default value is used.<br/><br/><b> Default:</b> 20<br /><br /><b>Maximum:</b> 100 items per page
        :param str continuation_token: The token used to access the next set of results.
        :return: TopicSearchResponse
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.TopicApi, commerce_notification.ApiClient, 'get_topics', CommerceNotificationException, False, ['commerce.notification', 'topic'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_fetch_item_aspects(self, category_tree_id, **kwargs):  # noqa: E501
        """Get Aspects for All Leaf Categories in a Marketplace  # noqa: E501

        This call returns a complete list of aspects for all of the leaf categories that belong to an eBay marketplace. The eBay marketplace is specified through the <b>category_tree_id</b> URI parameter.<br /><br /><span class=\"tablenote\"> <strong>Note:</strong> This call can return a large payload, so the call returns the response as a gzipped JSON file. The open source <a href=\"https://github.com/eBay/taxonomy-sdk\" target=\"_blank\">Taxonomy SDK</a> can be used to compare the aspect metadata that is returned in this response. The bulk download capability that this method provides, when combined with the Taxonomy SDK, brings transparency to the evolution of the metadata.</span>  # noqa: E501

        :param str category_tree_id: The unique identifier of the eBay category tree being requested. (required)
        :return: GetCategoriesAspectResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'fetch_item_aspects', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], category_tree_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_category_subtree(self, category_id, category_tree_id, **kwargs):  # noqa: E501
        """Get a Category Subtree  # noqa: E501

        This call retrieves the details of all nodes of the category tree hierarchy (the subtree) below a specified category of a category tree. You identify the tree using the <b>category_tree_id</b> parameter, which was returned by the <b>getDefaultCategoryTreeId</b> call in the <b>categoryTreeId</b> field.<br /><br /><span class=\"tablenote\"> <strong>Note:</strong> This call can return a very large payload, so you are strongly advised to submit the request with the following HTTP header:       <br /><br /><code>&nbsp;&nbsp;Accept-Encoding: application/gzip</code>       <br /><br />With this header (in addition to the required headers described under <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP Request Headers</a>), the call returns the response with <b>gzip</b> compression. </span>  # noqa: E501

        :param str category_id: The unique identifier of the category at the top of the subtree being requested. <br /><br />    <span class=\"tablenote\"> <strong>Note:</strong> If the <b>category_id</b> submitted identifies the root node of the tree, this call returns an error. To retrieve the complete tree, use this value with the <b>getCategoryTree</b> call.                   <br /><br />   If the <b>category_id</b> submitted identifies a leaf node of the tree, the call response will contain information about only that leaf node, which is a valid subtree.   <!-- <br /><br /> This call also returns an error if <b>category_id</b> identifies a deprecated category. This can occur if you routinely cache your category trees. Use the <b>Get Deprecated Categories and Mapping</b> call to determine which current category should be used in place of the deprecated category, and use the <b>getCategoryTree</b> call to update your cached copy of the tree. --> </span> (required)
        :param str category_tree_id: The unique identifier of the eBay category tree from which a category subtree is being requested. (required)
        :return: CategorySubtree
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_category_subtree', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_id, category_tree_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_category_suggestions(self, category_tree_id, q, **kwargs):  # noqa: E501
        """Get Suggested Categories  # noqa: E501

        This call returns an array of category tree leaf nodes in the specified category tree that are considered by eBay to most closely correspond to the query string <b>q</b>. Returned with each suggested node is a localized name for that category (based on the <b>Accept-Language</b> header specified for the call), and details about each of the category's ancestor nodes, extending from its immediate parent up to the root of the category tree.<br /><br /><span class=\"tablenote\"> <strong>Note:</strong> This call can return a large payload, so you are advised to submit the request with the following HTTP header:<br /><br /><code>&nbsp;&nbsp;Accept-Encoding: application/gzip</code><br /><br />              With this header (in addition to the required headers described under <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP Request Headers</a>), the call returns the response with <b>gzip</b> compression. </span><br /><br />You identify the tree using the <b>category_tree_id</b> parameter, which was returned by the <b>getDefaultCategoryTreeId</b> call in the <b>categoryTreeId</b> field.<br /><br /><span class=\"tablenote\"> <strong><span style=\"color:red\">Important:</span></strong> This call is not supported in the Sandbox environment. It will return a response payload in which the <b>categoryName</b> fields contain random or boilerplate text regardless of the query submitted. </span>  # noqa: E501

        :param str category_tree_id: The unique identifier of the eBay category tree for which suggested nodes are being requested. (required)
        :param str q: A quoted string that describes or characterizes the item being offered for sale. The string format is free form, and can contain any combination of phrases or keywords. eBay will parse the string and return suggested categories for the item. (required)
        :return: CategorySuggestionResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_category_suggestions', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_tree_id, q), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_category_tree(self, category_tree_id, **kwargs):  # noqa: E501
        """Get a Category Tree  # noqa: E501

        This call retrieves the complete category tree that is identified by the <b>category_tree_id</b> parameter. The value of <b>category_tree_id</b> was returned by the <b>getDefaultCategoryTreeId</b> call in the <b>categoryTreeId</b> field. The response contains details of all nodes of the specified eBay category tree, as well as the eBay marketplaces that use this category tree.      <br /><br />            <span class=\"tablenote\"> <strong>Note:</strong> This call can return a very large payload, so you are strongly advised to submit the request with the following HTTP header:       <br /><br />     <code>&nbsp;&nbsp;Accept-Encoding: application/gzip</code>       <br /><br />             With this header (in addition to the required headers described under <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP Request Headers</a>), the call returns the response with <b>gzip</b> compression.</span>  # noqa: E501

        :param str category_tree_id: The unique identifier of the eBay category tree being requested. (required)
        :return: CategoryTree
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_category_tree', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], category_tree_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_compatibility_properties(self, category_tree_id, category_id, **kwargs):  # noqa: E501
        """Get Compatibility Properties  # noqa: E501

        This call retrieves the compatible vehicle aspects that are used to define a motor vehicle that is compatible with a motor vehicle part or accessory. The values that are retrieved here might include motor vehicle aspects such as 'Make', 'Model', 'Year', 'Engine', and 'Trim', and each of these aspects are localized for the eBay marketplace.<br/><br/> The <strong>category_tree_id</strong> value is passed in as a path parameter, and this value identifies the eBay category tree. The <strong>category_id</strong> value is passed in as a query parameter, as this parameter is also required. The specified category must be a category that supports parts compatibility.<br/><br/> At this time, this operation only supports parts and accessories listings for cars, trucks, and motorcycles (not boats,  power sports, or any other vehicle types). Only the following eBay marketplaces support parts compatibility:<ul><li>eBay US (Motors and non-Motors categories)</li><li>eBay Canada (Motors and non-Motors categories)</li><li>eBay UK</li><li>eBay Germany</li><li>eBay Australia</li><li>eBay France</li><li>eBay Italy</li><li>eBay Spain</li></ul>  # noqa: E501

        :param str category_tree_id: This is the unique identifier of category tree. The following is the list of <strong>category_tree_id</strong> values and the eBay marketplaces that they represent. One of these ID values must be passed in as a path parameter, and the <strong>category_id</strong> value, that is passed in as query parameter, must be a valid eBay category on that eBay marketplace that supports parts compatibility for cars, trucks, or motorcycles.<br/><br/><ul><li>eBay US: 0</li><li>eBay Motors US: 100</li><li>eBay Canada: 2</li><li>eBay UK: 3</li><li>eBay Germany: 77</li><li>eBay Australia: 15</li><li>eBay France: 71</li><li>eBay Italy: 101</li><li>eBay Spain: 186</li></ul> (required)
        :param str category_id: The unique identifier of an eBay category. This eBay category must be a valid eBay category on the specified eBay marketplace, and the category must support parts compatibility for cars, trucks, or motorcycles. The <strong>getAutomotivePartsCompatibilityPolicies</strong> method of the Selling Metadata API can be used to retrieve all eBay categories for an eBay marketplace that supports parts compatibility cars, trucks, or motorcycles. The <strong>getAutomotivePartsCompatibilityPolicies</strong> method can also be used to see if one or more specific eBay categories support parts compatibility. (required)
        :return: GetCompatibilityMetadataResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_compatibility_properties', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_tree_id, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_compatibility_property_values(self, category_tree_id, compatibility_property, category_id, **kwargs):  # noqa: E501
        """Get Compatibility Property Values  # noqa: E501

        This call retrieves applicable compatible vehicle property values based on the specified eBay marketplace, specified eBay category, and filters used in the request. Compatible vehicle properties are returned in the <strong>compatibilityProperties.name</strong> field of a <strong>getCompatibilityProperties</strong> response. <br/><br/> One compatible vehicle property applicable to the specified eBay marketplace and eBay category is specified through the required <strong>compatibility_property</strong> filter. Then, the user has the option of further restricting the compatible vehicle property values that are returned in the response by specifying one or more compatible vehicle property name/value pairs through the <strong>filter</strong> query parameter.<br/><br/> See the documentation in <strong>URI parameters</strong> section for more information on using the <strong>compatibility_property</strong> and <strong>filter</strong> query parameters together to customize the data that is retrieved.  # noqa: E501

        :param str category_tree_id: This is the unique identifier of the category tree. The following is the list of <strong>category_tree_id</strong> values and the eBay marketplaces that they represent. One of these ID values must be passed in as a path parameter, and the <strong>category_id</strong> value, that is passed in as query parameter, must be a valid eBay category on that eBay marketplace that supports parts compatibility for cars, trucks, or motorcycles.<br/><br/><ul><li>eBay US: 0</li><li>eBay Motors US: 100</li><li>eBay Canada: 2</li><li>eBay UK: 3</li><li>eBay Germany: 77</li><li>eBay Australia: 15</li><li>eBay France: 71</li><li>eBay Italy: 101</li><li>eBay Spain: 186</li></ul> (required)
        :param str compatibility_property: One compatible vehicle property applicable to the specified eBay marketplace and eBay category is specified in this required filter. Compatible vehicle properties are returned in the <strong>compatibilityProperties.name</strong> field of a <strong>getCompatibilityProperties</strong> response. <br/><br/> For example, if you wanted to retrieve all vehicle trims for a 2018 Toyota Camry, you would set this filter as follows: <code>compatibility_property=Trim</code>; and then include the following three name/value filters through one <strong>filter</strong> parameter: <code>filter=Year:2018,Make:Toyota,Model:Camry</code>. So, putting this all together, your URI would look something like this:<br/><br/><pre><code>GET https://api.ebay.com/commerce/<br/>taxonomy/v1/category_tree/100/<br/>get_compatibility_property_values?<br/><strong>category_id</strong>=6016&<strong>compatibility_property</strong>=Trim<br/>&<strong>filter</strong>=filter=Year:2018,Make:Toyota,Model:Camry</code></pre> (required)
        :param str category_id: The unique identifier of an eBay category. This eBay category must be a valid eBay category on the specified eBay marketplace, and the category must support parts compatibility for cars, trucks, or motorcycles. The <strong>getAutomotivePartsCompatibilityPolicies</strong> method of the Selling Metadata API can be used to retrieve all eBay categories for an eBay marketplace that supports parts compatibility cars, trucks, or motorcycles. The <strong>getAutomotivePartsCompatibilityPolicies</strong> method can also be used to see if one or more specific eBay categories support parts compatibility. (required)
        :param str filter: One or more compatible vehicle property name/value pairs are passed in through this query parameter. The compatible vehicle property name and corresponding value are delimited with a colon (:), such as <code>filter=Year:2018</code>, and multiple compatible vehicle property name/value pairs are delimited with a comma (,). <br/><br/> For example, if you wanted to retrieve all vehicle trims for a 2018 Toyota Camry, you would set the <strong>compatibility_property</strong> filter as follows: <code>compatibility_property=Trim</code>; and then include the following three name/value filters through one <strong>filter</strong> parameter: <code>filter=Year:2018,Make:Toyota,Model:Camry</code>. So, putting this all together, your URI would look something like this:<br/><br/><pre><code>GET https://api.ebay.com/commerce/<br/>taxonomy/v1/category_tree/100/<br/>get_compatibility_property_values?<br/><strong>category_id</strong>=6016&<strong>compatibility_property</strong>=Trim<br/>&<strong>filter</strong>=filter=Year:2018,Make:Toyota,Model:Camry</code></pre> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/commerce/taxonomy/types/txn:ConstraintFilter
        :return: GetCompatibilityPropertyValuesResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_compatibility_property_values', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_tree_id, compatibility_property, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_default_category_tree_id(self, marketplace_id, **kwargs):  # noqa: E501
        """Get a Default Category Tree ID  # noqa: E501

        A given eBay marketplace might use multiple category trees, but one of those trees is considered to be the default for that marketplace. This call retrieves a reference to the default category tree associated with the specified eBay marketplace ID. The response includes only the tree's unique identifier and version, which you can use to retrieve more details about the tree, its structure, and its individual category nodes.  # noqa: E501

        :param str marketplace_id: The ID of the eBay marketplace for which the category tree ID is being requested. For a list of supported marketplace IDs, see <a href=\"/api-docs/commerce/taxonomy/static/supportedmarketplaces.html\">Marketplaces with Default Category Trees</a>. (required)
        :param str accept_language: A header used to indicate the natural language the seller prefers for the response.<br /><br />This specifies the language that the seller wants to use when the field values provided in the request body are displayed to consumers.<br /><br /><span class=\"tablenote\"> <strong>Note:</strong> For details, see <i>Accept-Language</i> in <a href=\"/api-docs/static/rest-request-components.html#headers\">HTTP request headers</a>.</span><br /><br /><b>Valid Values:</b> <ul><li>For EBAY_CA in French:<br /><code>Accept-Language: fr-CA</code></li><li>For EBAY_BE in French:<br /><code>Accept-Language: fr-BE</code></li></ul>
        :return: BaseCategoryTree
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_default_category_tree_id', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_item_aspects_for_category(self, category_id, category_tree_id, **kwargs):  # noqa: E501
        """get_item_aspects_for_category  # noqa: E501

        This call returns a list of <i>aspects</i> that are appropriate or necessary for accurately describing items in the specified leaf category. Each aspect identifies an item attribute (for example, color) for which the seller will be required or encouraged to provide a value (or variation values) when offering an item in that category on eBay.<br /><br />For each aspect, <b>getItemAspectsForCategory</b> provides complete metadata, including: <ul> <li>The aspect's data type, format, and entry mode</li> <li>Whether the aspect is required in listings</li> <li>Whether the aspect can be used for item variations</li> <li>Whether the aspect accepts multiple values for an item</li> <li>Allowed values for the aspect</li> </ul> Use this information to construct an interface through which sellers can enter or select the appropriate values for their items or item variations. Once you collect those values, include them as product aspects when creating inventory items using the Inventory API.  # noqa: E501

        :param str category_id: The unique identifier of the leaf category for which aspects are being requested.          <br /><br />                 <span class=\"tablenote\"> <strong>Note:</strong> If the <b>category_id</b> submitted does not identify a leaf node of the tree, this call returns an error. </span> (required)
        :param str category_tree_id: The unique identifier of the eBay category tree from which the specified category's aspects are being requested. (required)
        :return: AspectMetadata
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_item_aspects_for_category', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_id, category_tree_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_translation_translate(self, body, **kwargs):  # noqa: E501
        """translate  # noqa: E501

        This method translates listing title and listing description text from one language into another. For a full list of supported language translations, see the table in the API Overview page.  # noqa: E501

        :param TranslateRequest body: (required)
        :return: TranslateResponse
        """
        try:
            return self._method_single(commerce_translation.Configuration, '/commerce/translation/v1_beta', commerce_translation.LanguageApi, commerce_translation.ApiClient, 'translate', CommerceTranslationException, False, ['commerce.translation', 'language'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_analytics_get_rate_limits(self, **kwargs):  # noqa: E501
        """get_rate_limits  # noqa: E501

        This method retrieves the call limit and utilization data for an application. The data is retrieved for all RESTful APIs and resources. The response from getRateLimits includes a list of the applicable resources and the &quot;call limit&quot;, or quota, that is set for each resource. In addition to quota information, the response also includes the number of remaining calls available before the limit is reached, the time remaining before the quota resets, and the length of the &quot;time window&quot; to which the quota applies. By default, this method returns utilization data for all RESTful API resources. Use the api_name and api_context query parameters to filter the response to only the desired APIs. For more on call limits, see Compatible Application Check.  # noqa: E501

        :param str api_context: This optional query parameter filters the result to include only the specified API context. Acceptable values for the parameter are buy, sell, commerce, and developer.
        :param str api_name: This optional query parameter filters the result to include only the APIs specified. Example values are browse for the Buy APIs context, inventory for the Sell APIs context, and taxonomy for the Commerce APIs context.
        :return: RateLimitsResponse
        """
        try:
            return self._method_single(developer_analytics.Configuration, '/developer/analytics/v1_beta', developer_analytics.RateLimitApi, developer_analytics.ApiClient, 'get_rate_limits', DeveloperAnalyticsException, False, ['developer.analytics', 'rate_limit'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_analytics_get_user_rate_limits(self, **kwargs):  # noqa: E501
        """get_user_rate_limits  # noqa: E501

        This method retrieves the call limit and utilization data for an application user. The call-limit data is returned for all RESTful APIs and resources that limit calls on a per-user basis. The response from getUserRateLimits includes a list of the applicable resources and the &quot;call limit&quot;, or quota, that is set for each resource. In addition to quota information, the response also includes the number of remaining calls available before the limit is reached, the time remaining before the quota resets, and the length of the &quot;time window&quot; to which the quota applies. By default, this method returns utilization data for all RESTful API resources that limit request access by user. Use the api_name and api_context query parameters to filter the response to only the desired APIs. For more on call limits, see Compatible Application Check.  # noqa: E501

        :param str api_context: This optional query parameter filters the result to include only the specified API context. Acceptable values for the parameter are buy, sell, commerce, and developer.
        :param str api_name: This optional query parameter filters the result to include only the APIs specified. Example values are browse for the Buy APIs context, inventory for the Sell APIs context, and taxonomy for the Commerce APIs context.
        :return: RateLimitsResponse
        """
        try:
            return self._method_single(developer_analytics.Configuration, '/developer/analytics/v1_beta', developer_analytics.UserRateLimitApi, developer_analytics.ApiClient, 'get_user_rate_limits', DeveloperAnalyticsException, True, ['developer.analytics', 'user_rate_limit'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_custom_policy(self, body, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """create_custom_policy  # noqa: E501

        This method creates a new custom policy in which a seller specifies their terms for complying with local governmental regulations. <br/><br/>Two Custom Policy types are supported: <ul><li>Product Compliance (PRODUCT_COMPLIANCE)</li> <li>Takeback (TAKE_BACK)</li></ul>Each Custom Policy targets a <b>policyType</b> and <b>eBay marketplace</b> combination. Multiple policies may be created as follows: <ul><li><b>Product Compliance</b>: a maximum of 10 policies per eBay marketplace may be created</li> <li><b>Takeback</b>: a maximum of 3 policies per eBay marketplace may be created</li></ul>A successful create policy call returns an HTTP status code of <b>201 Created</b> with the system-generated policy ID included in the <b>Location</b> response header.<br/><br/><b>Product Compliance Policy</b><br/><br/>Product Compliance policies disclose product information as required for regulatory compliance.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> A maximum of 10 Product Compliance policies per eBay marketplace may be created.</span> <br/><br/> <b>Takeback Policy</b><br/><br/>Takeback policies describe the seller's legal obligation to take back a previously purchased item when the buyer purchases a new one.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> A maximum of 3 Takeback policies per eBay marketplace may be created.</span>  # noqa: E501

        :param CustomPolicyCreateRequest body: Request to create a new Custom Policy. (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay markeplace for the custom policy that is being created. Supported values for this header can be found in the <a href=\"/api-docs/sell/compliance/types/bas:MarketplaceIdEnum\" target=\"_blank\">MarketplaceIdEnum</a> type definition.<br/> <br/> <span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span> (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'create_custom_policy', SellAccountException, True, ['sell.account', 'custom_policy'], (body, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_custom_policies(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_custom_policies  # noqa: E501

        This method retrieves the list of custom policies specified by the <b>policy_types</b> query parameter for the selected eBay marketplace.<br/> <br/> <span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span><br/><br/>For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\" target=\"_blank\">HTTP request headers</a>.  # noqa: E501

        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay markeplace for the custom policy that is being created. Supported values for this header can be found in the <a href=\"/api-docs/sell/compliance/types/bas:MarketplaceIdEnum\" target=\"_blank\">MarketplaceIdEnum</a> type definition.<br/> <br/> <span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span> (required)
        :param str policy_types: This query parameter specifies the type of custom policies to be returned.<br /><br />Multiple policy types may be requested in a single call by providing a comma-delimited set of all policy types to be returned.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> Omitting this query parameter from a request will also return policies of all policy types.</span><br/><br/>Two Custom Policy types are supported: <ul><li>Product Compliance (PRODUCT_COMPLIANCE)</li> <li>Takeback (TAKE_BACK)</li></ul>
        :return: CustomPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'get_custom_policies', SellAccountException, True, ['sell.account', 'custom_policy'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_custom_policy(self, custom_policy_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_custom_policy  # noqa: E501

        This method retrieves the custom policy specified by the <b>custom_policy_id</b> path parameter for the selected eBay marketplace.<br/> <br/> <span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span><br/><br/>For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\" target=\"_blank\">HTTP request headers</a>.  # noqa: E501

        :param str custom_policy_id: This path parameter is the unique custom policy identifier for the policy to be returned.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> This value is automatically assigned by the system when the policy is created.</span> (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay markeplace for the custom policy that is being created. Supported values for this header can be found in the <a href=\"/api-docs/sell/compliance/types/bas:MarketplaceIdEnum\" target=\"_blank\">MarketplaceIdEnum</a> type definition.<br/> <br/> <span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span> (required)
        :return: CustomPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'get_custom_policy', SellAccountException, True, ['sell.account', 'custom_policy'], (custom_policy_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_custom_policy(self, body, x_ebay_c_marketplace_id, custom_policy_id, **kwargs):  # noqa: E501
        """update_custom_policy  # noqa: E501

        This method updates an existing custom policy specified by the <b>custom_policy_id</b> path parameter for the selected marketplace. This method overwrites the policy's <b>Name</b>, <b>Label</b>, and <b>Description</b> fields. Therefore, the complete, current text of all three policy fields must be included in the request payload even when one or two of these fields will not actually be updated.<br/> <br/>For example, the value for the <b>Label</b> field is to be updated, but the <b>Name</b> and <b>Description</b> values will remain unchanged. The existing <b>Name</b> and <b>Description</b> values, as they are defined in the current policy, must also be passed in. <br/><br/>A successful policy update call returns an HTTP status code of <b>204 No Content</b>.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span><br/><br/>For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.  # noqa: E501

        :param CustomPolicyRequest body: Request to update a current custom policy. (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay markeplace for the custom policy that is being created. Supported values for this header can be found in the <a href=\"/api-docs/sell/compliance/types/bas:MarketplaceIdEnum\" target=\"_blank\">MarketplaceIdEnum</a> type definition.<br/> <br/> <span class=\"tablenote\"><strong>Note:</strong> The following eBay marketplaces support Custom Policies: <ul><li>Germany (EBAY_DE)</li> <li>Canada (EBAY_CA)</li> <li>Australia (EBAY_AU)</li> <li>United States (EBAY_US)</li> <li>France (EBAY_FR)</li></ul></span> (required)
        :param str custom_policy_id: This path parameter is the unique custom policy identifier for the policy to be returned.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> This value is automatically assigned by the system when the policy is created.</span> (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'update_custom_policy', SellAccountException, True, ['sell.account', 'custom_policy'], (body, x_ebay_c_marketplace_id, custom_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_fulfillment_policy(self, body, **kwargs):  # noqa: E501
        """create_fulfillment_policy  # noqa: E501

        This method creates a new fulfillment policy where the policy encapsulates seller's terms for fulfilling item purchases. Fulfillment policies include the shipment options that the seller offers to buyers.  <br><br>Each policy targets a <b>marketplaceId</b> and <code>categoryTypes.</code><b>name</b> combination and you can create multiple policies for each combination. Be aware that some marketplaces require a specific fulfillment policy for vehicle listings.  <br><br>A successful request returns the URI to the new policy in the <b>Location</b> response header and the ID for the new policy is returned in the response payload.  <p class=\"tablenote\"><b>Tip:</b> For details on creating and using the business policies supported by the Account API, see <a href=\"/api-docs/sell/static/seller-accounts/business-policies.html\">eBay business policies</a>.</p>  <p><b>Marketplaces and locales</b></p>  <p>Policy instructions can be localized by providing a locale in the <code>Accept-Language</code> HTTP request header. For example, the following setting displays field values from the request body in German: <code>Accept-Language: de-DE</code>.</p>  <p>Target the specific locale of a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, target the French locale of the Canadian marketplace by specifying the <code>fr-CA</code> locale for <code>Content-Language</code>. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>.</p> <p class=\"tablenote\"><b>Tip:</b> For details on headers, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.</p><p><b>Using the eBay standard envelope service (eSE)</b></p>  <p>The eBay standard envelope service (eSE) is a domestic envelope service with tracking through eBay. This service applies to specific Trading Cards categories (not all categories are supported), and to Coins & Paper Money, Postcards, and Stamps. See <a href=\"/api-docs/sell/static/seller-accounts/using-the-ebay-standard-envelope-service.html\" target=\"_blank\">Using the eBay standard envelope (eSE) service</a>.</p>  # noqa: E501

        :param FulfillmentPolicyRequest body: Request to create a seller account fulfillment policy. (required)
        :return: SetFulfillmentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'create_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_fulfillment_policy(self, fulfillment_policy_id, **kwargs):  # noqa: E501
        """delete_fulfillment_policy  # noqa: E501

        This method deletes a fulfillment policy. Supply the ID of the policy you want to delete in the <b>fulfillmentPolicyId</b> path parameter. Note that you cannot delete the default fulfillment policy.  # noqa: E501

        :param str fulfillment_policy_id: This path parameter specifies the ID of the fulfillment policy to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'delete_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], fulfillment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_fulfillment_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_fulfillment_policies  # noqa: E501

        This method retrieves all the fulfillment policies configured for the marketplace you specify using the <code>marketplace_id</code> query parameter.  <br><br><b>Marketplaces and locales</b>  <br><br>Get the correct policies for a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, get the policies for the French locale of the Canadian marketplace by specifying <code>fr-CA</code> for the <code>Content-Language</code> header. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>. For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\" target=\"_blank\">HTTP request headers</a>.  # noqa: E501

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policies you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :return: FulfillmentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'get_fulfillment_policies', SellAccountException, True, ['sell.account', 'fulfillment_policy'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_fulfillment_policy(self, fulfillment_policy_id, **kwargs):  # noqa: E501
        """get_fulfillment_policy  # noqa: E501

        This method retrieves the complete details of a fulfillment policy. Supply the ID of the policy you want to retrieve using the <b>fulfillmentPolicyId</b> path parameter.  # noqa: E501

        :param str fulfillment_policy_id: This path parameter specifies the ID of the fulfillment policy you want to retrieve. (required)
        :return: FulfillmentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'get_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], fulfillment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_fulfillment_policy_by_name(self, marketplace_id, name, **kwargs):  # noqa: E501
        """get_fulfillment_policy_by_name  # noqa: E501

        This method retrieves the complete details for a single fulfillment policy. In the request, supply both the policy <code>name</code> and its associated <code>marketplace_id</code> as query parameters.   <br><br><b>Marketplaces and locales</b>  <br><br>Get the correct policy for a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, get a policy for the French locale of the Canadian marketplace by specifying <code>fr-CA</code> for the <code>Content-Language</code> header. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>. For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.  # noqa: E501

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :param str name: This query parameter specifies the user-defined name of the fulfillment policy you want to retrieve. (required)
        :return: FulfillmentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'get_fulfillment_policy_by_name', SellAccountException, True, ['sell.account', 'fulfillment_policy'], (marketplace_id, name), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_fulfillment_policy(self, body, fulfillment_policy_id, **kwargs):  # noqa: E501
        """update_fulfillment_policy  # noqa: E501

        This method updates an existing fulfillment policy. Specify the policy you want to update using the <b>fulfillment_policy_id</b> path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload.  # noqa: E501

        :param FulfillmentPolicyRequest body: Fulfillment policy request (required)
        :param str fulfillment_policy_id: This path parameter specifies the ID of the fulfillment policy you want to update. (required)
        :return: SetFulfillmentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'update_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], (body, fulfillment_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_kyc(self, **kwargs):  # noqa: E501
        """get_kyc  # noqa: E501

        This method is used by sellers onboarded for eBay managed payments, or sellers who are currently going through, or who are eligible for onboarding for eBay managed payments. With this method, a seller can discover if there are any action items in regards to providing more documentation and/or information about themselves, their company, or the bank account they are or will be using for seller payouts. These 'action items' are also know as 'Know Your Customer' (or KYC) checks.<br><br>This method does not require any parameters other than the OAuth user token associated with the seller's account.<br><br>If the managed payments seller does not currently have any pending 'KYC' action items, only a <code>204 No Content</code> HTTP status code is returned, and no response payload. <br><br><span class=\"tablenote\"><b>Note</b>: This method is not applicable for sellers who are not eligible for eBay managed payments. For sellers who sell on one or more eBay marketplaces that currently support managed payments, they can check on their managed payments onboarding status by using the <a href=\"../../payments_program/onboarding/methods/getPaymentsProgramOnboarding\">getPaymentsProgramOnboarding</a> method. </span>  # noqa: E501

        :return: KycResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.KycApi, sell_account.ApiClient, 'get_kyc', SellAccountException, True, ['sell.account', 'kyc'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payments_program_onboarding(self, marketplace_id, payments_program_type, **kwargs):  # noqa: E501
        """get_payments_program_onboarding  # noqa: E501

        This method retrieves a seller's onboarding status of eBay managed payments for a specified marketplace. The overall onboarding status of the seller and the status of each onboarding step is returned. <p>Presently, the only supported payments program type is <code>EBAY_PAYMENTS</code>. See <a href=\"https://pages.ebay.com/seller-center/service-and-payments/managed-payments-on-ebay.html\" target=\"_blank\">Managed Payments on eBay</a> and <a href=\"https://pages.ebay.com/payment/2.0/terms.html\" target=\"_blank\">Payments Terms of Use</a>.</p><p> <span class=\"tablenote\"><strong>Note:</strong> Managed payments availability: <a href=\"/managed-payments\">eBay managed payments</a> is presently available in the US and Germany, and will roll out to Canada, UK, and Australia in July 2020.</span></p>  # noqa: E501

        :param str marketplace_id: The eBay marketplace ID associated with the onboarding status to retrieve. Only enums for marketplaces that support or will soon support eBay managed payments are allowed. Error 20408 is returned for any other eBay marketplace. No response payload is returned with this error. (required)
        :param str payments_program_type: The type of payments program whose status is returned by the call. Presently, the only supported payments program is <code>EBAY_PAYMENTS</code>. For details on the program, see <a href=\"https://pages.ebay.com/payment/2.0/terms.html\" target=\"_blank\">Payments Terms of Use</a>.  (required)
        :return: PaymentsProgramOnboardingResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.OnboardingApi, sell_account.ApiClient, 'get_payments_program_onboarding', SellAccountException, True, ['sell.account', 'onboarding'], (marketplace_id, payments_program_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_payment_policy(self, body, **kwargs):  # noqa: E501
        """create_payment_policy  # noqa: E501

        This method creates a new payment policy where the policy encapsulates seller's terms for purchase payments.  <br><br>Each policy targets a <b>marketplaceId</b> and <code>categoryTypes.</code><b>name</b> combination and you can create multiple policies for each combination. Be aware that some marketplaces require a specific payment policy for vehicle listings.  <br><br>A successful request returns the URI to the new policy in the <b>Location</b> response header and the ID for the new policy is returned in the response payload.  <p class=\"tablenote\"><b>Tip:</b> For details on creating and using the business policies supported by the Account API, see <a href=\"/api-docs/sell/static/seller-accounts/business-policies.html\">eBay business policies</a>.</p>  <p><b>Marketplaces and locales</b></p>  <p>Policy instructions can be localized by providing a locale in the <code>Accept-Language</code> HTTP request header. For example, the following setting displays field values from the request body in German: <code>Accept-Language: de-DE</code>.</p>  <p>Target the specific locale of a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, target the French locale of the Canadian marketplace by specifying the <code>fr-CA</code> locale for <code>Content-Language</code>. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>.</p> <p class=\"tablenote\"><b>Tip:</b> For details on headers, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.</p>  # noqa: E501

        :param PaymentPolicyRequest body: Payment policy request (required)
        :return: SetPaymentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'create_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_payment_policy(self, payment_policy_id, **kwargs):  # noqa: E501
        """delete_payment_policy  # noqa: E501

        This method deletes a payment policy. Supply the ID of the policy you want to delete in the <b>paymentPolicyId</b> path parameter. Note that you cannot delete the default payment policy.  # noqa: E501

        :param str payment_policy_id: This path parameter specifies the ID of the payment policy you want to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'delete_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], payment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payment_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_payment_policies  # noqa: E501

        This method retrieves all the payment policies configured for the marketplace you specify using the <code>marketplace_id</code> query parameter.  <br><br><b>Marketplaces and locales</b>  <br><br>Get the correct policies for a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, get the policies for the French locale of the Canadian marketplace by specifying <code>fr-CA</code> for the <code>Content-Language</code> header. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>. For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\" target=\"_blank\">HTTP request headers</a>.  # noqa: E501

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policies you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :return: PaymentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'get_payment_policies', SellAccountException, True, ['sell.account', 'payment_policy'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payment_policy(self, payment_policy_id, **kwargs):  # noqa: E501
        """get_payment_policy  # noqa: E501

        This method retrieves the complete details of a payment policy. Supply the ID of the policy you want to retrieve using the <b>paymentPolicyId</b> path parameter.  # noqa: E501

        :param str payment_policy_id: This path parameter specifies the ID of the payment policy you want to retrieve. (required)
        :return: PaymentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'get_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], payment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payment_policy_by_name(self, marketplace_id, name, **kwargs):  # noqa: E501
        """get_payment_policy_by_name  # noqa: E501

        This method retrieves the complete details of a single payment policy. Supply both the policy <code>name</code> and its associated <code>marketplace_id</code> in the request query parameters.   <br><br><b>Marketplaces and locales</b>  <br><br>Get the correct policy for a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, get a policy for the French locale of the Canadian marketplace by specifying <code>fr-CA</code> for the <code>Content-Language</code> header. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>. For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.  # noqa: E501

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :param str name: This query parameter specifies the user-defined name of the payment policy you want to retrieve. (required)
        :return: PaymentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'get_payment_policy_by_name', SellAccountException, True, ['sell.account', 'payment_policy'], (marketplace_id, name), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_payment_policy(self, body, payment_policy_id, **kwargs):  # noqa: E501
        """update_payment_policy  # noqa: E501

        This method updates an existing payment policy. Specify the policy you want to update using the <b>payment_policy_id</b> path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload.  # noqa: E501

        :param PaymentPolicyRequest body: Payment policy request (required)
        :param str payment_policy_id: This path parameter specifies the ID of the payment policy you want to update. (required)
        :return: SetPaymentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'update_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], (body, payment_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payments_program(self, marketplace_id, payments_program_type, **kwargs):  # noqa: E501
        """get_payments_program  # noqa: E501

        This method returns whether or not the user is opted-in to the specified payments program. Sellers opt-in to payments programs by marketplace and you use the <b>marketplace_id</b> path parameter to specify the marketplace of the status flag you want returned.  <br><br><span class=\"tablenote\"><b>Note:</b> Currently, the only supported payments program is <b>eBay Payments</b>. For details, see: <ul><li><a href=\"https://pages.ebay.com/seller-center/service-and-payments/managed-payments-on-ebay.html\" target=\"_blank\">Managed Payments on eBay</a></li> <li><a href=\"https://pages.ebay.com/payment/2.0/terms.html\" target=\"_blank\">Payments Terms of Use</a></li></ul></span>  # noqa: E501

        :param str marketplace_id: This path parameter specifies the eBay marketplace of the payments program for which you want to retrieve the seller's status. (required)
        :param str payments_program_type: This path parameter specifies the payments program whose status is returned by the call.  <br><br>Currently the only supported payments program is <code>EBAY_PAYMENTS</code>. For details on the program, see <a href=\"https://pages.ebay.com/payment/2.0/terms.html\" target=\"_blank\">Payments Terms of Use</a>. (required)
        :return: PaymentsProgramResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentsProgramApi, sell_account.ApiClient, 'get_payments_program', SellAccountException, True, ['sell.account', 'payments_program'], (marketplace_id, payments_program_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_privileges(self, **kwargs):  # noqa: E501
        """get_privileges  # noqa: E501

        This method retrieves the seller's current set of privileges. The call returns whether or not the seller's eBay registration has been completed, as well as the details of their site-wide <b>sellingLimit</b> (the amount and quantity they can sell on a given day).  # noqa: E501

        :return: SellingPrivileges
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PrivilegeApi, sell_account.ApiClient, 'get_privileges', SellAccountException, True, ['sell.account', 'privilege'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_opted_in_programs(self, **kwargs):  # noqa: E501
        """get_opted_in_programs  # noqa: E501

        This method gets a list of the seller programs that the seller has opted-in to.  # noqa: E501

        :return: Programs
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ProgramApi, sell_account.ApiClient, 'get_opted_in_programs', SellAccountException, True, ['sell.account', 'program'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_opt_in_to_program(self, body, **kwargs):  # noqa: E501
        """opt_in_to_program  # noqa: E501

        This method opts the seller in to an eBay seller program. Refer to the <a href=\"/api-docs/sell/account/overview.html#opt-in\" target=\"_blank\">Account API overview</a> for information about available eBay seller programs.<br /><br /><span class=\"tablenote\"><b>Note:</b> It can take up to 24-hours for eBay to process your request to opt-in to a Seller Program. Use the <a href=\"/api-docs/sell/account/resources/program/methods/getOptedInPrograms\" target=\"_blank\">getOptedInPrograms</a> call to check the status of your request after the processing period has passed.</span>  # noqa: E501

        :param Program body: Program being opted-in to. (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ProgramApi, sell_account.ApiClient, 'opt_in_to_program', SellAccountException, True, ['sell.account', 'program'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_opt_out_of_program(self, body, **kwargs):  # noqa: E501
        """opt_out_of_program  # noqa: E501

        This method opts the seller out of a seller program to which you have previously opted-in to. Get a list of the seller programs you have opted-in to using the <b>getOptedInPrograms</b> call.  # noqa: E501

        :param Program body: Program being opted-out of. (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ProgramApi, sell_account.ApiClient, 'opt_out_of_program', SellAccountException, True, ['sell.account', 'program'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_rate_tables(self, **kwargs):  # noqa: E501
        """get_rate_tables  # noqa: E501

        This method retrieves a seller's <i>shipping rate tables</i> for the country specified in the <b>country_code</b> query parameter. If you call this method without specifying a country code, the call returns all the seller's shipping rate tables.  <br><br>The method's response includes a <b>rateTableId</b> for each table defined by the seller. Use a table's ID value in a fulfillment policy to specify the shipping rate table to use for that policy's DOMESTIC or INTERNATIONAL shipping option (make sure the <b>locality</b> of the rate table matches the <b>optionType</b> of the shipping option).  <br><br>This call currently supports getting rate tables related to the following marketplaces:<ul><li><code>EBAY_AU</code></li> <li><code>EBAY_CA</code></li> <li><code>EBAY_DE</code></li> <li><code>EBAY_ES</code></li> <li><code>EBAY_FR</code></li> <li><code>EBAY_GB</code></li> <li><code>EBAY_IT</code></li> <li><code>EBAY_US</code></li></ul>  <span class=\"tablenote\"><b>Note:</b> Rate tables created with the Trading API might not have been assigned a <b>rateTableId</b> at the time of their creation. This method can assign and return <b>rateTableId</b> values for rate tables with missing IDs if you make a request using the <b>country_code</b> where the seller has defined rate tables.</span>  <br><br>Sellers can define up to 40 shipping rate tables for their account, which lets them set up different rate tables for each of the marketplaces they sell into. Go to <b>My eBay > Account > Site Preferences</b> to create and maintain the rate tables. For more, see <a href=\"https://pages.ebay.com/help/pay/shipping-costs.html#tables\">Using shipping rate tables</a>.  <p>If you're using the Trading API, use the rate table ID values in the <b>RateTableDetails</b> container of the Add/Revise/Relist calls. If the <b>locality</b> for a rate table is set to <code>DOMESTIC</code>, pass the ID value in the <b>RateTableDetails.DomesticRateTableId</b> field. Otherwise, if <b>locality</b> is <code>INTERNATIONAL</code>, pass the ID value in <b>RateTableDetails.InternationalRateTableId</b>.</p>  # noqa: E501

        :param str country_code: This query parameter specifies the two-letter <a href=\"https://www.iso.org/iso-3166-country-codes.html\" title=\"https://www.iso.org\" target=\"_blank\">ISO 3166</a> code of country for which you want shipping-rate table information. If you do not specify a county code, the request returns all the seller-defined rate tables. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:CountryCodeEnum
        :return: RateTableResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.RateTableApi, sell_account.ApiClient, 'get_rate_tables', SellAccountException, True, ['sell.account', 'rate_table'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_return_policy(self, body, **kwargs):  # noqa: E501
        """create_return_policy  # noqa: E501

        This method creates a new return policy where the policy encapsulates seller's terms for returning items. Use the Metadata API method <b>getReturnPolicies</b> to determine which categories require you to supply a return policy for the marketplace(s) into which you list.  <br><br>Each policy targets a <b>marketplaceId</b> and <code>categoryTypes.</code><b>name</b> combination and you can create multiple policies for each combination.  <br><br>A successful request returns the URI to the new policy in the <b>Location</b> response header and the ID for the new policy is returned in the response payload.  <p class=\"tablenote\"><b>Tip:</b> For details on creating and using the business policies supported by the Account API, see <a href=\"/api-docs/sell/static/seller-accounts/business-policies.html\">eBay business policies</a>.</p>  <p><b>Marketplaces and locales</b></p>  <p>Policy instructions can be localized by providing a locale in the <code>Accept-Language</code> HTTP request header. For example, the following setting displays field values from the request body in German: <code>Accept-Language: de-DE</code>.</p>  <p>Target the specific locale of a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, target the French locale of the Canadian marketplace by specifying the <code>fr-CA</code> locale for <code>Content-Language</code>. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>.</p> <p class=\"tablenote\"><b>Tip:</b> For details on headers, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.</p>  # noqa: E501

        :param ReturnPolicyRequest body: Return policy request (required)
        :return: SetReturnPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'create_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_return_policy(self, return_policy_id, **kwargs):  # noqa: E501
        """delete_return_policy  # noqa: E501

        This method deletes a return policy. Supply the ID of the policy you want to delete in the <b>returnPolicyId</b> path parameter. Note that you cannot delete the default return policy.  # noqa: E501

        :param str return_policy_id: This path parameter specifies the ID of the return policy you want to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'delete_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], return_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_return_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_return_policies  # noqa: E501

        This method retrieves all the return policies configured for the marketplace you specify using the <code>marketplace_id</code> query parameter.  <br><br><b>Marketplaces and locales</b>  <br><br>Get the correct policies for a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, get the policies for the French locale of the Canadian marketplace by specifying <code>fr-CA</code> for the <code>Content-Language</code> header. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>. For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\" target=\"_blank\">HTTP request headers</a>.  # noqa: E501

        :param str marketplace_id: This query parameter specifies the ID of the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :return: ReturnPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'get_return_policies', SellAccountException, True, ['sell.account', 'return_policy'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_return_policy(self, return_policy_id, **kwargs):  # noqa: E501
        """get_return_policy  # noqa: E501

        This method retrieves the complete details of the return policy specified by the <b>returnPolicyId</b> path parameter.  # noqa: E501

        :param str return_policy_id: This path parameter specifies the of the return policy you want to retrieve. (required)
        :return: ReturnPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'get_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], return_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_return_policy_by_name(self, marketplace_id, name, **kwargs):  # noqa: E501
        """get_return_policy_by_name  # noqa: E501

        This method retrieves the complete details of a single return policy. Supply both the policy <code>name</code> and its associated <code>marketplace_id</code> in the request query parameters.   <br><br><b>Marketplaces and locales</b>  <br><br>Get the correct policy for a marketplace that supports multiple locales using the <code>Content-Language</code> request header. For example, get a policy for the French locale of the Canadian marketplace by specifying <code>fr-CA</code> for the <code>Content-Language</code> header. Likewise, target the Dutch locale of the Belgium marketplace by setting <code>Content-Language: nl-BE</code>. For details on header values, see <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a>.  # noqa: E501

        :param str marketplace_id: This query parameter specifies the ID of the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :param str name: This query parameter specifies the user-defined name of the return policy you want to retrieve. (required)
        :return: ReturnPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'get_return_policy_by_name', SellAccountException, True, ['sell.account', 'return_policy'], (marketplace_id, name), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_return_policy(self, body, return_policy_id, **kwargs):  # noqa: E501
        """update_return_policy  # noqa: E501

        This method updates an existing return policy. Specify the policy you want to update using the <b>return_policy_id</b> path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload.  # noqa: E501

        :param ReturnPolicyRequest body: Container for a return policy request. (required)
        :param str return_policy_id: This path parameter specifies the ID of the return policy you want to update. (required)
        :return: SetReturnPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'update_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], (body, return_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_or_replace_sales_tax(self, body, country_code, jurisdiction_id, **kwargs):  # noqa: E501
        """create_or_replace_sales_tax  # noqa: E501

        This method creates or updates a sales tax table entry for a jurisdiction. Specify the tax table entry you want to configure using the two path parameters: <b>countryCode</b> and <b>jurisdictionId</b>.  <br><br>A tax table entry for a jurisdiction is comprised of two fields: one for the jurisdiction's sales-tax rate and another that's a boolean value indicating whether or not shipping and handling are taxed in the jurisdiction.  <br><br>You can set up <i>tax tables</i> for countries that support different <i>tax jurisdictions</i>. Currently, only Canada, India, and the US support separate tax jurisdictions. If you sell into any of these countries, you can set up tax tables for any of the country's jurisdictions. Retrieve valid jurisdiction IDs using <b>getSalesTaxJurisdictions</b> in the Metadata API.  <br><br>For details on using this call, see <a href=\"/api-docs/sell/static/seller-accounts/tax-tables.html\">Establishing sales-tax tables</a>. <br><br><span class=\"tablenote\"><b>Important!</b> Starting in January 2019, eBay will begin to calculate, collect, and remit sales tax on behalf of sellers for items shipped to customers. This feature is rolling out on specific dates to specific US states as defined on the following page: <a href=\"https://www.ebay.com/help/selling/fees-credits-invoices/taxes-import-charges?id=4121#section4\" target=\"_balnk\">eBay sales tax collection</a>. <br><br>Once eBay starts to collect sales tax for a state, no action is required on the seller's part and there will be no charges or fees for eBay automatically calculating, collecting and remitting sales tax. The sales-tax collection process will apply to all the sales in the states that support this feature, whether the seller is located in or outside of the United States.  <br><br>When a buyer purchases an item on eBay, and the ship-to address is one of the states where eBay collects the sales tax, eBay will calculate and add the applicable sales tax at checkout. The buyer will pay both the cost of the item along with the sales tax. eBay will collect and remit the tax.</span>  # noqa: E501

        :param SalesTaxBase body: A container that describes the how the sales tax is calculated. (required)
        :param str country_code: This path parameter specifies the two-letter <a href=\"https://www.iso.org/iso-3166-country-codes.html\" title=\"https://www.iso.org\" target=\"_blank\">ISO 3166</a> code for the country for which you want to create tax table entry. (required)
        :param str jurisdiction_id: This path parameter specifies the ID of the sales-tax jurisdiction for the table entry you want to create. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'create_or_replace_sales_tax', SellAccountException, True, ['sell.account', 'sales_tax'], (body, country_code, jurisdiction_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_sales_tax(self, country_code, jurisdiction_id, **kwargs):  # noqa: E501
        """delete_sales_tax  # noqa: E501

        This call deletes a tax table entry for a jurisdiction. Specify the jurisdiction to delete using the <b>countryCode</b> and <b>jurisdictionId</b> path parameters.  # noqa: E501

        :param str country_code: This path parameter specifies the two-letter <a href=\"https://www.iso.org/iso-3166-country-codes.html\" title=\"https://www.iso.org\" target=\"_blank\">ISO 3166</a> code for the country whose tax table entry you want to delete. (required)
        :param str jurisdiction_id: This path parameter specifies the ID of the sales tax jurisdiction whose table entry you want to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'delete_sales_tax', SellAccountException, True, ['sell.account', 'sales_tax'], (country_code, jurisdiction_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_sales_tax(self, country_code, jurisdiction_id, **kwargs):  # noqa: E501
        """get_sales_tax  # noqa: E501

        This call gets the current tax table entry for a specific tax jurisdiction. Specify the jurisdiction to retrieve using the <b>countryCode</b> and <b>jurisdictionId</b> path parameters.  # noqa: E501

        :param str country_code: This path parameter specifies the two-letter <a href=\"https://www.iso.org/iso-3166-country-codes.html\" title=\"https://www.iso.org\" target=\"_blank\">ISO 3166</a> code for the country whose tax table you want to retrieve. (required)
        :param str jurisdiction_id: This path parameter specifies the ID of the sales tax jurisdiction for the tax table entry you want to retrieve. (required)
        :return: SalesTax
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'get_sales_tax', SellAccountException, True, ['sell.account', 'sales_tax'], (country_code, jurisdiction_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_sales_taxes(self, country_code, **kwargs):  # noqa: E501
        """get_sales_taxes  # noqa: E501

        Use this call to retrieve a sales tax table that the seller established for a specific country. Specify the tax table to retrieve using the <code>country_code</code> query parameter.  # noqa: E501

        :param str country_code: This path parameter specifies the two-letter <a href=\"https://www.iso.org/iso-3166-country-codes.html\" title=\"https://www.iso.org\" target=\"_blank\">ISO 3166</a> code for the country whose tax table you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:CountryCodeEnum (required)
        :return: SalesTaxes
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'get_sales_taxes', SellAccountException, True, ['sell.account', 'sales_tax'], country_code, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_get_customer_service_metric(self, customer_service_metric_type, evaluation_marketplace_id, evaluation_type, **kwargs):  # noqa: E501
        """get_customer_service_metric  # noqa: E501

        Use this method to retrieve a seller's performance and rating for the customer service metric.  <br><br>Control the response from the <b>getCustomerServiceMetric</b> method using the following path and query parameters: <ul><li><b>customer_service_metric_type</b> controls the type of customer service transactions evaluated for the metric rating.</li> <li><b>evaluation_type</b> controls the period you want to review.</li> <li><b>evaluation_marketplace_id</b> specifies the target marketplace for the evaluation.</li></ul> Currently, metric data is returned for only peer benchmarking. For details on the workings of peer benchmarking, see <a href=\"https://www.ebay.com/help/policies/selling-policies/seller-performance-policy/service-metrics-policy?id=4769\" title=\"eBay Help pages\" target=\"_blank\">Service metrics policy</a>.  <br><br>For details on using and understanding the response from this method, see <a href=\"/api-docs/sell/static/performance/customer-service-metric.html\" title=\"Selling Integration Guide\">Interpreting customer service metric ratings</a>.  # noqa: E501

        :param str customer_service_metric_type: Use this path parameter to specify the type of customer service metrics and benchmark data you want returned for the seller. Supported types are: <ul><li><code>ITEM_NOT_AS_DESCRIBED</code></li><li><code>ITEM_NOT_RECEIVED</code></li></ul> (required)
        :param str evaluation_marketplace_id: Use this query parameter to specify the Marketplace ID to evaluate for the customer service metrics and benchmark data.  <br><br>For the list of supported marketplaces, see <a href=\"/api-docs/sell/analytics/static/overview.html#requirements\" title=\"Analytics API Overview\" target=\"_blank\">Analytics API requirements and restrictions</a>. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/analytics/types/bas:MarketplaceIdEnum (required)
        :param str evaluation_type: Use this path parameter to specify the type of the seller evaluation you want returned, either: <ul><li><code>CURRENT</code> &ndash; A monthly evaluation that occurs on the 20th of every month.</li> <li><code>PROJECTED</code> &ndash; A daily evaluation that provides a projection of how the seller is currently performing with regards to the upcoming evaluation period.</li></ul> (required)
        :return: GetCustomerServiceMetricResponse
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.CustomerServiceMetricApi, sell_analytics.ApiClient, 'get_customer_service_metric', SellAnalyticsException, True, ['sell.analytics', 'customer_service_metric'], (customer_service_metric_type, evaluation_marketplace_id, evaluation_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_find_seller_standards_profiles(self, **kwargs):  # noqa: E501
        """find_seller_standards_profiles  # noqa: E501

        This call retrieves all the standards profiles for the associated seller.  <br><br>A <i>standards profile </i> is a set of eBay seller metrics and the seller's associated compliance values (either <code>TOP_RATED</code>, <code>ABOVE_STANDARD</code>, or <code>BELOW_STANDARD</code>).  <br><br>A seller's multiple profiles are distinguished by two criteria, a \"program\" and a \"cycle.\" A profile's <i>program </i> is one of three regions where the seller may have done business, or <code>PROGRAM_GLOBAL</code> to indicate all marketplaces where the seller has done business. The <i>cycle</i> value specifies whether the standards compliance values were determined at the last official eBay evaluation or at the time of the request.  # noqa: E501

        :return: FindSellerStandardsProfilesResponse
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.SellerStandardsProfileApi, sell_analytics.ApiClient, 'find_seller_standards_profiles', SellAnalyticsException, True, ['sell.analytics', 'seller_standards_profile'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_get_seller_standards_profile(self, cycle, program, **kwargs):  # noqa: E501
        """get_seller_standards_profile  # noqa: E501

        This call retrieves a single standards profile for the associated seller.  <br><br>A <i>standards profile </i> is a set of eBay seller metrics and the seller's associated compliance values (either <code>TOP_RATED</code>, <code>ABOVE_STANDARD</code>, or <code>BELOW_STANDARD</code>).  <br><br>A seller can have multiple profiles distinguished by two criteria, a \"program\" and a \"cycle.\" A profile's <i>program </i> is one of three regions where the seller may have done business, or <code>PROGRAM_GLOBAL</code> to indicate all marketplaces where the seller has done business. The <i>cycle</i> value specifies whether the standards compliance values were determined at the last official eBay evaluation (<code>CURRENT</code>) or at the time of the request (<code>PROJECTED</code>). Both cycle and a program values are required URI parameters for this method.  # noqa: E501

        :param str cycle: The period covered by the returned standards profile evaluation.  <br><br>Supply one of two values, <code>CURRENT</code> means the response reflects eBay's most recent monthly standards evaluation and <code>PROJECTED</code> means the response reflect the seller's projected monthly evaluation, as calculated at the time of the request. (required)
        :param str program: This input value specifies the region used to determine the seller's standards profile.  <br><br>Supply one of the four following values, <code>PROGRAM_DE</code>, <code>PROGRAM_UK</code>, <code>PROGRAM_US</code>, or <code>PROGRAM_GLOBAL</code>. (required)
        :return: StandardsProfile
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.SellerStandardsProfileApi, sell_analytics.ApiClient, 'get_seller_standards_profile', SellAnalyticsException, True, ['sell.analytics', 'seller_standards_profile'], (cycle, program), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_get_traffic_report(self, **kwargs):  # noqa: E501
        """get_traffic_report  # noqa: E501

        This method returns a report that details the user traffic received by a seller's listings. <br><br>A traffic report gives sellers the ability to review how often their listings appeared on eBay, how many times their listings are viewed, and how many purchases were made. The report also returns the report's start and end dates, and the date the information was last updated.  <br><br>When using this call: <ul><li>Be sure to URL-encode the values you pass in query parameters, as described in <a href=\"/api-docs/static/rest-request-components.html#parameters\">URI parameters</a>. See the request samples below for details.</li> <li>You can only specify a single metric in the <b>sort</b> parameter and the specified metric must be listed in the <b>metric</b> parameter of your request.</li> <li>Parameter names are case sensitive, but metric names are not. <p>For example, the following are <i>correct</i>:</p> <ul><li><code>sort=LISTING_IMPRESSION_TOTAL</code></li> <li><code>sort=listing_impression_total</code></li> <li><code>metric=listing_impression_total</code></li></ul> However, these are <i>incorrect</i>: <ul><li><code>SORT=LISTING_IMPRESSION_TOTAL</code></li> <li><code>SORT=listing_impression_total</code></li> <li><code>Metric=listing_impression_total</code></li></ul></ul> For more information, see <a href=\"/api-docs/sell/static/performance/traffic-report.html\">Traffic report details</a><br /><br /><span class=\"tablenote\"><b>Note:</b> Beginning on October 4, 2021, the options for the following <b>metric</b> inputs will change:<ul><li>Sorting on the <b>SALES_CONVERSION_RATE</b> metric will no longer be supported</li><li>Sorting on the <b>TRANSACTION</b> metric will no longer support ascending order; only descending order will be supported</li><li><b>LISTING_VIEWS_SOURCE_DIRECT</b> will only support a 90-day query range from October 4, 2021 until early January 2022, at which time it will again support a two year query range.</li></ul></span>  # noqa: E501

        :param str dimension: This query parameter specifies the <i>dimension</i>, or \"attribute,\" that is applied to the report <b>metric</b>.  <br><br><b>Valid values:</b> <code>DAY</code> or <code>LISTING</code>  <br><br><b>Examples</b> <ul><li>If you specify <code>dimension=DAY</code> and <code>metric=CLICK_THROUGH_RATE</code>, the traffic report contains the number of times an item displayed on a search results page and the buyer clicked through to the View Item page for each day in the date range, as in: <br><code>12-06-17: 32, 12-07-17: 54, ...</code></li> <li>If you specify <code>dimension=LISTING</code> and <code>metric=LISTING_IMPRESSION_STORE</code>, the traffic report contains the number of times that listing appeared on the seller's store during the specified date range. <br><br>For example, <code>LISTING_IMPRESSION_STORE: 157</code> means the item appeared 157 times in the store during the date range.</li></ul> <!-- Dimension - Enables user to specify input to slice the data that the user is interested in - For example specify listing and days as dimensions to get traffic report for all the sellers listings grouped by listing and days. Refer to DimensionEnum) -->
        :param str filter: This query parameter refines the information returned in the traffic report.  <br><br>Configure the following properties of the <b>filter</b> parameter to tune the traffic report to your needs: <ul> <li><b>date_range</b> <br>Limits the report to the specified range of dates.  <br><br>Format the date range by enclosing the earliest date and end date for the report in brackets (\"<code>[ ]</code>\"), as follows: <br><code>[YYYYMMDD..YYYYMMDD]</code>  <br><br>The maximum range between the start and end dates is 90 days, and the earliest start date you can specify is two years prior to the current date, which is defined as 730 days (365 &#42; 2), not accounting for Leap Year.  <br><br><a name=\"lastUDate\"></a>The last date for which traffic data exists is a value called <b>lastUpdatedDate</b>. eBay returns an error if you specify a date range greater than 90 days, or the start date is after the lastUpdatedDate. If the specified end date is beyond the lastUpdatedDate, eBay returns data up to the lastUpdatedDate.  <br><br><b>Required:</b> Always</li> <li><b>listing_ids</b> <br>This filter limits the results to only the supplied list of <b>listingId</b> values. <br><br>You can specify to 200 different <b>listingId</b> values. Enclose the list of IDs with curly braces (\"<code>{ }</code>\"), and separate multiple values with a pipe character (\"<code>|</code>\").  <br><br>This filter only returns data for listings that have been either active or sold in last 90 days, and any unsold listings in the last 30 days. All listings must be the seller's and they  must be listed on the marketplace specified by the <b>marketplace_ids</b> filter argument.</li> <li><b>marketplace_ids</b> <br>This filter limits the report to seller data related to only the specified marketplace ID (currently the filter allows only a single marketplace ID). Enclose the marketplace ID in curly braces (\"<code>{ }</code>\").  <br><br><b>Valid values:</b> <ul class=\"compact\"><li><code>EBAY_AU</code></li> <li><code>EBAY_DE</code></li> <li><code>EBAY_GB</code></li> <li><code>EBAY_US</code></li> <li><code>EBAY_MOTORS</code></li></ul> <br><b>Required if</b> you set the <b>dimension</b> parameter to <code>DAY</code>.</li></ul> <br><b>Example filter parameter</b> <br>The following example shows how to configure the <b>filter</b> parameter with the <b>marketplace_ids</b> and <b>date_range</b> filters: <p><code>filter=marketplace_ids:{EBAY_US},date_range:[20170601..20170828]</code> <p><span class=\"tablenote\"><b>Note: </b> You must URL encode all the values you supply in the <b>filter</b> parameter, as described in <a href=\"/api-docs/static/rest-request-components.html#parameters\">URL parameters</a>.</span></p> <!-- **Filter results based on the specified filter parameters- window_days (WindowDaysEnum), date_range, marketplace_id (MarketplaceIdEnum - Only EBAY_US, EBAY_MOTORS_US, EBAY_GB, EBAY_AU, EBAY_DE are supported), listing_ids, traffic_source (Takes a list. Supported values: ORGANIC, PROMOTED_LISTINGS). Valid filters come from QueryParamEnum --> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/analytics/types/csb:FilterField
        :param str metric: <a name=\"metrics\"></a>This query parameter specifies the metrics you want covered in the report.  <br><br>Specify a comma-separated list of the metrics you want included in the report.  <br><br><b>Valid values:</b><ul> <li><b>CLICK_THROUGH_RATE</b>  <br>The number of times an item displays on the search results page divided by the number of times buyers clicked through to its View Item page. <br><b>Localized name: </b> Click through rate</li> <li><b>LISTING_IMPRESSION_SEARCH_RESULTS_PAGE </b> <br>The number of times the seller's listings displayed on the search results page. Note, the listing might not have been visible to the buyer due to its position on the page. <br><b>Localized name: </b> Listing impressions from the search results page</li> <li><b>LISTING_IMPRESSION_STORE </b> <br> The number of times the seller's listings displayed on the seller's store. Note, the listing might not have been visible to the buyer due to its position on the page. <br><b>Localized name: </b> Listing impressions from your Store</li> <li><b>LISTING_IMPRESSION_TOTAL</b>  <br> The total number of times the seller's listings displayed on the search results page OR in the seller's store. The item is counted each time it displays on either page. However, the listing might not have been visible to the buyer due to its position on the page. <br>This is a combination of:  LISTING_IMPRESSION_SEARCH_RESULTS_PAGE <b>+</b> LISTING_IMPRESSION_STORE. <br><b>Localized name: </b> Total listing impressions</li> <li><b>LISTING_VIEWS_SOURCE_DIRECT</b> <br> The number of times a View Item page was directly accessed, such as when a buyer navigates to the page using a bookmark.<br><b>Localized name: </b> Direct views</li> <li><b> LISTING_VIEWS_SOURCE_OFF_EBAY</b>  <br>The number of times a View Item page was accessed via a site other than eBay, such as when a buyer clicks on a link to the listing from a search engine page. <br><b>Localized name: </b> Off eBay views</li> <li><b>LISTING_VIEWS_SOURCE_OTHER_EBAY</b>  <br> The number of times a View Item page was accessed from an eBay page that is not either the search results page or the seller's store. <br><b>Localized name: </b>Views from non-search and non-store pages within eBay</li> <li><b>LISTING_VIEWS_SOURCE_SEARCH_RESULTS_PAGE</b>  <br> The number of times the item displayed on the search results page. <br><b>Localized name: </b> Views on the search results page</li> <li><b>LISTING_VIEWS_SOURCE_STORE</b>  <br> The number of times a View Item page was accessed via the seller's store. <br><b>Localized name: </b> Views from your Store</li> <li><b>LISTING_VIEWS_TOTAL </b> <br> Total number of listings viewed. <br>This number sums: <br>LISTING_VIEWS_SOURCE_DIRECT <br> LISTING_VIEWS_SOURCE_OFF_EBAY <br>LISTING_VIEWS_SOURCE_OTHER_EBAY <br>LISTING_VIEWS_SOURCE_SEARCH_RESULTS_PAGE <br>LISTING_VIEWS_SOURCE_STORE. <br><b>Localized name: </b> Total views</li> <li><b>SALES_CONVERSION_RATE</b> <br>The number of completed transactions divided by the number of View Item page views. Equals: <br>TRANSACTION <b>/</b> LISTING_VIEWS_TOTAL <br><b>Localized name: </b> Sales conversion rate</li> <li><b>TRANSACTION</b>  <br>The total number of completed transactions. <br><b>Localized name: </b> Transaction count</li></ul> <!-- Metric - Lets the user specify the list of fields that they would like to see in the report. Allowed values: LISTING_IMPRESSION_SEARCH_RESULTS_PAGE, LISTING_IMPRESSION_STORE, LISTING_IMPRESSION_TOTAL, LISTING_VIEWS_SOURCE_SEARCH_RESULTS_PAGE, LISTING_VIEWS_SOURCE_STORE, LISTING_VIEWS_SOURCE_DIRECT, LISTING_VIEWS_SOURCE_OTHER_EBAY, LISTING_VIEWS_SOURCE_OFF_EBAY, LISTING_VIEWS_TOTAL, TRANSACTION_TOTAL, CLICK_THROUGH_RATE, SALES_CONVERSION_RATE (DataMetricEnum) -->
        :param str sort: This query parameter sorts the report on the specified metric.  <br><br>The metric you specify must be included in the configuration of the report's <a href=\"#metrics\">metric</a> parameter.  <br><br>Sorting is helpful when you want to review how a specific metric is performing, such as the CLICK_THROUGH_RATE.  <br><br>Reports can be sorted in ascending or descending order. Precede the value of a descending-order request with a minus sign (\"<code>-</code>\"), for example: <code>sort=-CLICK_THROUGH_RATE</code>.<br /><br /><span class=\"tablenote\"><b>Note:</b> Beginning on October 4, 2021, the options for the following <b>metric</b> inputs will change:<ul><li>Sorting on the <b>SALES_CONVERSION_RATE</b> metric will no longer be supported</li><li>Sorting on the <b>TRANSACTION</b> metric will no longer support ascending order; only descending order will be supported</li><li><b>LISTING_VIEWS_SOURCE_DIRECT</b> will only support a 90-day query range from October 4, 2021 until early January 2022, at which time it will again support a two year query range.</li></ul></span><!-- Sort order for a collection of resources: Specify the metric value to be sorted. Allowed values are from DataMetricEnum --> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/analytics/types/csb:SortField
        :return: Report
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.TrafficReportApi, sell_analytics.ApiClient, 'get_traffic_report', SellAnalyticsException, True, ['sell.analytics', 'traffic_report'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_compliance_get_listing_violations(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_listing_violations  # noqa: E501

        This call returns specific listing violations for the supported listing compliance types. Only one compliance type can be passed in per call, and the response will include all the listing violations for this compliance type, and listing violations are grouped together by eBay listing ID. See ComplianceTypeEnum for more information on the supported listing compliance types. This method also has pagination control. Note: A maximum of 2000 listing violations will be returned in a result set. If the seller has more than 2000 listing violations, some/all of those listing violations must be corrected before additional listing violations will be retrieved. The user should pay attention to the total value in the response. If this value is '2000', it is possible that the seller has more than 2000 listing violations, but this field maxes out at 2000. Note: In a future release of this API, the seller will be able to pass in a specific eBay listing ID as a query parameter to see if this specific listing has any violations. Note: Only mocked non-compliant listing data will be returned for this call in the Sandbox environment, and not specific to the seller. However, the user can still use this mock data to experiment with the compliance type filters and pagination control.  # noqa: E501

        :param str x_ebay_c_marketplace_id: This header is required and is used to specify the eBay marketplace identifier. Supported values for this header can be found in the MarketplaceIdEnum type definition. Note that Version 1.4.0 of the Compliance API is only supported on the US, UK, Australia, Canada {English), and Germany sites. (required)
        :param str compliance_type: A seller uses this query parameter to retrieve listing violations of a specific compliance type. Only one compliance type value should be passed in here. See ComplianceTypeEnum for more information on the compliance types that can be passed in here. If the listing_id query parameter is used, the compliance_type query parameter {if passed in) will be ignored. This is because all of a listing's policy violations {each compliance type) will be returned if a listing_id is provided. Either the listing_id or a compliance_type query parameter must be used, and if the seller only wants to view listing violations of a specific compliance type, both of these parameters can be used. Note: The listing_id query parameter is not yet available for use, so the seller does not have the ability to retrieve listing violations for one or more specific listings. Until the listing_id query parameter becomes available, the compliance_type query parameter is required with each getListingViolations call.
        :param str offset: The integer value input into this field controls the first listing violation in the result set that will be displayed at the top of the response. The offset and limit query parameters are used to control the pagination of the output. For example, if offset is set to 10 and limit is set to 10, the call retrieves listing violations 11 thru 20 from the resulting set of violations. Note: This feature employs a zero-based index, where the first item in the list has an offset of 0. If the listing_id parameter is included in the request, this parameter will be ignored. Default: 0 {zero)
        :param str listing_id: Note: This query parameter is not yet supported for the Compliance API. Please note that until this query parameter becomes available, the compliance_type query parameter is required with each getListingViolations call. This query parameter is used if the user wants to view all listing violations for one or more eBay listings. The string value passed into this field is the unique identifier of the listing, sometimes referred to as the Item ID. Either the listing_id or a compliance_type query parameter must be used, and if the seller only wants to view listing violations of a specific compliance type, both of these parameters can be used. Up to 50 listing IDs can be specified with this query parameter, and each unique listing ID is separated with a comma.
        :param str limit: This query parameter is used if the user wants to set a limit on the number of listing violations that are returned on one page of the result set. This parameter is used in conjunction with the offset parameter to control the pagination of the output. For example, if offset is set to 10 and limit is set to 10, the call retrieves listing violations 11 thru 20 from the collection of listing violations that match the value set in the compliance_type parameter. Note: This feature employs a zero-based index, where the first item in the list has an offset of 0. If the listing_id parameter is included in the request, this parameter will be ignored. Default: 100 Maximum: 200
        :param str filter: This filter allows a user to retrieve only listings that are currently out of compliance, or only listings that are at risk of becoming out of compliance. Although other filters may be added in the future, complianceState is the only supported filter type at this time. The two compliance 'states' are OUT_OF_COMPLIANCE and AT_RISK. Below is an example of how to set up this compliance state filter. Notice that the filter type and filter value are separated with a colon (:) character, and the filter value is wrapped with curly brackets. filter=complianceState:{OUT_OF_COMPLIANCE}
        :return: PagedComplianceViolationCollection
        """
        try:
            return self._method_paged(sell_compliance.Configuration, '/sell/compliance/v1', sell_compliance.ListingViolationApi, sell_compliance.ApiClient, 'get_listing_violations', SellComplianceException, True, ['sell.compliance', 'listing_violation'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_compliance_suppress_violation(self, body, **kwargs):  # noqa: E501
        """suppress_violation  # noqa: E501

        This call suppresses a listing violation for a specific listing. Only listing violations in the AT_RISK state (returned in the violations.complianceState field of the getListingViolations call) can be suppressed. Note: At this time, the suppressViolation call only supports the suppressing of ASPECTS_ADOPTION listing violations in the AT_RISK state. In the future, it is possible that this method can be used to suppress other listing violation types. A successful call returns a http status code of 204 Success. There is no response payload. If the call is not successful, an error code will be returned stating the issue.  # noqa: E501

        :param SuppressViolationRequest body: This type is the base request type of the SuppressViolation method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_compliance.Configuration, '/sell/compliance/v1', sell_compliance.ListingViolationApi, sell_compliance.ApiClient, 'suppress_violation', SellComplianceException, True, ['sell.compliance', 'listing_violation'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_compliance_get_listing_violations_summary(self, **kwargs):  # noqa: E501
        """get_listing_violations_summary  # noqa: E501

        This call returns listing violation counts for a seller. A user can pass in one or more compliance types through the compliance_type query parameter. See ComplianceTypeEnum for more information on the supported listing compliance types. Listing violations are returned for multiple marketplaces if the seller sells on multiple eBay marketplaces. Note: Only a canned response, with counts for all listing compliance types, is returned in the Sandbox environment. Due to this limitation, the compliance_type query parameter (if used) will not have an effect on the response.  # noqa: E501

        :param str x_ebay_c_marketplace_id: Use this header to specify the eBay marketplace identifier. Supported values for this header can be found in the MarketplaceIdEnum type definition. Note that Version 1.4.0 of the Compliance API is only supported on the US, UK, Australia, Canada {English), and Germany sites.
        :param str compliance_type: A user passes in one or more compliance type values through this query parameter. See ComplianceTypeEnum for more information on the supported compliance types that can be passed in here. If more than one compliance type value is used, delimit these values with a comma. If no compliance type values are passed in, the listing count for all compliance types will be returned. Note: Only a canned response, with counts for all listing compliance types, is returned in the Sandbox environment. Due to this limitation, the compliance_type query parameter (if used) will not have an effect on the response.
        :return: ComplianceSummary
        """
        try:
            return self._method_single(sell_compliance.Configuration, '/sell/compliance/v1', sell_compliance.ListingViolationSummaryApi, sell_compliance.ApiClient, 'get_listing_violations_summary', SellComplianceException, True, ['sell.compliance', 'listing_violation_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_customer_service_metric_task(self, body, accept_language, **kwargs):  # noqa: E501
        """create_customer_service_metric_task  # noqa: E501

        Use this method to create a customer service metrics download task with filter criteria for the customer service metrics report. When using this method, specify the feedType and filterCriteria including both evaluationMarketplaceId and customerServiceMetricType for the report. The method returns the location response header containing the call URI to use with getCustomerServiceMetricTask to retrieve status and details on the task. Only CURRENT Customer Service Metrics reports can be generated with the Sell Feed API. PROJECTED reports are not supported at this time. See the getCustomerServiceMetric method document in the Analytics API for more information about these two types of reports. Note: Before calling this API, retrieve the summary of the seller's performance and rating for the customer service metric by calling getCustomerServiceMetric (part of the Analytics API). You can then populate the create task request fields with the values from the response. This technique eliminates failed tasks that request a report for a customerServiceMetricType and evaluationMarketplaceId that are without evaluation.  # noqa: E501

        :param CreateServiceMetricsTaskRequest body: Request payload containing version, feedType, and optional filterCriteria. (required)
        :param str accept_language: Use this header to specify the natural language in which the authenticated user desires the response. (required)
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.CustomerServiceMetricTaskApi, sell_feed.ApiClient, 'create_customer_service_metric_task', SellFeedException, True, ['sell.feed', 'customer_service_metric_task'], (body, accept_language), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_customer_service_metric_task(self, task_id, **kwargs):  # noqa: E501
        """get_customer_service_metric_task  # noqa: E501

        Use this method to retrieve customer service metric task details for the specified task. The input is task_id.  # noqa: E501

        :param str task_id: Use this path parameter to specify the task ID value for the customer service metric task to retrieve. (required)
        :return: ServiceMetricsTask
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.CustomerServiceMetricTaskApi, sell_feed.ApiClient, 'get_customer_service_metric_task', SellFeedException, True, ['sell.feed', 'customer_service_metric_task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_customer_service_metric_tasks(self, **kwargs):  # noqa: E501
        """get_customer_service_metric_tasks  # noqa: E501

        Use this method to return an array of customer service metric tasks. You can limit the tasks returned by specifying a date range. Note: You can pass in either the look_back_days or date_range, but not both.  # noqa: E501

        :param str date_range: The task creation date range. The results are filtered to include only tasks with a creation date that is equal to the dates specified or is within the specified range. Do not use with the look_back_days parameter. Format: UTC For example, tasks within a range: yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ Tasks created on March 8, 2020 2020-03-08T00:00.00.000Z..2020-03-09T00:00:00.000Z Maximum: 90 days
        :param str feed_type: The feed type associated with the task. The only presently supported value is CUSTOMER_SERVICE_METRICS_REPORT.
        :param str limit: The number of customer service metric tasks to return per page of the result set. Use this parameter in conjunction with the offset parameter to control the pagination of the output. For example, if offset is set to 10 and limit is set to 10, the call retrieves tasks 11 thru 20 from the result set. If this parameter is omitted, the default value is used. Note:This feature employs a zero-based list, where the first item in the list has an offset of 0. Default: 10 Maximum: 500
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used. Default value: 7 Range: 1-90 (inclusive)
        :param str offset: The number of customer service metric tasks to skip in the result set before returning the first task in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: CustomerServiceMetricTaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.CustomerServiceMetricTaskApi, sell_feed.ApiClient, 'get_customer_service_metric_tasks', SellFeedException, True, ['sell.feed', 'customer_service_metric_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_inventory_task(self, body, **kwargs):  # noqa: E501
        """create_inventory_task  # noqa: E501

        This method creates an inventory-related download task for a specified feed type with optional filter criteria. When using this method, specify the feedType. This method returns the location response header containing the getInventoryTask call URI to retrieve the inventory task you just created. The URL includes the eBay-assigned task ID, which you can use to reference the inventory task. To retrieve the status of the task, use the getInventoryTask method to retrieve a single task ID or the getInventoryTasks method to retrieve multiple task IDs. Note: The scope depends on the feed type. An error message results when an unsupported scope or feed type is specified.Presently, this method supports Active Inventory Report. The ActiveInventoryReport returns a report that contains price and quantity information for all of the active listings for a specific seller. A seller can use this information to maintain their inventory on eBay.  # noqa: E501

        :param CreateInventoryTaskRequest body: The request payload containing the version, feedType, and optional filterCriteria. (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note: This value is case sensitive. For example: X-EBAY-C-MARKETPLACE-ID:EBAY_US This identifies the eBay marketplace that applies to this task. See MarketplaceIdEnum.
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.InventoryTaskApi, sell_feed.ApiClient, 'create_inventory_task', SellFeedException, True, ['sell.feed', 'inventory_task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_inventory_task(self, task_id, **kwargs):  # noqa: E501
        """get_inventory_task  # noqa: E501

        This method retrieves the task details and status of the specified inventory-related task. The input is task_id.  # noqa: E501

        :param str task_id: The ID of the task. This ID was generated when the task was created by the createInventoryTask method (required)
        :return: InventoryTask
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.InventoryTaskApi, sell_feed.ApiClient, 'get_inventory_task', SellFeedException, True, ['sell.feed', 'inventory_task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_inventory_tasks(self, **kwargs):  # noqa: E501
        """get_inventory_tasks  # noqa: E501

        This method searches for multiple tasks of a specific feed type, and includes date filters and pagination.  # noqa: E501

        :param str feed_type: The feed type associated with the inventory task. Either feed_type or schedule_id is required. Do not use with the schedule_id parameter. Presently, only one feed type is available: LMS_ACTIVE_INVENTORY_REPORT
        :param str schedule_id: The ID of the schedule for which to retrieve the latest result file. This ID is generated when the schedule was created by the createSchedule method. Schedules apply to downloaded reports (LMS_ACTIVE_INVENTORY_REPORT). Either schedule_id or feed_type is required. Do not use with the feed_type parameter.
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used. Default: 7 Range: 1-90 (inclusive)
        :param str date_range: Specifies the range of task creation dates used to filter the results. The results are filtered to include only tasks with a creation date that is equal to this date or is within specified range. Note: Maximum date range window size is 90 days. Valid Format (UTC): yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ For example: Tasks created on March 31, 2021 2021-03-31T00:00:00.000Z..2021-03-31T00:00:00.000Z
        :param str limit: The maximum number of tasks that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output. Note: This feature employs a zero-based list, where the first item in the list has an offset of 0. For example, if offset is set to 10 and limit is set to 10, the call retrieves tasks 11 thru 20 from the result set. If this parameter is omitted, the default value is used. Default: 10 Maximum: 500
        :param str offset: The number of tasks to skip in the result set before returning the first task in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :return: InventoryTaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.InventoryTaskApi, sell_feed.ApiClient, 'get_inventory_tasks', SellFeedException, True, ['sell.feed', 'inventory_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_order_task(self, body, **kwargs):  # noqa: E501
        """create_order_task  # noqa: E501

        This method creates an order download task with filter criteria for the order report. When using this method, specify the feedType, schemaVersion, and filterCriteria for the report. The method returns the location response header containing the getOrderTask call URI to retrieve the order task you just created. The URL includes the eBay-assigned task ID, which you can use to reference the order task. To retrieve the status of the task, use the getOrderTask method to retrieve a single task ID or the getOrderTasks method to retrieve multiple order task IDs. Note: The scope depends on the feed type. An error message results when an unsupported scope or feed type is specified. The following list contains this method's authorization scope and its corresponding feed type: https://api.ebay.com/oauth/api_scope/sell.fulfillment: LMS_ORDER_REPORT For details about how this method is used, see General feed types in the Selling Integration Guide. Note: At this time, the createOrderTask method only supports order creation date filters and not modified order date filters. Do not include the modifiedDateRange filter in your request payload.  # noqa: E501

        :param CreateOrderTaskRequest body: description not needed (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note: This value is case sensitive. For example: X-EBAY-C-MARKETPLACE-ID:EBAY_US This identifies the eBay marketplace that applies to this task. See MarketplaceIdEnum.
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.OrderTaskApi, sell_feed.ApiClient, 'create_order_task', SellFeedException, True, ['sell.feed', 'order_task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_order_task(self, task_id, **kwargs):  # noqa: E501
        """get_order_task  # noqa: E501

        This method retrieves the task details and status of the specified task. The input is task_id. For details about how this method is used, see Working with Order Feeds in the Selling Integration Guide.  # noqa: E501

        :param str task_id: The ID of the task. This ID is generated when the task was created by the createOrderTask method. (required)
        :return: OrderTask
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.OrderTaskApi, sell_feed.ApiClient, 'get_order_task', SellFeedException, True, ['sell.feed', 'order_task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_order_tasks(self, **kwargs):  # noqa: E501
        """get_order_tasks  # noqa: E501

        This method returns the details and status for an array of order tasks based on a specified feed_type or schedule_id. Specifying both feed_type and schedule_id results in an error. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type. If specifying the feed_type, limit which order tasks are returned by specifying filters such as the creation date range or period of time using look_back_days. If specifying a schedule_id, the schedule template (that the schedule_id is based on) determines which order tasks are returned (see schedule_id for additional information). Each schedule_id applies to one feed_type.  # noqa: E501

        :param str date_range: The order tasks creation date range. This range is used to filter the results. The filtered results are filtered to include only tasks with a creation date that is equal to this date or is within specified range. Only orders less than 90 days old can be retrieved. Do not use with the look_back_days parameter. Format: UTC For example: Tasks within a range yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ Tasks created on September 8, 2019 2019-09-08T00:00:00.000Z..2019-09-09T00:00:00.000Z
        :param str feed_type: The feed type associated with the task. The only presently supported value is LMS_ORDER_REPORT. Do not use with the schedule_id parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :param str limit: The maximum number of order tasks that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output. Note: This feature employs a zero-based list, where the first item in the list has an offset of 0. For example, if offset is set to 10 and limit is set to 10, the call retrieves order tasks 11 thru 20 from the result set. If this parameter is omitted, the default value is used. Default: 10 Maximum: 500
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used. Default: 7 Range: 1-90 (inclusive)
        :param str offset: The number of order tasks to skip in the result set before returning the first order in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :param str schedule_id: The schedule ID associated with the order task. A schedule periodically generates a report for the feed type specified by the schedule template (see scheduleTemplateId in createSchedule). Do not use with the feed_type parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :return: OrderTaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.OrderTaskApi, sell_feed.ApiClient, 'get_order_tasks', SellFeedException, True, ['sell.feed', 'order_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_schedule(self, body, **kwargs):  # noqa: E501
        """create_schedule  # noqa: E501

        This method creates a schedule, which is a subscription to the specified schedule template. A schedule periodically generates a report for the feedType specified by the template. Specify the same feedType as the feedType of the associated schedule template. When creating the schedule, if available from the template, you can specify a preferred trigger hour, day of the week, or day of the month. These and other fields are conditionally available as specified by the template. Note: Make sure to include all fields required by the schedule template (scheduleTemplateId). Call the getScheduleTemplate method (or the getScheduleTemplates method), to find out which fields are required or optional. If a field is optional and a default value is provided by the template, the default value will be used if omitted from the payload.A successful call returns the location response header containing the getSchedule call URI to retrieve the schedule you just created. The URL includes the eBay-assigned schedule ID, which you can use to reference the schedule task. To retrieve the details of the create schedule task, use the getSchedule method for a single schedule ID or the getSchedules method to retrieve all schedule details for the specified feed_type. The number of schedules for each feedType is limited. Error code 160031 is returned when you have reached this maximum. Note: Except for schedules with a HALF-HOUR frequency, all schedules will ideally run at the start of each hour ('00' minutes). Actual start time may vary time may vary due to load and other factors.  # noqa: E501

        :param CreateUserScheduleRequest body: In the request payload: feedType and scheduleTemplateId are required; scheduleName is optional; preferredTriggerHour, preferredTriggerDayOfWeek, preferredTriggerDayOfMonth, scheduleStartDate, scheduleEndDate, and schemaVersion are conditional. (required)
        :return: object
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'create_schedule', SellFeedException, True, ['sell.feed', 'schedule'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_delete_schedule(self, schedule_id, **kwargs):  # noqa: E501
        """delete_schedule  # noqa: E501

        This method deletes an existing schedule. Specify the schedule to delete using the schedule_id path parameter.  # noqa: E501

        :param str schedule_id: The schedule_id of the schedule to delete. This ID was generated when the task was created. If you do not know the schedule_id, use the getSchedules method to return all schedules based on a specified feed_type and find the schedule_id of the schedule to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'delete_schedule', SellFeedException, True, ['sell.feed', 'schedule'], schedule_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_latest_result_file(self, schedule_id, **kwargs):  # noqa: E501
        """get_latest_result_file  # noqa: E501

        This method downloads the latest result file generated by the schedule. The response of this call is a compressed or uncompressed CSV, XML, or JSON file, with the applicable file extension (for example: csv.gz). Specify the schedule_id path parameter to download its last generated file.  # noqa: E501

        :param str schedule_id: The ID of the schedule for which to retrieve the latest result file. This ID is generated when the schedule was created by the createSchedule method. (required)
        :return: StreamingOutput
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_latest_result_file', SellFeedException, True, ['sell.feed', 'schedule'], schedule_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedule(self, schedule_id, **kwargs):  # noqa: E501
        """get_schedule  # noqa: E501

        This method retrieves schedule details and status of the specified schedule. Specify the schedule to retrieve using the schedule_id. Use the getSchedules method to find a schedule if you do not know the schedule_id.  # noqa: E501

        :param str schedule_id: The ID of the schedule for which to retrieve the details. This ID is generated when the schedule was created by the createSchedule method. (required)
        :return: UserScheduleResponse
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedule', SellFeedException, True, ['sell.feed', 'schedule'], schedule_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedule_template(self, schedule_template_id, **kwargs):  # noqa: E501
        """get_schedule_template  # noqa: E501

        This method retrieves the details of the specified template. Specify the template to retrieve using the schedule_template_id path parameter. Use the getScheduleTemplates method to find a schedule template if you do not know the schedule_template_id.  # noqa: E501

        :param str schedule_template_id: The ID of the template to retrieve. If you do not know the schedule_template_id, refer to the documentation or use the getScheduleTemplates method to find the available schedule templates. (required)
        :return: ScheduleTemplateResponse
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedule_template', SellFeedException, True, ['sell.feed', 'schedule'], schedule_template_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedule_templates(self, feed_type, **kwargs):  # noqa: E501
        """get_schedule_templates  # noqa: E501

        This method retrieves an array containing the details and status of all schedule templates based on the specified feed_type. Use this method to find a schedule template if you do not know the schedule_template_id.  # noqa: E501

        :param str feed_type: The feed type of the schedule templates to retrieve. (required)
        :param str limit: The maximum number of schedule templates that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output. Note: This feature employs a zero-based list, where the first item in the list has an offset of 0. For example, if offset is set to 10 and limit is set to 10, the call retrieves schedule templates 11 thru 20 from the result set. If this parameter is omitted, the default value is used. Default: 10 Maximum: 500
        :param str offset: The number of schedule templates to skip in the result set before returning the first template in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :return: ScheduleTemplateCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedule_templates', SellFeedException, True, ['sell.feed', 'schedule'], feed_type, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedules(self, feed_type, **kwargs):  # noqa: E501
        """get_schedules  # noqa: E501

        This method retrieves an array containing the details and status of all schedules based on the specified feed_type. Use this method to find a schedule if you do not know the schedule_id.  # noqa: E501

        :param str feed_type: The feedType associated with the schedule. (required)
        :param str limit: The maximum number of schedules that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output. Note: This feature employs a zero-based list, where the first item in the list has an offset of 0. For example, if offset is set to 10 and limit is set to 10, the call retrieves schedules 11 thru 20 from the result set. If this parameter is omitted, the default value is used. Default: 10 Maximum: 500
        :param str offset: The number of schedules to skip in the result set before returning the first schedule in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :return: UserScheduleCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedules', SellFeedException, True, ['sell.feed', 'schedule'], feed_type, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_update_schedule(self, body, schedule_id, **kwargs):  # noqa: E501
        """update_schedule  # noqa: E501

        This method updates an existing schedule. Specify the schedule to update using the schedule_id path parameter. If the schedule template has changed after the schedule was created or updated, the input will be validated using the changed template. Note: Make sure to include all fields required by the schedule template (scheduleTemplateId). Call the getScheduleTemplate method (or the getScheduleTemplates method), to find out which fields are required or optional. If you do not know the scheduleTemplateId, call the getSchedule method to find out.  # noqa: E501

        :param UpdateUserScheduleRequest body: In the request payload: scheduleName is optional; preferredTriggerHour, preferredTriggerDayOfWeek, preferredTriggerDayOfMonth, scheduleStartDate, scheduleEndDate, and schemaVersion are conditional. (required)
        :param str schedule_id: The ID of the schedule to update. This ID is generated when the schedule was created by the createSchedule method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'update_schedule', SellFeedException, True, ['sell.feed', 'schedule'], (body, schedule_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_task(self, body, **kwargs):  # noqa: E501
        """create_task  # noqa: E501

        This method creates an upload task or a download task without filter criteria. When using this method, specify the feedType and the feed file schemaVersion. The feed type specified sets the task as a download or an upload task. For details about the upload and download flows, see Working with Order Feeds in the Selling Integration Guide. Note: The scope depends on the feed type. An error message results when an unsupported scope or feed type is specified. The following list contains this method's authorization scopes and their corresponding feed types: https://api.ebay.com/oauth/api_scope/sell.inventory: See LMS FeedTypes https://api.ebay.com/oauth/api_scope/sell.fulfillment: LMS_ORDER_ACK (specify for upload tasks). Also see LMS FeedTypes https://api.ebay.com/oauth/api_scope/sell.marketing: None* https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly: None* * Reserved for future release  # noqa: E501

        :param CreateTaskRequest body: description not needed (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note: This value is case sensitive. For example: X-EBAY-C-MARKETPLACE-ID:EBAY_US This identifies the eBay marketplace that applies to this task. See MarketplaceIdEnum.
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'create_task', SellFeedException, True, ['sell.feed', 'task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_input_file(self, task_id, **kwargs):  # noqa: E501
        """get_input_file  # noqa: E501

        This method downloads the file previously uploaded using uploadFile. Specify the task_id from the uploadFile call. Note: With respect to LMS, this method applies to all feed types except LMS_ORDER_REPORT and LMS_ACTIVE_INVENTORY_REPORT. See LMS API Feeds in the Selling Integration Guide.  # noqa: E501

        :param str task_id: The task ID associated with the file to be downloaded. (required)
        :return: StreamingOutput
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_input_file', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_result_file(self, task_id, **kwargs):  # noqa: E501
        """get_result_file  # noqa: E501

        This method retrieves the generated file that is associated with the specified task ID. The response of this call is a compressed or uncompressed CSV, XML, or JSON file, with the applicable file extension (for example: csv.gz). For details about how this method is used, see Working with Order Feeds in the Selling Integration Guide. Note: The status of the task to retrieve must be in the COMPLETED or COMPLETED_WITH_ERROR state before this method can retrieve the file. You can use the getTask or getTasks method to retrieve the status of the task.  # noqa: E501

        :param str task_id: The ID of the task associated with the file you want to download. This ID was generated when the task was created. (required)
        :return: StreamingOutput
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_result_file', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_task(self, task_id, **kwargs):  # noqa: E501
        """get_task  # noqa: E501

        This method retrieves the details and status of the specified task. The input is task_id. For details of how this method is used, see Working with Order Feeds in the Selling Integration Guide.  # noqa: E501

        :param str task_id: The ID of the task. This ID was generated when the task was created. (required)
        :return: Task
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_task', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_tasks(self, **kwargs):  # noqa: E501
        """get_tasks  # noqa: E501

        This method returns the details and status for an array of tasks based on a specified feed_type or scheduledId. Specifying both feed_type and scheduledId results in an error. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type. If specifying the feed_type, limit which tasks are returned by specifying filters, such as the creation date range or period of time using look_back_days. Also, by specifying the feed_type, both on-demand and scheduled reports are returned. If specifying a scheduledId, the schedule template (that the schedule ID is based on) determines which tasks are returned (see schedule_id for additional information). Each scheduledId applies to one feed_type.  # noqa: E501

        :param str date_range: Specifies the range of task creation dates used to filter the results. The results are filtered to include only tasks with a creation date that is equal to this date or is within specified range. Only tasks that are less than 90 days can be retrieved. Note: Maximum date range window size is 90 days. Valid Format (UTC):yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ For example: Tasks created on September 8, 2019 2019-09-08T00:00:00.000Z..2019-09-09T00:00:00.000Z
        :param str feed_type: The feed type associated with the tasks to be returned. Only use a feedType that is available for your API: Order Feeds: LMS_ORDER_ACK, LMS_ORDER_REPORT Large Merchant Services (LMS) Feeds: See Available FeedTypes Do not use with the schedule_id parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :param str limit: The maximum number of tasks that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output. Note: This feature employs a zero-based list, where the first item in the list has an offset of 0. For example, if offset is set to 10 and limit is set to 10, the call retrieves tasks 11 thru 20 from the result set. If this parameter is omitted, the default value is used. Default: 10 Maximum: 500
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used. Default: 7 Range: 1-90 (inclusive)
        :param str offset: The number of tasks to skip in the result set before returning the first task in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :param str schedule_id: The schedule ID associated with the task. A schedule periodically generates a report for the feed type specified by the schedule template (see scheduleTemplateId in createSchedule). Do not use with the feed_type parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :return: TaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_tasks', SellFeedException, True, ['sell.feed', 'task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_upload_file(self, task_id, **kwargs):  # noqa: E501
        """upload_file  # noqa: E501

        This method associates the specified file with the specified task ID and uploads the input file. After the file has been uploaded, the processing of the file begins. Reports often take time to generate and it's common for this method to return an HTTP status of 202, which indicates the report is being generated. Use the getTask with the task ID or getTasks to determine the status of a report. The status flow is QUEUED &gt; IN_PROCESS &gt; COMPLETED or COMPLETED_WITH_ERROR. When the status is COMPLETED or COMPLETED_WITH_ERROR, this indicates the file has been processed and the order report can be downloaded. If there are errors, they will be indicated in the report file. For details of how this method is used in the upload flow, see Working with Order Feeds in the Selling Integration Guide. Note: This method applies to all File Exchange feed types and LMS feed types except LMS_ORDER_REPORT and LMS_ACTIVE_INVENTORY_REPORT. See LMS API Feeds in the Selling Integration Guide and File Exchange FeedTypes in the File Exchange Migration Guide. Note: You must use a Content-Type header with its value set to &quot;multipart/form-data&quot;. See Samples for information.  # noqa: E501

        :param str task_id: The task_id associated with the file that will be uploaded. This ID was generated when the specified task was created. (required)
        :param str creation_date:
        :param str file_name:
        :param str modification_date:
        :param str name:
        :param dict(str, str) parameters:
        :param str read_date:
        :param int size:
        :param str type:
        :return: object
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'upload_file', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_payout(self, payout_id, **kwargs):  # noqa: E501
        """get_payout  # noqa: E501

        This method retrieves details on a specific seller payout. The unique identifier of the payout is passed in as a path parameter at the end of the call URI. <br/><br/>The <b>getPayouts</b> method can be used to retrieve the unique identifier of a payout, or the user can check Seller Hub.  # noqa: E501

        :param str payout_id: The unique identifier of the payout is passed in as a path parameter at the end of the call URI. <br/><br/>The <b>getPayouts</b> method can be used to retrieve the unique identifier of a payout, or the user can check Seller Hub to get the payout ID. (required)
        :return: Payout
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.PayoutApi, sell_finances.ApiClient, 'get_payout', SellFinancesException, True, ['sell.finances', 'payout'], payout_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_payout_summary(self, **kwargs):  # noqa: E501
        """get_payout_summary  # noqa: E501

        This method is used to retrieve cumulative values for payouts in a particular state, or all states. The metadata in the response includes total payouts, the total number of monetary transactions (sales, refunds, credits) associated with those payouts, and the total dollar value of all payouts.<br/><br/>If the <b>filter</b> query parameter is used to filter by payout status, only one payout status value may be used. If the <b>filter</b> query parameter is not used to filter by a specific payout status, cumulative values for payouts in all states are returned.<br/><br/>The user can also use the <b>filter</b> query parameter to specify a date range, and then only payouts that were processed within that date range are considered.  # noqa: E501

        :param str filter: The two filter types that can be used here are discussed below. One or both of these filter types can be used. If none of these filters are used, the data returned in the response will reflect payouts, in all states, processed within the last 90 days. <ul><li><b>payoutDate</b>: consider payouts processed within a specific range of dates. The date format to use is <code>YYYY-MM-DDTHH:MM:SS.SSSZ</code>. Below is the proper syntax to use if filtering by a date range: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/payout_summary?filter=payoutDate:[2018-12-17T00:00:01.000Z..2018-12-24T00:00:01.000Z]</code><br/><br/>Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past.</li> <li><b>payoutStatus</b>: consider only the payouts in a particular state. Only one payout state can be specified with this filter. The supported <b>payoutStatus</b> values are as follows:<ul><li><code>INITIATED</code>: search for payouts that have been initiated but not processed.</li><li><code>SUCCEEDED</code>: consider only successful payouts.</li><li><code>RETRYABLE_FAILED</code>: consider only payouts that failed, but ones which will be tried again.</li><li><code>TERMINAL_FAILED</code>: consider only payouts that failed, and ones that will not be tried again.</li><li> <code>REVERSED</code>: consider only payouts that were reversed. </li></ul>Below is the proper syntax to use if filtering by payout status: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/payout_summary?filter=payoutStatus:{SUCCEEDED}</code></ul><br/>If both the <b>payoutDate</b> and <b>payoutStatus</b> filters are used, only the payouts that satisfy both criteria are considered in the results. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :return: PayoutSummaryResponse
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.PayoutApi, sell_finances.ApiClient, 'get_payout_summary', SellFinancesException, True, ['sell.finances', 'payout'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_payouts(self, **kwargs):  # noqa: E501
        """get_payouts  # noqa: E501

        This method is used to retrieve the details of one or more seller payouts. By using the <b>filter</b> query parameter, users can retrieve payouts processed within a specific date range, and/or they can retrieve payouts in a specific state.<br/><br/>There are also pagination and sort query parameters that allow users to control the payouts that are returned in the response.<br/><br/>If no payouts match the input criteria, an empty payload is returned.  # noqa: E501

        :param str filter: The three filter types that can be used here are discussed below. If none of these filters are used, all recent payouts in all states are returned:<ul><li><b>payoutDate</b>: search for payouts within a specific range of dates. The date format to use is <code>YYYY-MM-DDTHH:MM:SS.SSSZ</code>. Below is the proper syntax to use if filtering by a date range: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/payout?filter=payoutDate:[2018-12-17T00:00:01.000Z..2018-12-24T00:00:01.000Z]</code><br/><br/>Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past.</li><li><b>lastAttemptedPayoutDate</b>: search for attempted payouts that failed within a specific range of dates. In order to use this filter, the <b>payoutStatus</b> filter must also be used and its value must be set to <code>RETRYABLE_FAILED</code>. The date format to use is <code>YYYY-MM-DDTHH:MM:SS.SSSZ</code>. The same syntax used for the <b>payoutDate</b> filter is also used for the <b>lastAttemptedPayoutDate</b> filter. <br><br>This filter is only applicable (and will return results) if one or more seller payouts have failed, but are retryable.</li> <li><b>payoutStatus</b>: search for payouts in a particular state. Only one payout state can be specified with this filter. The supported <b>payoutStatus</b> values are as follows:<ul><li><code>INITIATED</code>: search for payouts that have been initiated but not processed.</li><li><code>SUCCEEDED</code>: search for successful payouts.</li><li><code>RETRYABLE_FAILED</code>: search for payouts that failed, but ones which will be tried again. This value must be used if filtering by <b>lastAttemptedPayoutDate</b>. </li><li><code>TERMINAL_FAILED</code>: search for payouts that failed, and ones that will not be tried again.</li><li> <code>REVERSED</code>: search for payouts that were reversed. </li></ul>Below is the proper syntax to use if filtering by payout status: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/payout?filter=payoutStatus:{SUCCEEDED}</code></ul><br/>If both the <b>payoutDate</b> and <b>payoutStatus</b> filters are used, payouts must satisfy both criteria to be returned. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :param str sort: By default, payouts or failed payouts that match the input criteria are sorted in ascending order according to the payout date/last attempted payout date (oldest payouts returned first). <br><br>To view payouts in descending order instead (most recent payouts/attempted payouts first), you would include the <b>sort</b> query parameter, and then set the value of its <b>field</b> parameter to <code>payoutDate</code> or <code>lastAttemptedPayoutDate</code> (if searching for failed, retrybable payouts). Below is the proper syntax to use if filtering by a payout date range in descending order: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/payout?filter=payoutDate:[2018-12-17T00:00:01.000Z..2018-12-24T00:00:01.000Z]&sort=payoutDate</code><br/><br/>Payouts can only be sorted according to payout date, and can not be sorted by payout status. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:SortField
        :param str limit: The number of payouts to return per page of the result set. Use this parameter in conjunction with the <b>offset</b> parameter to control the pagination of the output. <br /><br /> For example, if <b>offset</b> is set to <code>10</code> and <b>limit</b> is set to <code>10</code>, the method retrieves payouts 11 thru 20 from the result set. <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first payout in the results set has an offset value of <code>0</code>. </span> <br /><br /> <b>Maximum:</b> <code>200</code> <br /> <b>Default:</b> <code>20</code>
        :param str offset: This integer value indicates the actual position that the first payout returned on the current page has in the results set. So, if you wanted to view the 11th payout of the result set, you would set the <strong>offset</strong> value in the request to <code>10</code>. <br><br>In the request, you can use the <b>offset</b> parameter in conjunction with the <b>limit</b> parameter to control the pagination of the output. For example, if <b>offset</b> is set to <code>30</code> and <b>limit</b> is set to <code>10</code>, the method retrieves payouts 31 thru 40 from the resulting collection of payouts. <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first payout in the results set has an offset value of <code>0</code>.</span><br /><br /><b>Default:</b> <code>0</code> (zero)
        :return: Payouts
        """
        try:
            return self._method_paged(sell_finances.Configuration, '/sell/finances/v1', sell_finances.PayoutApi, sell_finances.ApiClient, 'get_payouts', SellFinancesException, True, ['sell.finances', 'payout'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_seller_funds_summary(self, **kwargs):  # noqa: E501
        """get_seller_funds_summary  # noqa: E501

        This method retrieves all pending funds that have not yet been distributed through a seller payout.<br><br>There are no input parameters for this method. The response payload includes available funds, funds being processed, funds on hold, and also an aggregate count of all three of these categories.<br><br>If there are no funds that are pending, on hold, or being processed for the seller's account, no response payload is returned, and an http status code of <code>204 - No Content</code> is returned instead.  # noqa: E501

        :return: SellerFundsSummaryResponse
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.SellerFundsSummaryApi, sell_finances.ApiClient, 'get_seller_funds_summary', SellFinancesException, True, ['sell.finances', 'seller_funds_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_transaction_summary(self, **kwargs):  # noqa: E501
        """get_transaction_summary  # noqa: E501

        This method is used to retrieve cumulative values for five types of monetary transactions (order sales, seller credits, buyer refunds, buyer-initiated payment disputes, eBay shipping label purchases, and transfers). If applicable, the number of payment holds and the amount of the holds are also returned. <br/><br/>See the description for the <b>filter</b> query parameter for more information on the available filters.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> Unless the <b>transactionType</b> filter is used to retrieve a specific type of monetary transaction (sale, buyer refund, seller credit, payment dispute, shipping label, transfer), the <b>creditCount</b> and <b>creditAmount</b> response fields account for both order sales and seller credits (the count and value is not distinguished between the two monetary transaction types).</span>  # noqa: E501

        :param str filter: Numerous filters are available for the <strong>getTransactionSummary</strong> method, and these filters are discussed below. One or more of these filter types can be used. The <b>transactionStatus</b> filter must be used. All other filters are optional. <ul><li><b>transactionStatus</b>: the data returned in the response pertains to the sales, payouts, and transfer status set. The supported <b>transactionStatus</b> values are as follows:<ul><li><code>PAYOUT</code>: only consider monetary transactions where the proceeds from the sales order(s) have been paid out to the seller's bank account.</li><li><code>FUNDS_PROCESSING</code>: only consider monetary transactions where the proceeds from the sales order(s) are currently being processed.</li><li><code>FUNDS_AVAILABLE_FOR_PAYOUT</code>: only consider monetary transactions where the proceeds from the sales order(s) are available for a seller payout, but processing has not yet begun.</li><li><code>FUNDS_ON_HOLD</code>: only consider monetary transactions where the proceeds from the sales order(s) are currently being held by eBay, and are not yet available for a seller payout.</li><li><code>COMPLETED</code>: this indicates that the funds for the corresponding <code>TRANSFER</code> monetary transaction have transferred and the transaction has completed.</li><li><code>FAILED</code>: this indicates the process has failed for the corresponding <code>TRANSFER</code> monetary transaction. </li></ul>Below is the proper syntax to use when setting up the <b>transactionStatus</b> filter: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionStatus:&#123;PAYOUT&#125;</code></li><li><b>transactionDate</b>: only consider monetary transactions that occurred within a specific range of dates.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> All dates must be input using UTC format (<code>YYYY-MM-DDTHH:MM:SS.SSSZ</code>) and should be adjusted accordingly for the local timezone of the user.</span><br /><br />Below is the proper syntax to use if filtering by a date range: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionDate:&#91;2018-10-23T00:00:01.000Z..2018-11-09T00:00:01.000Z&#93;</code><br/><br/>Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past.</li>  <li><b>transactionType</b>: only consider a specific type of monetary transaction. The supported <b>transactionType</b> values are as follows:<ul><li><code>SALE</code>: a sales order.</li><li> <code>REFUND</code>: a refund to the buyer after an order cancellation or return.</li><li><code>CREDIT</code>: a credit issued by eBay to the seller's account.</li><li><code>DISPUTE</code>: a monetary transaction associated with a payment dispute between buyer and seller.</li><li><code>NON_SALE_CHARGE</code>: a monetary transaction involving a seller transferring money to eBay for the balance of a charge for NON_SALE_CHARGE transactions (transactions that contain non-transactional seller fees). These can include a one-time payment, monthly/yearly subscription fees charged monthly, NRC charges, and fee credits.</li><li><code>SHIPPING_LABEL</code>: a monetary transaction where eBay is billing the seller for an eBay shipping label. Note that the shipping label functionality will initially only be available to a select number of sellers.</li><li><code>TRANSFER</code>: A transfer is a monetary transaction where eBay is billing the seller for reimbursement of a charge. An example of a transfer is a seller reimbursing eBay for a buyer refund.</li></ul>Below is the proper syntax to use if filtering by a monetary transaction type: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionType:{SALE}</code></li><li><b>buyerUsername</b>: only consider monetary transactions involving a specific buyer (specified with the buyer's eBay user ID). Below is the proper syntax to use if filtering by a specific eBay buyer: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=buyerUsername:&#123;buyer1234&#125;</code> </li><li><b>salesRecordReference</b>: only consider monetary transactions corresponding to a specific order (identified with a Selling Manager order identifier). Below is the proper syntax to use if filtering by a specific Selling Manager Sales Record ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=salesRecordReference:&#123;123&#125;</code><br/><br/><span class=\"tablenote\"><strong>Note:</strong> For all orders originating after February 1, 2020, a value of <code>0</code> will be returned in the <b>salesRecordReference</b> field. So, this filter will only be useful to retrieve orders than occurred before this date.</span> </li><li><b>payoutId</b>: only consider monetary transactions related to a specific seller payout (identified with a Payout ID). This value is auto-generated by eBay once the seller payout is set to be processed. Below is the proper syntax to use if filtering by a specific Payout ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=payoutId:&#123;5000106638&#125;</code>  </li><li><b>transactionId</b>: the unique identifier of a monetary transaction. For a sales order, the <b>orderId</b> filter should be used instead. Only the monetary transaction(s) associated with this <b>transactionId</b> value are returned.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> This filter cannot be used alone; the <b>transactionType</b> must also be specified when filtering by transaction ID.</span><br /><br />Below is the proper syntax to use if filtering by a specific transaction ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionId:{03-03620-33763}&filter=transactionType:{SALE}</code> </li><li><b>orderId</b>: the unique identifier of a sales order. For any other monetary transaction, the <b>transactionId</b> filter should be used instead. Only the monetary transaction(s) associated with this <b>orderId</b> value are returned. Below is the proper syntax to use if filtering by a specific order ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=orderId:{03-03620-33763}</code> </li></ul> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :return: TransactionSummaryResponse
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.TransactionApi, sell_finances.ApiClient, 'get_transaction_summary', SellFinancesException, True, ['sell.finances', 'transaction'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_transactions(self, **kwargs):  # noqa: E501
        """get_transactions  # noqa: E501

        This method allows a seller to retrieve one or monetary transactions. In this case, 'monetary transactions' include sales orders, buyer refunds, seller credits, buyer-initiated payment disputes, eBay shipping label purchases, and transfers. There are numerous input filters available for use, including filters to retrieve specific types of monetary transactions, to retrieve monetary transactions processed within a specific date range, or to retrieve monetary transactions in a specific state. See the <b>filter</b> field for more information on each filter, and how each one is used. <br/><br/>There are also pagination and sort query parameters that allow users to further control the monetary transactions that are returned in the response.<br/><br/>If no monetary transactions match the input criteria, an http status code of <em>204 No Content</em> is returned with no response payload.  # noqa: E501

        :param str filter: Numerous filters are available for the <strong>getTransactions</strong> method, and these filters are discussed below. One or more of these filter types can be used. If none of these filters are used, all monetary transactions from the last 90 days are returned:<ul><li><b>transactionDate</b>: search for monetary transactions that occurred within a specific range of dates.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> All dates must be input using UTC format (<code>YYYY-MM-DDTHH:MM:SS.SSSZ</code>) and should be adjusted accordingly for the local timezone of the user.</span><br /><br />Below is the proper syntax to use if filtering by a date range: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionDate:[2018-10-23T00:00:01.000Z..2018-11-09T00:00:01.000Z]</code><br/><br/>Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past.</li>  <li><b>transactionType</b>: search for a specific type of monetary transaction. The supported <b>transactionType</b> values are as follows:<ul><li><code>SALE</code>: a sales order.</li><li> <code>REFUND</code>: a refund to the buyer after an order cancellation or return.</li><li><code>CREDIT</code>: a credit issued by eBay to the seller's account.</li><li><code>DISPUTE</code>: a monetary transaction associated with a payment dispute between buyer and seller.</li><li><code>NON_SALE_CHARGE</code>: a monetary transaction involving a seller transferring money to eBay for the balance of a charge for NON_SALE_CHARGE transactions (transactions that contain non-transactional seller fees). These can include a one-time payment, monthly/yearly subscription fees charged monthly, NRC charges, and fee credits.</li><li><code>SHIPPING_LABEL</code>: a monetary transaction where eBay is billing the seller for an eBay shipping label. Note that the shipping label functionality will initially only be available to a select number of sellers.</li><li><code>TRANSFER</code>: A transfer is a monetary transaction where eBay is billing the seller for reimbursement of a charge. An example of a transfer is a seller reimbursing eBay for a buyer refund.</li></ul>Below is the proper syntax to use if filtering by a monetary transaction type: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionType:{SALE}</code></li><li><b>transactionStatus</b>: this filter type is only applicable for sales orders, and allows the user to filter seller payouts in a particular state.  The supported <b>transactionStatus</b> values are as follows:<ul><li><code>PAYOUT</code>: this indicates that the proceeds from the corresponding sales order has been paid out to the seller's account.</li><li><code>FUNDS_PROCESSING</code>: this indicates that the funds for the corresponding monetary transaction are currently being processed.</li><li><code>FUNDS_AVAILABLE_FOR_PAYOUT</code>: this indicates that the proceeds from the corresponding sales order are available for a seller payout, but processing has not yet begun.</li><li><code>FUNDS_ON_HOLD</code>: this indicates that the proceeds from the corresponding sales order are currently being held by eBay, and are not yet available for a seller payout.</li><li><code>COMPLETED</code>: this indicates that the funds for the corresponding <code>TRANSFER</code> monetary transaction have transferred and the transaction has completed.</li><li><code>FAILED</code>: this indicates the process has failed for the corresponding <code>TRANSFER</code> monetary transaction. </li></ul>Below is the proper syntax to use if filtering by transaction status: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionStatus:{PAYOUT}</code></li><li><b>buyerUsername</b>: the eBay user ID of the buyer involved in the monetary transaction. Only monetary transactions involving this buyer are returned. Below is the proper syntax to use if filtering by a specific eBay buyer: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=buyerUsername:{buyer1234}</code> </li><li><b>salesRecordReference</b>: the unique Selling Manager identifier of the order involved in the monetary transaction. Only monetary transactions involving this Selling Manager Sales Record ID are returned. Below is the proper syntax to use if filtering by a specific Selling Manager Sales Record ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=salesRecordReference:{123}</code><br/><br/><span class=\"tablenote\"><strong>Note:</strong> For all orders originating after February 1, 2020, a value of <code>0</code> will be returned in the <b>salesRecordReference</b> field. So, this filter will only be useful to retrieve orders than occurred before this date. </span></li><li><b>payoutId</b>: the unique identifier of a seller payout. This value is auto-generated by eBay once the seller payout is set to be processed. Only monetary transactions involving this Payout ID are returned. Below is the proper syntax to use if filtering by a specific Payout ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=payoutId:{5000106638}</code>  </li><li><b>transactionId</b>: the unique identifier of a monetary transaction. For a sales order, the <b>orderId</b> filter should be used instead. Only the monetary transaction defined by the identifier is returned.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> This filter cannot be used alone; the <b>transactionType</b> must also be specified when filtering by transaction ID.</span><br /><br />Below is the proper syntax to use if filtering by a specific transaction ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionId:{03-03620-33763}&filter=transactionType:{SALE}</code> </li><li><b>orderId</b>: the unique identifier of a sales order. For any other monetary transaction, the <b>transactionId</b> filter should be used instead. Only the sales order defined by the identifier is returned. Below is the proper syntax to use if filtering by a specific order ID: <br/><br/><code>https://apiz.ebay.com/sell/finances/v1/transaction?filter=orderId:{03-03620-33763}</code> </li></ul> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :param str sort: Sorting is not yet available for the <b>getTransactions</b> method. By default, monetary transactions that match the input criteria are sorted in descending order according to the transaction date. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:SortField
        :param str limit: The number of monetary transactions to return per page of the result set. Use this parameter in conjunction with the <b>offset</b> parameter to control the pagination of the output. <br /><br /> For example, if <b>offset</b> is set to <code>10</code> and <b>limit</b> is set to <code>10</code>, the method retrieves monetary transactions 11 thru 20 from the result set. <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first item in the list has an offset of <code>0</code>. If an <b>orderId</b>, <b>transactionId</b>, or <b>payoutId</b> filter is included in the request, any <b>limit</b> value will be ignored.</span> <br /><br /> <b>Maximum:</b><code> 1000</code> <br /> <b>Default:</b><code> 20</code>
        :param str offset: This integer value indicates the actual position that the first monetary transaction returned on the current page has in the results set. So, if you wanted to view the 11th monetary transaction of the result set, you would set the <strong>offset</strong> value in the request to <code>10</code>. <br><br>In the request, you can use the <b>offset</b> parameter in conjunction with the <b>limit</b> parameter to control the pagination of the output. For example, if <b>offset</b> is set to <code>30</code> and <b>limit</b> is set to <code>10</code>, the method retrieves transactions 31 thru 40 from the resulting collection of transactions. <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first item in the list has an offset of <code>0</code>.</span><br/><b>Default:</b> <code>0</code> (zero)
        :return: Transactions
        """
        try:
            return self._method_paged(sell_finances.Configuration, '/sell/finances/v1', sell_finances.TransactionApi, sell_finances.ApiClient, 'get_transactions', SellFinancesException, True, ['sell.finances', 'transaction'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_transfer(self, transfer_id, **kwargs):  # noqa: E501
        """get_transfer  # noqa: E501

        This method retrieves detailed information regarding a <code>TRANSFER</code> transaction type. A <code>TRANSFER</code> is a  monetary transaction type that involves a seller transferring money to eBay for reimbursement of one or more charges. For example, when a seller reimburses eBay for a buyer refund.<br><br>If an ID is passed into the URI that is an identifier for another transaction type, this call will return an http status code of <code>404 Not found</code>.  # noqa: E501

        :param str transfer_id: The unique identifier of the <code>TRANSFER</code> transaction type you wish to retrieve. (required)
        :return: Transfer
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.TransferApi, sell_finances.ApiClient, 'get_transfer', SellFinancesException, True, ['sell.finances', 'transfer'], transfer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_order(self, order_id, **kwargs):  # noqa: E501
        """get_order  # noqa: E501

        Use this call to retrieve the contents of an order based on its unique identifier, <i>orderId</i>. This value was returned in the <b> getOrders</b> call's <b>orders.orderId</b> field when you searched for orders by creation date, modification date, or fulfillment status. Include the optional <b>fieldGroups</b> query parameter set to <code>TAX_BREAKDOWN</code> to return a breakdown of the taxes and fees. <br /><br /> The returned <b>Order</b> object contains information you can use to create and process fulfillments, including: <ul> <li>Information about the buyer and seller</li> <li>Information about the order's line items</li> <li> The plans for packaging, addressing and shipping the order</li> <li>The status of payment, packaging, addressing, and shipping the order</li> <li>A summary of monetary amounts specific to the order such as pricing, payments, and shipping costs</li> <li>A summary of applied taxes and fees, and optionally a breakdown of each </li></ul>  # noqa: E501

        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the <b>getOrders</b> method in the <b>orders.orderId</b> field. <br/><br/><span class=\"tablenote\"><strong>Note:</strong> A new order ID format was introduced to all eBay APIs (legacy and REST) in June 2019. In REST APIs that return Order IDs, including the Fulfillment API, all order IDs are returned in the new format, but the <strong>getOrder</strong> method will accept both the legacy and new format order ID. The new format is a non-parsable string, globally unique across all eBay marketplaces, and consistent for both single line item and multiple line item orders. These order identifiers will be automatically generated after buyer payment, and unlike in the past, instead of just being known and exposed to the seller, these unique order identifiers will also be known and used/referenced by the buyer and eBay customer support. </span> (required)
        :param str field_groups: The response type associated with the order. The only presently supported value is <code>TAX_BREAKDOWN</code>. This type returns a breakdown of tax and fee values associated with the order.
        :return: Order
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.OrderApi, sell_fulfillment.ApiClient, 'get_order', SellFulfillmentException, True, ['sell.fulfillment', 'order'], order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_orders(self, **kwargs):  # noqa: E501
        """get_orders  # noqa: E501

        Use this call to search for and retrieve one or more orders based on their creation date, last modification date, or fulfillment status using the <b>filter</b> parameter. You can alternatively specify a list of orders using the <b>orderIds</b> parameter. Include the optional <b>fieldGroups</b> query parameter set to <code>TAX_BREAKDOWN</code> to return a breakdown of the taxes and fees. <br /><br /> The returned <b>Order</b> objects contain information you can use to create and process fulfillments, including: <ul> <li>Information about the buyer and seller</li> <li>Information about the order's line items</li> <li>The plans for packaging, addressing and shipping the order</li> <li>The status of payment, packaging, addressing, and shipping the order</li> <li>A summary of monetary amounts specific to the order such as pricing, payments, and shipping costs</li> <li>A summary of applied taxes and fees, and optionally a breakdown of each </li></ul> <br /><br /> <span class=\"tablenote\"><strong>Important:</strong> In this call, the <b>cancelStatus.cancelRequests</b> array is returned but is always empty. Use the <b>getOrder</b> call instead, which returns this array fully populated with information about any cancellation requests.</span>  # noqa: E501

        :param str field_groups: The response type associated with the order. The only presently supported value is <code>TAX_BREAKDOWN</code>. This type returns a breakdown of tax and fee values associated with the order.
        :param str filter: One or more comma-separated criteria for narrowing down the collection of orders returned by this call. These criteria correspond to specific fields in the response payload. Multiple filter criteria combine to further restrict the results. <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> Currently, <b>filter</b> returns data from only the last 90 days. If the <b>orderIds</b> parameter is included in the request, the <b>filter</b> parameter will be ignored.</span> <br /><br /> The available criteria are as follows: <dl> <dt><code><b>creationdate</b></code></dt> <dd>The time period during which qualifying orders were created (the <b>orders.creationDate</b> field). In the URI, this is expressed as a starting timestamp, with or without an ending timestamp (in brackets). The timestamps are in ISO 8601 format, which uses the 24-hour Universal Coordinated Time (UTC) clock.For example: <ul> <li><code>creationdate:[2016-02-21T08:25:43.511Z..]</code> identifies orders created on or after the given timestamp.</li> <li><code>creationdate:[2016-02-21T08:25:43.511Z..2016-04-21T08:25:43.511Z]</code> identifies orders created between the given timestamps, inclusive.</li> </ul> </dd> <dt><code><b>lastmodifieddate</b></code></dt> <dd>The time period during which qualifying orders were last modified (the <b>orders.modifiedDate</b> field).  In the URI, this is expressed as a starting timestamp, with or without an ending timestamp (in brackets). The timestamps are in ISO 8601 format, which uses the 24-hour Universal Coordinated Time (UTC) clock.For example: <ul> <li><code>lastmodifieddate:[2016-05-15T08:25:43.511Z..]</code> identifies orders modified on or after the given timestamp.</li> <li><code>lastmodifieddate:[2016-05-15T08:25:43.511Z..2016-05-31T08:25:43.511Z]</code> identifies orders modified between the given timestamps, inclusive.</li> </ul> <span class=\"tablenote\"><strong>Note:</strong> If <b>creationdate</b> and <b>lastmodifieddate</b> are both included, only <b>creationdate</b> is used.</span> <br /><br /></dd> <dt><code><b>orderfulfillmentstatus</b></code></dt> <dd>The degree to which qualifying orders have been shipped (the <b>orders.orderFulfillmentStatus</b> field). In the URI, this is expressed as one of the following value combinations: <ul> <li><code>orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS}</code> specifies orders for which no shipping fulfillments have been started, plus orders for which at least one shipping fulfillment has been started but not completed.</li> <li><code>orderfulfillmentstatus:{FULFILLED|IN_PROGRESS}</code> specifies orders for which all shipping fulfillments have been completed, plus orders for which at least one shipping fulfillment has been started but not completed.</li> </ul> <span class=\"tablenote\"><strong>Note:</strong> The values <code>NOT_STARTED</code>, <code>IN_PROGRESS</code>, and <code>FULFILLED</code> can be used in various combinations, but only the combinations shown here are currently supported.</span> </dd> </dl> Here is an example of a <b>getOrders</b> call using all of these filters: <br /><br /> <code>GET https://api.ebay.com/sell/v1/order?<br />filter=<b>creationdate</b>:%5B2016-03-21T08:25:43.511Z..2016-04-21T08:25:43.511Z%5D,<br /><b>lastmodifieddate</b>:%5B2016-05-15T08:25:43.511Z..%5D,<br /><b>orderfulfillmentstatus</b>:%7BNOT_STARTED%7CIN_PROGRESS%7D</code> <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> This call requires that certain special characters in the URI query string be percent-encoded: <br /> &nbsp;&nbsp;&nbsp;&nbsp;<code>[</code> = <code>%5B</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>]</code> = <code>%5D</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>{</code> = <code>%7B</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>|</code> = <code>%7C</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>}</code> = <code>%7D</code> <br /> This query filter example uses these codes.</span> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/fulfillment/types/api:FilterField
        :param str limit: The number of orders to return per page of the result set. Use this parameter in conjunction with the <b>offset</b> parameter to control the pagination of the output. <br /><br />For example, if <b>offset</b> is set to <code>10</code> and <b>limit</b> is set to <code>10</code>, the call retrieves orders 11 thru 20 from the result set. <br /><br /> If a limit is not set, the <b>limit</b> defaults to 50 and returns up to 50 orders. If a requested limit is more than 200, the call fails and returns an error.<br ><br> <span class=\"tablenote\"><strong>Note:</strong> This feature employs a zero-based list, where the first item in the list has an offset of <code>0</code>. If the <b>orderIds</b> parameter is included in the request, this parameter will be ignored.</span> <br /><br /> <b>Maximum:</b> <code>200</code> <br /> <b>Default:</b> <code>50</code>
        :param str offset: Specifies the number of orders to skip in the result set before returning the first order in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :param str order_ids: A comma-separated list of the unique identifiers of the orders to retrieve (maximum 50). If one or more order ID values are specified through the <b>orderIds</b> query parameter, all other query parameters will be ignored. <br/><br/><span class=\"tablenote\"><strong>Note:</strong> A new order ID format was introduced to all eBay APIs (legacy and REST) in June 2019. In REST APIs that return Order IDs, including the Fulfillment API, all order IDs are returned in the new format, but the <strong>getOrders</strong> method will accept both the legacy and new format order ID. The new format is a non-parsable string, globally unique across all eBay marketplaces, and consistent for both single line item and multiple line item orders. These order identifiers will be automatically generated after buyer payment, and unlike in the past, instead of just being known and exposed to the seller, these unique order identifiers will also be known and used/referenced by the buyer and eBay customer support. </span>
        :return: OrderSearchPagedCollection
        """
        try:
            return self._method_paged(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.OrderApi, sell_fulfillment.ApiClient, 'get_orders', SellFulfillmentException, True, ['sell.fulfillment', 'order'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_issue_refund(self, order_id, **kwargs):  # noqa: E501
        """Issue Refund  # noqa: E501


        :param str order_id: The unique identifier of the order. Order IDs are returned in the <b>getOrders</b> method (and <b>GetOrders</b> call of Trading API). The <b>issueRefund</b> method supports the legacy API Order IDs and REST API order IDs.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> In the Trading API (and other legacy APIs), Order IDs are transitioning to a new format. The new format is a non-parsable string, globally unique across all eBay marketplaces, and consistent for both single line item and multiple line item orders. These order identifiers will be automatically generated after buyer payment, and unlike in the past, instead of just being known and exposed to the seller, these unique order identifiers will also be known and used/referenced by the buyer and eBay customer support.<br/><br/>For developers and sellers who are already integrated with the Trading API's order management calls, this change shouldn't impact your integration unless you parse the existing order identifiers (e.g., <b>OrderID</b> or <b>OrderLineItemID</b>), or otherwise infer meaning from the format (e.g., differentiating between a single line item order versus a multiple line item order). Because we realize that some integrations may have logic that is dependent upon the identifier format, eBay is rolling out the Trading API change with version control to support a transition period of approximately 9 months before applications must switch to the new format completely. See the <a href=\"https://developer.ebay.com/devzone/XML/docs/Reference/eBay/GetOrders.html#Request.OrderIDArray.OrderID\" target=\"_blank\">OrderID field description</a> in the <b>GetOrders</b> call for more details and requirements on transitioning to the new Order ID format.</span> (required)
        :param IssueRefundRequest body:
        :return: Refund
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.OrderApi, sell_fulfillment.ApiClient, 'issue_refund', SellFulfillmentException, True, ['sell.fulfillment', 'order'], order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_accept_payment_dispute(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Accept Payment Dispute  # noqa: E501

        This method is used if the seller wishes to accept a payment dispute. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the <strong>getPaymentDisputeSummaries</strong> method.<br><br>The <strong>revision</strong> field in the request payload is required, and the <strong>returnAddress</strong> field should be supplied if the seller is expecting the buyer to return the item. See the Request Payload section for more information on theste fields.  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to accept. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response.<br><br>This path parameter is required, and the actual identifier value is passed in right after the <strong>payment_dispute</strong> resource. See the Resource URI above. (required)
        :param AcceptPaymentDisputeRequest body:
        :return: None
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'accept_payment_dispute', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_add_evidence(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Add an Evidence File  # noqa: E501

        This method is used by the seller to add one or more evidence files to address a payment dispute initiated by the buyer. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the <strong>getPaymentDisputeSummaries</strong> method.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> All evidence files should be uploaded using <strong>addEvidence</strong> and <strong>updateEvidence</strong>  before the seller decides to contest the payment dispute. Once the seller has officially contested the dispute (using <strong>contestPaymentDispute</strong> or through My eBay), the <strong>addEvidence</strong> and <strong>updateEvidence</strong> methods can no longer be used. In the <strong>evidenceRequests</strong> array of the <strong>getPaymentDispute</strong> response, eBay prompts the seller with the type of evidence file(s) that will be needed to contest the payment dispute.</span><br><br>The file(s) to add are identified through the <strong>files</strong> array in the request payload.  Adding one or more new evidence files for a payment dispute triggers the creation of an evidence file, and the unique identifier for the new evidence file is automatically generated and returned in the <strong>evidenceId</strong> field of the <strong>addEvidence</strong> response payload upon a successful call.<br><br>The type of evidence being added should be specified in the <strong>evidenceType</strong> field. All files being added (if more than one) should correspond to this evidence type.<br><br>Upon a successful call, an <strong>evidenceId</strong> value is returned in the response. This indicates that a new evidence set has been created for the payment dispute, and this evidence set includes the evidence file(s) that were passed in to the <strong>fileId</strong> array. The <strong>evidenceId</strong> value will be needed if the seller wishes to add to the evidence set by using the <strong>updateEvidence</strong> method, or if they want to retrieve a specific evidence file within the evidence set by using the <strong>fetchEvidenceContent</strong> method.  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to add evidence for a contested payment dispute. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response.<br><br>This path parameter is required, and the actual identifier value is passed in right after the <strong>payment_dispute</strong> resource. See the Resource URI above. (required)
        :param AddEvidencePaymentDisputeRequest body:
        :return: AddEvidencePaymentDisputeResponse
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'add_evidence', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_contest_payment_dispute(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Contest Payment Dispute  # noqa: E501

        This method is used if the seller wishes to contest a payment dispute initiated by the buyer. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the <strong>getPaymentDisputeSummaries</strong> method.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> Before contesting a payment dispute, the seller must upload all evidence files using the <strong>addEvidence</strong> and <strong>updateEvidence</strong> methods. Once the seller has officially contested the dispute (using <strong>contestPaymentDispute</strong>), the <strong>addEvidence</strong> and <strong>updateEvidence</strong> methods can no longer be used. In the <strong>evidenceRequests</strong> array of the <strong>getPaymentDispute</strong> response, eBay prompts the seller with the type of evidence file(s) that will be needed to contest the payment dispute.</span><br><br>If a seller decides to contest a payment dispute, that seller should be prepared to provide evidential documents such as proof of delivery, proof of authentication, or other documents. The type of evidential documents that the seller will provide will depend on why the buyer initiated the payment dispute.<br><br>The <strong>revision</strong> field in the request payload is required, and the <strong>returnAddress</strong> field should be supplied if the seller is expecting the buyer to return the item. See the Request Payload section for more information on theste fields.  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to contest. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response.<br><br>This path parameter is required, and the actual identifier value is passed in right after the <strong>payment_dispute</strong> resource. See the Resource URI above. (required)
        :param ContestPaymentDisputeRequest body:
        :return: None
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'contest_payment_dispute', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_fetch_evidence_content(self, payment_dispute_id, evidence_id, file_id, **kwargs):  # noqa: E501
        """Get Payment Dispute Evidence File  # noqa: E501

        This call retrieves a specific evidence file for a payment dispute. The following three identifying parameters are needed in the call URI:<ul><li><strong>payment_dispute_id</strong>: the identifier of the payment dispute. The identifier of each payment dispute is returned in the <strong>getPaymentDisputeSummaries</strong> response.</li><li><strong>evidence_id</strong>: the identifier of the evidential file set. The identifier of an evidential file set for a payment dispute is returned under the <strong>evidence</strong> array in the <strong>getPaymentDispute</strong> response.</li><li><strong>file_id</strong>: the identifier of an evidential file. This file must belong to the evidential file set identified through the <strong>evidence_id</strong> query parameter. The identifier of each evidential file is returned under the <strong>evidence.files</strong> array in the <strong>getPaymentDispute</strong> response.</li></ul><p>An actual binary file is returned if the call is successful. An error will occur if any of three identifiers are invalid.</p>  # noqa: E501

        :param str payment_dispute_id: The identifier of the payment dispute. The identifier of each payment dispute is returned in the <strong>getPaymentDisputeSummaries</strong> response. This identifier is passed in as a path parameter at the end of the call URI. (required)
        :param str evidence_id: The identifier of the evidential file set. The identifier of an evidential file set for a payment dispute is returned under the <strong>evidence</strong> array in the <strong>getPaymentDispute</strong> response.<br><br>Below is an example of the syntax to use for this query parameter:<br/><br/><code>evidence_id=12345678</code> (required)
        :param str file_id: The identifier of an evidential file. This file must belong to the evidential file set identified through the <strong>evidence_id</strong> query parameter. The identifier of each evidential file is returned under the <strong>evidence.files</strong> array in the <strong>getPaymentDispute</strong> response. <br><br>Below is an example of the syntax to use for this query parameter:<br/><br/><code>file_id=12345678</code>  (required)
        :return: list[str]
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'fetch_evidence_content', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], (payment_dispute_id, evidence_id, file_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_activities(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Get Payment Dispute Activity  # noqa: E501

        This method retrieve a log of activity for a payment dispute. The identifier of the payment dispute is passed in as a path parameter. The output includes a timestamp for each action of the payment dispute, from creation to resolution, and all steps in between.  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed in at the end of the call URI to identify the payment dispute for which the user wishes to see all activity. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response.<br><br>This path parameter is required, and the actual identifier value is passed in right after the <strong>payment_dispute</strong> resource. See the Resource URI above. (required)
        :return: PaymentDisputeActivityHistory
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'get_activities', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_payment_dispute(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Get Payment Dispute Details  # noqa: E501

        This method retrieves detailed information on a specific payment dispute. The payment dispute identifier is passed in as path parameter at the end of the call URI.<br/><br/>Below is a summary of the information that is retrieved:<ul><li>Current status of payment dispute</li><li>Amount of the payment dispute</li><li>Reason the payment dispute was opened</li><li>Order and line items associated with the payment dispute</li><li>Seller response options if an action is currently required on the payment dispute</li><li>Details on the results of the payment dispute if it has been closed</li><li>Details on any evidence that was provided by the seller to fight the payment dispute</li></ul>  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed in at the end of the call URI to identify the payment dispute to retrieve. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response. (required)
        :return: PaymentDispute
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'get_payment_dispute', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_payment_dispute_summaries(self, **kwargs):  # noqa: E501
        """Search Payment Dispute by Filters  # noqa: E501

        This method is used retrieve one or more payment disputes filed against the seller. These payment disputes can be open or recently closed. The following filter types are available in the request payload to control the payment disputes that are returned:<ul><li>Dispute filed against a specific order (<b>order_id</b> parameter is used)</li><li>Dispute(s) filed by a specific buyer (<b>buyer_username</b> parameter is used)</li><li>Dispute(s) filed within a specific date range (<b>open_date_from</b> and/or <b>open_date_to</b> parameters are used)</li><li>Disputes in a specific state (<b>payment_dispute_status</b> parameter is used)</li></ul>More than one of these filter types can be used together. See the request payload request fields for more information about how each filter is used.<br/><br/>If none of the filters are used, all open and recently closed payment disputes are returned.<br/><br/>Pagination is also available. See the <b>limit</b> and <b>offset</b> fields for more information on how pagination is used for this method.  # noqa: E501

        :param str order_id: This filter is used if the seller wishes to retrieve one or more payment disputes filed against a specific order. It is possible that there can be more than one dispute filed against an order if the order has multiple line items. If this filter is used, any other filters are ignored.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> The order identifier passed into this field must be an Order ID in the new format. The legacy APIs still support the old and new order ID format to identify orders, but only the new order ID format is supported in REST-based APIs. eBay rolled out a new Order ID format in June 2019.</span>
        :param str buyer_username: This filter is used if the seller wishes to retrieve one or more payment disputes opened by a specific seller. The string that is passed in to this query parameter is the eBay user ID of the buyer.
        :param str open_date_from: The <b>open_date_from</b> and/or <b>open_date_to</b> date filters are used if the seller wishes to retrieve payment disputes opened within a specific date range. A maximum date range that may be set with the <b>open_date_from</b> and/or <b>open_date_to</b> filters is 90 days. These date filters use the ISO-8601 24-hour date and time format, and time zone used is Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT), or Zulu.<br><br>The <b>open_date_from</b> field sets the beginning date of the date range, and can be set as far back as 18 months from the present time. If a <b>open_date_from</b> field is used, but a <b>open_date_to</b> field is not used, the <b>open_date_to</b> value will default to 90 days after the date specified in the <b>open_date_from</b> field, or to the present time if less than 90 days in the past.<br/><br/>The ISO-8601 format looks like this: <em>yyyy-MM-ddThh:mm.ss.sssZ</em>. An example would be <code>2019-08-04T19:09:02.768Z</code>.
        :param str open_date_to: The <b>open_date_from</b> and/or <b>open_date_to</b> date filters are used if the seller wishes to retrieve payment disputes opened within a specific date range. A maximum date range that may be set with the <b>open_date_from</b> and/or <b>open_date_to</b> filters is 90 days. These date filters use the ISO-8601 24-hour date and time format, and the time zone used is Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT), or Zulu.<br><br>The <b>open_date_to</b> field sets the ending date of the date range, and can be set up to 90 days from the date set in the <b>open_date_from</b> field. <br/><br/>The ISO-8601 format looks like this: <em>yyyy-MM-ddThh:mm.ss.sssZ</em>. An example would be <code>2019-08-04T19:09:02.768Z</code>.
        :param str payment_dispute_status: This filter is used if the seller wishes to only retrieve payment disputes in a specific state. More than one value can be specified. If no <b>payment_dispute_status</b> filter is used, payment disputes in all states are returned in the response. See <strong>DisputeStateEnum</strong> type for supported values.
        :param str limit: The value passed in this query parameter sets the maximum number of payment disputes to return per page of data. The value passed in this field should be an integer from 1 to 200. If this query parameter is not set, up to 200 records will be returned on each page of results.<br><br><b>Min</b>: 1; <b>Max</b>: 200; <b>Default</b>: 200
        :param str offset: This field is used to specify the number of records to skip in the result set before returning the first payment dispute in the paginated response. A zero-based index is used, so if you set the <b>offset</b> value to <code>0</code> (default value), the first payment dispute in the result set appears at the top of the response. <br/><br/>Combine <b>offset</b> with the <b>limit</b> parameter to control the payment disputes returned in the response. For example, if you supply an <b>offset</b> value of <code>0</code> and a <b>limit</b> value of <code>10</code>, the response will contain the first 10 payment disputes from the result set that matches the input criteria. If you supply an <b>offset</b> value of <code>10</code> and a <b>limit</b> value of <code>20</code>, the response will contain payment disputes 11-30 from the result set that matches the input criteria.<br><br><b>Min</b>: 0; <b>Max</b>: total number of payment disputes - 1; <b>Default</b>: 0
        :return: DisputeSummaryResponse
        """
        try:
            return self._method_paged(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'get_payment_dispute_summaries', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_update_evidence(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Update evidence  # noqa: E501

        This method is used by the seller to update an existing evidence set for a payment dispute with one or more evidence files. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the <strong>getPaymentDisputeSummaries</strong> method.<br/><br/><span class=\"tablenote\"><strong>Note:</strong> All evidence files should be uploaded using <strong>addEvidence</strong> and <strong>updateEvidence</strong>  before the seller decides to contest the payment dispute. Once the seller has officially contested the dispute (using <strong>contestPaymentDispute</strong> or through My eBay), the <strong>addEvidence</strong> and <strong>updateEvidence</strong> methods can no longer be used. In the <strong>evidenceRequests</strong> array of the <strong>getPaymentDispute</strong> response, eBay prompts the seller with the type of evidence file(s) that will be needed to contest the payment dispute.</span><br><br>The unique identifier of the evidence set to update is specified through the <strong>evidenceId</strong> field, and the file(s) to add are identified through the <strong>files</strong> array in the request payload. The unique identifier for an evidence file is automatically generated and returned in the <strong>fileId</strong> field of the <strong>uploadEvidence</strong> response payload upon a successful call. Sellers must make sure to capture the <strong>fileId</strong> value for each evidence file that is uploaded with the <strong>uploadEvidence</strong> method.<br><br>The type of evidence being added should be specified in the <strong>evidenceType</strong> field.  All files being added (if more than one) should correspond to this evidence type.<br><br>Upon a successful call, an http status code of <code>204 Success</code> is returned. There is no response payload unless an error occurs. To verify that a new file is a part of the evidence set, the seller can use the <strong>fetchEvidenceContent</strong> method, passing in the proper <strong>evidenceId</strong> and <strong>fileId</strong> values.  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to update the evidence set for a contested payment dispute. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response.<br><br>This path parameter is required, and the actual identifier value is passed in right after the <strong>payment_dispute</strong> resource. See the Resource URI above. (required)
        :param UpdateEvidencePaymentDisputeRequest body:
        :return: None
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'update_evidence', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_upload_evidence_file(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Upload an Evidence File  # noqa: E501

        This method is used to upload an evidence file for a contested payment dispute. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the <strong>getPaymentDisputeSummaries</strong> method.<br><br>The <strong>uploadEvidenceFile</strong> only uploads an encrypted, binary image file (using multipart/form-data HTTP request header), and does not have a request payload. The three image formats supported at this time are .JPEG, .JPG, and .PNG.<br><br>Once the file is successfully uploaded, the seller will need to grab the <strong>fileId</strong> value in the response payload to add this file to a new evidence set using the <strong>addEvidence</strong> method, or to add this file to an existing evidence set using the <strong>updateEvidence</strong> method.  # noqa: E501

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to upload an evidence file. This identifier is automatically created by eBay once the payment dispute comes into the eBay managed payments system. The unique identifier for payment disputes is returned in the <strong>paymentDisputeId</strong> field in the <strong>getPaymentDisputeSummaries</strong> response.<br><br>This path parameter is required, and the actual identifier value is passed in right after the <strong>payment_dispute</strong> resource. See the Resource URI above. (required)
        :return: FileEvidence
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'upload_evidence_file', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_create_shipping_fulfillment(self, body, order_id, **kwargs):  # noqa: E501
        """create_shipping_fulfillment  # noqa: E501

        When you group an order's line items into one or more packages, each package requires a corresponding plan for handling, addressing, and shipping; this is a <i>shipping fulfillment</i>. For each package, execute this call once to generate a shipping fulfillment associated with that package. <br /><br /> <span class=\"tablenote\"><strong>Note:</strong> A single line item in an order can consist of multiple units of a purchased item, and one unit can consist of multiple parts or components. Although these components might be provided by the manufacturer in separate packaging, the seller must include all components of a given line item in the same package.</span> <br /><br />Before using this call for a given package, you must determine which line items are in the package. If the package has been shipped, you should provide the date of shipment in the request. If not provided, it will default to the current date and time.  # noqa: E501

        :param ShippingFulfillmentDetails body: fulfillment payload (required)
        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the <b>getOrders</b> method in the <b>orders.orderId</b> field. <br/><br/><span class=\"tablenote\"><strong>Note:</strong> A new order ID format was introduced to all eBay APIs (legacy and REST) in June 2019. In REST APIs that return Order IDs, including the Fulfillment API, all order IDs are returned in the new format, but the <strong>createShippingFulfillment</strong> method will accept both the legacy and new format order ID. The new format is a non-parsable string, globally unique across all eBay marketplaces, and consistent for both single line item and multiple line item orders. These order identifiers will be automatically generated after buyer payment, and unlike in the past, instead of just being known and exposed to the seller, these unique order identifiers will also be known and used/referenced by the buyer and eBay customer support. </span> (required)
        :return: object
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.ShippingFulfillmentApi, sell_fulfillment.ApiClient, 'create_shipping_fulfillment', SellFulfillmentException, True, ['sell.fulfillment', 'shipping_fulfillment'], (body, order_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_shipping_fulfillment(self, fulfillment_id, order_id, **kwargs):  # noqa: E501
        """get_shipping_fulfillment  # noqa: E501

        Use this call to retrieve the contents of a fulfillment based on its unique identifier, <b>fulfillmentId</b> (combined with the associated order's <b>orderId</b>). The <b>fulfillmentId</b> value was originally generated by the <b>createShippingFulfillment</b> call, and is returned by the <b>getShippingFulfillments</b> call in the <b>members.fulfillmentId</b> field.  # noqa: E501

        :param str fulfillment_id: The unique identifier of the fulfillment. This eBay-generated value was created by the <b>Create Shipping Fulfillment</b> call, and returned by the <b>getShippingFulfillments</b> call in the <b>fulfillments.fulfillmentId</b> field; for example, <code>9405509699937003457459</code>. (required)
        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the <b>getOrders</b> method in the <b>orders.orderId</b> field. <br/><br/><span class=\"tablenote\"><strong>Note:</strong> A new order ID format was introduced to all eBay APIs (legacy and REST) in June 2019. In REST APIs that return Order IDs, including the Fulfillment API, all order IDs are returned in the new format, but the <strong>getShippingFulfillment</strong> method will accept both the legacy and new format order ID. The new format is a non-parsable string, globally unique across all eBay marketplaces, and consistent for both single line item and multiple line item orders. These order identifiers will be automatically generated after buyer payment, and unlike in the past, instead of just being known and exposed to the seller, these unique order identifiers will also be known and used/referenced by the buyer and eBay customer support. </span> (required)
        :return: ShippingFulfillment
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.ShippingFulfillmentApi, sell_fulfillment.ApiClient, 'get_shipping_fulfillment', SellFulfillmentException, True, ['sell.fulfillment', 'shipping_fulfillment'], (fulfillment_id, order_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_shipping_fulfillments(self, order_id, **kwargs):  # noqa: E501
        """get_shipping_fulfillments  # noqa: E501

        Use this call to retrieve the contents of all fulfillments currently defined for a specified order based on the order's unique identifier, <b>orderId</b>. This value is returned in the <b>getOrders</b> call's <b>members.orderId</b> field when you search for orders by creation date or shipment status.  # noqa: E501

        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the <b>getOrders</b> method in the <b>orders.orderId</b> field. <br/><br/><span class=\"tablenote\"><strong>Note:</strong> A new order ID format was introduced to all eBay APIs (legacy and REST) in June 2019. In REST APIs that return Order IDs, including the Fulfillment API, all order IDs are returned in the new format, but the <strong>getShippingFulfillments</strong> method will accept both the legacy and new format order ID. The new format is a non-parsable string, globally unique across all eBay marketplaces, and consistent for both single line item and multiple line item orders. These order identifiers will be automatically generated after buyer payment, and unlike in the past, instead of just being known and exposed to the seller, these unique order identifiers will also be known and used/referenced by the buyer and eBay customer support. </span> (required)
        :return: ShippingFulfillmentPagedCollection
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.ShippingFulfillmentApi, sell_fulfillment.ApiClient, 'get_shipping_fulfillments', SellFulfillmentException, True, ['sell.fulfillment', 'shipping_fulfillment'], order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_create_or_replace_inventory_item(self, body, **kwargs):  # noqa: E501
        """bulk_create_or_replace_inventory_item  # noqa: E501

        <span class=\"tablenote\"><strong>Note:</strong> Please note that any eBay listing created using the Inventory API cannot be revised or relisted using the Trading API calls.</span><br/><br/>This call can be used to create and/or update up to 25 new inventory item records. It is up to sellers whether they want to create a complete inventory item records right from the start, or sellers can provide only some information with the initial <strong>bulkCreateOrReplaceInventoryItem</strong> call, and then make one or more additional <strong>bulkCreateOrReplaceInventoryItem</strong> calls to complete all required fields for the inventory item records and prepare for publishing. Upon first creating inventory item records, only the SKU values are required. <br/><br/> In the case of updating existing inventory item records, the <strong>bulkCreateOrReplaceInventoryItem</strong> call will do a complete replacement of the existing inventory item records, so all fields that are currently defined for the inventory item record are required in that update action, regardless of whether their values changed. So, when replacing/updating an inventory item record, it is advised that the seller run a 'Get' call to retrieve the full details of the inventory item records and see all of its current values/settings before attempting to update the records. Any changes that are made to inventory item records that are part of one or more active eBay listings, a successful call will automatically update these active listings. <br/><br/> The key information that is set with the <strong>bulkCreateOrReplaceInventoryItem</strong> call include: <ul> <li>Seller-defined SKU value for the product. Each seller product, including products within an item inventory group, must have their own SKU value. </li> <li>Condition of the item</li> <li>Product details, including any product identifier(s), such as a UPC, ISBN, EAN, or Brand/Manufacturer Part Number pair, a product description, a product title, product/item aspects, and links to images. eBay will use any supplied eBay Product ID (ePID) or a GTIN (UPC, ISBN, or EAN) and attempt to match those identifiers to a product in the eBay Catalog, and if a product match is found, the product details for the inventory item will automatically be populated.</li> <li>Quantity of the inventory item that is available for purchase</li> <li>Package weight and dimensions, which is required if the seller will be offering calculated shipping options. The package weight will also be required if the seller will be providing flat-rate shipping services, but charging a weight surcharge.</li> </ul> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>bulkCreateOrReplaceInventoryItem</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p><p>For those who prefer to create or update a single inventory item record, the <strong>createOrReplaceInventoryItem</strong> method can be used.</p>  # noqa: E501

        :param BulkInventoryItem body: Details of the inventories with sku and locale (required)
        :return: BulkInventoryItemResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'bulk_create_or_replace_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_get_inventory_item(self, body, **kwargs):  # noqa: E501
        """bulk_get_inventory_item  # noqa: E501

        This call retrieves up to 25 inventory item records. The SKU value of each inventory item record to retrieve is specified in the request payload. <br/><br/>The <code>authorization</code> header is the only required HTTP header for this call, and it is required for all Inventory API calls. See the <strong>HTTP request headers</strong> section for more information.<br/><br/>For those who prefer to retrieve only one inventory item record by SKU value, , the <strong>getInventoryItem</strong> method can be used. To retrieve all inventory item records defined on the seller's account, the <strong>getInventoryItems</strong> method can be used (with pagination control if desired).  # noqa: E501

        :param BulkGetInventoryItem body: Details of the inventories with sku and locale (required)
        :return: BulkGetInventoryItemResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'bulk_get_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_update_price_quantity(self, body, **kwargs):  # noqa: E501
        """bulk_update_price_quantity  # noqa: E501

        This call is used by the seller to update the total ship-to-home quantity of one inventory item, and/or to update the price and/or quantity of one or more offers associated with one inventory item. Up to 25 offers associated with an inventory item may be updated with one <strong>bulkUpdatePriceQuantity</strong> call. Only one SKU (one product) can be updated per call.<br /><br />The <strong>getOffers</strong> call can be used to retrieve all offers associated with a SKU. The seller will just pass in the correct SKU value through the <strong>sku</strong> query parameter. To update an offer, the <strong>offerId</strong> value is required, and this value is returned in the <strong>getOffers</strong> call response. It is also useful to know which offers are unpublished and which ones are published. To get this status, look for the <strong>status</strong> value in the <strong>getOffers</strong> call response. Offers in the published state are live eBay listings, and these listings will be revised with a successful <strong>bulkUpdatePriceQuantity</strong> call.<br /><br />An issue will occur if duplicate <strong>offerId</strong> values are passed through the same <strong>offers</strong> container, or if one or more of the specified offers are associated with different products/SKUs.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> For multiple-variation listings, it is recommended that the <strong>bulkUpdatePriceQuantity</strong> call be used to update price and quantity information for each SKU within that multiple-variation listing instead of using <strong>createOrReplaceInventoryItem</strong> calls to update the price and quantity for each SKU. Just remember that only one SKU (one product variation) can be updated per call.</span><p>The <code>authorization</code> header is the only required HTTP header for this call. See the <strong>HTTP request headers</strong> section for more information.</p>  # noqa: E501

        :param BulkPriceQuantity body: Price and allocation details for the given SKU and Marketplace (required)
        :return: BulkPriceQuantityResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'bulk_update_price_quantity', SellInventoryException, True, ['sell.inventory', 'inventory_item'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_or_replace_inventory_item(self, body, content_language, sku, **kwargs):  # noqa: E501
        """create_or_replace_inventory_item  # noqa: E501

        <span class=\"tablenote\"><strong>Note:</strong> Please note that any eBay listing created using the Inventory API cannot be revised or relisted using the Trading API calls.</span><br/><br/>This call creates a new inventory item record or replaces an existing inventory item record. It is up to sellers whether they want to create a complete inventory item record right from the start, or sellers can provide only some information with the initial <strong>createOrReplaceInventoryItem</strong> call, and then make one or more additional <strong>createOrReplaceInventoryItem</strong> calls to complete all required fields for  the inventory item record and prepare it for publishing. Upon first creating an inventory item record, only the SKU value in the call path is required. <br/><br/> In the case of replacing an existing inventory item record, the <strong>createOrReplaceInventoryItem</strong> call will do a complete replacement of the existing inventory item record, so all fields that are currently defined for the inventory item record are required in that update action, regardless of whether their values changed. So, when replacing/updating an inventory item record, it is advised that the seller run a <strong>getInventoryItem</strong> call to retrieve the full inventory item record and see all of its current values/settings before attempting to update the record. And if changes are made to an inventory item that is part of one or more active eBay listings, a successful call will automatically update these eBay listings. <br/><br/> The key information that is set with the <strong>createOrReplaceInventoryItem</strong> call include: <ul> <li>Seller-defined SKU value for the product. Each seller product, including products within an item inventory group, must have their own SKU value. This SKU value is passed in at the end of the call URI</li> <li>Condition of the item</li> <li>Product details, including any product identifier(s), such as a UPC, ISBN, EAN, or Brand/Manufacturer Part Number pair, a product description, a product title, product/item aspects, and links to images. eBay will use any supplied eBay Product ID (ePID) or a GTIN (UPC, ISBN, or EAN) and attempt to match those identifiers to a product in the eBay Catalog, and if a product match is found, the product details for the inventory item will automatically be populated.</li> <li>Quantity of the inventory item that is available for purchase</li> <li>Package weight and dimensions, which is required if the seller will be offering calculated shipping options. The package weight will also be required if the seller will be providing flat-rate shipping services, but charging a weight surcharge.</li> </ul> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>createOrReplaceInventoryItem</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p><p>For those who prefer to create or update numerous inventory item records with one call (up to 25 at a time), the <strong>bulkCreateOrReplaceInventoryItem</strong> method can be used.</p>  # noqa: E501

        :param InventoryItem body: Details of the inventory item record. (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :param str sku: The seller-defined SKU value for the inventory item is required whether the seller is creating a new inventory item, or updating an existing inventory item. This SKU value is passed in at the end of the call URI. SKU values must be unique across the seller's inventory. <br/><br/> <strong>Max length</strong>: 50. (required)
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'create_or_replace_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], (body, content_language, sku), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_inventory_item(self, sku, **kwargs):  # noqa: E501
        """delete_inventory_item  # noqa: E501

        This call is used to delete an inventory item record associated with a specified SKU. A successful call will not only delete that inventory item record, but will also have the following effects:<ul><li>Delete any and all unpublished offers associated with that SKU;</li><li>Delete any and all single-variation eBay listings associated with that SKU;</li><li>Automatically remove that SKU from a multiple-variation listing and remove that SKU from any and all inventory item groups in which that SKU was a member.</li></ul><p>The <code>authorization</code> header is the only required HTTP header for this call. See the <strong>HTTP request headers</strong> section for more information.</p>  # noqa: E501

        :param str sku: This is the seller-defined SKU value of the product whose inventory item record you wish to delete.<br/><br/><strong>Max length</strong>: 50. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'delete_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_item(self, sku, **kwargs):  # noqa: E501
        """get_inventory_item  # noqa: E501

        This call retrieves the inventory item record for a given SKU. The SKU value is passed in at the end of the call URI. There is no request payload for this call.<br/><br/>The <code>authorization</code> header is the only required HTTP header for this call, and it is required for all Inventory API calls. See the <strong>HTTP request headers</strong> section for more information.<br/><br/>For those who prefer to retrieve numerous inventory item records by SKU value with one call (up to 25 at a time), the <strong>bulkGetInventoryItem</strong> method can be used. To retrieve all inventory item records defined on the seller's account, the <strong>getInventoryItems</strong> method can be used (with pagination control if desired).  # noqa: E501

        :param str sku: This is the seller-defined SKU value of the product whose inventory item record you wish to retrieve.<br/><br/><strong>Max length</strong>: 50. (required)
        :return: InventoryItemWithSkuLocaleGroupid
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'get_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_items(self, **kwargs):  # noqa: E501
        """get_inventory_items  # noqa: E501

        This call retrieves all inventory item records defined for the seller's account. The <strong>limit</strong> query parameter allows the seller to control how many records are returned per page, and the <strong>offset</strong> query parameter is used to retrieve a specific page of records. The seller can make multiple calls to scan through multiple pages of records. There is no request payload for this call.<br/><br/>The <code>authorization</code> header is the only required HTTP header for this call, and it is required for all Inventory API calls. See the <strong>HTTP request headers</strong> section for more information.<br/><br/>For those who prefer to retrieve numerous inventory item records by SKU value with one call (up to 25 at a time), the <strong>bulkGetInventoryItem</strong> method can be used.  # noqa: E501

        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be an integer  from <code>1</code> to <code>100</code>. If this query parameter is not set, up to 100 records will be returned on each page of results.<br/><br/><strong>Min</strong>: 1, <strong>Max</strong>: 100 
        :param str offset: The value passed in this query parameter sets the page number to retrieve. The first page of records has a value of <code>0</code>, the second page of records has a value of <code>1</code>, and so on. If this query parameter is not set, its value defaults to <code>0</code>, and the first page of records is returned. 
        :return: InventoryItems
        """
        try:
            return self._method_paged(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'get_inventory_items', SellInventoryException, True, ['sell.inventory', 'inventory_item'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_or_replace_inventory_item_group(self, body, content_language, inventory_item_group_key, **kwargs):  # noqa: E501
        """create_or_replace_inventory_item_group  # noqa: E501

        This call creates a new inventory item group or updates an existing inventory item group. It is up to sellers whether they want to create a complete inventory item group record right from the start, or sellers can provide only some information with the initial <strong>createOrReplaceInventoryItemGroup</strong> call, and then make one or more additional <strong>createOrReplaceInventoryItemGroup</strong> calls to complete the inventory item group record. Upon first creating an inventory item group record, the only required elements are  the <strong>inventoryItemGroupKey</strong> identifier in the call URI, and the members of the inventory item group specified through the <strong>variantSKUs</strong> array in the request payload. <br><br>In the case of updating/replacing an existing inventory item group, this call does a complete replacement of the existing inventory item group record, so all fields (including the member SKUs) that make up the inventory item group are required, regardless of whether their values changed. So, when replacing/updating an inventory item group record, it is advised that the seller run a <strong>getInventoryItemGroup</strong> call for that inventory item group to see all of its current values/settings/members before attempting to update the record. And if changes are made to an inventory item group that is part of a live, multiple-variation eBay listing, these changes automatically update the eBay listing. For example, if a SKU value is removed from the inventory item group, the corresponding product variation will be removed from the eBay listing as well.<br/><br/> In addition to the required inventory item group identifier and member SKUs, other key information that is set with this call include: <ul> <li>Title and description of the inventory item group. The string values provided in these fields will actually become the listing title and listing description of the listing once the first SKU of the inventory item group is published successfully</li> <li>Common aspects that inventory items in the qroup share</li> <li>Product aspects that vary within each product variation</li> <li>Links to images demonstrating the variations of the product, and these images should correspond to the product aspect that is set with the <strong>variesBy.aspectsImageVariesBy</strong> field</li> </ul> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>createOrReplaceInventoryItemGroup</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p>  # noqa: E501

        :param InventoryItemGroup body: Details of the inventory Item Group (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :param str inventory_item_group_key: Unique identifier of the inventory item group. This identifier is supplied by the seller. The <strong>inventoryItemGroupKey</strong> value for the inventory item group to create/update is passed in at the end of the call URI. This value cannot be changed once it is set. (required)
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemGroupApi, sell_inventory.ApiClient, 'create_or_replace_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'inventory_item_group'], (body, content_language, inventory_item_group_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_inventory_item_group(self, inventory_item_group_key, **kwargs):  # noqa: E501
        """delete_inventory_item_group  # noqa: E501

        This call deletes the inventory item group for a given <strong>inventoryItemGroupKey</strong> value.  # noqa: E501

        :param str inventory_item_group_key: The unique identifier of an inventory item group. This value is assigned by the seller when an inventory item group is created. The <strong>inventoryItemGroupKey</strong> value for the inventory item group to delete is passed in at the end of the call URI. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemGroupApi, sell_inventory.ApiClient, 'delete_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'inventory_item_group'], inventory_item_group_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_item_group(self, inventory_item_group_key, **kwargs):  # noqa: E501
        """get_inventory_item_group  # noqa: E501

        This call retrieves the inventory item group for a given <strong>inventoryItemGroupKey</strong> value. The <strong>inventoryItemGroupKey</strong> value is passed in at the end of the call URI.  # noqa: E501

        :param str inventory_item_group_key: The unique identifier of an inventory item group. This value is assigned by the seller when an inventory item group is created. The <strong>inventoryItemGroupKey</strong> value for the inventory item group to retrieve is passed in at the end of the call URI. (required)
        :return: InventoryItemGroup
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemGroupApi, sell_inventory.ApiClient, 'get_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'inventory_item_group'], inventory_item_group_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_migrate_listing(self, body, **kwargs):  # noqa: E501
        """bulk_migrate_listing  # noqa: E501

        This call is used to convert existing eBay Listings to the corresponding Inventory API objects. If an eBay listing is successfully migrated to the Inventory API model, new Inventory Location, Inventory Item, and Offer objects are created. For a multiple-variation listing that is successfully migrated, in addition to the three new Inventory API objects just mentioned, an Inventory Item Group object will also be created. If the eBay listing is a motor vehicle part or accessory listing with a compatible vehicle list (<strong>ItemCompatibilityList</strong> container in Trading API's Add/Revise/Relist/Verify calls), a Product Compatibility object will be created.<br/><br/><h3>Migration Requirements</h3><br/>To be eligible for migration, the active eBay listings must meet the following requirements:<ul><li>Listing type is Fixed-Price<p><span class=\"tablenote\"><strong>Note:</strong> Auction listings are supported by the Inventory API, but the <b>bulkMigrateListing</b> method cannot be used to migrate auction listings.</span></p></li><li>The item(s) in the listings must have seller-defined SKU values associated with them, and in the case of a multiple-variation listing, each product variation must also have its own SKU value</li><li>Business Polices (Payment, Return Policy, and Shipping) must be used on the listing, as legacy payment, return policy, and shipping fields will not be accepted. With the Payment Policy associated with a listing, the immediate payment requirement must be enabled.</li><li>The postal/zip code (<strong>PostalCode</strong> field in Trading's <strong>ItemType</strong>) or city (<strong>Location</strong> field in Trading's <strong>ItemType</strong>) must be set in the listing; the country is also needed, but this value is required in Trading API, so it will always be set for every listing</li></ul><br /><h3>Unsupported Listing Features</h3><br/>The following features are not yet available to be set or modified through the Inventory API, but they will remain on the active eBay listing, even after a successful migration to the Inventory model. The downside to this is that the seller will be completely blocked (in APIs or My eBay) from revising these features/settings once the migration takes place:<ul><li>Any listing-level Buyer Requirements</li><li>Listing enhancements like a bold listing title or Gallery Plus</li></ul><br /><h3>Making the Call</h3><br/>In the request payload of the <strong>bulkMigrateListings</strong> call, the seller will pass in an array of one to five eBay listing IDs (aka Item IDs). To save time and hassle, that seller should do a pre-check on each listing to make sure those listings meet the requirements to be migrated to the new Inventory model. There are no path or query parameters for this call.<br/><br/><h3>Call Response</h3><br/>If an eBay listing is migrated successfully to the new Inventory model, the following will occur:<ul><li>An Inventory Item object will be created for the item(s) in the listing, and this object will be accessible through the Inventory API</li><li>An Offer object will be created for the listing, and this object will be accessible through the Inventory API</li><li>An Inventory Location object will be created and associated with the Offer object, as an Inventory Location must be associated with a published Offer</li></ul>The response payload of the Bulk Migrate Listings call will show the results of each listing migration. These results include an HTTP status code to indicate the success or failure of each listing migration, the SKU value associated with each item, and if the migration is successful, an Offer ID value. The SKU value will be used in the Inventory API to manage the Inventory Item object, and the Offer ID value will be used in the Inventory API to manage the Offer object. Errors and/or warnings containers will be returned for each listing where an error and/or warning occurred with the attempted migration.<br/><br/>If a multiple-variation listing is successfully migrated, along with the Offer and Inventory Location objects, an Inventory Item object will be created for each product variation within the listing, and an Inventory Item Group object will also be created, grouping those variations together in the Inventory API platform. For a motor vehicle part or accessory listing that has a specified list of compatible vehicles, in addition to the Inventory Item, Inventory Location, and Offer objects that are created, a Product Compatibility object will also be created in the Inventory API platform.  # noqa: E501

        :param BulkMigrateListing body: Details of the listings that needs to be migrated into Inventory (required)
        :return: BulkMigrateListingResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ListingApi, sell_inventory.ApiClient, 'bulk_migrate_listing', SellInventoryException, True, ['sell.inventory', 'listing'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_inventory_location(self, body, merchant_location_key, **kwargs):  # noqa: E501
        """create_inventory_location  # noqa: E501

        <p>Use this call to create a new inventory location. In order to create and publish an offer (and create an eBay listing), a seller must have at least one inventory location, as every offer must be associated with a location.</p><p>Upon first creating an inventory location, only a seller-defined location identifier and a physical location is required, and once set, these values can not be changed. The unique identifier value (<i>merchantLocationKey</i>) is passed in at the end of the call URI. This <i>merchantLocationKey</i> value will be used in other Inventory Location calls to identify the inventory location to perform an action against.</p><p>At this time, location types are either warehouse or store. Warehouse locations are used for traditional shipping, and store locations are generally used by US merchants selling products through the In-Store Pickup program, or used by UK, Australian, and German merchants selling products through the Click and Collect program. A full address is required for store inventory locations. However, for warehouse inventory locations, a full street address is not needed, but the city, state/province, and country of the location must be provided. </p><p>Note that all inventory locations are \"enabled\" by default when they are created, and you must specifically disable them (by passing in a value of <code>DISABLED</code> in the <strong>merchantLocationStatus</strong> field) if you want them to be set to the disabled state. The seller's inventory cannot be loaded to inventory locations in the disabled state.</p> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the following table includes another request header that is mandatory for the <strong>createInventoryLocation</strong> call, and two other request headers that are optional:</p><br> <table> <tr> <th>Header</th> <th>Description</th> <th>Required?</th> <th>Applicable Values</th> </tr> <tr> <td><code>Accept</code></td> <td>Describes the response encoding, as required by the caller. Currently, the interfaces require payloads formatted in JSON, and JSON is the default.</td> <td>No</td> <td><code>application/json</code></td> </tr> <tr> <td><code>Content-Language</code></td> <td>Use this header to control the language that is used for any returned errors or warnings in the call response.</td> <td>No</td> <td><code>en-US</code></td> </tr> <tr> <td><code>Content-Type</code></td> <td>The MIME type of the body of the request. Must be JSON.</td> <td>Yes</td> <td><code>application/json</code></td> </tr> </table></p><br/><p>Unless one or more errors and/or warnings occur with the call, there is no response payload for this call. A successful call will return an HTTP status value of <i>204 No Content</i>.</p>  # noqa: E501

        :param InventoryLocationFull body: Inventory Location details (required)
        :param str merchant_location_key: A unique, merchant-defined key (ID) for an inventory location. This unique identifier, or key, is used in other Inventory API calls to identify an inventory location. <br><br><b>Max length</b>: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'create_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], (body, merchant_location_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """delete_inventory_location  # noqa: E501

        <p>This call deletes the inventory location that is specified in the <code>merchantLocationKey</code> path parameter. Note that deleting a location will not affect any active eBay listings associated with the deleted location, but the seller will not be able modify the offers associated with the inventory location once it is deleted.</p><p>The <code>authorization</code> HTTP header is the only required request header for this call. </p><p>Unless one or more errors and/or warnings occur with the call, there is no response payload for this call. A successful call will return an HTTP status value of <i>200 OK</i>.</p>  # noqa: E501

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in at the end of the call URI to indicate the inventory location to be deleted. <br><br><b>Max length</b>: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'delete_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_disable_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """disable_inventory_location  # noqa: E501

        <p>This call disables the inventory location that is specified in the <code>merchantLocationKey</code> path parameter. Sellers can not load/modify inventory to disabled inventory locations. Note that disabling an inventory location will not affect any active eBay listings associated with the disabled location, but the seller will not be able modify the offers associated with a disabled inventory location.</p><p>The <code>authorization</code> HTTP header is the only required request header for this call.</p><p>A successful call will return an HTTP status value of <i>200 OK</i>.</p>  # noqa: E501

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in through the call URI to disable the specified inventory location. <br><br><b>Max length</b>: 36 (required)
        :return: object
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'disable_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_enable_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """enable_inventory_location  # noqa: E501

        <p>This call enables a disabled inventory location that is specified in the <code>merchantLocationKey</code> path parameter. Once a disabled inventory location is enabled, sellers can start loading/modifying inventory to that inventory location. </p><p>The <code>authorization</code> HTTP header is the only required request header for this call.</p><p>A successful call will return an HTTP status value of <i>200 OK</i>.</p>  # noqa: E501

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in through the call URI to specify the disabled inventory location to enable. <br><br><b>Max length</b>: 36 (required)
        :return: object
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'enable_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """get_inventory_location  # noqa: E501

        This call retrieves all defined details of the inventory location that is specified by the <b>merchantLocationKey</b> path parameter. <p>The <code>authorization</code> HTTP header is the only required request header for this call. </p><p>A successful call will return an HTTP status value of <i>200 OK</i>.</p>  # noqa: E501

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in at the end of the call URI to specify the inventory location to retrieve. <br><br><b>Max length</b>: 36 (required)
        :return: InventoryLocationResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'get_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_locations(self, **kwargs):  # noqa: E501
        """get_inventory_locations  # noqa: E501

        This call retrieves all defined details for every inventory location associated with the seller's account. There are no required parameters for this call and no request payload. However, there are two optional query parameters, <strong>limit</strong> and <strong>offset</strong>. The <strong>limit</strong> query parameter sets the maximum number of inventory locations returned on one page of data, and the <strong>offset</strong> query parameter specifies the page of data to return. These query parameters are discussed more in the <strong>URI parameters</strong> table below. <p>The <code>authorization</code> HTTP header is the only required request header for this call. </p><p>A successful call will return an HTTP status value of <i>200 OK</i>.</p>  # noqa: E501

        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be a positive integer value. If this query parameter is not set, up to 100 records will be returned on each page of results. <br><br> <strong>Min</strong>: 1
        :param str offset: Specifies the number of locations to skip in the result set before returning the first location in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :return: LocationResponse
        """
        try:
            return self._method_paged(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'get_inventory_locations', SellInventoryException, True, ['sell.inventory', 'location'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_update_inventory_location(self, body, merchant_location_key, **kwargs):  # noqa: E501
        """update_inventory_location  # noqa: E501

        <p>Use this call to update non-physical location details for an existing inventory location. Specify the inventory location you want to update using the <b>merchantLocationKey</b> path parameter. <br><br>You can update the following text-based fields: <strong>name</strong>, <strong>phone</strong>, <strong>locationWebUrl</strong>, <strong>locationInstructions</strong> and <strong>locationAdditionalInformation</strong>. Whatever text is passed in for these fields in an <strong>updateInventoryLocation</strong> call will replace the current text strings defined for these fields. For store inventory locations, the operating hours and/or the special hours can also be updated. <br><br> The merchant location key, the physical location of the store, and its geo-location coordinates can not be updated with an <strong>updateInventoryLocation</strong> call </p><p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the following table includes another request header that is mandatory for the <strong>updateInventoryLocation</strong> call, and two other request headers that are optional:</p><br> <table> <tr> <th>Header</th> <th>Description</th> <th>Required?</th> <th>Applicable Values</th> </tr> <tr> <td><code>Accept</code></td> <td>Describes the response encoding, as required by the caller. Currently, the interfaces require payloads formatted in JSON, and JSON is the default.</td> <td>No</td> <td><code>application/json</code></td> </tr> <tr> <td><code>Content-Language</code></td> <td>Use this header to control the language that is used for any returned errors or warnings in the call response.</td> <td>No</td> <td><code>en-US</code></td> </tr> <tr> <td><code>Content-Type</code></td> <td>The MIME type of the body of the request. Must be JSON.</td> <td>Yes</td> <td><code>application/json</code></td> </tr> </table><br/><p>Unless one or more errors and/or warnings occurs with the call, there is no response payload for this call. A successful call will return an HTTP status value of <i>204 No Content</i>.</p>  # noqa: E501

        :param InventoryLocation body: The inventory location details to be updated (other than the address and geo co-ordinates). (required)
        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in the call URI to indicate the inventory location to be updated. <br><br><b>Max length</b>: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'update_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], (body, merchant_location_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_create_offer(self, body, **kwargs):  # noqa: E501
        """bulk_create_offer  # noqa: E501

        This call creates multiple offers (up to 25) for specific inventory items on a specific eBay marketplace. Although it is not a requirement for the seller to create complete offers (with all necessary details) right from the start, eBay recommends that the seller provide all necessary details with this call since there is currently no bulk operation available to update multiple offers with one call. The following fields are always required in the request payload:  <strong>sku</strong>, <strong>marketplaceId</strong>, and (listing) <strong>format</strong>. <br><br>Other information that will be required before a offer can be published are highlighted below: <ul><li>Inventory location</li> <li>Offer price</li> <li>Available quantity</li> <li>eBay listing category</li> <li>Referenced listing policy profiles to set payment, return, and fulfillment values/settings</li> </ul><p><span class=\"tablenote\"><strong>Note:</strong> Though the <strong>includeCatalogProductDetails</strong> parameter is not required to be submitted in the request, the parameter defaults to <code>true</code> if omitted.</span></p> <p>If the call is successful, unique <strong>offerId</strong> values are returned in the response for each successfully created offer. The <strong>offerId</strong> value will be required for many other offer-related calls. Note that this call only stages an offer for publishing. The seller must run either the <strong>publishOffer</strong>, <strong>bulkPublishOffer</strong>, or <strong>publishOfferByInventoryItemGroup</strong> call to convert offer(s) into an active single- or multiple-variation listing.</p> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>bulkCreateOffer</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p><p>For those who prefer to create a single offer per call, the <strong>createOffer</strong> method can be used instead.</p>  # noqa: E501

        :param BulkEbayOfferDetailsWithKeys body: Details of the offer for the channel (required)
        :return: BulkOfferResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'bulk_create_offer', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_publish_offer(self, body, **kwargs):  # noqa: E501
        """bulk_publish_offer  # noqa: E501

        This call is used to convert unpublished offers (up to 25) into  published offers, or live eBay listings. The unique identifier (<strong>offerId</strong>) of each offer to publish is passed into the request payload. It is possible that some unpublished offers will be successfully created into eBay listings, but others may fail. The response payload will show the results for each <strong>offerId</strong> value that is passed into the request payload. The <strong>errors</strong> and <strong>warnings</strong> containers will be returned for an offer that had one or more issues being published. <br/><br/>For those who prefer to publish one offer per call, the <strong>publishOffer</strong> method can be used instead. In the case of a multiple-variation listing, the <strong>publishOfferByInventoryItemGroup</strong> call should be used instead, as this call will convert all unpublished offers associated with an inventory item group into a multiple-variation listing.  # noqa: E501

        :param BulkOffer body: The base request of the <strong>bulkPublishOffer</strong> method. (required)
        :return: BulkPublishResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'bulk_publish_offer', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_offer(self, body, content_language, **kwargs):  # noqa: E501
        """create_offer  # noqa: E501

        This call creates an offer for a specific inventory item on a specific eBay marketplace. It is up to the sellers whether they want to create a complete offer (with all necessary details) right from the start, or sellers can provide only some information with the initial <strong>createOffer</strong> call, and then make one or more subsequent <strong>updateOffer</strong> calls to complete the offer and prepare to publish the offer. Upon first creating an offer, the following fields are required in the request payload:  <strong>sku</strong>, <strong>marketplaceId</strong>, and (listing) <strong>format</strong>. <br><br>Other information that will be required before an offer can be published are highlighted below. These settings are either set with <strong>createOffer</strong>, or they can be set with a subsequent <strong>updateOffer</strong> call: <ul><li>Inventory location</li> <li>Offer price</li> <li>Available quantity</li> <li>eBay listing category</li> <li>Referenced listing policy profiles to set payment, return, and fulfillment values/settings</li> </ul> <p><span class=\"tablenote\"><strong>Note:</strong> Though the <strong>includeCatalogProductDetails</strong> parameter is not required to be submitted in the request, the parameter defaults to <code>true</code> if omitted.</span></p><p>If the call is successful, a unique <strong>offerId</strong> value is returned in the response. This value will be required for many other offer-related calls. Note that this call only stages an offer for publishing. The seller must run the <strong>publishOffer</strong> call to convert the offer to an active eBay listing.</p> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>createOffer</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p><p>For those who prefer to create multiple offers (up to 25 at a time) with one call, the <strong>bulkCreateOffer</strong> method can be used.</p>  # noqa: E501

        :param EbayOfferDetailsWithKeys body: Details of the offer for the channel (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :return: OfferResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'create_offer', SellInventoryException, True, ['sell.inventory', 'offer'], (body, content_language), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_offer(self, offer_id, **kwargs):  # noqa: E501
        """delete_offer  # noqa: E501

        If used against an unpublished offer, this call will permanently delete that offer. In the case of a published offer (or live eBay listing), a successful call will either end the single-variation listing associated with the offer, or it will remove that product variation from the eBay listing and also automatically remove that product variation from the inventory item group. In the case of a multiple-variation listing, the <strong>deleteOffer</strong> will not remove the product variation from the listing if that variation has one or more sales. If that product variation has one or more sales, the seller can alternately just set the available quantity of that product variation to <code>0</code>, so it is not available in the eBay search or View Item page, and then the seller can remove that product variation from the inventory item group at a later time.  # noqa: E501

        :param str offer_id: The unique identifier of the offer to delete. The unique identifier of the offer (<strong>offerId</strong>) is passed in at the end of the call URI. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'delete_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_listing_fees(self, **kwargs):  # noqa: E501
        """get_listing_fees  # noqa: E501

        This call is used to retrieve the expected listing fees for up to 250 unpublished offers. An array of one or more <strong>offerId</strong> values are passed in under the <strong>offers</strong> container.<br/><br/> In the response payload, all listing fees are grouped by eBay marketplace, and listing fees per offer are not shown. A <strong>fees</strong> container will be returned for each eBay marketplace where the seller is selling the products associated with the specified offers. <br/><br/> Errors will occur if the seller passes in <strong>offerIds</strong> that represent published offers, so this call should be made before the seller publishes offers with the <strong>publishOffer</strong>.  # noqa: E501

        :param OfferKeysWithId body: List of offers that needs fee information
        :return: FeesSummaryResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'get_listing_fees', SellInventoryException, True, ['sell.inventory', 'offer'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_offer(self, offer_id, **kwargs):  # noqa: E501
        """get_offer  # noqa: E501

        This call retrieves a specific published or unpublished offer. The unique identifier of the offer (<strong>offerId</strong>) is passed in at the end of the call URI.<p>The <code>authorization</code> header is the only required HTTP header for this call. See the <strong>HTTP request headers</strong> section for more information.</p>  # noqa: E501

        :param str offer_id: The unique identifier of the offer that is to be retrieved. (required)
        :return: EbayOfferDetailsWithAll
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'get_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_offers(self, **kwargs):  # noqa: E501
        """get_offers  # noqa: E501

        This call retrieves all existing offers for the specified SKU value. The seller has the option of limiting the offers that are retrieved to a specific eBay marketplace, or to a listing format.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> At this time, the same SKU value can not be offered across multiple eBay marketplaces, and the only supported listing format is fixed-price, so the <strong>marketplace_id</strong> and <strong>format</strong> query parameters currently do not have any practical use for this call.</span><br/><br/><p>The <code>authorization</code> header is the only required HTTP header for this call. See the <strong>HTTP request headers</strong> section for more information.</p>  # noqa: E501

        :param str format: This enumeration value sets the listing format for the offer. This query parameter will be passed in if the seller only wants to see offers in this specified listing format.
        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be a positive integer value. If this query parameter is not set, up to 100 records will be returned on each page of results.
        :param str marketplace_id: The unique identifier of the eBay marketplace. This query parameter will be passed in if the seller only wants to see the product's offers on a specific eBay marketplace.<br /><br /><span class=\"tablenote\"><strong>Note:</strong> At this time, the same SKU value can not be offered across multiple eBay marketplaces, so the <strong>marketplace_id</strong> query parameter currently does not have any practical use for this call.</span>
        :param str offset: The value passed in this query parameter sets the page number to retrieve. Although this field is a string, the value passed in this field should be a integer value equal to or greater than <code>0</code>. The first page of records has a value of <code>0</code>, the second page of records has a value of <code>1</code>, and so on. If this query parameter is not set, its value defaults to <code>0</code>, and the first page of records is returned.
        :param str sku: The seller-defined SKU value is passed in as a query parameter. All offers associated with this product are returned in the response.<br/><br/> <strong>Max length</strong>: 50.
        :return: Offers
        """
        try:
            return self._method_paged(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'get_offers', SellInventoryException, True, ['sell.inventory', 'offer'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_publish_offer(self, offer_id, **kwargs):  # noqa: E501
        """publish_offer  # noqa: E501

        This call is used to convert an unpublished offer into a published offer, or live eBay listing. The unique identifier of the offer (<strong>offerId</strong>) is passed in at the end of the call URI.<br/><br/>For those who prefer to publish multiple offers (up to 25 at a time) with one call, the <strong>bulkPublishOffer</strong> method can be used. In the case of a multiple-variation listing, the <strong>publishOfferByInventoryItemGroup</strong> call should be used instead, as this call will convert all unpublished offers associated with an inventory item group into a multiple-variation listing.  # noqa: E501

        :param str offer_id: The unique identifier of the offer that is to be published. (required)
        :return: PublishResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'publish_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_publish_offer_by_inventory_item_group(self, body, **kwargs):  # noqa: E501
        """publish_offer_by_inventory_item_group  # noqa: E501

        <span class=\"tablenote\"><strong>Note:</strong> Please note that any eBay listing created using the Inventory API cannot be revised or relisted using the Trading API calls.</span><br/><br/>This call is used to convert all unpublished offers associated with an inventory item group into an active, multiple-variation listing.<br/><br/> The unique identifier of the inventory item group (<strong>inventoryItemGroupKey</strong>) is passed in the request payload. All inventory items and their corresponding offers in the inventory item group must be valid (meet all requirements) for the <strong>publishOfferByInventoryItemGroup</strong> call to be completely successful. For any inventory items in the group that are missing required data or have no corresponding offers, the <strong>publishOfferByInventoryItemGroup</strong> will create a new multiple-variation listing, but any inventory items with missing required data/offers will not be in the newly-created listing. If any inventory items in the group to be published have invalid data, or one or more of the inventory items have conflicting data with one another, the <strong>publishOfferByInventoryItemGroup</strong> call will fail. Be sure to check for any error or warning messages in the call response for any applicable information about one or more inventory items/offers having issues.  # noqa: E501

        :param PublishByInventoryItemGroupRequest body: The identifier of the inventory item group to publish and the eBay marketplace where the listing will be published is needed in the request payload. (required)
        :return: PublishResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'publish_offer_by_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_update_offer(self, body, content_language, offer_id, **kwargs):  # noqa: E501
        """update_offer  # noqa: E501

        This call updates an existing offer. An existing offer may be in published state (active eBay listing), or in an unpublished state and yet to be published with the <strong>publishOffer</strong> call. The unique identifier (<strong>offerId</strong>) for the offer to update is passed in at the end of the call URI. <br/><br/> The <strong>updateOffer</strong> call does a complete replacement of the existing offer object, so all fields that make up the current offer object are required, regardless of whether their values changed. <br/><br/> Other information that is required before an unpublished offer can be published or before a published offer can be revised include: <ul><li>Inventory location</li> <li>Offer price</li> <li>Available quantity</li> <li>eBay listing category</li>  <li>Referenced listing policy profiles to set payment, return, and fulfillment values/settings</li> </ul> <p><span class=\"tablenote\"><strong>Note:</strong> Though the <strong>includeCatalogProductDetails</strong> parameter is not required to be submitted in the request, the parameter defaults to <code>true</code> if omitted from both the <strong>updateOffer</strong> and the <strong>createOffer</strong> calls. If a value is specified in the <strong>updateOffer</strong> call, this value will be used.</span></p> <p>For published offers, the <strong>listingDescription</strong> field is also required to update the offer/eBay listing. For unpublished offers, this field is not necessarily required unless it is already set for the unpublished offer.</p> <p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>updateOffer</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p>  # noqa: E501

        :param EbayOfferDetailsWithId body: Details of the offer for the channel (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :param str offer_id: The unique identifier of the offer that is being updated. This identifier is passed in at the end of the call URI. (required)
        :return: OfferResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'update_offer', SellInventoryException, True, ['sell.inventory', 'offer'], (body, content_language, offer_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_withdraw_offer(self, offer_id, **kwargs):  # noqa: E501
        """withdraw_offer  # noqa: E501

        This call is used to end a single-variation listing that is associated with the specified offer. This call is used in place of the <strong>deleteOffer</strong> call if the seller only wants to end the listing associated with the offer but does not want to delete the offer object. With this call, the offer object remains, but it goes into the unpublished state, and will require a <strong>publishOffer</strong> call to relist the offer.<br><br>To end a multiple-variation listing that is associated with an inventory item group, the <strong>withdrawOfferByInventoryItemGroup</strong> method can be used. This call only ends the multiple-variation listing associated with an inventory item group but does not delete the inventory item group object, nor does it delete any of the offers associated with the inventory item group, but instead all of these offers go into the unpublished state.  # noqa: E501

        :param str offer_id: The unique identifier of the offer that is to be withdrawn. This value is passed into the path of the call URI. (required)
        :return: WithdrawResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'withdraw_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_withdraw_offer_by_inventory_item_group(self, body, **kwargs):  # noqa: E501
        """withdraw_offer_by_inventory_item_group  # noqa: E501

        This call is used to end a multiple-variation eBay listing that is associated with the specified inventory item group. This call only ends multiple-variation eBay listing associated with the inventory item group but does not delete the inventory item group object. Similarly, this call also does not delete any of the offers associated with the inventory item group, but instead all of these offers go into the unpublished state. If the seller wanted to relist the multiple-variation eBay listing, they could use the <strong>publishOfferByInventoryItemGroup</strong> method.  # noqa: E501

        :param WithdrawByInventoryItemGroupRequest body: The base request of the <strong>withdrawOfferByInventoryItemGroup</strong> call. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'withdraw_offer_by_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_or_replace_product_compatibility(self, body, content_language, sku, **kwargs):  # noqa: E501
        """create_or_replace_product_compatibility  # noqa: E501

        This call is used by the seller to create or replace a list of products that are compatible with the inventory item. The inventory item is identified with a SKU value in the URI. Product compatibility is currently only applicable to motor vehicle parts and accessory categories, but more categories may be supported in the future.<br /><br /><p>In addition to the <code>authorization</code> header, which is required for all eBay REST API calls, the <strong>createOrReplaceProductCompatibility</strong> call also requires the <code>Content-Language</code> header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be <code>en-US</code>. To view other supported <code>Content-Language</code> values, and to read more about all supported HTTP headers for eBay REST API calls, see the <a href=\"/api-docs/static/rest-request-components.html#HTTP\">HTTP request headers</a> topic in the <strong>Using eBay RESTful APIs</strong> document.</p>  # noqa: E501

        :param Compatibility body: Details of the compatibility (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :param str sku: A SKU (stock keeping unit) is an unique identifier defined by a seller for a product (required)
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ProductCompatibilityApi, sell_inventory.ApiClient, 'create_or_replace_product_compatibility', SellInventoryException, True, ['sell.inventory', 'product_compatibility'], (body, content_language, sku), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_product_compatibility(self, sku, **kwargs):  # noqa: E501
        """delete_product_compatibility  # noqa: E501

        This call is used by the seller to delete the list of products that are compatible with the inventory item that is associated with the compatible product list. The inventory item is identified with a SKU value in the URI. Product compatibility is currently only applicable to motor vehicle parts and accessory categories, but more categories may be supported in the future.  # noqa: E501

        :param str sku: A SKU (stock keeping unit) is an unique identifier defined by a seller for a product (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ProductCompatibilityApi, sell_inventory.ApiClient, 'delete_product_compatibility', SellInventoryException, True, ['sell.inventory', 'product_compatibility'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_product_compatibility(self, sku, **kwargs):  # noqa: E501
        """get_product_compatibility  # noqa: E501

        This call is used by the seller to retrieve the list of products that are compatible with the inventory item. The SKU value for the inventory item is passed into the call URI, and a successful call with return the compatible vehicle list associated with this inventory item. Product compatibility is currently only applicable to motor vehicle parts and accessory categories, but more categories may be supported in the future.  # noqa: E501

        :param str sku: A SKU (stock keeping unit) is an unique identifier defined by a seller for a product (required)
        :return: Compatibility
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ProductCompatibilityApi, sell_inventory.ApiClient, 'get_product_compatibility', SellInventoryException, True, ['sell.inventory', 'product_compatibility'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_listing_create_item_draft(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """create_item_draft  # noqa: E501

        This call gives Partners the ability to create an eBay draft of a item for their seller using information from their site. <br /><br />This lets the Partner increase the exposure of items on their site and leverage the eBay user listing experience seamlessly. This experience provides guidance on pricing, aspects, etc. and recommendations that help create a listing that is complete and improves the exposure of the listing in search results. <br /><br />After the listing draft is created, the seller logs into their eBay account and uses the listing experience to finish the listing and publish the item on eBay.  # noqa: E501

        :param str x_ebay_c_marketplace_id: Use this header to specify an eBay marketplace ID. For a list of supported sites, see <a href=\"/api-docs/sell/listing/overview.html#API\">API Restrictions</a> in the Listing API overview.  (required)
        :param ItemDraft body:
        :param str content_language: Use this header to specify the natural language of the seller. For details, see Content-Language in <a href=\"/api-docs/static/rest-request-components.html#headers\">HTTP request headers</a>. <br /><br /><b> Required: </b>For EBAY_CA in French. <br /><br />(Content-Language = <code>fr-CA</code>)
        :return: ItemDraftResponse
        """
        try:
            return self._method_single(sell_listing.Configuration, '/sell/listing/v1_beta', sell_listing.ItemDraftApi, sell_listing.ApiClient, 'create_item_draft', SellListingException, True, ['sell.listing', 'item_draft'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_cancel_shipment(self, shipment_id, **kwargs):  # noqa: E501
        """cancel_shipment  # noqa: E501

        This method cancels the shipment associated with the specified shipment ID and the associated shipping label is deleted. When you cancel a shipment, the totalShippingCost of the canceled shipment is refunded to the account established by the user's billing agreement. Note that you cannot cancel a shipment if you have used the associated shipping label.  # noqa: E501

        :param str shipment_id: This path parameter specifies the unique eBay-assigned ID of the shipment to be canceled. The shipmentId value is generated and returned by a call to createFromShippingQuote. (required)
        :return: Shipment
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'cancel_shipment', SellLogisticsException, True, ['sell.logistics', 'shipment'], shipment_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_create_from_shipping_quote(self, body, **kwargs):  # noqa: E501
        """create_from_shipping_quote  # noqa: E501

        This method creates a &quot;shipment&quot; based on the shippingQuoteId and rateId values supplied in the request. The rate identified by the rateId value specifies the carrier and service for the package shipment, and the rate ID must be contained in the shipping quote identified by the shippingQuoteId value. Call createShippingQuote to retrieve a set of live shipping rates. When you create a shipment, eBay generates a shipping label that you can download and use to ship your package. In a createFromShippingQuote request, sellers can include a list of shipping options they want to add to the base service quoted in the selected rate. The list of available shipping options is specific to each quoted rate and if available, the options are listed in the rate container of the of the shipping quote. In addition to a configurable return-to location and other details about the shipment, the response to this method includes: The shipping carrier and service to be used for the package shipment A list of selected shipping options, if any The shipment tracking number The total shipping cost (the sum cost of the base shipping service and any added options) When you create a shipment, your billing agreement account is charged the sum of the baseShippingCost and the total cost of any additional shipping options you might have selected. Use the URL returned in labelDownloadUrl field, or call downloadLabelFile with the shipmentId value from the response, to download a shipping label for your package. Important! Sellers must set up their payment method with eBay before they can use this method to create a shipment and the associated shipping label.  # noqa: E501

        :param CreateShipmentFromQuoteRequest body: The create shipment from quote request. (required)
        :return: Shipment
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'create_from_shipping_quote', SellLogisticsException, True, ['sell.logistics', 'shipment'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_download_label_file(self, shipment_id, **kwargs):  # noqa: E501
        """download_label_file  # noqa: E501

        This method returns the shipping label file that was generated for the shipmentId value specified in the request. Call createFromShippingQuote to generate a shipment ID. Use the Accept HTTP header to specify the format of the returned file. The default file format is a PDF file.  # noqa: E501

        :param str shipment_id: This path parameter specifies the unique eBay-assigned ID of the shipment associated with the shipping label you want to download. The shipmentId value is generated and returned by a call to createFromShippingQuote. (required)
        :return: list[str]
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'download_label_file', SellLogisticsException, True, ['sell.logistics', 'shipment'], shipment_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_get_shipment(self, shipment_id, **kwargs):  # noqa: E501
        """get_shipment  # noqa: E501

        This method retrieves the shipment details for the specified shipment ID. Call createFromShippingQuote to generate a shipment ID.  # noqa: E501

        :param str shipment_id: This path parameter specifies the unique eBay-assigned ID of the shipment you want to retrieve. The shipmentId value is generated and returned by a call to createFromShippingQuote. (required)
        :return: Shipment
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'get_shipment', SellLogisticsException, True, ['sell.logistics', 'shipment'], shipment_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_create_shipping_quote(self, body, **kwargs):  # noqa: E501
        """create_shipping_quote  # noqa: E501

        The createShippingQuote method returns a shipping quote that contains a list of live &quot;rates.&quot; Each rate represents an offer made by a shipping carrier for a specific service and each offer has a live quote for the base service cost. Rates have a time window in which they are &quot;live,&quot; and rates expire when their purchase window ends. If offered by the carrier, rates can include shipping options (and their associated prices), and users can add any offered shipping option to the base service should they desire. Also, depending on the services required, rates can also include pickup and delivery windows. Each rate is for a single package and is based on the following information: The shipping origin The shipping destination The package size (weight and dimensions) Rates are identified by a unique eBay-assigned rateId and rates are based on price points, pickup and delivery time frames, and other user requirements. Because each rate offered must be compliant with the eBay shipping program, all rates reflect eBay-negotiated prices. The various rates returned in a shipping quote offer the user a choice from which they can choose a shipping service that best fits their needs. Select the rate for your shipment and using the associated rateId, call createFromShippingQuote to create a shipment and generate a shipping label that you can use to ship the package.  # noqa: E501

        :param ShippingQuoteRequest body: The request object for createShippingQuote. (required)
        :return: ShippingQuote
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShippingQuoteApi, sell_logistics.ApiClient, 'create_shipping_quote', SellLogisticsException, True, ['sell.logistics', 'shipping_quote'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_get_shipping_quote(self, shipping_quote_id, **kwargs):  # noqa: E501
        """get_shipping_quote  # noqa: E501

        This method retrieves the complete details of the shipping quote associated with the specified shippingQuoteId value. A &quot;shipping quote&quot; pertains to a single specific package and contains a set of shipping &quot;rates&quot; that quote the cost to ship the package by different shipping carriers and services. The quotes are based on the package's origin, destination, and size. Call createShippingQuote to create a shippingQuoteId.  # noqa: E501

        :param str shipping_quote_id: This path parameter specifies the unique eBay-assigned ID of the shipping quote you want to retrieve. The shippingQuoteId value is generated and returned by a call to createShippingQuote. (required)
        :return: ShippingQuote
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShippingQuoteApi, sell_logistics.ApiClient, 'get_shipping_quote', SellLogisticsException, True, ['sell.logistics', 'shipping_quote'], shipping_quote_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_create_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_create_ads_by_inventory_reference  # noqa: E501

        This method adds multiple listings that are managed with the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a> to an existing Promoted Listings campaign. <p>For each listing specified in the request, this method:</p>  <ul><li>Creates an ad for the listing.</li> <li>Sets the bid percentage (also known as the <i>ad rate</i>) for the ad.</li> <li>Associates the ad with the specified campaign.</li></ul>  <p>To create an ad for a listing, specify its <b>inventoryReferenceId</b> and <b>inventoryReferenceType</b>, plus the <b>bidPercentage</b> for the ad in the payload of the request. Specify the campaign to associate the ads to with using the <b>campaign_id</b> path parameter.</p>  <p>In the Inventory API, an <i>inventory reference ID</i> is either a seller-defined <b>SKU</b> value or an <b>inventoryItemGroupKey</b> (a seller-defined ID for a multiple-variation listing).</p>  <p>You can specify a maximum of <b>500 items per call</b> and each campaign can have ads for a maximum of 50,000 items. Be aware when using this call that each variation in a multiple-variation listing creates an individual ad.</p>  <p>Use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/createCampaign\">createCampaign</a> to create a new campaign and use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to get a list of existing campaigns.</p>  # noqa: E501

        :param BulkCreateAdsByInventoryReferenceRequest body: The container for the bulk request to create ads for eBay inventory reference IDs. eBay inventory reference IDs are seller-defined IDs used by theInventory API. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: BulkCreateAdsByInventoryReferenceResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_create_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_create_ads_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_create_ads_by_listing_id  # noqa: E501

        This method adds multiple listings to an existing Promoted Listings campaign using <b>listingId</b> values generated by either the <a href=\"/Devzone/XML/docs/Reference/eBay/index.html\" title=\"Trading API Reference\">Trading API</a> or <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>.  <p>For each listing ID specified in the request, this method:</p>  <ul><li>Creates an ad for the listing.</li> <li>Sets the bid percentage (also known as the <i>ad rate</i>) for the ad.</li> <li>Associates the ad with the specified campaign.</li></ul>  <p>To create an ad for a listing, specify its <b>listingId</b>, plus the <b>bidPercentage</b> for the ad in the payload of the request. Specify the campaign to associate the ads with using the <b>campaign_id</b> path parameter. Listing IDs are generated by eBay when a seller creates listings with the Trading API.</p>  <p>You can specify a maximum of <b>500 listings per call</b> and each campaign can have ads for a maximum of 50,000 items. Be aware when using this call that each variation in a multiple-variation listing creates an individual ad.</p>  <p>Use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/createCampaign\">createCampaign</a> to create a new campaign and use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to get a list of existing campaigns.</p>  # noqa: E501

        :param BulkCreateAdRequest body: The container for the bulk request to create ads for eBay listing IDs. eBay listing IDs are generated by the Trading API and Inventory API when the listing is created on eBay. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: BulkAdResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_create_ads_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_delete_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_delete_ads_by_inventory_reference  # noqa: E501

        This method works with listings created with the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>.  <p>The method deletes a set of ads, as specified by a list of inventory reference IDs, from the specified campaign. <i>Inventory reference IDs</i> are seller-defined IDs that are used with the Inventory API</a>.</p>  <p>Pass the <b>campaign_id</b> as a path parameter and populate the payload with a list of <b>inventoryReferenceId</b> and <b>inventoryReferenceType</b> pairs that you want to delete.</p>  <p>Get the campaign IDs for a seller by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> and call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to get a list of the seller's inventory reference IDs.</p>  # noqa: E501

        :param BulkDeleteAdsByInventoryReferenceRequest body: This request object defines the fields for a <b>bulkDeleteAdsByInventoryReference</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: BulkDeleteAdsByInventoryReferenceResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_delete_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_delete_ads_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_delete_ads_by_listing_id  # noqa: E501

        This method works with listing IDs created with either the <a href=\"/Devzone/XML/docs/Reference/eBay/index.html\" title=\"Trading API Reference\">Trading API</a> or the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>.  <p>The method deletes a set of ads, as specified by a list of <b>listingID</b> values from a Promoted Listings campaign. A listing ID value is generated by eBay when a seller creates a listing with either the Trading API and Inventory API.</p>  <p>Pass the <b>campaign_id</b> as a path parameter and populate the payload with the set of listing IDs that you want to delete.</p>  <p>Get the campaign IDs for a seller by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> and call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to get a list of the seller's inventory reference IDs.</p>  # noqa: E501

        :param BulkDeleteAdRequest body: This request object defines the fields for the <b>bulkDeleteAdsByListingId</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: BulkDeleteAdResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_delete_ads_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_ads_bid_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_ads_bid_by_inventory_reference  # noqa: E501

        This method works with listings that are managed with the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>. <p>The method updates the <b>bidPercentage</b> values for a set of ads associated with the specified campaign.</p>  <p>Specify the <b>campaign_id</b> as a path parameter and supply a list of <b>inventoryReferenceId</b> and <b>inventoryReferenceType</b> pairs with the updated <b>bidPercentage</b> values in the request body.</p>  <p>In the Inventory API, an <i>inventory reference ID</i> is either a seller-defined <b>SKU</b> value or an <b>inventoryItemGroupKey</b> (a seller-defined ID for a multiple-variation listing).</p>  <p>Get the campaign IDs for a seller by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> and call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to get a list of the seller's inventory reference IDs.</p>  # noqa: E501

        :param BulkCreateAdsByInventoryReferenceRequest body: This request object defines the fields for the <b>BulkCreateAdsByInventoryReference</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: BulkCreateAdsByInventoryReferenceResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_update_ads_bid_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_ads_bid_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_ads_bid_by_listing_id  # noqa: E501

        This method works with listings created with either the <a href=\"/Devzone/XML/docs/Reference/eBay/index.html\" title=\"Trading API Reference\">Trading API</a> or the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>.  <p>The method updates the <b>bidPercentage</b> values for a set of ads associated with the specified campaign.</p>  <p>Specify the <b>campaign_id</b> as a path parameter and supply a set of listing IDs with their associated updated <b>bidPercentage</b> values in the request body. An eBay listing ID is generated when a listing is created with the Trading API.</p>  <p>Get the campaign IDs for a seller by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> and call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to get a list of the seller's inventory reference IDs.</p>  # noqa: E501

        :param BulkCreateAdRequest body: This request object defines the fields for the <b>BulkCreateAdsByListingId</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: BulkAdResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_update_ads_bid_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_ad_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """create_ad_by_listing_id  # noqa: E501

        This method works with listings created with either the <a href=\"/Devzone/XML/docs/Reference/eBay/index.html\" title=\"Trading API Reference\">Trading API</a> or the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>. <p>The method:</p> <ul><li>Creates an ad for the specified listing ID.</li> <li>Sets the bid percentage (also known as the \"ad rate\") for the ad.</li> <li>Associates the ad with the specified campaign.</li></ul>  <p>To create an ad for a listing, specify its <b>listingId</b>, plus the <b>bidPercentage</b> for the ad in the payload of the request. Specify the campaign to associate the ad with using the <b>campaign_id</b> path parameter. Listing IDs are generated by eBay when a seller creates listings with the Trading API or Inventory API.</p>  <p>Each campaign can have ads for a maximum of 50,000 items, and each item in a multiple-variation listing is considered as an single item.</p>  <p>Use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/createCampaign\">createCampaign</a> to create a new campaign and use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to get a list of existing campaigns.</p>  # noqa: E501

        :param CreateAdRequest body: This request object defines the fields used in the <b>createAdByListingId</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'create_ad_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """create_ads_by_inventory_reference  # noqa: E501

        This method works with listings that are managed with the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>.  <p>The method:</p> <ul><li>Creates an ad for the specified listing.</li> <li>Sets the bid percentage (also known as the \"ad rate\") for the ad.</li> <li>Associates the ad with the specified campaign.</li></ul>  <p>To create an ad for a listing, specify its <b>inventoryReferenceId</b> and <b>inventoryReferenceType</b>, plus the <b>bidPercentage</b> for the ad in the payload of the request. Specify the campaign to associate the ad with using the <b>campaign_id</b> path parameter.</p>  <p>In the Inventory API, an <i>inventory reference ID</i> is either a seller-defined <b>SKU</b> value or an <b>inventoryItemGroupKey</b> (a seller-defined ID for a multiple-variation listing).</p>  <p>Each campaign can have ads for a maximum of 50,000 items, and each item in a multiple-variation listing is considered as an individual item.</p>  <p>Use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/createCampaign\">createCampaign</a> to create a new campaign and use <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to get a list of existing campaigns.</p>  # noqa: E501

        :param CreateAdsByInventoryReferenceRequest body: This request object defines the fields used in the <b>createAdsByInventoryReference</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: AdReferences
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'create_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_ad(self, ad_id, campaign_id, **kwargs):  # noqa: E501
        """delete_ad  # noqa: E501

        This method removes the specified ad from the specified campaign.  <p>Pass the ID of the ad to delete with the ID of the campaign associated with the ad as path parameters to the call.</p> <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to get the current list of the seller's campaign IDs.</p>  # noqa: E501

        :param str ad_id: Identifier of an ad. This ID was generated when the ad was created. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'delete_ad', SellMarketingException, True, ['sell.marketing', 'ad'], (ad_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """delete_ads_by_inventory_reference  # noqa: E501

        This method works with listings that are managed with the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>.  <p>The method deletes ads using a list of seller-defined inventory reference IDs, used with the Inventory API, that are associated with the specified campaign ID.</p> <p>Specify the campaign ID (as a path parameter) and a list of <b>inventoryReferenceId</b> and <b>inventoryReferenceType</b> pairs to be deleted.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to get a list of the seller's current campaign IDs.</p>  # noqa: E501

        :param DeleteAdsByInventoryReferenceRequest body: This request object defines the fields for the <b>deleteAdsByInventoryReference</b> request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: AdIds
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'delete_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ad(self, ad_id, campaign_id, **kwargs):  # noqa: E501
        """get_ad  # noqa: E501

        This method retrieves the specified ad from the specified campaign.  <p>In the request, supply the <b>campaign_id</b> and <b>ad_id</b> as path parameters.</p> <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve a list of the seller's current campaign IDs and call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to retrieve their current ad IDs.</p>  # noqa: E501

        :param str ad_id: Identifier of an ad. This ID was generated when the ad was created. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: Ad
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'get_ad', SellMarketingException, True, ['sell.marketing', 'ad'], (ad_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ads(self, campaign_id, **kwargs):  # noqa: E501
        """get_ads  # noqa: E501

        This method retrieves Promoted Listings ads that are associated with listings created with either the <a href=\"/Devzone/XML/docs/Reference/eBay/index.html\" title=\"Trading API Reference\">Trading API</a> or the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a>. <p>The method retrieves ads related to the specified campaign. Specify the Promoted Listings campaign to target with the <b>campaign_id</b> path parameter.</p>  <p>Because of the large number of possible results, you can use query parameters to paginate the result set by specifying a <b>limit</b>, which dictates how many ads to return on each page of the response. You can also specify how many ads to skip in the result set before returning the first result using the <b>offset</b> path parameter.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve the current campaign IDs for the seller.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :param str limit: Specifies the maximum number of ads to return on a page in the paginated response. <p><b>Default: </b>10 <br><b>Maximum:</b> 500</p>
        :param str listing_ids: A comma separated list of listing IDs. The response includes only active ads (ads associated with a RUNNING campaign). The results do not include listing IDs that are excluded by other conditions.
        :param str offset: Specifies the number of ads to skip in the result set before returning the first ad in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :return: AdPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'get_ads', SellMarketingException, True, ['sell.marketing', 'ad'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ads_by_inventory_reference(self, campaign_id, inventory_reference_id, inventory_reference_type, **kwargs):  # noqa: E501
        """get_ads_by_inventory_reference  # noqa: E501

        This method retrieves Promoted Listings ads associated with listings that are managed with the <a href=\"/api-docs/sell/inventory/resources/methods\" title=\"Inventory API Reference\">Inventory API</a> from the specified campaign.  <p>Supply the <b>campaign_id</b> as a path parameter and use query parameters to specify the <b>inventory_reference_id</b> and <b>inventory_reference_type</b> pairs.</p>  <p>In the Inventory API, an <i>inventory reference ID</i> is either a seller-defined <b>SKU</b> value or an <b>inventoryItemGroupKey</b> (a seller-defined ID for an inventory item group, which is an entity that's used in the Inventory API to create a multiple-variation listing). To indicate a listing managed by the Inventory API, you must always specify both an <b>inventory_reference_id</b> and the associated <b>inventory_reference_type</b>.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve all of the seller's the current campaign IDs.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :param str inventory_reference_id: The inventory reference ID associated with the ad you want returned. A seller's inventory reference ID is the ID of either a listing or the ID of an inventory item group (the parent of a multi-variation listing, such as a shirt that is available in multiple sizes and colors). You must always supply in both an <b>inventory_reference_id</b> and an <b>inventory_reference_type</b>. (required)
        :param str inventory_reference_type: The type of the inventory reference ID. Set this value to either <code>INVENTORY_ITEM</CODE> (a single listing) or <code>INVENTORY_ITEM_GROUP</CODE> (a multi-variation listing). You must always pass in both an <b>inventory_reference_id</b> and an <b>inventory_reference_type</b>.  (required)
        :return: Ads
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'get_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (campaign_id, inventory_reference_id, inventory_reference_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_bid(self, body, ad_id, campaign_id, **kwargs):  # noqa: E501
        """update_bid  # noqa: E501

        This method updates the bid percentage (also known as the \"ad rate\") for the specified ad in the specified campaign. <p>In the request, supply the <b>campaign_id</b> and <b>ad_id</b> as path parameters, and supply the new <b>bidPercentage</b> value in the payload of the call.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve a seller's current campaign IDs and call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to get their ad IDs.</p>  # noqa: E501

        :param UpdateBidPercentageRequest body: This type defines the fields for the <b>updateBid</b> request. (required)
        :param str ad_id: A unique eBay-assigned ID for an ad that's generated when an ad is created. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'update_bid', SellMarketingException, True, ['sell.marketing', 'ad'], (body, ad_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report(self, report_id, **kwargs):  # noqa: E501
        """get_report  # noqa: E501

        This call downloads the report as specified by the <b>report_id</b> path parameter.  <br><br>Call <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/createReportTask\" title=\"createReportTask API docs\">createReportTask</a> to schedule and generate a Promoted Listings report. All date values are returned in UTC format (<code>yyyy-MM-ddThh:mm:ss.sssZ</code>).  # noqa: E501

        :param str report_id: The unique ID of the Promoted Listings report you want to get. <p>This ID is generated by eBay when you run a report task with a call to <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/createReportTask\">createReportTask</a>. Get all the seller's report IDs by calling <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/getReportTasks\">getReportTasks</a>.</p> (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportApi, sell_marketing.ApiClient, 'get_report', SellMarketingException, True, ['sell.marketing', 'ad_report'], report_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_metadata(self, **kwargs):  # noqa: E501
        """get_report_metadata  # noqa: E501

        This call retrieves information that details the fields used in each of the Promoted Listings reports. Use the returned information to configure the different types of Promoted Listings reports.  <p> The request for this method does not use a payload or any URI parameters.</p>  # noqa: E501

        :return: ReportMetadatas
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportMetadataApi, sell_marketing.ApiClient, 'get_report_metadata', SellMarketingException, False, ['sell.marketing', 'ad_report_metadata'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_metadata_for_report_type(self, report_type, **kwargs):  # noqa: E501
        """get_report_metadata_for_report_type  # noqa: E501

        This call retrieves metadata that details the fields used by a specific Promoted Listings report type. Use the <b>report_type</b> path parameter to indicate metadata to retrieve.  <p>This method does not use a request payload.</p>  # noqa: E501

        :param str report_type: The name of the report type whose metadata you want to get.  <br><br>For details about each report type, see <a href=\"/api-docs/sell/marketing/types/plr:ReportTypeEnum\">ReportTypeEnum</a>. <br><br><b>Valid values:</b> <br>&nbsp;&nbsp;&nbsp;<code>ACCOUNT_PERFORMANCE_REPORT</code> <br>&nbsp;&nbsp;&nbsp;<code>CAMPAIGN_PERFORMANCE_REPORT</code> <br>&nbsp;&nbsp;&nbsp;<code>CAMPAIGN_PERFORMANCE_SUMMARY_REPORT</code> <br>&nbsp;&nbsp;&nbsp;<code>LISTING_PERFORMANCE_REPORT</code> <br>&nbsp;&nbsp;&nbsp;<code>INVENTORY_PERFORMANCE_REPORT</code> (required)
        :return: ReportMetadata
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportMetadataApi, sell_marketing.ApiClient, 'get_report_metadata_for_report_type', SellMarketingException, False, ['sell.marketing', 'ad_report_metadata'], report_type, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_report_task(self, body, **kwargs):  # noqa: E501
        """create_report_task  # noqa: E501

        This method creates a <i>report task</i>, which generates a Promoted Listings report based on the values specified in the call.  <p>The report is generated based on the criteria you specify, including the report type, the report's dimensions and metrics, the report's start and end dates, the listings to include in the report, and more. <i>Metrics </i>are the quantitative measurements in the report while <i>dimensions</i> specify the attributes of the data included in the reports.</p>  <p>When creating a report task, you can specify the items you want included in the report. The items you specify, using either <b>listingId</b> or <b>inventoryReference</b> values, must be in a Promoted Listings campaign for them to be included in the report.</p>  <p>For details on the required and optional fields for each report type, see <a href=\"/api-docs/sell/static/marketing/pl-reports.html\">Creating Promoted Listings reports</a>.</p>  <p>This call returns the URL to the report task in the <b>Location</b> response header, and the URL includes the report-task ID.</p>  <p>Reports often take time to generate and it's common for this call to return an HTTP status of <code>202</code>, which indicates the report is being generated. Call <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/getReportTasks\">getReportTasks</a> (or <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/getReportTask\">getReportTask</a> with the report-task ID) to determine the status of a Promoted Listings report. When a report is complete, eBay sets its status to <b>SUCCESS</b> and you can download it using the URL returned in the <b>reportHref</b> field of the <b>getReportTask</b> call. Report files are tab-separated value gzip files with a file extension of <code>.tsv.gz</code>.</p>  <p class=\"tablenote\"><b>Note:</b> This call fails if you don't submit all the required fields for the specified report type. Fields not supported by the specified report type are ignored. Call <a href=\"/api-docs/sell/marketing/resources/ad_report_metadata/methods/getReportMetadata\">getReportMetadata</a> to retrieve a list of the fields you need to configure for each Promoted Listings report type.</p>  # noqa: E501

        :param CreateReportTask body: The container for the fields that define the report task. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'create_report_task', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_report_task(self, report_task_id, **kwargs):  # noqa: E501
        """delete_report_task  # noqa: E501

        This call deletes the report task specified by the <b>report_task_id</b> path parameter. This method also deletes any reports generated by the report task.  <p>Report task IDs are generated by eBay when you call <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/createReportTask\">createReportTask</a>. Get a complete list of a seller's report-task IDs by calling <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/getReportTasks\">getReportTasks</a>.</p>  # noqa: E501

        :param str report_task_id: A unique eBay-assigned ID for the report task that's generated when the report task is created by a call to <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/createReportTask\">createReportTask</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'delete_report_task', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], report_task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_task(self, report_task_id, **kwargs):  # noqa: E501
        """get_report_task  # noqa: E501

        This call returns the details of a specific Promoted Listings report task, as specified by the <b>report_task_id</b> path parameter. <p>The report task includes the report criteria (such as the report dimensions, metrics, and included listing) and the report-generation rules (such as starting and ending dates for the specified report task).</p>  <p>Report-task IDs are generated by eBay when you call <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/createReportTask\">createReportTask</a>. Get a complete list of a seller's report-task IDs by calling <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/getReportTasks\">getReportTasks</a>.</p>  # noqa: E501

        :param str report_task_id: A unique eBay-assigned ID for the report task that's generated when the report task is created by a call to <a href=\"/api-docs/sell/marketing/resources/ad_report_task/methods/createReportTask\">createReportTask</a>. (required)
        :return: ReportTask
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'get_report_task', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], report_task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_tasks(self, **kwargs):  # noqa: E501
        """get_report_tasks  # noqa: E501

        This method returns information on all the existing report tasks related to a seller. <p>Use the <b>report_task_statuses</b> query parameter to control which reports to return. You can paginate the result set by specifying a <b>limit</b>, which dictates how many report tasks to return on each page of the response. Use the <b>offset</b> parameter to specify how many reports to skip in the result set before returning the first result.</p>  # noqa: E501

        :param str limit: Specifies the maximum number of report tasks to return on a page in the paginated response.  <p><b>Default:</b> 10<br><b>Maximum:</b> 500</p>
        :param str offset: Specifies the number of report tasks to skip in the result set before returning the first report in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the reports returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the response contains the first 10 reports from the complete list of report tasks retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>10</code>, the first page of the response contains reports 11-20 from the complete result set.</p> <b>Default:</b> 0
        :param str report_task_statuses: This parameter filters the returned report tasks by their status. Supply a comma-separated list of the report statuses you want returned. The results are filtered to include only the report statuses you specify.  <p><b>Note: </b>The results might not include some report tasks if other search conditions exclude them.</p>  <b>Valid values: </b> <br>&nbsp;&nbsp;&nbsp;<code>PENDING</code> <br>&nbsp;&nbsp;&nbsp;<code>SUCCESS</code> <br>&nbsp;&nbsp;&nbsp;<code>FAILED</code>
        :return: ReportTaskPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'get_report_tasks', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_clone_campaign(self, body, campaign_id, **kwargs):  # noqa: E501
        """clone_campaign  # noqa: E501

        This method clones (makes a copy of) the specified campaign. <p>To clone a campaign, supply the <b>campaign_id</b> as a path parameter in your call, there is no call payload.</p>  <p>The ID of the newly-cloned campaign is returned in the <b>Location</b> response header.  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve a seller's current campaign IDs</p>  <p><b>Requirement: </b>In order to clone a campaign, the <b>campaignStatus</b> must be <code>ENDED</code> and the campaign must define a set of selection rules (it must be a rules-based campaign).</p>  # noqa: E501

        :param CloneCampaignRequest body: This type defines the fields for a clone campaign request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'clone_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_campaign(self, body, **kwargs):  # noqa: E501
        """create_campaign  # noqa: E501

        This method creates a Promoted Listings ad campaign. <p>A Promoted Listings <i>campaign</i> is the structure into which you place the ads for the listings you want to promote.</p>  <p>Identify the items you want to place into a campaign either by \"key\" or by \"rule\" as follows:</p> <ul><li><b>Rules-based campaigns</b> &ndash; A rules-based campaign adds items to the campaign according to the <i>criteria</i> you specify in your call to <b>createCampaign</b>. You can set the <b>autoSelectFutureInventory</b> request field to <code>true</code> so that after your campaign launches, eBay will regularly assess your new, revised, or newly-eligible listings to determine whether any should be added or removed from your campaign according to the rules you set. If there are, eBay will add or remove them automatically on a daily basis.</li> <li><b>Key-based campaigns</b> &ndash; Add items to an existing campaign using either listing ID values or Inventory Reference values: <ul><li>Add <b>listingId</b> values to an existing campaign by calling either <b>createAdByListingID</b> or <b>bulkCreateAdsByListingId</b>.</li>  <li>Add <b>inventoryReference</b> values to an existing campaign by calling either <b>createAdByInventoryReference</b> or <b>bulkCreateAdsByInventoryReference</b>.</li></ul></li></ul>  <p class=\"tablenote\"><b>Note:</b> No matter how you add items to a Promoted Listings campaign, each campaign can contain ads for a maximum of 50,000 items. <br><br>If a rules-based campaign identifies more than 50,000 items, ads are created for only the first 50,000 items identified by the specified criteria, and ads are not created for the remaining items.</p>  <p><b>Creating a campaign</b></p> <p>To create a basic campaign, supply:</p>  <ul><li>The user-defined campaign name</li> <li>The start date (and optionally the end date) of the campaign</li> <li>The eBay marketplace on which the campaign is hosted</li> <li>Details on the campaign funding model</li></ul>  <p>The campaign funding model specifies how the Promoted Listings fee is calculated. Currently, the only supported funding model is <code>COST_PER_SALE</code>. For complete information on how the fee is calculated and when it applies, see <a href=\"/api-docs/sell/static/marketing/promoted-listings.html#pl-fees\">Promoted Listings fees</a>.</p>   <p>If you populate the <b>campaignCriterion</b> object in your <b>createCampaign</b> request, campaign \"ads\" are created by \"rule\" for the listings that meet the criteria you specify, and these ads are associated with the newly created campaign.</p>  <p>For details on creating Promoted Listings campaigns and how to select the items to be included in your campaigns, see <a href=\"/api-docs/sell/static/marketing/pl-create-campaign.html\">Creating a Promoted Listings campaign</a>.</p>  <p>For recommendations on which listings are prime for a Promoted Listings ad campaign and to get guidance on how to set the <b>bidPercentage</b> field, see <a href=\"/api-docs/sell/static/marketing/pl-reco-api.html\">Using the Recommendation API to help configure campaigns</a>.</p>  <p class=\"tablenote\"><b>Tip:</b> See <a href=\"/api-docs/sell/marketing/static/overview.html#PL-requirements\">Promoted Listings requirements and restrictions</a> for the details on the marketplaces that support Promoted Listings via the API.</p>  # noqa: E501

        :param CreateCampaignRequest body: This type defines the fields for the create campaign request. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'create_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """delete_campaign  # noqa: E501

        This method deletes the campaign specified by the <code>campaign_id</code> query parameter.  <p class=\"tablenote\"><b>Note: </b> You can delete only campaigns that have ended.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve the <b>campaign_id</b> and the campaign status (<code>RUNNING</code>, <code>PAUSED</code>, <code>ENDED</code>, and so on) for all the seller's campaigns.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'delete_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_end_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """end_campaign  # noqa: E501

        This method ends an active (<code>RUNNINGM</code>) or paused campaign. Specify the campaign you want to end by supplying its  campaign ID in a query parameter.  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve the <b>campaign_id</b> and the campaign status (<code>RUNNING</code>, <code>PAUSED</code>, <code>ENDED</code>, and so on) for all the seller's campaigns.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'end_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_find_campaign_by_ad_reference(self, **kwargs):  # noqa: E501
        """find_campaign_by_ad_reference  # noqa: E501

        This method retrieves the campaigns containing the listing that is specified using either a listing ID, or an inventory reference ID and inventory reference type pair.  <p>eBay <i>listing IDs</i> are generated by either the <a href=\"/Devzone/XML/docs/Reference/eBay/index.html\" title=\"Trading API Reference\">Trading API</a> or the <a href=\"/api-docs/sell/inventory/resources/methods\">Inventory API</a> when you create a listing.</p>  <p> An <i>inventory reference ID</i> can be either a seller-defined <b>SKU</b> or <b>inventoryItemGroupKey</b>, as specified in the Inventory API.</p>  <p class=\"tablenote\"><b>Note:</b> This request accepts either a <b>listing_id</b>, <i>or</i> an <b>inventory_reference_id</b> and <b>inventory_reference_type</b> pair, as used in the Inventory API.</p>  # noqa: E501

        :param str inventory_reference_id: The seller's inventory reference ID of the listing to be used to find the campaign in which it is associated. You must always pass in both  <b>inventory_reference_id</b> and <b>inventory_reference_type</b>.
        :param str inventory_reference_type: The type of the seller's inventory reference ID, which is a listing or group of items. You must always pass in both <b>inventory_reference_id</b> and <b>inventory_reference_type</b>.
        :param str listing_id: Identifier of the eBay listing associated with the ad.
        :return: Campaigns
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'find_campaign_by_ad_reference', SellMarketingException, True, ['sell.marketing', 'campaign'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """get_campaign  # noqa: E501

        This method retrieves the details of a single campaign, as specified with the <b>campaign_id</b> query parameter.  <p>This method returns all the details of a campaign (including the campaign's the selection rules), except the for the listing IDs or inventory reference IDs included in the campaign. These IDs are returned by <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a>.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve a list of the seller's campaign IDs.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: Campaign
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'get_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_campaign_by_name(self, campaign_name, **kwargs):  # noqa: E501
        """get_campaign_by_name  # noqa: E501

        This method retrieves the details of a single campaign, as specified with the <b>campaign_name</b> query parameter. Note that the campaign name you specify must be an exact, case-sensitive match of the name of the campaign you want to retrieve.</p>  <p>This method returns all the details of a campaign (including the campaign's the selection rules), except the for the listing IDs or inventory reference IDs included in the campaign. These IDs are returned by <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a>.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve a list of the seller's campaign names.</p>  # noqa: E501

        :param str campaign_name: Name of the campaign. (required)
        :return: Campaign
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'get_campaign_by_name', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_name, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_campaigns(self, **kwargs):  # noqa: E501
        """get_campaigns  # noqa: E501

        This method retrieves the details for all the campaigns of a seller, including the campaign's the selection rules. <p>Note that this method does not return the listing IDs or inventory reference IDs of the items included in the ad campaign. Call <a href=\"/api-docs/sell/marketing/resources/ad/methods/getAds\">getAds</a> to retrieve these IDs.</p>  <p>You can filter the result set by a campaign name, end date range, start date range, or campaign status. You can also paginate the records returned from the result set using the <b>limit</b> query parameter, and control which records to return using the  <b>offset</b> parameter.</p>  # noqa: E501

        :param str campaign_name: Specifies the campaign name. The results are filtered to include only the campaign by the specified name.<br /><br /><b>Note: </b>The results might be null if other filters exclude the campaign with this name. <br /><br /><b>Maximum: </b> 1 campaign name
        :param str campaign_status: Specifies the campaign status. The results are filtered to include only campaigns that are in the specified states. <br /><br /><b>Note: </b>The results might not include all the campaigns with this status if other filters exclude them. <br /><br /><b>Valid values:</b> See <a href=\"/api-docs/sell/marketing/types/pls:CampaignStatusEnum\">CampaignStatusEnum</a> <br /><br /><b>Maximum: </b> 1 status
        :param str end_date_range: Specifies the range of a campaign's end date. The results are filtered to include only campaigns with an end date that is within specified range. <br><br><b>Valid format (UTC): </b> <br><br>&nbsp;&nbsp;&nbsp;&nbsp;<code>yyyy-MM-ddThh:mm:ssZ..yyyy-MM-ddThh:mm:ssZ&nbsp;&nbsp;</code> (campaign ends within this range) <br>&nbsp;&nbsp;&nbsp;&nbsp;<code>yyyy-MM-ddThh:mm:ssZ..&nbsp;&nbsp;</code>(campaign ends on or after this date)<br>&nbsp;&nbsp;&nbsp;&nbsp;<code>..yyyy-MM-ddThh:mm:ssZ&nbsp;&nbsp;</code> (campaign ends on or before this date)<br>&nbsp;&nbsp;&nbsp;&nbsp;<code>2016-09-08T00:00:00Z..2016-09-09T00:00:00Z&nbsp;&nbsp;</code> (campaign ends on September 8, 2016) <br /><br /><b>Note: </b>The results might not include all the campaigns ending on this date if other filters exclude them.
        :param str limit: <p>Specifies the maximum number of campaigns to return on a page in the paginated response.</p>  <b>Default: </b>10 <br><b>Maximum: </b> 500
        :param str offset: Specifies the number of campaigns to skip in the result set before returning the first report in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :param str start_date_range: Specifies the range of a campaign's start date in which to filter the results. The results are filtered to include only campaigns with a start date that is equal to this date or is within specified range.<br><br><b>Valid format (UTC): </b> <br><br>&nbsp;&nbsp;&nbsp;&nbsp;<code>yyyy-MM-ddThh:mm:ssZ..yyyy-MM-ddThh:mm:ssZ&nbsp;&nbsp;</code> (starts within this range)<br>&nbsp;&nbsp;&nbsp;&nbsp;<code>yyyy-MM-ddThh:mm:ssZ..&nbsp;&nbsp;</code>(campaign starts on or after this date)<br>&nbsp;&nbsp;&nbsp;&nbsp;<code>..yyyy-MM-ddThh:mm:ssZ&nbsp;&nbsp;</code> (campaign starts on or before this date)<br>&nbsp;&nbsp;&nbsp;&nbsp;<code>2016-09-08T00:00.00.000Z..2016-09-09T00:00:00Z&nbsp;&nbsp;</code> (campaign starts on September 8, 2016)   <br /><br /><b>Note: </b>The results might not include all the campaigns with this start date if other filters exclude them.
        :return: CampaignPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'get_campaigns', SellMarketingException, True, ['sell.marketing', 'campaign'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_pause_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """pause_campaign  # noqa: E501

        This method pauses an active (RUNNING) campaign.  <p>You can restarted by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/resumeCampaign\">resumeCampaign</a>, as long as the campaign's end date is in the future.</p>  <p><b>Note: </b> The listings associated with a paused campaign cannot be added into another campaign.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve the <b>campaign_id</b> and the campaign status (<code>RUNNING</code>, <code>PAUSED</code>, <code>ENDED</code>, and so on) for all the seller's campaigns.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'pause_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_resume_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """resume_campaign  # noqa: E501

        This method resumes a paused campaign, as long as it's end date is in the future. Supply the <b>campaign_id</b> for the campaign you want to restart as a query parameter in the request.  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve the <b>campaign_id</b> and the campaign status (<code>RUNNING</code>, <code>PAUSED</code>, <code>ENDED</code>, and so on) for all the seller's campaigns.</p>  # noqa: E501

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'resume_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_campaign_identification(self, body, campaign_id, **kwargs):  # noqa: E501
        """update_campaign_identification  # noqa: E501

        This method replaces the name and the start and end dates of a campaign.  <p>Specify the <b>campaign_id</b> you want to update as a URI parameter, and configure the <b>campaignName</b> and <b>startDate</b> in the request payload.  <p>If you want to change only the end date of the campaign, specify the current campaign name and set <b>startDate</b> to the current date (you cannot use a start date that is in the past), and set the <b>endDate</b> as desired. Note that if you do not set a new end date in this call, any current <b>endDate</b> value will be set to <code>null</code>. To preserve the currently-set end date, you must specify the value again in your request.</p>  <p>Call <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a> to retrieve a seller's campaign details, including the campaign ID, campaign name, and the start and end dates of the campaign.  # noqa: E501

        :param UpdateCampaignIdentificationRequest body: This type defines the fields to updated the campaign name and start and end dates. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling <a href=\"/api-docs/sell/marketing/resources/campaign/methods/getCampaigns\">getCampaigns</a>. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'update_campaign_identification', SellMarketingException, True, ['sell.marketing', 'campaign'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_item_price_markdown_promotion(self, **kwargs):  # noqa: E501
        """create_item_price_markdown_promotion  # noqa: E501

        This method creates an <b>item price markdown promotion</b> (know simply as a \"markdown promotion\") where a discount amount is applied directly to the items included the promotion. Discounts can be specified as either a monetary amount or a percentage off the standard sales price. eBay highlights promoted items by placing teasers for the items throughout the online sales flows.  <p>Unlike an <a href=\"/api-docs/sell/marketing/resources/item_promotion/methods/createItemPromotion\">item promotion</a>, a markdown promotion does not require the buyer meet a \"threshold\" before the offer takes effect. With markdown promotions, all the buyer needs to do is purchase the item to receive the promotion benefit.</p>  <p class=\"tablenote\"><b>Important:</b> There are some restrictions for which listings are available for price markdown promotions. For details, see <a href=\"/api-docs/sell/marketing/static/overview.html#PM-requirements\">Promotions Manager requirements and restrictions</a>. <br><br>In addition, we recommend you list items at competitive prices before including them in your markdown promotions. For an extensive list of pricing recommendations, see the <b>Growth</b> tab in Seller Hub.</p> <p>There are two ways to add items to markdown promotions:</p> <ul><li><b>Key-based promotions</b> select items using either the listing IDs or inventory reference IDs of the items you want to promote. Note that if you use inventory reference IDs, you must specify both the <b>inventoryReferenceId</b> and the associated <b>inventoryReferenceType</b> of the item(s) you want to include the promotion.</li>  <li><b>Rule-based promotions</b> select items using a list of eBay category IDs or seller Store category IDs. Rules can further constrain items in a promotion by minimum and maximum prices, brands, and item conditions.</li></ul>  <p>New promotions must be created in either a <code>DRAFT</code> or a <code>SCHEDULED</code> state. Use the DRAFT state when you are initially creating a promotion and you want to be sure it's correctly configured before scheduling it to run. When you create a promotion, the promotion ID is returned in the <b>Location</b> response header. Use this ID to reference the promotion in subsequent requests (such as to schedule a promotion that's in a DRAFT state).</p>  <p class=\"tablenote\"><b>Tip:</b> Refer to <a href=\"/api-docs/sell/static/marketing/promotions-manager.html\">Promotions Manager</a> in the <i>Selling Integration Guide</i> for details and examples showing how to create and manage seller promotions.</p>  <p>Markdown promotions are available on all eBay marketplaces. For more information, see <a href=\"/api-docs/sell/marketing/static/overview.html#PM-requirements\">Promotions Manager requirements and restrictions</a>.</p>  # noqa: E501

        :param ItemPriceMarkdown body: This type defines the fields that describe an item price markdown promotion.
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'create_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_item_price_markdown_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """delete_item_price_markdown_promotion  # noqa: E501

        This method deletes the item price markdown promotion specified by the <b>promotion_id</b> path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.  <br><br>You can delete any promotion with the exception of those that are currently active (RUNNING). To end a running promotion, call <a href=\"/api-docs/sell/marketing/resources/item_price_markdown/methods/updateItemPriceMarkdownPromotion\">updateItemPriceMarkdownPromotion</a> and adjust the <b>endDate</b> field as appropriate.  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to delete plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'delete_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_item_price_markdown_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """get_item_price_markdown_promotion  # noqa: E501

        This method returns the complete details of the item price markdown promotion that's indicated by the <b>promotion_id</b> path parameter. <br><br>Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to get plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :return: ItemPriceMarkdown
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'get_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_item_price_markdown_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """update_item_price_markdown_promotion  # noqa: E501

        This method updates the specified item price markdown promotion with the new configuration that you supply in the payload of the request. Specify the promotion you want to update using the <b>promotion_id</b> path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.  <br><br>When updating a promotion, supply all the fields that you used to configure the original promotion (and not just the fields you are updating). eBay replaces the specified promotion with the values you supply in the update request and if you don't pass a field that currently has a value, the update request fails.  <br><br>The parameters you are allowed to update with this request depend on the status of the promotion you're updating:  <ul><li>DRAFT or SCHEDULED promotions: You can update any of the parameters in these promotions that have not yet started to run, including the <b>discountRules</b>.</li> <li>RUNNING promotions: You can change the <b>endDate</b> and the item's inventory but you cannot change the promotional discount or the promotion's start date.</li> <li>ENDED promotions: Nothing can be changed.</li></ul>  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to update plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :param ItemPriceMarkdown body: This type defines the fields that describe an item price markdown promotion.
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'update_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_item_promotion(self, **kwargs):  # noqa: E501
        """create_item_promotion  # noqa: E501

        <p>This method creates an <b>item promotion</b>, where the buyer receives a discount when they meet the buying criteria that's set for the promotion. Known here as \"threshold promotions\", these promotions trigger when a threshold is met.</p>  <p>eBay highlights promoted items by placing teasers for the promoted items throughout the online buyer flows.</p>  <p><i>Discounts</i> are specified as either a monetary amount or a percentage off the standard sales price of a listing, letting you offer deals such as \"Buy 1 Get 1\" and \"Buy $50, get 20% off\".</p> <p><i>Volume pricing</i> promotions increase the value of the discount as the buyer increases the quantity they purchase.</p> <p><i>Coded Coupons</i> provide unique codes that a buyer can use during checkout to receive a discount. The seller can specify the number of times a buyer can use the coupon and the maximum amount across all purchases that can be discounted using the coupon. The coupon code can also be made public (appearing on the seller’s Offer page, search pages, the item listing, and the checkout page) or private (only on the seller’s Offer page, but the seller can include the code in email and social media).</p> <p class=\"tablenote\"><b>Note</b>: Coded Coupons are currently available in the US, UK, DE, FR, IT, ES, and AU marketplaces.</p><p>There are two ways to add items to a threshold promotion:</p>  <ul><li><b>Key-based promotions</b> select items using either the listing IDs or inventory reference IDs of the items you want to promote. Note that if you use inventory reference IDs, you must specify both the <b>inventoryReferenceId</b> and the associated <b>inventoryReferenceType</b> of the item(s) you want to include the promotion.</li> <li><b>Rule-based promotions</b> select items using a list of eBay category IDs or seller Store category IDs. Rules can further constrain items in a promotion by minimum and maximum prices, brands, and item conditions.</li></ul>  <p>You must create a new promotion in either a <code>DRAFT</code> or <code>SCHEDULED</code> state. Use the DRAFT state when you are initially creating a promotion and you want to be sure it's correctly configured before scheduling it to run. When you create a promotion, the promotion ID is returned in the <b>Location</b> response header. Use this ID to reference the promotion in subsequent requests.</p>  <p class=\"tablenote\"><b>Tip:</b> Refer to the <a href=\"/api-docs/sell/static/marketing/promotions-manager.html\">Selling Integration Guide</a> for details and examples showing how to create and manage threshold promotions using the Promotions Manager.</p>  <p>For information on the eBay marketplaces that support item promotions, see <a href=\"/api-docs/sell/marketing/static/overview.html#PM-requirements\">Promotions Manager requirements and restrictions</a>.</p>  # noqa: E501

        :param ItemPromotion body: This type defines the fields that describe an item promotion.
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'create_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_item_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """delete_item_promotion  # noqa: E501

        This method deletes the threshold promotion specified by the <b>promotion_id</b> path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.  <br><br>You can delete any promotion with the exception of those that are currently active (RUNNING). To end a running threshold promotion, call <a href=\"/api-docs/sell/marketing/resources/item_promotion/methods/updateItemPromotion\">updateItemPromotion</a> and adjust the <b>endDate</b> field as appropriate.  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to delete plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'delete_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_item_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """get_item_promotion  # noqa: E501

        This method returns the complete details of the threshold promotion specified by the <b>promotion_id</b> path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to retrieve plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :return: ItemPromotionResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'get_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_item_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """update_item_promotion  # noqa: E501

        This method updates the specified threshold promotion with the new configuration that you supply in the request. Indicate the promotion you want to update using the <b>promotion_id</b> path parameter.  <p>Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.</p>  <p>When updating a promotion, supply all the fields that you used to configure the original promotion (and not just the fields you are updating). eBay replaces the specified promotion with the values you supply in the update request and if you don't pass a field that currently has a value, the update request will fail.</p>  <p>The parameters you are allowed to update with this request depend on the status of the promotion you're updating:  <ul><li>DRAFT or SCHEDULED promotions: You can update any of the parameters in these promotions that have not yet started to run, including the <b>discountRules</b>.</li> <li>RUNNING or PAUSED promotions: You can change the <b>endDate</b> and the item's inventory but you cannot change the promotional discount or the promotion's start date.</li> <li>ENDED promotions: Nothing can be changed.</li></ul> <p class=\"tablenote\"><b>Tip:</b> When updating a <code>RUNNING</code> or <code>PAUSED</code> promotion, set the <b>status</b> field to <code>SCHEDULED</code> for the update request. When the promotion is updated, the previous status (either <code>RUNNING</code> or <code>PAUSED</code>) is retained.</p>  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to update plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :param ItemPromotion body: This type defines the fields that describe an item promotion.
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'update_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_listing_set(self, promotion_id, **kwargs):  # noqa: E501
        """get_listing_set  # noqa: E501

        <p>This method returns the set of listings associated with the <b>promotion_id</b> specified in the path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of a seller's promotions.  <p>The listing details are returned in a paginated set and you can control and results returned using the following query parameters: <b>limit</b>, <b>offset</b>, <b>q</b>, <b>sort</b>, and <b>status</b>.</p>  <ul><li><b>Maximum associated listings returned:</b> 200</li>  <li><b>Default number of listings returned:</b> 200</li></ul>  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to get plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :param str limit: Specifies the maximum number of promotions returned on a page from the result set. <br><br><b>Default:</b> 200<br><b>Maximum:</b> 200
        :param str offset: Specifies the number of promotions to skip in the result set before returning the first promotion in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :param str q: Reserved for future use.
        :param str sort: Specifies the order in which to sort the associated listings in the response. If you precede the supplied value with a dash, the response is sorted in reverse order.  <br><br><b>Example:</b> <br>&nbsp;&nbsp;&nbsp;<code>sort=PRICE</code> - Sorts the associated listings by their current price in ascending order <br>&nbsp;&nbsp;&nbsp;<code>sort=-TITLE</code> - Sorts the associated listings by their title in descending alphabetical order (Z-Az-a)  <br><br><b>Valid values</b>:<ul class=\"compact\"><li>AVAILABLE</li> <li>PRICE</li> <li>TITLE</li></ul> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/marketing/types/csb:SortField
        :param str status: This query parameter applies only to markdown promotions. It filters the response based on the indicated status of the promotion. Currently, the only supported value for this parameter is <code>MARKED_DOWN</code>, which indicates active markdown promotions. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/marketing/types/sme:ItemMarkdownStatusEnum
        :return: None
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'get_listing_set', SellMarketingException, True, ['sell.marketing', 'promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_promotions(self, marketplace_id, **kwargs):  # noqa: E501
        """get_promotions  # noqa: E501

        This method returns a list of a seller's undeleted promotions. <p>The call returns up to 200 currently-available promotions on the specified marketplace. While the response body does not include the promotion's <b>discountRules</b> or <b>inventoryCriterion</b> containers, it does include the <b>promotionHref</b> (which you can use to retrieve the complete details of the promotion).</p>  <p>Use query parameters to sort and filter the results by the number of promotions to return, the promotion state or type, and the eBay marketplace. You can also supply keywords to limit the response to the promotions that contain that keywords in the title of the promotion.</p> <p><b>Maximum returned:</b> 200</p>  # noqa: E501

        :param str marketplace_id: The eBay marketplace ID of the site where the promotion is hosted.  <p><b>Valid values:</b></p>  <ul><li><code>EBAY_AU</code> = Australia</li> <li><code>EBAY_DE</code> = Germany</li> <li><code>EBAY_ES</code> = Spain</li> <li><code>EBAY_FR</code> = France</li> <li><code>EBAY_GB</code> = Great Britain</li> <li><code>EBAY_IT</code> = Italy</li> <li><code>EBAY_US</code> = United States</li></ul> (required)
        :param str limit: Specifies the maximum number of promotions returned on a page from the result set.  <br><br><b>Default:</b> 200 <br><b>Maximum:</b> 200
        :param str offset: Specifies the number of promotions to skip in the result set before returning the first promotion in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :param str promotion_status: Specifies the promotion state by which you want to filter the results. The response contains only those promotions that match the state you specify.  <br><br><b>Valid values:</b> <ul><li><code>DRAFT</code></li> <li><code>SCHEDULED</code></li> <li><code>RUNNING</code></li> <li><code>PAUSED</code></li> <li><code>ENDED</code></li></ul><b>Maximum number of input values:</b> 1
        :param str promotion_type: Filters the returned promotions based on their campaign promotion type. Specify one of the following values to indicate the promotion type you want returned: <ul><li><code>CODED_COUPON</code> &ndash; A coupon code promotion set with <b>createItemPromotion</b>.</li> <li><code>MARKDOWN_SALE</code> &ndash; A markdown promotion set with <b>createItemPriceMarkdownPromotion</b>.</li> <li><code>ORDER_DISCOUNT</code> &ndash; A threshold promotion set with <b>createItemPromotion</b>.</li> <li><code>VOLUME_DISCOUNT</code> &ndash; A volume pricing promotion set with <b>createItemPromotion</b>.</li></ul>
        :param str q: A string consisting of one or more <i>keywords</i>. eBay filters the response by returning only the promotions that contain the supplied keywords in the promotion title.  <br><br><b>Example:</b> \"iPhone\" or \"Harry Potter.\"  <br><br>Commas that separate keywords are ignored. For example, a keyword string of \"iPhone, iPad\" equals \"iPhone iPad\", and each results in a response that contains promotions with both \"iPhone\" and \"iPad\" in the title.
        :param str sort: Specifies the order for how to sort the response. If you precede the supplied value with a dash, the response is sorted in reverse order.  <br><br><b>Example:</b> <br>&nbsp;&nbsp;&nbsp;<code>sort=END_DATE</code> &nbsp; Sorts the promotions in the response by their end dates in ascending order <br>&nbsp;&nbsp;&nbsp;<code>sort=-PROMOTION_NAME</code> &nbsp; Sorts the promotions by their promotion name in descending alphabetical order (Z-Az-a)  <br><br><b>Valid values</b>:<ul><li><code>START_DATE</code></li> <li><code>END_DATE</code></li> <li><code>PROMOTION_NAME</code></li></ul> For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/marketing/types/csb:SortField
        :return: PromotionsPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'get_promotions', SellMarketingException, True, ['sell.marketing', 'promotion'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_pause_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """pause_promotion  # noqa: E501

        This method pauses a currently-active (RUNNING) threshold promotion and changes the state of the promotion from <code>RUNNING</code> to <code>PAUSED</code>. Pausing a promotion makes the promotion temporarily unavailable to buyers and any currently-incomplete transactions will not receive the promotional offer until the promotion is resumed. Also, promotion teasers are not displayed when a promotion is paused.  <br><br>Pass the ID of the promotion you want to pause using the <b>promotion_id</b> path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of the seller's promotions. <br><br><b>Note:</b> You can only pause threshold promotions (you cannot pause markdown promotions).  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to pause plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'pause_promotion', SellMarketingException, True, ['sell.marketing', 'promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_resume_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """resume_promotion  # noqa: E501

        This method restarts a threshold promotion that was previously paused and changes the state of the promotion from <code>PAUSED</code> to <code>RUNNING</code>. Only promotions that have been previously paused can be resumed. Resuming a promotion reinstates the promotional teasers and any transactions that were in motion before the promotion was paused will again be eligible for the promotion.  <br><br>Pass the ID of the promotion you want to resume using the <b>promotion_id</b> path parameter. Call <a href=\"/api-docs/sell/marketing/resources/promotion/methods/getPromotions\">getPromotions</a> to retrieve the IDs of the seller's promotions.  # noqa: E501

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to resume plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (<b>@</b>).  <br><br>The ID of the promotion (<b>promotionId</b>) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. <br><br><b>Example:</b> <code>1********5@EBAY_US</code> (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'resume_promotion', SellMarketingException, True, ['sell.marketing', 'promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_promotion_reports(self, marketplace_id, **kwargs):  # noqa: E501
        """get_promotion_reports  # noqa: E501

        This method generates a report that lists the seller's running, paused, and ended promotions for the specified eBay marketplace. The result set can be filtered by the promotion status and the number of results to return. You can also supply <i>keywords</i> to limit the report to promotions that contain the specified keywords. <br><br>Specify the eBay marketplace for which you want the report run using the <b>marketplace_id</b> query parameter. Supply additional query parameters to control the report as needed.  # noqa: E501

        :param str marketplace_id: The eBay marketplace ID of the site for which you want the promotions report.  <p><b>Valid values:</b>  </p><ul><li><code>EBAY_AU</code> = Australia</li> <li><code>EBAY_DE</code> = Germany</li> <li><code>EBAY_ES</code> = Spain</li> <li><code>EBAY_FR</code> = France</li> <li><code>EBAY_GB</code> = Great Britain</li> <li><code>EBAY_IT</code> = Italy</li> <li><code>EBAY_US</code> = United States</li></ul> (required)
        :param str limit: Specifies the maximum number of promotions returned on a page from the result set.  <br><br><b>Default:</b> 200 <br><b>Maximum:</b> 200
        :param str offset: Specifies the number of promotions to skip in the result set before returning the first promotion in the paginated response.  <p>Combine <b>offset</b> with the <b>limit</b> query parameter to control the items returned in the response. For example, if you supply an <b>offset</b> of <code>0</code> and a <b>limit</b> of <code>10</code>, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If <b>offset</b> is <code>10</code> and <b>limit</b> is <code>20</code>, the first page of the response contains items 11-30 from the complete result set.</p> <p><b>Default:</b> 0</p>
        :param str promotion_status: Limits the results to the promotions that are in the state specified by this query parameter.  <br><br><b>Valid values:</b> <ul><li><code>DRAFT</code></li> <li><code>SCHEDULED</code></li> <li><code>RUNNING</code></li> <li><code>PAUSED</code></li> <li><code>ENDED</code></li></ul><b>Maximum number of values supported:</b> 1
        :param str promotion_type: Filters the returned promotions in the report based on their campaign promotion type. Specify one of the following values to indicate the promotion type you want returned in the report: <ul><li><code>CODED_COUPON</code> &ndash; A coupon code promotion set with <b>createItemPromotion</b>.</li> <li><code>MARKDOWN_SALE</code> &ndash; A markdown promotion set with <b>createItemPriceMarkdownPromotion</b>.</li> <li><code>ORDER_DISCOUNT</code> &ndash; A threshold promotion set with <b>createItemPromotion</b>.</li> <li><code>VOLUME_DISCOUNT</code> &ndash; A volume pricing promotion set with <b>createItemPromotion</b>.</li></ul>
        :param str q: A string consisting of one or more <i>keywords</i>. eBay filters the response by returning only the promotions that contain the supplied keywords in the promotion title.  <br><br><b>Example:</b> \"iPhone\" or \"Harry Potter.\"  <br><br>Commas that separate keywords are ignored. For example, a keyword string of \"iPhone, iPad\" equals \"iPhone iPad\", and each results in a response that contains promotions with both \"iPhone\" and \"iPad\" in the title.
        :return: PromotionsReportPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionReportApi, sell_marketing.ApiClient, 'get_promotion_reports', SellMarketingException, True, ['sell.marketing', 'promotion_report'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_promotion_summary_report(self, marketplace_id, **kwargs):  # noqa: E501
        """get_promotion_summary_report  # noqa: E501

        This method generates a report that summarizes the seller's promotions for the specified eBay marketplace. The report returns information on <code>RUNNING</code>, <code>PAUSED</code>, and <code>ENDED</code> promotions (deleted reports are not returned) and summarizes the seller's campaign performance for all promotions on a given site.  <br><br>For information about summary reports, see <a href=\"/api-docs/sell/static/marketing/pm-summary-report.html\">Reading the item promotion Summary report</a>.  # noqa: E501

        :param str marketplace_id: The eBay marketplace ID of the site you for which you want a promotion summary report.  <p><b>Valid values:</b></p>  <ul><li><code>EBAY_AU</code> = Australia</li> <li><code>EBAY_DE</code> = Germany</li> <li><code>EBAY_ES</code> = Spain</li> <li><code>EBAY_FR</code> = France</li> <li><code>EBAY_GB</code> = Great Britain</li> <li><code>EBAY_IT</code> = Italy</li> <li><code>EBAY_US</code> = United States</li></ul> (required)
        :return: SummaryReportResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionSummaryReportApi, sell_marketing.ApiClient, 'get_promotion_summary_report', SellMarketingException, True, ['sell.marketing', 'promotion_summary_report'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_sales_tax_jurisdictions(self, country_code, **kwargs):  # noqa: E501
        """get_sales_tax_jurisdictions  # noqa: E501

        This method retrieves all the sales tax jurisdictions for the country that you specify in the <b>countryCode</b> path parameter. Countries with valid sales tax jurisdictions are Canada and the US.  <br><br>The response from this call tells you the jurisdictions for which a seller can configure tax tables. Although setting up tax tables is optional, you can use the <b>createOrReplaceSalesTax</b> in the <b>Account API</b> call to configure the tax tables for the jurisdictions you sell to.  # noqa: E501

        :param str country_code: This path parameter specifies the two-letter <a href=\"https://www.iso.org/iso-3166-country-codes.html\" title=\"https://www.iso.org\" target=\"_blank\">ISO 3166</a> country code for the country whose jurisdictions you want to retrieve. eBay provides sales tax jurisdiction information for Canada and the United States.Valid values for this path parameter are <code>CA</code> and <code>US</code>. (required)
        :return: SalesTaxJurisdictions
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.CountryApi, sell_metadata.ApiClient, 'get_sales_tax_jurisdictions', SellMetadataException, False, ['sell.metadata', 'country'], country_code, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_automotive_parts_compatibility_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_automotive_parts_compatibility_policies  # noqa: E501

        This method returns the eBay policies that define how to list automotive-parts-compatibility items in the categories of a specific marketplace.  <br><br>By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the <b>filter</b> query parameter to specify only the category IDs you want to review.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the <b>Accept-Encoding</b> request header and setting the value to <code>application/gzip</code>.</span>  # noqa: E501

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved.  <br><br><b>Note:</b> Only the following eBay marketplaces support automotive parts compatibility: <ul> <li>EBAY_US</li> <li>EBAY_AU</li> <li>EBAY_CA</li> <li>EBAY_DE</li> <li>EBAY_ES</li> <li>EBAY_FR</li> <li>EBAY_GB</li> <li>EBAY_IT</li><ul> (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply <b>categoryId</b> values for the sections of the tree you want returned.  <br><br>When you specify a <b>categoryId</b> value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  <br><br>The parameter takes a list of <b>categoryId</b> values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 <code>categoryId</code> values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  <br><br><b>Example:</b> <code>filter=categoryIds:{100|101|102}</code>  <br><br>Note that you must URL-encode the parameter list, which results in the following filter for the above example: <br><br> &nbsp;&nbsp;<code>filter=categoryIds%3A%7B100%7C101%7C102%7D</code>
        :return: AutomotivePartsCompatibilityPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_automotive_parts_compatibility_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_extended_producer_responsibility_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_extended_producer_responsibility_policies  # noqa: E501

        This method returns the Extended Producer Responsibility policies for one, multiple, or all eBay categories in an eBay marketplace.<br /><br />The identifier of the eBay marketplace is passed in as a path parameter, and unless one or more eBay category IDs are passed in through the filter query parameter, this method will return metadata on every applicable category for the specified marketplace.<br /><br /><span class=\"tablenote\"><span style=\"color:#004680\"><strong>Note:</strong></span> Currently, the Extended Producer Responsibility policies are only applicable to a limited number of categories, and only in the EBAY_FR marketplace.</span><br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the <b>Accept-Encoding</b> request header and setting the value to <code>application/gzip</code>.</span>  # noqa: E501

        :param str marketplace_id: A path parameter that specifies the eBay marketplace for which policy information shall be retrieved.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> See <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Request components</a> for a list of valid eBay marketplace IDs.</span> (required)
        :param str filter: A query parameter that can be used to limit the response by returning policy information for only the selected sections of the category tree. Supply <b>categoryId</b> values for the sections of the tree that should be returned.<br /><br />When a <b>categoryId</b> value is specified, the returned category tree includes the policies for that parent node, as well as the policies for any child nodes below that parent node.<br /><br />Pass in the <b>categoryId</b> values using a URL-encoded, pipe-separated ('|') list. For example:<br /><br /><code>filter=categoryIds%3A%7B100%7C101%7C102%7D</code><br /><br /><b>Maximum:</b> 50
        :return: ExtendedProducerResponsibilityPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_extended_producer_responsibility_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_item_condition_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_item_condition_policies  # noqa: E501

        This method returns item condition metadata on one, multiple, or all eBay categories on an eBay marketplace. This metadata consists of the different item conditions (with IDs) that an eBay category supports, and a boolean to indicate if an eBay category requires an item condition. <br><br>The identifier of the eBay marketplace is passed in as a path parameter, and unless one or more eBay category IDs are passed in through the <b>filter</b> query parameter, this method will return metadata on every single category for the specified marketplace. If you only want to view item condition metadata for one eBay category or a select group of eBay categories, you can pass in up to 50 eBay category ID through the <b>filter</b> query parameter.<br /><br /><span class=\"tablenote\"><span style=\"color:#FF0000\"><strong>Important:</strong></span> <b>Certified - Refurbished</b>-eligible sellers, and sellers who are eligible to list with the new values (EXCELLENT_REFURBISHED, VERY_GOOD_REFURBISHED, and GOOD_REFURBISHED) in category 9355, must use an OAuth token created with the <a href=\"/api-docs/static/oauth-authorization-code-grant.html\" target=\"_blank\">authorization code grant flow</a> and <b>https://api.ebay.com/oauth/api_scope/sell.inventory</b> scope in order to retrieve the refurbished conditions for the relevant categories. <br/><br/> These restricted item conditions will not be returned if an OAuth token created with the <a href=\"/api-docs/static/oauth-client-credentials-grant.html\" target=\"_blank\">client credentials grant flow</a> and <b>https://api.ebay.com/oauth/api_scope</b> scope is used, or if any seller is not eligible to list with that item condition. <br/><br/> See the <a href=\"/api-docs/static/oauth-scopes.html\" target=\"_blank\">Specifying OAuth scopes</a> topic for more information about specifying scopes.</span><br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the <b>Accept-Encoding</b> request header and setting the value to <code>application/gzip</code>.</span>  # noqa: E501

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Request components</a>. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply <b>categoryId</b> values for the sections of the tree you want returned.  <br><br>When you specify a <b>categoryId</b> value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  <br><br>The parameter takes a list of <b>categoryId</b> values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 <code>categoryId</code> values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  <br><br><b>Example:</b> <code>filter=categoryIds:{100|101|102}</code>  <br><br>Note that you must URL-encode the parameter list, which results in the following filter for the above example: <br><br> &nbsp;&nbsp;<code>filter=categoryIds%3A%7B100%7C101%7C102%7D</code>
        :return: ItemConditionPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_item_condition_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_listing_structure_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_listing_structure_policies  # noqa: E501

        This method returns the eBay policies that define the allowed listing structures for the categories of a specific marketplace. The listing-structure policies currently pertain to whether or not you can list items with variations.  <br><br>By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the <b>filter</b> query parameter to specify only the category IDs you want to review.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the <b>Accept-Encoding</b> request header and setting the value to <code>application/gzip</code>.</span>  # noqa: E501

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Request components</a>. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply <b>categoryId</b> values for the sections of the tree you want returned.  <br><br>When you specify a <b>categoryId</b> value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  <br><br>The parameter takes a list of <b>categoryId</b> values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 <code>categoryId</code> values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  <br><br><b>Example:</b> <code>filter=categoryIds:{100|101|102}</code>  <br><br>Note that you must URL-encode the parameter list, which results in the following filter for the above example: <br><br> &nbsp;&nbsp;<code>filter=categoryIds%3A%7B100%7C101%7C102%7D</code>
        :return: ListingStructurePolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_listing_structure_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_negotiated_price_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_negotiated_price_policies  # noqa: E501

        This method returns the eBay policies that define the supported negotiated price features (like \"best offer\") for the categories of a specific marketplace.  <br><br>By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the <b>filter</b> query parameter to specify only the category IDs you want to review.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the <b>Accept-Encoding</b> request header and setting the value to <code>application/gzip</code>.</span>  # noqa: E501

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Request components</a>. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply <b>categoryId</b> values for the sections of the tree you want returned.  <br><br>When you specify a <b>categoryId</b> value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  <br><br>The parameter takes a list of <b>categoryId</b> values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 <code>categoryId</code> values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  <br><br><b>Example:</b> <code>filter=categoryIds:{100|101|102}</code>  <br><br>Note that you must URL-encode the parameter list, which results in the following filter for the above example: <br><br> &nbsp;&nbsp;<code>filter=categoryIds%3A%7B100%7C101%7C102%7D</code>
        :return: NegotiatedPricePolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_negotiated_price_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_return_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_return_policies  # noqa: E501

        This method returns the eBay policies that define whether or not you must include a return policy for the items you list in the categories of a specific marketplace, plus the guidelines for creating domestic and international return policies in the different eBay categories.  <br><br>By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the <b>filter</b> query parameter to specify only the category IDs you want to review.<br /><br /><span class=\"tablenote\"><span style=\"color:#478415\"><strong>Tip:</strong></span> This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the <b>Accept-Encoding</b> request header and setting the value to <code>application/gzip</code>.</span>  # noqa: E501

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: <a href=\"/api-docs/static/rest-request-components.html#marketpl\" target=\"_blank\">Request components</a>. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply <b>categoryId</b> values for the sections of the tree you want returned.  <br><br>When you specify a <b>categoryId</b> value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  <br><br>The parameter takes a list of <b>categoryId</b> values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 <code>categoryId</code> values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  <br><br><b>Example:</b> <code>filter=categoryIds:{100|101|102}</code>  <br><br>Note that you must URL-encode the parameter list, which results in the following filter for the above example: <br><br> &nbsp;&nbsp;<code>filter=categoryIds%3A%7B100%7C101%7C102%7D</code>
        :return: ReturnPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_return_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_negotiation_find_eligible_items(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """find_eligible_items  # noqa: E501

        This method evaluates a seller's current listings and returns the set of IDs that are eligible for a seller-initiated discount offer to a buyer. A listing ID is returned only when one or more buyers have shown an &quot;interest&quot; in the listing. If any buyers have shown interest in a listing, the seller can initiate a &quot;negotiation&quot; with them by calling sendOfferToInterestedBuyers, which sends all interested buyers a message that offers the listing at a discount. For details about how to create seller offers to buyers, see Sending offers to buyers.  # noqa: E501

        :param str x_ebay_c_marketplace_id: The eBay marketplace on which you want to search for eligible listings. For a complete list of supported marketplaces, see Negotiation API requirements and restrictions. (required)
        :param str limit: This query parameter specifies the maximum number of items to return from the result set on a page in the paginated response. Minimum: 1 &nbsp; &nbsp;Maximum: 200 Default: 10
        :param str offset: This query parameter specifies the number of results to skip in the result set before returning the first result in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 results from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: PagedEligibleItemCollection
        """
        try:
            return self._method_paged(sell_negotiation.Configuration, '/sell/negotiation/v1', sell_negotiation.OfferApi, sell_negotiation.ApiClient, 'find_eligible_items', SellNegotiationException, True, ['sell.negotiation', 'offer'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_negotiation_send_offer_to_interested_buyers(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """send_offer_to_interested_buyers  # noqa: E501

        This method sends eligible buyers offers to purchase items in a listing at a discount. When a buyer has shown interest in a listing, they become &quot;eligible&quot; to receive a seller-initiated offer to purchase the item(s). Sellers use findEligibleItems to get the set of listings that have interested buyers. If a listing has interested buyers, sellers can use this method (sendOfferToInterestedBuyers) to send an offer to the buyers who are interested in the listing. The offer gives buyers the ability to purchase the associated listings at a discounted price. For details about how to create seller offers to buyers, see Sending offers to buyers.  # noqa: E501

        :param str x_ebay_c_marketplace_id: The eBay marketplace on which your listings with &quot;eligible&quot; buyers appear. For a complete list of supported marketplaces, see Negotiation API requirements and restrictions. (required)
        :param CreateOffersRequest body: Send offer to eligible items request.
        :return: SendOfferToInterestedBuyersCollectionResponse
        """
        try:
            return self._method_single(sell_negotiation.Configuration, '/sell/negotiation/v1', sell_negotiation.OfferApi, sell_negotiation.ApiClient, 'send_offer_to_interested_buyers', SellNegotiationException, True, ['sell.negotiation', 'offer'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_recommendation_find_listing_recommendations(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """find_listing_recommendations  # noqa: E501

        The find method currently returns information for a single recommendation type (AD) which contains information that sellers can use to configure Promoted Listings ad campaigns. The response from this method includes an array of the seller's listing IDs, where each element in the array contains recommendations related to the associated listing ID. For details on how to use this method, see Using the Recommendation API to help configure campaigns. The AD recommendation type The AD type contains two sets of information: The promoteWithAd indicator The promoteWithAd response field indicates whether or not eBay recommends you place the associated listing in a Promoted Listings ad campaign. The returned value is set to either RECOMMENDED or UNDETERMINED, where RECOMMENDED identifies the listings that will benefit the most from having them included in an ad campaign. The bid percentage Also known as the &quot;ad rate,&quot; the bidPercentage field provides the current trending bid percentage of similarly promoted items in the marketplace. The ad rate is a user-specified value that indicates the level of promotion that eBay applies to the campaign across the marketplace. The value is also used to calculate the Promotion Listings fee, which is assessed to the seller if a Promoted Listings action results in the sale of an item. Configuring the request You can configure a request to review all of a seller's currently active listings, or just a subset of them. All active listings &ndash; If you leave the request body empty, the request targets all the items currently listed by the seller. Here, the response is filtered to contain only the items where promoteWithAd equals RECOMMENDED. In this case, eBay recommends that all the returned listings should be included in a Promoted Listings ad campaign. Selected listing IDs &ndash; If you populate the request body with a set of listingIds, the response contains data for all the specified listing IDs. In this scenario, the response provides you with information on listings where the promoteWithAd can be either RECOMMENDED or UNDETERMINED. The paginated response Because the response can contain many listing IDs, the findListingRecommendations method paginates the response set. You can control size of the returned pages, as well as an offset that dictates where to start the pagination, using query parameters in the request.  # noqa: E501

        :param str x_ebay_c_marketplace_id: Use this header to specify the eBay marketplace where you list the items for which you want to get recommendations. (required)
        :param FindListingRecommendationRequest body:
        :param str filter: Provide a list of key-value pairs to specify the criteria you want to use to filter the response. In the list, separate each filter key from its associated value with a colon (&quot;:&quot;). Currently, the only supported filter value is recommendationTypes and it supports only the (&quot;AD&quot;) type. Follow the recommendationTypes specifier with the filter type(s) enclosed in curly braces (&quot;{ }&quot;), and separate multiple types with commas. Example: filter=recommendationTypes:{AD} Default: recommendationTypes:{AD}
        :param str limit: Use this query parameter to set the maximum number of ads to return on a page from the paginated response. Default: 10 Maximum: 500
        :param str offset: Specifies the number of ads to skip in the result set before returning the first ad in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: PagedListingRecommendationCollection
        """
        try:
            return self._method_paged(sell_recommendation.Configuration, '/sell/recommendation/v1', sell_recommendation.ListingRecommendationApi, sell_recommendation.ApiClient, 'find_listing_recommendations', SellRecommendationException, True, ['sell.recommendation', 'listing_recommendation'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

        # ANCHOR-er_methods-END"
