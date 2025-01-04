#!/usr/bin/python3
# Run this script from the command-line to get info from https://developer.ebay.com and generate code in the src folder.

# Wait day if this script intermittently fails to load pages from eBay's website.
# Perhaps making inhumanly frequent requests triggers eBay's DOS protection system.


# Standard library imports
import hashlib
from itertools import groupby
import json
import logging
from operator import itemgetter
import os
import re
import shutil
import sys
import string
import time
from typing import AsyncGenerator, Iterable, List, Set, Tuple

# Third party imports
import aiofiles
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit


# Local imports

# Globals


async def run_command(cmd):
    """Run a command line in a subprocess."""
    logger = logging.getLogger(__name__)
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    logger.debug(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        logger.debug(f"[stdout]\n{stdout.decode()}")
    if stderr:
        logger.error(f"[stderr]\n{stderr.decode()}")


async def get_table_via_link(url: str) -> list:
    data = []
    soup = await get_soup_via_link(url)
    # find the rows regarding Response Fields.
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        # put the rows into a table of data
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values
    if len(data) == 0:
        logging.warning(f"No data was extracted from {url}.")
    return data


async def make_json_file(source: dict or list, name: str) -> None:
    if len(source) > 0:
        path = "../src/ebay_rest/references/"
        async with aiofiles.open(path + name + ".json", mode="w") as outfile:
            await outfile.write(json.dumps(source, sort_keys=True, indent=4))
    else:
        logging.error(f"The json file for {name} should not be empty; not created.")


async def generate_country_codes() -> None:
    logging.info("Find the eBay's Country Codes.")

    # load the target webpage
    data = await get_table_via_link(await get_ebay_list_url("CountryCodeType"))

    # ignore header, convert to a dict & delete bad values
    dict_ = {}
    for datum in data[1:]:
        dict_[datum[0]] = datum[1]
    for bad_value in ("CustomCode", "QM", "QN", "QO", "TP", "UM", "YU", "ZZ"):
        if bad_value in dict_:
            del dict_[bad_value]
        else:
            logging.debug("Bad value " + bad_value + "no longer needs to be deleted.")

    await make_json_file(dict_, "country_codes")


async def generate_currency_codes() -> None:
    logging.info("Find the eBay's Currency Codes.")

    # load the target webpage
    data = await get_table_via_link(await get_ebay_list_url("CurrencyCodeType"))

    # ignore header, convert to a dict & delete bad values
    dict_ = {}
    for datum in data[1:]:
        dict_[datum[0]] = datum[1]

    bad_values = ("CustomCode",)
    to_delete = set()
    for key, value in dict_.items():
        if key in bad_values or "replaced" in value:
            to_delete.add(key)
    for key in to_delete:
        del dict_[key]

    await make_json_file(dict_, "currency_codes")


async def generate_global_id_values() -> None:
    logging.info("Find the eBay's Global ID Values.")

    # load the target webpage
    url = "https://developer.ebay.com/Devzone/merchandising/docs/CallRef/Enums/GlobalIdList.html"
    data = await get_table_via_link(url)

    # the header got messed up and is unlikely to change, so hard code it
    cols = ["global_id", "language", "territory", "site_name", "ebay_site_id"]

    # convert to a list of dicts
    dicts = []
    for datum in data[1:]:
        my_dict = {}
        for index, column in enumerate(cols):
            my_dict[column] = datum[index]
        dicts.append(my_dict)

    await make_json_file(dicts, "global_id_values")


async def generate_marketplace_id_values() -> None:
    logging.info("Find the eBay's Marketplace ID Values.")

    my_dict = dict()

    # load the target webpage
    url = "https://developer.ebay.com/api-docs/static/rest-request-components.html#marketpl"
    soup = await get_soup_via_link(url)

    if soup:
        # find the rows regarding Response Fields.
        tables = soup.findAll("table")
        if len(tables) > 1:
            table = tables[1]  # the second table is index 1
            rows = table.find_all("tr")

            # put the rows into a table of data
            data = []
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])  # Get rid of empty values

            # the header got messed up and is unlikely to change, so hard code it
            # cols = ['marketplace_id', 'country', 'marketplace_site', 'locale_support']

            # convert to a nested dict

            for datum in data[1:]:
                [marketplace_id, country, marketplace_site, locale_support] = datum
                locale_support = locale_support.replace(" ", "")
                locales = locale_support.split(
                    ","
                )  # convert comma separated locales to a list of strings
                sites = re.findall(
                    r"https?://(?:[a-zA-Z0-9]|[._~:@!$&'()*+,;=%]|/)+",
                    marketplace_site,
                )
                comments = re.findall("\\(([^)]*)\\)", marketplace_site)
                comment_shortage = len(locales) - len(comments)
                for _ in range(comment_shortage):
                    comments.append("")
                my_locales = dict()
                for index, locale in enumerate(locales):
                    my_locales[locale] = [sites[index], comments[index]]
                my_dict[marketplace_id] = [country, my_locales]

    await make_json_file(my_dict, "marketplace_id_values")
    return


