#!/usr/bin/python3

"""
Run this script from the command line to generate informational json files that ebay_rest.py loads.

Run this whenever the Response Fields in the following link change.

"""

# Standard library imports
from re import findall
from requests import get
from string import ascii_uppercase
from json import dump
from typing import Dict, List, Tuple, Union

# Third party imports
from bs4 import BeautifulSoup

# Local imports


def add_enum(enums: Dict[str, list], new_enum: str) -> None:
    enums[new_enum] = []


def camel_to_snake_case(name: str) -> str:
    result = name[0].lower()  # play it safe and cover the "upper Camel case" aka "Pascal case" variant too
    for c in name[1:]:
        if c in ascii_uppercase:
            result += '_'
            c = c.lower()
        result += c
    return result


def change_type_per_full_field(
        containers: Dict[str, Dict[str, Union[bool, str, List[Dict[str, Union[str, None, bool]]], List[str]]]],
        full_field: str,
        new_type: str
        ) -> None:
    """ In a container change sql types when a partial field name matches. """

    found = False
    for key in containers:
        container = containers[key]
        for field in container['fields']:
            if full_field == field['name_sql']:
                field['type_sql'] = new_type
                found = True
    if not found:
        print(f'change_type_per_full_field failed on full_field {full_field} and new_type {new_type}.')


def change_type_per_partial_field(
        containers: Dict[str, Dict[str, Union[bool, str, List[Dict[str, Union[str, None, bool]]], List[str]]]],
        partial_field: str,
        new_type: str
        ) -> None:
    """ In a container change sql types when a partial field name matches. """

    found = False
    for key in containers:
        container = containers[key]
        for field in container['fields']:
            if partial_field in field['name_sql']:
                field['type_sql'] = new_type
                found = True
    if not found:
        print(f'change_type_per_partial_field failed on partial_field {partial_field} and new_type {new_type}.')


def enum_name_converter(kind: str) -> str:
    if kind[-4:] in ('Enum', 'Type'):
        return camel_to_snake_case(kind[:-4])
    else:
        print(f'{kind} does not end in Enum or Type.')


def get_table_via_link(url):
    soup = get_soup_via_link(url)
    # find the rows regarding Response Fields.
    table = soup.find('table')
    rows = table.find_all('tr')
    # put the rows into a table of data
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values
    return data


def make_json_file(source: dict or list, name: str) -> None:
    path = '../src/ebay_rest/references/'
    with open(path + name + '.json', 'w') as outfile:
        dump(source, outfile, sort_keys=True, indent=4)


def get_enumerations(response_fields: List[Tuple[str, str, str, str]]) -> Dict[str, list]:
    enums_dict = {}
    variants = ['ba', 'gct']

    for response_field in response_fields:
        (name_full, kind, occurrence, description) = response_field

        parts = kind.split()  # if there is an enum, it is always the last word
        last = parts[-1]

        if last[-4:] in ('Enum', 'Type'):

            enum_name = enum_name_converter(last)

            if enum_name not in enums_dict:

                variant_count = 0
                data = []
                while variant_count < len(variants) and not data:
                    # form the url
                    url = f'https://developer.ebay.com/api-docs/buy/browse/types/{variants[variant_count]}:{last}'

                    # load the target webpage
                    soup = get_soup_via_link(url)
                    for datum in soup.find_all('div', class_='flex-4 first-column'):
                        data.append(datum.contents[0])
                    variant_count += 1
                if data:
                    enums_dict[enum_name] = data
                else:
                    print(f'Could not find values for {kind}.')

    return enums_dict


