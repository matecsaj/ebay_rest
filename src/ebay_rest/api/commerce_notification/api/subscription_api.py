# coding: utf-8

"""
    Notification API

    The eBay Notification API enables management of the entire end-to-end eBay notification experience by allowing users to:<ul><li>Browse for supported notification topics and retrieve topic details</li><li>Create, configure, and manage notification destination endpionts</li><li>Configure, manage, and test notification subscriptions</li><li>Process eBay notifications and verify the integrity of the message payload</li></ul>  # noqa: E501

    OpenAPI spec version: v1.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from ...commerce_notification.api_client import ApiClient


class SubscriptionApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def create_subscription(self, **kwargs):  # noqa: E501
        """create_subscription  # noqa: E501

        This method allows applications to create a subscription for a topic and supported schema version. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business. Each application and topic-schema pairing to a subscription should have a 1:1 cardinality. You can create the subscription in disabled mode, test it (see the test method), and when everything is ready, you can enable the subscription (see the enableSubscription method). Note: If an application is not authorized to subscribe to a topic, for example, if your authorization does not include the list of scopes required for the topic, an error code of 195011 is returned.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create_subscription(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param CreateSubscriptionRequest body: The create subscription request.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.create_subscription_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.create_subscription_with_http_info(**kwargs)  # noqa: E501
            return data

    def create_subscription_with_http_info(self, **kwargs):  # noqa: E501
        """create_subscription  # noqa: E501

        This method allows applications to create a subscription for a topic and supported schema version. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business. Each application and topic-schema pairing to a subscription should have a 1:1 cardinality. You can create the subscription in disabled mode, test it (see the test method), and when everything is ready, you can enable the subscription (see the enableSubscription method). Note: If an application is not authorized to subscribe to a topic, for example, if your authorization does not include the list of scopes required for the topic, an error code of 195011 is returned.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create_subscription_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param CreateSubscriptionRequest body: The create subscription request.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_subscription" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """delete_subscription  # noqa: E501

        This method allows applications to delete a subscription. Subscriptions can be deleted regardless of status.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_subscription(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.delete_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
            return data

    def delete_subscription_with_http_info(self, subscription_id, **kwargs):  # noqa: E501
        """delete_subscription  # noqa: E501

        This method allows applications to delete a subscription. Subscriptions can be deleted regardless of status.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_subscription_with_http_info(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['subscription_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_subscription" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'subscription_id' is set
        if ('subscription_id' not in params or
                params['subscription_id'] is None):
            raise ValueError("Missing the required parameter `subscription_id` when calling `delete_subscription`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in params:
            path_params['subscription_id'] = params['subscription_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription/{subscription_id}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def disable_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """disable_subscription  # noqa: E501

        This method disables a subscription, which prevents the subscription from providing notifications. To restart a subscription, call enableSubscription.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.disable_subscription(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.disable_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
        else:
            (data) = self.disable_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
            return data

    def disable_subscription_with_http_info(self, subscription_id, **kwargs):  # noqa: E501
        """disable_subscription  # noqa: E501

        This method disables a subscription, which prevents the subscription from providing notifications. To restart a subscription, call enableSubscription.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.disable_subscription_with_http_info(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['subscription_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method disable_subscription" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'subscription_id' is set
        if ('subscription_id' not in params or
                params['subscription_id'] is None):
            raise ValueError("Missing the required parameter `subscription_id` when calling `disable_subscription`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in params:
            path_params['subscription_id'] = params['subscription_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription/{subscription_id}/disable', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def enable_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """enable_subscription  # noqa: E501

        This method allows applications to enable a disabled subscription. To pause (or disable) an enabled subscription, call disableSubscription.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.enable_subscription(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.enable_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
        else:
            (data) = self.enable_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
            return data

    def enable_subscription_with_http_info(self, subscription_id, **kwargs):  # noqa: E501
        """enable_subscription  # noqa: E501

        This method allows applications to enable a disabled subscription. To pause (or disable) an enabled subscription, call disableSubscription.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.enable_subscription_with_http_info(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['subscription_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method enable_subscription" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'subscription_id' is set
        if ('subscription_id' not in params or
                params['subscription_id'] is None):
            raise ValueError("Missing the required parameter `subscription_id` when calling `enable_subscription`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in params:
            path_params['subscription_id'] = params['subscription_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription/{subscription_id}/enable', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """get_subscription  # noqa: E501

        This method allows applications to retrieve subscription details for the specified subscription. Specify the subscription to retrieve using the subscription_id. Use the getSubscriptions method to browse all subscriptions if you do not know the subscription_id. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_subscription(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: Subscription
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
            return data

    def get_subscription_with_http_info(self, subscription_id, **kwargs):  # noqa: E501
        """get_subscription  # noqa: E501

        This method allows applications to retrieve subscription details for the specified subscription. Specify the subscription to retrieve using the subscription_id. Use the getSubscriptions method to browse all subscriptions if you do not know the subscription_id. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_subscription_with_http_info(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: Subscription
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['subscription_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_subscription" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'subscription_id' is set
        if ('subscription_id' not in params or
                params['subscription_id'] is None):
            raise ValueError("Missing the required parameter `subscription_id` when calling `get_subscription`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in params:
            path_params['subscription_id'] = params['subscription_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription/{subscription_id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Subscription',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_subscriptions(self, **kwargs):  # noqa: E501
        """get_subscriptions  # noqa: E501

        This method allows applications to retrieve a list of all subscriptions. The list returned is a paginated collection of subscription resources. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_subscriptions(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str limit: The number of items, from the result set, returned in a single page. Range is from 10-100. If this parameter is omitted, the default value is used. Default: 20 Maximum: 100 items per page
        :param str continuation_token: The continuation token for the next set of results.
        :return: SubscriptionSearchResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_subscriptions_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_subscriptions_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_subscriptions_with_http_info(self, **kwargs):  # noqa: E501
        """get_subscriptions  # noqa: E501

        This method allows applications to retrieve a list of all subscriptions. The list returned is a paginated collection of subscription resources. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_subscriptions_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str limit: The number of items, from the result set, returned in a single page. Range is from 10-100. If this parameter is omitted, the default value is used. Default: 20 Maximum: 100 items per page
        :param str continuation_token: The continuation token for the next set of results.
        :return: SubscriptionSearchResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['limit', 'continuation_token']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_subscriptions" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501
        if 'continuation_token' in params:
            query_params.append(('continuation_token', params['continuation_token']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='SubscriptionSearchResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def test(self, subscription_id, **kwargs):  # noqa: E501
        """test  # noqa: E501

        This method triggers a mocked test payload that includes a notification ID, publish date, and so on. Use this method to test your subscription end-to-end. You can create the subscription in disabled mode, test it using this method, and when everything is ready, you can enable the subscription (see the enableSubscription method). Note: Use the notificationId to tell the difference between a test payload and a real payload.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.test(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.test_with_http_info(subscription_id, **kwargs)  # noqa: E501
        else:
            (data) = self.test_with_http_info(subscription_id, **kwargs)  # noqa: E501
            return data

    def test_with_http_info(self, subscription_id, **kwargs):  # noqa: E501
        """test  # noqa: E501

        This method triggers a mocked test payload that includes a notification ID, publish date, and so on. Use this method to test your subscription end-to-end. You can create the subscription in disabled mode, test it using this method, and when everything is ready, you can enable the subscription (see the enableSubscription method). Note: Use the notificationId to tell the difference between a test payload and a real payload.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.test_with_http_info(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['subscription_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method test" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'subscription_id' is set
        if ('subscription_id' not in params or
                params['subscription_id'] is None):
            raise ValueError("Missing the required parameter `subscription_id` when calling `test`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in params:
            path_params['subscription_id'] = params['subscription_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription/{subscription_id}/test', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def update_subscription(self, subscription_id, **kwargs):  # noqa: E501
        """update_subscription  # noqa: E501

        This method allows applications to update a subscription. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business. Note: This call returns an error if an application is not authorized to subscribe to a topic. You can pause and restart a subscription. See the disableSubscription and enableSubscription methods.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_subscription(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :param UpdateSubscriptionRequest body: The create subscription request.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.update_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
        else:
            (data) = self.update_subscription_with_http_info(subscription_id, **kwargs)  # noqa: E501
            return data

    def update_subscription_with_http_info(self, subscription_id, **kwargs):  # noqa: E501
        """update_subscription  # noqa: E501

        This method allows applications to update a subscription. Subscriptions allow applications to express interest in notifications and keep receiving the information relevant to their business. Note: This call returns an error if an application is not authorized to subscribe to a topic. You can pause and restart a subscription. See the disableSubscription and enableSubscription methods.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_subscription_with_http_info(subscription_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str subscription_id: The unique identifier for the subscription. (required)
        :param UpdateSubscriptionRequest body: The create subscription request.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['subscription_id', 'body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method update_subscription" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'subscription_id' is set
        if ('subscription_id' not in params or
                params['subscription_id'] is None):
            raise ValueError("Missing the required parameter `subscription_id` when calling `update_subscription`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in params:
            path_params['subscription_id'] = params['subscription_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_auth']  # noqa: E501

        return self.api_client.call_api(
            '/subscription/{subscription_id}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)