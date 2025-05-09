# coding: utf-8

"""
    Browse API

    The Browse API has the following resources:<ul><li><b>item_summary:</b><br>Allows shoppers to search for specific items by keyword, GTIN, category, charity, product, image, or item aspects and refine the results by using filters, such as aspects, compatibility, and fields values, or UI parameters.</li><li><b>item:</b><br>Allows shoppers to retrieve the details of a specific item or all items in an item group, which is an item with variations such as color and size and check if a product is compatible with the specified item, such as if a specific car is compatible with a specific part.<br><br>This resource also provides a bridge between the eBay legacy APIs, such as the <a href=\"/api-docs/user-guides/static/finding-user-guide-landing.html\" target=\"_blank\">Finding</b>, and the RESTful APIs, which use different formats for the item IDs.</li></ul>The <b>item_summary</b>, <b>search_by_image</b>, and <b>item</b> resource calls require an <a href=\"/api-docs/static/oauth-client-credentials-grant.html\" target=\"_blank\">Application access token</a>.  # noqa: E501

    OpenAPI spec version: v1.20.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Product(object):
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
        'additional_images': 'list[Image]',
        'additional_product_identities': 'list[AdditionalProductIdentity]',
        'aspect_groups': 'list[AspectGroup]',
        'brand': 'str',
        'description': 'str',
        'gtins': 'list[str]',
        'image': 'Image',
        'mpns': 'list[str]',
        'title': 'str'
    }

    attribute_map = {
        'additional_images': 'additionalImages',
        'additional_product_identities': 'additionalProductIdentities',
        'aspect_groups': 'aspectGroups',
        'brand': 'brand',
        'description': 'description',
        'gtins': 'gtins',
        'image': 'image',
        'mpns': 'mpns',
        'title': 'title'
    }

    def __init__(self, additional_images=None, additional_product_identities=None, aspect_groups=None, brand=None, description=None, gtins=None, image=None, mpns=None, title=None):  # noqa: E501
        """Product - a model defined in Swagger"""  # noqa: E501
        self._additional_images = None
        self._additional_product_identities = None
        self._aspect_groups = None
        self._brand = None
        self._description = None
        self._gtins = None
        self._image = None
        self._mpns = None
        self._title = None
        self.discriminator = None
        if additional_images is not None:
            self.additional_images = additional_images
        if additional_product_identities is not None:
            self.additional_product_identities = additional_product_identities
        if aspect_groups is not None:
            self.aspect_groups = aspect_groups
        if brand is not None:
            self.brand = brand
        if description is not None:
            self.description = description
        if gtins is not None:
            self.gtins = gtins
        if image is not None:
            self.image = image
        if mpns is not None:
            self.mpns = mpns
        if title is not None:
            self.title = title

    @property
    def additional_images(self):
        """Gets the additional_images of this Product.  # noqa: E501

        An array of containers with the URLs for the product images that are in addition to the primary image.   # noqa: E501

        :return: The additional_images of this Product.  # noqa: E501
        :rtype: list[Image]
        """
        return self._additional_images

    @additional_images.setter
    def additional_images(self, additional_images):
        """Sets the additional_images of this Product.

        An array of containers with the URLs for the product images that are in addition to the primary image.   # noqa: E501

        :param additional_images: The additional_images of this Product.  # noqa: E501
        :type: list[Image]
        """

        self._additional_images = additional_images

    @property
    def additional_product_identities(self):
        """Gets the additional_product_identities of this Product.  # noqa: E501

        An array of product identifiers associated with the item. This container is returned if the seller has associated the eBay Product Identifier (ePID) with the item and in the request <b> fieldgroups</b> is set to <code>PRODUCT</code>.  # noqa: E501

        :return: The additional_product_identities of this Product.  # noqa: E501
        :rtype: list[AdditionalProductIdentity]
        """
        return self._additional_product_identities

    @additional_product_identities.setter
    def additional_product_identities(self, additional_product_identities):
        """Sets the additional_product_identities of this Product.

        An array of product identifiers associated with the item. This container is returned if the seller has associated the eBay Product Identifier (ePID) with the item and in the request <b> fieldgroups</b> is set to <code>PRODUCT</code>.  # noqa: E501

        :param additional_product_identities: The additional_product_identities of this Product.  # noqa: E501
        :type: list[AdditionalProductIdentity]
        """

        self._additional_product_identities = additional_product_identities

    @property
    def aspect_groups(self):
        """Gets the aspect_groups of this Product.  # noqa: E501

        An array of containers for the product aspects. Each group contains the aspect group name and the aspect name/value pairs.  # noqa: E501

        :return: The aspect_groups of this Product.  # noqa: E501
        :rtype: list[AspectGroup]
        """
        return self._aspect_groups

    @aspect_groups.setter
    def aspect_groups(self, aspect_groups):
        """Sets the aspect_groups of this Product.

        An array of containers for the product aspects. Each group contains the aspect group name and the aspect name/value pairs.  # noqa: E501

        :param aspect_groups: The aspect_groups of this Product.  # noqa: E501
        :type: list[AspectGroup]
        """

        self._aspect_groups = aspect_groups

    @property
    def brand(self):
        """Gets the brand of this Product.  # noqa: E501

        The brand associated with product. To identify the product, this is always used along with MPN (manufacturer part number).  # noqa: E501

        :return: The brand of this Product.  # noqa: E501
        :rtype: str
        """
        return self._brand

    @brand.setter
    def brand(self, brand):
        """Sets the brand of this Product.

        The brand associated with product. To identify the product, this is always used along with MPN (manufacturer part number).  # noqa: E501

        :param brand: The brand of this Product.  # noqa: E501
        :type: str
        """

        self._brand = brand

    @property
    def description(self):
        """Gets the description of this Product.  # noqa: E501

        The rich description of an eBay product, which might contain HTML.  # noqa: E501

        :return: The description of this Product.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Product.

        The rich description of an eBay product, which might contain HTML.  # noqa: E501

        :param description: The description of this Product.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def gtins(self):
        """Gets the gtins of this Product.  # noqa: E501

        An array of all the possible GTINs values associated with the product. A GTIN is a unique Global Trade Item number of the item as defined by <a href=\"https://www.gtin.info \" target=\"_blank\">https://www.gtin.info</a>. This can be a UPC (Universal Product Code), EAN (European Article Number), or an ISBN (International Standard Book Number) value.  # noqa: E501

        :return: The gtins of this Product.  # noqa: E501
        :rtype: list[str]
        """
        return self._gtins

    @gtins.setter
    def gtins(self, gtins):
        """Sets the gtins of this Product.

        An array of all the possible GTINs values associated with the product. A GTIN is a unique Global Trade Item number of the item as defined by <a href=\"https://www.gtin.info \" target=\"_blank\">https://www.gtin.info</a>. This can be a UPC (Universal Product Code), EAN (European Article Number), or an ISBN (International Standard Book Number) value.  # noqa: E501

        :param gtins: The gtins of this Product.  # noqa: E501
        :type: list[str]
        """

        self._gtins = gtins

    @property
    def image(self):
        """Gets the image of this Product.  # noqa: E501


        :return: The image of this Product.  # noqa: E501
        :rtype: Image
        """
        return self._image

    @image.setter
    def image(self, image):
        """Sets the image of this Product.


        :param image: The image of this Product.  # noqa: E501
        :type: Image
        """

        self._image = image

    @property
    def mpns(self):
        """Gets the mpns of this Product.  # noqa: E501

        An array of all possible MPN values associated with the product. A MPNs is manufacturer part number of the product. To identify the product, this is always used along with brand.  # noqa: E501

        :return: The mpns of this Product.  # noqa: E501
        :rtype: list[str]
        """
        return self._mpns

    @mpns.setter
    def mpns(self, mpns):
        """Sets the mpns of this Product.

        An array of all possible MPN values associated with the product. A MPNs is manufacturer part number of the product. To identify the product, this is always used along with brand.  # noqa: E501

        :param mpns: The mpns of this Product.  # noqa: E501
        :type: list[str]
        """

        self._mpns = mpns

    @property
    def title(self):
        """Gets the title of this Product.  # noqa: E501

        The title of the product.  # noqa: E501

        :return: The title of this Product.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Product.

        The title of the product.  # noqa: E501

        :param title: The title of this Product.  # noqa: E501
        :type: str
        """

        self._title = title

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
        if issubclass(Product, dict):
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
        if not isinstance(other, Product):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
