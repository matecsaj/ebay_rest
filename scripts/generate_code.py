#!/usr/bin/python3
# Run this script from the command-line to get info from https://developer.ebay.com and generate code in the src folder.

# Wait day if this script intermittently fails to load pages from eBay's website.
# Perhaps making inhumanly frequent requests triggers eBay's DOS protection system.


# Standard library imports
import datetime
import hashlib
import json
import logging
import os
import re
import shutil
import sys
import string
import time
from typing import Dict, List, Set, Tuple, Union

# Third party imports
import aiofiles
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlunsplit


# Local imports

# Globals

async def run(cmd):
    """ Run a command line in a subprocess. """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


def add_enum(enums: Dict[str, list], new_enum: str) -> None:
    enums[new_enum] = []


def camel_to_snake_case(name: str) -> str:
    result = name[0].lower()  # play it safe and cover the "upper Camel case" aka "Pascal case" variant too
    for c in name[1:]:
        if c in string.ascii_uppercase:
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
        logging.debug(f'change_type_per_full_field failed on full_field {full_field} and new_type {new_type}.')


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
        logging.debug(f'change_type_per_partial_field failed on partial_field {partial_field} and new_type {new_type}.')


def enum_name_converter(kind: str) -> str:
    if kind[-4:] in ('Enum', 'Type'):
        return camel_to_snake_case(kind[:-4])
    else:
        logging.debug(f'{kind} does not end in Enum or Type.')


async def get_table_via_link(url: str) -> list:
    data = []
    soup = await get_soup_via_link(url)
    # find the rows regarding Response Fields.
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')
        # put the rows into a table of data
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values
    if len(data) == 0:
        logging.warning(f"No data was extracted from {url}.")
    return data


def make_json_file(source: dict or list, name: str) -> None:
    if len(source) > 0:
        path = '../src/ebay_rest/references/'
        with open(path + name + '.json', 'w') as outfile:
            json.dump(source, outfile, sort_keys=True, indent=4)
    else:
        logging.error(f"The json file for {name} should not be empty; not created.")


async def get_enumerations(response_fields: List[Tuple[str, str, str, str]]) -> Dict[str, list]:
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
                    soup = await get_soup_via_link(url)
                    for datum in soup.find_all('div', class_='flex-4 first-column'):
                        data.append(datum.contents[0])
                    variant_count += 1
                if data:
                    enums_dict[enum_name] = data
                else:
                    logging.debug(f'Could not find values for {kind}.')

    return enums_dict


async def get_response_fields() -> List[Tuple[str, str, str, str]]:
    logging.info('Find the Response Fields for the eBay Get Item call.')

    # load the target webpage
    url = 'https://developer.ebay.com/api-docs/buy/browse/resources/item/methods/getItem'
    soup = await get_soup_via_link(url)

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


async def generate_country_codes() -> None:
    logging.info("Find the eBay's Country Codes.")

    # load the target webpage
    data = await get_table_via_link(get_ebay_list_url('CountryCodeType'))

    # ignore header, convert to a dict & delete bad values
    dict_ = {}
    for datum in data[1:]:
        dict_[datum[0]] = datum[1]
    for bad_value in ('CustomCode', 'QM', 'QN', 'QO', 'TP', 'UM', 'YU', 'ZZ'):
        if bad_value in dict_:
            del dict_[bad_value]
        else:
            logging.debug("Bad value " + bad_value + "no longer needs to be deleted.")

    make_json_file(dict_, 'country_codes')
    return


async def generate_currency_codes() -> None:
    logging.info("Find the eBay's Currency Codes.")

    # load the target webpage
    data = await get_table_via_link(get_ebay_list_url('CurrencyCodeType'))

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


async def generate_global_id_values() -> None:
    logging.info("Find the eBay's Global ID Values.")

    # load the target webpage
    url = 'https://developer.ebay.com/Devzone/merchandising/docs/CallRef/Enums/GlobalIdList.html'
    data = await get_table_via_link(url)

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