async def generate_link_text_and_urls(
    urls: Iterable[str],
) -> AsyncGenerator[Tuple[str, str], None]:
    """
    This function is an asynchronous generator that takes an iterable of URLs and for each URL, it fetches the HTML,
    parses it to find all anchor tags and yields a tuple of the link text and the absolute link URL.

    :param urls: An iterable of URLs to process.
    :return: An asynchronous generator that yields tuples of link text and URLs.
    """

    async def process_url(url: str) -> AsyncGenerator[Tuple[str, str], None]:
        soup = await get_soup_via_link(url)
        for link in soup.find_all("a"):
            yield link.text, urljoin(url, link.get("href"))

    async def gather_links(url: str) -> List[Tuple[str, str]]:
        return [link async for link in process_url(url)]

    tasks = [gather_links(url) for url in urls]
    for task in asyncio.as_completed(tasks):
        completed_task = await task
        for link_text, link_url in completed_task:
            yield link_text, link_url


async def get_soup_via_link(url: str) -> BeautifulSoup:
    # Get the html at an url and then make soup of it.

    # the header is meant to prevent the exception 'Response payload is not completed'
    headers = {"Connection": "keep-alive"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()  # this will raise an exception for 4xx and 5xx status
                html_content = await response.text()
                # Parse the html content
                return BeautifulSoup(html_content, "html.parser")
    except aiohttp.ClientConnectorError as e:
        logging.fatal(
            "The server dropped the connection on the TCP level; it may think we are a "
            f"denial-of-service attacker; try again tomorrow. {url}: {e}"
        )
        sys.exit()
    except Exception as e:
        logging.error(f"An error occurred while trying to get content from {url}: {e}")
        return BeautifulSoup(
            "", "html.parser"
        )  # return an empty soup object instead of None


async def generate_references():
    """
    Generated JSON files for the 'references' directory found in 'src'.

    If you add, delete or rename a json file, then alter /src/ebay_rest/reference.py accordingly.

    :return:
    """
    # TODO Clear out any junk that happens to be in the target folder.

    await asyncio.gather(
        generate_country_codes(),
        generate_currency_codes(),
        generate_global_id_values(),
        generate_marketplace_id_values(),
    )


async def get_ebay_list_url(code_type: str) -> str:
    """
    Make an url to an ebay "code type" list

    Here is the complete list of possible code types.
    https://developer.ebay.com/devzone/xml/docs/Reference/eBay/enumindex.html#EnumerationIndex

    If eBay modified the url you need to determine the new pattern;
    at https://developer.ebay.com/ search for "countrycodetype" and study the result.

    example: https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/countrycodetype.html
    """
    if not code_type:
        raise ValueError("code_type can't be None or empty")
    else:
        return f"https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/{code_type}.html"


class Locations:
    """Where things are located in the locale file store."""

    target_directory: str = "api"
    target_path: str = os.path.abspath("../src/ebay_rest/" + target_directory)
    cache_path: str = os.path.abspath("./" + target_directory + "_cache")

    state_file: str = "state.json"
    state_path_file: str = os.path.abspath(os.path.join(cache_path, state_file))

    file_ebay_rest = os.path.abspath("../src/ebay_rest/a_p_i.py")


class State:
    """Track the state of progress, even if the program is re-run."""

    def __init__(self) -> None:
        try:
            with open(Locations.state_path_file) as file_handle:
                self._states = json.load(file_handle)
        except OSError:
            self._states = dict()

    async def get(self, key: str) -> str or None:
        if key in self._states:
            return self._states[key]
        else:
            return None

    async def set(self, key: str, value: str) -> None:
        self._states[key] = value
        try:
            with open(Locations.state_path_file, "w") as file_handle:
                json.dump(self._states, file_handle, sort_keys=True, indent=4)
        except OSError:
            message = f"Can't write to {Locations.state_path_file}."
            logging.fatal(message)
            sys.exit(message)


async def ensure_cache():
    # ensure that we have an empty cache
    if os.path.isdir(Locations.cache_path):
        await Contracts.delete_folder_contents(Locations.cache_path)
    else:
        os.mkdir(Locations.cache_path)
    # warn developers that they should not edit the files in the cache
    readme = "# READ ME\n"
    readme += "Don't change the contents of this folder directly; instead, edit and run scripts/generate_code.py"
    path_file = os.path.abspath(os.path.join(Locations.cache_path, "README.md"))
    with open(path_file, "w") as file_handle:
        file_handle.write(readme)


class Contracts:
    def __init__(self, contract_link) -> None:
        self.contract_link = contract_link
        self.category = None
        self.call = None
        self.link_href = None
        self.file_name = None
        self.name = None
        self.version = None
        self.beta = None

    async def process(self):
        (
            self.category,
            self.call,
            self.link_href,
            self.file_name,
            self.version,
            self.beta,
        ) = await self.get_contract_info(self.contract_link)
        self.name = await self.get_api_name()
        await self.cache_contract()
        await self.patch_contract()
        await self.swagger_codegen()
        await self.patch_generated()
        await self.copy_library()
        await self.fix_imports()

    @staticmethod
    async def get_contract_links() -> List[str]:
        """
        This asynchronous function is designed to get the contract URLs from eBay's developer site.

        Args: None

        Returns:
            A sorted list of contract URLs.

        Examples:
            To use this function, simply call it without any arguments and await its result:

            :return:
        """
        logging.info("Get a list of links to eBay OpenAPI 3 JSON contracts.")

        # store the urls used while doing a breadth first search; seed with starting urls
        category_urls = {
            "https://developer.ebay.com/develop/selling-apps",
            "https://developer.ebay.com/develop/buying-apps",
        }
        table_urls = {
            "https://developer.ebay.com/develop/application-settings-and-insights"
        }
        overview_urls = set()
        contract_urls = set()

        # use the category urls to find unique links to API table pages with visible text containing 'APIs'
        async for link_text, link_url in generate_link_text_and_urls(category_urls):
            if "APIs" in link_text:
                table_urls.add(link_url)

        # use the table urls to find unique links to overview pages which have urls ending with overview.html
        async for link_text, link_url in generate_link_text_and_urls(table_urls):
            if link_url.endswith("overview.html"):
                overview_urls.add(link_url)

        # use the overview urls to find unique links to contracts which have urls ending with .json
        async for link_text, link_url in generate_link_text_and_urls(overview_urls):
            if link_url.endswith(".json"):
                contract_urls.add(link_url)

        contract_urls_sorted = sorted(list(contract_urls))

        # safety check
        count = len(contract_urls_sorted)
        logging.info(f"Found contract {count} links.")
        if not (20 < count < 40):
            logging.warning(f"Having {count} contract links is unexpected!")

        return contract_urls_sorted

    async def cache_contract(self):
        destination = os.path.join(Locations.cache_path, self.file_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.link_href) as response:
                text_content = await response.text()
        async with aiofiles.open(destination, mode="w") as f:
            await f.write(text_content)

    @staticmethod
    async def deduplicate_contract_links(contract_links: Iterable[str]) -> List[str]:
        """
        Remove redundant contracts, drop betas and lower versions.

        Args:
            contract_links (Iterable[str]): A iterable container of contract links.

        Returns:
            List[str]: A list of 'keeper' links which are unique based on their category, call, beta, and version.

        Raises:
            AssertionError: If the total number of links is not equal to the sum of 'keepers' and 'junkers'.

        """

        keepers = []
        junkers = []

        contract_infos = await asyncio.gather(
            *[Contracts.get_contract_info(link) for link in contract_links]
        )

        # Sort links based on category, call, beta, and version
        sorted_contract_infos = sorted(
            contract_infos, key=lambda info: (info[0], info[1], info[5], -info[4])
        )

        # Group links by category and call
        for _, group in groupby(sorted_contract_infos, key=itemgetter(0, 1)):
            group_list = list(group)
            if len(group_list) > 1:
                tp = True
            # The first element is the preferred link
            keepers.append(group_list[0][2])
            # Remaining elements are junkers
            junkers.extend([link_info[2] for link_info in group_list[1:]])

        if len(contract_infos) != len(keepers) + len(junkers):
            logging.warning(
                "Lengths of links, keepers, and junkers do not add up correctly - possible loss of data."
            )

        return keepers

    @staticmethod
    async def get_contract_info(
        contract_link: str,
    ) -> Tuple[str, str, str, str, int, bool]:
        """
        Async method to parse a contract link and extract key data components from it.

        This method breaks down the contract link into its constituent parts and retrieves crucial information such
        as the category, call, link_href, file_name, version and whether it is a beta contract.

        It does so by splitting the URL and path, conducts string manipulations and applies regex pattern matching
        to decipher the version of the contract.

        Args:
            contract_link (str): The contract link that needs to be parsed.

        Returns:
            Tuple[str, str, str, str, int, bool]: A tuple containing 'category', 'call', 'link_href', 'file_name',
            'version', and 'beta'.
        """
        # split in raw parts
        url_split = urlsplit(contract_link)
        path_split = url_split.path.split("/")

        # if the path has dedicated version number element, example 'v2", then extract the number and remove from list
        path_version = None
        for i in range(len(path_split)):
            if re.match("^v[0-9]+", path_split[i]):
                path_version = int(path_split[i][1:])  # extract number part
                del path_split[i]  # remove the version element
                break  # exit after first match

        # ensure that the split path had the expected number of elements
        if len(path_split) != 8:
            logging.warning(
                f"The variable path_split should contain 8, not {len(path_split)} items."
            )

        # get key data from the parts
        category = path_split[-5]
        call = path_split[-4].replace("-", "_")
        link_href = contract_link
        file_name = path_split[-1]
        beta = True if "_beta_" in contract_link else False

        # extract the version number from the filename; for example version 2 looks like this "_v2_"
        version_match = re.search(r"_v(\d+)_", file_name)
        filename_version = int(version_match.group(1)) if version_match else 0

        if path_version and path_version != filename_version:
            logging.warning(
                f"Variable path_version {path_version} should equal version {filename_version}."
            )

        return category, call, link_href, file_name, filename_version, beta

    async def patch_contract(self) -> None:
        """If the contract from eBay has an error then patch it before generating code."""
        # This is no longer needed, ebay fixed the problem, but I'm leaving it here for reference.
        # if self.category == 'sell' and self.call == 'fulfillment':
        #     await Contracts.patch_contract_sell_fulfillment(self.file_name)

    # This is no longer needed, ebay fixed the problem, but I'm leaving it here for reference.
    @staticmethod
    async def patch_contract_sell_fulfillment(file_name):
        # In the Sell Fulfillment API, the model 'Address' is returned with attribute 'countryCode'.
        # However, the JSON specifies 'country' instead, thus Swagger generates the wrong API.
        file_location = os.path.join(Locations.cache_path, file_name)
        try:
            async with aiofiles.open(file_location, mode="r") as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_location}.")
        else:
            data = json.loads(data)
            properties = data["components"]["schemas"]["Address"]["properties"]
            if "country" in properties:
                properties["countryCode"] = properties.pop(
                    "country"
                )  # Warning, alphabetical key order spoiled.
                data = json.dumps(data, sort_keys=True, indent=4)
                async with aiofiles.open(file_location, mode="w") as f:
                    await f.write(data)
            else:
                logging.warning(f"Patching {file_name} is no longer needed.")

    async def patch_generated(self) -> None:
        """If the generated code has an error then patch it before making use of it."""

        # API calls that have a return type fail when there is no content. This is because
        # there in attempt to de-serialize an empty string. If there is no content, indicated
        # by a 204 status then don't de-serialize.
        bad_code = "if response_type:"
        file_location = os.path.join(
            Locations.cache_path, self.name, self.name, "api_client.py"
        )
        try:
            async with aiofiles.open(file_location, mode="r") as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_location}.")
        else:
            if bad_code not in data:
                logging.error(
                    f"Maybe for {file_location} the 204 patch is not needed any longer."
                )
            else:
                # add a new condition before the colon
                data = data.replace(
                    bad_code,
                    bad_code[:-1]
                    + " and response_data.status != 204:       # ebay_rest patch",
                )
                async with aiofiles.open(file_location, mode="w") as f:
                    await f.write(data)

        # Patch in code for Digital Signatures
        file_location = os.path.join(
            Locations.cache_path, self.name, self.name, "rest.py"
        )
        try:
            async with aiofiles.open(file_location, mode="r") as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_location}.")
        else:
            # Add a new import
            target = "from six.moves.urllib.parse import urlencode"  # noqa:
            new_code = (
                "\nfrom ...digital_signatures import signed_request  # ebay_rest patch"
            )
            data = data.replace(target, target + new_code, 1)
            # Save key_pair to RESTClientObject
            target = "# https pool manager"
            new_code = "\n        self.key_pair = configuration.api_key.get('key_pair', None)  # ebay_rest patch"
            data = data.replace(target, target + new_code, 1)
            # Replace all pool manager calls with wrapped call
            target = "r = self.pool_manager.request(\n"
            replace_code = "r = signed_request(self.pool_manager, self.key_pair,  # ebay_rest patch\n"
            data = data.replace(target, replace_code)
            target = "r = self.pool_manager.request(method, url,\n"
            replace_code = "r = signed_request(self.pool_manager, self.key_pair, method, url,  # ebay_rest patch\n"
            data = data.replace(target, replace_code)
            async with aiofiles.open(file_location, mode="w") as f:
                await f.write(data)

    async def swagger_codegen(self):
        source = os.path.join(Locations.cache_path, self.file_name)
        destination = f"{Locations.cache_path}/{self.name}"

        # The generator will warn if there is no .swagger-codegen-ignore file
        if not os.path.isdir(destination):
            os.mkdir(destination)
        path_file = os.path.abspath(
            os.path.join(Locations.cache_path, ".swagger-codegen-ignore")
        )
        with open(path_file, "w") as file_handle:
            file_handle.write("")

        command = f" generate -l python -o {destination} -DpackageName={self.name} -i {source}"
        if sys.platform == "darwin":  # OS X or MacOS
            command = "/usr/local/bin/swagger-codegen" + command
        elif sys.platform == "linux":  # Linux
            command = "java -jar swagger-codegen-cli.jar" + command
        else:
            assert False, f"Please extend main() for your {sys.platform} platform."
        await run_command(command)

    async def get_api_name(self):
        name = f"{self.category}_{self.call}"
        return name

    async def get_one_base_paths_and_flows(self):
        """Process the JSON contract and extract three things for later use.
        1) the base_path for each category_call (e.g. buy_browse)
        2) the security flow for each scope in each category_call
        3) the scopes for each call in each category_call
        """
        source = os.path.join(Locations.cache_path, self.file_name)
        try:
            async with aiofiles.open(source, mode="r") as f:
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
                logging.fatal(
                    message
                )  # Invalid \escape: line 3407 column 90 (char 262143)
                sys.exit(message)
            else:
                # Get the contract's major version number
                if "swagger" in data:
                    (version_major, _version_minor) = data["swagger"].split(".")
                elif "openapi" in data:
                    (version_major, _version_minor, _version_tertiary) = data[
                        "openapi"
                    ].split(".")
                else:
                    message = f"{source} has no OpenAPI version number."
                    logging.fatal(
                        message
                    )  # Invalid \escape: line 3407 column 90 (char 262143)
                    sys.exit(message)
                # Get base path
                if version_major == "2":
                    base_path = data["basePath"]
                elif version_major == "3":
                    base_path = data["servers"][0]["variables"]["basePath"]["default"]
                else:
                    message = (
                        f"{source} has unrecognized OpenAPI version {version_major}."
                    )
                    logging.fatal(
                        message
                    )  # Invalid \escape: line 3407 column 90 (char 262143)
                    sys.exit(message)
                # Get flows for this category_call
                if version_major == "2":
                    category_flows = data["securityDefinitions"]
                elif version_major == "3":
                    category_flows = data["components"]["securitySchemes"]["api_auth"][
                        "flows"
                    ]
                else:
                    message = (
                        f"{source} has unrecognized OpenAPI version {version_major}."
                    )
                    logging.fatal(
                        message
                    )  # Invalid \escape: line 3407 column 90 (char 262143)
                    sys.exit(message)
                flow_by_scope = {}  # dict of scope: flow type
                for flow, flow_details in category_flows.items():
                    for scope in flow_details["scopes"]:
                        if flow == "Authorization Code":  # needed by version_major 2
                            value = "authorizationCode"
                        elif flow == "Client Credentials":  # needed by version_major 2
                            value = "clientCredentials"
                        else:
                            value = flow
                        flow_by_scope[scope] = value
                # Get scope for each individually path-ed call
                operation_id_scopes = {}
                for path, path_methods in data["paths"].items():
                    for method, method_dict in path_methods.items():
                        if method not in ("get", "post", "put", "delete"):
                            # Consider only the HTTP request parts
                            continue
                        operation_id = method_dict["operationId"].lower()
                        security_list = method_dict.get("security", [])
                        if len(security_list) > 1:
                            raise ValueError(
                                "Expected zero/one security entry per path!"
                            )
                        elif len(security_list) == 1:
                            if "api_auth" in security_list[0]:
                                security = security_list[0]["api_auth"]
                            elif (
                                "Authorization Code" in security_list[0]
                            ):  # needed by version_major 2
                                security = security_list[0]["Authorization Code"]
                            else:
                                raise ValueError(
                                    "Expected 'api_auth' or 'Authorization Code' in security_list!'"
                                )
                        else:
                            security = None
                        if operation_id in operation_id_scopes:
                            logging.warning("Duplicate operation!")
                            logging.warning(path, path_methods)
                            logging.warning(method, method_dict)
                            raise ValueError("nope")
                        operation_id_scopes[operation_id] = security
                # TODO Get headers parameters
                # look for this  "in": "header",
                name = self.category + "_" + self.call
        return base_path, flow_by_scope, name, operation_id_scopes

    @staticmethod
    async def delete_folder_contents(path_to_folder: str):
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

    async def copy_library(self) -> None:
        """Copy the essential parts of the generated eBay library to within the src folder."""
        src = os.path.join(Locations.cache_path, self.name, self.name)
        dst = os.path.join(Locations.target_path, self.name)
        _destination = shutil.copytree(src, dst)

    async def fix_imports(self) -> None:
        """The deeper the directory, the more dots are needed to make the correct relative path."""
        await self._fix_imports_recursive(
            self.name, "..", os.path.join(Locations.target_path, self.name)
        )

    async def _fix_imports_recursive(self, name: str, dots: str, path: str) -> None:
        """This does the recursive part of fix_imports."""

        for _root, dirs, files in os.walk(path):
            swaps = [  # order is crucial, put more specific swaps before less
                (f"import {name}.models", f"from {dots}{name} import models"),
                (f"from models", f"from {dots}{name}.models"),
                (f"import {name}", f"import {dots}{name}"),
                (f"from {name}", f"from {dots}{name}"),
                (f"{name}.models", f"models"),
            ]
            for file in files:
                target_file = os.path.join(path, file)
                new_lines = ""
                with open(target_file) as file_handle:
                    for old_line in file_handle:
                        for original, replacement in swaps:
                            if original in old_line:
                                old_line = old_line.replace(original, replacement)
                                break  # only the first matching swap should happen
                        new_lines += old_line
                with open(target_file, "w") as file_handle:
                    file_handle.write(new_lines)

            dots += "."
            for directory in dirs:
                await self._fix_imports_recursive(
                    name, dots, os.path.join(path, directory)
                )

            break

    async def get_requirements(self) -> Set[str]:
        """Get the library's requirements."""

        # compile the set of all unique requirements from the generated library
        start_tag = "REQUIRES = ["
        end_tag = "]\n"
        requirements = set()
        src = os.path.join(Locations.cache_path, self.name, "setup.py")
        try:
            with open(src) as file:
                for line in file:
                    if line.startswith(start_tag):
                        line = line.replace(start_tag, "")
                        line = line.replace(end_tag, "")
                        parts = line.split(", ")
                        for part in parts:
                            requirements.add(part)
                        break
        except FileNotFoundError:
            logging.error(
                f"The requirements for library {self.name} are unknown because a file is missing {src}."
            )

        return requirements

    async def get_includes(self) -> List[str]:
        """Get the includes for a library."""
        includes = list()
        includes.append(f"from .{Locations.target_directory} import {self.name}")
        line = (
            f"from .{Locations.target_directory}.{self.name}.rest import ApiException as "
            f"{await self._camel(self.name)}Exception"
        )
        includes.append(line)
        return includes

    async def get_methods(self) -> str:
        """For a modules, get all code for its methods."""

        # catalog the module files that contain all method implementations
        modules = []
        path = os.path.join(Locations.cache_path, self.name, self.name, "api")
        for root, _dirs, files in os.walk(path):
            for file in files:
                if file != "__init__.py":
                    modules.append(
                        (self.name, file.replace(".py", ""), os.path.join(root, file))
                    )

        # catalog all methods in all modules
        methods = list()
        method_marker_part = "_with_http_info"
        method_marker_whole = method_marker_part + "(self,"
        docstring_marker = '"""'
        bad_docstring_markers = (
            ">>> ",
            "synchronous",
            "async_req",
            "request thread",
        )
        for name, module, path in modules:
            step = 0
            with open(path) as file_handle:
                for line in file_handle:
                    if step == 0:  # looking for the next method
                        if method_marker_whole in line:
                            (method_and_params, _junk) = line.split(")")
                            (method, params) = method_and_params.split("(")
                            method = method.replace("    def ", "")
                            method = method.replace(method_marker_part, "")
                            params = params.replace("self, ", "")
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
                            methods.append(
                                (name, module, path, method, params, docstring)
                            )
                            step = 0

        methods.sort()

        code = str()
        for method in methods:
            code += await self._make_method(method)

        return code

    @staticmethod
    async def clean_docstring(docstring: string) -> string:
        # strip HTML
        docstring = BeautifulSoup(docstring, features="html.parser").get_text()

        # fix typos
        typo_remedy = (  # pairs of typos found in docstrings and their remedy
            (
                "AustraliaeBay",
                "Australia eBay",
            ),  # noqa: - suppress flake8 compatible linters, misspelling is intended
            ("cerate", "create"),  # noqa:
            ("distibuted", "distributed"),  # noqa:
            ("FranceeBay", "Francee Bay"),  # noqa:
            ("GermanyeBay", "Germany eBay"),  # noqa:
            ("http:", "https:"),  # noqa:
            ("identfier", "identifier"),  # noqa:
            ("ItalyeBay", "Italy eBay"),  # noqa:
            ("Limt", "Limit"),  # noqa:
            ("lisitng", "listing"),  # noqa:
            ("maketplace", "marketplace"),  # noqa:
            ("markeplace", "marketplace"),  # noqa:
            ("motorcyles", "motorcycles"),  # noqa:
            ("parmeter", "parameter"),  # noqa:
            ("publlish", "publish"),  # noqa:
            ("qroup", "group"),  # noqa:
            ("retrybable", "retryable"),  # noqa:
            ("takeback", "take back"),  # noqa:
            ("Takeback", "Take back"),  # noqa:
            ("theste", "these"),  # noqa:
            ("UKeBay", "UK eBay"),  # noqa:
        )
        for typo, remedy in typo_remedy:
            docstring = docstring.replace(typo, remedy)

        # Replace single backslash before pipe (if any) with double backslash
        docstring = docstring.replace(r"\|", r"\\|")

        # telling the linter to suppress long line warnings taints the Sphinx generated docs so filter them out
        docstring = docstring.replace("# noqa: E501", "")

        return docstring

    async def _make_method(self, method: Tuple[str, str, str, str, str, str]) -> str:
        """Return the code for one python method."""

        (name, module, path, method, params, docstring) = method
        (
            base_path,
            flow_by_scope,
            name,
            operation_id_scopes,
        ) = await self.get_one_base_paths_and_flows()

        ignore_long = "  # noqa: E501"  # flake8 compatible linters should not warn about long lines

        # Fix how the docstring expresses optional parameters then end up in **kwargs
        # catalog all parameters listed in the docstring
        docstring_params = set()
        for line in docstring.split("\n"):
            if ":param" in line:
                for word in line.split(" "):
                    if word.endswith(":"):
                        docstring_params.add(word.replace(":", ""))
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
        method_type = "paged" if (":param str offset" in docstring) else "single"

        # identify if this is a user_access_token routine
        operation_id = method.lower().replace("_", "")
        scopes = operation_id_scopes[operation_id]
        if not scopes:
            # Assume application keys
            flows = {"clientCredentials"}
        else:
            flows = {flow_by_scope[scope] for scope in scopes}
        if len(flows) != 1:
            if operation_id in ("getitemconditionpolicies",) or module in (
                "subscription_api",
            ):
                # This usually uses the client credentials method
                flows = {"clientCredentials"}
            else:
                message = "Could not identify authorization method!"
                logging.warning(message)
                logging.warning("method: ", method)
                logging.warning("scopes: ", scopes)
                logging.warning("flows: ", flows)
                raise ValueError(message)
        (auth_method,) = flows  # note tuple unpacking of set
        user_access_token = auth_method == "authorizationCode"

        # identify and prep for parameter possibilities
        stars_kwargs = "**kwargs"
        params_modified = params.split(", ")
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
                params_modified = ", ".join(params_modified)
            else:
                has_args = False

        # Prepare the list of rate lookup information that will be used for throttling.
        resource_name_base = name.replace("_", ".")
        resource_name_module = module.replace("_api", "")
        rate = [resource_name_base, resource_name_module]

        code = f"    def {name}_{method}(self, {params}):{ignore_long}\n"
        code += docstring
        code += (
            f"        return self._method_{method_type}("
            f"{name}.Configuration,"
            f" '{base_path}',"
            f" {name}.{await self._camel(module)},"
            f" {name}.ApiClient,"
            f" '{method}',"
            f" {await self._camel(name)}Exception,"
            f" {user_access_token},"
            f" {rate},"
        )
        if has_args:
            if "," in params_modified:
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
        code += "\n"

        return code

    async def remove_duplicates(self, names) -> None:
        """Deduplicate identical .py files found in all APIs.
        for example when comments are ignored the rest.py files appear identical."""

        # build a catalog that includes a hashed file signature
        catalog = []
        for name in names:
            catalog.extend(
                await self._remove_duplicates_recursive_catalog(
                    name, os.path.join(Locations.target_path, name)
                )
            )

        # count how many times each signature appears
        signature_tally = {}
        for name, file, path, signature in catalog:
            if signature in signature_tally:
                signature_tally[signature] = +1
            else:
                signature_tally[signature] = 1

        # make a sub catalog that just includes signature repeaters
        catalog_repeaters = []
        for values in catalog:
            (name, file, path, signature) = values
            if signature_tally[signature] > 1:
                catalog_repeaters.append(values)

        # TODO apply the DRY principle to the repeaters

    async def _remove_duplicates_recursive_catalog(self, name: str, path: str) -> list:
        """This does the recursive part of cataloging for remove_duplicates."""

        catalog = []
        for _root, dirs, files in os.walk(path):
            for file in files:
                if file != "__init__.py" and file.endswith(".py"):
                    target_file = os.path.join(path, file)
                    with open(target_file) as file_handle:
                        code_text = file_handle.read()
                        # TODO Remove whitespace and comments from the Python code before hashing.
                        m = hashlib.sha256()
                        m.update(code_text.encode())
                        catalog.append((name, file, target_file, m.digest()))

            for directory in dirs:
                catalog.extend(
                    await self._remove_duplicates_recursive_catalog(
                        name, os.path.join(path, directory)
                    )
                )

            return catalog

    @staticmethod
    async def _camel(name: str) -> str:
        """Convert a name with underscore separators to upper camel case."""
        camel = ""
        for part in name.split("_"):
            camel += part.capitalize()
        return camel


