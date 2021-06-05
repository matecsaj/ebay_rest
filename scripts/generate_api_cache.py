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


def get_base_paths(contracts):
    base_paths = {}

    for (category, call, link_href) in contracts:
        with urlopen(link_href) as url:
            data = json.loads(url.read().decode())
            base_path = data['servers'][0]['variables']['basePath']['default']
            name = category + '_' + call
            base_paths[name] = base_path

    return base_paths


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


def fix_bug_item_filter():
    """ The item filtering parameter should be filters instead of filter. """
    path = os.path.join(TARGET_PATH, 'buy_browse/buy_browse/api/item_summary_api.py')
    with open(path, 'r') as f:
        text = f.read()

        if "'filters'" in text:
            print('fix_bug_item_filter() might not be needed anymore.')
            return

        text = text.replace("'filter'", "'filters'")
        text = text.replace(":param str filter:", ":param str filters:")
        text = text.replace(";filter=", ";filters=")
    with open(path, 'w') as f:
        f.write(text)


def main():
    install_tools()

    # ensure that we have an empty cache directory
    if os.path.isdir(TARGET_PATH):
        delete_folder_contents(TARGET_PATH)
    else:
        os.mkdir(TARGET_PATH)

    contracts = get_contracts(limit=300)
    base_paths = get_base_paths(contracts)

    print('For each contract generate and install a library.')
    for contract in contracts:
        category, call, url = contract
        name = f'{category}_{call}'
        if platform == 'darwin':  # OS X or MacOS
            command = f'/usr/local/bin/swagger-codegen generate -l python ' \
                      f'-o {TARGET_PATH}/{name} -DpackageName={name} -i {url} '
        else:
            assert False, f'Please extend main() for your {platform} platform.'
        os.system(command)

    destination = os.path.join(TARGET_PATH, 'base_paths.json')
    with open(destination, 'w') as outfile:
        json.dump(base_paths, outfile, sort_keys=True, indent=4)

    fix_bug_item_filter()
    return


if __name__ == "__main__":
    main()
