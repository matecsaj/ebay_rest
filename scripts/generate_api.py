#!/usr/bin/python3

# Standard library imports
from datetime import datetime, timedelta
import hashlib
import json
import logging
import os
import sys
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import urlretrieve
import shutil
from sys import platform
from typing import List, Tuple, Set

# Third party imports
import bs4
from bs4 import BeautifulSoup
import requests


# Local imports

# Globals

# Run this script from the command line to generate or update the api folder in src/ebay_rest.

# For a complete directory of eBay's APIs visit https://developer.ebay.com/docs. Ignore the "Traditional" APIs.

# For an introduction to OpenAPI and how to use eBay's REST-ful APIs
# visit https://developer.ebay.com/api-docs/static/openapi-swagger-codegen.html.


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


def ensure_cache():
    # ensure that we have a cache
    if os.path.isdir(Locations.cache_path):
        # delete_folder_contents(Locations.cache_path)  # TODO flush the cache when we want a fresh start
        pass
    else:
        os.mkdir(Locations.cache_path)


def ensure_swagger() -> None:
    s = State()  # skip if this was already done less than a day ago
    key = 'tool_date_time'
    dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    if s.get(key) is None or datetime.strptime(s.get(key), dt_format) < datetime.now() - timedelta(days=1):

        if platform == 'darwin':  # OS X or MacOS
            logging.info('Install or update the package manager named HomeBrew.')
            os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

            if os.path.isfile('/usr/local/bin/swagger-codegen'):
                logging.info('Upgrade the code generator from Swagger. https://swagger.io/')
                os.system('brew upgrade swagger-codegen')
            else:
                logging.info('Install the code generator from Swagger. https://swagger.io/')
                os.system('brew install swagger-codegen')

            logging.info('Test the generator installation by invoking its help screen.')
            os.system('/usr/local/bin/swagger-codegen -h')
        elif platform == 'linux':  # Linux platform
            # Don't install packages without user interaction.
            if not os.path.isfile('swagger-codegen-cli.jar'):
                os.system(
                    'wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/'
                    + 'swagger-codegen-cli/3.0.26/swagger-codegen-cli-3.0.26.jar '
                    + '-O swagger-codegen-cli.jar'
                )
            logging.info('Test the generator installation by invoking its help screen.')
            os.system('java -jar swagger-codegen-cli.jar -h')
        else:
            message = f'Please extend install_tools() for your {platform} platform.'
            logging.fatal(message)
            sys.exit(message)

        s.set(key, datetime.now().strftime(dt_format))