def get_response_fields() -> List[Tuple[str, str, str, str]]:
    print('Find the Response Fields for the eBay Get Item call.')

    # load the target webpage
    url = 'https://developer.ebay.com/api-docs/buy/browse/resources/item/methods/getItem'
    soup = get_soup_via_link(url)

    # find the rows regarding Response Fields.
    table = soup.find('table', id='Output-field-definitions-table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    # put the rows into a table of data
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values

    # fix a mess caused by description blurbs that contain tables
    more = True
    while more:
        more = False
        for i, datum in enumerate(data):
            if len(datum) != 3:
                # merge and delete the 3rd and following fields
                post_datum = datum[2:]
                blurb = ' '.join(post_datum)
                datum = datum[0:2]
                # also merge and remove abnormal rows that follow
                while len(data[i + 1]) != 3 or data[i + 1][0][0].isupper():
                    post_datum = data.pop(i + 1)
                    blurb += ' '.join(post_datum)
                datum.append(blurb)
                data[i] = datum
                more = True
                break  # we must restart the for loop because the enumerated data was altered

    # move the occurrence value to a new column
    for datum in data:
        blurb = datum[2]
        occurrence = ''
        for option in ('Conditional', 'Always', 'NA'):
            phrase = f' Occurrence: {option}'
            if phrase in blurb:
                occurrence = option
                blurb = blurb.replace(phrase, '')
                break
        assert (occurrence != '')
        datum[2] = occurrence
        datum.append(blurb)

    # adhere to Python naming conventions
    for datum in data:
        datum[0] = camel_to_snake_case(datum[0])

    return data


def generate_country_codes() -> None:
    print("Find the eBay's Country Codes.")

    # load the target webpage
    url = 'https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/countrycodetype.html'
    data = get_table_via_link(url)

    # ignore header, convert to a dict & delete bad values
    dict_ = {}
    for datum in data[1:]:
        dict_[datum[0]] = datum[1]
    for bad_value in ('CustomCode', 'QM', 'QN', 'QO', 'TP', 'UM', 'YU', 'ZZ'):
        if bad_value in dict_:
            del dict_[bad_value]
        else:
            print("Bad value " + bad_value + "no longer needs to be deleted.")

    make_json_file(dict_, 'country_codes')
    return


def generate_currency_codes() -> None:
    print("Find the eBay's Currency Codes.")

    # load the target webpage
    url = 'https://developer.ebay.com/devzone/xml/docs/Reference/eBay/types/CurrencyCodeType.html'
    data = get_table_via_link(url)

    # ignore header, convert to a dict & delete bad values
    dict_ = {}
    for datum in data[1:]:
        dict_[datum[0]] = datum[1]

    bad_values = ('CustomCode',)
    to_delete = set()
    for key, value in dict_.items():
        if key in bad_values or 'replaced' in value:
            to_delete.add(key)
    for key in to_delete:
        del dict_[key]

    make_json_file(dict_, 'currency_codes')
    return


def generate_global_id_values() -> None:
    print("Find the eBay's Global ID Values.")

    # load the target webpage
    url = 'https://developer.ebay.com/Devzone/merchandising/docs/CallRef/Enums/GlobalIdList.html'
    data = get_table_via_link(url)

    # the header got messed up and is unlikely to change, so hard code it
    cols = ['global_id', 'language', 'territory', 'site_name', 'ebay_site_id']

    # convert to a list of dicts
    dicts = []
    for datum in data[1:]:
        my_dict = {}
        for index, column in enumerate(cols):
            my_dict[column] = datum[index]
        dicts.append(my_dict)

    make_json_file(dicts, 'global_id_values')
    return


def generate_marketplace_id_values() -> None:
    print("Find the eBay's Marketplace ID Values.")

    # load the target webpage
    url = 'https://developer.ebay.com/api-docs/static/rest-request-components.html#marketpl'
    soup = get_soup_via_link(url)

    # find the rows regarding Response Fields.
    table = soup.findAll('table')[1]  # the second table is index 1
    rows = table.find_all('tr')

    # put the rows into a table of data
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values

    # the header got messed up and is unlikely to change, so hard code it
    # cols = ['marketplace_id', 'country', 'marketplace_site', 'locale_support']

    # convert to a nested dict
    my_dict = dict()
    for datum in data[1:]:
        [marketplace_id, country, marketplace_site, locale_support] = datum
        locale_support = locale_support.replace(' ', '')
        locales = locale_support.split(',')  # convert comma separated locales to a list of strings
        sites = findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                        marketplace_site)
        comments = findall('\(([^)]*)\)', marketplace_site)
        comment_shortage = len(locales) - len(comments)
        for _ in range(comment_shortage):
            comments.append('')
        my_locales = dict()
        for index, locale in enumerate(locales):
            my_locales[locale] = [sites[index], comments[index]]
        my_dict[marketplace_id] = [country, my_locales]

    make_json_file(my_dict, 'marketplace_id_values')
    return


def get_soup_via_link(url: str) -> BeautifulSoup:
    # Make a GET request to fetch the raw HTML content
    html_content = get(url).text

    # Parse the html content
    return BeautifulSoup(html_content, "html.parser")


