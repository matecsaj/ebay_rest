# coding: utf-8

"""
    Notification API

    The eBay Notification API enables management of the entire end-to-end eBay notification experience by allowing users to:<ul><li>Browse for supported notification topics and retrieve topic details</li><li>Create, configure, and manage notification destination endpoints</li><li>Configure, manage, and test notification subscriptions</li><li>Process eBay notifications and verify the integrity of the message payload</li></ul>  # noqa: E501

    OpenAPI spec version: v1.5.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Topic(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'topic_id': 'str',
        'description': 'str',
        'authorization_scopes': 'list[str]',
        'status': 'str',
        'context': 'str',
        'scope': 'str',
        'supported_payloads': 'list[PayloadDetail]',
        'filterable': 'bool'
    }

    attribute_map = {
        'topic_id': 'topicId',
        'description': 'description',
        'authorization_scopes': 'authorizationScopes',
        'status': 'status',
        'context': 'context',
        'scope': 'scope',
        'supported_payloads': 'supportedPayloads',
        'filterable': 'filterable'
    }

    def __init__(self, topic_id=None, description=None, authorization_scopes=None, status=None, context=None, scope=None, supported_payloads=None, filterable=None):  # noqa: E501
        """Topic - a model defined in Swagger"""  # noqa: E501
        self._topic_id = None
        self._description = None
        self._authorization_scopes = None
        self._status = None
        self._context = None
        self._scope = None
        self._supported_payloads = None
        self._filterable = None
        self.discriminator = None
        if topic_id is not None:
            self.topic_id = topic_id
        if description is not None:
            self.description = description
        if authorization_scopes is not None:
            self.authorization_scopes = authorization_scopes
        if status is not None:
            self.status = status
        if context is not None:
            self.context = context
        if scope is not None:
            self.scope = scope
        if supported_payloads is not None:
            self.supported_payloads = supported_payloads
        if filterable is not None:
            self.filterable = filterable

    @property
    def topic_id(self):
        """Gets the topic_id of this Topic.  # noqa: E501

        The unique identifier for the topic.  # noqa: E501

        :return: The topic_id of this Topic.  # noqa: E501
        :rtype: str
        """
        return self._topic_id

    @topic_id.setter
    def topic_id(self, topic_id):
        """Sets the topic_id of this Topic.

        The unique identifier for the topic.  # noqa: E501

        :param topic_id: The topic_id of this Topic.  # noqa: E501
        :type: str
        """

        self._topic_id = topic_id

    @property
    def description(self):
        """Gets the description of this Topic.  # noqa: E501

        The description of the topic.  # noqa: E501

        :return: The description of this Topic.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Topic.

        The description of the topic.  # noqa: E501

        :param description: The description of this Topic.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def authorization_scopes(self):
        """Gets the authorization_scopes of this Topic.  # noqa: E501

        The authorization scopes required to subscribe to this topic.  # noqa: E501

        :return: The authorization_scopes of this Topic.  # noqa: E501
        :rtype: list[str]
        """
        return self._authorization_scopes

    @authorization_scopes.setter
    def authorization_scopes(self, authorization_scopes):
        """Sets the authorization_scopes of this Topic.

        The authorization scopes required to subscribe to this topic.  # noqa: E501

        :param authorization_scopes: The authorization_scopes of this Topic.  # noqa: E501
        :type: list[str]
        """

        self._authorization_scopes = authorization_scopes

    @property
    def status(self):
        """Gets the status of this Topic.  # noqa: E501

        The status of this topic. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/notification/types/api:StatusEnum'>eBay API documentation</a>  # noqa: E501

        :return: The status of this Topic.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Topic.

        The status of this topic. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/notification/types/api:StatusEnum'>eBay API documentation</a>  # noqa: E501

        :param status: The status of this Topic.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def context(self):
        """Gets the context of this Topic.  # noqa: E501

        The business context associated with this topic. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/notification/types/api:ContextEnum'>eBay API documentation</a>  # noqa: E501

        :return: The context of this Topic.  # noqa: E501
        :rtype: str
        """
        return self._context

    @context.setter
    def context(self, context):
        """Sets the context of this Topic.

        The business context associated with this topic. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/notification/types/api:ContextEnum'>eBay API documentation</a>  # noqa: E501

        :param context: The context of this Topic.  # noqa: E501
        :type: str
        """

        self._context = context

    @property
    def scope(self):
        """Gets the scope of this Topic.  # noqa: E501

        The scope of this topic. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/notification/types/api:ScopeEnum'>eBay API documentation</a>  # noqa: E501

        :return: The scope of this Topic.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this Topic.

        The scope of this topic. For implementation help, refer to <a href='https://developer.ebay.com/api-docs/commerce/notification/types/api:ScopeEnum'>eBay API documentation</a>  # noqa: E501

        :param scope: The scope of this Topic.  # noqa: E501
        :type: str
        """

        self._scope = scope

    @property
    def supported_payloads(self):
        """Gets the supported_payloads of this Topic.  # noqa: E501

        The supported payloads for this topic.  # noqa: E501

        :return: The supported_payloads of this Topic.  # noqa: E501
        :rtype: list[PayloadDetail]
        """
        return self._supported_payloads

    @supported_payloads.setter
    def supported_payloads(self, supported_payloads):
        """Sets the supported_payloads of this Topic.

        The supported payloads for this topic.  # noqa: E501

        :param supported_payloads: The supported_payloads of this Topic.  # noqa: E501
        :type: list[PayloadDetail]
        """

        self._supported_payloads = supported_payloads

    @property
    def filterable(self):
        """Gets the filterable of this Topic.  # noqa: E501

        The indicator of whether this topic is filterable or not.  # noqa: E501

        :return: The filterable of this Topic.  # noqa: E501
        :rtype: bool
        """
        return self._filterable

    @filterable.setter
    def filterable(self, filterable):
        """Sets the filterable of this Topic.

        The indicator of whether this topic is filterable or not.  # noqa: E501

        :param filterable: The filterable of this Topic.  # noqa: E501
        :type: bool
        """

        self._filterable = filterable

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Topic, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Topic):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