async def generate_marketplace_id_values() -> None:
    logging.info("Find the eBay's Marketplace ID Values.")

    my_dict = dict()

    # load the target webpage
    url = 'https://developer.ebay.com/api-docs/static/rest-request-components.html#marketpl'
    soup = await get_soup_via_link(url)

    if soup:
        # find the rows regarding Response Fields.
        tables = soup.findAll('table')
        if len(tables) > 1:
            table = tables[1]   # the second table is index 1
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

            for datum in data[1:]:
                [marketplace_id, country, marketplace_site, locale_support] = datum
                locale_support = locale_support.replace(' ', '')
                locales = locale_support.split(',')  # convert comma separated locales to a list of strings
                sites = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+',
                                   marketplace_site)
                comments = re.findall('\\(([^)]*)\\)', marketplace_site)
                comment_shortage = len(locales) - len(comments)
                for _ in range(comment_shortage):
                    comments.append('')
                my_locales = dict()
                for index, locale in enumerate(locales):
                    my_locales[locale] = [sites[index], comments[index]]
                my_dict[marketplace_id] = [country, my_locales]

    make_json_file(my_dict, 'marketplace_id_values')
    return


async def get_soup_via_link(url: str) -> BeautifulSoup:
    # Get the html at an url and then make soup of it.

    # TODO Determine the common exceptions and then handle then; run the debugger with breakpoints on the bp lines.

    # Get the html
    try:
        # the header is meant to prevent the exception 'Response payload is not completed'
        async with aiohttp.ClientSession(headers={'Connection': 'keep-alive'}) as session:
            try:
                async with session.get(url) as response:
                    try:
                        html_content = await response.text()
                    except Exception as e:
                        bp = True
            except Exception as e:
                if 'Connection reset by peer' in e:
                    logging.fatal("The server dropped the connection on the TCP level; it may think we are a "
                                  "denial-of-service attacker; try again tomorrow.")
                    exit()
                else:
                    bp = True
    except Exception as e:
        bp = True

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
                logging.debug(f"Unexpected occurrence value {occurrence}.")

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
                logging.debug(f'Unhandled field {name_full} of type {kind}')

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
                logging.debug(f"In dictionary {name} key {key} should not have value {value}.")
                return False
    return True


def subfield_next(dot_level: int, i: int, response_fields: List[Tuple[str, str, str, str]]) -> bool:
    i += 1
    result = False
    if i < len(response_fields):
        if response_fields[i][0].count('.') > dot_level:
            result = True
    return result


async def generate_containers_and_enums():
    # True will slowly get a fresh object --- False will quickly reload the last object
    response_fields = await get_response_fields()
    enums = await get_enumerations(response_fields)
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
        logging.debug('ebay_item_shipping_options was not found.')
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
        logging.debug('No currency values were found.')
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
            message = f'Handle generic sounding field names failed on {container_name}, {field_name} and {new_type}.'
            logging.debug(message)
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
            logging.debug(f"Container {key} has unexpected shape {containers[key]['shape']}.")

    make_json_file(containers, 'item_fields_modified')
    make_json_file(enums, 'item_enums_modified')

    return


async def generate_references():
    """
    Generated JSON files for the 'references' directory found in 'src'.

    If you add, delete or rename a json file, then alter /src/ebay_rest/reference.py accordingly.

    :return:
    """
    # TODO Clear out any junk that happens to be in the target folder.

    await asyncio.gather(
        # generate_containers_and_enums(),      # TODO if nobody complains then permanently delete otherwise fix it
        generate_country_codes(),
        generate_currency_codes(),
        generate_global_id_values(),
        generate_marketplace_id_values()
    )


def get_ebay_list_url(code_type: str) -> str:
    """
    Make an url to an ebay "code type" list

    Here is the complete list of possible code types.
    https://developer.ebay.com/devzone/xml/docs/Reference/eBay/enumindex.html#EnumerationIndex

    If eBay modified the url you need to determine the new pattern;
    at https://developer.ebay.com/ search for "countrycodetype" and study the result.

    example: https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/countrycodetype.html
    """
    return f'https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/{code_type}.html'


class Locations:
    """ Where things are located in the locale file store. """

    target_directory: str = 'api'
    target_path: str = os.path.abspath('../src/ebay_rest/' + target_directory)
    cache_path: str = os.path.abspath('./' + target_directory + '_cache')

    state_file: str = 'state.json'
    state_path_file: str = os.path.abspath(os.path.join(cache_path, state_file))

    file_ebay_rest = os.path.abspath('../src/ebay_rest/a_p_i.py')


class State:
    """ Track the state of progress, even if the program is re-run. """

    def __init__(self) -> None:
        try:
            with open(Locations.state_path_file) as file_handle:
                self._states = json.load(file_handle)
        except OSError:
            self._states = dict()

    def get(self, key: str) -> str or None:
        if key in self._states:
            return self._states[key]
        else:
            return None

    def set(self, key: str, value: str) -> None:
        self._states[key] = value
        try:
            with open(Locations.state_path_file, 'w') as file_handle:
                json.dump(self._states, file_handle, sort_keys=True, indent=4)
        except OSError:
            message = f"Can't write to {Locations.state_path_file}."
            logging.fatal(message)
            sys.exit(message)