def make_containers(parent_is_array: bool,
                    parent_container_kind: str,
                    table_part: str,
                    table_parent: str,
                    dot_level: int,
                    response_fields: List[Tuple[str, str, str, str]]
                    ) -> Dict[str, Dict[str, Union[bool, str, List[Dict[str, Union[str, None, bool]]], List[str]]]]:
    containers = {}
    fields = []
    children = []

    ebay_to_sql_types = {'boolean': 'bool', 'integer': 'int', 'string': 'varchar'}

    container_name = f'{table_parent}_{table_part}'
    required_container = parent_is_array

    if parent_is_array:

        if parent_container_kind in ebay_to_sql_types:
            shape = 'array_of_type'  # array of a single native SQL type
            array_type_sql = ebay_to_sql_types[parent_container_kind]

        elif parent_container_kind[-4:] in ('Enum', 'Type'):
            shape = 'array_of_enum'  # array of a single SQL enum type
            array_type_sql = enum_name_converter(parent_container_kind)
        else:
            shape = 'array_of_container'  # array of an eBay container
            array_type_sql = parent_container_kind
    else:
        array_type_sql = None
        shape = 'container'  # not an array

    i = 0
    while i < len(response_fields):
        response_field = response_fields[i]
        (name_full, kind, occurrence, description) = response_field
        name_parts = name_full.split('.')

        if 'array of' in kind:
            is_array = True
            root_kind = kind.split()[-1]
        else:
            is_array = False
            root_kind = kind

        # If this the start of a container then find its end. A container has a header and fields.
        if subfield_next(dot_level, i, response_fields):
            is_container = True
            j = i + 1
            while subfield_next(dot_level, j, response_fields):
                j += 1
        else:
            is_container = False
            j = i

        if is_container or is_array:
            containers.update(make_containers(parent_is_array=is_array,
                                              parent_container_kind=root_kind,
                                              table_part=name_parts[dot_level],
                                              table_parent=container_name,
                                              dot_level=dot_level + 1,
                                              response_fields=response_fields[i + 1:j + 1]))
            children.append(f"{container_name}_{name_parts[dot_level]}")
            i = j  # advance to the last item processed

        else:
            # field placeholders
            field_success = False
            required_field = None
            type_sql = None
            name_python = None
            name_sql = None

            if occurrence == 'Always':
                required_field = True
            elif occurrence in ('Conditional', 'NA'):
                required_field = False
            else:
                print(f"Unexpected occurrence value {occurrence}.")

            # Does the field's type directly correspond to an SQL type?
            if root_kind in ebay_to_sql_types:
                type_sql = ebay_to_sql_types[kind]
                name_python = name_parts[dot_level]
                name_sql = name_python
                field_success = True

            # Is the field an enumeration?
            elif root_kind[-4:] in ('Enum', 'Type'):
                enum_name = enum_name_converter(kind)
                type_sql = enum_name
                name_python = name_parts[dot_level]
                name_sql = name_python
                field_success = True

            # Is the field a coupon constraint?
            elif root_kind == 'CouponConstraint':
                # Is this another enum? Let's play it safe, and treat it like a varchar. TODO double check database
                # eBay's docs link fails! https://developer.ebay.com/api-docs/buy/browse/types/gct:CouponConstraint

                type_sql = 'varchar'
                name_python = name_parts[dot_level] + 's'  # make this plural to avoid SQL reserved word problems
                name_sql = name_python
                field_success = True

            else:
                print(f'Unhandled field {name_full} of type {kind}')

            if field_success:
                field = {
                    'name_python': name_python,
                    'name_sql': name_sql,
                    'required': required_field,
                    'type_sql': type_sql,
                }
                if most_values_not_none('field', field):
                    fields.append(field)

        i += 1  # advance to the next field, container or to end-of-list

    container = {
        'required': required_container,
        'shape': shape,
        'array_type_sql': array_type_sql,
        'fields': fields,
        'children': children,
    }
    if most_values_not_none('container', container):
        containers[container_name] = container

    return containers


def most_values_not_none(name: str, dictionary: Dict[str, str]) -> bool:
    for key, value in dictionary.items():
        if key != 'array_type_sql':
            if value is None:
                print(f"In dictionary {name} key {key} should not have value {value}.")
                return False
    return True


def subfield_next(dot_level: int, i: int, response_fields: List[Tuple[str, str, str, str]]) -> bool:
    i += 1
    result = False
    if i < len(response_fields):
        if response_fields[i][0].count('.') > dot_level:
            result = True
    return result


