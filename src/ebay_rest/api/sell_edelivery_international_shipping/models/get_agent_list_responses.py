# coding: utf-8

"""
    EDIS public shipping API

    <div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span> This method is only available for Greater-China based sellers with an active eDIS account.</p></div><br>This API allows 3rd party developers in the Greater-China area to process package shipping details.  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class GetAgentListResponses(object):
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
        'agent_list': 'GetAgentListResponsesData'
    }

    attribute_map = {
        'agent_list': 'agentList'
    }

    def __init__(self, agent_list=None):  # noqa: E501
        """GetAgentListResponses - a model defined in Swagger"""  # noqa: E501
        self._agent_list = None
        self.discriminator = None
        if agent_list is not None:
            self.agent_list = agent_list

    @property
    def agent_list(self):
        """Gets the agent_list of this GetAgentListResponses.  # noqa: E501


        :return: The agent_list of this GetAgentListResponses.  # noqa: E501
        :rtype: GetAgentListResponsesData
        """
        return self._agent_list

    @agent_list.setter
    def agent_list(self, agent_list):
        """Sets the agent_list of this GetAgentListResponses.


        :param agent_list: The agent_list of this GetAgentListResponses.  # noqa: E501
        :type: GetAgentListResponsesData
        """

        self._agent_list = agent_list

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
        if issubclass(GetAgentListResponses, dict):
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
        if not isinstance(other, GetAgentListResponses):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
