#!/usr/bin/python3

# Standard library imports
from datetime import datetime, timedelta
import hashlib
import json
import logging
import os
import sys
from urllib.request import urlopen
from urllib.parse import urljoin
import shutil
from sys import platform
from typing import Any, Dict, List, Optional, Tuple

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
    target_path: str = '../src/ebay_rest/' + target_directory
    cache_path: str = './' + target_directory + '_cache'

    state_file: str = 'state.json'
    state_path_file: str = os.path.join(cache_path, state_file)


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


class Contract:

    def __init__(self, limit: int = 100) -> None:
        self.contracts = self.get_contracts(limit=limit)
        self.cache_contracts()
        self.patch_contracts()

    def cache_contracts(self) -> None:
        for contract in self.contracts:
            [category, call, link_href, file_name] = contract
            with urlopen(link_href) as url:
                data = json.loads(url.read().decode())
                destination = os.path.join(Locations.cache_path, file_name)
                with open(destination, 'w') as outfile:
                    json.dump(data, outfile, sort_keys=True, indent=4)

    def get_contracts(self, limit: int = 100) -> List[List[str]]:
        contracts = []
        overview_links = []
        base = 'https://developer.ebay.com/'

        logging.info('Find eBay OpenAPI 3 JSON contracts.')

        soup = self.get_soup_via_link(urljoin(base, 'docs'))
        for link in soup.find_all('a', href=lambda href: href and 'overview.html' in href):
            overview_links.append(urljoin(base, link.get('href')))
            if len(contracts) >= limit:
                break
        assert (len(overview_links) > 0), 'No contract overview pages found!'

        for overview_link in overview_links:
            soup = self.get_soup_via_link(overview_link)
            for link in soup.find_all('a', href=lambda href: href and 'oas3.json' in href, limit=1):
                link_href = urljoin(base, link.get('href'))
                parts = link_href.split('/')
                category = parts[5]
                call = parts[6].replace('-', '_')
                file_name = parts[-1]
                record = [category, call, link_href, file_name]
                if ('beta' not in call) and (record not in contracts):
                    contracts.append(record)
                    logging.info(record)
            if len(contracts) >= limit:  # useful for expediting debugging with a reduced data set
                break
        assert (len(contracts) > 0), 'No contracts found on any overview pages!'

        return contracts

    @staticmethod
    def patch_contracts() -> None:

        # In the Sell Fulfillment API, the model 'Address' is returned with attribute 'countryCode'.
        # However, the JSON specifies 'country' instead, thus Swagger generates the wrong API.
        file_location = os.path.join(Locations.cache_path, 'sell_fulfillment_v1_oas3.json')
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

    def get_base_paths_and_flows(self) -> Tuple[dict, Dict[Any, dict], Dict[Any, Dict[Any, Optional[Any]]]]:
        """Process the JSON contract and extract two things for later use.
        1) the base_path for each category_call (e.g. buy_browse)
        2) the security flow for each scope in each category_call
        3) the scopes for each call in each category_call
        """
        base_paths = {}
        flows = {}
        scopes = {}

        for [category, call, link_href, file_name] in self.contracts:
            source = os.path.join(Locations.cache_path, file_name)
            with open(source) as file_handle:
                data = json.load(file_handle)
            # Get base path
            base_path = data['servers'][0]['variables']['basePath']['default']
            # Get flows for this category_call
            category_flows = (
                data['components']['securitySchemes']['api_auth']['flows']
            )
            flow_by_scope = {}  # dict of scope: flow type
            for flow, flow_details in category_flows.items():
                for scope in flow_details['scopes']:
                    flow_by_scope[scope] = flow

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
                        raise ValueError(
                            'Expected zero/one security entry per path!')
                    elif len(security_list) == 1:
                        security = security_list[0]['api_auth']
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
            base_paths[name] = base_path
            flows[name] = flow_by_scope
            scopes[name] = operation_id_scopes

        return base_paths, flows, scopes