async def ensure_cache():
    # ensure that we have an empty cache
    if os.path.isdir(Locations.cache_path):
        Contracts.delete_folder_contents(Locations.cache_path)
    else:
        os.mkdir(Locations.cache_path)


async def ensure_swagger() -> None:
    s = State()  # skip if this was already done less than a day ago
    key = 'tool_date_time'
    dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    if s.get(key) is None or \
            datetime.datetime.strptime(s.get(key), dt_format) < datetime.datetime.now() - datetime.timedelta(days=1):

        if sys.platform == 'darwin':  # OS X or MacOS
            logging.info('Install or update the package manager named HomeBrew.')
            await run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

            if os.path.isfile('/usr/local/bin/swagger-codegen'):
                logging.info('Upgrade the code generator from Swagger. https://swagger.io/')
                await run('brew upgrade swagger-codegen')
            else:
                logging.info('Install the code generator from Swagger. https://swagger.io/')
                await run('brew install swagger-codegen')

            logging.info('Test the generator installation by invoking its help screen.')
            await run('/usr/local/bin/swagger-codegen -h')
        elif sys.platform == 'linux':  # Linux platform
            # Don't install packages without user interaction.
            if not os.path.isfile('swagger-codegen-cli.jar'):
                await run(
                    'wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/'
                    + 'swagger-codegen-cli/3.0.26/swagger-codegen-cli-3.0.26.jar '
                    + '-O swagger-codegen-cli.jar'
                )
            logging.info('Test the generator installation by invoking its help screen.')
            await run('java -jar swagger-codegen-cli.jar -h')
        else:
            message = f'Please extend install_tools() for your {sys.platform} platform.'
            logging.fatal(message)
            sys.exit(message)

        s.set(key, datetime.datetime.now().strftime(dt_format))


