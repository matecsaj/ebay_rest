#!/usr/bin/python3

# Standard library imports
import json
import os
from urllib.request import urlopen
from urllib.parse import urljoin
import shutil
from sys import platform

# Third party imports
from bs4 import BeautifulSoup
import requests

# Local imports

# Globals
TARGET_PATH = 'api_cache'


# Run this long-running script from the command line to generate the api_cache folder.
# The run the quick-running process_api_cache.py script.

# For a complete directory of eBay's APIs visit https://developer.ebay.com/docs. Ignore the "Traditional" APIs.

# For an introduction to OpenAPI and how to use eBay's REST-ful APIs
# visit https://developer.ebay.com/api-docs/static/openapi-swagger-codegen.html.


def get_soup_via_link(url):
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse the html content
    return BeautifulSoup(html_content, "html.parser")


def get_contracts(limit=100):
    contracts = []
    overview_links = []
    base = 'https://developer.ebay.com/'

    print('Find eBay OpenAPI 3 JSON contracts.')

    soup = get_soup_via_link(urljoin(base, 'docs'))
    for link in soup.find_all('a', href=lambda href: href and 'overview.html' in href):
        overview_links.append(urljoin(base, link.get('href')))
        if len(contracts) >= limit:
            break
    assert(len(overview_links) > 0), 'No contract overview pages found!'

    for overview_link in overview_links:
        soup = get_soup_via_link(overview_link)
        for link in soup.find_all('a', href=lambda href: href and 'oas3.json' in href, limit=1):
            link_href = urljoin(base, link.get('href'))
            parts = link_href.split('/')
            category = parts[5]
            call = parts[6].replace('-', '_')
            record = [category, call, link_href]
            if ('beta' not in call) and (record not in contracts):
                contracts.append(record)
                print(record)
        if len(contracts) >= limit:         # useful for expediting debugging with a reduced data set
            break
    assert(len(contracts) > 0), 'No contracts found on any overview pages!'

    return contracts


def get_base_paths_and_flows(contracts):
    """Process the JSON contract and extract two things for later use.
    1) the base_path for each category_call (e.g. buy_browse)
    2) the security flow for each scope in each category_call
    3) the scopes for each call in each category_call
    """
    base_paths = {}
    flows = {}
    scopes = {}

    for (category, call, link_href) in contracts:
        with urlopen(link_href) as url:
            data = json.loads(url.read().decode())
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
                    print('Duplicate operation!')
                    print(path, path_methods)
                    print(method, method_dict)
                    raise ValueError('nope')
                operation_id_scopes[operation_id] = security

        name = category + '_' + call
        base_paths[name] = base_path
        flows[name] = flow_by_scope
        scopes[name] = operation_id_scopes

    return base_paths, flows, scopes


def install_tools():
    if platform == 'darwin':    # OS X or MacOS
        print('Install or update the package manager named HomeBrew.')
        os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

        if os.path.isfile('/usr/local/bin/swagger-codegen'):
            print('Upgrade the code generator from Swagger. https://swagger.io/')
            os.system('brew upgrade swagger-codegen')
        else:
            print('Install the code generator from Swagger. https://swagger.io/')
            os.system('brew install swagger-codegen')

        print('Test the generator installation by invoking its help screen.')
        os.system('/usr/local/bin/swagger-codegen -h')
    elif platform == 'linux':  # Linux platform
        # Don't install packages without user interaction.
        if not os.path.isfile('swagger-codegen-cli.jar'):
            os.system(
                'wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/'
                + 'swagger-codegen-cli/3.0.26/swagger-codegen-cli-3.0.26.jar '
                + '-O swagger-codegen-cli.jar'
            )
        print('Test the generator installation by invoking its help screen.')
        os.system('java -jar swagger-codegen-cli.jar -h')
    else:
        assert False, f'Please extend install_tools() for your {platform} platform.'


def delete_folder_contents(path_to_folder):
    list_dir = os.listdir(path_to_folder)
    for filename in list_dir:
        file_path = os.path.join(path_to_folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            print("deleting file:", file_path)
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            print("deleting folder:", file_path)
            shutil.rmtree(file_path)


def main():
    install_tools()

    # ensure that we have an empty cache directory
    if os.path.isdir(TARGET_PATH):
        delete_folder_contents(TARGET_PATH)
    else:
        os.mkdir(TARGET_PATH)

    contracts = get_contracts(limit=300)
    base_paths, flows, scopes = get_base_paths_and_flows(contracts)

    print('For each contract generate and install a library.')
    for contract in contracts:
        category, call, url = contract
        name = f'{category}_{call}'
        if platform == 'darwin':  # OS X or MacOS
            command = f'/usr/local/bin/swagger-codegen generate -l python ' \
                      f'-o {TARGET_PATH}/{name} -DpackageName={name} -i {url} '
        elif platform == 'linux':  # Linux
            command = f'java -jar swagger-codegen-cli.jar generate -l python ' \
                      f'-o {TARGET_PATH}/{name} -DpackageName={name} -i {url} '
        else:
            assert False, f'Please extend main() for your {platform} platform.'
        os.system(command)

    destination = os.path.join(TARGET_PATH, 'base_paths.json')
    with open(destination, 'w') as outfile:
        json.dump(base_paths, outfile, sort_keys=True, indent=4)
    destination = os.path.join(TARGET_PATH, 'flows.json')
    with open(destination, 'w') as outfile:
        json.dump(flows, outfile, sort_keys=True, indent=4)
    destination = os.path.join(TARGET_PATH, 'scopes.json')
    with open(destination, 'w') as outfile:
        json.dump(scopes, outfile, sort_keys=True, indent=4)

    return


if __name__ == "__main__":
    main()