class Insert:
    async def do(self, requirements, includes, methods):
        await self.insert_requirements(requirements)
        await self.insert_includes(includes)
        await self.insert_methods(methods)

    @staticmethod
    async def insert_requirements(requirements):
        """Merge the required libraries into the master."""
        requirements = list(requirements)
        requirements.sort()
        # include these with the other requirements for our package
        insert_lines = ""
        for requirement in requirements:
            insert_lines += f"    {requirement}\n"
        # TODO Finish this and don't repeat things that are required for other reasons.
        # self._put_anchored_lines(target_file=self.file_setup, anchor='setup.cfg', insert_lines=insert_lines)

    async def insert_includes(self, includes):
        """Insert the includes for all libraries."""
        insert_lines = "\n".join(includes) + "\n"
        await self._put_anchored_lines(
            target_file=Locations.file_ebay_rest,
            anchor="er_imports",
            insert_lines=insert_lines,
        )

    async def insert_methods(self, methods: str) -> None:
        """Make all the python methods and insert them where needed."""

        methods = "\n" + methods
        await self._put_anchored_lines(
            target_file=Locations.file_ebay_rest,
            anchor="er_methods",
            insert_lines=methods,
        )

    @staticmethod
    async def _put_anchored_lines(
        target_file: str, anchor: str, insert_lines: str
    ) -> None:
        """In the file replace what is between anchors with new lines of code."""

        if os.path.isfile(target_file):
            new_lines = ""
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
                with open(target_file, "w") as file:
                    file.write(new_lines)

            else:
                logging.error(
                    f"Can't find proper start or end anchors for {anchor} in {target_file}."
                )
        else:
            logging.error(f"Can't find {target_file}")


