# coding: utf-8

"""
    Inventory API

    The Inventory API is used to create and manage inventory, and then to publish and manage this inventory on an eBay marketplace. There are also methods in this API that will convert eligible, active eBay listings into the Inventory API model.  # noqa: E501

    OpenAPI spec version: 1.18.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class InventoryItemWithSkuLocale(object):
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
        'availability': 'Availability',
        'condition': 'str',
        'condition_description': 'str',
        'condition_descriptors': 'list[ConditionDescriptor]',
        'locale': 'str',
        'package_weight_and_size': 'PackageWeightAndSize',
        'product': 'Product',
        'sku': 'str'
    }

    attribute_map = {
        'availability': 'availability',
        'condition': 'condition',
        'condition_description': 'conditionDescription',
        'condition_descriptors': 'conditionDescriptors',
        'locale': 'locale',
        'package_weight_and_size': 'packageWeightAndSize',
        'product': 'product',
        'sku': 'sku'
    }

    def __init__(self, availability=None, condition=None, condition_description=None, condition_descriptors=None, locale=None, package_weight_and_size=None, product=None, sku=None):  # noqa: E501
        """InventoryItemWithSkuLocale - a model defined in Swagger"""  # noqa: E501
        self._availability = None
        self._condition = None
        self._condition_description = None
        self._condition_descriptors = None
        self._locale = None
        self._package_weight_and_size = None
        self._product = None
        self._sku = None
        self.discriminator = None
        if availability is not None:
            self.availability = availability
        if condition is not None:
            self.condition = condition
        if condition_description is not None:
            self.condition_description = condition_description
        if condition_descriptors is not None:
            self.condition_descriptors = condition_descriptors
        if locale is not None:
            self.locale = locale
        if package_weight_and_size is not None:
            self.package_weight_and_size = package_weight_and_size
        if product is not None:
            self.product = product
        if sku is not None:
            self.sku = sku

    @property
    def availability(self):
        """Gets the availability of this InventoryItemWithSkuLocale.  # noqa: E501


        :return: The availability of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: Availability
        """
        return self._availability

    @availability.setter
    def availability(self, availability):
        """Sets the availability of this InventoryItemWithSkuLocale.


        :param availability: The availability of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: Availability
        """

        self._availability = availability

    @property
    def condition(self):
        """Gets the condition of this InventoryItemWithSkuLocale.  # noqa: E501

        This enumeration value indicates the condition of the item. Supported item condition values will vary by eBay site and category. To see which item condition values that a particular eBay category supports, use the <a href=\"/api-docs/sell/metadata/resources/marketplace/methods/getItemConditionPolicies\" target=\"_blank\">getItemConditionPolicies</a> method of the <strong>Metadata API</strong>. This method returns condition ID values that map to the enumeration values defined in the <a href=\"/api-docs/sell/inventory/types/slr:ConditionEnum\" target=\"_blank\">ConditionEnum</a> type. The <a href=\"/api-docs/sell/static/metadata/condition-id-values.html\" target=\"_blank\">Item condition ID and name values</a> topic in the <strong>Selling Integration Guide</strong> has a table that maps condition ID values to <strong>ConditionEnum</strong> values. The <strong>getItemConditionPolicies</strong> call reference page has more information.<br><br>A <strong>condition</strong> value is optional up until the seller is ready to publish an offer with the SKU, at which time it becomes required for most eBay categories. <br><br><span class=\"tablenote\"> <strong>Note:</strong> The 'Manufacturer Refurbished' item condition is no longer a valid item condition on any eBay marketplace, and to reflect this change, the <code>MANUFACTURER_REFURBISHED</code> value is no longer applicable, and should not be used. With Version 1.13.0, the <code>CERTIFIED_REFURBISHED</code> enumeration value has been introduced, and CR-eligible sellers should make a note to start using <code>CERTIFIED_REFURBISHED</code> from this point forward. For the time being, if the <code>MANUFACTURER_REFURBISHED</code> enum is used for any of the SKUs in a <strong>bulkCreateOrReplaceInventoryItem</strong> method, it will be accepted but automatically converted by eBay to <code>CERTIFIED_REFURBISHED</code>. <br><br>To list an item as 'Certified Refurbished', a seller must be pre-qualified by eBay for this feature. Any seller who is not eligible for this feature will be blocked if they try to create a new listing or revise an existing listing with this item condition. <br><br>Any seller that is interested in eligibility requirements to list with 'Certified Refurbished' should see the <a href=\"https://pages.ebay.com/seller-center/listing-and-marketing/certified-refurbished-program.html \" target=\"_blank\">Certified refurbished program</a> page in Seller Center. </span><div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span>For trading card listings in Non-Sport Trading Card Singles (183050), CCG Individual Cards (183454), and Sports Trading Card Singles (261328) categories, sellers must use either LIKE_NEW (2750) or USED_VERY_GOOD (4000) item condition. No other item conditions will be accepted. Use of these item conditions require the seller to use the conditionDescriptors array to provide one or more applicable Condition Descriptor name-value pairs. See the conditionDescriptors field description for more information. If these requierments are not followed,  publishOffer, updateOffer, bulkPublishOffer, and publishOfferByInventoryItemGroup methods will fail when trying to create new listings.</p></span></div><br><div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span>Publish offer note: This field is required before an offer can be published to create an active listing. </p></span></div> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:ConditionEnum'>eBay API documentation</a>  # noqa: E501

        :return: The condition of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: str
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Sets the condition of this InventoryItemWithSkuLocale.

        This enumeration value indicates the condition of the item. Supported item condition values will vary by eBay site and category. To see which item condition values that a particular eBay category supports, use the <a href=\"/api-docs/sell/metadata/resources/marketplace/methods/getItemConditionPolicies\" target=\"_blank\">getItemConditionPolicies</a> method of the <strong>Metadata API</strong>. This method returns condition ID values that map to the enumeration values defined in the <a href=\"/api-docs/sell/inventory/types/slr:ConditionEnum\" target=\"_blank\">ConditionEnum</a> type. The <a href=\"/api-docs/sell/static/metadata/condition-id-values.html\" target=\"_blank\">Item condition ID and name values</a> topic in the <strong>Selling Integration Guide</strong> has a table that maps condition ID values to <strong>ConditionEnum</strong> values. The <strong>getItemConditionPolicies</strong> call reference page has more information.<br><br>A <strong>condition</strong> value is optional up until the seller is ready to publish an offer with the SKU, at which time it becomes required for most eBay categories. <br><br><span class=\"tablenote\"> <strong>Note:</strong> The 'Manufacturer Refurbished' item condition is no longer a valid item condition on any eBay marketplace, and to reflect this change, the <code>MANUFACTURER_REFURBISHED</code> value is no longer applicable, and should not be used. With Version 1.13.0, the <code>CERTIFIED_REFURBISHED</code> enumeration value has been introduced, and CR-eligible sellers should make a note to start using <code>CERTIFIED_REFURBISHED</code> from this point forward. For the time being, if the <code>MANUFACTURER_REFURBISHED</code> enum is used for any of the SKUs in a <strong>bulkCreateOrReplaceInventoryItem</strong> method, it will be accepted but automatically converted by eBay to <code>CERTIFIED_REFURBISHED</code>. <br><br>To list an item as 'Certified Refurbished', a seller must be pre-qualified by eBay for this feature. Any seller who is not eligible for this feature will be blocked if they try to create a new listing or revise an existing listing with this item condition. <br><br>Any seller that is interested in eligibility requirements to list with 'Certified Refurbished' should see the <a href=\"https://pages.ebay.com/seller-center/listing-and-marketing/certified-refurbished-program.html \" target=\"_blank\">Certified refurbished program</a> page in Seller Center. </span><div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span>For trading card listings in Non-Sport Trading Card Singles (183050), CCG Individual Cards (183454), and Sports Trading Card Singles (261328) categories, sellers must use either LIKE_NEW (2750) or USED_VERY_GOOD (4000) item condition. No other item conditions will be accepted. Use of these item conditions require the seller to use the conditionDescriptors array to provide one or more applicable Condition Descriptor name-value pairs. See the conditionDescriptors field description for more information. If these requierments are not followed,  publishOffer, updateOffer, bulkPublishOffer, and publishOfferByInventoryItemGroup methods will fail when trying to create new listings.</p></span></div><br><div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span>Publish offer note: This field is required before an offer can be published to create an active listing. </p></span></div> For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:ConditionEnum'>eBay API documentation</a>  # noqa: E501

        :param condition: The condition of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: str
        """

        self._condition = condition

    @property
    def condition_description(self):
        """Gets the condition_description of this InventoryItemWithSkuLocale.  # noqa: E501

        This string field is used by the seller to more clearly describe the condition of a used inventory item, or an inventory item whose <strong>condition</strong> value is not <code>NEW</code>, <code>LIKE_NEW</code>, <code>NEW_OTHER</code>, or <code>NEW_WITH_DEFECTS</code>.<br><br>The <strong>conditionDescription</strong> field is available for all eBay categories. If the <strong>conditionDescription</strong> field is used with an item in one of the new conditions (mentioned in previous paragraph), eBay will simply ignore this field if included, and eBay will return a warning message to the user. <br><br>This field should only be used to further clarify the condition of the used item. It should not be used for branding, promotions, shipping, returns, payment or other information unrelated to the condition of the used item. Make sure that the <strong>condition</strong> value, condition description, listing description, and the item's pictures do not contradict one another. <br><br>This field is not always required, but is required if an inventory item is being updated and a condition description already exists for that inventory item. <br><br>This field is returned in the <strong>getInventoryItem</strong>, <strong>bulkGetInventoryItem</strong>, and <strong>getInventoryItems</strong> calls if a condition description was provided for a used inventory item.<br><br><b>Max Length</b>: 1000  # noqa: E501

        :return: The condition_description of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: str
        """
        return self._condition_description

    @condition_description.setter
    def condition_description(self, condition_description):
        """Sets the condition_description of this InventoryItemWithSkuLocale.

        This string field is used by the seller to more clearly describe the condition of a used inventory item, or an inventory item whose <strong>condition</strong> value is not <code>NEW</code>, <code>LIKE_NEW</code>, <code>NEW_OTHER</code>, or <code>NEW_WITH_DEFECTS</code>.<br><br>The <strong>conditionDescription</strong> field is available for all eBay categories. If the <strong>conditionDescription</strong> field is used with an item in one of the new conditions (mentioned in previous paragraph), eBay will simply ignore this field if included, and eBay will return a warning message to the user. <br><br>This field should only be used to further clarify the condition of the used item. It should not be used for branding, promotions, shipping, returns, payment or other information unrelated to the condition of the used item. Make sure that the <strong>condition</strong> value, condition description, listing description, and the item's pictures do not contradict one another. <br><br>This field is not always required, but is required if an inventory item is being updated and a condition description already exists for that inventory item. <br><br>This field is returned in the <strong>getInventoryItem</strong>, <strong>bulkGetInventoryItem</strong>, and <strong>getInventoryItems</strong> calls if a condition description was provided for a used inventory item.<br><br><b>Max Length</b>: 1000  # noqa: E501

        :param condition_description: The condition_description of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: str
        """

        self._condition_description = condition_description

    @property
    def condition_descriptors(self):
        """Gets the condition_descriptors of this InventoryItemWithSkuLocale.  # noqa: E501

        <div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span>For trading card listings in Non-Sport Trading Card Singles (183050), CCG Individual Cards (183454), and Sports Trading Card Singles (261328) categories, sellers must use either LIKE_NEW (2750) or USED_VERY_GOOD (4000) item condition. No other item conditions will be accepted. Use of these item conditions require the seller to use the conditionDescriptors array to provide one or more applicable Condition Descriptor name-value pairs. See the conditionDescriptors field description for more information. If these requierments are not followed,  publishOffer, updateOffer, bulkPublishOffer, and publishOfferByInventoryItemGroup methods will fail when trying to create new listings.</p></span></div><br><br>This container is used by the seller to provide additional information about the condition of an item in a structured format. Condition descriptors are name-value attributes that can be either closed set or open text inputs.<br><br>To retrieve all condition descriptor numeric IDs for a category, use the <a href=\"/api-docs/sell/metadata/resources/marketplace/methods/getItemConditionPolicies\" target=\"_blank\">getItemConditionPolicies</a> method of the Metadata API. <br><br>  # noqa: E501

        :return: The condition_descriptors of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: list[ConditionDescriptor]
        """
        return self._condition_descriptors

    @condition_descriptors.setter
    def condition_descriptors(self, condition_descriptors):
        """Sets the condition_descriptors of this InventoryItemWithSkuLocale.

        <div class=\"msgbox_important\"><p class=\"msgbox_importantInDiv\" data-mc-autonum=\"&lt;b&gt;&lt;span style=&quot;color: #dd1e31;&quot; class=&quot;mcFormatColor&quot;&gt;Important! &lt;/span&gt;&lt;/b&gt;\"><span class=\"autonumber\"><span><b><span style=\"color: #dd1e31;\" class=\"mcFormatColor\">Important!</span></b></span></span>For trading card listings in Non-Sport Trading Card Singles (183050), CCG Individual Cards (183454), and Sports Trading Card Singles (261328) categories, sellers must use either LIKE_NEW (2750) or USED_VERY_GOOD (4000) item condition. No other item conditions will be accepted. Use of these item conditions require the seller to use the conditionDescriptors array to provide one or more applicable Condition Descriptor name-value pairs. See the conditionDescriptors field description for more information. If these requierments are not followed,  publishOffer, updateOffer, bulkPublishOffer, and publishOfferByInventoryItemGroup methods will fail when trying to create new listings.</p></span></div><br><br>This container is used by the seller to provide additional information about the condition of an item in a structured format. Condition descriptors are name-value attributes that can be either closed set or open text inputs.<br><br>To retrieve all condition descriptor numeric IDs for a category, use the <a href=\"/api-docs/sell/metadata/resources/marketplace/methods/getItemConditionPolicies\" target=\"_blank\">getItemConditionPolicies</a> method of the Metadata API. <br><br>  # noqa: E501

        :param condition_descriptors: The condition_descriptors of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: list[ConditionDescriptor]
        """

        self._condition_descriptors = condition_descriptors

    @property
    def locale(self):
        """Gets the locale of this InventoryItemWithSkuLocale.  # noqa: E501

        This request parameter sets the natural language that was provided in the field values of the request payload (i.e., en_AU, en_GB or de_DE). For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:LocaleEnum'>eBay API documentation</a>  # noqa: E501

        :return: The locale of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: str
        """
        return self._locale

    @locale.setter
    def locale(self, locale):
        """Sets the locale of this InventoryItemWithSkuLocale.

        This request parameter sets the natural language that was provided in the field values of the request payload (i.e., en_AU, en_GB or de_DE). For implementation help, refer to <a href='https://developer.ebay.com/api-docs/sell/inventory/types/slr:LocaleEnum'>eBay API documentation</a>  # noqa: E501

        :param locale: The locale of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: str
        """

        self._locale = locale

    @property
    def package_weight_and_size(self):
        """Gets the package_weight_and_size of this InventoryItemWithSkuLocale.  # noqa: E501


        :return: The package_weight_and_size of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: PackageWeightAndSize
        """
        return self._package_weight_and_size

    @package_weight_and_size.setter
    def package_weight_and_size(self, package_weight_and_size):
        """Sets the package_weight_and_size of this InventoryItemWithSkuLocale.


        :param package_weight_and_size: The package_weight_and_size of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: PackageWeightAndSize
        """

        self._package_weight_and_size = package_weight_and_size

    @property
    def product(self):
        """Gets the product of this InventoryItemWithSkuLocale.  # noqa: E501


        :return: The product of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: Product
        """
        return self._product

    @product.setter
    def product(self, product):
        """Sets the product of this InventoryItemWithSkuLocale.


        :param product: The product of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: Product
        """

        self._product = product

    @property
    def sku(self):
        """Gets the sku of this InventoryItemWithSkuLocale.  # noqa: E501

        This is the seller-defined SKU value of the product that will be listed on the eBay site (specified in the <strong>marketplaceId</strong> field). Only one offer (in unpublished or published state) may exist for each <strong>sku</strong>/<strong>marketplaceId</strong>/<strong>format</strong> combination. This field is required.<br><br><strong>Max Length</strong>: 50<br>  # noqa: E501

        :return: The sku of this InventoryItemWithSkuLocale.  # noqa: E501
        :rtype: str
        """
        return self._sku

    @sku.setter
    def sku(self, sku):
        """Sets the sku of this InventoryItemWithSkuLocale.

        This is the seller-defined SKU value of the product that will be listed on the eBay site (specified in the <strong>marketplaceId</strong> field). Only one offer (in unpublished or published state) may exist for each <strong>sku</strong>/<strong>marketplaceId</strong>/<strong>format</strong> combination. This field is required.<br><br><strong>Max Length</strong>: 50<br>  # noqa: E501

        :param sku: The sku of this InventoryItemWithSkuLocale.  # noqa: E501
        :type: str
        """

        self._sku = sku

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
        if issubclass(InventoryItemWithSkuLocale, dict):
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
        if not isinstance(other, InventoryItemWithSkuLocale):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
