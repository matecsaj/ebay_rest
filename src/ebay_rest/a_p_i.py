# Standard library imports
import collections
import datetime
from json import loads
import logging
import os
from threading import Lock
from typing import Callable, Dict, List, Tuple, Union

# Local imports
from .error import Error
from .multiton import Multiton
from .rates import Rates
from .reference import Reference
from .token import ApplicationToken, UserToken, KeyPairToken

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
from .api import developer_client_registration
from .api.developer_client_registration.rest import ApiException as DeveloperClientRegistrationException
from .api import developer_key_management
from .api.developer_key_management.rest import ApiException as DeveloperKeyManagementException
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


class API(metaclass=Multiton):
    """
    A wrapper for all of eBay's REST-ful APIs.

    For an overview of the APIs and more see https://developer.ebay.com/docs.
    """

    # TODO Improve efficiency, unique objects could be created in parallel.
    # Use these to mitigate the duplication risk that Mutition has while treading.
    _lock_application_token = Lock()
    _lock_user_token = Lock()
    _lock_key_pair_token = Lock()
    _lock_rates = Lock()

    __slots__ = (
        "_config_location", "_application", "_user", "_header", "_key_pair", "_sandbox",
        "_marketplace_ids", "_throttle", "_timeout", "_rates", "_end_user_ctx",
        "_application_token", "_user_token", "_key_pair_token", "_async_req",
        "_use_digital_signatures"
    )

    def __init__(self,
                 path: str or None = None,
                 application: str or dict or None = None,
                 user: str or dict or None = None,
                 header: str or dict or None = None,
                 throttle: bool or None = False,
                 timeout: float or None = -1.0,
                 key_pair: str or dict or None = None,
                 digital_signatures: bool or None = False,
                 async_req: bool or None = False,) -> None:
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

        :param
        key_pair (str or dict, optional) :
        Supply the name of the desired eBay public/private key pair record in ebay_rest.json or a dict with
        the key pair details.
        Can omit when ebay_rest.json contains only one record.

        :param
        digital_signatures (bool, optional): Use eBay digital signatures

        :param
        async_req (bool, optional) : When True make asynchronous HTTP requests, defaults to False for synchronous.
        !!!IGNORE THIS OPTION, THE CODE FOR IT IS INCOMPLETE!!!

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
        try:
            self._key_pair = self._process_config_section(
                config_contents, 'key_pairs', key_pair, mandatory=False)
        except Error:
            raise
        self._use_digital_signatures = digital_signatures

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

        # check the key pair keys and values
        key_pair_keys = [
            ('creation_time', False), ('expiration_time', False),
            ('jwe', False), ('private_key', False), ('public_key', False),
            ('signing_key_cipher', False), ('signing_key_id', False)
        ]
        try:
            self._check_keys(self._key_pair, key_pair_keys, 'key_pair')
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

        # check the async_req parameter
        if async_req not in (True, False):
            detail = f"Parameter async_req {async_req} must be unspecified, True or False."
            raise Error(number=99016, reason="Bad async_req parameter.", detail=detail)
        else:
            self._async_req = async_req

        if self._sandbox:  # The sandbox will not return rates so there is no point to doing throttling.
            self._throttle = False
            self._timeout = -1.0
            self._rates = None
        else:
            with API._lock_rates:
                try:
                    # If sandbox starts return rates, you will need to add a sandbox param to the Rates constructor.
                    self._rates = Rates(app_id=self._application['app_id'])
                except Error:
                    raise

        # preload the multipurpose header self._end_user_ctx
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

        with API._lock_application_token:
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

        with API._lock_user_token:
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

        with API._lock_key_pair_token:
            try:
                self._key_pair_token = KeyPairToken(
                    creation_time=self._key_pair.get('creation_time', None),
                    expiration_time=self._key_pair.get('expiration_time', None),
                    jwe=self._key_pair.get('jwe', None),
                    private_key=self._key_pair.get('private_key', None),
                    public_key=self._key_pair.get('public_key', None),
                    signing_key_cipher=self._key_pair.get('signing_key_cipher', None),
                    signing_key_id=self._key_pair.get('signing_key_id', None)
                )
            except Error:
                raise

        return

    @staticmethod
    def _process_config_section(config_contents: dict,
                                section: str,
                                parameter: str or dict or None,
                                mandatory: bool = True,
                                ) -> dict or None:
        """
        Get a configuration section from the parameter or the loaded config file.

        :param config_contents (dict, required)
        :param section (str, required)
        :param parameter (str or dict or None, required)
        :param mandatory (bool, optional)
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
                    sections = config_contents[section].keys()
                    if len(sections) == 1:
                        result = config_contents[section][tuple(sections)[0]]
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
            if mandatory:
                raise Error(number=99003, reason="Get configuration for " + param_name + " problem.", detail=detail)
            else:
                return {}
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

        # Load key pair for digital signature
        use_digital_signatures = (
            self._use_digital_signatures and 'key_management' not in base_path
        )
        if use_digital_signatures:
            self._key_pair_token._ensure_key_pair(self)
            configuration.api_key['key_pair'] = self._key_pair_token.key_dict()

        # Configure the host endpoint
        if self._sandbox:
            configuration.host = configuration.host.replace('.ebay.com',
                                                            '.sandbox.ebay.com')
        # check for flawed host and if so compensate
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

        # Digital signatures
        # Add 'x-ebay-enforce-signature', and then the rest is handled in the modified Swagger code.
        if use_digital_signatures:
            api_instance.api_client.default_headers['x-ebay-enforce-signature'] = 'true'

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
        # Swagger defaults to False, only add the key word argument if need be.
        if self._async_req:
            kwargs["async_req"] = self._async_req
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

        except object_error as e:
            # error.status will be 100 to 599, see https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
            raise Error(number=99000 + e.status, reason=e.reason, detail=e.body)

        except DeveloperKeyManagementException as e:
            raise Error(number=99018, reason="A Digital Signature problem.", detail=f"{e}")

        else:
            if self._async_req:     # TODO Wait for the asynchronous HTTP request to finish.
                detail = f"Don't use async_req=True; the feature is currently incomplete."
                raise Error(number=99017, reason="Bad async_req parameter.", detail=detail)
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

    def get_digital_signature_key(self, create_new=False):
        """Load the details of the current public/private key pair suitable for
        entering into ebay_rest.json or as an API parameter.

        If create_new is True, creates a new public/private key pair if
        (and only if) required. Otherwise, if no private key is supplied,
        return an error.
        """
        if not self._use_digital_signatures:
            raise Error(
                number=99018,
                reason='Digital Signatures not enabled',
                detail='Set digital_signatures=True when creating API instance'
            )

        if not self._key_pair_token._has_valid_key(self):
            if create_new:
                self._key_pair_token._create_key_pair(self)
            else:
                raise Error(
                    number=99019,
                    reason='New key pair needed',
                    detail='get_digital_signature_key parameter create_new parameter must be True'
                )
        key = self._key_pair_token._load_key()
        return key

    # Don't edit the anchors or in-between; instead, edit and run scripts/generate_code.py.
    # ANCHOR-er_methods-START"

    def buy_browse_check_compatibility(self, x_ebay_c_marketplace_id, item_id, **kwargs):  # noqa: E501
        """check_compatibility  

        This method checks if a product is compatible with the specified item. You can use this method to check the compatibility of cars, trucks, and motorcycles with a specific part listed on eBay. For example, to check the compatibility of a part, you pass in the item ID of the part as a URI parameter and specify all the attributes used to define a specific car in the  compatibilityProperties container. If the call is successful, the response will be  COMPATIBLE,  NOT_COMPATIBLE, or  UNDETERMINED. See compatibilityStatus for details.     Note:  The only products supported are cars, trucks, and motorcycles.   To find the attributes and values for a specific marketplace, you can use the compatibility methods in the Taxonomy API. You can use this data to create menus to help buyers specify the product, such as their car.  For more details and a list of the required attributes for the US marketplace that describe motor vehicles, see Check compatibility in the Buy Integration Guide. For an example, see the Samples section.  URLs for this method  Production URL:  https://api.ebay.com/buy/browse/v1/item/{item_id}/check_compatibility   Note:  This method is supported only on Production.   Restrictions  For a list of supported sites and other restrictions, see API Restrictions.   

        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace you want to use.  Note:  This value is case sensitive.For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US  For a list of supported sites see, API Restrictions. (required)
        :param str item_id: The eBay RESTful identifier of an item (such as a part you want to check). This ID is returned by the  Browse and  Feed API methods.    RESTful Item ID Format: v1|#|# For example: v1|2**********2|0 or v1|1**********2|4**********2 For more information about item ID for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview. (required)
        :param CompatibilityPayload body:
        :return: CompatibilityResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'check_compatibility', BuyBrowseException, False, ['buy.browse', 'item'], (x_ebay_c_marketplace_id, item_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_item(self, item_id, **kwargs):  # noqa: E501
        """get_item  

        This method retrieves the details of a specific item, such as description, price, category, all item aspects, condition, return policies, seller feedback and score, shipping options, shipping costs, estimated delivery, and other information the buyer needs to make a purchasing decision.The Buy APIs are designed to let you create an eBay shopping experience in your app or website. This means you will need to know when something, such as the availability, quantity, etc., has changed in any eBay item you are offering. You can do this easily by setting the  fieldgroups URI parameter. This parameter lets you control what is returned in the response. Setting  fieldgroups to COMPACT reduces the response to only those fields that you need in order to check if any item detail has changed.  Setting  fieldgroups to PRODUCT, adds additional fields to the default response that return information about the product of the item. You can use either COMPACT or PRODUCT but not both. For more information, see fieldgroups. URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/item/{item_id}  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/item/{item_id}    Request headers This method uses the  X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.  For details see, Request headers in the Buying Integration Guide.      Restrictions  For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network:  In order to be commissioned for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.   

        :param str item_id: The eBay RESTful identifier of an item. This ID is returned by the  Browse and  Feed API methods.    RESTful Item ID Format: v1|#|# For example: v1|2**********2|0 or v1|1**********2|4**********2 For more information about item ID for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview. (required)
        :param str fieldgroups: This parameter lets you control what is returned in the response. If you do not set this field, the method returns all the details of the item.      Valid Values:     PRODUCT - This adds the additionalImages, additionalProductIdentities, aspectGroups, description, gtins, image, and title product fields to the response, which describe the product associated with the item. See Product for more information about these fields.  COMPACT -  This returns only the following fields, which let you quickly check if the availability or price of the item has changed, if the item has been revised by the seller, or if an item's top-rated plus status has changed for items you have stored.     itemId - The identifier of the item. bidCount - This integer value indicates the total number of bids that have been placed against an auction item. currentBidPrice - This container shows the current highest bid for an auction item. This container will only be returned for auction items. eligibleForInlineCheckout - This parameter returns items based on whether or not the items can be purchased using the Buy Order API.  If the value of this field is true, this indicates that the item can be purchased using the  Order API.  If the value of this field is false, this indicates that the item cannot be purchased using the  Order API and must be purchased on the eBay site.   estimatedAvailabilities -  Returns the item availability information, which is based on the item's quantity.  Note: Changes in quantity are not tracked by sellerItemRevision. itemAffiliateWebURL - The URL of the View Item page of the item, which includes the affiliate tracking ID. This field is only returned if the eBay partner enables affiliate tracking for the item by including the X-EBAY-C-ENDUSERCTX request header in the method.itemCreationDate - This is a timestamp that indicates the date and time an item listing was created. itemEndDate - This is the scheduled end time of the listing. ItemWebURL - The URL of the View Item page of the item. This enables you to include a \"Report Item on eBay\" link that takes the buyer to the View Item page on eBay. From there they can report any issues regarding this item to eBay. legacyItemId - The unique identifier of the eBay listing that contains the item. This is the traditional/legacy ID that is often seen in the URL of the listing View Item page. minimumPriceToBid - This container shows the minimum bid amount that would be accepted as a qualifying bid in an auction listing. This container will only be returned for auction items. price - This is tracked by the revision ID but is returned here to enable you to quickly verify the price of the item. priorityListing - This field is returned as true if the listing is part of a Promoted Listing campaign. Promoted Listings are available to Above Standard and Top Rated sellers with recent sales activity. reservePriceMet - This field indicates whether or not an auction's reserve price (if set by the seller) has been met yet. This field will only be returned for auction items.  sellerItemRevision - An identifier generated/incremented when a seller revises the item. The following are the two types of item revisions:     Seller changes, such as changing the title   eBay system changes, such as changing the quantity when an item is purchased.  This ID is changed only when the seller makes a change to the item. This means you cannot use this value to determine if the quantity has changed. To check if the quantity has changed, use  estimatedAvailabilities. shippingOptions - A container for the cost, carrier, and other details of shipping options. taxes - A container for the tax information for the item, such as the tax jurisdiction, the tax percentage, and the tax type.  topRatedBuyingExperience - A boolean value indicating if this item is a top-rated plus item. A change in the item's top rated plus standing is not tracked by the revision ID. See topRatedBuyingExperience for more information. uniqueBidderCount - This integer value indicates the number of different eBay users who have placed one or more bids on an auction item. This field is only applicable to auction items.  For Example  To check if a stored item's information is current, do following.   Pass in the item ID and set  fieldgroups to COMPACT.  item/v1|4**********8|0?fieldgroups=COMPACT  Do one of the following:     If the  sellerItemRevision field is returned and you haven't stored a revision number for this item, record the number and pass in the item ID in the  getItem method to get the latest information. If the revision number is different from the value you have stored, update the value and pass in the item ID in the  getItem method to get the latest information. If the  sellerItemRevision field is not returned or has not changed, where needed, update the item information with the information returned in the response.       Maximum value:  1 If more than one values is specified, the first value will be used.
        :return: Item
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_item', BuyBrowseException, False, ['buy.browse', 'item'], item_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_item_by_legacy_id(self, legacy_item_id, **kwargs):  # noqa: E501
        """get_item_by_legacy_id  

          This method is a bridge between the eBay legacy APIs, such as   Shopping, and  Finding and the eBay Buy APIs. There are differences between how legacy APIs and RESTful APIs return the identifier of an \"item\" and what the item ID represents. This method lets you use the legacy item ids retrieve the details of a specific item, such as description, price, and other information the buyer needs to make a purchasing decision. It also returns the RESTful item ID, which you can use with all the Buy API  methods. For more information about how to use legacy ids with the Buy APIs, see Legacy API compatibility in the Buying Integration guide. This method returns the item details and requires you to pass in either the item ID of a non-variation item or the item ids of both the parent and child of an item group. An item group is an item that has various aspect differences, such as color, size, storage capacity, etc. When an item group is created, one of the item variations, such as the red shirt size L, is chosen as the \"parent\". All the other items in the group are the children, such as the blue shirt size L, red shirt size M, etc. The  fieldgroups URI parameter lets you control what is returned in the response. Setting  fieldgroups to PRODUCT, adds additional fields to the default response that return information about the product of the item. For more information, see fieldgroups. URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/item/get_item_by_legacy_id?  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/item/get_item_by_legacy_id?    Request headers This method uses the  X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.   For details see, Request headers in the Buying Integration Guide.     Restrictions  For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network:  In order to be commissioned for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.   

        :param str legacy_item_id: Specifies either:  The legacy item ID of an item that is not part of a group.  The legacy item ID of a group, which is the ID of the \"parent\" of the group of items.    Note:  If you pass in a group ID, you must also use the  legacy_variation_id field and pass in the legacy ID of the specific item variation (child ID).  Legacy ids are returned by APIs, such as the Finding API.  The following is an example of using the value of the  ItemID field for a specific item from Finding to get the RESTful  itemId value.      browse/v1/item/get_item_by_legacy_id?legacy_item_id=1**********9   Maximum:  1 (required)
        :param str fieldgroups: This field lets you control what is returned in the response. If you do not set this field, the method returns all the details of the item.  Note: In this method, the only value supported is PRODUCT.  Valid Values:   PRODUCT - This adds the additionalImages, additionalProductIdentities, aspectGroups, description, gtins, image, and title fields to the response, which describe the item's product.  See Product for more information about these fields. Code so that your app gracefully handles any future changes to this list.
        :param str legacy_variation_id: Specifies the legacy item ID of a specific item in an item group, such as the red shirt size L. Legacy ids are returned by APIs, such as the Finding API.      Maximum:  1  Requirement:  You must  always pass in the  legacy_item_id  with the  legacy_variation_id
        :param str legacy_variation_sku: Specifics the legacy SKU of the item. SKU are item ids created by the seller. Legacy SKUs are returned by eBay the  Shopping API. The following is an example of using the value of the  ItemID and  SKU fields to get the RESTful  itemId value.      browse/v1/item/get_item_by_legacy_id?legacy_item_id=1**********9&legacy_variation_sku=V**********M Maximum:  1  Requirement:  You must  always pass in the  legacy_item_id  with the  legacy_variation_sku
        :return: Item
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_item_by_legacy_id', BuyBrowseException, False, ['buy.browse', 'item'], legacy_item_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_items(self, **kwargs):  # noqa: E501
        """get_items  

        This method retrieves the details of specific items that the buyer needs to make a purchasing decision.   Note: This is a  (Limited Release) available only to select Partners. For this method, only the following fields are returned: bidCount, currentBidPrice, eligibleForInlineCheckout, enabledForGuestCheckout, estimatedAvailabilities, itemAffiliateWebUrl, itemCreationDate, itemId, itemWebUrl, legacyItemId, minimumPriceToBid, price, priorityListing, reservePriceMet, sellerItemRevision, taxes, topRatedBuyingExperience, and uniqueBidderCount.The array shippingOptions, which comprises multiple fields, is also returned. URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/item?  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/item?    Request headers This method uses the  X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.   For details see, Request headers in the Buying Integration Guide.    Restrictions  For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to be commissioned for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.   

        :param str item_ids: A list of item IDs. Item IDs are the eBay RESTful identifier of items.  RESTful Item ID Format: v1|#|#For example: v1|2**********2|0 or v1|1**********2|4**********2 In any given request, either item_ids or item_group_ids can be retrieved. Attempting to retrieve both will result in an error.  In a request, multiple item_ids can be passed as comma separated values. Maximum allowed itemIDs:  20 For more information about item IDs for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview.
        :param str item_group_ids: A list of item group IDs. Item group IDs are the eBay RESTful identifier of item groups.  RESTful Group Item ID Format: ############For example: 3**********9In any given request, either item_ids or item_group_ids can be retrieved. Attempting to retrieve both will result in an error.In a request, multiple item_group_ids can be passed as comma separated values. Maximum allowed itemGroupIDs:  10 
        :return: Items
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_items', BuyBrowseException, False, ['buy.browse', 'item'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_items_by_item_group(self, item_group_id, **kwargs):  # noqa: E501
        """get_items_by_item_group  

         This method retrieves the details of the individual items in an item group. An item group is an item that has various aspect differences, such as color, size, storage capacity, etc.  You pass in the item group ID as a URI parameter. You use this method to show the item details of items with multiple aspects, such as color, size, storage capacity, etc.   This method returns two main containers;   items and  commonDescriptions. The  items container has an array of  containers with the details of each item in the group. The  commonDescriptions container has an array of containers for a description and the item ids of all the items that have this exact description. Because items within an item group often have the same description, this decreases the size of the response.  URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/item/get_items_by_item_group?  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/item/get_items_by_item_group?    Request headers This method uses the  X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations.   For details see, Request headers in the Buying Integration Guide.    Restrictions  For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network:  In order to be commissioned for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.    

        :param str item_group_id: Identifier of the item group to return.  An item group is an item that has various aspect differences, such as color, size, storage capacity, etc.  This ID is returned in the  itemGroupHref field of the search and getItem methods.  For Example:  https://api.ebay.com/buy/browse/v1/item/get_items_by_item_group?item_group_id=3**********6 (required)
        :return: ItemGroup
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemApi, buy_browse.ApiClient, 'get_items_by_item_group', BuyBrowseException, False, ['buy.browse', 'item'], item_group_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_search(self, **kwargs):  # noqa: E501
        """search  

        This method searches for eBay items by various query parameters and retrieves summaries of the items. You can search by keyword, category, eBay product ID (ePID), or GTIN, charity ID, or a combination of these.Note: Only listings where FIXED_PRICE (Buy It Now) is a buying option are returned by default. To retrieve listings that do not have FIXED_PRICE as a buying option, the buyingOptions filter can be used to retrieve those listings.Note that an auction listing enabled with the 'Buy it Now' feature will initially show AUCTION and FIXED_PRICE as buying options, but if/when that auction listing receives a qualifying bid, only AUCTION would remain as a buying option. If this happens, the buyingOptions filter would need to be used to retrieve that auction listing.This method also supports the following:Filtering by the value of one or multiple fields, such as listing format, item condition, price range, location, and more. For the fields supported by this method, see the filter parameter.Retrieving the refinements (metadata) of an item , such as item aspects (color, brand), condition, category, etc. using the fieldgroups parameter.Filtering by item aspects and other refinements using the aspect_filter parameter.  Filtering for items that are compatible with a specific product, using the compatibility_filter parameter.Creating aspects histograms, which enables shoppers to drill down in each refinement narrowing the search results.For details and examples of these capabilities, see Browse API in the Buying Integration Guide. Pagination and sort controlsThere are pagination controls (limit and offset fields) and  sort query parameters that control/sort the data that is returned. By default, the results are sorted by "Best Match". For more information about Best Match, see the eBay help page Best Match.URLs for this methodProduction URL:https://api.ebay.com/buy/browse/v1/item_summary/search?Sandbox URL:https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search? Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide.Restrictions  This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions.eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  

        :param str aspect_filter: This field lets you filter by item aspects. The aspect name/value pairs and category, which is required, is used to limit the results to specific aspects of the item. For example, in a clothing category one aspect pair would be Color/Red. For example, the method below uses the category ID for Women's Clothing. This will return only items for a woman's red shirt./buy/browse/v1/item_summary/search?q=shirt&category_ids=15724&aspect_filter=categoryId:15724,Color:{Red} To get a list of the aspect pairs and the category, which is returned in the dominantCategoryId field, set fieldgroups to ASPECT_REFINEMENTS.    /buy/browse/v1/item_summary/search?q=shirt&fieldgroups=ASPECT_REFINEMENTS  Note: The pipe symbol is used as a delimiter between aspect filter values. If a value contains a pipe symbol (for example, the brand name 'Bed|Stü'), you must enter a backslash before the pipe character to prevent it from being evaluated as a delimiter. The following example shows the correct format for entering two brand names as aspect filter values, one of which contains a pipe symbol:/buy/browse/v1/item_summary/search?limit=50&category_ids=3034&filter=buyingOptions:{AUCTION|FIXED_PRICE}&aspect_filter=categoryId:3034,Brand:{Bed\|Stü|Nike}Required: The category ID is required twice; once as a URI parameter and as part of the  aspect_filter. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/gct:AspectFilter
        :param str auto_correct: A query parameter that enables auto correction.Valid Values: KEYWORD
        :param str category_ids: The category ID is used to limit the results. This field can have one category ID or a comma separated list of IDs. For example: /buy/browse/v1/item_summary/search?category_ids=29792  Note: Currently, you can pass in only one category ID per request.  You can also use any combination of the  category_Ids,  epid, and  q fields. This gives you additional control over the result set. For example, let's say you are looking of a toy phone. If you search for \"phone\", the result set will be mobile phones because this is the \"Best Match\" for this search. But if you also include the toy category ID, the results will be what you wanted.  For example: /buy/browse/v1/item_summary/search?q=phone&category_ids=220 The list of eBay category IDs is not published and category IDs are not the same across all the eBay marketplaces. You can use the following techniques to find a category by site:  Use the Category Changes page. Use the Taxonomy API. For details see Get Categories for Buy APIs.  Submit the following method to get the  dominantCategoryId for an item. /buy/browse/v1/item_summary/search?q= keyword&fieldgroups=ASPECT_REFINEMENTS     Note: If a top-level (L1) category is specified, you  must also include the  q query parameter.  Required:  The method must have  category_ids,  epid,  gtin, or  q  (or any combination of these)
        :param str charity_ids: The charity ID is used to limit the results to only items associated with the specified charity. This field can have one charity ID or a comma separated list of IDs. The method will return all the items associated with the specified charities. For example:/buy/browse/v1/item_summary/search?charity_ids=13-1788491,300108469The charity ID is the charity's registration ID, also known as the Employer Identification Number (EIN). In GB, it is the Charity Registration Number (CRN), commonly called \"Charity Number\".   To find the charities eBay supports, you can search for a charity at Charity Search  or go to Charity Shop. To find the charity ID of a specific charity, click on a charity and use the EIN number. For example, the charity ID for  American Red Cross, is 530196605. You  can also use any combination of the category_Ids and q fields with a charity_Ids to filter the result set. This gives you additional control over the result set. Restriction:  This is supported only on the US and GB marketplaces.Maximum:  20 IDs Required: One ID
        :param str compatibility_filter: This field specifies the attributes used to define a specific product. The service searches for items matching the keyword or matching the keyword and a product attribute value in the title of the item.Note: The only products supported are cars, trucks, and motorcycles.For example, if the keyword is brakes and compatibility-filter=Year:2018;Make:BMW, the items returned are items with brakes, 2018, or BMW in the title.The service uses the product attributes to determine whether the item is compatible. The service returns the attributes that are compatible and the  CompatibilityMatchEnum value that indicates how well the item matches the attributes.Tip: See the Samples section for a detailed example.Best Practice: Submit all of the product attributes for the specific product.To find the attributes and values for a specific marketplace, you can use the getCompatibilityProperties method in the Taxonomy API.For more details, see Check compatibility in the Buy Integration Guide.Note: Testing in Sandbox is only supported using mock data. See Testing search in the Sandbox for details.Required:q (keyword)One fitment supported category ID (such as 33559 Brakes)At least one product attribute name/value pair For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/gct:CompatibilityFilter
        :param str epid: The ePID is the eBay product identifier of a product from the eBay product catalog. This field limits the results to only items in the specified ePID. The  Marketing API getMerchandisedProducts method and the Browse API  getItem,  getItemByLegacyId, and  getItemsByItemGroup calls return the ePID of the product.  You can also use the product_summary/search method in the Catalog API to search for the ePID of the product.  For example: /buy/browse/v1/item_summary/search?epid=15032  Maximum:  1     Required:  The method must have   category_ids,  epid,   gtin,  or  q  (or any combination of these)
        :param str fieldgroups: This field is a comma separated list of values that lets you control what is returned in the response. The default is  MATCHING_ITEMS, which returns the items that match the keyword or category specified. The other values return data that can be used to create histograms or provide additional information.Valid Values:  ASPECT_REFINEMENTS - This returns the aspectDistributions container, which has the dominantCategoryId, matchCount, and refinementHref for the various aspects of the items found. For example, if you searched for 'Mustang', some of the aspect would be Model Year, Exterior Color, Vehicle Mileage, etc. Note: ASPECT_REFINEMENTS are category specific.BUYING_OPTION_REFINEMENTS - This returns the buyingOptionDistributions  container, which has the matchCount and refinementHref for AUCTION, FIXED_PRICE (Buy It Now), and CLASSIFIED_AD items.CATEGORY_REFINEMENTS - This returns the categoryDistributions container, which has the categories that the item is in.CONDITION_REFINEMENTS - This returns the conditionDistributions  container, such as NEW, USED, etc. Within these groups are multiple states of the condition. For example, New can be New without tag, New in box, New without box, etc.EXTENDED - This returns the shortDescription field, which provides condition and item aspect information and the itemLocation.city field.MATCHING_ITEMS - This is meant to be used with one or more of the refinement values above. You use this to return the specified refinements and all the matching items.FULL - This returns all the refinement containers and all the matching items.Code so that your app gracefully handles any future changes to this list.Default: MATCHING_ITEMS
        :param str filter: An array of field filters that can be used to limit/customize the result set.  For example: /buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50]You can also combine filters. /buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50],sellers:{rpseller|bigSal}Note: Refer to Buy API Field Filters for details and examples of all supported filters. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:FilterField
        :param str gtin: This field lets you search by the Global Trade Item Number of the item as defined by https://www.gtin.info. You can search only by UPC (Universal Product Code). If you have other formats of GTIN, you need to search by keyword.   For example:  /buy/browse/v1/item_summary/search?gtin=099482432621   Maximum:  1      Required:  The method must have  category_ids,  epid,  gtin, or  q (or any combination of these)
        :param str limit: The number of items from the result set returned in a single page. Note: If a value is set in the limit field, the value of offset must be either zero or a multiple of the limit value. An error is returned for invalid values of offset. Default: 50 Maximum number of items per page (limit): 200  Maximum number of items in a result set: 10,000
        :param str offset: Specifies the number of items to skip in the result set. This is used with the limit field to control the pagination of the output. For example, if offset is 0 and limit is 10, the method will retrieve items 1-10 from the list of items returned; if offset is 10 and limit is 10, the method will retrieve items 11-20 from the list of items returned. Note: The value of offset must be either zero or a multiple of the value set in the limit field. An error is returned for invalid values of offset.  Valid Values: 0-10,000 (inclusive) Default: 0 Maximum number of items returned: 10,000
        :param str q: A string consisting of one or more keywords that are used to search for items on eBay. The keywords are handled as follows:If the keywords are separated by a space, it is treated as an AND. In the following example, the query returns items that have iphone AND ipad./buy/browse/v1/item_summary/search?q=iphone ipadIf the keywords are input using parentheses and separated by a comma, or if they are URL-encoded, it is treated as an OR. In the following examples, the query returns items that have iphone OR ipad./buy/browse/v1/item_summary/search?q=(iphone, ipad)/buy/browse/v1/item_summary/search?q=%28iphone%2c%20ipad%29Restriction: The * wildcard character is not allowed in this field.Required: The method must have category_ids, epid, gtin, or q (or any combination of these). 
        :param str sort: The order and field name that is used to sort the items. You can sort items by price, distance, or listing date. To sort in descending order, insert a hyphen (-) before the name of the sorting option. If no sort parameter is submitted, the result set is sorted by "Best Match".Here are some examples showing how to use the sort query parameter:sort=distance - This sorts by distance in ascending order (shortest distance first). This sorting option is only applicable if the pickup filters are used, and only ascending order is supported.sort=-price - This sorts by price + shipping cost in descending order (highest price first). This sorting option (by price) is only guaranteed to work correctly if the X-EBAY-C-ENDUSERCTX request header is used, with the contextualLocation parameter being used to set the delivery country and postal code. Here is an example of how this header would be used to do this (note the URL encoding):X-EBAY-C-ENDUSERCTX: contextualLocation=country%3DUS%2Czip%3D19406sort=newlyListed - This sorts by listing date (most recently listed/newest items first).sort=endingSoonest - This sorts by date/time the listing ends (listings nearest to end date/time first).Default: Ascending For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:SortField
        :return: SearchPagedCollection
        """
        try:
            return self._method_paged(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ItemSummaryApi, buy_browse.ApiClient, 'search', BuyBrowseException, False, ['buy.browse', 'item_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_search_by_image(self, **kwargs):  # noqa: E501
        """search_by_image  

        Note:   This is an experimental method that is available to select developers approved by business units. For information on how to obtain access to this API in production, see the Buy APIs Requirements. This method searches for eBay items based on a image and retrieves summaries of the items. You pass in a Base64 image in the request payload and can refine the search by category, or eBay product ID (ePID), or a combination of these using URI parameters.  To get the Base64 image string, you can use sites such as https://codebeautify.org/image-to-base64-converter. This method also supports the following:   Filtering by the value of one or multiple fields, such as listing format, item condition, price range, location, and more.  For the fields supported by this method, see the filter parameter.Filtering by item aspects using the aspect_filter parameter.   For details and examples of these capabilities, see Browse API in the Buying Integration Guide.Pagination and sort controls There are pagination controls (limit and offset fields) and  sort query parameters that control/sort the data that is returned. By default, the results are sorted by "Best Match". For more information about  Best Match, see the eBay help page Best Match.    URLs for this methodProduction URL: https://api.ebay.com/buy/browse/v1/item_summary/search_by_image? Sandbox URL:  Due to the data available, this method is not supported in the eBay Sandbox. To test your integration, use the Production URL. Request headers This method uses the  X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide.   URL Encoding for Parameters Query parameter values need to be URL encoded. For details, see URL encoding query parameter values.  For readability, code examples in this document have not been URL encoded. Restrictions  This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network:  In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.    

        :param SearchByImageRequest body: The container for the image information fields.
        :param str aspect_filter: This field lets you filter by item aspects. The aspect name/value pairs and category, which is required, is used to limit the results to specific aspects of the item. For example, in a clothing category one aspect pair would be Color/Red. For example, the method below uses the category ID for Women's Clothing. This will return only items for a woman's red shirt.category_ids=15724&aspect_filter=categoryId:15724,Color:{Red} Required:  The category ID is required twice; once as a URI parameter and as part of the  aspect_filter. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/gct:AspectFilter
        :param str category_ids: The category ID is used to limit the results. This field can have one category ID or a comma separated list of IDs.     Note: Currently, you can pass in only one category ID per request.  You can also use any combination of the  category_Ids and  epid fields. This gives you additional control over the result set. The list of eBay category IDs is not published and category IDs are not the same across all the eBay marketplaces. You can use the following techniques to find a category by site:  Use the Category Changes page. Use the Taxonomy API. For details see Get Categories for Buy APIs.  Submit the following method to get the  dominantCategoryId for an item. /buy/browse/v1/item_summary/search?q= keyword&fieldgroups=ASPECT_REFINEMENTS    Required:  The method must have  category_ids or  epid (or any combination of these)
        :param str charity_ids: The charity ID is used to limit the results to only items associated with the specified charity. This field can have one charity ID or a comma separated list of IDs. The method will return all the items associated with the specified charities. For example:/buy/browse/v1/item_summary/search?charity_ids=13-1788491,300108469The charity ID is the charity's registration ID, also known as the Employer Identification Number (EIN). In GB, it is the Charity Registration Number (CRN), commonly called \"Charity Number\".   To find the charities eBay supports, you can search for a charity at Charity Search  or go to Charity Shop. To find the charity ID of a specific charity, click on a charity and use the EIN number. For example, the charity ID for  American Red Cross, is 530196605. You  can also use any combination of the category_Ids and q fields with a charity_Ids to filter the result set. This gives you additional control over the result set. Restriction:  This is supported only on the US and GB marketplaces.Maximum:  20 IDs Required: One ID
        :param str fieldgroups: This field is a comma separated list of values that lets you control what is returned in the response. The default is MATCHING_ITEMS, which returns the items that match the keyword or category specified. The other values return data that can be used to create histograms or provide additional information.Valid Values:ASPECT_REFINEMENTS - This returns the aspectDistributions container, which has the dominantCategoryId, matchCount, and refinementHref for the various aspects of the items found. For example, if you searched for 'Mustang', some of the aspect would be Model Year,  Exterior Color, Vehicle Mileage, etc.Note: ASPECT_REFINEMENTS are category specific.BUYING_OPTION_REFINEMENTS - This returns the buyingOptionDistributions  container, which has the matchCount and refinementHref for AUCTION, FIXED_PRICE (Buy It Now), and CLASSIFIED_AD items.CATEGORY_REFINEMENTS - This returns the categoryDistributions container, which has the categories that the item is in.CONDITION_REFINEMENTS - This returns the conditionDistributions container, such as  NEW,  USED, etc. Within these groups are multiple states of the condition. For example, New can be New without tag, New in box, New without box, etc.EXTENDED - This returns the shortDescription field, which provides condition and item aspect information and the itemLocation.city field.MATCHING_ITEMS - This is meant to be used with one or more of the refinement values above. You use this to return the specified refinements and all the matching items.FULL - This returns all the refinement containers and all the matching items.Code so that your app gracefully handles any future changes to this list.Default: MATCHING_ITEMS
        :param str filter: An array of field filters that can be used to limit/customize the result set.  For example: /buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50]You can also combine filters. /buy/browse/v1/item_summary/search?q=shirt&filter=price:[10..50],sellers:{rpseller|bigSal}Note: Refer to Buy API Field Filters for details and examples of all supported filters. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:FilterField
        :param str limit: The number of items, from the result set, returned in a single page.   Default: 50     Maximum number of items per page (limit): 200     Maximum number of items in a result set:  10,000
        :param str offset: The number of items to skip in the result set. This is used with the  limit field to control the pagination of the output.  If  offset is 0 and  limit is 10, the method will retrieve items 1-10 from the list of items returned, if  offset is 10 and  limit is 10, the method will retrieve items 11 thru 20 from the list of items returned.   Valid Values: 0-10,000 (inclusive)      Default: 0       Maximum number of items returned:  10,000  
        :param str sort: The order and field name that is used to sort the items. You can sort items by price, distance, or listing date. To sort in descending order, insert a hyphen (-) before the name of the sorting option. If no sort parameter is submitted, the result set is sorted by "Best Match".Here are some examples showing how to use the sort query parameter:sort=distance - This sorts by distance in ascending order (shortest distance first). This sorting option is only applicable if the pickup filters are used, and only ascending order is supported.sort=-price - This sorts by price + shipping cost in descending order (highest price first). This sorting option (by price) is only guaranteed to work correctly if the X-EBAY-C-ENDUSERCTX request header is used, with the contextualLocation parameter being used to set the delivery country and postal code. Here is an example of how this header would be used to do this (note the URL encoding):X-EBAY-C-ENDUSERCTX: contextualLocation=country%3DUS%2Czip%3D19406sort=newlyListed - This sorts by listing date (most recently listed/newest items first).sort=endingSoonest - This sorts by date/time the listing ends (listings nearest to end date/time first).Default: Ascending For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/browse/types/cos:SortField
        :return: SearchPagedCollection
        """
        try:
            return self._method_paged(buy_browse.Configuration, '/buy/browse/v1', buy_browse.SearchByImageApi, buy_browse.ApiClient, 'search_by_image', BuyBrowseException, False, ['buy.browse', 'search_by_image'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_add_item(self, **kwargs):  # noqa: E501
        """add_item  

        Note:   This is an experimental method that is available as a  (Limited Release) to select developers approved by business units. For information on how to obtain access to this API in production, see the Buy APIs Requirements. This method creates an eBay cart for the eBay member, if one does not exist, and adds items to that cart. Because a cart never expires, any item added to the cart will remain in the cart until it is removed.  To use this method, you must submit a RESTful item ID and the quantity of the item. If the  quantity value is greater than the number of available, the  quantity value is changed to the number available and a warning is returned. For example, if there are 15 baseballs available and you set the  quantity value to 50, the service automatically changes the value of quantity to 15.    The response returns all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API.   The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, when the listing has ended or the item is out of stock, whether it has just been added to the cart or has been in the cart for some time, the item will be returned in the  unavailableCartItems container. Note: There are differences between how legacy APIs, such as Finding, and RESTful APIs, such as Browse, return the identifier of an \"item\" and what the item ID represents. If you have an item ID from one of the legacy APIs, you can use the legacy item ID with the  getItemByLegacyId method to retrieve the RESTful ID for that item. For more information about how to use legacy IDs with the Buy APIs, see Legacy API compatibility in the Buying Integration guide. URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/shopping_cart/add_item  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/add_item Note: This method is not available in the eBay API Explorer.   Restrictions   This method can be used only for eBay members. You can only add FIXED_PRICE items.    For a list of supported sites and other restrictions, see API Restrictions.    

        :param AddCartItemInput body:
        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'add_item', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_get_shopping_cart(self, **kwargs):  # noqa: E501
        """get_shopping_cart  

        Note:   This is an experimental method that is available as a  (Limited Release) to select developers approved by business units. For information on how to obtain access to this API in production, see the Buy APIs Requirements. This method retrieves all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API. There are no URI parameters or request payload.  The response returns the summary details of all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API. If the cart is empty, the response is HTTP 204.   The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, when the listing has ended or the item is out of stock, the item will be returned in the  unavailableCartItems container.                         URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/shopping_cart/  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/ Note: This method is not available in the eBay API Explorer.   Restrictions  This method can be used only for eBay members. For a list of supported sites and other restrictions, see API Restrictions.  

        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'get_shopping_cart', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_remove_item(self, **kwargs):  # noqa: E501
        """remove_item  

        Note:   This is an experimental method that is available as a  (Limited Release) to select developers approved by business units. For information on how to obtain access to this API in production, see the Buy APIs Requirements. This method removes a specific item from the eBay member's cart. You specify the ID of the item in the cart (cartItemId) that you want to remove.   The response returns all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API. If you remove the last item in the cart, the response is HTTP 204.  The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, when the listing has ended or the item is out of stock, the item will be returned in the  unavailableCartItems container. Note:  The   cartItemId is not the same as the item ID. The  cartItemId is the identifier of a specific item in the cart and is generated when the item was added to the cart. URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/shopping_cart/remove_item  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/remove_item Note: This method is not available in the eBay API Explorer.   Restrictions  This method can be used only for eBay members. For a list of supported sites and other restrictions, see API Restrictions.  

        :param RemoveCartItemInput body:
        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'remove_item', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_browse_update_quantity(self, **kwargs):  # noqa: E501
        """update_quantity  

        Note:   This is an experimental method that is available as a  (Limited Release) to select developers approved by business units. For information on how to obtain access to this API in production, see the Buy APIs Requirements. This method updates the quantity value of a specific item in the eBay member's cart. You specify the ID of the item in the cart (cartItemId) and the new value for the quantity. If the  quantity value is greater than the number of available, the  quantity value is changed to the number available and a warning is returned. For example, if there are 15 baseballs available and you set the  quantity value to 50, the service automatically changes the value of quantity to 15.   The response returns all the items in the eBay member's cart; items added to the cart while on ebay.com as well as items added to the cart using the Browse API.   The quantity and state of an item changes often. If the item becomes \"unavailable\" such as, the listing has ended or the item is out of stock, the item will be returned in the  unavailableCartItems container. Note:  The   cartItemId is not the same as the item ID. The  cartItemId is the identifier of a specific item in the cart and is generated when the item was added to the cart. URLs for this method   Production URL:  https://api.ebay.com/buy/browse/v1/shopping_cart/update_quantity  Sandbox URL:  https://api.sandbox.ebay.com/buy/browse/v1/shopping_cart/update_quantity Note: This method is not available in the eBay API Explorer.   Restrictions  This method can be used only for eBay members. For a list of supported sites and other restrictions, see API Restrictions.  

        :param UpdateCartItemInput body:
        :return: RemoteShopcartResponse
        """
        try:
            return self._method_single(buy_browse.Configuration, '/buy/browse/v1', buy_browse.ShoppingCartApi, buy_browse.ApiClient, 'update_quantity', BuyBrowseException, True, ['buy.browse', 'shopping_cart'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_deal_get_deal_items(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_deal_items  

        This method retrieves a paginated set of deal items. The result set contains all deal items associated with the specified search criteria and marketplace ID. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  

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
        """get_event  

        This method retrieves the details for an eBay event. The result set contains detailed information associated with the specified event ID, such as applicable coupons, start and end dates, and event terms. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID. (required)
        :param str event_id: The unique identifier for the eBay event. (required)
        :return: Event
        """
        try:
            return self._method_single(buy_deal.Configuration, '/buy/deal/v1', buy_deal.EventApi, buy_deal.ApiClient, 'get_event', BuyDealException, False, ['buy.deal', 'event'], (x_ebay_c_marketplace_id, event_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_deal_get_events(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_events  

        This method returns paginated results containing all eBay events for the specified marketplace. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  

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
        """get_event_items  

        This method returns a paginated set of event items. The result set contains all event items associated with the specified search criteria and marketplace ID. Request headers This method uses the X-EBAY-C-ENDUSERCTX request header to support revenue sharing for eBay Partner Networks and to improve the accuracy of shipping and delivery time estimations. For details see, Request headers in the Buying Integration Guide. Restrictions This method can return a maximum of 10,000 items. For a list of supported sites and other restrictions, see API Restrictions. eBay Partner Network: In order to receive a commission for your sales, you must use the URL returned in the itemAffiliateWebUrl field to forward your buyer to the ebay.com site.  

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
        """get_item_feed  

        This method lets you download a TSV_GZIP (tab separated value gzip)  Item feed file. The feed file contains all the items from  all the child categories of the specified category.  The first line of the file is the header, which labels the columns and indicates the order of the values on each line.  Each header is described in the Response fields section.    There are two types of item feed files generated:  A daily Item feed file containing all the newly listed items for a specific category, date, and marketplace (feed_scope = NEWLY_LISTED) A weekly Item Bootstrap feed file containing  all the items in a specific category and marketplace (feed_scope = ALL_ACTIVE)   Note:   Filters are applied to the feed files. For details, see Feed File Filters. When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future. URLs for this method   Production URL:  https://api.ebay.com/buy/feed/v1_beta/item?  Sandbox URL:  https://api.sandbox.ebay.com/buy/feed/v1_beta/item?   Downloading feed files  Item feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the Range request header. The Content-range response header indicates where in the full resource this partial chunk of data belongs  and the total number of bytes in the file.       For more information about using these headers, see Retrieving a gzip feed file.     In addition to the API, there is an open source Feed SDK written in Java that downloads, combines files into a single file when needed, and unzips the entire feed file. It also lets you specify field filters to curate the items in the file.   Note: A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.  Restrictions  For a list of supported sites and other restrictions, see API Restrictions.  

        :param str accept: The formats that the client accepts for the response.A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format.Default: application/json,text/tab-separated-values (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note:  This value is case sensitive.For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US  For a list of supported sites see, API Restrictions. (required)
        :param str range: This header specifies the range in bytes of the chunks of the gzip file being returned.  Format: bytes=startpos-endpos  For example, the following retrieves the first 10 MBs of the feed file.   Range bytes=0-10485760 For more information about using this header, see Retrieving a gzip feed file. Maximum: 100 MB (10MB in the Sandbox) (required)
        :param str feed_scope: Specifies the type of feed file to return. Valid Values:    NEWLY_LISTED - Returns the daily Item feed file containing all Good 'Til Cancelled items that were listed on the day specified by the  date parameter in the category specified by the  category_id parameter./item?feed_scope=NEWLY_LISTED&category_id=15032&date=20170925ALL_ACTIVE - Returns the weekly Item Bootstrap feed file containing all the Good 'Til Cancelled items in the category specified by the category_id parameter.Note: Bootstrap files are generated every Tuesday and the file is available on Wednesday. However, the exact time the file is available can vary so we recommend you download the Bootstrap file on Thursday. The items in the file are the items that were in the specified category on Sunday. /item?feed_scope=ALL_ACTIVE&category_id=15032  (required)
        :param str category_id: An eBay top-level category ID of the items to be returned in the feed file.  The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplace, you can use the Taxonomy API getCategoryTree method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the categoryTreeNodeLevel field. For example:  \"categoryTreeNodeLevel\": 1 For details see Get Categories for Buy APIs.    Restriction: Must be a top-level (L1) category other than Real Estate. Items listed under Real Estate L1 categories are excluded from all feeds in all marketplaces. (required)
        :param str _date: The date of the daily Item feed file (feed_scope=NEWLY_LISTED) you want. The  date is required only for the daily Item feed file. If you specify a date for the Item Bootstrap file (feed_scope=ALL_ACTIVE), the date is ignored and the latest file is returned. The date the Item Bootstrap feed file was generated is returned in the Last-Modified response header. The  Item feed files are generated every day and there are 14 daily files available.  Note:  The daily Item feed files are available each day after 9AM MST (US Mountain Standard Time), which is -7 hours UTC time. There is a 48 hour latency when generating the  Item feed files. This means you can download the file for July 10th on July 12 after 9AM MST. Note:  For categories with a large number of items, the latency can be up to 72 hours.   Format: yyyyMMdd Requirements:   Required when feed_scope=NEWLY_LISTED  Must be within 3-14 days in the past
        :return: ItemResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemApi, buy_feed.ApiClient, 'get_item_feed', BuyFeedException, False, ['buy.feed', 'item'], (accept, x_ebay_c_marketplace_id, range, feed_scope, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_group_feed(self, accept, x_ebay_c_marketplace_id, feed_scope, category_id, **kwargs):  # noqa: E501
        """get_item_group_feed  

        This method lets you download a TSV_GZIP (tab separated value gzip)  Item Group feed file. An item group is an item that has various aspect differences, such as color, size, storage capacity, etc.  There are two types of item group feed files generated:  A daily Item Group feed file containing the item group variation information associated with items returned in the Item feed file for a specific day, category, and marketplace. (feed_scope = NEWLY_LISTED) A weekly Item Group Bootstrap feed file containing all the item group variation information associated with items returned in the Item Bootstrap feed file for all the items in a specific category.  (feed_scope = ALL_ACTIVE)  Note:   Filters are applied to the feed files. For details, see Feed File Filters.  When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future. The contents of these feed files are based on the contents of the corresponding daily  Item or Item Bootstrap feed file. When a new  Item or Item Bootstrap feed file is generated, the service reads the file and if an item in the file has a  primaryItemGroupId value, which indicates the item is part of an item group, it uses that value to return the item group (parent item) information for that item in the corresponding  Item Group or  Item Group Bootstrap feed file.   This information includes the  name/value pair of the aspects of the items in this group returned in the  variesByLocalizedAspects  column. For example, if the item was a shirt some of the variation names could be Size, Color, etc. Also the images for the various aspects are returned in the additionalImageUrls column. The first line in any feed file is the header, which labels the columns and indicates the order of the values on each line.  Each header is described in the Response fields section. Combining the Item Group and Item feed files The  Item Group or  Item Group Bootstrap feed file contains details about the item group (parent item), including the item group ID  itemGroupId.  You match the value of  itemGroupId from the  Item Group feed file with the value of  primaryItemGroupId from the corresponding daily  Item or Item Bootstrap feed file.            URLs for this method   Production URL:  https://api.ebay.com/buy/feed/v1_beta/item_group?  Sandbox URL:  https://api.sandbox.ebay.com/buy/feed/v1_beta/item_group?   Downloading feed files  Item Group feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the Range request header. The content-range response header indicates where in the full resource this partial chunk of data belongs  and the total number of bytes in the file.       For more information about using these headers, see Retrieving a gzip feed file.    Note:  A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.  Restrictions  For a list of supported sites and other restrictions, see API Restrictions.    

        :param str accept: The formats that the client accepts for the response.A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate error codes that are returned in JSON format.Default: application/json,text/tab-separated-values (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note:  This value is case sensitive.For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US  For a list of supported sites see, API Restrictions. (required)
        :param str feed_scope: Specifies the type of file to return. Valid Values:    NEWLY_LISTED - Returns the Item Group feed file containing the  item group variation information for items in the daily Item feed file that were associated with an item group. The items in this type of Item feed file are items that were listed on the day specified by the  date parameter in the category specified by the category_id parameter. /item_group?feed_scope=NEWLY_LISTED&category_id=15032&date=20170925 ALL_ACTIVE - Returns the weekly Item Group Bootstrap file containing the item group  variation information for items in the weekly Item Bootstrap feed file that were associated with an item group. The items are Good 'Til Cancelled items in the category specified by the  category_id parameter.   Note:  Bootstrap files are generated every Tuesday and the file is available on Wednesday. However, the exact time the file is available can vary so we recommend you download the Bootstrap file on Thursday. The item groups in the file are for the items that were in the specified category on Sunday./item_group?feed_scope=ALL_ACTIVE&category_id=15032   (required)
        :param str category_id: An eBay top-level category ID of the items to be returned in the feed file. The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplaces, you can use the Taxonomy API getCategoryTree method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the categoryTreeNodeLevel field. For example:  \"categoryTreeNodeLevel\": 1 For details see Get Categories for Buy APIs.    Restriction: Must be a top-level category other than Real Estate. Items listed under Real Estate L1 categories are excluded from all feeds in all marketplaces. (required)
        :param str range: This header specifies the range in bytes of the chunks of the gzip file being returned.  Format: bytes=startpos-endpos  For example, the following retrieves the first 10 MBs of the feed file.   Range bytes=0-10485760 For more information about using this header, see Retrieving a gzip feed file. Maximum: 100 MB (10MB in the Sandbox)
        :param str _date:  The date of the daily Item Group feed file (feed_scope=NEWLY_LISTED) you want. The  date is required only for the daily Item Group feed file. If you specify a date for the Item Group Bootstrap file (feed_scope=ALL_ACTIVE), the date is ignored and the latest file is returned. The date the Item Group Bootstrap feed file was generated is returned in the Last-Modified response header. The  Item Group feed files are generated every day and there are 14 daily files available. There is a 48 hour latency when generating the files. This means on July 10, the latest feed file you can download is July 8. Note:  The generated files are stored using MST (US Mountain Standard Time), which is -7 hours UTC time.  Format: yyyyMMdd Requirement: Requirements:   Required only when feed_scope=NEWLY_LISTED  Must be within 3-14 days in the past   
        :return: ItemGroupResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemGroupApi, buy_feed.ApiClient, 'get_item_group_feed', BuyFeedException, False, ['buy.feed', 'item_group'], (accept, x_ebay_c_marketplace_id, feed_scope, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_priority_feed(self, accept, x_ebay_c_marketplace_id, range, category_id, _date, **kwargs):  # noqa: E501
        """get_item_priority_feed  

        Using this method, you can download a TSV_GZIP (tab separated value gzip) Item Priority feed file, which allows you to track changes (deltas) in the status of your priority items, such as when an item is added or removed from a campaign.  The delta feed tracks the changes to the status of items within a category you specify in the input URI. You can also specify a specific date for the feed you want returned.  Important:  You must consume the daily feeds (Item, Item Group) before consuming the Item Priority feed. This ensures that your inventory is up to date. URLs for this method   Production URL:  https://api.ebay.com/buy/feed/v1_beta/item_priority?  Sandbox URL:  https://api.sandbox.ebay.com/buy/feed/v1_beta/item_priority?   Downloading feed files  Note:  Filters are applied to the feed files. For details, see Feed File Filters. When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future.Priority Item feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the Range request header. The Content-range response header indicates where in the full resource this partial chunk of data belongs  and the total number of bytes in the file.       For more information about using these headers, see Retrieving a gzip feed file.     In addition to the API, there is an open source Feed SDK written in Java that downloads, combines files into a single file when needed, and unzips the entire feed file. It also lets you specify field filters to curate the items in the file.   Note:  A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file.  Restrictions  For a list of supported sites and other restrictions, see API Restrictions.  

        :param str accept: The formats that the client accepts for the response.A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate error codes that are returned in JSON format.Default: application/json,text/tab-separated-values (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note:  This value is case sensitive.For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US  For a list of supported sites see, Buy API Support by Marketplace. (required)
        :param str range: Header specifying content range to be retrieved. Only supported range is bytes. Example : bytes = 0-102400. (required)
        :param str category_id: An eBay top-level category ID of the items to be returned in the feed file. The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplaces, you can use the Taxonomy API getCategoryTree method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the categoryTreeNodeLevel field.For example:  \"categoryTreeNodeLevel\": 1 For details see Get the eBay categories of a marketplace.Restriction: Must be a top-level category other than Real Estate. Items listed under Real Estate L1 categories are excluded from all feeds in all marketplaces. (required)
        :param str _date: The date of the feed you want returned. This can be up to 14 days in the past but cannot be set to a date in the future. Format: yyyyMMdd Note:  The daily Item feed files are available each day after 9AM MST (US Mountain Standard Time), which is -7 hours UTC time. There is a 48 hour latency when generating the  Item feed files. This means you can download the file for July 10th on July 12 after 9AM MST. Note:  For categories with a large number of items, the latency can be up to 72 hours.  (required)
        :return: ItemPriorityResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemPriorityApi, buy_feed.ApiClient, 'get_item_priority_feed', BuyFeedException, False, ['buy.feed', 'item_priority'], (accept, x_ebay_c_marketplace_id, range, category_id, _date), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_feed_get_item_snapshot_feed(self, accept, x_ebay_c_marketplace_id, range, category_id, snapshot_date, **kwargs):  # noqa: E501
        """get_item_snapshot_feed  

         The  Hourly Snapshot feed file is generated each hour every day for most categories. This method lets you download an  Hourly Snapshot TSV_GZIP (tab-separated value gzip) feed file containing the details of all the items that have changed  within the specified day and hour for a specific category.  This means to generate the 8AM file of items that have changed from 8AM and 8:59AM, the service starts at 9AM. You can retrieve the 8AM snapshot file at 10AM. Snapshot feeds now include new listings. You can check itemCreationDate to identify listings that were newly created within the specified hour. Note:   Filters are applied to the feed files. For details, see Feed File Filters.  When curating the items returned, be sure to code as if these filters are not applied as they can be changed or removed in the future. You can use the response from this method to update the item details of items stored in your database. By looking at the value of itemSnapshotDate for a given item, you will be able to tell which information is the latest.   Important:  When the value of the  availability column is UNAVAILABLE, only the itemId and  availability columns are populated.   URLs for this method   Production URL:  https://api.ebay.com/buy/feed/v1_beta/item_snapshot?  Sandbox URL:  https://api.sandbox.ebay.com/buy/feed/v1_beta/item_snapshot?   Downloading feed files  Hourly snapshot feed files are binary gzip files. If the file is larger than 100 MB, the download must be streamed in chunks. You specify the size of the chunks in bytes using the Range request header. The Content-range response header indicates where in the full resource this partial chunk of data belongs and the total number of bytes in the file.       For more information about using these headers, see Retrieving a gzip feed file.     Note: A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate errors that are returned in JSON format. For documentation purposes, the successful call response is shown below as JSON fields so that the value returned in each column can be explained. The order of the response fields shows the order of the columns in the feed file. Restrictions  For a list of supported sites and other restrictions, see API Restrictions.    

        :param str accept: The formats that the client accepts for the response.A successful call will always return a TSV.GZIP file; however, unsuccessful calls generate error codes that are returned in JSON format.Default: application/json,text/tab-separated-values (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted. Note:  This value is case sensitive.For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US  For a list of supported sites see, API Restrictions. (required)
        :param str range: This header specifies the range in bytes of the chunks of the gzip file being returned.  Format: bytes=startpos-endpos  For example, the following retrieves the first 10 MBs of the feed file.   Range bytes=0-10485760 For more information about using this header, see Retrieving a gzip feed file. Maximum: 100 MB (10MB in the Sandbox) (required)
        :param str category_id: An eBay top-level category ID  of the items to be returned in the feed file. The list of eBay category IDs changes over time and category IDs are not the same across all the eBay marketplaces. To get a list of the top-level categories for a marketplace, you can use the Taxonomy API getCategoryTree method. This method retrieves the complete category tree for the marketplace. The top-level categories are identified by the categoryTreeNodeLevel field.For example:  \"categoryTreeNodeLevel\": 1 For details see Get Categories for Buy APIs.   Restriction: Must be a top-level category other than Real Estate. Items listed under Real Estate L1 categories are excluded from all feeds in all marketplaces. (required)
        :param str snapshot_date: The date and hour of the snapshot feed file you want. Each file contains the items that changed within the hour in the specified category. So, the 9AM file contains the items that changed between 9AM and 9:59AM on the day specified.  It takes 2 hours to generate a snapshot file, which means to get the file for 9AM the earliest you could submit the call is at 11AM.There are 7 days of  Hourly Snapshot feed files available.Note:  The Feed API uses GMT, so you must convert your local time to GMT. For example, if you lived in California and wanted the September 15th 7pm file, you would submit the following call:  item_snapshot?category_id=625&snapshot_date=2017-09-16T02:00:00.000Z  Format: UTC format (yyyy-MM-ddThh:00:00.000Z) Files are generated on the hour, so minutes and seconds are  always zeros. (required)
        :return: ItemSnapshotResponse
        """
        try:
            return self._method_single(buy_feed.Configuration, '/buy/feed/v1_beta', buy_feed.ItemSnapshotApi, buy_feed.ApiClient, 'get_item_snapshot_feed', BuyFeedException, False, ['buy.feed', 'item_snapshot'], (accept, x_ebay_c_marketplace_id, range, category_id, snapshot_date), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_marketing_get_merchandised_products(self, category_id, metric_name, **kwargs):  # noqa: E501
        """get_merchandised_products  

        This method returns an array of products based on the category and metric specified. This includes details of the product, such as the eBay product ID (EPID), title, and user reviews and ratings for the product. You can use the epid returned by this method in the Browse API search method to retrieve items for this product. Restrictions  To test  getMerchandisedProducts in Sandbox, you must use category ID 9355 and the response will be mock data.   For a list of supported sites and other restrictions, see API Restrictions.   

        :param str category_id: This query parameter limits the products returned to a specific eBay category.   The list of eBay category IDs is not published and category IDs are not all the same across all the eBay marketplace. You can use the following techniques to find a category by site:  Use the Category Changes page. Use the Taxonomy API. For details see Get Categories for Buy APIs.  Use the Browse API and submit the following method to get the  dominantCategoryId for an item. /buy/browse/v1/item_summary/search?q=keyword&fieldgroups=ASPECT_REFINEMENTS    Maximum:  1   Required:  1  (required)
        :param str metric_name: This value filters the result set by the specified metric. Only products in this metric are returned. Currently, the only metric supported is  BEST_SELLING.  Default: BEST_SELLING   Maximum:  1   Required:  1 (required)
        :param str aspect_filter: The aspect name/value pairs used to further refine product results.  For example:    /buy/marketing/v1_beta/merchandised_product?category_id=31388&metric_name=BEST_SELLING&aspect_filter=Brand:Canon You can use the Browse API search method with the fieldgroups=ASPECT_REFINEMENTS field to return the aspects of a product. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketing/types/gct:MarketingAspectFilter
        :param str limit: This value specifies the maximum number of products to return in a result set.   Note: Maximum value means the method will return up to that many products per set, but it can be less than this value. If the number of products found is less than this value, the method will return all of the products matching the criteria.  Default: 8 Maximum: 100
        :return: BestSellingProductResponse
        """
        try:
            return self._method_single(buy_marketing.Configuration, '/buy/marketing/v1_beta', buy_marketing.MerchandisedProductApi, buy_marketing.ApiClient, 'get_merchandised_products', BuyMarketingException, False, ['buy.marketing', 'merchandised_product'], (category_id, metric_name), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_marketplace_insights_search(self, **kwargs):  # noqa: E501
        """search  

        (Limited Release) This method searches for sold eBay items by various URI query parameters and retrieves the sales history of the items for the last 90 days. You can search by keyword, category, eBay product ID (ePID), or GTIN, or a combination of these.     This method also supports the following:   Filtering by the value of one or multiple fields, such as listing format, item condition, price range, location, and more.  For the fields supported by this method, see the filter parameter. Retrieving the refinements (metadata) of an item , such as item aspects (color, brand), condition, category, etc. using the fieldgroups parameter.  Filtering by item aspects and other refinements using the aspect_filter parameter.  Creating aspects histograms, which enables shoppers to drill down in each refinement narrowing the search results.    For details and examples of these capabilities, see Browse API in the Buying Integration Guide. Pagination and sort controlsThere are pagination controls (limit and offset fields) and  sort query parameters that  control/sort the data that is returned. By default, the results are sorted by "Best Match". For more information about  Best Match, see the eBay help page Best Match.   URLs for this method   Production URL:  https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search?  Sandbox URL:  https://api.sandbox.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search?    Request headers You will want to use the  X-EBAY-C-ENDUSERCTX request header with this method. If you are an eBay Network Partner you  must use affiliateCampaignId=ePNCampaignId,affiliateReferenceId=referenceId in the header in order to be paid for selling eBay items on your site . For details see, Request headers in the  Buy APIs Overview. URL Encoding for Parameters Query parameter values need to be URL encoded. For details, see URL encoding query parameter values. Restrictions   For a list of supported sites and other restrictions, see API Restrictions.   

        :param str aspect_filter: This field lets you filter by item aspects. The aspect name/value pairs and category, which is required, is used to limit the results to specific aspects of the item. For example, in a clothing category one aspect pair would be Color/Red. The results are returned in the refinement container.   For example, the method below uses the category ID for Women's Clothing. This will return only sold items for a woman's red or blue shirt.   /buy/marketplace_insights/v1_beta/item_sales/search?q=shirt&category_ids=15724&aspect_filter=categoryId:15724,Color:{Red|Blue} To get a list of the aspects pairs and the category, which is returned in the  dominantCategoryId field, set  fieldgroups to ASPECT_REFINEMENTS.    /buy/marketplace_insights/v1_beta/item_sales/search?q=shirt&category_ids=15724&fieldgroups=ASPECT_REFINEMENTS Format:  aspectName:{value1|value2} Required:  The category ID is required twice; once as a URI parameter and as part of the  aspect_filter parameter. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketplace_insights/types/gct:AspectFilter
        :param str category_ids: The category ID is required and is used to limit the results. For example, if you search for 'shirt' the result set will be very large. But if you also include the category ID 137084, the results will be limited to 'Men's Athletic Apparel'. For example: /buy/marketplace-insights/v1_beta/item_sales/search?q=shirt&category_ids=137084 The list of eBay category IDs is not published and category IDs are not the same across all the eBay marketplaces. You can use the following techniques to find a category by site:   For the US marketplace, use the Category Changes page. Use the Taxonomy API. For details see Get Categories for Buy APIs.    Usage: This field can have one category ID or a comma separated list of IDs. You can use category_ids by itself or use it with any combination of the  gtin,  epid, and  q fields, which gives you additional control over the result set.  Restrictions:   Partners will be given a list of categories they can use.   To use a top-level (L1) category, you  must also include the  q, or  gtin, or  epid  query parameter.    Maximum number of categories: 4
        :param str epid: The ePID is the eBay product identifier of a product from the eBay product catalog. This field limits the results to only items in the specified ePID. /buy/marketplace-insights/v1_beta/item_sales/search?epid=241986085&category_ids=168058 You can use the product_summary/search method in the Catalog API to search for the ePID of the product.    Required:  At least 1  category_ids  Maximum:  1 epid Optional: Any combination of  epid,   gtin,  or  q
        :param str fieldgroups: This field lets you control what is to be returned in the response and accepts a comma separated list of values. The default is  MATCHING_ITEMS, which returns the items that match the keyword or category specified. The other values return data that can be used to create histograms. For code examples see, aspect_filter.  Valid Values:    ASPECT_REFINEMENTS - This returns the aspectDistributions container, which has the  dominantCategoryId,  matchCount, and  refinementHref for the various aspects of the items found. For example, if you searched for 'Mustang', some of the aspect would be  Model Year,   Exterior Color,  Vehicle Mileage, etc.   Note:  ASPECT_REFINEMENTS are category specific.   BUYING_OPTION_REFINEMENTS - This returns the buyingOptionDistributions  container, which has the  matchCount and  refinementHref for  AUCTION and  FIXED_PRICE (Buy It Now) items.  Note: Classified items are not supported.     CATEGORY_REFINEMENTS - This returns the categoryDistributions container, which has the categories that the item is in.     CONDITION_REFINEMENTS - This returns the conditionDistributions  container, such as  NEW,  USED, etc. Within these groups are multiple states of the condition. For example,  New  can be New without tag, New in box, New without box, etc.   MATCHING_ITEMS - This is meant to be used with one or more of the refinement values above. You use this to return the specified refinements and all the matching items.   FULL  - This returns all the refinement containers and all the matching items.  Code so that your app gracefully handles any future changes to this list.  Default:  MATCHING_ITEMS  
        :param str filter: This field supports multiple field filters that can be used to limit/customize the result set. The following lists the supported filters. For details and examples for all the filters, see Buy API Field Filters.     buyingOptions  conditionIds  conditions  itemLocationCountry     lastSoldDate  price  priceCurrency     The following example filters the result set by price. Note: To filter by price, price and priceCurrency must always be used together.   /buy/marketplace-insights/v1_beta/item_sales/search?q=iphone&category_ids=15724&filter=price:[50..500],priceCurrency:USD For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketplace_insights/types/cos:FilterField
        :param str gtin: This field lets you search by the Global Trade Item Number of the item as defined by https://www.gtin.info. This can be a UPC (Universal Product Code), EAN (European Article Number), or an ISBN (International Standard Book Number) value.        /buy/marketplace-insights/v1_beta/item_sales/search?gtin=241986085&category_ids=9355  Required:  At least 1  category_ids  Maximum:  1 gtin Optional: Any combination of  epid,   gtin,  or  q
        :param str limit: The number of items, from the result set, returned in a single page.   Default: 50 Maximum number of items per page (limit): 200    Maximum number of items in a result set:  10,000
        :param str offset: Specifies the number of items to skip in the result set. This is used with the  limit field to control the pagination of the output.  If  offset is 0 and  limit is 10, the method will retrieve items 1-10 from the list of items returned, if  offset is 10 and  limit is 10, the method will retrieve items 11 thru 20 from the list of items returned.   Valid Values: 0-10,000 (inclusive)   Default: 0   Maximum number of items returned:  10,000
        :param str q: A string consisting of one or more keywords that are used to search for items on eBay. The keywords are handled as follows: If the keywords are separated by a comma, it is treated as an AND. In the following example, the query returns items that have iphone  AND ipad./buy/marketplace-insights/v1_beta/item_sales/search?q=iphone,ipad&category_ids=15724    If the keywords are separated by a space, it is treated as an OR.  In the following examples, the query returns items that have iphone  OR ipad.   /buy/marketplace-insights/v1_beta/item_sales/search?q=iphone&category_ids=15724 ipad /buy/marketplace-insights/v1_beta/item_sales/search?q=iphone, ipad&category_ids=15724    Restriction: The * wildcard character is  not allowed in this field.  Required:  At least 1  category_ids Optional: Any combination of  epid,   gtin,  or  q     
        :param str sort: This field specifies the order and the field name to use to sort the items. To sort in descending order use - before the field name.  Currently, you can only sort by price (in ascending or descending order).     If no sort parameter is submitted, the result set is sorted by  "Best Match".     The following are examples of using the  sort query parameter.    SortResult&sort=price Sorts by  price in ascending order (lowest price first)&sort=-price Sorts by  price in descending order (highest price first) Default:  ascending For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/buy/marketplace_insights/types/cos:SortField
        :return: SalesHistoryPagedCollection
        """
        try:
            return self._method_paged(buy_marketplace_insights.Configuration, '/buy/marketplace_insights/v1_beta', buy_marketplace_insights.ItemSalesApi, buy_marketplace_insights.ApiClient, 'search', BuyMarketplaceInsightsException, False, ['buy.marketplace.insights', 'item_sales'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_offer_get_bidding(self, item_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_bidding  

        This method retrieves the bidding details that are specific to the buyer of the specified auction. This must be an auction where the buyer has already placed a bid. To retrieve the bidding information you use a user access token and pass in the item ID of the auction. You can also retrieve general bidding details about the auction, such as minimum bid price and the count of unique bidders, using the Browse API getItem method. URLs for this method Production URL: https://api.ebay.com/buy/offer/v1_beta/bidding/{item_id} Sandbox URL: https://api.sandbox.ebay.com/buy/offer/v1_beta/bidding/{item_id} Restrictions For a list of supported sites and other restrictions, see API Restrictions.  

        :param str item_id: The eBay RESTful identifier of an item that you want the buyer's bidding information. This ID is returned by the Browse and Feed API methods. RESTful Item ID example: v1|2**********2|0 For more information about item ID for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview. Restriction: The buyer must have placed a bid for this item. (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the buyer is based. Note: This value is case sensitive. For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US For a list of supported sites see, API Restrictions. (required)
        :return: Bidding
        """
        try:
            return self._method_single(buy_offer.Configuration, '/buy/offer/v1_beta', buy_offer.BiddingApi, buy_offer.ApiClient, 'get_bidding', BuyOfferException, True, ['buy.offer', 'bidding'], (item_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_offer_place_proxy_bid(self, x_ebay_c_marketplace_id, item_id, **kwargs):  # noqa: E501
        """place_proxy_bid  

        This method uses a user access token to place a proxy bid for the buyer on a specific auction item. The item must offer AUCTION as one of the buyingOptions. To place a bid, you pass in the item ID of the auction as a URI parameter and the buyer's maximum bid amount (maxAmount ) in the payload. By placing a proxy bid, the buyer is agreeing to purchase the item if they win the auction. After this bid is placed, if someone else outbids the buyer a bid, eBay automatically bids again for the buyer up to the amount of their maximum bid. When the bid exceeds the buyer's maximum bid, eBay will notify them that they have been outbid. To find auctions, you can use the Browse API to search for items and use a filter to return only auction items. For example: /buy/browse/v1/item_summary/search?q=iphone&filter=buyingOptions:{AUCTION} URLs for this method Production URL: https://api.ebay.com/buy/offer/v1_beta/bidding/{item_id}/place_proxy_bid Sandbox URL: https://api.sandbox.ebay.com/buy/offer/v1_beta/bidding/{item_id}/place_proxy_bid Restrictions For a list of supported sites and other restrictions, see API Restrictions.  

        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the buyer is based. Note: This value is case sensitive. For example:   X-EBAY-C-MARKETPLACE-ID = EBAY_US For a list of supported sites see, API Restrictions. (required)
        :param str item_id: The eBay RESTful identifier of an item you want to bid on. This ID is returned by the Browse and Feed API methods. RESTful Item ID Example: v1|2**********2|0 For more information about item ID for RESTful APIs, see the Legacy API compatibility section of the Buy APIs Overview. (required)
        :param PlaceProxyBidRequest body:
        :return: PlaceProxyBidResponse
        """
        try:
            return self._method_single(buy_offer.Configuration, '/buy/offer/v1_beta', buy_offer.BiddingApi, buy_offer.ApiClient, 'place_proxy_bid', BuyOfferException, True, ['buy.offer', 'bidding'], (x_ebay_c_marketplace_id, item_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_apply_guest_coupon(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """apply_guest_coupon  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method adds a coupon to an eBay guest checkout session and applies it to all the eligible items in the order.The checkoutSessionId is passed in as a URI parameter and is required. The redemption code of the coupon is in the payload and is also required.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/apply_couponSandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/apply_coupon  

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the  initiateGuestCheckoutSession method.Note: When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See Checkout session restrictions in the Buy Integration Guide for details. (required)
        :param CouponRequest body: The container for the fields used to apply a coupon to a guest checkout session.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'apply_guest_coupon', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_get_guest_checkout_session(self, checkout_session_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_guest_checkout_session  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method returns the details of the specified guest checkout session. The checkoutSessionId is passed in as a URI parameter and is required. This method has no request payload.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}Sandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}  

        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the  initiateGuestCheckoutSession method.Note: When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See Checkout session restrictions in the Buy Integration Guide for details. (required)
        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'get_guest_checkout_session', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (checkout_session_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_initiate_guest_checkout_session(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """initiate_guest_checkout_session  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method creates an eBay guest checkout session, which is the first step in performing a checkout. The method returns a checkoutSessionId that you use as a URI parameter in subsequent guest checkout methods.Also see Negative Testing Using Stubs for information on how to emulate error conditions for this  method using stubs.TIP: To test the entire checkout flow, you might need a \"test\" credit card. You can generate a credit card number from https://www.getcreditcardnumbers.com.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://apix.ebay.com/buy/order/v2/guest_checkout_session/initiateSandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/initiate  

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :param CreateGuestCheckoutSessionRequestV2 body: The container for the fields used by the initiateGuestCheckoutSession method.
        :param str x_ebay_c_enduserctx: A header that is used to specify the affiliateCampaignId, and optionally the affiliateReferenceId, to enable revenue sharing when the buyer purchases items.TIP: See Request headers in the Buying Integration Guide for more information.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'initiate_guest_checkout_session', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_remove_guest_coupon(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """remove_guest_coupon  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method removes a coupon from an eBay guest checkout session. The checkoutSessionId is passed in as a URI parameter and is required. The redemption code of the coupon is specified in the payload and is also required.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/remove_couponSandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/remove_coupon  

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the  initiateGuestCheckoutSession method.Note: When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See Checkout session restrictions in the Buy Integration Guide for details. (required)
        :param CouponRequest body: The container for the fields used by the removeGuestCoupon method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'remove_guest_coupon', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_update_guest_quantity(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """update_guest_quantity  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method changes the quantity of the specified line item in an eBay guest checkout session.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_quantitySandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_quantity  

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the  initiateGuestCheckoutSession method.Note: When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See Checkout session restrictions in the Buy Integration Guide for details. (required)
        :param UpdateQuantity body: The container for the fields used by the updateGuestQuantity method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'update_guest_quantity', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_update_guest_shipping_address(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """update_guest_shipping_address  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method changes the shipping address for the order in an eBay guest checkout session. All the line items in an order must be shipped to the same address, but the shipping method can be specific to the line item.Note: If the address submitted cannot be validated, a warning message will be returned. This does not prevent the method from executing, but you may want to verify the address.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_addressSandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_address  

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the  initiateGuestCheckoutSession method.Note: When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See Checkout session restrictions in the Buy Integration Guide for details. (required)
        :param ShippingAddressImpl body: The container for the fields used by the updateGuestShippingAddress method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'update_guest_shipping_address', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_update_guest_shipping_option(self, x_ebay_c_marketplace_id, checkout_session_id, **kwargs):  # noqa: E501
        """update_guest_shipping_option  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method changes the shipping method for the specified line item in an eBay guest checkout session. The shipping option can be set for each line item. This gives the shopper the ability choose the cost of shipping for each line item.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL:  https://apix.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_optionSandbox URL: https://apix.sandbox.ebay.com/buy/order/v2/guest_checkout_session/{checkoutSessionId}/update_shipping_option   

        :param str x_ebay_c_marketplace_id: A header that identifies the user's business context and is specified using a marketplace ID value.Note: This header does not indicate a language preference or consumer location.See Marketplace ID values for a list of supported values. (required)
        :param str checkout_session_id: The eBay-assigned session ID, for a specific eBay marketplace, that is returned by the  initiateGuestCheckoutSession method.Note: When using this ID, the X-EBAY-C-MARKETPLACE-ID value and developer App ID must be the same as that used when this guest checkout session was created. See Checkout session restrictions in the Buy Integration Guide for details. (required)
        :param UpdateShippingOption body: The container for the fields used by the updateGuestShippingOption method.
        :return: GuestCheckoutSessionResponseV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestCheckoutSessionApi, buy_order.ApiClient, 'update_guest_shipping_option', BuyOrderException, False, ['buy.order', 'guest_checkout_session'], (x_ebay_c_marketplace_id, checkout_session_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def buy_order_get_guest_purchase_order(self, purchase_order_id, **kwargs):  # noqa: E501
        """get_guest_purchase_order  

        Note: The Order API (v2) currently only supports the guest payment/checkout flow. If you need to support member payment/checkout flow, use the v1_beta version of the Order API.(Limited Release) This method is only available to select developers approved by business units.This method retrieves the details about a specific guest purchase order. It returns the line items, including purchase  order status, dates created and modified, item quantity and listing data, payment and shipping information, and prices, taxes, discounts and credits.The purchaseOrderId is passed in as a URI parameter and is required.Note: The purchaseOrderId value is returned in the call-back URL that is sent through the new eBay pay widget. For more information about eBay managed payments and the new Order API payment flow, see Order API in the Buying Integration Guide.You can use this method to not only get the details of a purchase order, but to check the value of the purchaseOrderPaymentStatus field to determine if the order has been paid for. If the order has been paid for, this field will return PAID.For a list of supported sites and other restrictions, see API Restrictions in the Order API overview.The URLs for this method are:Production URL: https://api.ebay.com/buy/order/v2/guest_purchase_order/{purchaseOrderId}Sandbox URL: https://api.sandbox.ebay.com/buy/order/v2/guest_purchase_order/{purchaseOrderId}  

        :param str purchase_order_id: The unique identifier of a purchase order made by a guest buyer, for which details are to be retrieved.Note: This value is returned in the response URL that is sent through the new eBay pay widget. For more information about eBay managed payments and the new Order API payment flow, see Order API in the Buying Integration Guide. (required)
        :return: GuestPurchaseOrderV2
        """
        try:
            return self._method_single(buy_order.Configuration, '/buy/order/v2', buy_order.GuestPurchaseOrderApi, buy_order.ApiClient, 'get_guest_purchase_order', BuyOrderException, False, ['buy.order', 'guest_purchase_order'], purchase_order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_catalog_get_product(self, epid, **kwargs):  # noqa: E501
        """get_product  

        This method retrieves details of the catalog product identified by the eBay product identifier (ePID) specified in the request. These details include the product's title and description, aspects and their values, associated images, applicable category IDs, and any recognized identifiers that apply to the product.  For a new listing, you can use the search method to identify candidate products on which to base the listing, then use the getProduct method to present the full details of those candidate products to the seller to make a a final selection.  

        :param str epid: The ePID of the product being requested. This value can be discovered by issuing the search method and examining the value of the productSummaries.epid field for the desired returned product summary. (required)
        :param str x_ebay_c_marketplace_id: This method also uses the X-EBAY-C-MARKETPLACE-ID header to identify the seller's eBay marketplace. It is required for all marketplaces except EBAY_US, which is the default. Note: This method is limited to EBAY_US, EBAY_AU, EBAY_CA, and EBAY_GB values.
        :return: Product
        """
        try:
            return self._method_single(commerce_catalog.Configuration, '/commerce/catalog/v1_beta', commerce_catalog.ProductApi, commerce_catalog.ApiClient, 'get_product', CommerceCatalogException, True, ['commerce.catalog', 'product'], epid, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_catalog_search(self, **kwargs):  # noqa: E501
        """search  

        This method searches for and retrieves summaries of one or more products in the eBay catalog that match the search criteria provided by a seller. The seller can use the summaries to select the product in the eBay catalog that corresponds to the item that the seller wants to offer for sale. When a corresponding product is found and adopted by the seller, eBay will use the product information to populate the item listing. The criteria supported by search include keywords, product categories, and category aspects. To see the full details of a selected product, use the getProduct call.  In addition to product summaries, this method can also be used to identify refinements, which help you to better pinpoint the product you're looking for. A refinement consists of one or more aspect values and a count of the number of times that each value has been used in previous eBay listings. An aspect is a property (e.g. color or size) of an eBay category, used by sellers to provide details about the items they're listing. The refinement container is returned when you include the fieldGroups query parameter in the request with a value of ASPECT_REFINEMENTS or FULL.  Example A seller wants to find a product that is \"gray\" in color, but doesn't know what term the manufacturer uses for that color. It might be Silver, Brushed Nickel, Pewter, or even Grey. The returned refinement container identifies all aspects that have been used in past listings for products that match your search criteria, along with all of the values those aspects have taken, and the number of times each value was used. You can use this data to present the seller with a histogram of the values of each aspect. The seller can see which color values have been used in the past, and how frequently they have been used, and selects the most likely value or values for their product. You issue the search method again with those values in the aspect_filter parameter to narrow down the collection of products returned by the call.  Although all query parameters are optional, this method must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value. If you provide more than one of these parameters, they will be combined with a logical AND to further refine the returned collection of matching products.  Note: This method requires that certain special characters in the query parameters be percent-encoded:      (space) = %20       , = %2C       : = %3A       [ = %5B       ] = %5D       { = %7B       | = %7C       } = %7D  This requirement applies to all query parameter values. However, for readability, method examples and samples in this documentation will not use the encoding.  This method returns product summaries rather than the full details of the products. To retrieve the full details of a product, use the getProduct method with an ePID.  

        :param str x_ebay_c_marketplace_id: This method also uses the X-EBAY-C-MARKETPLACE-ID header to identify the seller's eBay marketplace. It is required for all marketplaces except EBAY_US, which is the default. Note: This method is limited to EBAY_US, EBAY_AU, EBAY_CA, and EBAY_GB values.
        :param str aspect_filter: An eBay category and one or more aspects of that category, with the values that can be used to narrow down the collection of products returned by this call.  Aspects are product attributes that can represent different types of information for different products. Every product has aspects, but different products have different sets of aspects.  You can determine appropriate values for the aspects by first submitting this method without this parameter. It will return either the productSummaries.aspects container, the refinement.aspectDistributions container, or both, depending on the value of the fieldgroups parameter in the request. The productSummaries.aspects container provides the category aspects and their values that are associated with each returned product. The refinement.aspectDistributions container provides information about the distribution of values of the set of category aspects associated with the specified categories. In both cases sellers can select from among the returned aspects to use with this parameter.   Note: You can also use the Taxonomy API's getItemAspectsForCategory method to retrieve detailed information about aspects and their values that are appropriate for your selected category.   The syntax for the aspect_filter parameter is as follows (on several lines for readability; categoryId is required):  aspect_filter=categoryId:category_id, aspect1:{valueA|valueB|...}, aspect2:{valueC|valueD|...},.  A matching product must be within the specified category, and it must have least one of the values identified for every specified aspect.   Note: Aspect names and values are case sensitive.   Here is an example of an aspect_filter parameter in which 9355 is the category ID, Color is an aspect of that category, and Black and White are possible values of that aspect (on several lines for readability):  GET https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search? aspect_filter=categoryId:9355,Color:{White|Black}  Here is the aspect_filter with required URL encoding and a second aspect (on several lines for readability):  GET https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search? aspect_filter=categoryId:9355,Color:%7BWhite%7CBlack%7D, Storage%20Capacity:%128GB%7C256GB%7D   Note: You cannot use the aspect_filter parameter in the same method with either the gtin parameter or the mpn parameter.  For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/commerce/catalog/types/catal:AspectFilter
        :param str category_ids:  Important: Currently, only the first category_id value is accepted.   One or more comma-separated category identifiers for narrowing down the collection of products returned by this call.   Note: This parameter requires a valid category ID value. You can use the Taxonomy API's getCategorySuggestions method to retrieve appropriate category IDs for your product based on keywords.   The syntax for this parameter is as follows:  category_ids=category_id1,category_id2,.  Here is an example of a method with the category_ids parameter: br /> GET https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search? category_ids=178893   Note: Although all query parameters are optional, this method must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value.  If you provide only the category_ids parameter, you cannot specify a top-level (L1) category. 
        :param str fieldgroups: The type of information to return in the response.   Important: This parameter may not produce valid results if you also provide more than one value for the category_ids parameter. It is recommended that you avoid using this combination.    Valid Values:   ASPECT_REFINEMENTS — This returns the refinement container, which includes the category aspect and aspect value distributions that apply to the returned products. For example, if you searched for Ford Mustang, some of the category aspects might be Model Year, Exterior Color, Vehicle Mileage, and so on.    Note: Aspects are category specific.  FULL — This returns all the refinement containers and all the matching products. This value overrides the other values, which will be ignored. MATCHING_PRODUCTS — This returns summaries for all products that match the values you provide for the q and category_ids parameters. This does not affect your use of the ASPECT_REFINEMENTS value, which you can use in the same call.  Code so that your app gracefully handles any future changes to this list. Default:  MATCHING_PRODUCTS
        :param str gtin: A string consisting of one or more comma-separated Global Trade Item Numbers (GTINs) that identify products to search for. Currently the GTIN values can include EAN, ISBN, and UPC identifier types.   Note: Although all query parameters are optional, this method must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value.   You cannot use the gtin parameter in the same method with either the q parameter or the aspect_filter parameter. 
        :param str limit: The number of product summaries to return. This is the result set, a subset of the full collection of products that match the search or filter criteria of this call.  Maximum: 200  Default: 50
        :param str mpn: A string consisting of one or more comma-separated Manufacturer Part Numbers (MPNs) that identify products to search for. This method will return all products that have one of the specified MPNs.  MPNs are defined by manufacturers for their own products, and are therefore certain to be unique only within a given brand. However, many MPNs do turn out to be globally unique.   Note: Although all query parameters are optional, this method must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value.  You cannot use the mpn parameter in the same method with either the q parameter or the aspect_filter parameter. 
        :param str offset: This parameter is reserved for internal or future use.
        :param str q: A string consisting of one or more keywords to use to search for products in the eBay catalog.   Note: This method searches the following product record fields: title, description, brand, and aspects.localizedName, which do not include product IDs. Wildcard characters (e.g. *) are not allowed.   The keywords are handled as follows:  If the keywords are separated by a comma (e.g. iPhone,256GB), the query returns products that have iPhone AND 256GB. If the keywords are separated by a space (e.g. \"iPhone ipad\" or \"iPhone, ipad\"), the query ignores any commas and returns products that have iPhone OR iPad.   Note: Although all query parameters are optional, this method must include at least the q parameter, or the category_ids, gtin, or mpn parameter with a valid value.   You cannot use the q parameter in the same method with either the gtin parameter or the mpn parameter. 
        :return: ProductSearchResponse
        """
        try:
            return self._method_paged(commerce_catalog.Configuration, '/commerce/catalog/v1_beta', commerce_catalog.ProductSummaryApi, commerce_catalog.ApiClient, 'search', CommerceCatalogException, True, ['commerce.catalog', 'product_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_charity_get_charity_org(self, charity_org_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_charity_org  

        This call is used to retrieve detailed information about supported charitable organizations. It allows users to retrieve the details for a specific charitable organization using its charity organization ID.  

        :param str charity_org_id: The unique ID of the charitable organization. (required)
        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID.Valid Values: EBAY_GB and EBAY_US (required)
        :return: CharityOrg
        """
        try:
            return self._method_single(commerce_charity.Configuration, '/commerce/charity/v1', commerce_charity.CharityOrgApi, commerce_charity.ApiClient, 'get_charity_org', CommerceCharityException, False, ['commerce.charity', 'charity_org'], (charity_org_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_charity_get_charity_orgs(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_charity_orgs  

        This call is used to search for supported charitable organizations. It allows users to search for a specific charitable organization, or for multiple charitable organizations, from a particular charitable domain and/or geographical region, or by using search criteria.The call returns paginated search results containing the charitable organizations that match the specified criteria.  

        :param str x_ebay_c_marketplace_id: A header used to specify the eBay marketplace ID.Valid Values: EBAY_GB and EBAY_US (required)
        :param str limit: The number of items, from the result set, returned in a single page.Valid Values: 1-100Default: 20
        :param str offset: The number of items that will be skipped in the result set. This is used with the limit field to control the pagination of the output.For example, if the offset is set to 0 and the limit is set to 10, the method will retrieve items 1 through 10 from the list of items returned. If the offset is set to 10 and the limit is set to 10, the method will retrieve items 11 through 20 from the list of items returned.Valid Values: 0-10,000Default: 0
        :param str q: A query string that matches the keywords in name, mission statement, or description.
        :param str registration_ids: A comma-separated list of charitable organization registration IDs.Note: Do not specify this parameter for query-based searches. Specify either the q or registration_ids parameter, but not both.Maximum Limit: 20
        :return: CharitySearchResponse
        """
        try:
            return self._method_paged(commerce_charity.Configuration, '/commerce/charity/v1', commerce_charity.CharityOrgApi, commerce_charity.ApiClient, 'get_charity_orgs', CommerceCharityException, False, ['commerce.charity', 'charity_org'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_identity_get_user(self, **kwargs):  # noqa: E501
        """get_user  

        This method retrieves the account profile information for an authenticated user, which requires a User access token. What is returned is controlled by the scopes. For a business account you use the default scope commerce.identity.readonly, which returns all the fields in the businessAccount container. These are returned because this is all public information. For an individual account, the fields returned in the individualAccount container are based on the scope you use. Using the default scope, only public information, such as eBay user ID, are returned. For details about what each scope returns, see the Identity API Overview. URLs for this method Production URL: https://apiz.ebay.com/commerce/identity/v1/user/ Sandbox URL: https://apiz.sandbox.ebay.com/commerce/identity/v1/user/ In the Sandbox, this method returns mock data. Note: You must use the correct scope or scopes for the data you want returned.  

        :return: UserResponse
        """
        try:
            return self._method_single(commerce_identity.Configuration, '/commerce/identity/v1', commerce_identity.UserApi, commerce_identity.ApiClient, 'get_user', CommerceIdentityException, True, ['commerce.identity', 'user'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_media_create_video(self, **kwargs):  # noqa: E501
        """create_video  

        This method creates a video. When using this method, specify the title, size, and classification of the video to be created. Description is an optional field for this method.Tip: See Adding a video to your listing in the eBay Seller Center for details about video formatting requirements and restrictions, or visit the relevant eBay site help pages for the region in which the listings will be posted.When a video is successfully created, the method returns the HTTP Status Code 201 Created.The method also returns the location response header containing the video ID, which you can use to retrieve the video.Note: There is no ability to edit metadata on videos at this time. There is also no method to delete videos.To upload a created video, use the uploadVideo method.  

        :param CreateVideoRequest body:
        :return: None
        """
        try:
            return self._method_single(commerce_media.Configuration, '/commerce/media/v1_beta', commerce_media.VideoApi, commerce_media.ApiClient, 'create_video', CommerceMediaException, True, ['commerce.media', 'video'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_media_get_video(self, video_id, **kwargs):  # noqa: E501
        """get_video  

        This method retrieves a video's metadata and content given a specified video ID. The method returns the title, size, classification, description, video ID, playList, status, status message (if any), expiration  date, and thumbnail image of the retrieved video. The video’s title, size, classification, and description are set using the createVideo method. The video's playList contains two URLs that link to instances of the streaming video based on the supported protocol.The status field contains the current status of the video. After a video upload is successfully completed, the video's status will show as PROCESSING until the video reaches one of the terminal states of LIVE, BLOCKED or PROCESSING_FAILED. If a video's processing fails, it could be because the file is corrupted, is too large, or its size doesn’t match what was provided in the metadata. Refer to the error messages to determine the cause of the video’s failure to upload.  The status message will indicate why a video was blocked from uploading.The video’s expiration date is automatically set to 365 days (one year) after the video’s initial creation.The video's thumbnail image is automatically generated when the video is created.  

        :param str video_id: The video ID for the video to be retrieved. (required)
        :return: Video
        """
        try:
            return self._method_single(commerce_media.Configuration, '/commerce/media/v1_beta', commerce_media.VideoApi, commerce_media.ApiClient, 'get_video', CommerceMediaException, True, ['commerce.media', 'video'], video_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_media_upload_video(self, content_type, video_id, **kwargs):  # noqa: E501
        """upload_video  

        This method associates the specified file with the specified video ID and uploads the input file. After the file has been uploaded the processing of the file begins.Note: The size of the video to be uploaded must exactly match the size of the video's input stream that was set in the createVideo method. If the sizes do not match, the video will not upload successfully.When a video is successfully uploaded, it returns the HTTP Status Code 200 OK.The status flow is PENDING_UPLOAD > PROCESSING > LIVE,  PROCESSING_FAILED, or BLOCKED. After a video upload is successfully completed, the status will show as PROCESSING until the video reaches one of the terminal states of LIVE, BLOCKED, or PROCESSING_FAILED. If the size information (in bytes) provided is incorrect, the API will throw an error.Tip: See Adding a video to your listing in the eBay Seller Center for details about video formatting requirements and restrictions, or visit the relevant eBay site help pages for the region in which the listings will be posted.To retrieve an uploaded video, use the getVideo method.  

        :param str content_type: Use this header to specify the content type for the upload. The Content-Type should be set to application/octet-stream. (required)
        :param str video_id: The video ID for the uploaded video. (required)
        :param InputStream body: The request payload for this method is the input stream for the video source. The input source must be an .mp4 file of the type MPEG-4 Part 10 or Advanced Video Coding (MPEG-4 AVC).
        :param str content_length: Use this header to specify the content length for the upload. Use Content-Range: bytes {1}-{2}/{3} and Content-Length:{4} headers.Note: This header is optional and is only required for resumable uploads (when an upload is interrupted and must be resumed from a certain point).
        :param str content_range: Use this header to specify the content range for the upload. The Content-Range should be of the following bytes ((?:[0-9]+-[0-9]+)|\\\\\\\\*)/([0-9]+|\\\\\\\\*) pattern.Note: This header is optional and is only required for resumable uploads (when an upload is interrupted and must be resumed from a certain point).
        :return: None
        """
        try:
            return self._method_single(commerce_media.Configuration, '/commerce/media/v1_beta', commerce_media.VideoApi, commerce_media.ApiClient, 'upload_video', CommerceMediaException, True, ['commerce.media', 'video'], (content_type, video_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_config(self, **kwargs):  # noqa: E501
        """get_config  

        This method allows applications to retrieve a previously created configuration.  

        :return: Config
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.ConfigApi, commerce_notification.ApiClient, 'get_config', CommerceNotificationException, False, ['commerce.notification', 'config'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_update_config(self, **kwargs):  # noqa: E501
        """update_config  

        This method allows applications to create a new configuration or update an existing configuration. This app-level configuration allows developers to set up alerts.  

        :param Config body: The configurations for this application.
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.ConfigApi, commerce_notification.ApiClient, 'update_config', CommerceNotificationException, False, ['commerce.notification', 'config'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_create_destination(self, **kwargs):  # noqa: E501
        """create_destination  

        This method allows applications to create a destination. A destination is an endpoint that receives HTTP push notifications.A single destination for all topics is valid, as is individual destinations for each topic.To update a destination, use the updateDestination call.The destination created will need to be referenced while creating or updating a subscription to a topic.Note: The destination should be created and ready to respond with the expected challengeResponse for the endpoint to be registered successfully. Refer to the Notification API overview for more information.  

        :param DestinationRequest body: The create destination request.
        :return: object
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'create_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_delete_destination(self, destination_id, **kwargs):  # noqa: E501
        """delete_destination  

        This method provides applications a way to delete a destination.The same destination ID can be used by many destinations.Trying to delete an active destination results in an error. You can disable a subscription, and when the destination is no longer in use, you can delete it.  

        :param str destination_id: The unique identifier for the destination. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'delete_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], destination_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_destination(self, destination_id, **kwargs):  # noqa: E501
        """get_destination  

        This method allows applications to fetch the details for a destination. The details include the destination name, status, and configuration, including the endpoint and verification token.  

        :param str destination_id: The unique identifier for the destination. (required)
        :return: Destination
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'get_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], destination_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_destinations(self, **kwargs):  # noqa: E501
        """get_destinations  

        This method allows applications to retrieve a paginated collection of destination resources and related details. The details include the destination names, statuses, and configurations, including the endpoints and verification tokens.  

        :param str limit: The number of items, from the result set, returned in a single page. Range is from 10-100. If this parameter is omitted, the default value is used.Default: 20Maximum: 100 items per page
        :param str continuation_token: The continuation token for the next set of results.
        :return: DestinationSearchResponse
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'get_destinations', CommerceNotificationException, False, ['commerce.notification', 'destination'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_update_destination(self, destination_id, **kwargs):  # noqa: E501
        """update_destination  

        This method allows applications to update a destination.Note: The destination should be created and ready to respond with the expected challengeResponse for the endpoint to be registered successfully. Refer to the Notification API overview for more information.  

        :param str destination_id: The unique identifier for the destination. (required)
        :param DestinationRequest body: The create subscription request.
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.DestinationApi, commerce_notification.ApiClient, 'update_destination', CommerceNotificationException, False, ['commerce.notification', 'destination'], destination_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_public_key(self, public_key_id, **kwargs):  # noqa: E501
        """get_public_key  

        This method allows users to retrieve a public key using a specified key ID. The public key that is returned in the response payload is used to process and validate eBay notifications.The public key ID, which is a required request parameter for this method, is retrieved from the Base64-encoded X-EBAY-SIGNATURE header that is included in the eBay notification.Note: For more details about how to process eBay push notifications and validate notification message payloads, see the Notification API overview.  

        :param str public_key_id: The unique key ID that is used to retrieve the public key.Note: This is retrieved from the X-EBAY-SIGNATURE header that is included with the push notification. (required)
        :return: PublicKey
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.PublicKeyApi, commerce_notification.ApiClient, 'get_public_key', CommerceNotificationException, False, ['commerce.notification', 'public_key'], public_key_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_create_subscription(self, **kwargs):  # noqa: E501
        """create_subscription  

        This method allows applications to create a subscription for a topic and supported schema version. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.Each application and topic-schema pairing to a subscription should have a 1:1 cardinality.You can create the subscription in disabled mode, test it (see the test method), and when everything is ready, you can enable the subscription (see the enableSubscription method).Note: If an application is not authorized to subscribe to a topic, for example, if your authorization does not include the list of scopes required for the topic, an error code of 195011 is returned.  

        :param CreateSubscriptionRequest body: The create subscription request.
        :return: object
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'create_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_delete_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """delete_subscription  

        This method allows applications to delete a subscription. Subscriptions can be deleted regardless of status.  

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'delete_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_disable_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """disable_subscription  

        This method disables a subscription, which prevents the subscription from providing notifications. To restart a subscription, call enableSubscription.  

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'disable_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_enable_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """enable_subscription  

        This method allows applications to enable a disabled subscription. To pause (or disable) an enabled subscription, call disableSubscription.  

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'enable_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """get_subscription  

        This method allows applications to retrieve subscription details for the specified subscription.Specify the subscription to retrieve using the subscription_id. Use the getSubscriptions method to browse all subscriptions if you do not know the subscription_id.Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: Subscription
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'get_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_subscriptions(self, **kwargs):  # noqa: E501
        """get_subscriptions  

        This method allows applications to retrieve a list of all subscriptions. The list returned is a paginated collection of subscription resources.Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  

        :param str limit: The number of items, from the result set, returned in a single page. Range is from 10-100. If this parameter is omitted, the default value is used.Default: 20Maximum: 100 items per page
        :param str continuation_token: The continuation token for the next set of results.
        :return: SubscriptionSearchResponse
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'get_subscriptions', CommerceNotificationException, False, ['commerce.notification', 'subscription'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_test(self, subscription_id, **kwargs):  # noqa: E501
        """test  

        This method triggers a mocked test payload that includes a notification ID, publish date, and so on. Use this method to test your subscription end-to-end.You can create the subscription in disabled mode, test it using this method, and when everything is ready, you can enable the subscription (see the enableSubscription method).Note: Use the notificationId to tell the difference between a test payload and a real payload.  

        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'test', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_update_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """update_subscription  

        This method allows applications to update a subscription. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.Note: This call returns an error if an application is not authorized to subscribe to a topic.You can pause and restart a subscription. See the disableSubscription and enableSubscription methods.  

        :param str subscription_id: The unique identifier for the subscription. (required)
        :param UpdateSubscriptionRequest body: The create subscription request.
        :return: None
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.SubscriptionApi, commerce_notification.ApiClient, 'update_subscription', CommerceNotificationException, False, ['commerce.notification', 'subscription'], subscription_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_topic(self, topic_id, **kwargs):  # noqa: E501
        """get_topic  

        This method allows applications to retrieve details for the specified topic. This information includes supported schema versions, formats, and other metadata for the topic.Applications can subscribe to any of the topics for a supported schema version and format, limited by the authorization scopes required to subscribe to the topic.A topic specifies the type of information to be received and the data types associated with an event. An event occurs in the eBay system, such as when a user requests deletion or revokes access for an application. An event is an instance of an event type (topic).Specify the topic to retrieve using the topic_id URI parameter.Note: Use the getTopics method to find a topic if you do not know the topic ID.  

        :param str topic_id: The ID of the topic for which to retrieve the details. (required)
        :return: Topic
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.TopicApi, commerce_notification.ApiClient, 'get_topic', CommerceNotificationException, False, ['commerce.notification', 'topic'], topic_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_notification_get_topics(self, **kwargs):  # noqa: E501
        """get_topics  

        This method returns a paginated collection of all supported topics, along with the details for the topics. This information includes supported schema versions, formats, and other metadata for the topics.Applications can subscribe to any of the topics for a supported schema version and format, limited by the authorization scopes required to subscribe to the topic.A topic specifies the type of information to be received and the data types associated with an event. An event occurs in the eBay system, such as when a user requests deletion or revokes access for an application. An event is an instance of an event type (topic).  

        :param str limit: The maximum number of items to return per page from the result set. A result set is the complete set of results returned by the method. Range is from 10-100. If this parameter is omitted, the default value is used. Default: 20Maximum: 100 items per page
        :param str continuation_token: The token used to access the next set of results.
        :return: TopicSearchResponse
        """
        try:
            return self._method_single(commerce_notification.Configuration, '/commerce/notification/v1', commerce_notification.TopicApi, commerce_notification.ApiClient, 'get_topics', CommerceNotificationException, False, ['commerce.notification', 'topic'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_fetch_item_aspects(self, category_tree_id, **kwargs):  # noqa: E501
        """Get Aspects for All Leaf Categories in a Marketplace  

        This call returns a complete list of aspects for all of the leaf categories that belong to an eBay marketplace. The eBay marketplace is specified through the category_tree_id URI parameter. Note: A successful call returns a payload as a gzipped JSON file sent as a binary file using the content-type:application/octet-stream in the response. This file may be large (over 100 MB, compressed). Extract the JSON file from the compressed file with a utility that handles .gz or .gzip. The open source Taxonomy SDK can be used to compare the aspect metadata that is returned in this response. The Taxonomy SDK uses this method to surface changes (new, modified, and removed entities) between an updated version of a bulk downloaded file relative to a previous version.  

        :param str category_tree_id: The unique identifier of the eBay category tree being requested. (required)
        :return: GetCategoriesAspectResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'fetch_item_aspects', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], category_tree_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_category_subtree(self, category_id, category_tree_id, **kwargs):  # noqa: E501
        """Get a Category Subtree  

        This call retrieves the details of all nodes of the category tree hierarchy (the subtree) below a specified category of a category tree. You identify the tree using the category_tree_id parameter, which was returned by the getDefaultCategoryTreeId call in the categoryTreeId field. Note: This call can return a very large payload, so you are strongly advised to submit the request with the following HTTP header:         Accept-Encoding: application/gzip With this header (in addition to the required headers described under HTTP Request Headers), the call returns the response with gzip compression.   

        :param str category_id: The unique identifier of the category at the top of the subtree being requested.   Note: If the category_id submitted identifies the root node of the tree, this call returns an error. To retrieve the complete tree, use this value with the getCategoryTree call.                      If the category_id submitted identifies a leaf node of the tree, the call response will contain information about only that leaf node, which is a valid subtree.     (required)
        :param str category_tree_id: The unique identifier of the eBay category tree from which a category subtree is being requested. (required)
        :return: CategorySubtree
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_category_subtree', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_id, category_tree_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_category_suggestions(self, category_tree_id, q, **kwargs):  # noqa: E501
        """Get Suggested Categories  

        This call returns an array of category tree leaf nodes in the specified category tree that are considered by eBay to most closely correspond to the query string q. Returned with each suggested node is a localized name for that category (based on the Accept-Language header specified for the call), and details about each of the category's ancestor nodes, extending from its immediate parent up to the root of the category tree. Note: This call can return a large payload, so you are advised to submit the request with the following HTTP header:  Accept-Encoding: application/gzip              With this header (in addition to the required headers described under HTTP Request Headers), the call returns the response with gzip compression. You identify the tree using the category_tree_id parameter, which was returned by the getDefaultCategoryTreeId call in the categoryTreeId field. Important: This call is not supported in the Sandbox environment. It will return a response payload in which the categoryName fields contain random or boilerplate text regardless of the query submitted.   

        :param str category_tree_id: The unique identifier of the eBay category tree for which suggested nodes are being requested. (required)
        :param str q: A quoted string that describes or characterizes the item being offered for sale. The string format is free form, and can contain any combination of phrases or keywords. eBay will parse the string and return suggested categories for the item. (required)
        :return: CategorySuggestionResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_category_suggestions', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_tree_id, q), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_category_tree(self, category_tree_id, **kwargs):  # noqa: E501
        """Get a Category Tree  

        This call retrieves the complete category tree that is identified by the category_tree_id parameter. The value of category_tree_id was returned by the getDefaultCategoryTreeId call in the categoryTreeId field. The response contains details of all nodes of the specified eBay category tree, as well as the eBay marketplaces that use this category tree.        Note: This call can return a very large payload, so you are strongly advised to submit the request with the following HTTP header:          Accept-Encoding: application/gzip              With this header (in addition to the required headers described under HTTP Request Headers), the call returns the response with gzip compression.  

        :param str category_tree_id: The unique identifier of the eBay category tree being requested. (required)
        :return: CategoryTree
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_category_tree', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], category_tree_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_compatibility_properties(self, category_tree_id, category_id, **kwargs):  # noqa: E501
        """Get Compatibility Properties  

        This call retrieves the compatible vehicle aspects that are used to define a motor vehicle that is compatible with a motor vehicle part or accessory. The values that are retrieved here might include motor vehicle aspects such as 'Make', 'Model', 'Year', 'Engine', and 'Trim', and each of these aspects are localized for the eBay marketplace. The category_tree_id value is passed in as a path parameter, and this value identifies the eBay category tree. The category_id value is passed in as a query parameter, as this parameter is also required. The specified category must be a category that supports parts compatibility. At this time, this operation only supports parts and accessories listings for cars, trucks, and motorcycles (not boats,  power sports, or any other vehicle types). Only the following eBay marketplaces support parts compatibility:eBay US (Motors and non-Motors categories)eBay Canada (Motors and non-Motors categories)eBay UK eBay Germany eBay Australia eBay Francee Bay Italy eBay Spain  

        :param str category_tree_id: This is the unique identifier of category tree. The following is the list of category_tree_id values and the eBay marketplaces that they represent. One of these ID values must be passed in as a path parameter, and the category_id value, that is passed in as query parameter, must be a valid eBay category on that eBay marketplace that supports parts compatibility for cars, trucks, or motorcycles.eBay US: 0eBay Motors US: 100eBay Canada: 2eBay UK: 3eBay Germany: 77eBay Australia: 15eBay France: 71eBay Italy: 101eBay Spain: 186 (required)
        :param str category_id: The unique identifier of an eBay category. This eBay category must be a valid eBay category on the specified eBay marketplace, and the category must support parts compatibility for cars, trucks, or motorcycles. The getAutomotivePartsCompatibilityPolicies method of the Selling Metadata API can be used to retrieve all eBay categories for an eBay marketplace that supports parts compatibility cars, trucks, or motorcycles. The getAutomotivePartsCompatibilityPolicies method can also be used to see if one or more specific eBay categories support parts compatibility. (required)
        :return: GetCompatibilityMetadataResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_compatibility_properties', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_tree_id, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_compatibility_property_values(self, category_tree_id, compatibility_property, category_id, **kwargs):  # noqa: E501
        """Get Compatibility Property Values  

        This call retrieves applicable compatible vehicle property values based on the specified eBay marketplace, specified eBay category, and filters used in the request. Compatible vehicle properties are returned in the compatibilityProperties.name field of a getCompatibilityProperties response.  One compatible vehicle property applicable to the specified eBay marketplace and eBay category is specified through the required compatibility_property filter. Then, the user has the option of further restricting the compatible vehicle property values that are returned in the response by specifying one or more compatible vehicle property name/value pairs through the filter query parameter. See the documentation in URI parameters section for more information on using the compatibility_property and filter query parameters together to customize the data that is retrieved.  

        :param str category_tree_id: This is the unique identifier of the category tree. The following is the list of category_tree_id values and the eBay marketplaces that they represent. One of these ID values must be passed in as a path parameter, and the category_id value, that is passed in as query parameter, must be a valid eBay category on that eBay marketplace that supports parts compatibility for cars, trucks, or motorcycles.eBay US: 0eBay Motors US: 100eBay Canada: 2eBay UK: 3eBay Germany: 77eBay Australia: 15eBay France: 71eBay Italy: 101eBay Spain: 186 (required)
        :param str compatibility_property: One compatible vehicle property applicable to the specified eBay marketplace and eBay category is specified in this required filter. Compatible vehicle properties are returned in the compatibilityProperties.name field of a getCompatibilityProperties response.  For example, if you wanted to retrieve all vehicle trims for a 2018 Toyota Camry, you would set this filter as follows: compatibility_property=Trim; and then include the following three name/value filters through one filter parameter: filter=Year:2018,Make:Toyota,Model:Camry. So, putting this all together, your URI would look something like this:GET https://api.ebay.com/commerce/taxonomy/v1/category_tree/100/get_compatibility_property_values?category_id=6016&compatibility_property=Trim&filter=filter=Year:2018,Make:Toyota,Model:Camry (required)
        :param str category_id: The unique identifier of an eBay category. This eBay category must be a valid eBay category on the specified eBay marketplace, and the category must support parts compatibility for cars, trucks, or motorcycles. The getAutomotivePartsCompatibilityPolicies method of the Selling Metadata API can be used to retrieve all eBay categories for an eBay marketplace that supports parts compatibility cars, trucks, or motorcycles. The getAutomotivePartsCompatibilityPolicies method can also be used to see if one or more specific eBay categories support parts compatibility. (required)
        :param str filter: One or more compatible vehicle property name/value pairs are passed in through this query parameter. The compatible vehicle property name and corresponding value are delimited with a colon (:), such as filter=Year:2018, and multiple compatible vehicle property name/value pairs are delimited with a comma (,).  For example, if you wanted to retrieve all vehicle trims for a 2018 Toyota Camry, you would set the compatibility_property filter as follows: compatibility_property=Trim; and then include the following three name/value filters through one filter parameter: filter=Year:2018,Make:Toyota,Model:Camry. So, putting this all together, your URI would look something like this:GET https://api.ebay.com/commerce/taxonomy/v1/category_tree/100/get_compatibility_property_values?category_id=6016&compatibility_property=Trim&filter=filter=Year:2018,Make:Toyota,Model:Camry For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/commerce/taxonomy/types/txn:ConstraintFilter
        :return: GetCompatibilityPropertyValuesResponse
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_compatibility_property_values', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_tree_id, compatibility_property, category_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_default_category_tree_id(self, marketplace_id, **kwargs):  # noqa: E501
        """Get a Default Category Tree ID  

        A given eBay marketplace might use multiple category trees, but one of those trees is considered to be the default for that marketplace. This call retrieves a reference to the default category tree associated with the specified eBay marketplace ID. The response includes only the tree's unique identifier and version, which you can use to retrieve more details about the tree, its structure, and its individual category nodes.  

        :param str marketplace_id: The ID of the eBay marketplace for which the category tree ID is being requested. For a list of supported marketplace IDs, see Marketplaces with Default Category Trees. (required)
        :param str accept_language: A header used to indicate the natural language the seller prefers for the response.This specifies the language that the seller wants to use when the field values provided in the request body are displayed to consumers. Note: For details, see Accept-Language in HTTP request headers.Valid Values: For EBAY_CA in French:Accept-Language: fr-CAFor EBAY_BE in French:Accept-Language: fr-BE
        :return: BaseCategoryTree
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_default_category_tree_id', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_taxonomy_get_item_aspects_for_category(self, category_id, category_tree_id, **kwargs):  # noqa: E501
        """get_item_aspects_for_category  

        This call returns a list of aspects that are appropriate or necessary for accurately describing items in the specified leaf category. Each aspect identifies an item attribute (for example, color) for which the seller will be required or encouraged to provide a value (or variation values) when offering an item in that category on eBay.For each aspect, getItemAspectsForCategory provides complete metadata, including:  The aspect's data type, format, and entry mode Whether the aspect is required in listings Whether the aspect can be used for item variations Whether the aspect accepts multiple values for an item Allowed values for the aspect  Use this information to construct an interface through which sellers can enter or select the appropriate values for their items or item variations. Once you collect those values, include them as product aspects when creating inventory items using the Inventory API.  

        :param str category_id: The unique identifier of the leaf category for which aspects are being requested.            Note: If the category_id submitted does not identify a leaf node of the tree, this call returns an error.  (required)
        :param str category_tree_id: The unique identifier of the eBay category tree from which the specified category's aspects are being requested. (required)
        :return: AspectMetadata
        """
        try:
            return self._method_single(commerce_taxonomy.Configuration, '/commerce/taxonomy/v1', commerce_taxonomy.CategoryTreeApi, commerce_taxonomy.ApiClient, 'get_item_aspects_for_category', CommerceTaxonomyException, False, ['commerce.taxonomy', 'category_tree'], (category_id, category_tree_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def commerce_translation_translate(self, body, **kwargs):  # noqa: E501
        """translate  

        This method translates listing title and listing description text from one language into another. For a full list of supported language translations, see the table in the API Overview page.  

        :param TranslateRequest body: (required)
        :return: TranslateResponse
        """
        try:
            return self._method_single(commerce_translation.Configuration, '/commerce/translation/v1_beta', commerce_translation.LanguageApi, commerce_translation.ApiClient, 'translate', CommerceTranslationException, False, ['commerce.translation', 'language'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_analytics_get_rate_limits(self, **kwargs):  # noqa: E501
        """get_rate_limits  

        This method retrieves the call limit and utilization data for an application. The data is retrieved for all RESTful APIs and the legacy Trading API.  The response from getRateLimits includes a list of the applicable resources and the \"call limit\", or quota, that is set for each resource. In addition to quota information, the response also includes the number of remaining calls available before the limit is reached, the time remaining before the quota resets, and the length of the \"time window\" to which the quota applies.  By default, this method returns utilization data for all RESTful API and the legacy Trading API resources. Use the api_name and api_context query parameters to filter the response to only the desired APIs.  For more on call limits, see Compatible Application Check.  

        :param str api_context: This optional query parameter filters the result to include only the specified API context. Valid values: buysell commercedevelopertradingapi
        :param str api_name: This optional query parameter filters the result to include only the APIs specified. Example values:  browse for the Buy APIs inventory for the Sell APIs taxonomy for the Commerce APIs tradingapi for the Trading APIs
        :return: RateLimitsResponse
        """
        try:
            return self._method_single(developer_analytics.Configuration, '/developer/analytics/v1_beta', developer_analytics.RateLimitApi, developer_analytics.ApiClient, 'get_rate_limits', DeveloperAnalyticsException, False, ['developer.analytics', 'rate_limit'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_analytics_get_user_rate_limits(self, **kwargs):  # noqa: E501
        """get_user_rate_limits  

        This method retrieves the call limit and utilization data for an application user. The call-limit data is returned for all RESTful APIs and the legacy Trading API that limit calls on a per-user basis.  The response from getUserRateLimits includes a list of the applicable resources and the \"call limit\", or quota, that is set for each resource. In addition to quota information, the response also includes the number of remaining calls available before the limit is reached, the time remaining before the quota resets, and the length of the \"time window\" to which the quota applies.  By default, this method returns utilization data for all RESTful APIs resources and the legacy Trading API calls that limit request access by user. Use the api_name and api_context query parameters to filter the response to only the desired APIs.  For more on call limits, see Compatible Application Check.  

        :param str api_context: This optional query parameter filters the result to include only the specified API context. Valid values: buy sell commerce developer tradingapi
        :param str api_name: This optional query parameter filters the result to include only the APIs specified. Example values: browse for the Buy APIs inventory for the Sell APIs taxonomy for the Commerce APIs tradingapi for the Trading APIs
        :return: RateLimitsResponse
        """
        try:
            return self._method_single(developer_analytics.Configuration, '/developer/analytics/v1_beta', developer_analytics.UserRateLimitApi, developer_analytics.ApiClient, 'get_user_rate_limits', DeveloperAnalyticsException, True, ['developer.analytics', 'user_rate_limit'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_client_registration_register_client(self, body, **kwargs):  # noqa: E501
        """register_client  

        Note: The Client Registration API is not intended for use by developers who have previously registered for a Developer Account on the eBay platform.This call registers a new third party financial application with eBay.Important! When calling the registerClient method, Third Party Providers (TPPs) are required to pass their valid eIDAS certificate to eBay via Mutual Transport Layer Security (MTLS) handshake Certificate Request messages.A successful call returns an HTTP status code of 201 Created and the response payload.Registering multiple applicationsA regulated third party provider (identified by a unique organizationIdentifier) may register up to 15 different applications with eBay provided the unique software_id for each application is passed in at the time of registration.Each registerClient call that passes in a unique software_id will generate new client_id and client_secret keypairs.If a third party provider calls registerClient using a previously registered software_id, the existing client_id and client_secret keypairs are returned.Note: For additional information about using an organizationIdentifier, refer to the following sections of ETSI Technical Specification 119 495Section 5.2.1: Authorization Number or other recognized identifier for Open Banking;Section 5.4: Profile Requirements for Digital Signatures.  

        :param ClientSettings body: This container stores information about the third party provider's financial application that is being registered. (required)
        :return: ClientDetails
        """
        try:
            return self._method_single(developer_client_registration.Configuration, '/developer/registration/v1', developer_client_registration.RegisterApi, developer_client_registration.ApiClient, 'register_client', DeveloperClientRegistrationException, False, ['developer.client.registration', 'register'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_key_management_create_signing_key(self, **kwargs):  # noqa: E501
        """create_signing_key  

        This method creates keypairs using one of the following ciphers:ED25519 (Edwards Curve)RSANote: The recommended signature cipher is ED25519 (Edwards Curve) since it uses much shorter keys and therefore decreases the header size. However, for development frameworks that do not support ED25519, RSA is also supported.Following a successful completion, the following keys are returned:Private KeyPublic KeyPublic Key as JWEOnce keypairs are created, developers are strongly advised to create and store a local copy of each keypair for future reference. Although the Public Key, Public Key as JWE, and metadata for keypairs may be retrieved by the getSigningKey and getSigningKeys methods, in order to further ensure the security of confidential client information, eBay does not store the Private Key value in any system. If a developer loses their Private Key they must generate new keypairs using the createSigningKey method.Note: For additional information about using keypairs, refer to Digital Signatures for APIs.  

        :param CreateSigningKeyRequest body:
        :return: SigningKey
        """
        try:
            return self._method_single(developer_key_management.Configuration, '/developer/key_management/v1', developer_key_management.SigningKeyApi, developer_key_management.ApiClient, 'create_signing_key', DeveloperKeyManagementException, False, ['developer.key.management', 'signing_key'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_key_management_get_signing_key(self, signing_key_id, **kwargs):  # noqa: E501
        """get_signing_key  

        This method returns the Public Key, Public Key as JWE, and metadata for a specified signingKeyId associated with the application key making the call.Note: It is important to note that the privateKey value is not returned. In order to further ensure the security of confidential client information, eBay does not store the privateKey value in any system. If a developer loses their privateKey they must generate new keypairs using the createSigningKey method.  

        :param str signing_key_id: The system-generated eBay ID of the keypairs being requested. (required)
        :return: SigningKey
        """
        try:
            return self._method_single(developer_key_management.Configuration, '/developer/key_management/v1', developer_key_management.SigningKeyApi, developer_key_management.ApiClient, 'get_signing_key', DeveloperKeyManagementException, False, ['developer.key.management', 'signing_key'], signing_key_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def developer_key_management_get_signing_keys(self, **kwargs):  # noqa: E501
        """get_signing_keys  

        This method returns the Public Key, Public Key as JWE, and metadata for all keypairs associated with the application key making the call.Note: It is important to note that privateKey values are not returned. In order to further ensure the security of confidential client information, eBay does not store privateKey values in any system. If a developer loses their privateKey they must generate new keypairs set using the createSigningKey method.  

        :return: QuerySigningKeysResponse
        """
        try:
            return self._method_single(developer_key_management.Configuration, '/developer/key_management/v1', developer_key_management.SigningKeyApi, developer_key_management.ApiClient, 'get_signing_keys', DeveloperKeyManagementException, False, ['developer.key.management', 'signing_key'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_advertising_eligibility(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_advertising_eligibility  

        This method allows developers to check the seller eligibility status for eBay advertising programs.  

        :param str x_ebay_c_marketplace_id: The unique identifier of the eBay marketplace for which the seller eligibility status shall be checked.Note: This value is case-sensitive. (required)
        :param str program_types: A comma-separated list of eBay advertising programs.Tip: See the  AdvertisingProgramEnum type for possible values.If no programs are specified, the results will be returned for all programs.
        :return: SellerEligibilityMultiProgramResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.AdvertisingEligibilityApi, sell_account.ApiClient, 'get_advertising_eligibility', SellAccountException, True, ['sell.account', 'advertising_eligibility'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_sales_tax_jurisdictions(self, country_code, **kwargs):  # noqa: E501
        """get_sales_tax_jurisdictions  

        This method retrieves all the sales tax jurisdictions for the country that you specify in the countryCode path parameter. Countries with valid sales tax jurisdictions are Canada and the US.  The response from this call tells you the jurisdictions for which a seller can configure tax tables. Although setting up tax tables is optional, you can use the createOrReplaceSalesTax in the Account API call to configure the tax tables for the jurisdictions you sell to.  

        :param str country_code: This path parameter specifies the two-letter ISO 3166 country code for the country whose jurisdictions you want to retrieve. eBay provides sales tax jurisdiction information for Canada and the United States.Valid values for this path parameter are CA and US. (required)
        :return: SalesTaxJurisdictions
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CountryApi, sell_account.ApiClient, 'get_sales_tax_jurisdictions', SellAccountException, False, ['sell.account', 'country'], country_code, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_custom_policy(self, body, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """create_custom_policy  

        This method creates a new custom policy in which a seller specifies their terms for complying with local governmental regulations. Two Custom Policy types are supported: Product Compliance (PRODUCT_COMPLIANCE) Take back (TAKE_BACK)Each Custom Policy targets a policyType and eBay marketplace combination. Multiple policies may be created as follows: Product Compliance: a maximum of 10 policies per eBay marketplace may be created Take back: a maximum of 3 policies per eBay marketplace may be createdA successful create policy call returns an HTTP status code of 201 Created with the system-generated policy ID included in the Location response header.Product Compliance PolicyProduct Compliance policies disclose product information as required for regulatory compliance.Note: A maximum of 10 Product Compliance policies per eBay marketplace may be created.  Take back PolicyTake back policies describe the seller's legal obligation to take back a previously purchased item when the buyer purchases a new one.Note: A maximum of 3 Take back policies per eBay marketplace may be created.  

        :param CustomPolicyCreateRequest body: Request to create a new Custom Policy. (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay marketplace for the custom policy that is being created. Supported values for this header can be found in the MarketplaceIdEnum type definition.  Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR) (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'create_custom_policy', SellAccountException, True, ['sell.account', 'custom_policy'], (body, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_custom_policies(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_custom_policies  

        This method retrieves the list of custom policies specified by the policy_types query parameter for the selected eBay marketplace.  Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR)For details on header values, see HTTP request headers.  

        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay marketplace for the custom policy that is being created. Supported values for this header can be found in the MarketplaceIdEnum type definition.  Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR) (required)
        :param str policy_types: This query parameter specifies the type of custom policies to be returned.Multiple policy types may be requested in a single call by providing a comma-delimited set of all policy types to be returned.Note: Omitting this query parameter from a request will also return policies of all policy types.Two Custom Policy types are supported: Product Compliance (PRODUCT_COMPLIANCE) Take back (TAKE_BACK)
        :return: CustomPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'get_custom_policies', SellAccountException, True, ['sell.account', 'custom_policy'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_custom_policy(self, custom_policy_id, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_custom_policy  

        This method retrieves the custom policy specified by the custom_policy_id path parameter for the selected eBay marketplace.  Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR)For details on header values, see HTTP request headers.  

        :param str custom_policy_id: This path parameter is the unique custom policy identifier for the policy to be returned.Note: This value is automatically assigned by the system when the policy is created. (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay marketplace for the custom policy that is being created. Supported values for this header can be found in the MarketplaceIdEnum type definition.  Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR) (required)
        :return: CustomPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'get_custom_policy', SellAccountException, True, ['sell.account', 'custom_policy'], (custom_policy_id, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_custom_policy(self, body, x_ebay_c_marketplace_id, custom_policy_id, **kwargs):  # noqa: E501
        """update_custom_policy  

        This method updates an existing custom policy specified by the custom_policy_id path parameter for the selected marketplace. This method overwrites the policy's Name, Label, and Description fields. Therefore, the complete, current text of all three policy fields must be included in the request payload even when one or two of these fields will not actually be updated. For example, the value for the Label field is to be updated, but the Name and Description values will remain unchanged. The existing Name and Description values, as they are defined in the current policy, must also be passed in. A successful policy update call returns an HTTP status code of 204 No Content.Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR)For details on header values, see HTTP request headers.  

        :param CustomPolicyRequest body: Request to update a current custom policy. (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay marketplace for the custom policy that is being created. Supported values for this header can be found in the MarketplaceIdEnum type definition.  Note: The following eBay marketplaces support Custom Policies: Germany (EBAY_DE) Canada (EBAY_CA) Australia (EBAY_AU) United States (EBAY_US) France (EBAY_FR) (required)
        :param str custom_policy_id: This path parameter is the unique custom policy identifier for the policy to be returned.Note: This value is automatically assigned by the system when the policy is created. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.CustomPolicyApi, sell_account.ApiClient, 'update_custom_policy', SellAccountException, True, ['sell.account', 'custom_policy'], (body, x_ebay_c_marketplace_id, custom_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_fulfillment_policy(self, body, **kwargs):  # noqa: E501
        """create_fulfillment_policy  

        This method creates a new fulfillment policy where the policy encapsulates seller's terms for fulfilling item purchases. Fulfillment policies include the shipment options that the seller offers to buyers.  Each policy targets a specific eBay marketplace and a category group type, and you can create multiple policies for each combination. A successful request returns the getFulfillmentPolicy URI to the new policy in the Location response header and the ID for the new policy is returned in the response payload.  Tip: For details on creating and using the business policies supported by the Account API, see eBay business policies. Using the eBay standard envelope service (eSE) The eBay standard envelope service (eSE) is a domestic envelope service with tracking through eBay. This service applies to specific Trading Cards categories (not all categories are supported), and to Coins & Paper Money, Postcards, and Stamps. See Using the eBay standard envelope (eSE) service.  

        :param FulfillmentPolicyRequest body: Request to create a seller account fulfillment policy. (required)
        :return: SetFulfillmentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'create_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_fulfillment_policy(self, fulfillment_policy_id, **kwargs):  # noqa: E501
        """delete_fulfillment_policy  

        This method deletes a fulfillment policy. Supply the ID of the policy you want to delete in the fulfillmentPolicyId path parameter.  

        :param str fulfillment_policy_id: This path parameter specifies the ID of the fulfillment policy to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'delete_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], fulfillment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_fulfillment_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_fulfillment_policies  

        This method retrieves all the fulfillment policies configured for the marketplace you specify using the marketplace_id query parameter.  Marketplaces and locales Get the correct policies for a marketplace that supports multiple locales using the Content-Language request header. For example, get the policies for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers.  

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policies you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :return: FulfillmentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'get_fulfillment_policies', SellAccountException, True, ['sell.account', 'fulfillment_policy'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_fulfillment_policy(self, fulfillment_policy_id, **kwargs):  # noqa: E501
        """get_fulfillment_policy  

        This method retrieves the complete details of a fulfillment policy. Supply the ID of the policy you want to retrieve using the fulfillmentPolicyId path parameter.  

        :param str fulfillment_policy_id: This path parameter specifies the ID of the fulfillment policy you want to retrieve. (required)
        :return: FulfillmentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'get_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], fulfillment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_fulfillment_policy_by_name(self, marketplace_id, name, **kwargs):  # noqa: E501
        """get_fulfillment_policy_by_name  

        This method retrieves the details for a specific fulfillment policy. In the request, supply both the policy name and its associated marketplace_id as query parameters.   Marketplaces and locales Get the correct policy for a marketplace that supports multiple locales using the Content-Language request header. For example, get a policy for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers.  

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :param str name: This query parameter specifies the seller-defined name of the fulfillment policy you want to retrieve. (required)
        :return: FulfillmentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'get_fulfillment_policy_by_name', SellAccountException, True, ['sell.account', 'fulfillment_policy'], (marketplace_id, name), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_fulfillment_policy(self, body, fulfillment_policy_id, **kwargs):  # noqa: E501
        """update_fulfillment_policy  

        This method updates an existing fulfillment policy. Specify the policy you want to update using the fulfillment_policy_id path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload.  

        :param FulfillmentPolicyRequest body: Fulfillment policy request (required)
        :param str fulfillment_policy_id: This path parameter specifies the ID of the fulfillment policy you want to update. (required)
        :return: SetFulfillmentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.FulfillmentPolicyApi, sell_account.ApiClient, 'update_fulfillment_policy', SellAccountException, True, ['sell.account', 'fulfillment_policy'], (body, fulfillment_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_kyc(self, **kwargs):  # noqa: E501
        """get_kyc  

        Note:This method was originally created to see which onboarding requirements were still pending for sellers being onboarded for eBay managed payments, but now that all seller accounts are onboarded globally, this method should now just returne an empty payload with a 204 No Content HTTP status code.   

        :return: KycResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.KycApi, sell_account.ApiClient, 'get_kyc', SellAccountException, True, ['sell.account', 'kyc'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_inventory_location(self, body, merchant_location_key, **kwargs):  # noqa: E501
        """create_inventory_location  

        Use this call to create a new inventory location. In order to create and publish an offer (and create an eBay listing), a seller must have at least one inventory location, as every offer must be associated with a location.Upon first creating an inventory location, only a seller-defined location identifier and a physical location is required, and once set, these values can not be changed. The unique identifier value (merchantLocationKey) is passed in at the end of the call URI. This merchantLocationKey value will be used in other Inventory Location calls to identify the inventory location to perform an action against.At this time, location types are either warehouse or store. Warehouse locations are used for traditional shipping, and store locations are generally used by US merchants selling products through the In-Store Pickup program, or used by UK, Australian, and German merchants selling products through the Click and Collect program. A full address is required for store inventory locations. However, for warehouse inventory locations, a full street address is not needed, but the city, state/province, and country of the location must be provided. Note that all inventory locations are \"enabled\" by default when they are created, and you must specifically disable them (by passing in a value of DISABLED in the merchantLocationStatus field) if you want them to be set to the disabled state. The seller's inventory cannot be loaded to inventory locations in the disabled state. In addition to the authorization header, which is required for all eBay REST API calls, the following table includes another request header that is mandatory for the createInventoryLocation call, and two other request headers that are optional:   Header Description Required? Applicable Values   Accept Describes the response encoding, as required by the caller. Currently, the interfaces require payloads formatted in JSON, and JSON is the default. No application/json   Content-Language Use this header to control the language that is used for any returned errors or warnings in the call response. No en-US   Content-Type The MIME type of the body of the request. Must be JSON. Yes application/json  Unless one or more errors and/or warnings occur with the call, there is no response payload for this call. A successful call will return an HTTP status value of 204 No Content.  

        :param InventoryLocationFull body: Inventory Location details (required)
        :param str merchant_location_key: A unique, merchant-defined key (ID) for an inventory location. This unique identifier, or key, is used in other Inventory API calls to identify an inventory location. Max length: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'create_inventory_location', SellAccountException, True, ['sell.account', 'location'], (body, merchant_location_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """delete_inventory_location  

        This call deletes the inventory location that is specified in the merchantLocationKey path parameter. Note that deleting a location will not affect any active eBay listings associated with the deleted location, but the seller will not be able modify the offers associated with the inventory location once it is deleted.The authorization HTTP header is the only required request header for this call. Unless one or more errors and/or warnings occur with the call, there is no response payload for this call. A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in at the end of the call URI to indicate the inventory location to be deleted. Max length: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'delete_inventory_location', SellAccountException, True, ['sell.account', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_disable_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """disable_inventory_location  

        This call disables the inventory location that is specified in the merchantLocationKey path parameter. Sellers can not load/modify inventory to disabled inventory locations. Note that disabling an inventory location will not affect any active eBay listings associated with the disabled location, but the seller will not be able modify the offers associated with a disabled inventory location.The authorization HTTP header is the only required request header for this call.A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in through the call URI to disable the specified inventory location. Max length: 36 (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'disable_inventory_location', SellAccountException, True, ['sell.account', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_enable_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """enable_inventory_location  

        This call enables a disabled inventory location that is specified in the merchantLocationKey path parameter. Once a disabled inventory location is enabled, sellers can start loading/modifying inventory to that inventory location. The authorization HTTP header is the only required request header for this call.A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in through the call URI to specify the disabled inventory location to enable. Max length: 36 (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'enable_inventory_location', SellAccountException, True, ['sell.account', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """get_inventory_location  

        This call retrieves all defined details of the inventory location that is specified by the merchantLocationKey path parameter. The authorization HTTP header is the only required request header for this call. A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in at the end of the call URI to specify the inventory location to retrieve. Max length: 36 (required)
        :return: InventoryLocationResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'get_inventory_location', SellAccountException, True, ['sell.account', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_inventory_locations(self, **kwargs):  # noqa: E501
        """get_inventory_locations  

        This call retrieves all defined details for every inventory location associated with the seller's account. There are no required parameters for this call and no request payload. However, there are two optional query parameters, limit and offset. The limit query parameter sets the maximum number of inventory locations returned on one page of data, and the offset query parameter specifies the page of data to return. These query parameters are discussed more in the URI parameters table below. The authorization HTTP header is the only required request header for this call. A successful call will return an HTTP status value of 200 OK.  

        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be a positive integer value. If this query parameter is not set, up to 100 records will be returned on each page of results.  Min: 1
        :param str offset: Specifies the number of locations to skip in the result set before returning the first location in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: LocationResponse
        """
        try:
            return self._method_paged(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'get_inventory_locations', SellAccountException, True, ['sell.account', 'location'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_inventory_location(self, body, merchant_location_key, **kwargs):  # noqa: E501
        """update_inventory_location  

        Use this call to update non-physical location details for an existing inventory location. Specify the inventory location you want to update using the merchantLocationKey path parameter. You can update the following text-based fields: name, phone, locationWebUrl, locationInstructions and locationAdditionalInformation. Whatever text is passed in for these fields in an updateInventoryLocation call will replace the current text strings defined for these fields. For store inventory locations, the operating hours and/or the special hours can also be updated.  The merchant location key, the physical location of the store, and its geo-location coordinates can not be updated with an updateInventoryLocation call In addition to the authorization header, which is required for all eBay REST API calls, the following table includes another request header that is mandatory for the updateInventoryLocation call, and two other request headers that are optional:   Header Description Required? Applicable Values   Accept Describes the response encoding, as required by the caller. Currently, the interfaces require payloads formatted in JSON, and JSON is the default. No application/json   Content-Language Use this header to control the language that is used for any returned errors or warnings in the call response. No en-US   Content-Type The MIME type of the body of the request. Must be JSON. Yes application/json  Unless one or more errors and/or warnings occurs with the call, there is no response payload for this call. A successful call will return an HTTP status value of 204 No Content.  

        :param InventoryLocation body: The inventory location details to be updated (other than the address and geo co-ordinates). (required)
        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in the call URI to indicate the inventory location to be updated. Max length: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.LocationApi, sell_account.ApiClient, 'update_inventory_location', SellAccountException, True, ['sell.account', 'location'], (body, merchant_location_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payments_program_onboarding(self, marketplace_id, payments_program_type, **kwargs):  # noqa: E501
        """get_payments_program_onboarding  

        Note: This method is no longer applicable, as all seller accounts globally have been enabled for the new eBay payment and checkout flow.This method retrieves a seller's onboarding status for a payments program for a specified marketplace. The overall onboarding status of the seller and the status of each onboarding step is returned.  

        :param str marketplace_id: The eBay marketplace ID associated with the onboarding status to retrieve. (required)
        :param str payments_program_type: The type of payments program whose status is returned by the method. (required)
        :return: PaymentsProgramOnboardingResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.OnboardingApi, sell_account.ApiClient, 'get_payments_program_onboarding', SellAccountException, True, ['sell.account', 'onboarding'], (marketplace_id, payments_program_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_payment_policy(self, body, **kwargs):  # noqa: E501
        """create_payment_policy  

        This method creates a new payment policy where the policy encapsulates seller's terms for order payments.  Each policy targets a specific eBay marketplace and category group, and you can create multiple policies for each combination.  A successful request returns the getPaymentPolicy URI to the new policy in the Location response header and the ID for the new policy is returned in the response payload.  Tip: For details on creating and using the business policies supported by the Account API, see eBay business policies.  

        :param PaymentPolicyRequest body: Payment policy request (required)
        :return: SetPaymentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'create_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_payment_policy(self, payment_policy_id, **kwargs):  # noqa: E501
        """delete_payment_policy  

        This method deletes a payment policy. Supply the ID of the policy you want to delete in the paymentPolicyId path parameter.   

        :param str payment_policy_id: This path parameter specifies the ID of the payment policy you want to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'delete_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], payment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payment_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_payment_policies  

        This method retrieves all the payment policies configured for the marketplace you specify using the marketplace_id query parameter.  Marketplaces and locales Get the correct policies for a marketplace that supports multiple locales using the Content-Language request header. For example, get the policies for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers.  

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policies you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :return: PaymentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'get_payment_policies', SellAccountException, True, ['sell.account', 'payment_policy'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payment_policy(self, payment_policy_id, **kwargs):  # noqa: E501
        """get_payment_policy  

        This method retrieves the complete details of a payment policy. Supply the ID of the policy you want to retrieve using the paymentPolicyId path parameter.  

        :param str payment_policy_id: This path parameter specifies the ID of the payment policy you want to retrieve. (required)
        :return: PaymentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'get_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], payment_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payment_policy_by_name(self, marketplace_id, name, **kwargs):  # noqa: E501
        """get_payment_policy_by_name  

        This method retrieves the details of a specific payment policy. Supply both the policy name and its associated marketplace_id in the request query parameters.   Marketplaces and locales Get the correct policy for a marketplace that supports multiple locales using the Content-Language request header. For example, get a policy for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers.  

        :param str marketplace_id: This query parameter specifies the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :param str name: This query parameter specifies the seller-defined name of the payment policy you want to retrieve. (required)
        :return: PaymentPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'get_payment_policy_by_name', SellAccountException, True, ['sell.account', 'payment_policy'], (marketplace_id, name), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_payment_policy(self, body, payment_policy_id, **kwargs):  # noqa: E501
        """update_payment_policy  

        This method updates an existing payment policy. Specify the policy you want to update using the payment_policy_id path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload.  

        :param PaymentPolicyRequest body: Payment policy request (required)
        :param str payment_policy_id: This path parameter specifies the ID of the payment policy you want to update. (required)
        :return: SetPaymentPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentPolicyApi, sell_account.ApiClient, 'update_payment_policy', SellAccountException, True, ['sell.account', 'payment_policy'], (body, payment_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_payments_program(self, marketplace_id, payments_program_type, **kwargs):  # noqa: E501
        """get_payments_program  

        Note: This method is no longer applicable, as all seller accounts globally have been enabled for the new eBay payment and checkout flow.This method returns whether or not the user is opted-in to the specified payments program. Sellers opt-in to payments programs by marketplace and you use the marketplace_id path parameter to specify the marketplace of the status flag you want returned.  

        :param str marketplace_id: This path parameter specifies the eBay marketplace of the payments program for which you want to retrieve the seller's status. (required)
        :param str payments_program_type: This path parameter specifies the payments program whose status is returned by the call. (required)
        :return: PaymentsProgramResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PaymentsProgramApi, sell_account.ApiClient, 'get_payments_program', SellAccountException, True, ['sell.account', 'payments_program'], (marketplace_id, payments_program_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_privileges(self, **kwargs):  # noqa: E501
        """get_privileges  

        This method retrieves the seller's current set of privileges, including whether or not the seller's eBay registration has been completed, as well as the details of their site-wide sellingLimit (the amount and quantity they can sell on a given day).  

        :return: SellingPrivileges
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.PrivilegeApi, sell_account.ApiClient, 'get_privileges', SellAccountException, True, ['sell.account', 'privilege'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_opted_in_programs(self, **kwargs):  # noqa: E501
        """get_opted_in_programs  

        This method gets a list of the seller programs that the seller has opted-in to.  

        :return: Programs
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ProgramApi, sell_account.ApiClient, 'get_opted_in_programs', SellAccountException, True, ['sell.account', 'program'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_opt_in_to_program(self, body, **kwargs):  # noqa: E501
        """opt_in_to_program  

        This method opts the seller in to an eBay seller program. Refer to the Account API overview for information about available eBay seller programs.Note: It can take up to 24-hours for eBay to process your request to opt-in to a Seller Program. Use the getOptedInPrograms call to check the status of your request after the processing period has passed.  

        :param Program body: Program being opted-in to. (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ProgramApi, sell_account.ApiClient, 'opt_in_to_program', SellAccountException, True, ['sell.account', 'program'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_opt_out_of_program(self, body, **kwargs):  # noqa: E501
        """opt_out_of_program  

        This method opts the seller out of a seller program to which you have previously opted-in to. Get a list of the seller programs you have opted-in to using the getOptedInPrograms call.  

        :param Program body: Program being opted-out of. (required)
        :return: object
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ProgramApi, sell_account.ApiClient, 'opt_out_of_program', SellAccountException, True, ['sell.account', 'program'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_rate_tables(self, **kwargs):  # noqa: E501
        """get_rate_tables  

        This method retrieves a seller's shipping rate tables for the country specified in the country_code query parameter. If you call this method without specifying a country code, the call returns all of the seller's shipping rate tables.  The method's response includes a rateTableId for each table defined by the seller. This rateTableId value is used in add/revise item call or in create/update fulfillment business policy call to specify the shipping rate table to use for that policy's domestic or international shipping options. This call currently supports getting rate tables related to the following marketplaces:EBAY_AU EBAY_CA EBAY_DE EBAY_ES EBAY_FR EBAY_GB EBAY_IT EBAY_US Note: Rate tables created with the Trading API might not have been assigned a rateTableId at the time of their creation. This method can assign and return rateTableId values for rate tables with missing IDs if you make a request using the country_code where the seller has defined rate tables. Sellers can define up to 40 shipping rate tables for their account, which lets them set up different rate tables for each of the marketplaces they sell into. Go to Shipping rate tables in  My eBay to create and update rate tables.  

        :param str country_code: This query parameter specifies the two-letter ISO 3166 code of country for which you want shipping rate table information. If you do not specify a country code, the request returns all of the seller's defined shipping rate tables for all eBay marketplaces. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:CountryCodeEnum
        :return: RateTableResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.RateTableApi, sell_account.ApiClient, 'get_rate_tables', SellAccountException, True, ['sell.account', 'rate_table'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_return_policy(self, body, **kwargs):  # noqa: E501
        """create_return_policy  

        This method creates a new return policy where the policy encapsulates seller's terms for returning items.  Each policy targets a specific marketplace, and you can create multiple policies for each marketplace. Return policies are not applicable to motor-vehicle listings.A successful request returns the getReturnPolicy URI to the new policy in the Location response header and the ID for the new policy is returned in the response payload.  Tip: For details on creating and using the business policies supported by the Account API, see eBay business policies.  

        :param ReturnPolicyRequest body: Return policy request (required)
        :return: SetReturnPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'create_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_return_policy(self, return_policy_id, **kwargs):  # noqa: E501
        """delete_return_policy  

        This method deletes a return policy. Supply the ID of the policy you want to delete in the returnPolicyId path parameter.  

        :param str return_policy_id: This path parameter specifies the ID of the return policy you want to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'delete_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], return_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_return_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_return_policies  

        This method retrieves all the return policies configured for the marketplace you specify using the marketplace_id query parameter.  Marketplaces and locales Get the correct policies for a marketplace that supports multiple locales using the Content-Language request header. For example, get the policies for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers.  

        :param str marketplace_id: This query parameter specifies the ID of the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :return: ReturnPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'get_return_policies', SellAccountException, True, ['sell.account', 'return_policy'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_return_policy(self, return_policy_id, **kwargs):  # noqa: E501
        """get_return_policy  

        This method retrieves the complete details of the return policy specified by the returnPolicyId path parameter.  

        :param str return_policy_id: This path parameter specifies the of the return policy you want to retrieve. (required)
        :return: ReturnPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'get_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], return_policy_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_return_policy_by_name(self, marketplace_id, name, **kwargs):  # noqa: E501
        """get_return_policy_by_name  

        This method retrieves the details of a specific return policy. Supply both the policy name and its associated marketplace_id in the request query parameters.   Marketplaces and locales Get the correct policy for a marketplace that supports multiple locales using the Content-Language request header. For example, get a policy for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers.  

        :param str marketplace_id: This query parameter specifies the ID of the eBay marketplace of the policy you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:MarketplaceIdEnum (required)
        :param str name: This query parameter specifies the seller-defined name of the return policy you want to retrieve. (required)
        :return: ReturnPolicy
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'get_return_policy_by_name', SellAccountException, True, ['sell.account', 'return_policy'], (marketplace_id, name), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_update_return_policy(self, body, return_policy_id, **kwargs):  # noqa: E501
        """update_return_policy  

        This method updates an existing return policy. Specify the policy you want to update using the return_policy_id path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload.  

        :param ReturnPolicyRequest body: Container for a return policy request. (required)
        :param str return_policy_id: This path parameter specifies the ID of the return policy you want to update. (required)
        :return: SetReturnPolicyResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.ReturnPolicyApi, sell_account.ApiClient, 'update_return_policy', SellAccountException, True, ['sell.account', 'return_policy'], (body, return_policy_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_create_or_replace_sales_tax(self, body, country_code, jurisdiction_id, **kwargs):  # noqa: E501
        """create_or_replace_sales_tax  

        This method creates or updates a sales tax table entry for a jurisdiction. Specify the tax table entry you want to configure using the two path parameters: countryCode and jurisdictionId.  A tax table entry for a jurisdiction is comprised of two fields: one for the jurisdiction's sales-tax rate and another that's a boolean value indicating whether or not shipping and handling are taxed in the jurisdiction.  You can set up tax tables for countries that support different tax jurisdictions. Currently, only Canada, India, and the US support separate tax jurisdictions. If you sell into any of these countries, you can set up tax tables for any of the country's jurisdictions. Retrieve valid jurisdiction IDs using getSalesTaxJurisdictions in the Metadata API.  For details on using this call, see Establishing sales-tax tables. Important! In the US, eBay now 'collects and remits' sales tax for every US state except for Missouri (and a few US territories), so sellers can no longer configure sales tax rates for any states except Missouri. With eBay 'collect and remit', eBay calculates the sales tax, collects the sales tax from the buyer, and remits the sales tax to the tax authorities at the buyer's location.  

        :param SalesTaxBase body: A container that describes the how the sales tax is calculated. (required)
        :param str country_code: This path parameter specifies the two-letter ISO 3166 code for the country for which you want to create a sales tax table entry. (required)
        :param str jurisdiction_id: This path parameter specifies the ID of the tax jurisdiction for the table entry you want to create. Retrieve valid jurisdiction IDs using getSalesTaxJurisdictions in the Metadata API. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'create_or_replace_sales_tax', SellAccountException, True, ['sell.account', 'sales_tax'], (body, country_code, jurisdiction_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_delete_sales_tax(self, country_code, jurisdiction_id, **kwargs):  # noqa: E501
        """delete_sales_tax  

        This call deletes a sales tax table entry for a jurisdiction. Specify the jurisdiction to delete using the countryCode and jurisdictionId path parameters.  

        :param str country_code: This path parameter specifies the two-letter ISO 3166 code for the country whose sales tax table entry you want to delete. (required)
        :param str jurisdiction_id: This path parameter specifies the ID of the sales tax jurisdiction whose table entry you want to delete. Retrieve valid jurisdiction IDs using getSalesTaxJurisdictions in the Metadata API. (required)
        :return: None
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'delete_sales_tax', SellAccountException, True, ['sell.account', 'sales_tax'], (country_code, jurisdiction_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_sales_tax(self, country_code, jurisdiction_id, **kwargs):  # noqa: E501
        """get_sales_tax  

        This call gets the current sales tax table entry for a specific tax jurisdiction. Specify the jurisdiction to retrieve using the countryCode and jurisdictionId path parameters. All four response fields will be returned if a sales tax entry exists for the tax jurisdiction. Otherwise, the response will be returned as empty.Important! In most US states and territories, eBay now 'collects and remits' sales tax, so sellers can no longer configure sales tax rates for these states/territories.  

        :param str country_code: This path parameter specifies the two-letter ISO 3166 code for the country whose sales tax table you want to retrieve. (required)
        :param str jurisdiction_id: This path parameter specifies the ID of the sales tax jurisdiction for the tax table entry you want to retrieve. Retrieve valid jurisdiction IDs using getSalesTaxJurisdictions in the Metadata API. (required)
        :return: SalesTax
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'get_sales_tax', SellAccountException, True, ['sell.account', 'sales_tax'], (country_code, jurisdiction_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_sales_taxes(self, country_code, **kwargs):  # noqa: E501
        """get_sales_taxes  

        Use this call to retrieve all sales tax table entries that the seller has defined for a specific country. All four response fields will be returned for each tax jurisdiction that matches the search criteria. Important! In most US states and territories, eBay now 'collects and remits' sales tax, so sellers can no longer configure sales tax rates for these states/territories.  

        :param str country_code: This path parameter specifies the two-letter ISO 3166 code for the country whose tax table you want to retrieve. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/account/types/ba:CountryCodeEnum (required)
        :return: SalesTaxes
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SalesTaxApi, sell_account.ApiClient, 'get_sales_taxes', SellAccountException, True, ['sell.account', 'sales_tax'], country_code, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_account_get_subscription(self, **kwargs):  # noqa: E501
        """get_subscription  

        This method retrieves a list of subscriptions associated with the seller account.  

        :param str limit: This field is for future use.
        :param str continuation_token: This field is for future use.
        :return: SubscriptionResponse
        """
        try:
            return self._method_single(sell_account.Configuration, '/sell/account/v1', sell_account.SubscriptionApi, sell_account.ApiClient, 'get_subscription', SellAccountException, True, ['sell.account', 'subscription'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_get_customer_service_metric(self, customer_service_metric_type, evaluation_marketplace_id, evaluation_type, **kwargs):  # noqa: E501
        """get_customer_service_metric  

        Use this method to retrieve a seller's performance and rating for the customer service metric. Control the response from the getCustomerServiceMetric method using the following path and query parameters: customer_service_metric_type controls the type of customer service transactions evaluated for the metric rating. evaluation_type controls the period you want to review. evaluation_marketplace_id specifies the target marketplace for the evaluation. Currently, metric data is returned for only peer benchmarking. For more detail on the workings of peer benchmarking, see Service metrics policy.  

        :param str customer_service_metric_type: Use this path parameter to specify the type of customer service metrics and benchmark data you want returned for the seller. Supported types are: ITEM_NOT_AS_DESCRIBED ITEM_NOT_RECEIVED (required)
        :param str evaluation_marketplace_id: Use this query parameter to specify the Marketplace ID to evaluate for the customer service metrics and benchmark data. For the list of supported marketplaces, see Analytics API requirements and restrictions. For implementation help, refer to eBay API documentation at https://developer.ebay.com/devzone/rest/api-ref/analytics/types/MarketplaceIdEnum.html (required)
        :param str evaluation_type: Use this path parameter to specify the type of the seller evaluation you want returned, either: CURRENT – A monthly evaluation that occurs on the 20th of every month. PROJECTED – A daily evaluation that provides a projection of how the seller is currently performing with regards to the upcoming evaluation period. (required)
        :return: GetCustomerServiceMetricResponse
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.CustomerServiceMetricApi, sell_analytics.ApiClient, 'get_customer_service_metric', SellAnalyticsException, True, ['sell.analytics', 'customer_service_metric'], (customer_service_metric_type, evaluation_marketplace_id, evaluation_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_find_seller_standards_profiles(self, **kwargs):  # noqa: E501
        """find_seller_standards_profiles  

        This call retrieves all the standards profiles for the associated seller. A standards profile is a set of eBay seller metrics and the seller's associated compliance values (either TOP_RATED, ABOVE_STANDARD, or BELOW_STANDARD). A seller's multiple profiles are distinguished by two criteria, a "program" and a "cycle." A profile's program is one of three regions where the seller may have done business, or PROGRAM_GLOBAL to indicate all marketplaces where the seller has done business. The cycle value specifies whether the standards compliance values were determined at the last official eBay evaluation or at the time of the request.  

        :return: FindSellerStandardsProfilesResponse
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.SellerStandardsProfileApi, sell_analytics.ApiClient, 'find_seller_standards_profiles', SellAnalyticsException, True, ['sell.analytics', 'seller_standards_profile'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_get_seller_standards_profile(self, cycle, program, **kwargs):  # noqa: E501
        """get_seller_standards_profile  

        This call retrieves a single standards profile for the associated seller. A standards profile is a set of eBay seller metrics and the seller's associated compliance values (either TOP_RATED, ABOVE_STANDARD, or BELOW_STANDARD). A seller can have multiple profiles distinguished by two criteria, a "program" and a "cycle." A profile's program is one of three regions where the seller may have done business, or PROGRAM_GLOBAL to indicate all marketplaces where the seller has done business. The cycle value specifies whether the standards compliance values were determined at the last official eBay evaluation (CURRENT) or at the time of the request (PROJECTED). Both cycle and a program values are required URI parameters for this method.  

        :param str cycle: The period covered by the returned standards profile evaluation. Supply one of two values, CURRENT means the response reflects eBay's most recent monthly standards evaluation and PROJECTED means the response reflect the seller's projected monthly evaluation, as calculated at the time of the request. (required)
        :param str program: This input value specifies the region used to determine the seller's standards profile. Supply one of the four following values, PROGRAM_DE, PROGRAM_UK, PROGRAM_US, or PROGRAM_GLOBAL. (required)
        :return: StandardsProfile
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.SellerStandardsProfileApi, sell_analytics.ApiClient, 'get_seller_standards_profile', SellAnalyticsException, True, ['sell.analytics', 'seller_standards_profile'], (cycle, program), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_analytics_get_traffic_report(self, **kwargs):  # noqa: E501
        """get_traffic_report  

        This method returns a report that details the user traffic received by a seller's listings. A traffic report gives sellers the ability to review how often their listings appeared on eBay, how many times their listings are viewed, and how many purchases were made. The report also returns the report's start and end dates, and the date the information was last updated. When using this call: Be sure to URL-encode the values you pass in query parameters, as described in URI parameters. See the request samples below for details. You can only specify a single metric in the sort parameter and the specified metric must be listed in the metric parameter of your request. Parameter names are case sensitive, but metric names are not. For example, the following are correct: sort=LISTING_IMPRESSION_TOTAL sort=listing_impression_total metric=listing_impression_total However, these are incorrect: SORT=LISTING_IMPRESSION_TOTAL SORT=listing_impression_total Metric=listing_impression_total For more information, see Traffic report details.  

        :param str dimension: This query parameter specifies the dimension, or "attribute," that is applied to the report metric. Valid values: DAY or LISTING Examples If you specify dimension=DAY and metric=CLICK_THROUGH_RATE, the traffic report contains the number of times an item displayed on a search results page and the buyer clicked through to the View Item page for each day in the date range, as in: 12-06-17: 32, 12-07-17: 54, ... If you specify dimension=LISTING and metric=LISTING_IMPRESSION_STORE, the traffic report contains the number of times that listing appeared on the seller's store during the specified date range. For example, LISTING_IMPRESSION_STORE: 157 means the item appeared 157 times in the store during the date range.
        :param str filter: This query parameter refines the information returned in the traffic report. Configure the following properties of the filter parameter to tune the traffic report to your needs: date_range Limits the report to the specified range of dates. Format the date range by enclosing the earliest date and end date for the report in brackets ("[ ]"), as follows: [YYYYMMDD..YYYYMMDD] The maximum range between the start and end dates is 90 days, and the earliest start date you can specify is two years prior to the current date, which is defined as 730 days (365 * 2), not accounting for Leap Year. The last date for which traffic data exists is a value called lastUpdatedDate. eBay returns an error if you specify a date range greater than 90 days, or the start date is after the lastUpdatedDate. If the specified end date is beyond the lastUpdatedDate, eBay returns data up to the lastUpdatedDate. Required: Always listing_ids This filter limits the results to only the supplied list of listingId values. You can specify to 200 different listingId values. Enclose the list of IDs with curly braces ("{ }"), and separate multiple values with a pipe character ("|"). This filter only returns data for listings that have been either active or sold in last 90 days, and any unsold listings in the last 30 days. All listings must be the seller's and they must be listed on the marketplace specified by the marketplace_ids filter argument. marketplace_ids This filter limits the report to seller data related to only the specified marketplace ID (currently the filter allows only a single marketplace ID). Enclose the marketplace ID in curly braces ("{ }"). Valid values: EBAY_AU EBAY_DE EBAY_GB EBAY_US EBAY_MOTORS_US Required if you set the dimension parameter to DAY. traffic_source Limits the report to either Promoted Listings items or non-Promoted Listings (organic) items. Valid values are ORGANIC and PROMOTED_LISTINGS. Enclose the list of values with curly braces ("{ }"), and separate multiple values with a pipe character ("|") The default is both values. Example filter parameter The following example shows how to configure the filter parameter with the marketplace_ids and date_range filters: filter=marketplace_ids:{EBAY_US},date_range:[20170601..20170828] Note: You must URL encode all the values you supply in the filter parameter, as described in URL parameters. For implementation help, refer to eBay API documentation at https://developer.ebay.com/devzone/rest/api-ref/analytics/types/FilterField.html
        :param str metric: This query parameter specifies the metrics you want covered in the report. Specify a comma-separated list of the metrics you want included in the report. Valid values: CLICK_THROUGH_RATE The number of times an item displays on the search results page divided by the number of times buyers clicked through to its View Item page. Localized name: Click through rate LISTING_IMPRESSION_SEARCH_RESULTS_PAGE The number of times the seller's listings displayed on the search results page. Note, the listing might not have been visible to the buyer due to its position on the page. Localized name: Listing impressions from the search results page LISTING_IMPRESSION_STORE The number of times the seller's listings displayed on the seller's store. Note, the listing might not have been visible to the buyer due to its position on the page. Localized name: Listing impressions from your Store LISTING_IMPRESSION_TOTAL The total number of times the seller's listings displayed on the search results page OR in the seller's store. The item is counted each time it displays on either page. However, the listing might not have been visible to the buyer due to its position on the page. This is a combination of: LISTING_IMPRESSION_SEARCH_RESULTS_PAGE + LISTING_IMPRESSION_STORE. Localized name: Total listing impressions LISTING_VIEWS_SOURCE_DIRECT The number of times a View Item page was directly accessed, such as when a buyer navigates to the page using a bookmark. Localized name: Direct views LISTING_VIEWS_SOURCE_OFF_EBAY The number of times a View Item page was accessed via a site other than eBay, such as when a buyer clicks on a link to the listing from a search engine page. Localized name: Off eBay views LISTING_VIEWS_SOURCE_OTHER_EBAY The number of times a View Item page was accessed from an eBay page that is not either the search results page or the seller's store. Localized name: Views from non-search and non-store pages within eBay LISTING_VIEWS_SOURCE_SEARCH_RESULTS_PAGE The number of times the item displayed on the search results page. Localized name: Views on the search results page LISTING_VIEWS_SOURCE_STORE The number of times a View Item page was accessed via the seller's store. Localized name: Views from your Store LISTING_VIEWS_TOTAL Total number of listings viewed. This number sums: LISTING_VIEWS_SOURCE_DIRECT LISTING_VIEWS_SOURCE_OFF_EBAY LISTING_VIEWS_SOURCE_OTHER_EBAY LISTING_VIEWS_SOURCE_SEARCH_RESULTS_PAGE LISTING_VIEWS_SOURCE_STORE. Localized name: Total views SALES_CONVERSION_RATE The number of completed transactions divided by the number of View Item page views. Equals: TRANSACTION / LISTING_VIEWS_TOTAL Localized name: Sales conversion rate TRANSACTION The total number of completed transactions. Localized name: Transaction count
        :param str sort: This query parameter sorts the report on the specified metric. The metric you specify must be included in the configuration of the report's metric parameter. Sorting is helpful when you want to review how a specific metric is performing, such as the CLICK_THROUGH_RATE. Reports can be sorted in ascending or descending order. Precede the value of a descending-order request with a minus sign ("-"), for example: sort=-CLICK_THROUGH_RATE. For implementation help, refer to eBay API documentation at https://developer.ebay.com/devzone/rest/api-ref/analytics/types/SortField.html
        :return: Report
        """
        try:
            return self._method_single(sell_analytics.Configuration, '/sell/analytics/v1', sell_analytics.TrafficReportApi, sell_analytics.ApiClient, 'get_traffic_report', SellAnalyticsException, True, ['sell.analytics', 'traffic_report'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_compliance_get_listing_violations(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """get_listing_violations  

        This call returns specific listing violations for the supported listing compliance types. Only one compliance type can be passed in per call, and the response will include all the listing violations for this compliance type, and listing violations are grouped together by eBay listing ID. See ComplianceTypeEnum for more information on the supported listing compliance types. This method also has pagination control. Note: A maximum of 2000 listing violations will be returned in a result set. If the seller has more than 2000 listing violations, some/all of those listing violations must be corrected before additional listing violations will be retrieved. The user should pay attention to the total value in the response. If this value is '2000', it is possible that the seller has more than 2000 listing violations, but this field maxes out at 2000. Note: In a future release of this API, the seller will be able to pass in a specific eBay listing ID as a query parameter to see if this specific listing has any violations. Note: Only mocked non-compliant listing data will be returned for this call in the Sandbox environment, and not specific to the seller. However, the user can still use this mock data to experiment with the compliance type filters and pagination control.  

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
        """suppress_violation  

        This call suppresses a listing violation for a specific listing. Only listing violations in the AT_RISK state (returned in the violations.complianceState field of the getListingViolations call) can be suppressed. Note: At this time, the suppressViolation call only supports the suppressing of ASPECTS_ADOPTION listing violations in the AT_RISK state. In the future, it is possible that this method can be used to suppress other listing violation types. A successful call returns a http status code of 204 Success. There is no response payload. If the call is not successful, an error code will be returned stating the issue.  

        :param SuppressViolationRequest body: This type is the base request type of the SuppressViolation method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_compliance.Configuration, '/sell/compliance/v1', sell_compliance.ListingViolationApi, sell_compliance.ApiClient, 'suppress_violation', SellComplianceException, True, ['sell.compliance', 'listing_violation'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_compliance_get_listing_violations_summary(self, **kwargs):  # noqa: E501
        """get_listing_violations_summary  

        This call returns listing violation counts for a seller. A user can pass in one or more compliance types through the compliance_type query parameter. See ComplianceTypeEnum for more information on the supported listing compliance types. Listing violations are returned for multiple marketplaces if the seller sells on multiple eBay marketplaces. Note: Only a canned response, with counts for all listing compliance types, is returned in the Sandbox environment. Due to this limitation, the compliance_type query parameter (if used) will not have an effect on the response.  

        :param str x_ebay_c_marketplace_id: Use this header to specify the eBay marketplace identifier. Supported values for this header can be found in the MarketplaceIdEnum type definition. Note that Version 1.4.0 of the Compliance API is only supported on the US, UK, Australia, Canada {English), and Germany sites.
        :param str compliance_type: A user passes in one or more compliance type values through this query parameter. See ComplianceTypeEnum for more information on the supported compliance types that can be passed in here. If more than one compliance type value is used, delimit these values with a comma. If no compliance type values are passed in, the listing count for all compliance types will be returned. Note: Only a canned response, with counts for all listing compliance types, is returned in the Sandbox environment. Due to this limitation, the compliance_type query parameter (if used) will not have an effect on the response.
        :return: ComplianceSummary
        """
        try:
            return self._method_single(sell_compliance.Configuration, '/sell/compliance/v1', sell_compliance.ListingViolationSummaryApi, sell_compliance.ApiClient, 'get_listing_violations_summary', SellComplianceException, True, ['sell.compliance', 'listing_violation_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_customer_service_metric_task(self, body, accept_language, **kwargs):  # noqa: E501
        """create_customer_service_metric_task  

        Use this method to create a customer service metrics download task with filter criteria for the customer service metrics report. When using this method, specify the feedType and filterCriteria including both evaluationMarketplaceId and customerServiceMetricType for the report. The method returns the location response header containing the call URI to use with getCustomerServiceMetricTask to retrieve status and details on the task.Only CURRENT Customer Service Metrics reports can be generated with the Sell Feed API. PROJECTED reports are not supported at this time. See the getCustomerServiceMetric method document in the Analytics API for more information about these two types of reports.Note: Before calling this API, retrieve the summary of the seller's performance and rating for the customer service metric by calling getCustomerServiceMetric (part of the Analytics API). You can then populate the create task request fields with the values from the response. This technique eliminates failed tasks that request a report for a customerServiceMetricType and evaluationMarketplaceId that are without evaluation.  

        :param CreateServiceMetricsTaskRequest body: Request payload containing version, feedType, and optional filterCriteria. (required)
        :param str accept_language: Use this header to specify the natural language in which the authenticated user desires the response. (required)
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.CustomerServiceMetricTaskApi, sell_feed.ApiClient, 'create_customer_service_metric_task', SellFeedException, True, ['sell.feed', 'customer_service_metric_task'], (body, accept_language), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_customer_service_metric_task(self, task_id, **kwargs):  # noqa: E501
        """get_customer_service_metric_task  

        Use this method to retrieve customer service metric task details for the specified task. The input is task_id.  

        :param str task_id: Use this path parameter to specify the task ID value for the customer service metric task to retrieve. (required)
        :return: ServiceMetricsTask
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.CustomerServiceMetricTaskApi, sell_feed.ApiClient, 'get_customer_service_metric_task', SellFeedException, True, ['sell.feed', 'customer_service_metric_task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_customer_service_metric_tasks(self, **kwargs):  # noqa: E501
        """get_customer_service_metric_tasks  

        Use this method to return an array of customer service metric tasks. You can limit the tasks returned by specifying a date range.   Note: You can pass in either the look_back_days or date_range, but not both.  

        :param str date_range: The task creation date range. The results are filtered to include only tasks with a creation date that is equal to the dates specified or is within the specified range. Do not use with the look_back_days parameter.Format: UTCFor example, tasks within a range: yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ Tasks created on March 8, 20202020-03-08T00:00.00.000Z..2020-03-09T00:00:00.000ZMaximum: 90 days
        :param str feed_type: The feed type associated with the task. The only presently supported value is CUSTOMER_SERVICE_METRICS_REPORT.
        :param str limit: The number of customer service metric tasks to return per page of the result set. Use this parameter in conjunction with the offset parameter to control the pagination of the output. For example, if offset is set to 10 and limit is set to 10, the call retrieves tasks 11 thru 20 from the result set.If this parameter is omitted, the default value is used. Note:This feature employs a zero-based list, where the first item in the list has an offset of 0.Default: 10 Maximum: 500
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used. Default value: 7Range: 1-90 (inclusive)
        :param str offset: The number of customer service metric tasks to skip in the result set before returning the first task in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: CustomerServiceMetricTaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.CustomerServiceMetricTaskApi, sell_feed.ApiClient, 'get_customer_service_metric_tasks', SellFeedException, True, ['sell.feed', 'customer_service_metric_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_inventory_task(self, body, **kwargs):  # noqa: E501
        """create_inventory_task  

        This method creates an inventory-related download task for a specified feed type with optional filter criteria. When using this method, specify the feedType. This method returns the location response header containing the getInventoryTask call URI to retrieve the inventory task you just created. The URL includes the eBay-assigned task ID, which you can use to reference the inventory task.To retrieve the status of the task, use the getInventoryTask method to retrieve a single task ID or the getInventoryTasks method to retrieve multiple task IDs. Note: The scope depends on the feed type. An error message results when an unsupported scope or feed type is specified.Presently, this method supports Active Inventory Report. The ActiveInventoryReport returns a report that contains price and quantity information for all of the active listings for a specific seller. A seller can use this information to maintain their inventory on eBay.  

        :param CreateInventoryTaskRequest body: The request payload containing the version, feedType, and optional filterCriteria. (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted.  Note: This value is case sensitive.For example:X-EBAY-C-MARKETPLACE-ID:EBAY_USThis identifies the eBay marketplace that applies to this task. See MarketplaceIdEnum.
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.InventoryTaskApi, sell_feed.ApiClient, 'create_inventory_task', SellFeedException, True, ['sell.feed', 'inventory_task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_inventory_task(self, task_id, **kwargs):  # noqa: E501
        """get_inventory_task  

        This method retrieves the task details and status of the specified inventory-related task. The input is task_id.  

        :param str task_id: The ID of the task. This ID was generated when the task was created by the createInventoryTask method (required)
        :return: InventoryTask
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.InventoryTaskApi, sell_feed.ApiClient, 'get_inventory_task', SellFeedException, True, ['sell.feed', 'inventory_task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_inventory_tasks(self, **kwargs):  # noqa: E501
        """get_inventory_tasks  

        This method searches for multiple tasks of a specific feed type, and includes date filters and pagination.  

        :param str feed_type: The feed type associated with the inventory task. Either feed_type or schedule_id is required. Do not use with the schedule_id parameter. Presently, only one feed type is available:LMS_ACTIVE_INVENTORY_REPORT
        :param str schedule_id: The ID of the schedule for which to retrieve the latest result file. This ID is generated when the schedule was created by the createSchedule method. Schedules apply to downloaded reports (LMS_ACTIVE_INVENTORY_REPORT). Either schedule_id or feed_type is  required. Do not use with the feed_type parameter.
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used.  Default:  7 Range:  1-90 (inclusive)
        :param str date_range: Specifies the range of task creation dates used to filter the results. The results are filtered to include only tasks with a creation date that is equal to this date or is within specified range.  Note: Maximum date range window size is 90 days.Valid Format (UTC): yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZFor example: Tasks created on March 31, 2021 2021-03-31T00:00:00.000Z..2021-03-31T00:00:00.000Z
        :param str limit: The maximum number of tasks that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.For example, if offset is set to 10 and limit is set to 10, the call retrieves tasks 11 thru 20 from the result set.If this parameter is omitted, the default value is used. Default:  10 Maximum: 500
        :param str offset: The number of tasks to skip in the result set before returning the first task in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :return: InventoryTaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.InventoryTaskApi, sell_feed.ApiClient, 'get_inventory_tasks', SellFeedException, True, ['sell.feed', 'inventory_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_order_task(self, body, **kwargs):  # noqa: E501
        """create_order_task  

        This method creates an order download task with filter criteria for the order report. When using this method, specify the  feedType,  schemaVersion, and  filterCriteria for the report. The method returns the  location response header containing the getOrderTask call URI to retrieve the order task you just created. The URL includes the eBay-assigned task ID, which you can use to reference the order task. To retrieve the status of the task, use the  getOrderTask method to retrieve a single task ID or the getOrderTasks method to retrieve multiple order task IDs. Note: The scope depends on the feed type. An error message results when an unsupported scope or feed type is specified.The following list contains this method's authorization scope and its corresponding feed type:https://api.ebay.com/oauth/api_scope/sell.fulfillment: LMS_ORDER_REPORT For details about how this method is used, see General feed types in the Selling Integration Guide.  Note: At this time, the createOrderTask method only supports order creation date filters and not modified order date filters. Do not include the modifiedDateRange filter in your request payload.  

        :param CreateOrderTaskRequest body: description not needed (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted.  Note: This value is case sensitive.For example:X-EBAY-C-MARKETPLACE-ID:EBAY_USThis identifies the eBay marketplace that applies to this task. See MarketplaceIdEnum.
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.OrderTaskApi, sell_feed.ApiClient, 'create_order_task', SellFeedException, True, ['sell.feed', 'order_task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_order_task(self, task_id, **kwargs):  # noqa: E501
        """get_order_task  

        This method retrieves the task details and status of the specified task. The input is task_id. For details about how this method is used, see Working with Order Feeds in the Selling Integration Guide.    

        :param str task_id: The ID of the task. This ID is generated when the task was created by the  createOrderTask method. (required)
        :return: OrderTask
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.OrderTaskApi, sell_feed.ApiClient, 'get_order_task', SellFeedException, True, ['sell.feed', 'order_task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_order_tasks(self, **kwargs):  # noqa: E501
        """get_order_tasks  

        This method returns the details and status for an array of order tasks based on a specified feed_type or schedule_id. Specifying both feed_type and schedule_id results in an error. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.If specifying the feed_type, limit which order tasks are returned by specifying filters such as the creation date range or period of time using look_back_days. If specifying a schedule_id, the schedule template (that the schedule_id is based on) determines which order tasks are returned (see schedule_id for additional information). Each schedule_id applies to one feed_type.  

        :param str date_range: The order tasks creation date range. This range is used to filter the results. The filtered results are filtered to include only tasks with a creation date that is equal to this date or is within specified range. Only orders less than 90 days old can be retrieved. Do not use with the look_back_days parameter. Format: UTC     For example:  Tasks within a range   yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ   Tasks created on September 8, 2019 2019-09-08T00:00:00.000Z..2019-09-09T00:00:00.000Z
        :param str feed_type: The feed type associated with the task. The only presently supported value is LMS_ORDER_REPORT. Do not use with the schedule_id parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :param str limit: The maximum number of order tasks that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.For example, if offset is set to 10 and limit is set to 10, the call retrieves order tasks 11 thru 20 from the result set.If this parameter is omitted, the default value is used.Default: 10 Maximum: 500
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used.  Default:  7 Range:  1-90 (inclusive)  
        :param str offset: The number of order tasks to skip in the result set before returning the first order in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned.Default: 0
        :param str schedule_id: The schedule ID associated with the order task. A schedule periodically generates a report for the feed type specified by the schedule template (see scheduleTemplateId in createSchedule). Do not use with the feed_type parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :return: OrderTaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.OrderTaskApi, sell_feed.ApiClient, 'get_order_tasks', SellFeedException, True, ['sell.feed', 'order_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_schedule(self, body, **kwargs):  # noqa: E501
        """create_schedule  

        This method creates a schedule, which is a subscription to the specified schedule template. A schedule periodically generates a report for the feedType specified by the template. Specify the same feedType as the feedType of the associated schedule template. When creating the schedule, if available from the template, you can specify a preferred trigger hour, day of the week, or day of the month. These and other fields are conditionally available as specified by the template. Note: Make sure to include all fields required by the schedule template (scheduleTemplateId). Call the getScheduleTemplate method (or the getScheduleTemplates method), to find out which fields are required or optional. If a field is optional and a default value is provided by the template, the default value will be used if omitted from the payload.A successful call returns the location response header containing the getSchedule call URI to retrieve the schedule you just created. The URL includes the eBay-assigned schedule ID, which you can use to reference the schedule task. To retrieve the details of the create schedule task, use the getSchedule method for a single schedule ID or the getSchedules method to retrieve all schedule details for the specified feed_type. The number of schedules for each feedType is limited. Error code 160031 is returned when you have reached this maximum. Note: Except for schedules with a HALF-HOUR frequency, all schedules will ideally run at the start of each hour ('00' minutes). Actual start time may vary time may vary due to load and other factors.  

        :param CreateUserScheduleRequest body: In the request payload: feedType and scheduleTemplateId are required; scheduleName is optional; preferredTriggerHour, preferredTriggerDayOfWeek, preferredTriggerDayOfMonth, scheduleStartDate, scheduleEndDate, and schemaVersion are conditional. (required)
        :return: object
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'create_schedule', SellFeedException, True, ['sell.feed', 'schedule'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_delete_schedule(self, schedule_id, **kwargs):  # noqa: E501
        """delete_schedule  

        This method deletes an existing schedule. Specify the schedule to delete using the schedule_id path parameter.  

        :param str schedule_id: The schedule_id of the schedule to delete. This ID was generated when the task was created. If you do not know the schedule_id, use the getSchedules method to return all schedules based on a specified feed_type and find the schedule_id of the schedule to delete. (required)
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'delete_schedule', SellFeedException, True, ['sell.feed', 'schedule'], schedule_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_latest_result_file(self, schedule_id, **kwargs):  # noqa: E501
        """get_latest_result_file  

        This method downloads the latest result file generated by the schedule. The response of this call is a compressed or uncompressed CSV, XML, or JSON file, with the applicable file extension (for example: csv.gz). Specify the schedule_id path parameter to download its last generated file.  

        :param str schedule_id: The ID of the schedule for which to retrieve the latest result file. This ID is generated when the schedule was created by the createSchedule method. (required)
        :return: StreamingOutput
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_latest_result_file', SellFeedException, True, ['sell.feed', 'schedule'], schedule_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedule(self, schedule_id, **kwargs):  # noqa: E501
        """get_schedule  

        This method retrieves schedule details and status of the specified schedule. Specify the schedule to retrieve using the schedule_id. Use the getSchedules method to find a schedule if you do not know the schedule_id.  

        :param str schedule_id: The ID of the schedule for which to retrieve the details. This ID is generated when the schedule was created by the createSchedule method. (required)
        :return: UserScheduleResponse
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedule', SellFeedException, True, ['sell.feed', 'schedule'], schedule_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedule_template(self, schedule_template_id, **kwargs):  # noqa: E501
        """get_schedule_template  

        This method retrieves the details of the specified template. Specify the template to retrieve using the schedule_template_id path parameter. Use the getScheduleTemplates method to find a schedule template if you do not know the schedule_template_id.  

        :param str schedule_template_id: The ID of the template to retrieve. If you do not know the schedule_template_id, refer to the documentation or use the getScheduleTemplates method to find the available schedule templates. (required)
        :return: ScheduleTemplateResponse
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedule_template', SellFeedException, True, ['sell.feed', 'schedule'], schedule_template_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedule_templates(self, feed_type, **kwargs):  # noqa: E501
        """get_schedule_templates  

        This method retrieves an array containing the details and status of all schedule templates based on the specified feed_type. Use this method to find a schedule template if you do not know the schedule_template_id.  

        :param str feed_type: The feed type of the schedule templates to retrieve. (required)
        :param str limit: The maximum number of schedule templates that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.For example, if offset is set to 10 and limit is set to 10, the call retrieves schedule templates 11 thru 20 from the result set.If this parameter is omitted, the default value is used. Default:  10 Maximum: 500
        :param str offset: The number of schedule templates to skip in the result set before returning the first template in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned.Default: 0
        :return: ScheduleTemplateCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedule_templates', SellFeedException, True, ['sell.feed', 'schedule'], feed_type, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_schedules(self, feed_type, **kwargs):  # noqa: E501
        """get_schedules  

        This method retrieves an array containing the details and status of all schedules based on the specified feed_type. Use this method to find a schedule if you do not know the schedule_id.  

        :param str feed_type: The feedType associated with the schedule. (required)
        :param str limit: The maximum number of schedules that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.For example, if offset is set to 10 and limit is set to 10, the call retrieves schedules 11 thru 20 from the result set.If this parameter is omitted, the default value is used. Default:  10 Maximum: 500
        :param str offset: The number of schedules to skip in the result set before returning the first schedule in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned.Default: 0
        :return: UserScheduleCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'get_schedules', SellFeedException, True, ['sell.feed', 'schedule'], feed_type, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_update_schedule(self, body, schedule_id, **kwargs):  # noqa: E501
        """update_schedule  

        This method updates an existing schedule. Specify the schedule to update using the schedule_id path parameter. If the schedule template has changed after the schedule was created or updated, the input will be validated using the changed template. Note: Make sure to include all fields required by the schedule template (scheduleTemplateId). Call the getScheduleTemplate method (or the getScheduleTemplates method), to find out which fields are required or optional. If you do not know the scheduleTemplateId, call the getSchedule method to find out.  

        :param UpdateUserScheduleRequest body: In the request payload: scheduleName is optional; preferredTriggerHour, preferredTriggerDayOfWeek, preferredTriggerDayOfMonth, scheduleStartDate, scheduleEndDate, and schemaVersion are conditional. (required)
        :param str schedule_id: The ID of the schedule to update. This ID is generated when the schedule was created by the createSchedule method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.ScheduleApi, sell_feed.ApiClient, 'update_schedule', SellFeedException, True, ['sell.feed', 'schedule'], (body, schedule_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_create_task(self, body, **kwargs):  # noqa: E501
        """create_task  

        This method creates an upload task or a download task without filter criteria. When using this method, specify the  feedType and the feed file  schemaVersion. The feed type specified sets the task as a download or an upload task.  For details about the upload and download flows, see Working with Order Feeds in the Selling Integration Guide. Note: The scope depends on the feed type. An error message results when an unsupported scope or feed type is specified.The following list contains this method's authorization scopes and their corresponding feed types:https://api.ebay.com/oauth/api_scope/sell.inventory: See LMS FeedTypeshttps://api.ebay.com/oauth/api_scope/sell.fulfillment: LMS_ORDER_ACK (specify for upload tasks). Also see LMS FeedTypeshttps://api.ebay.com/oauth/api_scope/sell.marketing: None*https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly: None** Reserved for future release  

        :param CreateTaskRequest body: description not needed (required)
        :param str x_ebay_c_marketplace_id: The ID of the eBay marketplace where the item is hosted.  Note: This value is case sensitive.For example:X-EBAY-C-MARKETPLACE-ID:EBAY_USThis identifies the eBay marketplace that applies to this task. See MarketplaceIdEnum.
        :return: None
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'create_task', SellFeedException, True, ['sell.feed', 'task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_input_file(self, task_id, **kwargs):  # noqa: E501
        """get_input_file  

        This method downloads the file previously uploaded using uploadFile. Specify the task_id from the uploadFile call. Note: With respect to LMS, this method applies to all feed types except LMS_ORDER_REPORT and LMS_ACTIVE_INVENTORY_REPORT. See LMS API Feeds in the Selling Integration Guide.  

        :param str task_id: The task ID associated with the file to be downloaded. (required)
        :return: StreamingOutput
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_input_file', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_result_file(self, task_id, **kwargs):  # noqa: E501
        """get_result_file  

        This method retrieves the generated file that is associated with the specified task ID. The response of this call is a compressed or uncompressed CSV, XML, or JSON file, with the applicable file extension (for example: csv.gz). For details about how this method is used, see Working with Order Feeds in the Selling Integration Guide. Note: The status of the task to retrieve must be in the COMPLETED or COMPLETED_WITH_ERROR state before this method can retrieve the file. You can use the getTask or getTasks method to retrieve the status of the task.  

        :param str task_id: The ID of the task associated with the file you want to download. This ID was generated when the task was created. (required)
        :return: StreamingOutput
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_result_file', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_task(self, task_id, **kwargs):  # noqa: E501
        """get_task  

        This method retrieves the details and status of the specified task. The input is task_id. For details of how this method is used, see Working with Order Feeds in the Selling Integration Guide.   

        :param str task_id: The ID of the task. This ID was generated when the task was created. (required)
        :return: Task
        """
        try:
            return self._method_single(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_task', SellFeedException, True, ['sell.feed', 'task'], task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_get_tasks(self, **kwargs):  # noqa: E501
        """get_tasks  

        This method returns the details and status for an array of tasks based on a specified feed_type or scheduledId. Specifying both feed_type and scheduledId results in an error. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.If specifying the feed_type, limit which tasks are returned by specifying filters, such as the creation date range or period of time using look_back_days. Also, by specifying the feed_type, both on-demand and scheduled reports are returned.If specifying a scheduledId, the schedule template (that the schedule ID is based on) determines which tasks are returned (see schedule_id for additional information). Each scheduledId applies to one feed_type.   

        :param str date_range: Specifies the range of task creation dates used to filter the results. The results are filtered to include only tasks with a creation date that is equal to this date or is within specified range. Only tasks that are less than 90 days can be retrieved.  Note: Maximum date range window size is 90 days. Valid Format (UTC):yyyy-MM-ddThh:mm:ss.SSSZ..yyyy-MM-ddThh:mm:ss.SSSZ For example: Tasks created on September 8, 2019 2019-09-08T00:00:00.000Z..2019-09-09T00:00:00.000Z
        :param str feed_type: The feed type associated with the tasks to be returned. Only use a feedType that is available for your API: Order Feeds: LMS_ORDER_ACK, LMS_ORDER_REPORTLarge Merchant Services (LMS) Feeds: See Available FeedTypesDo not use with the schedule_id parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :param str limit: The maximum number of tasks that can be returned on each page of the paginated response. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.For example, if offset is set to 10 and limit is set to 10, the call retrieves tasks 11 thru 20 from the result set.If this parameter is omitted, the default value is used. Default:  10 Maximum: 500
        :param str look_back_days: The number of previous days in which to search for tasks. Do not use with the date_range parameter. If both date_range and look_back_days are omitted, this parameter's default value is used.  Default:  7 Range:  1-90 (inclusive)
        :param str offset: The number of tasks to skip in the result set before returning the first task in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. If this query parameter is not set, the default value is used and the first page of records is returned. Default: 0
        :param str schedule_id: The schedule ID associated with the task. A schedule periodically generates a report for the feed type specified by the schedule template (see scheduleTemplateId in createSchedule). Do not use with the feed_type parameter. Since schedules are based on feed types, you can specify a schedule (schedule_id) that returns the needed feed_type.
        :return: TaskCollection
        """
        try:
            return self._method_paged(sell_feed.Configuration, '/sell/feed/v1', sell_feed.TaskApi, sell_feed.ApiClient, 'get_tasks', SellFeedException, True, ['sell.feed', 'task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_feed_upload_file(self, task_id, **kwargs):  # noqa: E501
        """upload_file  

        This method associates the specified file with the specified task ID and uploads the input file. After the file has been uploaded, the processing of the file begins. Reports often take time to generate and it's common for this method to return an HTTP status of 202, which indicates the report is being generated. Use the  getTask with the task ID or  getTasks to determine the status of a report. The status flow is QUEUED > IN_PROCESS > COMPLETED or COMPLETED_WITH_ERROR. When the status is COMPLETED or COMPLETED_WITH_ERROR, this indicates the file has been processed and the order report can be downloaded. If there are errors, they will be indicated in the report file. For details of how this method is used in the upload flow, see Working with Order Feeds in the Selling Integration Guide. Note: This method applies to all Seller Hub feed types and LMS feed types except LMS_ORDER_REPORT and LMS_ACTIVE_INVENTORY_REPORT. See LMS feed types and Seller Hub feed types. Note: You must use a Content-Type header with its value set to \"multipart/form-data\". See Samples for information.  

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
        """get_payout  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.This method retrieves details on a specific seller payout. The unique identifier of the payout is passed in as a path parameter at the end of the call URI. The getPayouts method can be used to retrieve the unique identifier of a payout, or the user can check Seller Hub.  

        :param str payout_id: The unique identifier of the payout is passed in as a path parameter at the end of the call URI. The getPayouts method can be used to retrieve the unique identifier of a payout, or the user can check Seller Hub to get the payout ID. (required)
        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :return: Payout
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.PayoutApi, sell_finances.ApiClient, 'get_payout', SellFinancesException, True, ['sell.finances', 'payout'], payout_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_payout_summary(self, **kwargs):  # noqa: E501
        """get_payout_summary  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.This method is used to retrieve cumulative values for payouts in a particular state, or all states. The metadata in the response includes total payouts, the total number of monetary transactions (sales, refunds, credits) associated with those payouts, and the total dollar value of all payouts.If the filter query parameter is used to filter by payout status, only one payout status value may be used. If the filter query parameter is not used to filter by a specific payout status, cumulative values for payouts in all states are returned.The user can also use the filter query parameter to specify a date range, and then only payouts that were processed within that date range are considered.  

        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :param str filter: The two filter types that can be used here are discussed below. One or both of these filter types can be used. If none of these filters are used, the data returned in the response will reflect payouts, in all states, processed within the last 90 days. payoutDate: consider payouts processed within a specific range of dates. The date format to use is YYYY-MM-DDTHH:MM:SS.SSSZ. Below is the proper syntax to use if filtering by a date range: https://apiz.ebay.com/sell/finances/v1/payout_summary?filter=payoutDate:[2018-12-17T00:00:01.000Z..2018-12-24T00:00:01.000Z]Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past. payoutStatus: consider only the payouts in a particular state. Only one payout state can be specified with this filter. The supported payoutStatus values are as follows:INITIATED: search for payouts that have been initiated but not processed.SUCCEEDED: consider only successful payouts.RETRYABLE_FAILED: consider only payouts that failed, but ones which will be tried again.TERMINAL_FAILED: consider only payouts that failed, and ones that will not be tried again. REVERSED: consider only payouts that were reversed. Below is the proper syntax to use if filtering by payout status: https://apiz.ebay.com/sell/finances/v1/payout_summary?filter=payoutStatus:{SUCCEEDED}If both the payoutDate and payoutStatus filters are used, only the payouts that satisfy both criteria are considered in the results. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :return: PayoutSummaryResponse
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.PayoutApi, sell_finances.ApiClient, 'get_payout_summary', SellFinancesException, True, ['sell.finances', 'payout'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_payouts(self, **kwargs):  # noqa: E501
        """get_payouts  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.This method is used to retrieve the details of one or more seller payouts. By using the filter query parameter, users can retrieve payouts processed within a specific date range, and/or they can retrieve payouts in a specific state.There are also pagination and sort query parameters that allow users to control the payouts that are returned in the response.If no payouts match the input criteria, an empty payload is returned.  

        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :param str filter: The three filter types that can be used here are discussed below. If none of these filters are used, all recent payouts in all states are returned:payoutDate: search for payouts within a specific range of dates. The date format to use is YYYY-MM-DDTHH:MM:SS.SSSZ. Below is the proper syntax to use if filtering by a date range: https://apiz.ebay.com/sell/finances/v1/payout?filter=payoutDate:[2018-12-17T00:00:01.000Z..2018-12-24T00:00:01.000Z]Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past.lastAttemptedPayoutDate: search for attempted payouts that failed within a specific range of dates. In order to use this filter, the payoutStatus filter must also be used and its value must be set to RETRYABLE_FAILED. The date format to use is YYYY-MM-DDTHH:MM:SS.SSSZ. The same syntax used for the payoutDate filter is also used for the lastAttemptedPayoutDate filter. This filter is only applicable (and will return results) if one or more seller payouts have failed, but are retryable. payoutStatus: search for payouts in a particular state. Only one payout state can be specified with this filter. The supported payoutStatus values are as follows:INITIATED: search for payouts that have been initiated but not processed.SUCCEEDED: search for successful payouts.RETRYABLE_FAILED: search for payouts that failed, but ones which will be tried again. This value must be used if filtering by lastAttemptedPayoutDate. TERMINAL_FAILED: search for payouts that failed, and ones that will not be tried again. REVERSED: search for payouts that were reversed. Below is the proper syntax to use if filtering by payout status: https://apiz.ebay.com/sell/finances/v1/payout?filter=payoutStatus:{SUCCEEDED}If both the payoutDate and payoutStatus filters are used, payouts must satisfy both criteria to be returned. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :param str limit: The number of payouts to return per page of the result set. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  For example, if offset is set to 10 and limit is set to 10, the method retrieves payouts 11 thru 20 from the result set.  Note: This feature employs a zero-based list, where the first payout in the results set has an offset value of 0.   Maximum: 200  Default: 20
        :param str offset: This integer value indicates the actual position that the first payout returned on the current page has in the results set. So, if you wanted to view the 11th payout of the result set, you would set the offset value in the request to 10. In the request, you can use the offset parameter in conjunction with the limit parameter to control the pagination of the output. For example, if offset is set to 30 and limit is set to 10, the method retrieves payouts 31 thru 40 from the resulting collection of payouts.  Note: This feature employs a zero-based list, where the first payout in the results set has an offset value of 0.Default: 0 (zero)
        :param str sort: By default, payouts or failed payouts that match the input criteria are sorted in ascending order according to the payout date/last attempted payout date (oldest payouts returned first). To view payouts in descending order instead (most recent payouts/attempted payouts first), you would include the sort query parameter, and then set the value of its field parameter to payoutDate or lastAttemptedPayoutDate (if searching for failed, retryable payouts). Below is the proper syntax to use if filtering by a payout date range in descending order: https://apiz.ebay.com/sell/finances/v1/payout?filter=payoutDate:[2018-12-17T00:00:01.000Z..2018-12-24T00:00:01.000Z]&sort=payoutDatePayouts can only be sorted according to payout date, and can not be sorted by payout status. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:SortField
        :return: Payouts
        """
        try:
            return self._method_paged(sell_finances.Configuration, '/sell/finances/v1', sell_finances.PayoutApi, sell_finances.ApiClient, 'get_payouts', SellFinancesException, True, ['sell.finances', 'payout'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_seller_funds_summary(self, **kwargs):  # noqa: E501
        """get_seller_funds_summary  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.This method retrieves all pending funds that have not yet been distributed through a seller payout.There are no input parameters for this method. The response payload includes available funds, funds being processed, funds on hold, and also an aggregate count of all three of these categories.If there are no funds that are pending, on hold, or being processed for the seller's account, no response payload is returned, and an http status code of 204 - No Content is returned instead.  

        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :return: SellerFundsSummaryResponse
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.SellerFundsSummaryApi, sell_finances.ApiClient, 'get_seller_funds_summary', SellFinancesException, True, ['sell.finances', 'seller_funds_summary'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_transaction_summary(self, **kwargs):  # noqa: E501
        """get_transaction_summary  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.The getTransactionSummary method retrieves cumulative information for monetary transactions. If applicable, the number of payments with a transactionStatus equal to FUNDS_ON_HOLD and the total monetary amount of these on-hold payments are also returned.Note: For a complete list of transaction types, refer to TransactionTypeEnum.Refer to the filter field for additional information about each filter and its use.Note: Unless a transactionType filter is used to retrieve a specific type of transaction (e.g., SALE, REFUND, etc.,) the creditCount and creditAmount response fields both include order sales and seller credits information. That is, the count and value fields do not distinguish between these two types monetary transactions.  

        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :param str filter: Numerous filters are available for the getTransactionSummary method, and these filters are discussed below. One or more of these filter types can be used. The transactionStatus filter must be used. All other filters are optional. transactionStatus: the data returned in the response pertains to the sales, payouts, and transfer status set. The supported transactionStatus values are as follows:PAYOUT: only consider monetary transactions where the proceeds from the sales order(s) have been paid out to the seller's bank account.FUNDS_PROCESSING: only consider monetary transactions where the proceeds from the sales order(s) are currently being processed.FUNDS_AVAILABLE_FOR_PAYOUT: only consider monetary transactions where the proceeds from the sales order(s) are available for a seller payout, but processing has not yet begun.FUNDS_ON_HOLD: only consider monetary transactions where the proceeds from the sales order(s) are currently being held by eBay, and are not yet available for a seller payout.COMPLETED: this indicates that the funds for the corresponding TRANSFER monetary transaction have transferred and the transaction has completed.FAILED: this indicates the process has failed for the corresponding TRANSFER monetary transaction. Below is the proper syntax to use when setting up the transactionStatus filter: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionStatus:{PAYOUT}transactionDate: only consider monetary transactions that occurred within a specific range of dates.Note: All dates must be input using UTC format (YYYY-MM-DDTHH:MM:SS.SSSZ) and should be adjusted accordingly for the local timezone of the user.Below is the proper syntax to use if filtering by a date range: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionDate:[2018-10-23T00:00:01.000Z..2018-11-09T00:00:01.000Z]Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past. transactionType: only consider a specific type of monetary transaction. The supported transactionType values are as follows:SALE: a sales order. REFUND: a refund to the buyer after an order cancellation or return.CREDIT: a credit issued by eBay to the seller's account.DISPUTE: a monetary transaction associated with a payment dispute between buyer and seller.NON_SALE_CHARGE: a monetary transaction involving a seller transferring money to eBay for the balance of a charge for NON_SALE_CHARGE transactions (transactions that contain non-transactional seller fees). These can include a one-time payment, monthly/yearly subscription fees charged monthly, NRC charges, and fee credits.SHIPPING_LABEL: a monetary transaction where eBay is billing the seller for an eBay shipping label. Note that the shipping label functionality will initially only be available to a select number of sellers.TRANSFER: A transfer is a monetary transaction where eBay is billing the seller for reimbursement of a charge. An example of a transfer is a seller reimbursing eBay for a buyer refund.ADJUSTMENT: An adjustment is a monetary transaction where eBay is crediting or debiting the seller's account.WITHDRAWAL: A withdrawal is a monetary transaction where the seller requests an on-demand payout from eBay.Note: On-demand payout is not available for sellers who are already on a daily payout schedule. In order to initiate an on-demand payout, a seller must be on a weekly, bi-weekly, or monthly payout schedule.LOAN_REPAYMENT: A monetary transaction related to the repayment of an outstanding loan balance for approved participants enrolled in the eBay Seller Capital financing program.Note: eBay Seller Capital financing is only available in select marketplaces. Refer to Marketplace availability for eBay Seller Capital funding program for current marketplace eligibility.Below is the proper syntax to use if filtering by a monetary transaction type: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionType:{SALE}buyerUsername: only consider monetary transactions involving a specific buyer (specified with the buyer's eBay user ID). Below is the proper syntax to use if filtering by a specific eBay buyer: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=buyerUsername:{buyer1234} salesRecordReference: only consider monetary transactions corresponding to a specific order (identified with a Selling Manager order identifier). Below is the proper syntax to use if filtering by a specific Selling Manager Sales Record ID: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=salesRecordReference:{123}Note: For all orders originating after February 1, 2020, a value of 0 will be returned in the salesRecordReference field. So, this filter will only be useful to retrieve orders than occurred before this date. payoutId: only consider monetary transactions related to a specific seller payout (identified with a Payout ID). This value is auto-generated by eBay once the seller payout is set to be processed. Below is the proper syntax to use if filtering by a specific Payout ID: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=payoutId:{5********8} transactionId: the unique identifier of a monetary transaction. For a sales order, the orderId filter should be used instead. Only the monetary transaction(s) associated with this transactionId value are returned.Note: This filter cannot be used alone; the transactionType must also be specified when filtering by transaction ID.Below is the proper syntax to use if filtering by a specific transaction ID: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=transactionId:{0*-0***0-3***3}&filter=transactionType:{SALE} orderId: the unique identifier of a sales order. For any other monetary transaction, the transactionId filter should be used instead. Only the monetary transaction(s) associated with this orderId value are returned. Below is the proper syntax to use if filtering by a specific order ID: https://apiz.ebay.com/sell/finances/v1/transaction_summary?filter=orderId:{0*-0***0-3***3}  For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :return: TransactionSummaryResponse
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.TransactionApi, sell_finances.ApiClient, 'get_transaction_summary', SellFinancesException, True, ['sell.finances', 'transaction'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_transactions(self, **kwargs):  # noqa: E501
        """get_transactions  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.The getTransactions method allows a seller to retrieve information about one or more of their monetary transactions.Note: For a complete list of transaction types, refer to TransactionTypeEnum.Numerous input filters are available which can be used individualy or combined to refine the data that are returned. For example:SALE transactions for August 15, 2022;RETURN transactions for the month of January, 2021;Transactions currently in a transactionStatus equal to FUNDS_ON_HOLD.Refer to the filter field for additional information about each filter and its use.Pagination and sort query parameters are also provided that allow users to further control how monetary transactions are displayed in the response.If no monetary transactions match the input criteria, an http status code of 204 No Content is returned with no response payload.  

        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :param str filter: Numerous filters are available for the getTransactions method, and these filters are discussed below. One or more of these filter types can be used. If none of these filters are used, all monetary transactions from the last 90 days are returned:transactionDate: search for monetary transactions that occurred within a specific range of dates.Note: All dates must be input using UTC format (YYYY-MM-DDTHH:MM:SS.SSSZ) and should be adjusted accordingly for the local timezone of the user.Below is the proper syntax to use if filtering by a date range: https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionDate:[2018-10-23T00:00:01.000Z..2018-11-09T00:00:01.000Z]Alternatively, the user could omit the ending date, and the date range would include the starting date and up to 90 days past that date, or the current date if the starting date is less than 90 days in the past. transactionType: search for a specific type of monetary transaction. The supported transactionType values are as follows:SALE: a sales order. REFUND: a refund to the buyer after an order cancellation or return.CREDIT: a credit issued by eBay to the seller's account.DISPUTE: a monetary transaction associated with a payment dispute between buyer and seller.NON_SALE_CHARGE: a monetary transaction involving a seller transferring money to eBay for the balance of a charge for NON_SALE_CHARGE transactions (transactions that contain non-transactional seller fees). These can include a one-time payment, monthly/yearly subscription fees charged monthly, NRC charges, and fee credits.SHIPPING_LABEL: a monetary transaction where eBay is billing the seller for an eBay shipping label. Note that the shipping label functionality will initially only be available to a select number of sellers.TRANSFER: A transfer is a monetary transaction where eBay is billing the seller for reimbursement of a charge. An example of a transfer is a seller reimbursing eBay for a buyer refund.ADJUSTMENT: An adjustment is a monetary transaction where eBay is crediting or debiting the seller's account.WITHDRAWAL: A withdrawal is a monetary transaction where the seller requests an on-demand payout from eBay.Note: On-demand payout is not available for sellers who are already on a daily payout schedule. In order to initiate an on-demand payout, a seller must be on a weekly, bi-weekly, or monthly payout schedule.LOAN_REPAYMENT: A monetary transaction related to the repayment of an outstanding loan balance for approved participants enrolled in the eBay Seller Capital financing program.Note: eBay Seller Capital financing is only available in select marketplaces. Refer to Marketplace availability for eBay Seller Capital funding program for current marketplace eligibility.Below is the proper syntax to use if filtering by a monetary transaction type: https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionType:{SALE}transactionStatus: this filter type is only applicable for sales orders, and allows the user to filter seller payouts in a particular state.  The supported transactionStatus values are as follows:PAYOUT: this indicates that the proceeds from the corresponding sales order has been paid out to the seller's account.FUNDS_PROCESSING: this indicates that the funds for the corresponding monetary transaction are currently being processed.FUNDS_AVAILABLE_FOR_PAYOUT: this indicates that the proceeds from the corresponding sales order are available for a seller payout, but processing has not yet begun.FUNDS_ON_HOLD: this indicates that the proceeds from the corresponding sales order are currently being held by eBay, and are not yet available for a seller payout.COMPLETED: this indicates that the funds for the corresponding TRANSFER monetary transaction have transferred and the transaction has completed.FAILED: this indicates the process has failed for the corresponding TRANSFER monetary transaction. Below is the proper syntax to use if filtering by transaction status: https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionStatus:{PAYOUT}buyerUsername: the eBay user ID of the buyer involved in the monetary transaction. Only monetary transactions involving this buyer are returned. Below is the proper syntax to use if filtering by a specific eBay buyer: https://apiz.ebay.com/sell/finances/v1/transaction?filter=buyerUsername:{buyer1234} salesRecordReference: the unique Selling Manager identifier of the order involved in the monetary transaction. Only monetary transactions involving this Selling Manager Sales Record ID are returned. Below is the proper syntax to use if filtering by a specific Selling Manager Sales Record ID: https://apiz.ebay.com/sell/finances/v1/transaction?filter=salesRecordReference:{123}Note: For all orders originating after February 1, 2020, a value of 0 will be returned in the salesRecordReference field. So, this filter will only be useful to retrieve orders than occurred before this date. payoutId: the unique identifier of a seller payout. This value is auto-generated by eBay once the seller payout is set to be processed. Only monetary transactions involving this Payout ID are returned. Below is the proper syntax to use if filtering by a specific Payout ID: https://apiz.ebay.com/sell/finances/v1/transaction?filter=payoutId:{5********8} transactionId: the unique identifier of a monetary transaction. For a sales order, the orderId filter should be used instead. Only the monetary transaction defined by the identifier is returned.Note: This filter cannot be used alone; the transactionType must also be specified when filtering by transaction ID.Below is the proper syntax to use if filtering by a specific transaction ID: https://apiz.ebay.com/sell/finances/v1/transaction?filter=transactionId:{0*-0***0-3***3}&filter=transactionType:{SALE} orderId: the unique identifier of a sales order. Only monetary transaction(s) associated with this orderId value are returned.For any other monetary transaction, the transactionId filter should be used instead.Below is the proper syntax to use if filtering by a specific order ID:https://apiz.ebay.com/sell/finances/v1/transaction?filter=orderId:{0*-0***0-3***3}  For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:FilterField
        :param str limit: The number of monetary transactions to return per page of the result set. Use this parameter in conjunction with the offset parameter to control the pagination of the output.  For example, if offset is set to 10 and limit is set to 10, the method retrieves monetary transactions 11 thru 20 from the result set.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.  Maximum: 1000  Default: 20
        :param str offset: This integer value indicates the actual position that the first monetary transaction returned on the current page has in the results set. So, if you wanted to view the 11th monetary transaction of the result set, you would set the offset value in the request to 10. In the request, you can use the offset parameter in conjunction with the limit parameter to control the pagination of the output. For example, if offset is set to 30 and limit is set to 10, the method retrieves transactions 31 thru 40 from the resulting collection of transactions.  Note: This feature employs a zero-based list, where the first item in the list has an offset of 0.Default: 0 (zero)
        :param str sort: Sorting is not yet available for the getTransactions method. By default, monetary transactions that match the input criteria are sorted in descending order according to the transaction date. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/finances/types/cos:SortField
        :return: Transactions
        """
        try:
            return self._method_paged(sell_finances.Configuration, '/sell/finances/v1', sell_finances.TransactionApi, sell_finances.ApiClient, 'get_transactions', SellFinancesException, True, ['sell.finances', 'transaction'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_finances_get_transfer(self, transfer_id, **kwargs):  # noqa: E501
        """get_transfer  

        Important! Due to EU & UK Payments regulatory requirements, an additional security verification via Digital Signatures is required for certain API calls that are made on behalf of EU/UK sellers, including all Finances API methods. Please refer to Digital Signatures for APIs to learn more on the impacted APIs and the process to create signatures to be included in the HTTP payload.This method retrieves detailed information regarding a TRANSFER transaction type. A TRANSFER is a  monetary transaction type that involves a seller transferring money to eBay for reimbursement of one or more charges. For example, when a seller reimburses eBay for a buyer refund.If an ID is passed into the URI that is an identifier for another transaction type, this call will return an http status code of 404 Not found.  

        :param str transfer_id: The unique identifier of the TRANSFER transaction type you wish to retrieve. (required)
        :param str x_ebay_c_marketplace_id: This header identifies the seller's eBay marketplace. It is required for all marketplaces outside of the US. See HTTP request headers for the marketplace ID values.
        :return: Transfer
        """
        try:
            return self._method_single(sell_finances.Configuration, '/sell/finances/v1', sell_finances.TransferApi, sell_finances.ApiClient, 'get_transfer', SellFinancesException, True, ['sell.finances', 'transfer'], transfer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_order(self, order_id, **kwargs):  # noqa: E501
        """get_order  

        Use this call to retrieve the contents of an order based on its unique identifier, orderId. This value was returned in the  getOrders call's orders.orderId field when you searched for orders by creation date, modification date, or fulfillment status. Include the optional fieldGroups query parameter set to TAX_BREAKDOWN to return a breakdown of the taxes and fees.  The returned Order object contains information you can use to create and process fulfillments, including:  Information about the buyer and seller Information about the order's line items  The plans for packaging, addressing and shipping the order The status of payment, packaging, addressing, and shipping the order A summary of monetary amounts specific to the order such as pricing, payments, and shipping costs A summary of applied taxes and fees, and optionally a breakdown of each   

        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the getOrders method in the orders.orderId field. (required)
        :param str field_groups: The response type associated with the order. The only presently supported value is TAX_BREAKDOWN. This type returns a breakdown of tax and fee values associated with the order.
        :return: Order
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.OrderApi, sell_fulfillment.ApiClient, 'get_order', SellFulfillmentException, True, ['sell.fulfillment', 'order'], order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_orders(self, **kwargs):  # noqa: E501
        """get_orders  

        Use this call to search for and retrieve one or more orders based on their creation date, last modification date, or fulfillment status using the filter parameter. You can alternatively specify a list of orders using the orderIds parameter. Include the optional fieldGroups query parameter set to TAX_BREAKDOWN to return a breakdown of the taxes and fees.  The returned Order objects contain information you can use to create and process fulfillments, including:  Information about the buyer and seller Information about the order's line items The plans for packaging, addressing and shipping the order The status of payment, packaging, addressing, and shipping the order A summary of monetary amounts specific to the order such as pricing, payments, and shipping costs A summary of applied taxes and fees, and optionally a breakdown of each   Important: In this call, the cancelStatus.cancelRequests array is returned but is always empty. Use the getOrder call instead, which returns this array fully populated with information about any cancellation requests.  

        :param str field_groups: The response type associated with the order. The only presently supported value is TAX_BREAKDOWN. This type returns a breakdown of tax and fee values associated with the order.
        :param str filter: One or more comma-separated criteria for narrowing down the collection of orders returned by this call. These criteria correspond to specific fields in the response payload. Multiple filter criteria combine to further restrict the results.  Note: Currently, filter returns data from only the last 90 days. If the orderIds parameter is included in the request, the filter parameter will be ignored.  The available criteria are as follows:  creationdate The time period during which qualifying orders were created (the orders.creationDate field). In the URI, this is expressed as a starting timestamp, with or without an ending timestamp (in brackets). The timestamps are in ISO 8601 format, which uses the 24-hour Universal Coordinated Time (UTC) clock.For example:  creationdate:[2016-02-21T08:25:43.511Z..] identifies orders created on or after the given timestamp. creationdate:[2016-02-21T08:25:43.511Z..2016-04-21T08:25:43.511Z] identifies orders created between the given timestamps, inclusive.   lastmodifieddate The time period during which qualifying orders were last modified (the orders.modifiedDate field).  In the URI, this is expressed as a starting timestamp, with or without an ending timestamp (in brackets). The timestamps are in ISO 8601 format, which uses the 24-hour Universal Coordinated Time (UTC) clock.For example:  lastmodifieddate:[2016-05-15T08:25:43.511Z..] identifies orders modified on or after the given timestamp. lastmodifieddate:[2016-05-15T08:25:43.511Z..2016-05-31T08:25:43.511Z] identifies orders modified between the given timestamps, inclusive.  Note: If creationdate and lastmodifieddate are both included, only creationdate is used.  orderfulfillmentstatus The degree to which qualifying orders have been shipped (the orders.orderFulfillmentStatus field). In the URI, this is expressed as one of the following value combinations:  orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS} specifies orders for which no shipping fulfillments have been started, plus orders for which at least one shipping fulfillment has been started but not completed. orderfulfillmentstatus:{FULFILLED|IN_PROGRESS} specifies orders for which all shipping fulfillments have been completed, plus orders for which at least one shipping fulfillment has been started but not completed.  Note: The values NOT_STARTED, IN_PROGRESS, and FULFILLED can be used in various combinations, but only the combinations shown here are currently supported.   Here is an example of a getOrders call using all of these filters:  GET https://api.ebay.com/sell/v1/order?filter=creationdate:%5B2016-03-21T08:25:43.511Z..2016-04-21T08:25:43.511Z%5D,lastmodifieddate:%5B2016-05-15T08:25:43.511Z..%5D,orderfulfillmentstatus:%7BNOT_STARTED%7CIN_PROGRESS%7D  Note: This call requires that certain special characters in the URI query string be percent-encoded:      [ = %5B       ] = %5D       { = %7B       | = %7C       } = %7D  This query filter example uses these codes. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/fulfillment/types/api:FilterField
        :param str limit: The number of orders to return per page of the result set. Use this parameter in conjunction with the offset parameter to control the pagination of the output. For example, if offset is set to 10 and limit is set to 10, the call retrieves orders 11 thru 20 from the result set.  If a limit is not set, the limit defaults to 50 and returns up to 50 orders. If a requested limit is more than 200, the call fails and returns an error. Note: This feature employs a zero-based list, where the first item in the list has an offset of 0. If the orderIds parameter is included in the request, this parameter will be ignored.  Maximum: 200  Default: 50
        :param str offset: Specifies the number of orders to skip in the result set before returning the first order in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :param str order_ids: A comma-separated list of the unique identifiers of the orders to retrieve (maximum 50). If one or more order ID values are specified through the orderIds query parameter, all other query parameters will be ignored.
        :return: OrderSearchPagedCollection
        """
        try:
            return self._method_paged(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.OrderApi, sell_fulfillment.ApiClient, 'get_orders', SellFulfillmentException, True, ['sell.fulfillment', 'order'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_issue_refund(self, order_id, **kwargs):  # noqa: E501
        """Issue Refund  


        :param str order_id: The unique identifier of the order. Order IDs are returned in the getOrders method (and GetOrders call of Trading API). The issueRefund method supports the legacy API Order IDs and REST API order IDs. (required)
        :param IssueRefundRequest body:
        :return: Refund
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.OrderApi, sell_fulfillment.ApiClient, 'issue_refund', SellFulfillmentException, True, ['sell.fulfillment', 'order'], order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_accept_payment_dispute(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Accept Payment Dispute  

        This method is used if the seller wishes to accept a payment dispute. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the getPaymentDisputeSummaries method.The revision field in the request payload is required, and the returnAddress field should be supplied if the seller is expecting the buyer to return the item. See the Request Payload section for more information on these fields.  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to accept. This identifier is automatically created by eBay once the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response.This path parameter is required, and the actual identifier value is passed in right after the payment_dispute resource. See the Resource URI above. (required)
        :param AcceptPaymentDisputeRequest body:
        :return: None
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'accept_payment_dispute', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_add_evidence(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Add an Evidence File  

        This method is used by the seller to add one or more evidence files to address a payment dispute initiated by the buyer. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the getPaymentDisputeSummaries method.Note: All evidence files should be uploaded using addEvidence and updateEvidence  before the seller decides to contest the payment dispute. Once the seller has officially contested the dispute (using contestPaymentDispute or through My eBay), the addEvidence and updateEvidence methods can no longer be used. In the evidenceRequests array of the getPaymentDispute response, eBay prompts the seller with the type of evidence file(s) that will be needed to contest the payment dispute.The file(s) to add are identified through the files array in the request payload.  Adding one or more new evidence files for a payment dispute triggers the creation of an evidence file, and the unique identifier for the new evidence file is automatically generated and returned in the evidenceId field of the addEvidence response payload upon a successful call.The type of evidence being added should be specified in the evidenceType field. All files being added (if more than one) should correspond to this evidence type.Upon a successful call, an evidenceId value is returned in the response. This indicates that a new evidence set has been created for the payment dispute, and this evidence set includes the evidence file(s) that were passed in to the fileId array. The evidenceId value will be needed if the seller wishes to add to the evidence set by using the updateEvidence method, or if they want to retrieve a specific evidence file within the evidence set by using the fetchEvidenceContent method.  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to add evidence for a contested payment dispute. This identifier is automatically created by eBay once the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response.This path parameter is required, and the actual identifier value is passed in right after the payment_dispute resource. See the Resource URI above. (required)
        :param AddEvidencePaymentDisputeRequest body:
        :return: AddEvidencePaymentDisputeResponse
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'add_evidence', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_contest_payment_dispute(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Contest Payment Dispute  

        This method is used if the seller wishes to contest a payment dispute initiated by the buyer. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the getPaymentDisputeSummaries method.Note: Before contesting a payment dispute, the seller must upload all supporting files using the addEvidence and updateEvidence methods. Once the seller has officially contested the dispute (using contestPaymentDispute), the addEvidence and updateEvidence methods can no longer be used. In the evidenceRequests array of the getPaymentDispute response, eBay prompts the seller with the type of supporting file(s) that will be needed to contest the payment dispute.If a seller decides to contest a payment dispute, that seller should be prepared to provide supporting documents such as proof of delivery, proof of authentication, or other documents. The type of supporting documents that the seller will provide will depend on why the buyer filed the payment dispute.The revision field in the request payload is required, and the returnAddress field should be supplied if the seller is expecting the buyer to return the item. See the Request Payload section for more information on these fields.  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to contest. This identifier is automatically created by eBay once the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response.This path parameter is required, and the actual identifier value is passed in right after the payment_dispute resource. See the Resource URI above. (required)
        :param ContestPaymentDisputeRequest body:
        :return: None
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'contest_payment_dispute', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_fetch_evidence_content(self, payment_dispute_id, evidence_id, file_id, **kwargs):  # noqa: E501
        """Get Payment Dispute Evidence File  

        This call retrieves a specific evidence file for a payment dispute. The following three identifying parameters are needed in the call URI:payment_dispute_id: the identifier of the payment dispute. The identifier of each payment dispute is returned in the getPaymentDisputeSummaries response.evidence_id: the identifier of the evidential file set. The identifier of an evidential file set for a payment dispute is returned under the evidence array in the getPaymentDispute response.file_id: the identifier of an evidential file. This file must belong to the evidential file set identified through the evidence_id query parameter. The identifier of each evidential file is returned under the evidence.files array in the getPaymentDispute response.An actual binary file is returned if the call is successful. An error will occur if any of three identifiers are invalid.  

        :param str payment_dispute_id: The identifier of the payment dispute. The identifier of each payment dispute is returned in the getPaymentDisputeSummaries response. This identifier is passed in as a path parameter at the end of the call URI. (required)
        :param str evidence_id: The identifier of the evidential file set. The identifier of an evidential file set for a payment dispute is returned under the evidence array in the getPaymentDispute response.Below is an example of the syntax to use for this query parameter:evidence_id=12345678 (required)
        :param str file_id: The identifier of an evidential file. This file must belong to the evidential file set identified through the evidence_id query parameter. The identifier of each evidential file is returned under the evidence.files array in the getPaymentDispute response. Below is an example of the syntax to use for this query parameter:file_id=12345678  (required)
        :return: list[str]
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'fetch_evidence_content', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], (payment_dispute_id, evidence_id, file_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_activities(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Get Payment Dispute Activity  

        This method retrieve a log of activity for a payment dispute. The identifier of the payment dispute is passed in as a path parameter. The output includes a timestamp for each action of the payment dispute, from creation to resolution, and all steps in between.  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed in at the end of the call URI to identify the payment dispute for which the user wishes to see all activity. This identifier is automatically created by eBay once the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response.This path parameter is required, and the actual identifier value is passed in right after the payment_dispute resource. See the Resource URI above. (required)
        :return: PaymentDisputeActivityHistory
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'get_activities', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_payment_dispute(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Get Payment Dispute Details  

        This method retrieves detailed information on a specific payment dispute. The payment dispute identifier is passed in as path parameter at the end of the call URI.Below is a summary of the information that is retrieved:Current status of payment disputeAmount of the payment disputeReason the payment dispute was openedOrder and line items associated with the payment disputeSeller response options if an action is currently required on the payment disputeDetails on the results of the payment dispute if it has been closedDetails on any evidence that was provided by the seller to fight the payment dispute  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed in at the end of the call URI to identify the payment dispute to retrieve. This identifier is automatically created by eBay once the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response. (required)
        :return: PaymentDispute
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'get_payment_dispute', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_payment_dispute_summaries(self, **kwargs):  # noqa: E501
        """Search Payment Dispute by Filters  

        This method is used retrieve one or more payment disputes filed against the seller. These payment disputes can be open or recently closed. The following filter types are available in the request payload to control the payment disputes that are returned:Dispute filed against a specific order (order_id parameter is used)Dispute(s) filed by a specific buyer (buyer_username parameter is used)Dispute(s) filed within a specific date range (open_date_from and/or open_date_to parameters are used)Disputes in a specific state (payment_dispute_status parameter is used)More than one of these filter types can be used together. See the request payload request fields for more information about how each filter is used.If none of the filters are used, all open and recently closed payment disputes are returned.Pagination is also available. See the limit and offset fields for more information on how pagination is used for this method.  

        :param str order_id: This filter is used if the seller wishes to retrieve one or more payment disputes filed against a specific order. It is possible that there can be more than one dispute filed against an order if the order has multiple line items. If this filter is used, any other filters are ignored.
        :param str buyer_username: This filter is used if the seller wishes to retrieve one or more payment disputes opened by a specific seller. The string that is passed in to this query parameter is the eBay user ID of the buyer.
        :param str open_date_from: The open_date_from and/or open_date_to date filters are used if the seller wishes to retrieve payment disputes opened within a specific date range. A maximum date range that may be set with the open_date_from and/or open_date_to filters is 90 days. These date filters use the ISO-8601 24-hour date and time format, and time zone used is Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT), or Zulu.The open_date_from field sets the beginning date of the date range, and can be set as far back as 18 months from the present time. If a open_date_from field is used, but a open_date_to field is not used, the open_date_to value will default to 90 days after the date specified in the open_date_from field, or to the present time if less than 90 days in the past.The ISO-8601 format looks like this: yyyy-MM-ddThh:mm.ss.sssZ. An example would be 2019-08-04T19:09:02.768Z.
        :param str open_date_to: The open_date_from and/or open_date_to date filters are used if the seller wishes to retrieve payment disputes opened within a specific date range. A maximum date range that may be set with the open_date_from and/or open_date_to filters is 90 days. These date filters use the ISO-8601 24-hour date and time format, and the time zone used is Universal Coordinated Time (UTC), also known as Greenwich Mean Time (GMT), or Zulu.The open_date_to field sets the ending date of the date range, and can be set up to 90 days from the date set in the open_date_from field. The ISO-8601 format looks like this: yyyy-MM-ddThh:mm.ss.sssZ. An example would be 2019-08-04T19:09:02.768Z.
        :param str payment_dispute_status: This filter is used if the seller wishes to only retrieve payment disputes in a specific state. More than one value can be specified. If no payment_dispute_status filter is used, payment disputes in all states are returned in the response. See DisputeStateEnum type for supported values.
        :param str limit: The value passed in this query parameter sets the maximum number of payment disputes to return per page of data. The value passed in this field should be an integer from 1 to 200. If this query parameter is not set, up to 200 records will be returned on each page of results.Min: 1; Max: 200; Default: 200
        :param str offset: This field is used to specify the number of records to skip in the result set before returning the first payment dispute in the paginated response. A zero-based index is used, so if you set the offset value to 0 (default value), the first payment dispute in the result set appears at the top of the response. Combine offset with the limit parameter to control the payment disputes returned in the response. For example, if you supply an offset value of 0 and a limit value of 10, the response will contain the first 10 payment disputes from the result set that matches the input criteria. If you supply an offset value of 10 and a limit value of 20, the response will contain payment disputes 11-30 from the result set that matches the input criteria.Min: 0; Max: total number of payment disputes - 1; Default: 0
        :return: DisputeSummaryResponse
        """
        try:
            return self._method_paged(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'get_payment_dispute_summaries', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_update_evidence(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Update evidence  

        This method is used by the seller to update an existing evidence set for a payment dispute with one or more evidence files. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the getPaymentDisputeSummaries method.Note: All evidence files should be uploaded using addEvidence and updateEvidence  before the seller decides to contest the payment dispute. Once the seller has officially contested the dispute (using contestPaymentDispute or through My eBay), the addEvidence and updateEvidence methods can no longer be used. In the evidenceRequests array of the getPaymentDispute response, eBay prompts the seller with the type of evidence file(s) that will be needed to contest the payment dispute.The unique identifier of the evidence set to update is specified through the evidenceId field, and the file(s) to add are identified through the files array in the request payload. The unique identifier for an evidence file is automatically generated and returned in the fileId field of the uploadEvidence response payload upon a successful call. Sellers must make sure to capture the fileId value for each evidence file that is uploaded with the uploadEvidence method.The type of evidence being added should be specified in the evidenceType field.  All files being added (if more than one) should correspond to this evidence type.Upon a successful call, an http status code of 204 Success is returned. There is no response payload unless an error occurs. To verify that a new file is a part of the evidence set, the seller can use the fetchEvidenceContent method, passing in the proper evidenceId and fileId values.  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to update the evidence set for a contested payment dispute. This identifier is automatically created by eBay once the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response.This path parameter is required, and the actual identifier value is passed in right after the payment_dispute resource. See the Resource URI above. (required)
        :param UpdateEvidencePaymentDisputeRequest body:
        :return: None
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'update_evidence', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_upload_evidence_file(self, payment_dispute_id, **kwargs):  # noqa: E501
        """Upload an Evidence File  

        This method is used to upload an evidence file for a contested payment dispute. The unique identifier of the payment dispute is passed in as a path parameter, and unique identifiers for payment disputes can be retrieved with the getPaymentDisputeSummaries method.Note: The uploadEvidenceFile only uploads an encrypted, binary image file (using multipart/form-data HTTP request header), and does not have a JSON-based request payload.Use 'file' as the name of the key that you use to upload the image file. The upload will not be successful if a different key name is used.The three image formats supported at this time are .JPEG, .JPG, and .PNG.After the file is successfully uploaded, the seller will need to grab the fileId value in the response payload to add this file to a new evidence set using the addEvidence method, or to add this file to an existing evidence set using the updateEvidence method.  

        :param str payment_dispute_id: This is the unique identifier of the payment dispute. This path parameter must be passed into the call URI to identify the payment dispute for which the user plans to upload an evidence file. This identifier is automatically created by eBay after the payment dispute comes into the eBay system. The unique identifier for payment disputes is returned in the paymentDisputeId field in the getPaymentDisputeSummaries response.This path parameter is required, and the actual identifier value is passed in right after the payment_dispute resource. See the Resource URI above. (required)
        :return: FileEvidence
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.PaymentDisputeApi, sell_fulfillment.ApiClient, 'upload_evidence_file', SellFulfillmentException, True, ['sell.fulfillment', 'payment_dispute'], payment_dispute_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_create_shipping_fulfillment(self, body, order_id, **kwargs):  # noqa: E501
        """create_shipping_fulfillment  

        When you group an order's line items into one or more packages, each package requires a corresponding plan for handling, addressing, and shipping; this is a shipping fulfillment. For each package, execute this call once to generate a shipping fulfillment associated with that package.  Note: A single line item in an order can consist of multiple units of a purchased item, and one unit can consist of multiple parts or components. Although these components might be provided by the manufacturer in separate packaging, the seller must include all components of a given line item in the same package. Before using this call for a given package, you must determine which line items are in the package. If the package has been shipped, you should provide the date of shipment in the request. If not provided, it will default to the current date and time.  

        :param ShippingFulfillmentDetails body: fulfillment payload (required)
        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the getOrders method in the orders.orderId field. (required)
        :return: object
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.ShippingFulfillmentApi, sell_fulfillment.ApiClient, 'create_shipping_fulfillment', SellFulfillmentException, True, ['sell.fulfillment', 'shipping_fulfillment'], (body, order_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_shipping_fulfillment(self, fulfillment_id, order_id, **kwargs):  # noqa: E501
        """get_shipping_fulfillment  

        Use this call to retrieve the contents of a fulfillment based on its unique identifier, fulfillmentId (combined with the associated order's orderId). The fulfillmentId value was originally generated by the createShippingFulfillment call, and is returned by the getShippingFulfillments call in the members.fulfillmentId field.  

        :param str fulfillment_id: The unique identifier of the fulfillment. This eBay-generated value was created by the Create Shipping Fulfillment call, and returned by the getShippingFulfillments call in the fulfillments.fulfillmentId field; for example, 9405509699937003457459. (required)
        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the getOrders method in the orders.orderId field. (required)
        :return: ShippingFulfillment
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.ShippingFulfillmentApi, sell_fulfillment.ApiClient, 'get_shipping_fulfillment', SellFulfillmentException, True, ['sell.fulfillment', 'shipping_fulfillment'], (fulfillment_id, order_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_fulfillment_get_shipping_fulfillments(self, order_id, **kwargs):  # noqa: E501
        """get_shipping_fulfillments  

        Use this call to retrieve the contents of all fulfillments currently defined for a specified order based on the order's unique identifier, orderId. This value is returned in the getOrders call's members.orderId field when you search for orders by creation date or shipment status.  

        :param str order_id: The unique identifier of the order. Order ID values are shown in My eBay/Seller Hub, and are also returned by the getOrders method in the orders.orderId field. (required)
        :return: ShippingFulfillmentPagedCollection
        """
        try:
            return self._method_single(sell_fulfillment.Configuration, '/sell/fulfillment/v1', sell_fulfillment.ShippingFulfillmentApi, sell_fulfillment.ApiClient, 'get_shipping_fulfillments', SellFulfillmentException, True, ['sell.fulfillment', 'shipping_fulfillment'], order_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_create_or_replace_inventory_item(self, body, **kwargs):  # noqa: E501
        """bulk_create_or_replace_inventory_item  

        Note: Please note that any eBay listing created using the Inventory API cannot be revised or relisted using the Trading API calls.Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.This call can be used to create and/or update up to 25 new inventory item records. It is up to sellers whether they want to create a complete inventory item records right from the start, or sellers can provide only some information with the initial bulkCreateOrReplaceInventoryItem call, and then make one or more additional bulkCreateOrReplaceInventoryItem calls to complete all required fields for the inventory item records and prepare for publishing. Upon first creating inventory item records, only the SKU values are required.  In the case of updating existing inventory item records, the bulkCreateOrReplaceInventoryItem call will do a complete replacement of the existing inventory item records, so all fields that are currently defined for the inventory item record are required in that update action, regardless of whether their values changed. So, when replacing/updating an inventory item record, it is advised that the seller run a 'Get' call to retrieve the full details of the inventory item records and see all of its current values/settings before attempting to update the records. Any changes that are made to inventory item records that are part of one or more active eBay listings, a successful call will automatically update these active listings.  The key information that is set with the bulkCreateOrReplaceInventoryItem call include:  Seller-defined SKU value for the product. Each seller product, including products within an item inventory group, must have their own SKU value.  Condition of the item Product details, including any product identifier(s), such as a UPC, ISBN, EAN, or Brand/Manufacturer Part Number pair, a product description, a product title, product/item aspects, and links to images. eBay will use any supplied eBay Product ID (ePID) or a GTIN (UPC, ISBN, or EAN) and attempt to match those identifiers to a product in the eBay Catalog, and if a product match is found, the product details for the inventory item will automatically be populated. Quantity of the inventory item that is available for purchase Package weight and dimensions, which is required if the seller will be offering calculated shipping options. The package weight will also be required if the seller will be providing flat-rate shipping services, but charging a weight surcharge.  In addition to the authorization header, which is required for all eBay REST API calls, the bulkCreateOrReplaceInventoryItem call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.For those who prefer to create or update a single inventory item record, the createOrReplaceInventoryItem method can be used.  

        :param BulkInventoryItem body: Details of the inventories with sku and locale (required)
        :return: BulkInventoryItemResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'bulk_create_or_replace_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_get_inventory_item(self, body, **kwargs):  # noqa: E501
        """bulk_get_inventory_item  

        This call retrieves up to 25 inventory item records. The SKU value of each inventory item record to retrieve is specified in the request payload. The authorization header is the only required HTTP header for this call, and it is required for all Inventory API calls. See the HTTP request headers section for more information.For those who prefer to retrieve only one inventory item record by SKU value, , the getInventoryItem method can be used. To retrieve all inventory item records defined on the seller's account, the getInventoryItems method can be used (with pagination control if desired).  

        :param BulkGetInventoryItem body: Details of the inventories with sku and locale (required)
        :return: BulkGetInventoryItemResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'bulk_get_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_update_price_quantity(self, body, **kwargs):  # noqa: E501
        """bulk_update_price_quantity  

        This call is used by the seller to update the total ship-to-home quantity of one inventory item, and/or to update the price and/or quantity of one or more offers associated with one inventory item. Up to 25 offers associated with an inventory item may be updated with one bulkUpdatePriceQuantity call. Only one SKU (one product) can be updated per call.Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.The getOffers call can be used to retrieve all offers associated with a SKU. The seller will just pass in the correct SKU value through the sku query parameter. To update an offer, the offerId value is required, and this value is returned in the getOffers call response. It is also useful to know which offers are unpublished and which ones are published. To get this status, look for the status value in the getOffers call response. Offers in the published state are live eBay listings, and these listings will be revised with a successful bulkUpdatePriceQuantity call.An issue will occur if duplicate offerId values are passed through the same offers container, or if one or more of the specified offers are associated with different products/SKUs.Note: For multiple-variation listings, it is recommended that the bulkUpdatePriceQuantity call be used to update price and quantity information for each SKU within that multiple-variation listing instead of using createOrReplaceInventoryItem calls to update the price and quantity for each SKU. Just remember that only one SKU (one product variation) can be updated per call.The authorization header is the only required HTTP header for this call. See the HTTP request headers section for more information.  

        :param BulkPriceQuantity body: Price and allocation details for the given SKU and Marketplace (required)
        :return: BulkPriceQuantityResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'bulk_update_price_quantity', SellInventoryException, True, ['sell.inventory', 'inventory_item'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_or_replace_inventory_item(self, body, content_language, sku, **kwargs):  # noqa: E501
        """create_or_replace_inventory_item  

        Note: Please note that any eBay listing created using the Inventory API cannot be revised or relisted using the Trading API calls.Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.This call creates a new inventory item record or replaces an existing inventory item record. It is up to sellers whether they want to create a complete inventory item record right from the start, or sellers can provide only some information with the initial createOrReplaceInventoryItem call, and then make one or more additional createOrReplaceInventoryItem calls to complete all required fields for  the inventory item record and prepare it for publishing. Upon first creating an inventory item record, only the SKU value in the call path is required.  In the case of replacing an existing inventory item record, the createOrReplaceInventoryItem call will do a complete replacement of the existing inventory item record, so all fields that are currently defined for the inventory item record are required in that update action, regardless of whether their values changed. So, when replacing/updating an inventory item record, it is advised that the seller run a getInventoryItem call to retrieve the full inventory item record and see all of its current values/settings before attempting to update the record. And if changes are made to an inventory item that is part of one or more active eBay listings, a successful call will automatically update these eBay listings.  The key information that is set with the createOrReplaceInventoryItem call include:  Seller-defined SKU value for the product. Each seller product, including products within an item inventory group, must have their own SKU value. This SKU value is passed in at the end of the call URI Condition of the item Product details, including any product identifier(s), such as a UPC, ISBN, EAN, or Brand/Manufacturer Part Number pair, a product description, a product title, product/item aspects, and links to images. eBay will use any supplied eBay Product ID (ePID) or a GTIN (UPC, ISBN, or EAN) and attempt to match those identifiers to a product in the eBay Catalog, and if a product match is found, the product details for the inventory item will automatically be populated. Quantity of the inventory item that is available for purchase Package weight and dimensions, which is required if the seller will be offering calculated shipping options. The package weight will also be required if the seller will be providing flat-rate shipping services, but charging a weight surcharge.  In addition to the authorization header, which is required for all eBay REST API calls, the createOrReplaceInventoryItem call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.For those who prefer to create or update numerous inventory item records with one call (up to 25 at a time), the bulkCreateOrReplaceInventoryItem method can be used.  

        :param InventoryItem body: Details of the inventory item record. (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :param str sku: The seller-defined SKU value for the inventory item is required whether the seller is creating a new inventory item, or updating an existing inventory item. This SKU value is passed in at the end of the call URI. SKU values must be unique across the seller's inventory.  Max length: 50. (required)
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'create_or_replace_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], (body, content_language, sku), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_inventory_item(self, sku, **kwargs):  # noqa: E501
        """delete_inventory_item  

        This call is used to delete an inventory item record associated with a specified SKU. A successful call will not only delete that inventory item record, but will also have the following effects:Delete any and all unpublished offers associated with that SKU;Delete any and all single-variation eBay listings associated with that SKU;Automatically remove that SKU from a multiple-variation listing and remove that SKU from any and all inventory item groups in which that SKU was a member.The authorization header is the only required HTTP header for this call. See the HTTP request headers section for more information.  

        :param str sku: This is the seller-defined SKU value of the product whose inventory item record you wish to delete.Max length: 50. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'delete_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_item(self, sku, **kwargs):  # noqa: E501
        """get_inventory_item  

        This call retrieves the inventory item record for a given SKU. The SKU value is passed in at the end of the call URI. There is no request payload for this call.The authorization header is the only required HTTP header for this call, and it is required for all Inventory API calls. See the HTTP request headers section for more information.For those who prefer to retrieve numerous inventory item records by SKU value with one call (up to 25 at a time), the bulkGetInventoryItem method can be used. To retrieve all inventory item records defined on the seller's account, the getInventoryItems method can be used (with pagination control if desired).  

        :param str sku: This is the seller-defined SKU value of the product whose inventory item record you wish to retrieve.Max length: 50. (required)
        :return: InventoryItemWithSkuLocaleGroupid
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'get_inventory_item', SellInventoryException, True, ['sell.inventory', 'inventory_item'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_items(self, **kwargs):  # noqa: E501
        """get_inventory_items  

        This call retrieves all inventory item records defined for the seller's account. The limit query parameter allows the seller to control how many records are returned per page, and the offset query parameter is used to retrieve a specific page of records. The seller can make multiple calls to scan through multiple pages of records. There is no request payload for this call.The authorization header is the only required HTTP header for this call, and it is required for all Inventory API calls. See the HTTP request headers section for more information.For those who prefer to retrieve numerous inventory item records by SKU value with one call (up to 25 at a time), the bulkGetInventoryItem method can be used.  

        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be an integer  from 1 to 100. If this query parameter is not set, up to 100 records will be returned on each page of results.Min: 1, Max: 100 
        :param str offset: The value passed in this query parameter sets the page number to retrieve. The first page of records has a value of 0, the second page of records has a value of 1, and so on. If this query parameter is not set, its value defaults to 0, and the first page of records is returned. 
        :return: InventoryItems
        """
        try:
            return self._method_paged(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemApi, sell_inventory.ApiClient, 'get_inventory_items', SellInventoryException, True, ['sell.inventory', 'inventory_item'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_or_replace_inventory_item_group(self, body, content_language, inventory_item_group_key, **kwargs):  # noqa: E501
        """create_or_replace_inventory_item_group  

        Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.This call creates a new inventory item group or updates an existing inventory item group. It is up to sellers whether they want to create a complete inventory item group record right from the start, or sellers can provide only some information with the initial createOrReplaceInventoryItemGroup call, and then make one or more additional createOrReplaceInventoryItemGroup calls to complete the inventory item group record. Upon first creating an inventory item group record, the only required elements are  the inventoryItemGroupKey identifier in the call URI, and the members of the inventory item group specified through the variantSKUs array in the request payload. In the case of updating/replacing an existing inventory item group, this call does a complete replacement of the existing inventory item group record, so all fields (including the member SKUs) that make up the inventory item group are required, regardless of whether their values changed. So, when replacing/updating an inventory item group record, it is advised that the seller run a getInventoryItemGroup call for that inventory item group to see all of its current values/settings/members before attempting to update the record. And if changes are made to an inventory item group that is part of a live, multiple-variation eBay listing, these changes automatically update the eBay listing. For example, if a SKU value is removed from the inventory item group, the corresponding product variation will be removed from the eBay listing as well. In addition to the required inventory item group identifier and member SKUs, other key information that is set with this call include:  Title and description of the inventory item group. The string values provided in these fields will actually become the listing title and listing description of the listing once the first SKU of the inventory item group is published successfully Common aspects that inventory items in the group share Product aspects that vary within each product variation Links to images demonstrating the variations of the product, and these images should correspond to the product aspect that is set with the variesBy.aspectsImageVariesBy field  In addition to the authorization header, which is required for all eBay REST API calls, the createOrReplaceInventoryItemGroup call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.  

        :param InventoryItemGroup body: Details of the inventory Item Group (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :param str inventory_item_group_key: Unique identifier of the inventory item group. This identifier is supplied by the seller. The inventoryItemGroupKey value for the inventory item group to create/update is passed in at the end of the call URI. This value cannot be changed once it is set. (required)
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemGroupApi, sell_inventory.ApiClient, 'create_or_replace_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'inventory_item_group'], (body, content_language, inventory_item_group_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_inventory_item_group(self, inventory_item_group_key, **kwargs):  # noqa: E501
        """delete_inventory_item_group  

        This call deletes the inventory item group for a given inventoryItemGroupKey value.  

        :param str inventory_item_group_key: The unique identifier of an inventory item group. This value is assigned by the seller when an inventory item group is created. The inventoryItemGroupKey value for the inventory item group to delete is passed in at the end of the call URI. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemGroupApi, sell_inventory.ApiClient, 'delete_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'inventory_item_group'], inventory_item_group_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_item_group(self, inventory_item_group_key, **kwargs):  # noqa: E501
        """get_inventory_item_group  

        This call retrieves the inventory item group for a given inventoryItemGroupKey value. The inventoryItemGroupKey value is passed in at the end of the call URI.  

        :param str inventory_item_group_key: The unique identifier of an inventory item group. This value is assigned by the seller when an inventory item group is created. The inventoryItemGroupKey value for the inventory item group to retrieve is passed in at the end of the call URI. (required)
        :return: InventoryItemGroup
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.InventoryItemGroupApi, sell_inventory.ApiClient, 'get_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'inventory_item_group'], inventory_item_group_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_migrate_listing(self, body, **kwargs):  # noqa: E501
        """bulk_migrate_listing  

        This call is used to convert existing eBay Listings to the corresponding Inventory API objects. If an eBay listing is successfully migrated to the Inventory API model, new Inventory Location, Inventory Item, and Offer objects are created. For a multiple-variation listing that is successfully migrated, in addition to the three new Inventory API objects just mentioned, an Inventory Item Group object will also be created. If the eBay listing is a motor vehicle part or accessory listing with a compatible vehicle list (ItemCompatibilityList container in Trading API's Add/Revise/Relist/Verify calls), a Product Compatibility object will be created.Migration RequirementsTo be eligible for migration, the active eBay listings must meet the following requirements:Listing type is Fixed-PriceNote: Auction listings are supported by the Inventory API, but the bulkMigrateListing method cannot be used to migrate auction listings.The item(s) in the listings must have seller-defined SKU values associated with them, and in the case of a multiple-variation listing, each product variation must also have its own SKU valueBusiness Polices (Payment, Return Policy, and Shipping) must be used on the listing, as legacy payment, return policy, and shipping fields will not be accepted. With the Payment Policy associated with a listing, the immediate payment requirement must be enabled.The postal/zip code (PostalCode field in Trading's ItemType) or city (Location field in Trading's ItemType) must be set in the listing; the country is also needed, but this value is required in Trading API, so it will always be set for every listingUnsupported Listing FeaturesThe following features are not yet available to be set or modified through the Inventory API, but they will remain on the active eBay listing, even after a successful migration to the Inventory model. The downside to this is that the seller will be completely blocked (in APIs or My eBay) from revising these features/settings once the migration takes place:Any listing-level Buyer RequirementsListing enhancements like a bold listing title or Gallery PlusMaking the CallIn the request payload of the bulkMigrateListings call, the seller will pass in an array of one to five eBay listing IDs (aka Item IDs). To save time and hassle, that seller should do a pre-check on each listing to make sure those listings meet the requirements to be migrated to the new Inventory model. There are no path or query parameters for this call.Call ResponseIf an eBay listing is migrated successfully to the new Inventory model, the following will occur:An Inventory Item object will be created for the item(s) in the listing, and this object will be accessible through the Inventory APIAn Offer object will be created for the listing, and this object will be accessible through the Inventory APIAn Inventory Location object will be created and associated with the Offer object, as an Inventory Location must be associated with a published OfferThe response payload of the Bulk Migrate Listings call will show the results of each listing migration. These results include an HTTP status code to indicate the success or failure of each listing migration, the SKU value associated with each item, and if the migration is successful, an Offer ID value. The SKU value will be used in the Inventory API to manage the Inventory Item object, and the Offer ID value will be used in the Inventory API to manage the Offer object. Errors and/or warnings containers will be returned for each listing where an error and/or warning occurred with the attempted migration.If a multiple-variation listing is successfully migrated, along with the Offer and Inventory Location objects, an Inventory Item object will be created for each product variation within the listing, and an Inventory Item Group object will also be created, grouping those variations together in the Inventory API platform. For a motor vehicle part or accessory listing that has a specified list of compatible vehicles, in addition to the Inventory Item, Inventory Location, and Offer objects that are created, a Product Compatibility object will also be created in the Inventory API platform.  

        :param BulkMigrateListing body: Details of the listings that needs to be migrated into Inventory (required)
        :return: BulkMigrateListingResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ListingApi, sell_inventory.ApiClient, 'bulk_migrate_listing', SellInventoryException, True, ['sell.inventory', 'listing'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_inventory_location(self, body, merchant_location_key, **kwargs):  # noqa: E501
        """create_inventory_location  

        Use this call to create a new inventory location. In order to create and publish an offer (and create an eBay listing), a seller must have at least one inventory location, as every offer must be associated with a location.Upon first creating an inventory location, only a seller-defined location identifier and a physical location is required, and once set, these values can not be changed. The unique identifier value (merchantLocationKey) is passed in at the end of the call URI. This merchantLocationKey value will be used in other Inventory Location calls to identify the inventory location to perform an action against.At this time, location types are either warehouse or store. Warehouse locations are used for traditional shipping, and store locations are generally used by US merchants selling products through the In-Store Pickup program, or used by UK, Australian, and German merchants selling products through the Click and Collect program. A full address is required for store inventory locations. However, for warehouse inventory locations, a full street address is not needed, but the city, state/province, and country of the location must be provided. Note that all inventory locations are \"enabled\" by default when they are created, and you must specifically disable them (by passing in a value of DISABLED in the merchantLocationStatus field) if you want them to be set to the disabled state. The seller's inventory cannot be loaded to inventory locations in the disabled state. In addition to the authorization header, which is required for all eBay REST API calls, the following table includes another request header that is mandatory for the createInventoryLocation call, and two other request headers that are optional:   Header Description Required? Applicable Values   Accept Describes the response encoding, as required by the caller. Currently, the interfaces require payloads formatted in JSON, and JSON is the default. No application/json   Content-Language Use this header to control the language that is used for any returned errors or warnings in the call response. No en-US   Content-Type The MIME type of the body of the request. Must be JSON. Yes application/json  Unless one or more errors and/or warnings occur with the call, there is no response payload for this call. A successful call will return an HTTP status value of 204 No Content.  

        :param InventoryLocationFull body: Inventory Location details (required)
        :param str merchant_location_key: A unique, merchant-defined key (ID) for an inventory location. This unique identifier, or key, is used in other Inventory API calls to identify an inventory location. Max length: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'create_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], (body, merchant_location_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """delete_inventory_location  

        This call deletes the inventory location that is specified in the merchantLocationKey path parameter. Note that deleting a location will not affect any active eBay listings associated with the deleted location, but the seller will not be able modify the offers associated with the inventory location once it is deleted.The authorization HTTP header is the only required request header for this call. Unless one or more errors and/or warnings occur with the call, there is no response payload for this call. A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in at the end of the call URI to indicate the inventory location to be deleted. Max length: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'delete_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_disable_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """disable_inventory_location  

        This call disables the inventory location that is specified in the merchantLocationKey path parameter. Sellers can not load/modify inventory to disabled inventory locations. Note that disabling an inventory location will not affect any active eBay listings associated with the disabled location, but the seller will not be able modify the offers associated with a disabled inventory location.The authorization HTTP header is the only required request header for this call.A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in through the call URI to disable the specified inventory location. Max length: 36 (required)
        :return: object
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'disable_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_enable_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """enable_inventory_location  

        This call enables a disabled inventory location that is specified in the merchantLocationKey path parameter. Once a disabled inventory location is enabled, sellers can start loading/modifying inventory to that inventory location. The authorization HTTP header is the only required request header for this call.A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in through the call URI to specify the disabled inventory location to enable. Max length: 36 (required)
        :return: object
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'enable_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_location(self, merchant_location_key, **kwargs):  # noqa: E501
        """get_inventory_location  

        This call retrieves all defined details of the inventory location that is specified by the merchantLocationKey path parameter. The authorization HTTP header is the only required request header for this call. A successful call will return an HTTP status value of 200 OK.  

        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in at the end of the call URI to specify the inventory location to retrieve. Max length: 36 (required)
        :return: InventoryLocationResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'get_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], merchant_location_key, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_inventory_locations(self, **kwargs):  # noqa: E501
        """get_inventory_locations  

        This call retrieves all defined details for every inventory location associated with the seller's account. There are no required parameters for this call and no request payload. However, there are two optional query parameters, limit and offset. The limit query parameter sets the maximum number of inventory locations returned on one page of data, and the offset query parameter specifies the page of data to return. These query parameters are discussed more in the URI parameters table below. The authorization HTTP header is the only required request header for this call. A successful call will return an HTTP status value of 200 OK.  

        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be a positive integer value. If this query parameter is not set, up to 100 records will be returned on each page of results.  Min: 1
        :param str offset: Specifies the number of locations to skip in the result set before returning the first location in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: LocationResponse
        """
        try:
            return self._method_paged(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'get_inventory_locations', SellInventoryException, True, ['sell.inventory', 'location'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_update_inventory_location(self, body, merchant_location_key, **kwargs):  # noqa: E501
        """update_inventory_location  

        Use this call to update non-physical location details for an existing inventory location. Specify the inventory location you want to update using the merchantLocationKey path parameter. You can update the following text-based fields: name, phone, locationWebUrl, locationInstructions and locationAdditionalInformation. Whatever text is passed in for these fields in an updateInventoryLocation call will replace the current text strings defined for these fields. For store inventory locations, the operating hours and/or the special hours can also be updated.  The merchant location key, the physical location of the store, and its geo-location coordinates can not be updated with an updateInventoryLocation call In addition to the authorization header, which is required for all eBay REST API calls, the following table includes another request header that is mandatory for the updateInventoryLocation call, and two other request headers that are optional:   Header Description Required? Applicable Values   Accept Describes the response encoding, as required by the caller. Currently, the interfaces require payloads formatted in JSON, and JSON is the default. No application/json   Content-Language Use this header to control the language that is used for any returned errors or warnings in the call response. No en-US   Content-Type The MIME type of the body of the request. Must be JSON. Yes application/json  Unless one or more errors and/or warnings occurs with the call, there is no response payload for this call. A successful call will return an HTTP status value of 204 No Content.  

        :param InventoryLocation body: The inventory location details to be updated (other than the address and geo co-ordinates). (required)
        :param str merchant_location_key: A unique merchant-defined key (ID) for an inventory location. This value is passed in the call URI to indicate the inventory location to be updated. Max length: 36 (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.LocationApi, sell_inventory.ApiClient, 'update_inventory_location', SellInventoryException, True, ['sell.inventory', 'location'], (body, merchant_location_key), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_create_offer(self, body, **kwargs):  # noqa: E501
        """bulk_create_offer  

        This call creates multiple offers (up to 25) for specific inventory items on a specific eBay marketplace. Although it is not a requirement for the seller to create complete offers (with all necessary details) right from the start, eBay recommends that the seller provide all necessary details with this call since there is currently no bulk operation available to update multiple offers with one call. The following fields are always required in the request payload:  sku, marketplaceId, and (listing) format. Other information that will be required before a offer can be published are highlighted below: Inventory location Offer price Available quantity eBay listing category Referenced listing policy profiles to set payment, return, and fulfillment values/settings Note: Though the includeCatalogProductDetails parameter is not required to be submitted in the request, the parameter defaults to true if omitted. If the call is successful, unique offerId values are returned in the response for each successfully created offer. The offerId value will be required for many other offer-related calls. Note that this call only stages an offer for publishing. The seller must run either the publishOffer, bulkPublishOffer, or publishOfferByInventoryItemGroup call to convert offer(s) into an active single- or multiple-variation listing. In addition to the authorization header, which is required for all eBay REST API calls, the bulkCreateOffer call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.For those who prefer to create a single offer per call, the createOffer method can be used instead.  

        :param BulkEbayOfferDetailsWithKeys body: Details of the offer for the channel (required)
        :return: BulkOfferResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'bulk_create_offer', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_bulk_publish_offer(self, body, **kwargs):  # noqa: E501
        """bulk_publish_offer  

        Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.This call is used to convert unpublished offers (up to 25) into  published offers, or live eBay listings. The unique identifier (offerId) of each offer to publish is passed into the request payload. It is possible that some unpublished offers will be successfully created into eBay listings, but others may fail. The response payload will show the results for each offerId value that is passed into the request payload. The errors and warnings containers will be returned for an offer that had one or more issues being published. For those who prefer to publish one offer per call, the publishOffer method can be used instead. In the case of a multiple-variation listing, the publishOfferByInventoryItemGroup call should be used instead, as this call will convert all unpublished offers associated with an inventory item group into a multiple-variation listing.  

        :param BulkOffer body: The base request of the bulkPublishOffer method. (required)
        :return: BulkPublishResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'bulk_publish_offer', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_offer(self, body, content_language, **kwargs):  # noqa: E501
        """create_offer  

        This call creates an offer for a specific inventory item on a specific eBay marketplace. It is up to the sellers whether they want to create a complete offer (with all necessary details) right from the start, or sellers can provide only some information with the initial createOffer call, and then make one or more subsequent updateOffer calls to complete the offer and prepare to publish the offer. Upon first creating an offer, the following fields are required in the request payload:  sku, marketplaceId, and (listing) format. Other information that will be required before an offer can be published are highlighted below. These settings are either set with createOffer, or they can be set with a subsequent updateOffer call: Inventory location Offer price Available quantity eBay listing category Referenced listing policy profiles to set payment, return, and fulfillment values/settings  Note: Though the includeCatalogProductDetails parameter is not required to be submitted in the request, the parameter defaults to true if omitted.If the call is successful, a unique offerId value is returned in the response. This value will be required for many other offer-related calls. Note that this call only stages an offer for publishing. The seller must run the publishOffer call to convert the offer to an active eBay listing. In addition to the authorization header, which is required for all eBay REST API calls, the createOffer call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.For those who prefer to create multiple offers (up to 25 at a time) with one call, the bulkCreateOffer method can be used.  

        :param EbayOfferDetailsWithKeys body: Details of the offer for the channel (required)
        :param str content_language: This request header sets the natural language that will be provided in the field values of the request payload. (required)
        :return: OfferResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'create_offer', SellInventoryException, True, ['sell.inventory', 'offer'], (body, content_language), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_delete_offer(self, offer_id, **kwargs):  # noqa: E501
        """delete_offer  

        If used against an unpublished offer, this call will permanently delete that offer. In the case of a published offer (or live eBay listing), a successful call will either end the single-variation listing associated with the offer, or it will remove that product variation from the eBay listing and also automatically remove that product variation from the inventory item group. In the case of a multiple-variation listing, the deleteOffer will not remove the product variation from the listing if that variation has one or more sales. If that product variation has one or more sales, the seller can alternately just set the available quantity of that product variation to 0, so it is not available in the eBay search or View Item page, and then the seller can remove that product variation from the inventory item group at a later time.  

        :param str offer_id: The unique identifier of the offer to delete. The unique identifier of the offer (offerId) is passed in at the end of the call URI. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'delete_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_listing_fees(self, **kwargs):  # noqa: E501
        """get_listing_fees  

        This call is used to retrieve the expected listing fees for up to 250 unpublished offers. An array of one or more offerId values are passed in under the offers container. In the response payload, all listing fees are grouped by eBay marketplace, and listing fees per offer are not shown. A fees container will be returned for each eBay marketplace where the seller is selling the products associated with the specified offers.  Errors will occur if the seller passes in offerIds that represent published offers, so this call should be made before the seller publishes offers with the publishOffer.  

        :param OfferKeysWithId body: List of offers that needs fee information
        :return: FeesSummaryResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'get_listing_fees', SellInventoryException, True, ['sell.inventory', 'offer'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_offer(self, offer_id, **kwargs):  # noqa: E501
        """get_offer  

        This call retrieves a specific published or unpublished offer. The unique identifier of the offer (offerId) is passed in at the end of the call URI.The authorization header is the only required HTTP header for this call. See the HTTP request headers section for more information.  

        :param str offer_id: The unique identifier of the offer that is to be retrieved. (required)
        :return: EbayOfferDetailsWithAll
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'get_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_offers(self, **kwargs):  # noqa: E501
        """get_offers  

        This call retrieves all existing offers for the specified SKU value. The seller has the option of limiting the offers that are retrieved to a specific eBay marketplace, or to a listing format.Note: At this time, the same SKU value can not be offered across multiple eBay marketplaces, and the only supported listing format is fixed-price, so the marketplace_id and format query parameters currently do not have any practical use for this call.The authorization header is the only required HTTP header for this call. See the HTTP request headers section for more information.  

        :param str format: This enumeration value sets the listing format for the offer. This query parameter will be passed in if the seller only wants to see offers in this specified listing format.
        :param str limit: The value passed in this query parameter sets the maximum number of records to return per page of data. Although this field is a string, the value passed in this field should be a positive integer value. If this query parameter is not set, up to 100 records will be returned on each page of results.
        :param str marketplace_id: The unique identifier of the eBay marketplace. This query parameter will be passed in if the seller only wants to see the product's offers on a specific eBay marketplace.Note: At this time, the same SKU value can not be offered across multiple eBay marketplaces, so the marketplace_id query parameter currently does not have any practical use for this call.
        :param str offset: The value passed in this query parameter sets the page number to retrieve. Although this field is a string, the value passed in this field should be a integer value equal to or greater than 0. The first page of records has a value of 0, the second page of records has a value of 1, and so on. If this query parameter is not set, its value defaults to 0, and the first page of records is returned.
        :param str sku: The seller-defined SKU value is passed in as a query parameter. All offers associated with this product are returned in the response. Max length: 50.
        :return: Offers
        """
        try:
            return self._method_paged(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'get_offers', SellInventoryException, True, ['sell.inventory', 'offer'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_publish_offer(self, offer_id, **kwargs):  # noqa: E501
        """publish_offer  

        Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.This call is used to convert an unpublished offer into a published offer, or live eBay listing. The unique identifier of the offer (offerId) is passed in at the end of the call URI.For those who prefer to publish multiple offers (up to 25 at a time) with one call, the bulkPublishOffer method can be used. In the case of a multiple-variation listing, the publishOfferByInventoryItemGroup call should be used instead, as this call will convert all unpublished offers associated with an inventory item group into a multiple-variation listing.  

        :param str offer_id: The unique identifier of the offer that is to be published. (required)
        :return: PublishResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'publish_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_publish_offer_by_inventory_item_group(self, body, **kwargs):  # noqa: E501
        """publish_offer_by_inventory_item_group  

        Note: Please note that any eBay listing created using the Inventory API cannot be revised or relisted using the Trading API calls.Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.This call is used to convert all unpublished offers associated with an inventory item group into an active, multiple-variation listing. The unique identifier of the inventory item group (inventoryItemGroupKey) is passed in the request payload. All inventory items and their corresponding offers in the inventory item group must be valid (meet all requirements) for the publishOfferByInventoryItemGroup call to be completely successful. For any inventory items in the group that are missing required data or have no corresponding offers, the publishOfferByInventoryItemGroup will create a new multiple-variation listing, but any inventory items with missing required data/offers will not be in the newly-created listing. If any inventory items in the group to be published have invalid data, or one or more of the inventory items have conflicting data with one another, the publishOfferByInventoryItemGroup call will fail. Be sure to check for any error or warning messages in the call response for any applicable information about one or more inventory items/offers having issues.  

        :param PublishByInventoryItemGroupRequest body: The identifier of the inventory item group to publish and the eBay marketplace where the listing will be published is needed in the request payload. (required)
        :return: PublishResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'publish_offer_by_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_update_offer(self, body, content_language, offer_id, **kwargs):  # noqa: E501
        """update_offer  

        This call updates an existing offer. An existing offer may be in published state (active eBay listing), or in an unpublished state and yet to be published with the publishOffer call. The unique identifier (offerId) for the offer to update is passed in at the end of the call URI.  The updateOffer call does a complete replacement of the existing offer object, so all fields that make up the current offer object are required, regardless of whether their values changed.  Other information that is required before an unpublished offer can be published or before a published offer can be revised include: Inventory location Offer price Available quantity eBay listing category Referenced listing policy profiles to set payment, return, and fulfillment values/settings  Note: Though the includeCatalogProductDetails parameter is not required to be submitted in the request, the parameter defaults to true if omitted from both the updateOffer and the createOffer calls. If a value is specified in the updateOffer call, this value will be used.Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day.Note: Each listing can be revised up to 250 times in one calendar day. If this revision threshold is reached, the seller will be blocked from revising the item until the next calendar day. For published offers, the listingDescription field is also required to update the offer/eBay listing. For unpublished offers, this field is not necessarily required unless it is already set for the unpublished offer. In addition to the authorization header, which is required for all eBay REST API calls, the updateOffer call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.  

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
        """withdraw_offer  

        This call is used to end a single-variation listing that is associated with the specified offer. This call is used in place of the deleteOffer call if the seller only wants to end the listing associated with the offer but does not want to delete the offer object. With this call, the offer object remains, but it goes into the unpublished state, and will require a publishOffer call to relist the offer.To end a multiple-variation listing that is associated with an inventory item group, the withdrawOfferByInventoryItemGroup method can be used. This call only ends the multiple-variation listing associated with an inventory item group but does not delete the inventory item group object, nor does it delete any of the offers associated with the inventory item group, but instead all of these offers go into the unpublished state.  

        :param str offer_id: The unique identifier of the offer that is to be withdrawn. This value is passed into the path of the call URI. (required)
        :return: WithdrawResponse
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'withdraw_offer', SellInventoryException, True, ['sell.inventory', 'offer'], offer_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_withdraw_offer_by_inventory_item_group(self, body, **kwargs):  # noqa: E501
        """withdraw_offer_by_inventory_item_group  

        This call is used to end a multiple-variation eBay listing that is associated with the specified inventory item group. This call only ends multiple-variation eBay listing associated with the inventory item group but does not delete the inventory item group object. Similarly, this call also does not delete any of the offers associated with the inventory item group, but instead all of these offers go into the unpublished state. If the seller wanted to relist the multiple-variation eBay listing, they could use the publishOfferByInventoryItemGroup method.  

        :param WithdrawByInventoryItemGroupRequest body: The base request of the withdrawOfferByInventoryItemGroup call. (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.OfferApi, sell_inventory.ApiClient, 'withdraw_offer_by_inventory_item_group', SellInventoryException, True, ['sell.inventory', 'offer'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_create_or_replace_product_compatibility(self, body, content_language, sku, **kwargs):  # noqa: E501
        """create_or_replace_product_compatibility  

        This call is used by the seller to create or replace a list of products that are compatible with the inventory item. The inventory item is identified with a SKU value in the URI. Product compatibility is currently only applicable to motor vehicle parts and accessory categories, but more categories may be supported in the future.In addition to the authorization header, which is required for all eBay REST API calls, the createOrReplaceProductCompatibility call also requires the Content-Language header, that sets the natural language that will be used in the field values of the request payload. For US English, the code value passed in this header should be en-US. To view other supported Content-Language values, and to read more about all supported HTTP headers for eBay REST API calls, see the HTTP request headers topic in the Using eBay RESTful APIs document.  

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
        """delete_product_compatibility  

        This call is used by the seller to delete the list of products that are compatible with the inventory item that is associated with the compatible product list. The inventory item is identified with a SKU value in the URI. Product compatibility is currently only applicable to motor vehicle parts and accessory categories, but more categories may be supported in the future.  

        :param str sku: A SKU (stock keeping unit) is an unique identifier defined by a seller for a product (required)
        :return: None
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ProductCompatibilityApi, sell_inventory.ApiClient, 'delete_product_compatibility', SellInventoryException, True, ['sell.inventory', 'product_compatibility'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_inventory_get_product_compatibility(self, sku, **kwargs):  # noqa: E501
        """get_product_compatibility  

        This call is used by the seller to retrieve the list of products that are compatible with the inventory item. The SKU value for the inventory item is passed into the call URI, and a successful call with return the compatible vehicle list associated with this inventory item. Product compatibility is currently only applicable to motor vehicle parts and accessory categories, but more categories may be supported in the future.  

        :param str sku: A SKU (stock keeping unit) is an unique identifier defined by a seller for a product (required)
        :return: Compatibility
        """
        try:
            return self._method_single(sell_inventory.Configuration, '/sell/inventory/v1', sell_inventory.ProductCompatibilityApi, sell_inventory.ApiClient, 'get_product_compatibility', SellInventoryException, True, ['sell.inventory', 'product_compatibility'], sku, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_cancel_shipment(self, shipment_id, **kwargs):  # noqa: E501
        """cancel_shipment  

        This method cancels the shipment associated with the specified shipment ID and the associated shipping label is deleted. When you cancel a shipment, the totalShippingCost of the canceled shipment is refunded to the account established by the user's billing agreement.  Note that you cannot cancel a shipment if you have used the associated shipping label.  

        :param str shipment_id: This path parameter specifies the unique eBay-assigned ID of the shipment to be canceled. The shipmentId value is generated and returned by a call to createFromShippingQuote. (required)
        :return: Shipment
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'cancel_shipment', SellLogisticsException, True, ['sell.logistics', 'shipment'], shipment_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_create_from_shipping_quote(self, body, **kwargs):  # noqa: E501
        """create_from_shipping_quote  

        This method creates a \"shipment\" based on the shippingQuoteId and rateId values supplied in the request. The rate identified by the rateId value specifies the carrier and service for the package shipment, and the rate ID must be contained in the shipping quote identified by the shippingQuoteId value. Call createShippingQuote to retrieve a set of live shipping rates.  When you create a shipment, eBay generates a shipping label that you can download and use to ship your package.  In a createFromShippingQuote request, sellers can include a list of shipping options they want to add to the base service quoted in the selected rate. The list of available shipping options is specific to each quoted rate and if available, the options are listed in the rate container of the of the shipping quote.  In addition to a configurable return-to location and other details about the shipment, the response to this method includes:  The shipping carrier and service to be used for the package shipment A list of selected shipping options, if any The shipment tracking number The total shipping cost (the sum cost of the base shipping service and any added options) When you create a shipment, your billing agreement account is charged the sum of the baseShippingCost and the total cost of any additional shipping options you might have selected. Use the URL returned in labelDownloadUrl field, or call downloadLabelFile with the shipmentId value from the response, to download a shipping label for your package. Important! Sellers must set up their payment method with eBay before they can use this method to create a shipment and the associated shipping label.  

        :param CreateShipmentFromQuoteRequest body: The create shipment from quote request. (required)
        :return: Shipment
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'create_from_shipping_quote', SellLogisticsException, True, ['sell.logistics', 'shipment'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_download_label_file(self, shipment_id, **kwargs):  # noqa: E501
        """download_label_file  

        This method returns the shipping label file that was generated for the shipmentId value specified in the request. Call createFromShippingQuote to generate a shipment ID.  Use the Accept HTTP header to specify the format of the returned file. The default file format is a PDF file.   

        :param str shipment_id: This path parameter specifies the unique eBay-assigned ID of the shipment associated with the shipping label you want to download. The shipmentId value is generated and returned by a call to createFromShippingQuote. (required)
        :return: list[str]
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'download_label_file', SellLogisticsException, True, ['sell.logistics', 'shipment'], shipment_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_get_shipment(self, shipment_id, **kwargs):  # noqa: E501
        """get_shipment  

        This method retrieves the shipment details for the specified shipment ID. Call createFromShippingQuote to generate a shipment ID.  

        :param str shipment_id: This path parameter specifies the unique eBay-assigned ID of the shipment you want to retrieve. The shipmentId value is generated and returned by a call to createFromShippingQuote. (required)
        :return: Shipment
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShipmentApi, sell_logistics.ApiClient, 'get_shipment', SellLogisticsException, True, ['sell.logistics', 'shipment'], shipment_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_create_shipping_quote(self, body, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """create_shipping_quote  

        The createShippingQuote method returns a shipping quote  that contains a list of live \"rates.\"  Each rate represents an offer made by a shipping carrier for a specific service and each offer has a live quote for the base service cost. Rates have a time window in which they are \"live,\" and rates expire when their purchase window ends. If offered by the carrier, rates can include shipping options (and their associated prices), and users can add any offered shipping option to the base service should they desire.  Also, depending on the services required, rates can also include pickup and delivery windows.  Each rate is for a single package and is based on the following information: The shipping origin The shipping destination The package size (weight and dimensions)  Rates are identified by a unique eBay-assigned rateId and rates are based on price points, pickup and delivery time frames, and other user requirements. Because each rate offered must be compliant with the eBay shipping program, all rates reflect eBay-negotiated prices.  The various rates returned in a shipping quote offer the user a choice from which they can choose a shipping service that best fits their needs. Select the rate for your shipment and using the associated rateId, call createFromShippingQuote to create a shipment and generate a shipping label that you can use to ship the package.  

        :param ShippingQuoteRequest body: The request object for createShippingQuote. (required)
        :param str x_ebay_c_marketplace_id: This header parameter specifies the eBay marketplace for the shipping quote that is being created. For a list of valid values, refer to the section Marketplace ID Values in the Using eBay RESTful APIs guide. (required)
        :return: ShippingQuote
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShippingQuoteApi, sell_logistics.ApiClient, 'create_shipping_quote', SellLogisticsException, True, ['sell.logistics', 'shipping_quote'], (body, x_ebay_c_marketplace_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_logistics_get_shipping_quote(self, shipping_quote_id, **kwargs):  # noqa: E501
        """get_shipping_quote  

        This method retrieves the complete details of the shipping quote associated with the specified shippingQuoteId value.  A \"shipping quote\" pertains to a single specific package and contains a set of shipping \"rates\" that quote the cost to ship the package by different shipping carriers and services. The quotes are based on the package's origin, destination, and size.  Call createShippingQuote to create a shippingQuoteId.  

        :param str shipping_quote_id: This path parameter specifies the unique eBay-assigned ID of the shipping quote you want to retrieve. The shippingQuoteId value is generated and returned by a call to createShippingQuote. (required)
        :return: ShippingQuote
        """
        try:
            return self._method_single(sell_logistics.Configuration, '/sell/logistics/v1_beta', sell_logistics.ShippingQuoteApi, sell_logistics.ApiClient, 'get_shipping_quote', SellLogisticsException, True, ['sell.logistics', 'shipping_quote'], shipping_quote_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_create_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_create_ads_by_inventory_reference  

        This method adds multiple listings that are managed with the Inventory API to an existing Promoted Listings campaign.For Promoted Listings Standard (PLS) campaigns using the Cost Per Sale (CPS) model, bulk ads may be directly created for the listing.For each listing specified in the request, this method:Creates an ad for the listing. Sets the bid percentage (also known as the ad rate) for the ads created. Associates the ads created with the specified campaign.To create ads for a listing, specify their inventoryReferenceId and inventoryReferenceType, plus the bidPercentage for the ad in the payload of the request. Specify the campaign to which you want to associate the ads using the campaign_id path parameter.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.Use createCampaign to create a new campaign and use getCampaigns to get a list of existing campaigns.  

        :param BulkCreateAdsByInventoryReferenceRequest body: The container for the bulk request to create ads for eBay inventory reference IDs. eBay inventory reference IDs are seller-defined IDs used by theInventory API. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created. Get a seller's campaign IDs by calling getCampaigns. (required)
        :return: BulkCreateAdsByInventoryReferenceResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_create_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_create_ads_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_create_ads_by_listing_id  

        This method adds multiple listings to an existing Promoted Listings campaign using listingId values generated by the Trading API or Inventory API, or using values generated by an ad group ID.For Promoted Listings Standard (PLS) campaigns using the Cost Per Sale (CPS) funding model, bulk ads may be directly created for the listing.For each listing ID specified in the request, this method: Creates an ad for the listing. Sets the bid percentage (also known as the ad rate) for the ad. Associates the ad with the specified campaign.To create an ad for a listing, specify its listingId, plus the bidPercentage for the ad in the payload of the request. Specify the campaign to associate the ads with using the campaign_id path parameter. Listing IDs are generated by eBay when a seller creates listings with the Trading API.You can specify a maximum of 500 listings per call and each campaign can have ads for a maximum of 50,000 items. Be aware when using this call that each variation in a multiple-variation listing creates an individual ad.For Promoted Listings Advanced (PLA) campaigns using the Cost Per Click (CPC) funding model, an ad group must be created first. If no ad group has been created for the campaign, ads cannot be created.For the ad group specified in the request, this method associates the ad with the specified ad group.To create an ad for an ad group, specify the name of the ad group plus the defaultBid for the ad in the payload of the request. Specify the campaign to associate the ads with using the campaign_id path parameter. Ad groups are generated using the createAdGroup  method. You can specify one or more ad groups per campaign.Use createCampaign to create a new campaign and use getCampaigns to get a list of existing campaigns.  

        :param BulkCreateAdRequest body: The container for the bulk request to create ads for eBay listing IDs. eBay listing IDs are generated by the Trading API and Inventory API when the listing is created on eBay. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling getCampaigns. (required)
        :return: BulkAdResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_create_ads_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_delete_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_delete_ads_by_inventory_reference  

        This method works with listings created with the Inventory API.The method deletes a set of ads, as specified by a list of inventory reference IDs, from the specified campaign. Inventory reference IDs are seller-defined IDs that are used with the Inventory API.Pass the campaign_id as a path parameter and populate the payload with a list of inventoryReferenceId and inventoryReferenceType pairs that you want to delete.Get the campaign IDs for a seller by calling getCampaigns and call getAds to get a list of the seller's inventory reference IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param BulkDeleteAdsByInventoryReferenceRequest body: This request works with listings created via the Inventory API.The request is to delete a set of ads in bulk, as specified by a list of inventory reference IDs from the specified campaign. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling getCampaigns. (required)
        :return: BulkDeleteAdsByInventoryReferenceResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_delete_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_delete_ads_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_delete_ads_by_listing_id  

        This method works with listing IDs created with either the Trading API or the Inventory API.The method deletes a set of ads, as specified by a list of listingID values from a Promoted Listings campaign. A listing ID value is generated by eBay when a seller creates a listing with either the Trading API and Inventory API.Pass the campaign_id as a path parameter and populate the payload with the set of listing IDs that you want to delete.Get the campaign IDs for a seller by calling getCampaigns and call getAds to get a list of the seller's inventory reference IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.When using the CPC funding model, use the bulkUpdateAdsStatusByListingId method to change the status of ads to ARCHIVED.  

        :param BulkDeleteAdRequest body: This request object defines the fields for the bulkDeleteAdsByListingId request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling getCampaigns. (required)
        :return: BulkDeleteAdResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_delete_ads_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_ads_bid_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_ads_bid_by_inventory_reference  

        This method works with listings created with either the Trading API or the Inventory API.  The method updates the bidPercentage values for a set of ads associated with the specified campaign. Specify the campaign_id as a path parameter and supply a set of listing IDs with their associated updated bidPercentage values in the request body. An eBay listing ID is generated when a listing is created with the Trading API. Get the campaign IDs for a seller by calling getCampaigns and call getAds to get a list of the seller's inventory reference IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param BulkCreateAdsByInventoryReferenceRequest body: This request object defines the fields for the BulkCreateAdsByInventoryReference request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling getCampaigns. (required)
        :return: BulkUpdateAdsByInventoryReferenceResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_update_ads_bid_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_ads_bid_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_ads_bid_by_listing_id  

        This method works with listings created with either the Trading API or the Inventory API.  The method updates the bidPercentage values for a set of ads associated with the specified campaign. Specify the campaign_id as a path parameter and supply a set of listing IDs with their associated updated bidPercentage values in the request body. An eBay listing ID is generated when a listing is created with the Trading API. Get the campaign IDs for a seller by calling getCampaigns and call getAds to get a list of the seller's inventory reference IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param BulkCreateAdRequest body: This request object defines the fields for the BulkCreateAdsByListingId request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that's generated when a campaign is created. Get a seller's campaign IDs by calling getCampaigns. (required)
        :return: BulkAdUpdateResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_update_ads_bid_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_ads_status(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_ads_status  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method works with listings created with either the Trading API or the Inventory API.This method updates the status of ads in bulk.Specify the campaign_id you want to update as a URI parameter, and configure the adGroupStatus in the request payload.  

        :param BulkUpdateAdStatusRequest body: The bulk request to update the ads. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: BulkAdUpdateStatusResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_update_ads_status', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_ads_status_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_ads_status_by_listing_id  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method works with listings created with either the Trading API or the Inventory API.The method updates the status of ads in bulk, based on listing ID values.Specify the campaign_id as a path parameter and supply a set of listing IDs with their updated adStatus values in the request body. An eBay listing ID is generated when a listing is created with the Trading API.Get the campaign IDs for a seller by calling getCampaigns and call getAds to retrieve a list of seller inventory reference IDs.  

        :param BulkUpdateAdStatusByListingIdRequest body: The bulk request to update ads. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: BulkAdUpdateStatusByListingIdResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'bulk_update_ads_status_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_ad_by_listing_id(self, body, campaign_id, **kwargs):  # noqa: E501
        """create_ad_by_listing_id  

        This method adds a listing to an existing Promoted Listings campaign using a listingId value generated by the Trading API or Inventory API, or using a value generated by an ad group ID. For Promoted Listings Standard (PLS) campaigns using the Cost Per Sale (CPS) funding model, an ad may be directly created for the listing.For the listing ID specified in the request, this method: Creates an ad for the listing. Sets the bid percentage (also known as the ad rate) for the ad. Associates the ad with the specified campaign. To create an ad for a listing, specify its listingId, plus the bidPercentage for the ad in the payload of the request. Specify the campaign to associate the ad with using the campaign_id path parameter. Listing IDs are generated by eBay when a seller creates listings with the Trading API.For Promoted Listings Advanced (PLA) campaigns using the Cost Per Click (CPC) funding model, an ad group must be created first. If no ad group has been created for the campaign, an ad cannot be created.For the ad group specified in the request, this method associates the ad with the specified ad group.To create an ad for an ad group, specify the name of the ad group in the payload of the request. Specify the campaign to associate the ads with using the campaign_id path parameter. Ad groups are generated using the createAdGroup method. You can specify one or more ad groups per campaign.Use createCampaign to create a new campaign and use getCampaigns to get a list of existing campaigns.This call has no response payload. If the ad is successfully created, a 201 Created HTTP status code and the getAd URI of the ad are returned in the location header.  

        :param CreateAdRequest body: This request object defines the fields used in the createAdByListingId request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'create_ad_by_listing_id', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """create_ads_by_inventory_reference  

        This method adds a listing that is managed with the Inventory API to an existing Promoted Listings campaign.For Promoted Listings Standard (PLS) campaigns using the Cost Per Sale (CPS) funding model, an ad may be directly created for the listing.For each listing specified in the request, this method:Creates an ad for the listing. Sets the bid percentage (also known as the ad rate) for the ads created. Associates the created ad with the specified campaign.To create an ad for a listing, specify its inventoryReferenceId and inventoryReferenceType, plus the bidPercentage for the ad in the payload of the request. Specify the campaign to associate the ad with using the campaign_id path parameter.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.Use createCampaign to create a new campaign and use getCampaigns to get a list of existing campaigns.  

        :param CreateAdsByInventoryReferenceRequest body: This request object defines the fields used in the createAdsByInventoryReference request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: AdReferences
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'create_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_ad(self, ad_id, campaign_id, **kwargs):  # noqa: E501
        """delete_ad  

        This method removes the specified ad from the specified campaign.Pass the ID of the ad to delete with the ID of the campaign associated with the ad as path parameters to the call.Call getCampaigns to get the current list of the seller's campaign IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.When using the CPC funding model, use the bulkUpdateAdsStatusByListingId method to change the status of ads to ARCHIVED.  

        :param str ad_id: Identifier of an ad. This ID was generated when the ad was created. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'delete_ad', SellMarketingException, True, ['sell.marketing', 'ad'], (ad_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_ads_by_inventory_reference(self, body, campaign_id, **kwargs):  # noqa: E501
        """delete_ads_by_inventory_reference  

        This method works with listings that are managed with the Inventory API.  The method deletes ads using a list of seller-defined inventory reference IDs, used with the Inventory API, that are associated with the specified campaign ID. Specify the campaign ID (as a path parameter) and a list of inventoryReferenceId and inventoryReferenceType pairs to be deleted. Call getCampaigns to get a list of the seller's current campaign IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.When using the CPC funding model, use the bulkUpdateAdsStatusByInventoryReference method to change the status of ads to ARCHIVED.  

        :param DeleteAdsByInventoryReferenceRequest body: This request object defines the fields for the deleteAdsByInventoryReference request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: AdIds
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'delete_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ad(self, ad_id, campaign_id, **kwargs):  # noqa: E501
        """get_ad  

        This method retrieves the specified ad from the specified campaign.  In the request, supply the campaign_id and ad_id as path parameters. Call getCampaigns to retrieve a list of the seller's current campaign IDs and call getAds to retrieve their current ad IDs.  

        :param str ad_id: A unique identifier for an ad. This ID is generated when the ad is created. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: Ad
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'get_ad', SellMarketingException, True, ['sell.marketing', 'ad'], (ad_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ads(self, campaign_id, **kwargs):  # noqa: E501
        """get_ads  

        This method retrieves Promoted Listings ads that are associated with listings created with either the Trading API or the Inventory API. The method retrieves ads related to the specified campaign. Specify the Promoted Listings campaign to target with the campaign_id path parameter. Because of the large number of possible results, you can use query parameters to paginate the result set by specifying a limit, which dictates how many ads to return on each page of the response. You can also specify how many ads to skip in the result set before returning the first result using the offset path parameter. Call getCampaigns to retrieve the current campaign IDs for the seller.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str ad_group_ids: A comma-separated list of ad group IDs. The results will be filtered to only include active ads for these ad groups. Call getAdGroups to retrieve the ad group ID for the ad group.Note: This field only applies to the Cost Per Click (CPC) funding model; it does not apply to the Cost Per Sale (CPS) funding model.
        :param str ad_status: A comma-separated list of ad statuses. The results will be filtered to only include the given statuses of the ad. If none are provided, all ads are returned.
        :param str limit: Specifies the maximum number of ads to return on a page in the paginated response. Default: 10 Maximum: 500
        :param str listing_ids: A comma-separated list of listing IDs. The response includes only active ads (ads associated with a RUNNING campaign). The results do not include listing IDs that are excluded by other conditions.
        :param str offset: Specifies the number of ads to skip in the result set before returning the first ad in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: AdPagedCollectionResponse
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'get_ads', SellMarketingException, True, ['sell.marketing', 'ad'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ads_by_inventory_reference(self, campaign_id, inventory_reference_id, inventory_reference_type, **kwargs):  # noqa: E501
        """get_ads_by_inventory_reference  

        This method retrieves Promoted Listings ads associated with listings that are managed with the Inventory API from the specified campaign.Supply the campaign_id as a path parameter and use query parameters to specify the inventory_reference_id and inventory_reference_type pairs.In the Inventory API, an inventory reference ID is either a seller-defined SKU value or an inventoryItemGroupKey (a seller-defined ID for an inventory item group, which is an entity that's used in the Inventory API to create a multiple-variation listing). To indicate a listing managed by the Inventory API, you must always specify both an inventory_reference_id and the associated inventory_reference_type.Call getCampaigns to retrieve all of the seller's the current campaign IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str inventory_reference_id: The inventory reference ID associated with the ad you want returned. A seller's inventory reference ID is the ID of either a listing or the ID of an inventory item group (the parent of a multi-variation listing, such as a shirt that is available in multiple sizes and colors). You must always supply in both an inventory_reference_id and an inventory_reference_type. (required)
        :param str inventory_reference_type: The type of the inventory reference ID. Set this value to either INVENTORY_ITEM (a single listing) or INVENTORY_ITEM_GROUP (a multi-variation listing). You must always pass in both an inventory_reference_id and an inventory_reference_type.  (required)
        :return: Ads
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'get_ads_by_inventory_reference', SellMarketingException, True, ['sell.marketing', 'ad'], (campaign_id, inventory_reference_id, inventory_reference_type), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_bid(self, body, ad_id, campaign_id, **kwargs):  # noqa: E501
        """update_bid  

        This method updates the bid percentage (also known as the \"ad rate\") for the specified ad in the specified campaign. In the request, supply the campaign_id and ad_id as path parameters, and supply the new bidPercentage value in the payload of the call. Call getCampaigns to retrieve a seller's current campaign IDs and call getAds to get their ad IDs.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param UpdateBidPercentageRequest body: This type defines the fields for the updateBid request. (required)
        :param str ad_id: A unique eBay-assigned ID for an ad that's generated when an ad is created. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdApi, sell_marketing.ApiClient, 'update_bid', SellMarketingException, True, ['sell.marketing', 'ad'], (body, ad_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_ad_group(self, body, campaign_id, **kwargs):  # noqa: E501
        """create_ad_group  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method adds an ad group to an existing PLA campaign that uses the Cost Per Click (CPC) funding model.To create an ad group for a campaign, specify the defaultBid for the ad group in the payload of the request. Then specify the campaign to which the ad group should be associated using the campaign_id path parameter.Each campaign can have one or more associated ad groups.  

        :param CreateAdGroupRequest body: This type defines the fields for the createAdGroup request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdGroupApi, sell_marketing.ApiClient, 'create_ad_group', SellMarketingException, True, ['sell.marketing', 'ad_group'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ad_group(self, ad_group_id, campaign_id, **kwargs):  # noqa: E501
        """get_ad_group  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method retrieves the details of a specified ad group, such as the ad group’s default bid and status.In the request, specify the campaign_id and ad_group_id as path parameters.Call getCampaigns to retrieve a list of the current campaign IDs for a seller and call getAdGroups for the ad group ID of the ad group you wish to retrieve.  

        :param str ad_group_id: The ID of the ad group that shall be retrieved. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: AdGroup
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdGroupApi, sell_marketing.ApiClient, 'get_ad_group', SellMarketingException, True, ['sell.marketing', 'ad_group'], (ad_group_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_ad_groups(self, campaign_id, **kwargs):  # noqa: E501
        """get_ad_groups  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method retrieves ad groups for the specified campaigns.Each campaign can only have one ad group.In the request, supply the campaign_ids as path parameters.Call getCampaigns to retrieve a list of the current campaign IDs for a seller.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str ad_group_status: A comma-separated list of ad group statuses. The results will be filtered to only include the given statuses of the ad group.The results might not include these ad groups if other search conditions exclude them.
        :param str limit: The number of results, from the current result set, to be returned in a single page.
        :param str offset: The number of results that will be skipped in the result set. This is used with the limit field to control the pagination of the output.For example, if the offset is set to 0 and the limit is set to 10, the method will retrieve items 1 through 10 from the list of items returned. If the offset is set to 10 and the limit is set to 10, the method will retrieve items 11 through 20 from the list of items returned.Default: 0
        :return: AdGroupPagedCollectionResponse
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdGroupApi, sell_marketing.ApiClient, 'get_ad_groups', SellMarketingException, True, ['sell.marketing', 'ad_group'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_suggest_bids(self, body, ad_group_id, campaign_id, **kwargs):  # noqa: E501
        """suggest_bids  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method allows sellers to retrieve the suggested bids for input keywords and match type.  

        :param TargetedBidRequest body: The data requested to retrieve the suggested bids. (required)
        :param str ad_group_id: The ID of the ad group containing the keywords for which the bid suggestions will be provided. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: TargetedBidsPagedCollection
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdGroupApi, sell_marketing.ApiClient, 'suggest_bids', SellMarketingException, True, ['sell.marketing', 'ad_group'], (body, ad_group_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_suggest_keywords(self, ad_group_id, campaign_id, **kwargs):  # noqa: E501
        """suggest_keywords  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method allows sellers to retrieve a list of keyword ideas to be targeted for Promoted Listings campaigns.  

        :param str ad_group_id: The ID of the ad group for which the keyword suggestions will be provided. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param TargetedKeywordRequest body: The required data to retrieve suggested keywords.
        :return: TargetedKeywordsPagedCollection
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdGroupApi, sell_marketing.ApiClient, 'suggest_keywords', SellMarketingException, True, ['sell.marketing', 'ad_group'], (ad_group_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_ad_group(self, body, ad_group_id, campaign_id, **kwargs):  # noqa: E501
        """update_ad_group  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method updates the ad group associated with a campaign.With this method, you can modify the default bid for the ad group, change the state of the ad group, or change the name of the ad group. Pass the ad_group_id you want to update as a URI parameter, and configure the adGroupStatus and defaultBid in the request payload.Call getAdGroup to retrieve the current default bid and status of the ad group that you would like to update.  

        :param UpdateAdGroupRequest body: This type defines the fields for the UpdateAdGroup request. (required)
        :param str ad_group_id: The ID of the ad group that shall be updated. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdGroupApi, sell_marketing.ApiClient, 'update_ad_group', SellMarketingException, True, ['sell.marketing', 'ad_group'], (body, ad_group_id, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report(self, report_id, **kwargs):  # noqa: E501
        """get_report  

        This call downloads the report as specified by the report_id path parameter.  Call createReportTask to schedule and generate a Promoted Listings report. All date values are returned in UTC format (yyyy-MM-ddThh:mm:ss.sssZ).Note: The reporting of some data related to sales and ad-fees may require a 72-hour (maximum) adjustment period which is often referred to as the Reconciliation Period. Such adjustment periods should, on average, be minimal. However, at any given time, the payments tab may be used to view those amounts that have actually been charged.  

        :param str report_id: The unique ID of the Promoted Listings report you want to get. This ID is generated by eBay when you run a report task with a call to createReportTask. Get all the seller's report IDs by calling getReportTasks. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportApi, sell_marketing.ApiClient, 'get_report', SellMarketingException, True, ['sell.marketing', 'ad_report'], report_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_metadata(self, **kwargs):  # noqa: E501
        """get_report_metadata  

        This call retrieves information that details the fields used in each of the Promoted Listings reports. Use the returned information to configure the different types of Promoted Listings reports.The request for this method does not use a payload or any URI parameters.Note: The reporting of some data related to sales and ad-fees may require a 72-hour (maximum) adjustment period which is often referred to as the Reconciliation Period. Such adjustment periods should, on average, be minimal. However, at any given time, the payments tab may be used to view those amounts that have actually been charged.  

        :return: ReportMetadatas
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportMetadataApi, sell_marketing.ApiClient, 'get_report_metadata', SellMarketingException, False, ['sell.marketing', 'ad_report_metadata'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_metadata_for_report_type(self, report_type, **kwargs):  # noqa: E501
        """get_report_metadata_for_report_type  

        This call retrieves metadata that details the fields used by a specific Promoted Listings report type. Use the report_type path parameter to indicate metadata to retrieve.This method does not use a request payload.Note: The reporting of some data related to sales and ad-fees may require a 72-hour (maximum) adjustment period which is often referred to as the Reconciliation Period. Such adjustment periods should, on average, be minimal. However, at any given time, the payments tab may be used to view those amounts that have actually been charged.  

        :param str report_type: The name of the report type whose metadata you want to retrieve.Tip: For details about available report types and their descriptions, refer to the ReportTypeEnum. (required)
        :return: ReportMetadata
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportMetadataApi, sell_marketing.ApiClient, 'get_report_metadata_for_report_type', SellMarketingException, False, ['sell.marketing', 'ad_report_metadata'], report_type, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_report_task(self, body, **kwargs):  # noqa: E501
        """create_report_task  

        Note: Using multiple funding models in one report is deprecated. If multiple funding models are used, a Warning will be returned in a header. This functionality will be decommissioned on April 3, 2023. See API Deprecation Status for details.This method creates a report task, which generates a Promoted Listings report based on the values specified in the call.The report is generated based on the criteria you specify, including the report type, the report's dimensions and metrics, the report's start and end dates, the listings to include in the report, and more. Metrics are the quantitative measurements in the report while dimensions specify the attributes of the data included in the reports.When creating a report task, you can specify the items you want included in the report. The items you specify, using either listingId or inventoryReference values, must be in a Promoted Listings campaign for them to be included in the report.For details on the required and optional fields for each report type, see Promoted Listings reporting.This call returns the URL to the report task in the Location response header, and the URL includes the report-task ID.Reports often take time to generate and it's common for this call to return an HTTP status of 202, which indicates the report is being generated. Call getReportTasks (or getReportTask with the report-task ID) to determine the status of a Promoted Listings report. When a report is complete, eBay sets its status to SUCCESS and you can download it using the URL returned in the reportHref field of the getReportTask call. Report files are tab-separated value gzip files with a file extension of .tsv.gz.Note: The reporting of some data related to sales and ad-fees may require a 72-hour (maximum) adjustment period which is often referred to as the Reconciliation Period. Such adjustment periods should, on average, be minimal. However, at any given time, the payments tab may be used to view those amounts that have actually been charged.Note: This call fails if you don't submit all the required fields for the specified report type. Fields not supported by the specified report type are ignored. Call getReportMetadata to retrieve a list of the fields you need to configure for each Promoted Listings report type.  

        :param CreateReportTask body: The container for the fields that define the report task. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'create_report_task', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_report_task(self, report_task_id, **kwargs):  # noqa: E501
        """delete_report_task  

        This call deletes the report task specified by the report_task_id path parameter. This method also deletes any reports generated by the report task.  Report task IDs are generated by eBay when you call createReportTask. Get a complete list of a seller's report-task IDs by calling getReportTasks.  

        :param str report_task_id: A unique eBay-assigned ID for the report task that's generated when the report task is created by a call to createReportTask. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'delete_report_task', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], report_task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_task(self, report_task_id, **kwargs):  # noqa: E501
        """get_report_task  

        This call returns the details of a specific Promoted Listings report task, as specified by the report_task_id path parameter. The report task includes the report criteria (such as the report dimensions, metrics, and included listing) and the report-generation rules (such as starting and ending dates for the specified report task). Report-task IDs are generated by eBay when you call createReportTask. Get a complete list of a seller's report-task IDs by calling getReportTasks.  

        :param str report_task_id: A unique eBay-assigned ID for the report task that's generated when the report task is created by a call to createReportTask. (required)
        :return: ReportTask
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'get_report_task', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], report_task_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_report_tasks(self, **kwargs):  # noqa: E501
        """get_report_tasks  

        This method returns information on all the existing report tasks related to a seller. Use the report_task_statuses query parameter to control which reports to return. You can paginate the result set by specifying a limit, which dictates how many report tasks to return on each page of the response. Use the offset parameter to specify how many reports to skip in the result set before returning the first result.  

        :param str limit: Specifies the maximum number of report tasks to return on a page in the paginated response.  Default: 10Maximum: 500
        :param str offset: Specifies the number of report tasks to skip in the result set before returning the first report in the paginated response.  Combine offset with the limit query parameter to control the reports returned in the response. For example, if you supply an offset of 0 and a limit of 10, the response contains the first 10 reports from the complete list of report tasks retrieved by the call. If offset is 10 and limit is 10, the first page of the response contains reports 11-20 from the complete result set. Default: 0
        :param str report_task_statuses: This parameter filters the returned report tasks by their status. Supply a comma-separated list of the report statuses you want returned. The results are filtered to include only the report statuses you specify.Note: The results might not include some report tasks if other search conditions exclude them.Valid values:     PENDING    SUCCESS    FAILED
        :return: ReportTaskPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.AdReportTaskApi, sell_marketing.ApiClient, 'get_report_tasks', SellMarketingException, True, ['sell.marketing', 'ad_report_task'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_clone_campaign(self, body, campaign_id, **kwargs):  # noqa: E501
        """clone_campaign  

        This method clones (makes a copy of) the specified campaign's campaign criterion. The campaign criterion is a container for the fields that define the criteria for a rule-based campaign.To clone a campaign, supply the campaign_id as a path parameter in your call. There is no request payload. The ID of the newly-cloned campaign is returned in the Location response header.Call getCampaigns to retrieve a seller's current campaign IDs. Requirement: In order to clone a campaign, the campaignStatus must be ENDED and the campaign must define a set of selection rules (it must be a rules-based campaign).Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param CloneCampaignRequest body: This type defines the fields for a clone campaign request. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created. This ID is the campaign ID of the campaign being cloned.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'clone_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_campaign(self, body, **kwargs):  # noqa: E501
        """create_campaign  

        This method creates a Promoted Listings ad campaign. A Promoted Listings campaign is the structure into which you place the ads or ad group for the listings you want to promote. Identify the items you want to place into a campaign either by \"key\" or by \"rule\" as follows: Rules-based campaigns – A rules-based campaign adds items to the campaign according to the criteria you specify in your call to createCampaign. You can set the autoSelectFutureInventory request field to true so that after your campaign launches, eBay will regularly assess your new, revised, or newly-eligible listings to determine whether any should be added or removed from your campaign according to the rules you set. If there are, eBay will add or remove them automatically on a daily basis. Key-based campaigns – Add items to an existing campaign using either listing ID values or Inventory Reference values: Add listingId values to an existing campaign by calling either createAdByListingID or bulkCreateAdsByListingId. Add inventoryReference values to an existing campaign by calling either createAdByInventoryReference or bulkCreateAdsByInventoryReference.Add an ad group to an existing campaign by calling createAdGroup.Note: No matter how you add items to a Promoted Listings campaign, each campaign can contain ads for a maximum of 50,000 items. If a rules-based campaign identifies more than 50,000 items, ads are created for only the first 50,000 items identified by the specified criteria, and ads are not created for the remaining items. Creating a campaign To create a basic campaign, supply: The user-defined campaign name The start date (and optionally the end date) of the campaign The eBay marketplace on which the campaign is hosted Details on the campaign funding model The campaign funding model specifies how the Promoted Listings fee is calculated. Currently, the supported funding models are COST_PER_SALE and COST_PER_CLICK. For complete information on how the fee is calculated and when it applies, see Promoted Listings fees. If you populate the campaignCriterion object in your createCampaign request, campaign \"ads\" are created by \"rule\" for the listings that meet the criteria you specify, and these ads are associated with the newly created campaign. For details on creating Promoted Listings campaigns and how to select the items to be included in your campaigns, see Promoted Listings campaign creation. For recommendations on which listings are prime for a Promoted Listings ad campaign and to get guidance on how to set the bidPercentage field, see Using the Recommendation API to help configure campaigns. Tip: See Promoted Listings requirements and restrictions for the details on the marketplaces that support Promoted Listings via the API. See Promoted Listings restrictions for details about campaign limitations and restrictions.  

        :param CreateCampaignRequest body: This type defines the fields for the create campaign request. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'create_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """delete_campaign  

        This method deletes the campaign specified by the campaign_id query parameter.Note:  You can only delete campaigns that have ended.Call getCampaigns to retrieve the campaign_id and the campaign status (RUNNING, PAUSED, ENDED, and so on) for all the seller's campaigns.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'delete_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_end_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """end_campaign  

        This method ends an active (RUNNING) or paused campaign. Specify the campaign you want to end by supplying its campaign ID in a query parameter.  Call getCampaigns to retrieve the campaign_id and the campaign status (RUNNING, PAUSED, ENDED, and so on) for all the seller's campaigns.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'end_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_find_campaign_by_ad_reference(self, **kwargs):  # noqa: E501
        """find_campaign_by_ad_reference  

        This method retrieves the campaigns containing the listing that is specified using either a listing ID, or an inventory reference ID and inventory reference type pair. The request accepts either a listing_id, or an inventory_reference_id and inventory_reference_type pair, as used in the Inventory API.eBay listing IDs are generated by either the Trading API or the Inventory API when you create a listing.An inventory reference ID can be either a seller-defined SKU or inventoryItemGroupKey, as specified in the Inventory API.Note: This method only applies to the Cost Per Sale (CPS) funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param str inventory_reference_id: The seller's inventory reference ID of the listing to be used to find the campaign in which it is associated.  This will either be a seller-defined SKU value or inventory item group ID, depending on the reference type specified. You must always pass in both  inventory_reference_id and inventory_reference_type.
        :param str inventory_reference_type: The type of the seller's inventory reference ID, which is a listing or group of items. You must always pass in both inventory_reference_id and inventory_reference_type.
        :param str listing_id: Identifier of the eBay listing associated with the ad.
        :return: Campaigns
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'find_campaign_by_ad_reference', SellMarketingException, True, ['sell.marketing', 'campaign'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """get_campaign  

        This method retrieves the details of a single campaign, as specified with the campaign_id query parameter.  This method returns all the details of a campaign (including the campaign's the selection rules), except the for the listing IDs or inventory reference IDs included in the campaign. These IDs are returned by getAds. Call getCampaigns to retrieve a list of the seller's campaign IDs.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: Campaign
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'get_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_campaign_by_name(self, campaign_name, **kwargs):  # noqa: E501
        """get_campaign_by_name  

        This method retrieves the details of a single campaign, as specified with the campaign_name query parameter. Note that the campaign name you specify must be an exact, case-sensitive match of the name of the campaign you want to retrieve.Call getCampaigns to retrieve a list of the seller's campaign names.  

        :param str campaign_name: The name of the campaign. (required)
        :return: Campaign
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'get_campaign_by_name', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_name, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_campaigns(self, **kwargs):  # noqa: E501
        """get_campaigns  

        This method retrieves the details for all of the seller's defined campaigns. Request parameters can be used to retrieve a specific campaign, such as the campaign's name, the start and end date, the status, and the funding model (Cost Per Sale (CPS) or Cost Per Click (CPC). You can filter the result set by a campaign name, end date range, start date range, or campaign status. You can also paginate the records returned from the result set using the limit query parameter, and control which records to return using the  offset parameter.  

        :param str campaign_name: Specifies the campaign name. The results are filtered to include only the campaign by the specified name.Note: The results might be null if other filters exclude the campaign with this name. Maximum:  1 campaign name
        :param str campaign_status: Include this filter and input a specific campaign status to retrieve campaigns currently in that state. Note: The results might not include all the campaigns with this status if other filters exclude them. Valid values: See CampaignStatusEnum Maximum:  1 status
        :param str end_date_range: Specifies the range of a campaign's end date. The results are filtered to include only campaigns with an end date that is within specified range. Valid format (UTC):  yyyy-MM-ddThh:mm:ssZ..yyyy-MM-ddThh:mm:ssZ   (campaign ends within this range)yyyy-MM-ddThh:mm:ssZ.. (campaign ends on or after this date)..yyyy-MM-ddThh:mm:ssZ  (campaign ends on or before this date)2016-09-08T00:00.00.000Z..2016-09-09T00:00:00Z (campaign ends on September 08, 2016) Note: The results might not include all the campaigns ending on this date if other filters exclude them.
        :param str funding_strategy: Specifies the funding strategy for the campaign.The results will be filtered to only include campaigns with the specified funding model. If not specified, all campaigns matching the other filter parameters will be returned. The results might not include these campaigns if other search conditions exclude them.Valid Values:COST_PER_SALECOST_PER_CLICK
        :param str limit: Specifies the maximum number of campaigns to return on a page in the paginated response. Default: 10 Maximum:  500
        :param str offset: Specifies the number of campaigns to skip in the result set before returning the first report in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :param str start_date_range: Specifies the range of a campaign's start date in which to filter the results. The results are filtered to include only campaigns with a start date that is equal to this date or is within specified range.Valid format (UTC):  yyyy-MM-ddThh:mm:ssZ..yyyy-MM-ddThh:mm:ssZ (starts within this range)yyyy-MM-ddThh:mm:ssZ (campaign starts on or after this date)..yyyy-MM-ddThh:mm:ssZ (campaign starts on or before this date)2016-09-08T00:00.00.000Z..2016-09-09T00:00:00Z (campaign starts on September 08, 2016)Note: The results might not include all the campaigns with this start date if other filters exclude them.
        :return: CampaignPagedCollectionResponse
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'get_campaigns', SellMarketingException, True, ['sell.marketing', 'campaign'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_pause_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """pause_campaign  

        This method pauses an active (RUNNING) campaign.  You can restart the campaign by calling resumeCampaign, as long as the campaign's end date is in the future. Note:  The listings associated with a paused campaign cannot be added into another campaign. Call getCampaigns to retrieve the campaign_id and the campaign status (RUNNING, PAUSED, ENDED, and so on) for all the seller's campaigns.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'pause_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_resume_campaign(self, campaign_id, **kwargs):  # noqa: E501
        """resume_campaign  

        This method resumes a paused campaign, as long as its end date is in the future. Supply the campaign_id for the campaign you want to restart as a query parameter in the request.  Call getCampaigns to retrieve the campaign_id and the campaign status (RUNNING, PAUSED, ENDED, and so on) for all the seller's campaigns.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'resume_campaign', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_suggest_items(self, campaign_id, **kwargs):  # noqa: E501
        """suggest_items  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method allows sellers to obtain ideas for listings, which can be targeted for Promoted Listings campaigns.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str category_ids: Specifies the category ID that is used to limit the results. This refers to an exact leaf category (the lowest level in that category and has no children). This field can have one category ID, or a comma-separated list of IDs. To return all category IDs, set to null. Maximum:  10 
        :param str limit: Specifies the maximum number of campaigns to return on a page in the paginated response. If no value is specified, the default value is used. Default: 10 Minimum:  1Maximum:  1000
        :param str offset: Specifies the number of campaigns to skip in the result set before returning the first report in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: TargetedAdsPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'suggest_items', SellMarketingException, True, ['sell.marketing', 'campaign'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_ad_rate_strategy(self, body, campaign_id, **kwargs):  # noqa: E501
        """update_ad_rate_strategy  

        This method updates the ad rate strategy for an existing Promoted Listings Standard (PLS) rules-based ad campaign that uses the Cost Per Sale (CPS) funding model.Specify the campaign_id as a path parameter. You can retrieve the campaign IDs for a seller by calling the getCampaigns method.Note: This method only applies to the CPS funding model; it does not apply to the Cost Per Click (CPC) funding model. See Funding Models in the Promoted Listings Playbook for more information.  

        :param UpdateAdrateStrategyRequest body: This type defines the request fields for the ad rate strategy that shall be updated. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'update_ad_rate_strategy', SellMarketingException, True, ['sell.marketing', 'campaign'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_campaign_budget(self, body, campaign_id, **kwargs):  # noqa: E501
        """update_campaign_budget  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method updates the daily budget for a PLA campaign that uses the Cost Per Click (CPC) funding model.A click occurs when an eBay user finds and clicks on the seller’s listing (within the search results) after using a keyword that the seller has created for the campaign. For each ad in an ad group in the campaign, each click triggers a cost, which gets subtracted from the campaign’s daily budget. If the cost of the clicks exceeds the daily budget, the Promoted Listings campaign will be paused until the next day.Specify the campaign_id as a path parameter. You can retrieve the campaign IDs for a seller by calling the getCampaigns method.  

        :param UpdateCampaignBudgetRequest body: This type defines the request fields for the budget details that shall be updated. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'update_campaign_budget', SellMarketingException, True, ['sell.marketing', 'campaign'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_campaign_identification(self, body, campaign_id, **kwargs):  # noqa: E501
        """update_campaign_identification  

        This method can be used to change the name of a campaign, as well as modify the start or end dates. Specify the campaign_id you want to update as a URI parameter, and configure the campaignName and startDate in the request payload.  If you want to change only the end date of the campaign, specify the current campaign name and set startDate to the current date (you cannot use a start date that is in the past), and set the endDate as desired. Note that if you do not set a new end date in this call, any current endDate value will be set to null. To preserve the currently-set end date, you must specify the value again in your request. Call getCampaigns to retrieve a seller's campaign details, including the campaign ID, campaign name, and the start and end dates of the campaign.  

        :param UpdateCampaignIdentificationRequest body: This type defines the fields to update the campaign name and start and end dates. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.CampaignApi, sell_marketing.ApiClient, 'update_campaign_identification', SellMarketingException, True, ['sell.marketing', 'campaign'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_item_price_markdown_promotion(self, **kwargs):  # noqa: E501
        """create_item_price_markdown_promotion  

        This method creates an item price markdown promotion (know simply as a \"markdown promotion\") where a discount amount is applied directly to the items included the promotion. Discounts can be specified as either a monetary amount or a percentage off the standard sales price. eBay highlights promoted items by placing teasers for the items throughout the online sales flows.  Unlike an item promotion, a markdown promotion does not require the buyer meet a \"threshold\" before the offer takes effect. With markdown promotions, all the buyer needs to do is purchase the item to receive the promotion benefit. Important: There are some restrictions for which listings are available for price markdown promotions. For details, see Promotions Manager requirements and restrictions. In addition, we recommend you list items at competitive prices before including them in your markdown promotions. For an extensive list of pricing recommendations, see the Growth tab in Seller Hub. There are two ways to add items to markdown promotions: Key-based promotions select items using either the listing IDs or inventory reference IDs of the items you want to promote. Note that if you use inventory reference IDs, you must specify both the inventoryReferenceId and the associated inventoryReferenceType of the item(s) you want to include the promotion. Rule-based promotions select items using a list of eBay category IDs or seller Store category IDs. Rules can further constrain items in a promotion by minimum and maximum prices, brands, and item conditions. New promotions must be created in either a DRAFT or a SCHEDULED state. Use the DRAFT state when you are initially creating a promotion and you want to be sure it's correctly configured before scheduling it to run. When you create a promotion, the promotion ID is returned in the Location response header. Use this ID to reference the promotion in subsequent requests (such as to schedule a promotion that's in a DRAFT state). Tip: Refer to Promotions Manager in the Selling Integration Guide for details and examples showing how to create and manage seller promotions. Markdown promotions are available on all eBay marketplaces. For more information, see Promotions Manager requirements and restrictions.  

        :param ItemPriceMarkdown body: This type defines the fields that describe an item price markdown promotion.
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'create_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_item_price_markdown_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """delete_item_price_markdown_promotion  

        This method deletes the item price markdown promotion specified by the promotion_id path parameter. Call getPromotions to retrieve the IDs of a seller's promotions.  You can delete any promotion with the exception of those that are currently active (RUNNING). To end a running promotion, call updateItemPriceMarkdownPromotion and adjust the endDate field as appropriate.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to delete plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'delete_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_item_price_markdown_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """get_item_price_markdown_promotion  

        This method returns the complete details of the item price markdown promotion that's indicated by the promotion_id path parameter. Call getPromotions to retrieve the IDs of a seller's promotions.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to get plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :return: ItemPriceMarkdown
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'get_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_item_price_markdown_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """update_item_price_markdown_promotion  

        This method updates the specified item price markdown promotion with the new configuration that you supply in the payload of the request. Specify the promotion you want to update using the promotion_id path parameter. Call getPromotions to retrieve the IDs of a seller's promotions.  When updating a promotion, supply all the fields that you used to configure the original promotion (and not just the fields you are updating). eBay replaces the specified promotion with the values you supply in the update request and if you don't pass a field that currently has a value, the update request fails.  The parameters you are allowed to update with this request depend on the status of the promotion you're updating:  DRAFT or SCHEDULED promotions: You can update any of the parameters in these promotions that have not yet started to run, including the discountRules. RUNNING promotions: You can change the endDate and the item's inventory but you cannot change the promotional discount or the promotion's start date. ENDED promotions: Nothing can be changed.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to update plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :param ItemPriceMarkdown body: This type defines the fields that describe an item price markdown promotion.
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPriceMarkdownApi, sell_marketing.ApiClient, 'update_item_price_markdown_promotion', SellMarketingException, True, ['sell.marketing', 'item_price_markdown'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_item_promotion(self, **kwargs):  # noqa: E501
        """create_item_promotion  

        This method creates an item promotion, where the buyer receives a discount when they meet the buying criteria that's set for the promotion. Known here as \"threshold promotions\", these promotions trigger when a threshold is met.  eBay highlights promoted items by placing teasers for the promoted items throughout the online buyer flows. Discounts are specified as either a monetary amount or a percentage off the standard sales price of a listing, letting you offer deals such as \"Buy 1 Get 1\" and \"Buy $50, get 20% off\". Volume pricing promotions increase the value of the discount as the buyer increases the quantity they purchase. Coded Coupons provide unique codes that a buyer can use during checkout to receive a discount. The seller can specify the number of times a buyer can use the coupon and the maximum amount across all purchases that can be discounted using the coupon. The coupon code can also be made public (appearing on the seller's Offer page, search pages, the item listing, and the checkout page) or private (only on the seller's Offer page, but the seller can include the code in email and social media). Note: Coded Coupons are currently available in the US, UK, DE, FR, IT, ES, and AU marketplaces.There are two ways to add items to a threshold promotion: Key-based promotions select items using either the listing IDs or inventory reference IDs of the items you want to promote. Note that if you use inventory reference IDs, you must specify both the inventoryReferenceId and the associated inventoryReferenceType of the item(s) you want to include the promotion. Rule-based promotions select items using a list of eBay category IDs or seller Store category IDs. Rules can further constrain items in a promotion by minimum and maximum prices, brands, and item conditions. You must create a new promotion in either a DRAFT or SCHEDULED state. Use the DRAFT state when you are initially creating a promotion and you want to be sure it's correctly configured before scheduling it to run. When you create a promotion, the promotion ID is returned in the Location response header. Use this ID to reference the promotion in subsequent requests. Tip: Refer to the Selling Integration Guide for details and examples showing how to create and manage threshold promotions using the Promotions Manager. For information on the eBay marketplaces that support item promotions, see Promotions Manager requirements and restrictions.  

        :param ItemPromotion body: This type defines the fields that describe an item promotion.
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'create_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_delete_item_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """delete_item_promotion  

        This method deletes the threshold promotion specified by the promotion_id path parameter. Call getPromotions to retrieve the IDs of a seller's promotions.  You can delete any promotion with the exception of those that are currently active (RUNNING). To end a running threshold promotion, call updateItemPromotion and adjust the endDate field as appropriate.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to delete plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'delete_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_item_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """get_item_promotion  

        This method returns the complete details of the threshold promotion specified by the promotion_id path parameter. Call getPromotions to retrieve the IDs of a seller's promotions.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to retrieve plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :return: ItemPromotionResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'get_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_item_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """update_item_promotion  

        This method updates the specified threshold promotion with the new configuration that you supply in the request. Indicate the promotion you want to update using the promotion_id path parameter.  Call getPromotions to retrieve the IDs of a seller's promotions. When updating a promotion, supply all the fields that you used to configure the original promotion (and not just the fields you are updating). eBay replaces the specified promotion with the values you supply in the update request and if you don't pass a field that currently has a value, the update request will fail. The parameters you are allowed to update with this request depend on the status of the promotion you're updating:  DRAFT or SCHEDULED promotions: You can update any of the parameters in these promotions that have not yet started to run, including the discountRules. RUNNING or PAUSED promotions: You can change the endDate and the item's inventory but you cannot change the promotional discount or the promotion's start date. ENDED promotions: Nothing can be changed. Tip: When updating a RUNNING or PAUSED promotion, set the status field to SCHEDULED for the update request. When the promotion is updated, the previous status (either RUNNING or PAUSED) is retained.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to update plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :param ItemPromotion body: This type defines the fields that describe an item promotion.
        :return: BaseResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.ItemPromotionApi, sell_marketing.ApiClient, 'update_item_promotion', SellMarketingException, True, ['sell.marketing', 'item_promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_create_keyword(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_create_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method adds keywords, in bulk, to an existing PLA ad group in a campaign that uses the Cost Per Click (CPC) funding model.This method also sets the CPC rate for each keyword.In the request, supply the campaign_id as a path parameter.Call the getCampaigns method to retrieve a list of current campaign IDs for a specified seller.  

        :param BulkCreateKeywordRequest body: A type that defines the fields for the bulk request to create keywords. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: BulkCreateKeywordResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.KeywordApi, sell_marketing.ApiClient, 'bulk_create_keyword', SellMarketingException, True, ['sell.marketing', 'keyword'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_keyword(self, body, campaign_id, **kwargs):  # noqa: E501
        """bulk_update_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method updates the bids and statuses of keywords, in bulk, for an existing PLA campaign.In the request, supply the campaign_id as a path parameter.Call the getCampaigns method to retrieve a list of current campaign IDs for a specified seller.  

        :param BulkUpdateKeywordRequest body: A type that defines the fields for the bulk request to update keywords. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: BulkUpdateKeywordResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.KeywordApi, sell_marketing.ApiClient, 'bulk_update_keyword', SellMarketingException, True, ['sell.marketing', 'keyword'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_keyword(self, body, campaign_id, **kwargs):  # noqa: E501
        """create_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method creates keywords using a specified campaign ID for an existing PLA campaign.In the request, supply the campaign_id as a path parameter.Call the suggestKeywords method to retrieve a list of keyword ideas to be targeted for PLA campaigns, and call the getCampaigns method to retrieve a list of current campaign IDs for a seller.  

        :param CreateKeywordRequest body: A type that defines the fields for the request to create a keyword. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.KeywordApi, sell_marketing.ApiClient, 'create_keyword', SellMarketingException, True, ['sell.marketing', 'keyword'], (body, campaign_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_keyword(self, campaign_id, keyword_id, **kwargs):  # noqa: E501
        """get_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method retrieves details on a specific keyword from an ad group within a PLA campaign that uses the Cost Per Click (CPC) funding model.In the request, specify the campaign_id and keyword_id as path parameters.Call the getCampaigns method to retrieve a list of current campaign IDs for a seller and call the getKeywords method to retrieve their keyword IDs.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str keyword_id: This path parameter is used to identify the keyword to retrieve. (required)
        :return: Keyword
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.KeywordApi, sell_marketing.ApiClient, 'get_keyword', SellMarketingException, True, ['sell.marketing', 'keyword'], (campaign_id, keyword_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_keywords(self, campaign_id, **kwargs):  # noqa: E501
        """get_keywords  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method can be used to retrieve all of the keywords for ad groups in PLA campaigns that use the Cost Per Click (CPC) funding model.In the request, specify the campaign_id as a path parameter. If one or more ad_group_ids are passed in the request body, the keywords for those ad groups will be returned. If ad_group_ids are not passed in the response body, the call will return all the keywords in the campaign.Call the getCampaigns method to retrieve a list of current campaign IDs for a seller.  

        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str ad_group_ids: A comma-separated list of ad group IDs. This query parameter is used if the seller wants to retrieve keywords from one or more specific ad groups. If this query parameter is not used, all keywords that are part of the CPC campaign are returned.Note:You can call the getAdGroups  method to retrieve the ad group IDs for a seller.
        :param str keyword_status: A comma-separated list of keyword statuses. The results will be filtered to only include the given statuses of the keyword. If none are provided, all keywords are returned.
        :param str limit: Specifies the maximum number of results to return on a page in the paginated response. Default: 10 Maximum:  500
        :param str offset: Specifies the number of results to skip in the result set before returning the first report in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: KeywordPagedCollectionResponse
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.KeywordApi, sell_marketing.ApiClient, 'get_keywords', SellMarketingException, True, ['sell.marketing', 'keyword'], campaign_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_keyword(self, body, campaign_id, keyword_id, **kwargs):  # noqa: E501
        """update_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method updates keywords using a campaign ID and keyword ID for an existing PLA campaign.In the request, specify the campaign_id and keyword_id as path parameters.Call the getCampaigns method to retrieve a list of current campaign IDs for a seller and call the getKeywords method to retrieve their keyword IDs.  

        :param UpdateKeywordRequest body: A type that defines the fields for the request to update a keyword. (required)
        :param str campaign_id: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.Note: You can retrieve the campaign IDs for a specified seller using the getCampaigns method. (required)
        :param str keyword_id: A unique eBay-assigned ID that is generated when a keyword is created. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.KeywordApi, sell_marketing.ApiClient, 'update_keyword', SellMarketingException, True, ['sell.marketing', 'keyword'], (body, campaign_id, keyword_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_create_negative_keyword(self, body, **kwargs):  # noqa: E501
        """bulk_create_negative_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method adds negative keywords, in bulk, to an existing ad group in a PLA campaign that uses the Cost Per Click (CPC) funding model.Specify the campaignId and adGroupId in the request body, along with the negativeKeywordText and negativeKeywordMatchType.Call the getCampaigns method to retrieve a list of current campaign IDs for a specified seller.  

        :param BulkCreateNegativeKeywordRequest body: A type that defines the fields for the bulk request to create negative keywords. (required)
        :return: BulkCreateNegativeKeywordResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.NegativeKeywordApi, sell_marketing.ApiClient, 'bulk_create_negative_keyword', SellMarketingException, True, ['sell.marketing', 'negative_keyword'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_bulk_update_negative_keyword(self, body, **kwargs):  # noqa: E501
        """bulk_update_negative_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method updates the statuses of existing negative keywords, in bulk.Specify the negativeKeywordId and negativeKeywordStatus in the request body.  

        :param BulkUpdateNegativeKeywordRequest body: A type that defines the fields for the bulk request to update negative keyword statuses. (required)
        :return: BulkUpdateNegativeKeywordResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.NegativeKeywordApi, sell_marketing.ApiClient, 'bulk_update_negative_keyword', SellMarketingException, True, ['sell.marketing', 'negative_keyword'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_create_negative_keyword(self, body, **kwargs):  # noqa: E501
        """create_negative_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method adds a negative keyword to an existing ad group in a PLA campaign that uses the Cost Per Click (CPC) funding model.Specify the campaignId and adGroupId in the request body, along with the negativeKeywordText and negativeKeywordMatchType.Call the getCampaigns method to retrieve a list of current campaign IDs for a specified seller.  

        :param CreateNegativeKeywordRequest body: A type that defines the fields for the request to create a negative keyword. (required)
        :return: object
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.NegativeKeywordApi, sell_marketing.ApiClient, 'create_negative_keyword', SellMarketingException, True, ['sell.marketing', 'negative_keyword'], body, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_negative_keyword(self, negative_keyword_id, **kwargs):  # noqa: E501
        """get_negative_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method retrieves details on a specific negative keyword.In the request, specify the negative_keyword_id as a path parameter.  

        :param str negative_keyword_id: The unique identifier for the negative keyword.This value is returned in the Location response header from the createNegativeKeyword method. (required)
        :return: NegativeKeyword
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.NegativeKeywordApi, sell_marketing.ApiClient, 'get_negative_keyword', SellMarketingException, True, ['sell.marketing', 'negative_keyword'], negative_keyword_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_negative_keywords(self, **kwargs):  # noqa: E501
        """get_negative_keywords  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method can be used to retrieve all of the negative keywords for ad groups in PLA campaigns that use the Cost Per Click (CPC) funding model.The results can be filtered using the campaign_ids, ad_group_ids, and negative_keyword_status query parameters.Call the getCampaigns method to retrieve a list of current campaign IDs for a seller.  

        :param str ad_group_ids: A comma-separated list of ad group IDs.This query parameter is used if the seller wants to retrieve the negative keywords from one or more specific ad groups. The results might not include these ad group IDs if other search conditions exclude them.Note:You can call the getAdGroups method to retrieve the ad group IDs for a seller.Required if the search results must be filtered to include negative keywords created at the ad group level.
        :param str campaign_ids: A unique eBay-assigned ID for an ad campaign that is generated when a campaign is created.This query parameter is used if the seller wants to retrieve the negative keywords from a specific campaign. The results might not include these campaign IDs if other search conditions exclude them.Note: Currently, only one campaign ID value is supported for each request.
        :param str limit: The number of results, from the current result set, to be returned in a single page.
        :param str negative_keyword_status: A comma-separated list of negative keyword statuses.This query parameter is used if the seller wants to filter the search results based on one or more negative keyword statuses.
        :param str offset: The number of results that will be skipped in the result set. This is used with the limit field to control the pagination of the output.For example, if the offset is set to 0 and the limit is set to 10, the method will retrieve items 1 through 10 from the list of items returned. If the offset is set to 10 and the limit is set to 10, the method will retrieve items 11 through 20 from the list of items returned.
        :return: NegativeKeywordPagedCollectionResponse
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.NegativeKeywordApi, sell_marketing.ApiClient, 'get_negative_keywords', SellMarketingException, True, ['sell.marketing', 'negative_keyword'], None, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_update_negative_keyword(self, body, negative_keyword_id, **kwargs):  # noqa: E501
        """update_negative_keyword  

        Note: This method is only available for select partners who have been approved for the eBay Promoted Listings Advanced (PLA) program. For information about how to request access to this program, refer to  Promoted Listings Advanced Access Requests in the Promoted Listings Playbook. To determine if a seller qualifies for PLA, use the getAdvertisingEligibility method in Account API.This method updates the status of an existing negative keyword.Specify the negative_keyword_id as a path parameter, and specify the negativeKeywordStatus in the request body.  

        :param UpdateNegativeKeywordRequest body: A type that defines the fields for the request to update a negative keyword. (required)
        :param str negative_keyword_id: The unique identifier for the negative keyword.This value is returned in the Location response header from the createNegativeKeyword method. (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.NegativeKeywordApi, sell_marketing.ApiClient, 'update_negative_keyword', SellMarketingException, True, ['sell.marketing', 'negative_keyword'], (body, negative_keyword_id), **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_listing_set(self, promotion_id, **kwargs):  # noqa: E501
        """get_listing_set  

        This method returns the set of listings associated with the promotion_id specified in the path parameter. Call getPromotions to retrieve the IDs of a seller's promotions.  The listing details are returned in a paginated set and you can control and results returned using the following query parameters: limit, offset, q, sort, and status. Maximum associated listings returned: 200 Default number of listings returned: 200  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to get plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :param str limit: Specifies the maximum number of promotions returned on a page from the result set. Default: 200Maximum: 200
        :param str offset: Specifies the number of promotions to skip in the result set before returning the first promotion in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :param str q: Reserved for future use.
        :param str sort: Specifies the order in which to sort the associated listings in the response. If you precede the supplied value with a dash, the response is sorted in reverse order.  Example:    sort=PRICE - Sorts the associated listings by their current price in ascending order    sort=-TITLE - Sorts the associated listings by their title in descending alphabetical order (Z-Az-a)  Valid values:AVAILABLE PRICE TITLE For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/marketing/types/csb:SortField
        :param str status: This query parameter applies only to markdown promotions. It filters the response based on the indicated status of the promotion. Currently, the only supported value for this parameter is MARKED_DOWN, which indicates active markdown promotions. For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/marketing/types/sme:ItemMarkdownStatusEnum
        :return: ItemsPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'get_listing_set', SellMarketingException, True, ['sell.marketing', 'promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_promotions(self, marketplace_id, **kwargs):  # noqa: E501
        """get_promotions  

        This method returns a list of a seller's undeleted promotions. The call returns up to 200 currently-available promotions on the specified marketplace. While the response body does not include the promotion's discountRules or inventoryCriterion containers, it does include the promotionHref (which you can use to retrieve the complete details of the promotion). Use query parameters to sort and filter the results by the number of promotions to return, the promotion state or type, and the eBay marketplace. You can also supply keywords to limit the response to the promotions that contain that keywords in the title of the promotion. Maximum returned: 200  

        :param str marketplace_id: The eBay marketplace ID of the site where the promotion is hosted.  Valid values: EBAY_AU = Australia EBAY_DE = Germany EBAY_ES = Spain EBAY_FR = France EBAY_GB = Great Britain EBAY_IT = Italy EBAY_US = United States (required)
        :param str limit: Specifies the maximum number of promotions returned on a page from the result set.  Default: 200 Maximum: 200
        :param str offset: Specifies the number of promotions to skip in the result set before returning the first promotion in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :param str promotion_status: Specifies the promotion state by which you want to filter the results. The response contains only those promotions that match the state you specify.  Valid values: DRAFT SCHEDULED RUNNING PAUSED ENDEDMaximum number of input values: 1
        :param str promotion_type: Filters the returned promotions based on their campaign promotion type. Specify one of the following values to indicate the promotion type you want returned: CODED_COUPON – A coupon code promotion set with createItemPromotion. MARKDOWN_SALE – A markdown promotion set with createItemPriceMarkdownPromotion. ORDER_DISCOUNT – A threshold promotion set with createItemPromotion. VOLUME_DISCOUNT – A volume pricing promotion set with createItemPromotion.
        :param str q: A string consisting of one or more keywords. eBay filters the response by returning only the promotions that contain the supplied keywords in the promotion title.  Example: \"iPhone\" or \"Harry Potter.\"  Commas that separate keywords are ignored. For example, a keyword string of \"iPhone, iPad\" equals \"iPhone iPad\", and each results in a response that contains promotions with both \"iPhone\" and \"iPad\" in the title.
        :param str sort: Specifies the order for how to sort the response. If you precede the supplied value with a dash, the response is sorted in reverse order.  Example:    sort=END_DATE   Sorts the promotions in the response by their end dates in ascending order    sort=-PROMOTION_NAME   Sorts the promotions by their promotion name in descending alphabetical order (Z-Az-a)  Valid values:START_DATE END_DATE PROMOTION_NAME For implementation help, refer to eBay API documentation at https://developer.ebay.com/api-docs/sell/marketing/types/csb:SortField
        :return: PromotionsPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'get_promotions', SellMarketingException, True, ['sell.marketing', 'promotion'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_pause_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """pause_promotion  

        This method pauses a currently-active (RUNNING) threshold promotion and changes the state of the promotion from RUNNING to PAUSED. Pausing a promotion makes the promotion temporarily unavailable to buyers and any currently-incomplete transactions will not receive the promotional offer until the promotion is resumed. Also, promotion teasers are not displayed when a promotion is paused.  Pass the ID of the promotion you want to pause using the promotion_id path parameter. Call getPromotions to retrieve the IDs of the seller's promotions. Note: You can only pause threshold promotions (you cannot pause markdown promotions).  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to pause plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'pause_promotion', SellMarketingException, True, ['sell.marketing', 'promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_resume_promotion(self, promotion_id, **kwargs):  # noqa: E501
        """resume_promotion  

        This method restarts a threshold promotion that was previously paused and changes the state of the promotion from PAUSED to RUNNING. Only promotions that have been previously paused can be resumed. Resuming a promotion reinstates the promotional teasers and any transactions that were in motion before the promotion was paused will again be eligible for the promotion.  Pass the ID of the promotion you want to resume using the promotion_id path parameter. Call getPromotions to retrieve the IDs of the seller's promotions.  

        :param str promotion_id: This path parameter takes a concatenation of the ID of the promotion you want to resume plus the marketplace ID on which the promotion is hosted. Concatenate the two values by separating them with an \"at sign\" (@).  The ID of the promotion (promotionId) is a unique eBay-assigned value that's generated when the promotion is created. The Marketplace ID is the ENUM value of eBay marketplace where the promotion is hosted. Example: 1********5@EBAY_US (required)
        :return: None
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionApi, sell_marketing.ApiClient, 'resume_promotion', SellMarketingException, True, ['sell.marketing', 'promotion'], promotion_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_promotion_reports(self, marketplace_id, **kwargs):  # noqa: E501
        """get_promotion_reports  

        This method generates a report that lists the seller's running, paused, and ended promotions for the specified eBay marketplace. The result set can be filtered by the promotion status and the number of results to return. You can also supply keywords to limit the report to promotions that contain the specified keywords. Specify the eBay marketplace for which you want the report run using the marketplace_id query parameter. Supply additional query parameters to control the report as needed.  

        :param str marketplace_id: The eBay marketplace ID of the site for which you want the promotions report.  Valid values: EBAY_AU = Australia EBAY_DE = Germany EBAY_ES = Spain EBAY_FR = France EBAY_GB = Great Britain EBAY_IT = Italy EBAY_US = United States (required)
        :param str limit: Specifies the maximum number of promotions returned on a page from the result set.  Default: 200 Maximum: 200
        :param str offset: Specifies the number of promotions to skip in the result set before returning the first promotion in the paginated response.  Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :param str promotion_status: Limits the results to the promotions that are in the state specified by this query parameter.  Valid values: DRAFT SCHEDULED RUNNING PAUSED ENDEDMaximum number of values supported: 1
        :param str promotion_type: Filters the returned promotions in the report based on their campaign promotion type. Specify one of the following values to indicate the promotion type you want returned in the report: CODED_COUPON – A coupon code promotion set with createItemPromotion. MARKDOWN_SALE – A markdown promotion set with createItemPriceMarkdownPromotion. ORDER_DISCOUNT – A threshold promotion set with createItemPromotion. VOLUME_DISCOUNT – A volume pricing promotion set with createItemPromotion.
        :param str q: A string consisting of one or more keywords. eBay filters the response by returning only the promotions that contain the supplied keywords in the promotion title.  Example: \"iPhone\" or \"Harry Potter.\"  Commas that separate keywords are ignored. For example, a keyword string of \"iPhone, iPad\" equals \"iPhone iPad\", and each results in a response that contains promotions with both \"iPhone\" and \"iPad\" in the title.
        :return: PromotionsReportPagedCollection
        """
        try:
            return self._method_paged(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionReportApi, sell_marketing.ApiClient, 'get_promotion_reports', SellMarketingException, True, ['sell.marketing', 'promotion_report'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_marketing_get_promotion_summary_report(self, marketplace_id, **kwargs):  # noqa: E501
        """get_promotion_summary_report  

        This method generates a report that summarizes the seller's promotions for the specified eBay marketplace. The report returns information on RUNNING, PAUSED, and ENDED promotions (deleted reports are not returned) and summarizes the seller's campaign performance for all promotions on a given site.  For information about summary reports, see Reading the item promotion Summary report.  

        :param str marketplace_id: The eBay marketplace ID of the site you for which you want a promotion summary report.  Valid values: EBAY_AU = Australia EBAY_DE = Germany EBAY_ES = Spain EBAY_FR = France EBAY_GB = Great Britain EBAY_IT = Italy EBAY_US = United States (required)
        :return: SummaryReportResponse
        """
        try:
            return self._method_single(sell_marketing.Configuration, '/sell/marketing/v1', sell_marketing.PromotionSummaryReportApi, sell_marketing.ApiClient, 'get_promotion_summary_report', SellMarketingException, True, ['sell.marketing', 'promotion_summary_report'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_sales_tax_jurisdictions(self, country_code, **kwargs):  # noqa: E501
        """get_sales_tax_jurisdictions  

        This method retrieves all the sales tax jurisdictions for the country that you specify in the countryCode path parameter. Countries with valid sales tax jurisdictions are Canada and the US.  The response from this call tells you the jurisdictions for which a seller can configure tax tables. Although setting up tax tables is optional, you can use the createOrReplaceSalesTax in the Account API call to configure the tax tables for the jurisdictions you sell to.  

        :param str country_code: This path parameter specifies the two-letter ISO 3166 country code for the country whose jurisdictions you want to retrieve. eBay provides sales tax jurisdiction information for Canada and the United States.Valid values for this path parameter are CA and US. (required)
        :return: SalesTaxJurisdictions
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.CountryApi, sell_metadata.ApiClient, 'get_sales_tax_jurisdictions', SellMetadataException, False, ['sell.metadata', 'country'], country_code, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_automotive_parts_compatibility_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_automotive_parts_compatibility_policies  

        This method returns the eBay policies that define how to list automotive-parts-compatibility items in the categories of a specific marketplace.  By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the filter query parameter to specify only the category IDs you want to review.Tip: This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the Accept-Encoding request header and setting the value to application/gzip.  

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved.  Note: Only the following eBay marketplaces support automotive parts compatibility:  EBAY_US EBAY_AU EBAY_CA EBAY_DE EBAY_ES EBAY_FR EBAY_GB EBAY_IT (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply categoryId values for the sections of the tree you want returned.  When you specify a categoryId value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  The parameter takes a list of categoryId values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 categoryId values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  Example: filter=categoryIds:{100|101|102} Note that you must URL-encode the parameter list, which results in the following filter for the above example:    filter=categoryIds%3A%7B100%7C101%7C102%7D
        :return: AutomotivePartsCompatibilityPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_automotive_parts_compatibility_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_extended_producer_responsibility_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_extended_producer_responsibility_policies  

        This method returns the Extended Producer Responsibility policies for one, multiple, or all eBay categories in an eBay marketplace.The identifier of the eBay marketplace is passed in as a path parameter, and unless one or more eBay category IDs are passed in through the filter query parameter, this method will return metadata on every applicable category for the specified marketplace.Note: Currently, the Extended Producer Responsibility policies are only applicable to a limited number of categories, and only in the EBAY_FR marketplace.Tip: This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the Accept-Encoding request header and setting the value to application/gzip.  

        :param str marketplace_id: A path parameter that specifies the eBay marketplace for which policy information shall be retrieved.Tip: See Request components for a list of valid eBay marketplace IDs. (required)
        :param str filter: A query parameter that can be used to limit the response by returning policy information for only the selected sections of the category tree. Supply categoryId values for the sections of the tree that should be returned.When a categoryId value is specified, the returned category tree includes the policies for that parent node, as well as the policies for any child nodes below that parent node.Pass in the categoryId values using a URL-encoded, pipe-separated ('|') list. For example:filter=categoryIds%3A%7B100%7C101%7C102%7DMaximum: 50
        :return: ExtendedProducerResponsibilityPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_extended_producer_responsibility_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_hazardous_materials_labels(self, marketplace_id, **kwargs):  # noqa: E501
        """get_hazardous_materials_labels  

        This method returns hazardous materials label information for the specified eBay marketplace. The information includes IDs, descriptions, and URLs (as applicable) for the available signal words, statements, and pictograms. The returned statements are localized for the default langauge of the marketplace. If a marketplace does not support hazardous materials label information, an error is returned.This information is used by the seller to add hazardous materials label related information to their listings (see Specifying hazardous material related information).  

        :param str marketplace_id: A path parameter that specifies the eBay marketplace for which hazardous materials label information shall be retrieved.Tip: See Request components for a list of valid eBay marketplace IDs. (required)
        :return: HazardousMaterialDetailsResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_hazardous_materials_labels', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_item_condition_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_item_condition_policies  

        This method returns item condition metadata on one, multiple, or all eBay categories on an eBay marketplace. This metadata consists of the different item conditions (with IDs) that an eBay category supports, and a boolean to indicate if an eBay category requires an item condition. The identifier of the eBay marketplace is passed in as a path parameter, and unless one or more eBay category IDs are passed in through the filter query parameter, this method will return metadata on every single category for the specified marketplace. If you only want to view item condition metadata for one eBay category or a select group of eBay categories, you can pass in up to 50 eBay category ID through the filter query parameter.Important: Certified - Refurbished-eligible sellers, and sellers who are eligible to list with the new values (EXCELLENT_REFURBISHED, VERY_GOOD_REFURBISHED, and GOOD_REFURBISHED) must use an OAuth token created with the authorization code grant flow and https://api.ebay.com/oauth/api_scope/sell.inventory scope in order to retrieve the refurbished conditions for the relevant categories.See the eBay Refurbished Program - Category and marketplace support topic for the categories and marketplaces that support these refurbished conditionsThese restricted item conditions will not be returned if an OAuth token created with the client credentials grant flow and https://api.ebay.com/oauth/api_scope scope is used, or if any seller is not eligible to list with that item condition.  See the Specifying OAuth scopes topic for more information about specifying scopes.Tip: This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the Accept-Encoding request header and setting the value to application/gzip.  

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: Request components. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply categoryId values for the sections of the tree you want returned.  When you specify a categoryId value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  The parameter takes a list of categoryId values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 categoryId values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  Example: filter=categoryIds:{100|101|102} Note that you must URL-encode the parameter list, which results in the following filter for the above example:    filter=categoryIds%3A%7B100%7C101%7C102%7D
        :return: ItemConditionPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_item_condition_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_listing_structure_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_listing_structure_policies  

        This method returns the eBay policies that define the allowed listing structures for the categories of a specific marketplace. The listing-structure policies currently pertain to whether or not you can list items with variations.  By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the filter query parameter to specify only the category IDs you want to review.Tip: This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the Accept-Encoding request header and setting the value to application/gzip.  

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: Request components. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply categoryId values for the sections of the tree you want returned.  When you specify a categoryId value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  The parameter takes a list of categoryId values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 categoryId values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  Example: filter=categoryIds:{100|101|102} Note that you must URL-encode the parameter list, which results in the following filter for the above example:    filter=categoryIds%3A%7B100%7C101%7C102%7D
        :return: ListingStructurePolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_listing_structure_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_negotiated_price_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_negotiated_price_policies  

        This method returns the eBay policies that define the supported negotiated price features (like \"best offer\") for the categories of a specific marketplace.  By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the filter query parameter to specify only the category IDs you want to review.Tip: This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the Accept-Encoding request header and setting the value to application/gzip.  

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: Request components. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply categoryId values for the sections of the tree you want returned.  When you specify a categoryId value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  The parameter takes a list of categoryId values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 categoryId values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  Example: filter=categoryIds:{100|101|102} Note that you must URL-encode the parameter list, which results in the following filter for the above example:    filter=categoryIds%3A%7B100%7C101%7C102%7D
        :return: NegotiatedPricePolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_negotiated_price_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_metadata_get_return_policies(self, marketplace_id, **kwargs):  # noqa: E501
        """get_return_policies  

        This method returns the eBay policies that define whether or not you must include a return policy for the items you list in the categories of a specific marketplace, plus the guidelines for creating domestic and international return policies in the different eBay categories.  By default, this method returns the entire category tree for the specified marketplace. You can limit the size of the result set by using the filter query parameter to specify only the category IDs you want to review.Tip: This method can potentially return a very large response payload. eBay recommends that the response payload be compressed by passing in the Accept-Encoding request header and setting the value to application/gzip.  

        :param str marketplace_id: This path parameter specifies the eBay marketplace for which policy information is retrieved. See the following page for a list of valid eBay marketplace IDs: Request components. (required)
        :param str filter: This query parameter limits the response by returning policy information for only the selected sections of the category tree. Supply categoryId values for the sections of the tree you want returned.  When you specify a categoryId value, the returned category tree includes the policies for that parent node, plus the policies for any leaf nodes below that parent node.  The parameter takes a list of categoryId values and you can specify up to 50 separate category IDs. Separate multiple values with a pipe character ('|'). If you specify more than 50 categoryId values, eBay returns the policies for the first 50 IDs and a warning that not all categories were returned.  Example: filter=categoryIds:{100|101|102} Note that you must URL-encode the parameter list, which results in the following filter for the above example:    filter=categoryIds%3A%7B100%7C101%7C102%7D
        :return: ReturnPolicyResponse
        """
        try:
            return self._method_single(sell_metadata.Configuration, '/sell/metadata/v1', sell_metadata.MarketplaceApi, sell_metadata.ApiClient, 'get_return_policies', SellMetadataException, False, ['sell.metadata', 'marketplace'], marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_negotiation_find_eligible_items(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """find_eligible_items  

        This method evaluates a seller's current listings and returns the set of IDs that are eligible for a seller-initiated discount offer to a buyer. A listing ID is returned only when one or more buyers have shown an "interest" in the listing. If any buyers have shown interest in a listing, the seller can initiate a "negotiation" with them by calling sendOfferToInterestedBuyers, which sends all interested buyers a message that offers the listing at a discount. For details about how to create seller offers to buyers, see Sending offers to buyers.  

        :param str x_ebay_c_marketplace_id: The eBay marketplace on which you want to search for eligible listings. For a complete list of supported marketplaces, see Negotiation API requirements and restrictions. (required)
        :param str limit: This query parameter specifies the maximum number of items to return from the result set on a page in the paginated response. Minimum: 1    Maximum: 200 Default: 10
        :param str offset: This query parameter specifies the number of results to skip in the result set before returning the first result in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 results from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: PagedEligibleItemCollection
        """
        try:
            return self._method_paged(sell_negotiation.Configuration, '/sell/negotiation/v1', sell_negotiation.OfferApi, sell_negotiation.ApiClient, 'find_eligible_items', SellNegotiationException, True, ['sell.negotiation', 'offer'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_negotiation_send_offer_to_interested_buyers(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """send_offer_to_interested_buyers  

        This method sends eligible buyers offers to purchase items in a listing at a discount. When a buyer has shown interest in a listing, they become "eligible" to receive a seller-initiated offer to purchase the item(s). Sellers use findEligibleItems to get the set of listings that have interested buyers. If a listing has interested buyers, sellers can use this method (sendOfferToInterestedBuyers) to send an offer to the buyers who are interested in the listing. The offer gives buyers the ability to purchase the associated listings at a discounted price. For details about how to create seller offers to buyers, see Sending offers to buyers.  

        :param str x_ebay_c_marketplace_id: The eBay marketplace on which your listings with "eligible" buyers appear. For a complete list of supported marketplaces, see Negotiation API requirements and restrictions. (required)
        :param CreateOffersRequest body: Send offer to eligible items request.
        :return: SendOfferToInterestedBuyersCollectionResponse
        """
        try:
            return self._method_single(sell_negotiation.Configuration, '/sell/negotiation/v1', sell_negotiation.OfferApi, sell_negotiation.ApiClient, 'send_offer_to_interested_buyers', SellNegotiationException, True, ['sell.negotiation', 'offer'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

    def sell_recommendation_find_listing_recommendations(self, x_ebay_c_marketplace_id, **kwargs):  # noqa: E501
        """find_listing_recommendations  

        The find method currently returns information for a single recommendation type (AD) which contains information that sellers can use to configure Promoted Listings ad campaigns. The response from this method includes an array of the seller's listing IDs, where each element in the array contains recommendations related to the associated listing ID. For details on how to use this method, see Using the Recommendation API to help configure campaigns. The AD recommendation type The AD type contains two sets of information: The promoteWithAd indicator The promoteWithAd response field indicates whether or not eBay recommends you place the associated listing in a Promoted Listings ad campaign. The returned value is set to either RECOMMENDED or UNDETERMINED, where RECOMMENDED identifies the listings that will benefit the most from having them included in an ad campaign. The bid percentage Also known as the "ad rate," the bidPercentage field provides the current trending bid percentage of similarly promoted items in the marketplace. The ad rate is a user-specified value that indicates the level of promotion that eBay applies to the campaign across the marketplace. The value is also used to calculate the Promotion Listings fee, which is assessed to the seller if a Promoted Listings action results in the sale of an item. Configuring the request You can configure a request to review all of a seller's currently active listings, or just a subset of them. All active listings – If you leave the request body empty, the request targets all the items currently listed by the seller. Here, the response is filtered to contain only the items where promoteWithAd equals RECOMMENDED. In this case, eBay recommends that all the returned listings should be included in a Promoted Listings ad campaign. Selected listing IDs – If you populate the request body with a set of listingIds, the response contains data for all the specified listing IDs. In this scenario, the response provides you with information on listings where the promoteWithAd can be either RECOMMENDED or UNDETERMINED. The paginated response Because the response can contain many listing IDs, the findListingRecommendations method paginates the response set. You can control size of the returned pages, as well as an offset that dictates where to start the pagination, using query parameters in the request.  

        :param str x_ebay_c_marketplace_id: Use this header to specify the eBay marketplace where you list the items for which you want to get recommendations. (required)
        :param FindListingRecommendationRequest body:
        :param str filter: Provide a list of key-value pairs to specify the criteria you want to use to filter the response. In the list, separate each filter key from its associated value with a colon (":"). Currently, the only supported filter value is recommendationTypes and it supports only the ("AD") type. Follow the recommendationTypes specifier with the filter type(s) enclosed in curly braces ("{ }"), and separate multiple types with commas. Example: filter=recommendationTypes:{AD} Default: recommendationTypes:{AD}
        :param str limit: Use this query parameter to set the maximum number of ads to return on a page from the paginated response. Default: 10 Maximum: 500
        :param str offset: Specifies the number of ads to skip in the result set before returning the first ad in the paginated response. Combine offset with the limit query parameter to control the items returned in the response. For example, if you supply an offset of 0 and a limit of 10, the first page of the response contains the first 10 items from the complete list of items retrieved by the call. If offset is 10 and limit is 20, the first page of the response contains items 11-30 from the complete result set. Default: 0
        :return: PagedListingRecommendationCollection
        """
        try:
            return self._method_paged(sell_recommendation.Configuration, '/sell/recommendation/v1', sell_recommendation.ListingRecommendationApi, sell_recommendation.ApiClient, 'find_listing_recommendations', SellRecommendationException, True, ['sell.recommendation', 'listing_recommendation'], x_ebay_c_marketplace_id, **kwargs)  # noqa: E501
        except Error:
            raise

        # ANCHOR-er_methods-END"