class Contracts:

    def __init__(self, overview_link) -> None:
        self.overview_link = overview_link
        self.category = None
        self.call = None
        self.link_href = None
        self.file_name = None
        self.name = None

    async def process(self):
        [self.category, self.call, self.link_href, self.file_name] = await self.get_contract(self.overview_link)
        self.name = self.get_api_name()
        await self.cache_contract()
        await self.patch_contract()
        await self.swagger_codegen()
        await self.patch_generated()
        self.copy_library()
        self.fix_imports()

    @staticmethod
    async def get_overview_links():
        logging.info('Get a list of links to overview pages; pages contain links to eBay OpenAPI 3 JSON contracts.')

        overview_links = []
        developer_url = 'https://developer.ebay.com/'
        soup = await get_soup_via_link(urljoin(developer_url, 'docs'))

        for link in soup.find_all('a', href=lambda href: href and 'overview.html' in href):
            path = link.get('href')
            path = path.replace('/static/', '/')   # help dup. filter, remove a redundant part that is sometimes present
            if not re.search("/v\d/", path):    # skip the experimental libraries because few people can use them
                overview_link = urljoin(developer_url, path)
                if overview_link not in overview_links:  # skip duplicate links
                    overview_links.append(overview_link)

        # safety check
        count = len(overview_links)
        logging.info(f'Found {count} links to overview pages.')
        assert (25 < count < 40), f'Having {count} contract overview links is unexpected!'

        overview_links.sort()
        return overview_links

    async def cache_contract(self):
        destination = os.path.join(Locations.cache_path, self.file_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.link_href) as response:
                text_content = await response.text()
        async with aiofiles.open(destination, mode='w') as f:
            await f.write(text_content)

    @staticmethod
    async def get_contract(overview_link: str):
        # find the path to the json contract with the highest version number
        soup = await get_soup_via_link(overview_link)
        paths = []
        for link in soup.find_all('a', href=lambda href: href and 'oas' in href and '.json' in href):
            path = link.get('href')
            if path not in paths:
                paths.append(path)
        assert (len(paths) > 0), f'{overview_link} should contain a contract!'
        paths.sort()
        path = paths[-1]
        # get parts
        path_split = path.split('/')
        url_split = urlsplit(overview_link)
        # make a record from the parts
        category = path_split[-5]
        call = path_split[-4].replace('-', '_')
        link_href = urlunsplit((url_split.scheme, url_split.hostname, path, '', ''))
        file_name = path_split[-1]
        contract = [category, call, link_href, file_name]
        return contract

    async def patch_contract(self) -> None:
        """ If the contract from eBay has an error then patch it before generating code. """
        if self.category == 'sell' and self.call == 'fulfillment':
            await Contracts.patch_contract_sell_fulfillment(self.file_name)

    @staticmethod
    async def patch_contract_sell_fulfillment(file_name):
        # In the Sell Fulfillment API, the model 'Address' is returned with attribute 'countryCode'.
        # However, the JSON specifies 'country' instead, thus Swagger generates the wrong API.
        file_location = os.path.join(Locations.cache_path, file_name)
        try:
            async with aiofiles.open(file_location, mode='r') as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_location}.")
        else:
            data = json.loads(data)
            properties = data['components']['schemas']['Address']['properties']
            if 'country' in properties:
                properties['countryCode'] = properties.pop('country')  # Warning, alphabetical key order spoiled.
                data = json.dumps(data, sort_keys=True, indent=4)
                async with aiofiles.open(file_location, mode='w') as f:
                    await f.write(data)
            else:
                logging.warning(f'Patching {file_name} is no longer needed.')

    async def patch_generated(self) -> None:
        """ If the generated code has an error then patch it before making use of it. """

        # API calls that have a return type fail when there is no content. This is because
        # there in attempt to de-serialize an empty string. If there is no content, indicated
        # by a 204 status then don't de-serialize.
        bad_code = 'if response_type:'
        file_location = os.path.join(Locations.cache_path, self.name, self.name, 'api_client.py')
        try:
            async with aiofiles.open(file_location, mode='r') as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_location}.")
        else:
            if bad_code not in data:
                logging.error(f"Maybe for {file_location} the 204 patch is not needed any longer.")
            else:
                # add a new condition before the colon
                data = data.replace(bad_code,
                                    bad_code[:-1] + ' and response_data.status != 204:       # ebay_rest patch')
                async with aiofiles.open(file_location, mode='w') as f:
                    await f.write(data)

    async def swagger_codegen(self):
        source = os.path.join(Locations.cache_path, self.file_name)
        command = f' generate -l python -o {Locations.cache_path}/{self.name} -DpackageName={self.name} -i {source}'
        if sys.platform == 'darwin':  # OS X or MacOS
            command = '/usr/local/bin/swagger-codegen' + command
        elif sys.platform == 'linux':  # Linux
            command = 'java -jar swagger-codegen-cli.jar' + command
        else:
            assert False, f'Please extend main() for your {sys.platform} platform.'
        await run(command)

    def get_api_name(self):
        name = f'{self.category}_{self.call}'
        return name

    async def get_one_base_paths_and_flows(self):
        """Process the JSON contract and extract three things for later use.
        1) the base_path for each category_call (e.g. buy_browse)
        2) the security flow for each scope in each category_call
        3) the scopes for each call in each category_call
        """
        source = os.path.join(Locations.cache_path, self.file_name)
        try:
            async with aiofiles.open(source, mode='r') as f:
                data = await f.read()
        except FileNotFoundError:
            message = f"Can't open {source}."
            logging.error(message)
            sys.exit(message)
        else:
            try:
                data = json.loads(data)
            except ValueError:
                message = "Invalid JSON in " + source
                logging.fatal(message)  # Invalid \escape: line 3407 column 90 (char 262143)
                sys.exit(message)
            else:
                # Get the contract's major version number
                if 'swagger' in data:
                    (version_major, _version_minor) = data['swagger'].split('.')
                elif 'openapi' in data:
                    (version_major, _version_minor, _version_tertiary) = data['openapi'].split('.')
                else:
                    message = f"{source} has no OpenAPI version number."
                    logging.fatal(message)  # Invalid \escape: line 3407 column 90 (char 262143)
                    sys.exit(message)
                # Get base path
                if version_major == '2':
                    base_path = data['basePath']
                elif version_major == '3':
                    base_path = data['servers'][0]['variables']['basePath']['default']
                else:
                    message = f"{source} has unrecognized OpenAPI version {version_major}."
                    logging.fatal(message)  # Invalid \escape: line 3407 column 90 (char 262143)
                    sys.exit(message)
                # Get flows for this category_call
                if version_major == '2':
                    category_flows = (
                        data['securityDefinitions']
                    )
                elif version_major == '3':
                    category_flows = (
                        data['components']['securitySchemes']['api_auth']['flows']
                    )
                else:
                    message = f"{source} has unrecognized OpenAPI version {version_major}."
                    logging.fatal(message)  # Invalid \escape: line 3407 column 90 (char 262143)
                    sys.exit(message)
                flow_by_scope = {}  # dict of scope: flow type
                for flow, flow_details in category_flows.items():
                    for scope in flow_details['scopes']:
                        if flow == 'Authorization Code':  # needed by version_major 2
                            value = 'authorizationCode'
                        elif flow == 'Client Credentials':  # needed by version_major 2
                            value = 'clientCredentials'
                        else:
                            value = flow
                        flow_by_scope[scope] = value
                # Get scope for each individually path-ed call
                operation_id_scopes = {}
                for path, path_methods in data['paths'].items():
                    for method, method_dict in path_methods.items():
                        if method not in ('get', 'post', 'put', 'delete'):
                            # Consider only the HTTP request parts
                            continue
                        operation_id = method_dict['operationId'].lower()
                        security_list = method_dict.get('security', [])
                        if len(security_list) > 1:
                            raise ValueError('Expected zero/one security entry per path!')
                        elif len(security_list) == 1:
                            if 'api_auth' in security_list[0]:
                                security = security_list[0]['api_auth']
                            elif 'Authorization Code' in security_list[0]:  # needed by version_major 2
                                security = security_list[0]['Authorization Code']
                            else:
                                raise ValueError("Expected 'api_auth' or 'Authorization Code' in security_list!'")
                        else:
                            security = None
                        if operation_id in operation_id_scopes:
                            logging.warning('Duplicate operation!')
                            logging.warning(path, path_methods)
                            logging.warning(method, method_dict)
                            raise ValueError('nope')
                        operation_id_scopes[operation_id] = security
                # TODO Get headers parameters
                # look for this  "in": "header",
                name = self.category + '_' + self.call
        return base_path, flow_by_scope, name, operation_id_scopes

    @staticmethod
    def delete_folder_contents(path_to_folder: str):
        list_dir = os.listdir(path_to_folder)
        for filename in list_dir:
            file_path = os.path.join(path_to_folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                logging.debug(f"deleting file: {file_path}")
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                logging.debug(f"deleting folder: {file_path}")
                shutil.rmtree(file_path)

    @staticmethod
    async def purge_existing():
        # purge what might already be there
        for filename in os.listdir(Locations.target_path):
            file_path = os.path.join(Locations.target_path, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def copy_library(self) -> None:
        """ Copy the essential parts of the generated eBay library to within the src folder. """
        src = os.path.join(Locations.cache_path, self.name, self.name)
        dst = os.path.join(Locations.target_path, self.name)
        _destination = shutil.copytree(src, dst)

    def fix_imports(self) -> None:
        """ The deeper the directory, the more dots are needed to make the correct relative path. """
        self._fix_imports_recursive(self.name, '..', os.path.join(Locations.target_path, self.name))

    def _fix_imports_recursive(self, name: str, dots: str, path: str) -> None:
        """ This does the recursive part of fix_imports. """

        for (_root, dirs, files) in os.walk(path):

            swaps = [  # order is crucial, put more specific swaps before less
                (f'import {name}.models', f'from {dots}{name} import models'),
                (f'from models', f'from {dots}{name}.models'),
                (f'import {name}', f'import {dots}{name}'),
                (f'from {name}', f'from {dots}{name}'),
                (f'{name}.models', f'models'),
            ]
            for file in files:
                target_file = os.path.join(path, file)
                new_lines = ''
                with open(target_file) as file_handle:
                    for old_line in file_handle:
                        for (original, replacement) in swaps:
                            if original in old_line:
                                old_line = old_line.replace(original, replacement)
                                break  # only the first matching swap should happen
                        new_lines += old_line
                with open(target_file, 'w') as file_handle:
                    file_handle.write(new_lines)

            dots += '.'
            for directory in dirs:
                self._fix_imports_recursive(name, dots, os.path.join(path, directory))

            break

    def get_requirements(self) -> Set[str]:
        """ Get the library's requirements. """

        # compile the set of all unique requirements from the generated library
        start_tag = 'REQUIRES = ['
        end_tag = ']\n'
        requirements = set()
        src = os.path.join(Locations.cache_path, self.name, 'setup.py')
        with open(src) as file:
            for line in file:
                if line.startswith(start_tag):
                    line = line.replace(start_tag, '')
                    line = line.replace(end_tag, '')
                    parts = line.split(', ')
                    for part in parts:
                        requirements.add(part)
                    break
        return requirements

    def get_includes(self) -> List[str]:
        """ Get the includes for a library. """
        includes = list()
        includes.append(f'from .{Locations.target_directory} import {self.name}')
        line = f'from .{Locations.target_directory}.{self.name}.rest import ApiException as ' \
               f'{self._camel(self.name)}Exception'
        includes.append(line)
        return includes

    async def get_methods(self) -> str:
        """ For a modules, get all code for its methods. """

        # catalog the module files that contain all method implementations
        modules = []
        path = os.path.join(Locations.cache_path, self.name, self.name, 'api')
        for (root, _dirs, files) in os.walk(path):
            for file in files:
                if file != '__init__.py':
                    modules.append((self.name, file.replace('.py', ''), os.path.join(root, file)))

        # catalog all methods in all modules
        methods = list()
        method_marker_part = '_with_http_info'
        method_marker_whole = method_marker_part + '(self,'
        docstring_marker = '"""'
        bad_docstring_markers = (
            '>>> ',
            'synchronous',
            'async_req',
            'request thread',
        )
        for (name, module, path) in modules:
            step = 0
            with open(path) as file_handle:
                for line in file_handle:

                    if step == 0:  # looking for the next method
                        if method_marker_whole in line:
                            (method_and_params, _junk) = line.split(')')
                            (method, params) = method_and_params.split('(')
                            method = method.replace('    def ', '')
                            method = method.replace(method_marker_part, '')
                            params = params.replace('self, ', '')
                            step += 1

                    elif step == 1:  # looking for the start of the docstring block
                        if docstring_marker in line:
                            docstring = line
                            step += 1

                    elif step == 2:  # looking for the end of the docstring block
                        if docstring_marker not in line:
                            bad = False
                            for bad_docstring_marker in bad_docstring_markers:
                                if bad_docstring_marker in line:
                                    bad = True
                                    break
                            if not bad:
                                docstring += line
                        else:
                            docstring += line
                            docstring = await self.clean_docstring(docstring)
                            methods.append((name, module, path, method, params, docstring))
                            step = 0

        methods.sort()

        code = str()
        for method in methods:
            code += await self._make_method(method)

        return code

    @staticmethod
    async def clean_docstring(docstring: string) -> string:

        # strip HTML
        docstring = BeautifulSoup(docstring).get_text()

        # fix typos
        typo_remedy = (  # pairs of typos found in docstrings and their remedy
            ('AustraliaeBay', 'Australia eBay'),  # noqa: - suppress flake8 compatible linters, misspelling is intended
            ('cerate', 'create'),  # noqa:
            ('distibuted', 'distributed'),  # noqa:
            ('FranceeBay', 'Francee Bay'),  # noqa:
            ('GermanyeBay', 'Germany eBay'),  # noqa:
            ('http:', 'https:'),  # noqa:
            ('identfier', 'identifier'),  # noqa:
            ('ItalyeBay', 'Italy eBay'),  # noqa:
            ('Limt', 'Limit'),  # noqa:
            ('lisitng', 'listing'),  # noqa:
            ('maketplace', 'marketplace'),  # noqa:
            ('markeplace', 'marketplace'),  # noqa:
            ('motorcyles', 'motorcycles'),  # noqa:
            ('parmeter', 'parameter'),  # noqa:
            ('publlish', 'publish'),  # noqa:
            ('qroup', 'group'),  # noqa:
            ('retrybable', 'retryable'),  # noqa:
            ('takeback', 'take back'),  # noqa:
            ('Takeback', 'Take back'),  # noqa:
            ('theste', 'these'),  # noqa:
            ('UKeBay', 'UK eBay'),  # noqa:
        )
        for (typo, remedy) in typo_remedy:
            docstring = docstring.replace(typo, remedy)

        # telling the linter to suppress long line warnings taints the Sphinx generated docs so filter them out
        docstring = docstring.replace('# noqa: E501', "")

        return docstring

    async def _make_method(self, method: Tuple[str, str, str, str, str, str]) -> str:
        """ Return the code for one python method. """

        (name, module, path, method, params, docstring) = method
        base_path, flow_by_scope, name, operation_id_scopes = \
            await self.get_one_base_paths_and_flows()

        ignore_long = '  # noqa: E501'  # flake8 compatible linters should not warn about long lines

        # Fix how the docstring expresses optional parameters then end up in **kwargs
        # catalog all parameters listed in the docstring
        docstring_params = set()
        for line in docstring.split('\n'):
            if ':param' in line:
                for word in line.split(' '):
                    if word.endswith(':'):
                        docstring_params.add(word.replace(':', ''))
                        break
        # determine if any docstring parameters are method parameters
        has_docstring_problem = False
        for docstring_param in docstring_params:
            if docstring_param not in params:
                has_docstring_problem = True
                break
        # if we found an optional parameter, then add a provision for 'optionals' aka *args in the right spot
        if has_docstring_problem:
            pass  # TODO Do something to make the comments aka docstring handle optional parameters properly

        # prepare the method type by testing for 'offset' parameter
        method_type = 'paged' if (':param str offset' in docstring) else 'single'

        # identify if this is a user_access_token routine
        operation_id = method.lower().replace('_', '')
        scopes = operation_id_scopes[operation_id]
        if not scopes:
            # Assume application keys
            flows = {'clientCredentials'}
        else:
            flows = {flow_by_scope[scope] for scope in scopes}
        if len(flows) != 1:
            if operation_id in ('getitemconditionpolicies',) or module in ('subscription_api',):
                # This usually uses the client credentials method
                flows = {'clientCredentials'}
            else:
                message = 'Could not identify authorization method!'
                logging.warning(message)
                logging.warning('method: ', method)
                logging.warning('scopes: ', scopes)
                logging.warning('flows: ', flows)
                raise ValueError(message)
        auth_method, = flows  # note tuple unpacking of set
        user_access_token = auth_method == 'authorizationCode'

        # identify and prep for parameter possibilities
        stars_kwargs = '**kwargs'
        params_modified = params.split(', ')
        if len(params_modified) == 0:
            has_args = False
            has_kw = False
        else:
            if params_modified[-1] == stars_kwargs:
                has_kw = True
                params_modified.pop()
            else:
                has_kw = False
            if len(params_modified) > 0:
                has_args = True
                params_modified = ', '.join(params_modified)
            else:
                has_args = False

        # Prepare the list of rate lookup information that will be used for throttling.
        resource_name_base = name.replace('_', '.')
        resource_name_module = module.replace('_api', '')
        rate = [resource_name_base, resource_name_module]

        code = f"    def {name}_{method}(self, {params}):{ignore_long}\n"
        code += docstring
        code += "        try:\n"
        code += f"            return self._method_{method_type}(" \
                f"{name}.Configuration," \
                f" '{base_path}'," \
                f" {name}.{self._camel(module)}," \
                f" {name}.ApiClient," \
                f" '{method}'," \
                f" {self._camel(name)}Exception," \
                f" {user_access_token}," \
                f" {rate},"
        if has_args:
            if ',' in params_modified:
                code += f" ({params_modified}),"
            else:
                code += f" {params_modified},"
        else:
            code += f" None,"
        if has_kw:
            code += f" **kwargs"
        else:
            code += f" None"
        code += f"){ignore_long}\n"
        code += "        except Error:\n"
        code += "            raise\n"
        code += "\n"

        return code

    def remove_duplicates(self, names) -> None:
        """ Deduplicate identical .py files found in all APIs.
        for example when comments are ignored the rest.py files appear identical. """

        # build a catalog that includes a hashed file signature
        catalog = []
        for name in names:
            catalog.extend(self._remove_duplicates_recursive_catalog(name, os.path.join(Locations.target_path, name)))

        # count how many times each signature appears
        signature_tally = {}
        for (name, file, path, signature) in catalog:
            if signature in signature_tally:
                signature_tally[signature] = + 1
            else:
                signature_tally[signature] = 1

        # make a sub catalog that just includes signature repeaters
        catalog_repeaters = []
        for values in catalog:
            (name, file, path, signature) = values
            if signature_tally[signature] > 1:
                catalog_repeaters.append(values)

        # TODO apply the DRY principle to the repeaters

    def _remove_duplicates_recursive_catalog(self, name: str, path: str) -> list:
        """ This does the recursive part of cataloging for remove_duplicates. """

        catalog = []
        for (_root, dirs, files) in os.walk(path):
            for file in files:
                if file != '__init__.py' and file.endswith('.py'):
                    target_file = os.path.join(path, file)
                    with open(target_file) as file_handle:
                        code_text = file_handle.read()
                        # TODO Remove whitespace and comments from the Python code before hashing.
                        m = hashlib.sha256()
                        m.update(code_text.encode())
                        catalog.append((name, file, target_file, m.digest()))

            for directory in dirs:
                catalog.extend(self._remove_duplicates_recursive_catalog(name, os.path.join(path, directory)))

            return catalog

    @staticmethod
    def _camel(name: str) -> str:
        """ Convert a name with underscore separators to upper camel case. """
        camel = ''
        for part in name.split('_'):
            camel += part.capitalize()
        return camel


class Insert:

    def do(self, requirements, includes, methods):
        self.insert_requirements(requirements)
        self.insert_includes(includes)
        self.insert_methods(methods)

    @staticmethod
    def insert_requirements(requirements):
        """ Merge the required libraries into the master. """
        requirements = list(requirements)
        requirements.sort()
        # include these with the other requirements for our package
        insert_lines = ''
        for requirement in requirements:
            insert_lines += f'    {requirement}\n'
        # TODO Finish this and don't repeat things that are required for other reasons.
        # self._put_anchored_lines(target_file=self.file_setup, anchor='setup.cfg', insert_lines=insert_lines)

    def insert_includes(self, includes):
        """ Insert the includes for all libraries. """
        insert_lines = '\n'.join(includes) + '\n'
        self._put_anchored_lines(target_file=Locations.file_ebay_rest, anchor='er_imports', insert_lines=insert_lines)

    def insert_methods(self, methods: str) -> None:
        """ Make all the python methods and insert them where needed. """

        methods = "\n" + methods
        self._put_anchored_lines(target_file=Locations.file_ebay_rest, anchor='er_methods', insert_lines=methods)

    @staticmethod
    def _put_anchored_lines(target_file: str, anchor: str, insert_lines: str) -> None:
        """ In the file replace what is between anchors with new lines of code. """

        if os.path.isfile(target_file):
            new_lines = ''
            start = f"ANCHOR-{anchor}-START"
            end = f"ANCHOR-{anchor}-END"
            start_found = False
            end_found = False

            with open(target_file) as file:
                for old_line in file:
                    if not start_found:
                        new_lines += old_line
                        if start in old_line:
                            start_found = True
                            new_lines += insert_lines
                    elif start_found and not end_found:
                        if end in old_line:
                            end_found = True
                            new_lines += old_line
                    else:
                        new_lines += old_line

            if start_found and end_found:
                with open(target_file, 'w') as file:
                    file.write(new_lines)

            else:
                logging.error(f"Can't find proper start or end anchors for {anchor} in {target_file}.")
        else:
            logging.error(f"Can't find {target_file}")


async def process_overview_link(overview_link):
    logging.info(f"Process overview link {overview_link}.")
    c = Contracts(overview_link)
    await c.process()
    name = c.name
    requirement = c.get_requirements()
    include = c.get_includes()
    method = await c.get_methods()
    return include, method, name, requirement


async def generate_apis():
    """
    Generate the contents of the api folder in src/ebay_rest and some code in a_p_i.py.

    For a complete directory of eBay's APIs visit https://developer.ebay.com/docs. Ignore the "Traditional" APIs.

    For an introduction to OpenAPI and how to use eBay's REST-ful APIs
    visit https://developer.ebay.com/api-docs/static/openapi-swagger-codegen.html.
    :return:
    """
    await asyncio.gather(
        ensure_cache(),
        ensure_swagger(),
        Contracts.purge_existing()
    )

    limit = 100  # lower to expedite debugging with a reduced data set
    records = list()
    tasks = list()
    overview_links = await Contracts.get_overview_links()
    for overview_link in overview_links[:limit]:
        task = asyncio.create_task(process_overview_link(overview_link))
        tasks.append(task)
    for task in tasks:
        record = await task
        records.append(record)

    names = list()
    requirements = set()
    includes = list()
    methods = str()
    for record in records:
        include, method, name, requirement = record
        names.append(name)
        requirements.update(requirement)
        includes.extend(include)
        methods += method
    Insert().do(requirements, includes, methods)
    # p.remove_duplicates(names)     # uncomment the method call when work on it resumes


async def main() -> None:
    start = time.time()

    # while debugging, it is handy to change the log level from INFO to DEBUG
    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s %(lineno)d %(funcName)s: %(message)s',
                        level=logging.DEBUG)

    await asyncio.gather(generate_apis(), generate_references())
    logging.info(f'Run time was {int(time.time() - start)} seconds.')
    return


if __name__ == "__main__":
    asyncio.run(main())     # Python 3.7+