def generate_containers_and_enums():
    # True will slowly get a fresh object --- False will quickly reload the last object
    response_fields = get_response_fields()
    enums = get_enumerations(response_fields)
    # create containers from the response fields
    containers = make_containers(parent_is_array=False,
                                 parent_container_kind='item',
                                 table_part='item',
                                 table_parent='ebay',
                                 dot_level=0,
                                 response_fields=response_fields)
    # despite what the ebay documentation says, this field is not always provided
    found = False
    for field in containers['ebay_item_shipping_options']['fields']:
        if field['name_python'] == 'shipping_carrier_code':
            field['required'] = False
            found = True
            break
    if not found:
        print('ebay_item_shipping_options was not found.')
    # Add a missing enum. To learn why this hack is required, search on 'CouponConstraint' in this python file.
    # add_enum(enums=enums, field_name='coupon_constraint')  TODO double check database to see if we should change this
    # SQL types are changed from varchar, when it would improve computational and storage efficiency
    # change that are possible by a simple partial field name match
    change_type_per_partial_field(containers, 'rating', 'numeric(1)')
    change_type_per_partial_field(containers, 'average_rating', 'numeric(2,1)')  # this must be after 'rating'
    change_type_per_partial_field(containers, '_date', 'timestamp with time zone')
    change_type_per_partial_field(containers, 'gtin', 'numeric(14,0)')
    change_type_per_partial_field(containers, 'percentage', 'numeric(4,1)')
    # change currency values to numeric(16,4)
    found = False
    for key in containers:
        container = containers[key]
        has_currency = False
        for field in container['fields']:
            if field['type_sql'] == 'currency_code':
                has_currency = True
                break
        if has_currency:
            for field in container['fields']:
                if 'value' in field['name_sql']:
                    field['type_sql'] = 'numeric(16,4)'
                    found = True
    if not found:
        print('No currency values were found.')
    # change complete field names that are always integers
    for field_name in ('category_id', 'condition_id', 'identifier_value', 'item_group_id'):
        change_type_per_full_field(containers, field_name, 'int')
    change_type_per_full_field(containers, 'legacy_item_id', 'bigint')
    # change complete field names that would make ideal enums
    for field_name in ('age_group', 'condition', 'domain', 'energy_efficiency_class', 'gender', 'identifier_type',
                       'region_id', 'region_name', 'seller_account_type', 'shipping_carrier_code',
                       'shipping_cost_type', 'size_system', 'subdomain', 'tax_jurisdiction_id', 'trademark_symbol'):
        change_type_per_full_field(containers, field_name, field_name)
        add_enum(enums, field_name)
    # handle generic sounding field names, that would make good enums
    for (container_name, field_name, new_type) in (
            ('ebay_item_authenticity_verification', 'description', 'authenticity_verification_description'),
            ('ebay_item_shipping_options', 'type', 'shipping_option_type'),
            ('ebay_item_warnings', 'category', 'warning_category')):
        found = False
        container = containers[container_name]
        for field in container['fields']:
            if field['name_sql'] == field_name:
                field['type_sql'] = new_type
                add_enum(enums, new_type)
                found = True
                break
        if not found:
            print(f'Handle generic sounding field names failed on {container_name}, {field_name} and {new_type}.')
    containers['ebay_item_product_gtins']['array_type_sql'] = 'numeric(14,0)'
    containers['ebay_item_product_gtins']['shape'] = 'array_of_type'
    for (container_name, new_enum) in (
            ('ebay_item_buying_options', 'buying_options'),
            ('ebay_item_qualified_programs', 'qualified_programs')):
        containers[container_name]['array_type_sql'] = new_enum
        containers[container_name]['shape'] = 'array_of_enum'
        add_enum(enums, new_enum)
    # safety check
    for key in containers:
        if containers[key]['shape'] not in ('container', 'array_of_type', 'array_of_enum', 'array_of_container'):
            print(f"Container {key} has unexpected shape {containers[key]['shape']}.")

    make_json_file(containers, 'item_fields_modified')
    make_json_file(enums, 'item_enums_modified')

    return


def main():
    generate_containers_and_enums()
    generate_country_codes()
    generate_currency_codes()
    generate_global_id_values()
    generate_marketplace_id_values()

    return


if __name__ == "__main__":
    main()
