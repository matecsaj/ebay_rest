# coding: utf-8

"""
    Metadata API

    The Metadata API has operations that retrieve configuration details pertaining to the different eBay marketplaces. In addition to marketplace information, the API also has operations that get information that helps sellers list items on eBay.  # noqa: E501

    OpenAPI spec version: v1.11.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class SpecificationRequest(object):
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
        'category_id': 'str',
        'compatibility_property_filters': 'list[PropertyFilterInner]',
        'dataset': 'str',
        'dataset_property_name': 'list[str]',
        'exact_match': 'bool',
        'pagination_input': 'PaginationInput',
        'sort_orders': 'list[SortOrderInner]',
        'specifications': 'list[PropertyFilterInner]'
    }

    attribute_map = {
        'category_id': 'categoryId',
        'compatibility_property_filters': 'compatibilityPropertyFilters',
        'dataset': 'dataset',
        'dataset_property_name': 'datasetPropertyName',
        'exact_match': 'exactMatch',
        'pagination_input': 'paginationInput',
        'sort_orders': 'sortOrders',
        'specifications': 'specifications'
    }

    def __init__(self, category_id=None, compatibility_property_filters=None, dataset=None, dataset_property_name=None, exact_match=None, pagination_input=None, sort_orders=None, specifications=None):  # noqa: E501
        """SpecificationRequest - a model defined in Swagger"""  # noqa: E501
        self._category_id = None
        self._compatibility_property_filters = None
        self._dataset = None
        self._dataset_property_name = None
        self._exact_match = None
        self._pagination_input = None
        self._sort_orders = None
        self._specifications = None
        self.discriminator = None
        if category_id is not None:
            self.category_id = category_id
        if compatibility_property_filters is not None:
            self.compatibility_property_filters = compatibility_property_filters
        if dataset is not None:
            self.dataset = dataset
        if dataset_property_name is not None:
            self.dataset_property_name = dataset_property_name
        if exact_match is not None:
            self.exact_match = exact_match
        if pagination_input is not None:
            self.pagination_input = pagination_input
        if sort_orders is not None:
            self.sort_orders = sort_orders
        if specifications is not None:
            self.specifications = specifications

    @property
    def category_id(self):
        """Gets the category_id of this SpecificationRequest.  # noqa: E501

        The unique identifier of the eBay leaf category for which compatibility details are being retrieved. This category must be a valid eBay category on the specified eBay marketplace, and the category must support parts compatibility for cars, trucks, or motorcycles.<br><br>Use the <a href=\"/api-docs/sell/metadata/resources/marketplace/methods/getAutomotivePartsCompatibilityPolicies\" target=\"_blank \">getAutomotivePartsCompatibilityPolicies</a> method to retrieve a list of categories that support parts compatibility by specification. For the categories in the response that support compatibility by specification, you’ll see <code>SPECIFICATIONS</code> as the value for the <b>compatibilityBasedOn</b> field   # noqa: E501

        :return: The category_id of this SpecificationRequest.  # noqa: E501
        :rtype: str
        """
        return self._category_id

    @category_id.setter
    def category_id(self, category_id):
        """Sets the category_id of this SpecificationRequest.

        The unique identifier of the eBay leaf category for which compatibility details are being retrieved. This category must be a valid eBay category on the specified eBay marketplace, and the category must support parts compatibility for cars, trucks, or motorcycles.<br><br>Use the <a href=\"/api-docs/sell/metadata/resources/marketplace/methods/getAutomotivePartsCompatibilityPolicies\" target=\"_blank \">getAutomotivePartsCompatibilityPolicies</a> method to retrieve a list of categories that support parts compatibility by specification. For the categories in the response that support compatibility by specification, you’ll see <code>SPECIFICATIONS</code> as the value for the <b>compatibilityBasedOn</b> field   # noqa: E501

        :param category_id: The category_id of this SpecificationRequest.  # noqa: E501
        :type: str
        """

        self._category_id = category_id

    @property
    def compatibility_property_filters(self):
        """Gets the compatibility_property_filters of this SpecificationRequest.  # noqa: E501

        This comma-delimited array can be used to restrict the number of compatible application name-value pairs returned in the response by specifying the properties that the seller wishes to be included in the response.<br><br>Only compatible applications with the specified properties will be returned. Properties that can be specified here include make, model, year, and trim.  # noqa: E501

        :return: The compatibility_property_filters of this SpecificationRequest.  # noqa: E501
        :rtype: list[PropertyFilterInner]
        """
        return self._compatibility_property_filters

    @compatibility_property_filters.setter
    def compatibility_property_filters(self, compatibility_property_filters):
        """Sets the compatibility_property_filters of this SpecificationRequest.

        This comma-delimited array can be used to restrict the number of compatible application name-value pairs returned in the response by specifying the properties that the seller wishes to be included in the response.<br><br>Only compatible applications with the specified properties will be returned. Properties that can be specified here include make, model, year, and trim.  # noqa: E501

        :param compatibility_property_filters: The compatibility_property_filters of this SpecificationRequest.  # noqa: E501
        :type: list[PropertyFilterInner]
        """

        self._compatibility_property_filters = compatibility_property_filters

    @property
    def dataset(self):
        """Gets the dataset of this SpecificationRequest.  # noqa: E501

        This field can be used to define the type of properties that will be returned in the response.<br><br> For example, if you specify <code>Searchable</code>, the compatibility details will contain properties that can be used to search for products, such as make or model.<br><br><span class=\"tablenote\"><b>Note:</b> This field cannot be used alongside <b>dataPropertyName</b>. If both are used, an error will occur.</span><br><b>Valid values:</b><ul><li><code>DisplayableProductDetails</code>: Properties for use in a user interface to describe products.</li><li><code>DisplayableSearchResults</code>: Properties for use in results for product searches.</li><li><code>Searchable</code>: Properties for use in searches.</li><li><code>Sortable</code>: Properties that are suitable for sorting.</li></ul><b>Default value:</b> <code>DisplayableSearchResults</code>  # noqa: E501

        :return: The dataset of this SpecificationRequest.  # noqa: E501
        :rtype: str
        """
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        """Sets the dataset of this SpecificationRequest.

        This field can be used to define the type of properties that will be returned in the response.<br><br> For example, if you specify <code>Searchable</code>, the compatibility details will contain properties that can be used to search for products, such as make or model.<br><br><span class=\"tablenote\"><b>Note:</b> This field cannot be used alongside <b>dataPropertyName</b>. If both are used, an error will occur.</span><br><b>Valid values:</b><ul><li><code>DisplayableProductDetails</code>: Properties for use in a user interface to describe products.</li><li><code>DisplayableSearchResults</code>: Properties for use in results for product searches.</li><li><code>Searchable</code>: Properties for use in searches.</li><li><code>Sortable</code>: Properties that are suitable for sorting.</li></ul><b>Default value:</b> <code>DisplayableSearchResults</code>  # noqa: E501

        :param dataset: The dataset of this SpecificationRequest.  # noqa: E501
        :type: str
        """

        self._dataset = dataset

    @property
    def dataset_property_name(self):
        """Gets the dataset_property_name of this SpecificationRequest.  # noqa: E501

        This comma-delimited array can be used to define the specific property name(s) that will be returned in the response.<br><br>For example, if you specify <code>Engine</code>, the result set will only contain engines that are compatible with the input criteria.<br><br><span class=\"tablenote\"><b>Note:</b> This array cannot be used alongside <b>dataset</b>. If both are used, an error will occur.</span>  # noqa: E501

        :return: The dataset_property_name of this SpecificationRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._dataset_property_name

    @dataset_property_name.setter
    def dataset_property_name(self, dataset_property_name):
        """Sets the dataset_property_name of this SpecificationRequest.

        This comma-delimited array can be used to define the specific property name(s) that will be returned in the response.<br><br>For example, if you specify <code>Engine</code>, the result set will only contain engines that are compatible with the input criteria.<br><br><span class=\"tablenote\"><b>Note:</b> This array cannot be used alongside <b>dataset</b>. If both are used, an error will occur.</span>  # noqa: E501

        :param dataset_property_name: The dataset_property_name of this SpecificationRequest.  # noqa: E501
        :type: list[str]
        """

        self._dataset_property_name = dataset_property_name

    @property
    def exact_match(self):
        """Gets the exact_match of this SpecificationRequest.  # noqa: E501

        This boolean can be used to specify that the compatibilities returned in the response are to be defined by an exact match on the input value of specification properties.<br><br>By default, an expanded compatibility match is done when it applies, such as for Load Index, where a compatible vehicle is one that has a load index requirement that is less than or equal to the input. By specifying this field as <code>true</code>, only exact matches are returned.  # noqa: E501

        :return: The exact_match of this SpecificationRequest.  # noqa: E501
        :rtype: bool
        """
        return self._exact_match

    @exact_match.setter
    def exact_match(self, exact_match):
        """Sets the exact_match of this SpecificationRequest.

        This boolean can be used to specify that the compatibilities returned in the response are to be defined by an exact match on the input value of specification properties.<br><br>By default, an expanded compatibility match is done when it applies, such as for Load Index, where a compatible vehicle is one that has a load index requirement that is less than or equal to the input. By specifying this field as <code>true</code>, only exact matches are returned.  # noqa: E501

        :param exact_match: The exact_match of this SpecificationRequest.  # noqa: E501
        :type: bool
        """

        self._exact_match = exact_match

    @property
    def pagination_input(self):
        """Gets the pagination_input of this SpecificationRequest.  # noqa: E501


        :return: The pagination_input of this SpecificationRequest.  # noqa: E501
        :rtype: PaginationInput
        """
        return self._pagination_input

    @pagination_input.setter
    def pagination_input(self, pagination_input):
        """Sets the pagination_input of this SpecificationRequest.


        :param pagination_input: The pagination_input of this SpecificationRequest.  # noqa: E501
        :type: PaginationInput
        """

        self._pagination_input = pagination_input

    @property
    def sort_orders(self):
        """Gets the sort_orders of this SpecificationRequest.  # noqa: E501

        This array specifies the sorting order of the compatibility properties. Any of the searchable properties can be used to specify search order. Up to 5 levels of sort order may be specified.<br><br><span class=\"tablenote\"><b>Note:</b> If no sort order is specified through this field, the default sort order of <b>popularity descending</b> is applied.</span>  # noqa: E501

        :return: The sort_orders of this SpecificationRequest.  # noqa: E501
        :rtype: list[SortOrderInner]
        """
        return self._sort_orders

    @sort_orders.setter
    def sort_orders(self, sort_orders):
        """Sets the sort_orders of this SpecificationRequest.

        This array specifies the sorting order of the compatibility properties. Any of the searchable properties can be used to specify search order. Up to 5 levels of sort order may be specified.<br><br><span class=\"tablenote\"><b>Note:</b> If no sort order is specified through this field, the default sort order of <b>popularity descending</b> is applied.</span>  # noqa: E501

        :param sort_orders: The sort_orders of this SpecificationRequest.  # noqa: E501
        :type: list[SortOrderInner]
        """

        self._sort_orders = sort_orders

    @property
    def specifications(self):
        """Gets the specifications of this SpecificationRequest.  # noqa: E501

        This array defines the specifications of the part, in the form of name-value pairs, for which compatible applications will be retrieved.  # noqa: E501

        :return: The specifications of this SpecificationRequest.  # noqa: E501
        :rtype: list[PropertyFilterInner]
        """
        return self._specifications

    @specifications.setter
    def specifications(self, specifications):
        """Sets the specifications of this SpecificationRequest.

        This array defines the specifications of the part, in the form of name-value pairs, for which compatible applications will be retrieved.  # noqa: E501

        :param specifications: The specifications of this SpecificationRequest.  # noqa: E501
        :type: list[PropertyFilterInner]
        """

        self._specifications = specifications

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
        if issubclass(SpecificationRequest, dict):
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
        if not isinstance(other, SpecificationRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