class Contracts:

    def __init__(self, limit: int = 100) -> None:
        self.contracts = []

        for overview_link in self.get_overview_links():
            contract = self.get_contract(overview_link)
            self.cache_contract(contract)
            self.patch_contract(contract)
            self.contracts.append(contract)

            if len(self.contracts) >= limit:  # useful for expediting debugging with a reduced data set
                break

    def get_overview_links(self):
        logging.info('Get a list of links to overview pages; pages contain links to eBay OpenAPI 3 JSON contracts.')

        overview_links = []
        developer_url = 'https://developer.ebay.com/'
        soup = self.get_soup_via_link(urljoin(developer_url, 'docs'))

        for link in soup.find_all('a', href=lambda href: href and 'overview.html' in href):
            path = link.get('href')
            if path.split('/')[6] == 'static':  # filter atypical links
                overview_link = urljoin(developer_url, path)
                if overview_link not in overview_links:     # filter redundant links
                    overview_links.append(overview_link)

        # safety check
        count = len(overview_links)
        logging.info('Found {count} links to overview pages.')
        assert (25 < count < 40), f'Having {count} contract overview links is unexpected!'

        overview_links.sort()
        return overview_links

    @staticmethod
    def cache_contract(contract):
        [_category, _call, link_href, file_name] = contract
        destination = os.path.join(Locations.cache_path, file_name)
        urlretrieve(link_href, destination)  # if a destination file exists, it will be replaced

    def get_contract(self, overview_link):
        # find the path to the json contract with the highest version number
        soup = self.get_soup_via_link(overview_link)
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

    @staticmethod
    def patch_contract(contract) -> None:
        [category, call, _link_href, file_name] = contract

        if category == 'sell' and call == 'fulfillment':
            Contracts.patch_contract_sell_fulfillment(file_name)

    @staticmethod
    def patch_contract_sell_fulfillment(file_name):
        # In the Sell Fulfillment API, the model 'Address' is returned with attribute 'countryCode'.
        # However, the JSON specifies 'country' instead, thus Swagger generates the wrong API.
        file_location = os.path.join(Locations.cache_path, file_name)
        try:
            with open(file_location) as file_handle:
                data = json.load(file_handle)
                properties = data['components']['schemas']['Address']['properties']
                if 'country' in properties:
                    properties['countryCode'] = properties.pop('country')  # Warning, alphabetical key order spoiled.
                    with open(file_location, 'w') as outfile:
                        json.dump(data, outfile, sort_keys=True, indent=4)
                else:
                    logging.warning('Patching sell_fulfillment_v1_oas3.json is no longer needed.')
        except FileNotFoundError:
            logging.error(f"Can't open {file_location}.")

    @staticmethod
    def get_soup_via_link(url: str) -> bs4.BeautifulSoup:
        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url).text

        # Parse the html content
        return BeautifulSoup(html_content, "html.parser")

    @staticmethod
    def swagger_codegen(call, category, file_name):
        logging.info('For each contract generate and install a library.')
        source = os.path.join(Locations.cache_path, file_name)
        name = Contracts.get_api_name(call, category)
        command = f' generate -l python -o {Locations.cache_path}/{name} -DpackageName={name} -i {source}'
        if platform == 'darwin':  # OS X or MacOS
            command = '/usr/local/bin/swagger-codegen' + command
        elif platform == 'linux':  # Linux
            command = 'java -jar swagger-codegen-cli.jar' + command
        else:
            assert False, f'Please extend main() for your {platform} platform.'
        os.system(command)

    @staticmethod
    def get_api_name(call, category):
        name = f'{category}_{call}'
        return name

    @staticmethod
    def get_one_base_paths_and_flows(call, category, file_name):
        """Process the JSON contract and extract three things for later use.
        1) the base_path for each category_call (e.g. buy_browse)
        2) the security flow for each scope in each category_call
        3) the scopes for each call in each category_call
        """
        source = os.path.join(Locations.cache_path, file_name)
        with open(source) as file_handle:
            try:
                data = json.load(file_handle)
            except ValueError:
                message = "Invalid JSON in " + source
                logging.fatal(message)  # Invalid \escape: line 3407 column 90 (char 262143)
                sys.exit(message)
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
        name = category + '_' + call
        return base_path, flow_by_scope, name, operation_id_scopes


