# coding: utf-8

"""
    Metadata API

    The Metadata API has operations that retrieve configuration details pertaining to the different eBay marketplaces. In addition to marketplace information, the API also has operations that get information that helps sellers list items on eBay.  # noqa: E501

    OpenAPI spec version: v1.9.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ProductRequest(object):
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
        'application_property_filters': 'list[PropertyFilterInner]',
        'dataset': 'list[str]',
        'dataset_property_name': 'list[str]',
        'disabled_product_filter': 'DisabledProductFilter',
        'pagination_input': 'PaginationInput',
        'product_identifier': 'ProductIdentifier',
        'sort_orders': 'list[SortOrderInner]'
    }

    attribute_map = {
        'application_property_filters': 'applicationPropertyFilters',
        'dataset': 'dataset',
        'dataset_property_name': 'datasetPropertyName',
        'disabled_product_filter': 'disabledProductFilter',
        'pagination_input': 'paginationInput',
        'product_identifier': 'productIdentifier',
        'sort_orders': 'sortOrders'
    }

    def __init__(self, application_property_filters=None, dataset=None, dataset_property_name=None, disabled_product_filter=None, pagination_input=None, product_identifier=None, sort_orders=None):  # noqa: E501
        """ProductRequest - a model defined in Swagger"""  # noqa: E501
        self._application_property_filters = None
        self._dataset = None
        self._dataset_property_name = None
        self._disabled_product_filter = None
        self._pagination_input = None
        self._product_identifier = None
        self._sort_orders = None
        self.discriminator = None
        if application_property_filters is not None:
            self.application_property_filters = application_property_filters
        if dataset is not None:
            self.dataset = dataset
        if dataset_property_name is not None:
            self.dataset_property_name = dataset_property_name
        if disabled_product_filter is not None:
            self.disabled_product_filter = disabled_product_filter
        if pagination_input is not None:
            self.pagination_input = pagination_input
        if product_identifier is not None:
            self.product_identifier = product_identifier
        if sort_orders is not None:
            self.sort_orders = sort_orders

    @property
    def application_property_filters(self):
        """Gets the application_property_filters of this ProductRequest.  # noqa: E501

        This array is used to filter the properties of an application, such as a vehicle's make or model, that will be returned in the response.<br><br>Application property filters are specified as name-value pairs. Only products compatible with these name-value pairs will be returned.  # noqa: E501

        :return: The application_property_filters of this ProductRequest.  # noqa: E501
        :rtype: list[PropertyFilterInner]
        """
        return self._application_property_filters

    @application_property_filters.setter
    def application_property_filters(self, application_property_filters):
        """Sets the application_property_filters of this ProductRequest.

        This array is used to filter the properties of an application, such as a vehicle's make or model, that will be returned in the response.<br><br>Application property filters are specified as name-value pairs. Only products compatible with these name-value pairs will be returned.  # noqa: E501

        :param application_property_filters: The application_property_filters of this ProductRequest.  # noqa: E501
        :type: list[PropertyFilterInner]
        """

        self._application_property_filters = application_property_filters

    @property
    def dataset(self):
        """Gets the dataset of this ProductRequest.  # noqa: E501

        This array defines the type of properties that are returned for the catalog-enabled category.<br><br>For example, if you specify <code>Searchable</code>, the compatibility details will contain properties that can be used to search for products, such as make or model.<br><br><span class=\"tablenote\"><b>Note:</b> This field cannot be used alongside <b>dataPropertyName</b>. If both are used, an error will occur.</span><br><b>Valid values:</b><ul><li><code>DisplayableProductDetails</code>: Properties for use in a user interface to describe products.</li><li><code>DisplayableSearchResults</code>: Properties for use in results for product searches.</li><li><code>Searchable</code>: Properties for use in searches.</li><li><code>Sortable</code>: Properties that are suitable for sorting.</li></ul><br><b>Default:</b> <code>DisplayableSearchResults</code>  # noqa: E501

        :return: The dataset of this ProductRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        """Sets the dataset of this ProductRequest.

        This array defines the type of properties that are returned for the catalog-enabled category.<br><br>For example, if you specify <code>Searchable</code>, the compatibility details will contain properties that can be used to search for products, such as make or model.<br><br><span class=\"tablenote\"><b>Note:</b> This field cannot be used alongside <b>dataPropertyName</b>. If both are used, an error will occur.</span><br><b>Valid values:</b><ul><li><code>DisplayableProductDetails</code>: Properties for use in a user interface to describe products.</li><li><code>DisplayableSearchResults</code>: Properties for use in results for product searches.</li><li><code>Searchable</code>: Properties for use in searches.</li><li><code>Sortable</code>: Properties that are suitable for sorting.</li></ul><br><b>Default:</b> <code>DisplayableSearchResults</code>  # noqa: E501

        :param dataset: The dataset of this ProductRequest.  # noqa: E501
        :type: list[str]
        """

        self._dataset = dataset

    @property
    def dataset_property_name(self):
        """Gets the dataset_property_name of this ProductRequest.  # noqa: E501

        This comma-delimted array can be used to define the specific property name(s) that will be returned in the response.<br><br>For example, if you specify <code>Engine</code>, the result set will only contain engines that are compatible with the input criteria.<br><br><span class=\"tablenote\"><b>Note:</b> This array cannot be used alongside <b>dataset</b>. If both are used, an error will occur.</span>  # noqa: E501

        :return: The dataset_property_name of this ProductRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._dataset_property_name

    @dataset_property_name.setter
    def dataset_property_name(self, dataset_property_name):
        """Sets the dataset_property_name of this ProductRequest.

        This comma-delimted array can be used to define the specific property name(s) that will be returned in the response.<br><br>For example, if you specify <code>Engine</code>, the result set will only contain engines that are compatible with the input criteria.<br><br><span class=\"tablenote\"><b>Note:</b> This array cannot be used alongside <b>dataset</b>. If both are used, an error will occur.</span>  # noqa: E501

        :param dataset_property_name: The dataset_property_name of this ProductRequest.  # noqa: E501
        :type: list[str]
        """

        self._dataset_property_name = dataset_property_name

    @property
    def disabled_product_filter(self):
        """Gets the disabled_product_filter of this ProductRequest.  # noqa: E501


        :return: The disabled_product_filter of this ProductRequest.  # noqa: E501
        :rtype: DisabledProductFilter
        """
        return self._disabled_product_filter

    @disabled_product_filter.setter
    def disabled_product_filter(self, disabled_product_filter):
        """Sets the disabled_product_filter of this ProductRequest.


        :param disabled_product_filter: The disabled_product_filter of this ProductRequest.  # noqa: E501
        :type: DisabledProductFilter
        """

        self._disabled_product_filter = disabled_product_filter

    @property
    def pagination_input(self):
        """Gets the pagination_input of this ProductRequest.  # noqa: E501


        :return: The pagination_input of this ProductRequest.  # noqa: E501
        :rtype: PaginationInput
        """
        return self._pagination_input

    @pagination_input.setter
    def pagination_input(self, pagination_input):
        """Sets the pagination_input of this ProductRequest.


        :param pagination_input: The pagination_input of this ProductRequest.  # noqa: E501
        :type: PaginationInput
        """

        self._pagination_input = pagination_input

    @property
    def product_identifier(self):
        """Gets the product_identifier of this ProductRequest.  # noqa: E501


        :return: The product_identifier of this ProductRequest.  # noqa: E501
        :rtype: ProductIdentifier
        """
        return self._product_identifier

    @product_identifier.setter
    def product_identifier(self, product_identifier):
        """Sets the product_identifier of this ProductRequest.


        :param product_identifier: The product_identifier of this ProductRequest.  # noqa: E501
        :type: ProductIdentifier
        """

        self._product_identifier = product_identifier

    @property
    def sort_orders(self):
        """Gets the sort_orders of this ProductRequest.  # noqa: E501

        This array controls the sort order of compatibility properties.  # noqa: E501

        :return: The sort_orders of this ProductRequest.  # noqa: E501
        :rtype: list[SortOrderInner]
        """
        return self._sort_orders

    @sort_orders.setter
    def sort_orders(self, sort_orders):
        """Sets the sort_orders of this ProductRequest.

        This array controls the sort order of compatibility properties.  # noqa: E501

        :param sort_orders: The sort_orders of this ProductRequest.  # noqa: E501
        :type: list[SortOrderInner]
        """

        self._sort_orders = sort_orders

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
        if issubclass(ProductRequest, dict):
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
        if not isinstance(other, ProductRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other