def install_tools() -> None:
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

    def __init__(self) -> None:
        self.file_ebay_rest = os.path.abspath('../src/ebay_rest/a_p_i.py')
        self.file_setup = os.path.abspath('../setup.cfg')

        self.path_cache = os.path.abspath(Locations.cache_path)
        self.path_final = os.path.abspath(Locations.target_path)
        self.path_ebay_rest = os.path.abspath('../src/ebay_rest')

        assert os.path.isdir(self.path_cache), \
            'Fatal error. Prior, you must run the script generate_api_cache.py.'
        for (_root, dirs, _files) in os.walk(self.path_cache):
            dirs.sort()
            self.names = dirs
            break

        with open(os.path.join(Locations.cache_path, 'base_paths.json')) as file_handle:
            self.base_paths = json.load(file_handle)
        with open(os.path.join(Locations.cache_path, 'flows.json')) as file_handle:
            self.flows = json.load(file_handle)
        with open(os.path.join(Locations.cache_path, 'scopes.json')) as file_handle:
            self.scopes = json.load(file_handle)

    def copy_libraries(self) -> None:
        """ Copy essential parts of the generated eBay libraries to within the src folder. """
        # purge what might already be there
        for filename in os.listdir(self.path_final):
            file_path = os.path.join(self.path_final, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # copy each library's directory
        for name in self.names:
            src = os.path.join(self.path_cache, name, name)
            dst = os.path.join(self.path_final, name)
            _destination = shutil.copytree(src, dst)

    def fix_imports(self) -> None:
        """ The deeper the directory, the more dots are needed to make the correct relative path. """
        for name in self.names:
            self._fix_imports_recursive(name, '..', os.path.join(self.path_final, name))

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

    def merge_setup(self) -> None:
        """ Merge the essential bits of the generated setup files into the master. """

        # compile a list of all unique requirements from the generated libraries
        start_tag = 'REQUIRES = ['
        end_tag = ']\n'
        requirements = set()
        for name in self.names:
            src = os.path.join(self.path_cache, name, 'setup.py')
            with open(src) as file:
                for line in file:
                    if line.startswith(start_tag):
                        line = line.replace(start_tag, '')
                        line = line.replace(end_tag, '')
                        parts = line.split(', ')
                        for part in parts:
                            requirements.add(part)
                        break
        requirements = list(requirements)
        requirements.sort()

        # include these with the other requirements for our package
        insert_lines = ''
        for requirement in requirements:
            insert_lines += f'    {requirement}\n'
        # TODO This was commented out because it caused an error. Is something like it truly needed?
        # self._put_anchored_lines(target_file=self.file_setup, anchor='setup.cfg', insert_lines=insert_lines)

    def make_includes(self) -> None:
        """ Make includes for all the libraries. """

        lines = []
        for name in self.names:
            lines.append(f'from .{Locations.target_directory} import {name}')
            line = f'from .{Locations.target_directory}.{name}.rest import ApiException as {self._camel(name)}Exception'
            lines.append(line)
        insert_lines = '\n'.join(lines) + '\n'
        self._put_anchored_lines(target_file=self.file_ebay_rest, anchor='er_imports', insert_lines=insert_lines)

    def get_methods(self) -> List[Tuple[str, str, str, str, str, str]]:
        """ For all modules, get all methods. """

        # catalog the module files that contain all method implementations
        modules = []
        for name in self.names:
            path = os.path.join(self.path_cache, name, name, 'api')
            for (root, _dirs, files) in os.walk(path):
                for file in files:
                    if file != '__init__.py':
                        modules.append((name, file.replace('.py', ''), os.path.join(root, file)))

        # catalog all methods in all modules
        methods = []
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

    def make_methods(self, methods: List[Tuple[str, str, str, str, str, str]]) -> None:
        """ Make all the python methods and insert them where needed. """

        code = "\n"
        for method in methods:
            code += self._make_method(method)
        self._put_anchored_lines(target_file=self.file_ebay_rest, anchor='er_methods', insert_lines=code)

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

    def remove_duplicates(self) -> None:
        """ Deduplicate identical .py files found in all APIs.
        for example when comments are ignored the rest.py files appear identical. """

        # build a catalog that includes a hashed file signature
        catalog = []
        for name in self.names:
            catalog.extend(self._remove_duplicates_recursive_catalog(name, os.path.join(self.path_final, name)))

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

    # ensure that we have a cache
    if os.path.isdir(Locations.cache_path):
        # delete_folder_contents(Locations.cache_path)  # TODO flush the cache when we want a fresh start
        pass
    else:
        os.mkdir(Locations.cache_path)

    s = State()  # Track the state of progress

    # install tools if they are missing # TODO
    # or, update tools if it has been more than a day
    key = 'tool_date_time'
    dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    if s.get(key) is None or datetime.strptime(s.get(key), dt_format) < datetime.now() - timedelta(days=1):
        # install_tools()
        s.set(key, datetime.now().strftime(dt_format))

    c = Contract(limit=100)  # hint, save time by reducing the limit while debugging

    base_paths, flows, scopes = c.get_base_paths_and_flows()

    logging.info('For each contract generate and install a library.')
    for contract in c.contracts:
        [category, call, link_href, file_name] = contract
        source = os.path.join(Locations.cache_path, file_name)
        name = f'{category}_{call}'
        command = f' generate -l python -o {Locations.cache_path}/{name} -DpackageName={name} -i {source}'
        if platform == 'darwin':  # OS X or MacOS
            command = '/usr/local/bin/swagger-codegen' + command
        elif platform == 'linux':  # Linux
            command = 'java -jar swagger-codegen-cli.jar' + command
        else:
            assert False, f'Please extend main() for your {platform} platform.'
        os.system(command)

    destination = os.path.join(Locations.cache_path, 'base_paths.json')
    with open(destination, 'w') as outfile:
        json.dump(base_paths, outfile, sort_keys=True, indent=4)
    destination = os.path.join(Locations.cache_path, 'flows.json')
    with open(destination, 'w') as outfile:
        json.dump(flows, outfile, sort_keys=True, indent=4)
    destination = os.path.join(Locations.cache_path, 'scopes.json')
    with open(destination, 'w') as outfile:
        json.dump(scopes, outfile, sort_keys=True, indent=4)

    # Refrain from altering the sequence of the method calls because there may be dependencies.
    p = Process()
    p.copy_libraries()
    p.fix_imports()
    p.merge_setup()
    p.make_includes()
    # p.remove_duplicates()     # uncomment the method call when work on it resumes
    p.make_methods(p.get_methods())

    return


if __name__ == "__main__":
    main()
