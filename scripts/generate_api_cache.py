#!/usr/bin/python3

# Standard library imports
import os
from urllib.parse import urljoin

# Third party imports
from bs4 import BeautifulSoup
import requests

# Local imports

# Globals


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


def install_tools():
    print('Install or update the package manager named HomeBrew.')
    os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

    print('Install the code generator from Swagger. https://swagger.io/')
    os.system('brew install swagger-codegen')

    print('Test the generator installation by invoking its help screen.')
    os.system('/usr/local/bin/swagger-codegen -h')

    return


def main():

    install_tools()
    contracts = get_contracts(limit=100)

    print('For each contract generate and install a library.')
    for contract in contracts:
        category, call, url = contract
        name = f'{category}_{call}'
        command = f'/usr/local/bin/swagger-codegen generate -l python ' \
                  f'-o api_cache/{name} -DpackageName={name} -i {url} '
        # print(command)
        os.system(command)

    return


if __name__ == "__main__":
    main()