def delete_folder_contents(path_to_folder: str):
    list_dir = os.listdir(path_to_folder)
    for filename in list_dir:
        file_path = os.path.join(path_to_folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            logging.debug("deleting file:", file_path)
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            logging.debug("deleting folder:", file_path)
            shutil.rmtree(file_path)


class Process:
    """ The processing steps are split into bite sized methods. """

    def __init__(self, base_paths, flows, scopes) -> None:

        self.base_paths = base_paths
        self.flows = flows
        self.scopes = scopes

    @staticmethod
    def purge_existing():
        # purge what might already be there
        for filename in os.listdir(Locations.target_path):
            file_path = os.path.join(Locations.target_path, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)

    @staticmethod
    def copy_library(name) -> None:
        """ Copy the essential parts of the generated eBay library to within the src folder. """
        src = os.path.join(Locations.cache_path, name, name)
        dst = os.path.join(Locations.target_path, name)
        _destination = shutil.copytree(src, dst)

    def fix_imports(self, name) -> None:
        """ The deeper the directory, the more dots are needed to make the correct relative path. """
        self._fix_imports_recursive(name, '..', os.path.join(Locations.target_path, name))

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

    @staticmethod
    def get_requirements(name) -> Set[str]:
        """ Get the library's requirements. """

        # compile the set of all unique requirements from the generated library
        start_tag = 'REQUIRES = ['
        end_tag = ']\n'
        requirements = set()
        src = os.path.join(Locations.cache_path, name, 'setup.py')
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

    def get_includes(self, name) -> List[str]:
        """ Get the includes for a library. """
        includes = list()
        includes.append(f'from .{Locations.target_directory} import {name}')
        line = f'from .{Locations.target_directory}.{name}.rest import ApiException as {self._camel(name)}Exception'
        includes.append(line)
        return includes

    def insert_includes(self, includes):
        """ Insert the includes for all libraries. """
        insert_lines = '\n'.join(includes) + '\n'
        self._put_anchored_lines(target_file=Locations.file_ebay_rest, anchor='er_imports', insert_lines=insert_lines)

    @staticmethod
    def get_methods(name) -> List[Tuple[str, str, str, str, str, str]]:
        """ For all modules, get all methods. """

        # catalog the module files that contain all method implementations
        modules = []
        path = os.path.join(Locations.cache_path, name, name, 'api')
        for (root, _dirs, files) in os.walk(path):
            for file in files:
                if file != '__init__.py':
                    modules.append((name, file.replace('.py', ''), os.path.join(root, file)))

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
        typo_remedy = (  # pairs of typos found in docstrings and their remedy
            ('cerate', 'create'),  # noqa: - suppress flake8 compatible linters, misspelling is intended
            ('distibuted', 'distributed'),  # noqa:
            ('http:', 'https:'),  # noqa:
            ('identfier', 'identifier'),  # noqa:
            ('Limt', 'Limit'),  # noqa:
            ('lisitng', 'listing'),  # noqa:
            ('maketplace', 'marketplace'),  # noqa:
            ('motorcyles', 'motorcycles'),  # noqa:
            ('parmeter', 'parameter'),  # noqa:
            ('publlish', 'publish'),  # noqa:
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
                            for (typo, remedy) in typo_remedy:
                                docstring = docstring.replace(typo, remedy)
                            methods.append((name, module, path, method, params, docstring))
                            step = 0

        methods.sort()

        return methods

    def insert_methods(self, methods: List[Tuple[str, str, str, str, str, str]]) -> None:
        """ Make all the python methods and insert them where needed. """

        code = "\n"
        for method in methods:
            code += self._make_method(method)
        self._put_anchored_lines(target_file=Locations.file_ebay_rest, anchor='er_methods', insert_lines=code)

    def _make_method(self, method: Tuple[str, str, str, str, str, str]) -> str:
        """ Return the code for one python method. """

        (name, module, path, method, params, docstring) = method
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
        scopes = self.scopes[name][operation_id]
        if not scopes:
            # Assume application keys
            flows = {'clientCredentials'}
        else:
            flows = {self.flows[name][scope] for scope in scopes}
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
                f" '{self.base_paths[name]}'," \
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


def main() -> None:
    # while debugging it is handy to change the log level from INFO to DEBUG
    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s %(funcName)s: %(message)s', level=logging.DEBUG)

    ensure_cache()
    ensure_swagger()
    Process.purge_existing()

    contracts = Contracts(limit=100)  # hint, save time by reducing the limit while debugging

    base_paths = {}
    flows = {}
    scopes = {}

    names = list()
    requirements = set()
    includes = list()
    methods = list()

    for contract in contracts.contracts:
        [category, call, _link_href, file_name] = contract

        Contracts.swagger_codegen(call, category, file_name)

        base_path, flow_by_scope, name, operation_id_scopes = \
            Contracts.get_one_base_paths_and_flows(call, category, file_name)
        base_paths[name] = base_path
        flows[name] = flow_by_scope
        scopes[name] = operation_id_scopes

    p = Process(base_paths, flows, scopes)
    for contract in contracts.contracts:
        [category, call, _link_href, _file_name] = contract
        name = Contracts.get_api_name(call, category)
        names.append(name)
        p.copy_library(name)
        p.fix_imports(name)
        requirements.update(p.get_requirements(name))
        includes.extend(p.get_includes(name))
        methods.extend(p.get_methods(name))
    p.insert_requirements(requirements)
    p.insert_includes(includes)
    p.insert_methods(methods)
    # p.remove_duplicates(names)     # uncomment the method call when work on it resumes

    return


if __name__ == "__main__":
    main()