async def process_contract_link(contract_link):
    logging.info(f"Process overview link {contract_link}.")
    c = Contracts(contract_link)
    await c.process()
    name = c.name
    requirement_task = asyncio.create_task(c.get_requirements())
    include_task = asyncio.create_task(c.get_includes())
    method_task = asyncio.create_task(c.get_methods())
    requirement = await requirement_task
    include = await include_task
    method = await method_task
    return include, method, name, requirement


async def generate_apis():
    """
    Generate the contents of the api folder in src/ebay_rest and some code in a_p_i.py.

    For a complete directory of eBay's APIs visit https://developer.ebay.com/docs. Ignore the "Traditional" APIs.

    For an introduction to OpenAPI and how to use eBay's REST-ful APIs
    visit https://developer.ebay.com/api-docs/static/openapi-swagger-codegen.html.
    :return:
    """
    await asyncio.gather(ensure_cache(), Contracts.purge_existing())

    limit = 100  # lower to expedite debugging with a reduced data set
    records = list()
    tasks = list()
    contract_links = await Contracts.get_contract_links()
    contract_links_deduplicated = await Contracts.deduplicate_contract_links(
        contract_links
    )
    for contract_link in contract_links_deduplicated[:limit]:
        task = asyncio.create_task(process_contract_link(contract_link))
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
        if include == "":
            logging.error(f"There are no includes for {name}.")
        elif method == "":
            logging.error(f"There are no methods for {name}.")
        elif requirement == "":
            logging.error(f"There are no requirements for {name}.")
        else:
            names.append(name)
            requirements.update(requirement)
            includes.extend(include)
            methods += method
        await Insert().do(requirements, includes, methods)
    # p.remove_duplicates(names)     # TODO uncomment the method call when work on it resumes


async def main() -> None:
    start = time.time()

    # while debugging, it is handy to change the log level from WARNING to INFO or DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(filename)s %(lineno)d %(funcName)s: %(message)s",  # noqa:
        level=logging.INFO,
    )

    await asyncio.gather(generate_apis(), generate_references())
    logging.info(f"Run time was {int(time.time() - start)} seconds.")
    return


if __name__ == "__main__":
    asyncio.run(main())  # Python 3.7+
