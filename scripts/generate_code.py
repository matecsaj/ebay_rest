#!/usr/bin/python3
# Run this script from the command-line to get info from https://developer.ebay.com and generate code in the src folder.

# Wait a day if this script intermittently fails to load pages from eBay's website.
# Perhaps making inhumanly frequent requests triggers eBay's DOS protection system.

# Standard library imports
from dataclasses import dataclass
import hashlib
from itertools import groupby
import json
import logging
import os
import re
import shutil
import sys
import time
from typing import AsyncGenerator, Dict, Iterable, List, Optional, Set, Union

# Third party imports
import aiofiles
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from chardet import detect
from urllib.parse import urljoin, urlsplit


# Local imports

# Globals

# Data Classes


@dataclass
class BasePathsAndFlows:
    base_path: str
    flow_by_scope: dict
    name: str
    operation_id_scopes: dict


@dataclass
class CatalogItem:
    file: str
    name: str
    path: str
    signature: bytes


@dataclass
class ContractData:
    contract_url: str
    category: Optional[str] = None
    call: Optional[str] = None
    url: Optional[str] = None
    file_name: Optional[str] = None
    name: Optional[str] = None
    version: Optional[int] = None
    beta: Optional[bool] = None


@dataclass
class ContractInfo:
    category: str
    call: str
    url: str
    file_name: str
    version: int
    beta: bool


@dataclass
class CountryCode:
    code: str
    description: str


@dataclass
class CurrencyCode:
    code: str
    description: str


@dataclass
class GlobalIdValue:
    ebay_site_id: str
    global_id: str
    language: str
    site_name: str
    territory: str


@dataclass
class HeaderParameter:
    description: str
    name: str
    required: bool
    type: str


@dataclass
class LocaleDetail:
    site_url: str
    comment: str


@dataclass
class MarketplaceIdValue:
    country: str
    locale_details: dict
    marketplace_id: str


@dataclass
class MethodInfo:
    docstring: str
    method: str
    module: str
    name: str
    params: str
    path: str

    def __lt__(self, other):
        """
        Compare MethodInfo objects for sorting.
        """
        if self.module != other.module:
            return self.module < other.module
        return self.method < other.method

    def __eq__(self, other):
        """
        Check if two MethodInfo objects are equal.
        """
        return self.module == other.module and self.method == other.method


@dataclass
class ModuleInfo:
    module: str
    name: str
    path: str


@dataclass
class ProcessResult:
    include: List[str]
    method: str
    name: str
    requirement: Set[str]


@dataclass
class SecurityInfo:
    flow_type: str
    operation_id: str
    security_scopes: Optional[List[str]]
    user_access_token: bool


@dataclass
class SwapInfo:
    original: str
    replacement: str


@dataclass
class TypoRemedy:
    typo: str
    remedy: str


@dataclass
class UrlPair:
    text: str
    url: str


# Standard Classes


class WebScraper:
    """
    Class for web scraping operations.
    """

    @staticmethod
    async def get_table_via_url(url: str) -> list:
        data = []
        soup = await WebScraper.get_soup_via_url(url)
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

    @staticmethod
    async def generate_url_text_and_urls(
        urls: Iterable[str],
    ) -> AsyncGenerator[UrlPair, None]:
        """
        Asynchronously fetch and parse anchor tags from a sequence of URLs.

        :param urls: Iterable of URLs to process.
        :return: An asynchronous generator that yields UrlPair objects containing text and URL.
        """

        async def process_url(url: str) -> AsyncGenerator[UrlPair, None]:
            soup = await WebScraper.get_soup_via_url(url)
            for url_link in soup.find_all("a"):
                yield UrlPair(
                    text=url_link.text, url=urljoin(url, url_link.get("href"))
                )

        async def gather_urls(url: str) -> List[UrlPair]:
            return [url_item async for url_item in process_url(url)]

        tasks = [gather_urls(url) for url in urls]
        for task in asyncio.as_completed(tasks):
            completed_task = await task
            for url_pair in completed_task:
                yield url_pair

    @staticmethod
    async def get_soup_via_url(url: str) -> BeautifulSoup:
        # Get the HTML from a URL and then make soup of it.

        # the header is meant to prevent the exception 'Response payload is not completed'
        headers = {"Connection": "keep-alive"}

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # this will raise an exception for 4xx and 5xx status
                    html_content = await response.text()
                    # Parse the HTML content
                    return BeautifulSoup(html_content, "html.parser")
        except aiohttp.ClientConnectorError as e:
            logging.fatal(
                "The server dropped the connection on the TCP level; it may think we are a "
                f"denial-of-service attacker; try again tomorrow. {url}: {e}"
            )
            sys.exit()
        except Exception as e:
            logging.error(
                f"An error occurred while trying to get content from {url}: {e}"
            )
            return BeautifulSoup(
                "", "html.parser"
            )  # return an empty soup object instead of None

    @staticmethod
    async def get_ebay_list_url(code_type: str) -> str:
        """
        Make a URL to an ebay "code type" list

        Here is the complete list of possible code types.
        https://developer.ebay.com/devzone/xml/docs/Reference/eBay/enumindex.html#EnumerationIndex

        If eBay modifies the URL, you need to determine the new pattern;
        at https://developer.ebay.com/ search for 'countrycodetype' and study the result.

        example: https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/countrycodetype.html
        """
        if not code_type:
            raise ValueError("code_type can't be None or empty")
        else:
            return f"https://developer.ebay.com/devzone/xml/docs/reference/ebay/types/{code_type}.html"


class Reference:
    """
    Class for operations involving a single reference type.
    """

    @staticmethod
    async def make_json_file(source: Union[Dict, List], name: str) -> None:
        """
        Save data to a JSON file, stored in the 'references' directory.

        :param source: The data to save
        :param name: The name of the file without extension
        """
        if len(source) > 0:
            path = "../src/ebay_rest/references/"
            async with aiofiles.open(path + name + ".json", mode="w") as outfile:
                await outfile.write(json.dumps(source, sort_keys=True, indent=4))
        else:
            logging.error(f"The json file for {name} should not be empty; not created.")

    @staticmethod
    async def generate_country_codes() -> None:
        """
        Generate a reference file for eBay's Country Codes.
        """
        logging.info("Find the eBay's Country Codes.")

        # load the target webpage
        data = await WebScraper.get_table_via_url(
            await WebScraper.get_ebay_list_url("CountryCodeType")
        )

        # ignore the header, convert to a list of CountryCode objects and delete bad values
        country_codes = []
        bad_values = ("CustomCode", "QM", "QN", "QO", "TP", "UM", "YU", "ZZ")

        for datum in data[1:]:
            code = datum[0]
            if code not in bad_values:
                country_code = CountryCode(code=code, description=datum[1])
                # Convert to dict for JSON serialization
                country_codes_dict = {country_code.code: country_code.description}
                country_codes.append(country_codes_dict)
            else:
                logging.debug(f"Bad value {code} skipped.")

        # Convert a list of dicts to a single dict for backward compatibility
        country_codes_dict = {}
        for country_code_dict in country_codes:
            country_codes_dict.update(country_code_dict)

        await Reference.make_json_file(country_codes_dict, "country_codes")

    @staticmethod
    async def generate_currency_codes() -> None:
        """
        Generate a reference file for eBay's Currency Codes.
        """
        logging.info("Find the eBay's Currency Codes.")

        # load the target webpage
        data = await WebScraper.get_table_via_url(
            await WebScraper.get_ebay_list_url("CurrencyCodeType")
        )

        # ignore the header, convert to a list of CurrencyCode objects and delete bad values
        currency_codes = []
        bad_values = ("CustomCode",)

        for datum in data[1:]:
            code = datum[0]
            description = datum[1]
            if code not in bad_values and "replaced" not in description:
                currency_code = CurrencyCode(code=code, description=description)
                # Convert to dict for JSON serialization
                currency_codes_dict = {currency_code.code: currency_code.description}
                currency_codes.append(currency_codes_dict)
            else:
                logging.debug(f"Bad value {code} skipped.")

        # Convert a list of dicts to a single dict for backward compatibility
        currency_codes_dict = {}
        for currency_code_dict in currency_codes:
            currency_codes_dict.update(currency_code_dict)

        await Reference.make_json_file(currency_codes_dict, "currency_codes")

    @staticmethod
    async def generate_global_id_values() -> None:
        """
        Generate a reference file for eBay's Global ID Values.
        """
        logging.info("Find the eBay's Global ID Values.")

        # load the target webpage
        url = "https://developer.ebay.com/Devzone/merchandising/docs/CallRef/Enums/GlobalIdList.html"
        data = await WebScraper.get_table_via_url(url)

        # convert to a list of GlobalIdValue objects
        global_id_values = []
        for datum in data[1:]:
            global_id_value = GlobalIdValue(
                global_id=datum[0],
                language=datum[1],
                territory=datum[2],
                site_name=datum[3],
                ebay_site_id=datum[4],
            )
            # Convert to dict for JSON serialization
            global_id_dict = {
                "global_id": global_id_value.global_id,
                "language": global_id_value.language,
                "territory": global_id_value.territory,
                "site_name": global_id_value.site_name,
                "ebay_site_id": global_id_value.ebay_site_id,
            }
            global_id_values.append(global_id_dict)

        await Reference.make_json_file(global_id_values, "global_id_values")

    @staticmethod
    async def generate_marketplace_id_values() -> None:
        """
        Generate a reference file for eBay's Marketplace ID Values.
        """
        logging.info("Find the eBay's Marketplace ID Values.")

        marketplace_id_dict = dict()

        # load the target webpage
        url = "https://developer.ebay.com/api-docs/static/rest-request-components.html#marketpl"
        soup = await WebScraper.get_soup_via_url(url)

        if soup:
            # find the rows regarding Response Fields.
            tables = soup.find_all("table")
            if len(tables) > 1:
                table = tables[1]  # the second table is index 1
                rows = table.find_all("tr")

                # put the rows into a table of data
                data = []
                for row in rows:
                    cols = row.find_all("td")
                    cols = [ele.text.strip() for ele in cols]
                    data.append([ele for ele in cols if ele])  # Get rid of empty values

                # The header got messed up and is unlikely to change, so hardcode it
                # cols = ['marketplace_id', 'country', 'marketplace_site', 'locale_support']

                # convert to a nested dict using dataclasses

                for datum in data[1:]:
                    [marketplace_id, country, marketplace_site, locale_support] = datum
                    locale_support = locale_support.replace(" ", "")
                    locales = locale_support.split(
                        ","
                    )  # convert comma-separated locales to a list of strings
                    sites = re.findall(
                        r"https?://(?:[a-zA-Z0-9]|[._~:@!$&'()*+,;=%]|/)+",
                        marketplace_site,
                    )
                    comments = re.findall("\\(([^)]*)\\)", marketplace_site)
                    comment_shortage = len(locales) - len(comments)
                    for _ in range(comment_shortage):
                        comments.append("")

                    # Create LocaleDetail objects and store them in a dictionary
                    locale_details_dict = dict()
                    for index, locale in enumerate(locales):
                        locale_detail = LocaleDetail(
                            site_url=sites[index], comment=comments[index]
                        )
                        # Convert to a list for backward compatibility with existing code
                        locale_details_dict[locale] = [
                            locale_detail.site_url,
                            locale_detail.comment,
                        ]

                    # Create a MarketplaceIdValue object
                    marketplace_value = MarketplaceIdValue(
                        marketplace_id=marketplace_id,
                        country=country,
                        locale_details=locale_details_dict,
                    )

                    # Store in a dictionary for backward compatibility
                    marketplace_id_dict[marketplace_value.marketplace_id] = [
                        marketplace_value.country,
                        marketplace_value.locale_details,
                    ]

        await Reference.make_json_file(marketplace_id_dict, "marketplace_id_values")


class References:
    """
    Class for operations involving multiple reference types.
    """

    @staticmethod
    async def generate_all() -> None:
        """
        Generate all reference JSON files for the 'references' directory found in 'src'.

        If you add, delete, or rename a JSON file, then alter /src/ebay_rest/reference.py accordingly.
        """
        # TODO Clear out any junk that happens to be in the target folder.

        await asyncio.gather(
            Reference.generate_country_codes(),
            Reference.generate_currency_codes(),
            Reference.generate_global_id_values(),
            Reference.generate_marketplace_id_values(),
        )


class Locations:
    """
    Where things are located in the locale file store.
    """

    target_directory: str = "api"
    target_path: str = os.path.abspath("../src/ebay_rest/" + target_directory)
    cache_path: str = os.path.abspath("./" + target_directory + "_cache")
    file_ebay_rest: str = os.path.abspath("../src/ebay_rest/a_p_i.py")

    @staticmethod
    async def ensure_cache():
        # ensure that we have an empty cache
        if os.path.isdir(Locations.cache_path):
            await Contracts.delete_folder_contents(Locations.cache_path)
        else:
            os.mkdir(Locations.cache_path)
        # warn developers that they should not edit the files in the cache
        readme = "# READ ME\n"
        readme += "Don't change the contents of this folder directly; instead, edit and run scripts/generate_code.py"
        file_path = os.path.abspath(os.path.join(Locations.cache_path, "README.md"))
        with open(file_path, "w") as file_handle:
            file_handle.write(readme)


class Contract:
    def __init__(self, contract_url) -> None:
        self.data = ContractData(contract_url=contract_url)

    async def process(self) -> None:
        contract_info = await Contract.get_contract_info(self.data.contract_url)
        self.data.category = contract_info.category
        self.data.call = contract_info.call
        self.data.url = contract_info.url
        self.data.file_name = contract_info.file_name
        self.data.version = contract_info.version
        self.data.beta = contract_info.beta
        self.data.name = await self.get_api_name()
        await self.cache_contract()
        await self.patch_contract()
        await self.swagger_codegen()
        await self.patch_generated()
        await self.copy_library()
        await self.fix_imports()

    @staticmethod
    async def get_contract_info(
        contract_url: str,
    ) -> ContractInfo:
        """
        Async method to parse a contract link and extract key data parts from it.

        This method breaks down the contract link into its constituent parts and retrieves crucial information such
        as the category, call, url, file_name, version, and whether it is a beta contract.

        It does so by splitting the URL and path, conducts string manipulations, and applies regex pattern matching
        to decipher the version of the contract.

        :param contract_url: The contract link that needs to be parsed.

        :return:
            ContractInfo: An object containing 'category', 'call', 'url', 'file_name',
            'version', and 'beta'.
        """
        # split in raw parts
        url_split = urlsplit(contract_url)
        path_split = url_split.path.split("/")

        # if the path has a dedicated version number element, example "v2",
        # then extract the number and remove from the list
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
        url = contract_url
        file_name = path_split[-1]
        beta = True if "_beta_" in contract_url else False

        # extract the version number from the filename; for example, version 2 looks like this "_v2_"
        version_match = re.search(r"_v(\d+)_", file_name)
        filename_version = int(version_match.group(1)) if version_match else 0

        if path_version and path_version != filename_version:
            logging.warning(
                f"Variable path_version {path_version} should equal version {filename_version}."
            )

        return ContractInfo(
            category=category,
            call=call,
            url=url,
            file_name=file_name,
            version=filename_version,
            beta=beta,
        )

    async def cache_contract(self) -> None:
        destination = os.path.join(Locations.cache_path, self.data.file_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.data.url) as response:
                response_body = await response.read()

                # determine encoding
                if response.charset:
                    encoding = response.charset
                    method = "Declared"
                else:
                    detected = detect(response_body)
                    if detected["encoding"] is not None:
                        encoding = detected["encoding"]
                        method = "Detected"
                    else:
                        encoding = "utf-8"
                        method = "Fallback"
                logging.debug(
                    f"{method} encoding: {encoding} for {self.data.file_name}"
                )

        decoded_content = response_body.decode(encoding, errors="replace")

        # normalize to UTF-8 when saving
        async with aiofiles.open(destination, mode="w", encoding="utf-8") as f:
            await f.write(decoded_content)

    async def patch_contract(self) -> None:
        """
        If the contract from eBay has an error, then patch it before generating code.
        """
        # This is no longer needed, ebay fixed the problem, but I'm leaving it here for reference.
        # if self.data.category == 'sell' and self.data.call == 'fulfillment':
        #     await Contracts.patch_contract_sell_fulfillment(self.data.file_name)

    @staticmethod
    async def patch_file_upload_method(api_file_path: str, method_name: str) -> bool:
        """
        Patch a file upload method in an API file to support the 'files' parameter.

        This function adds 'files' to the all_params list, handles file uploads
        by repurposing the existing local_var_files parameter, and updates docstrings.

        Args:
            api_file_path: Path to the API file to patch
            method_name: Name of the method to patch (e.g., 'upload_video', 'create_image_from_file')

        Returns:
            bool: True if the file was patched, False otherwise
        """
        try:
            async with aiofiles.open(api_file_path) as f:
                data = await f.read()
        except FileNotFoundError:
            return False

        # Check if this file contains the method we want to patch
        # We need to patch the _with_http_info method, not the wrapper
        method_with_http_info = f"{method_name}_with_http_info"
        if f"def {method_with_http_info}" not in data:
            return False

        file_was_modified = False

        # Patch 1: Add 'files' to the all_params list within the _with_http_info method
        # Find the method definition and patch the all_params within its scope
        # Use a more specific pattern that finds all_params after the method definition
        method_pattern = rf"def {method_with_http_info}\(.*?\):.*?(?=def |\Z)"
        method_match = re.search(method_pattern, data, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            # Find all_params within this method
            pattern = r"all_params = \[([^\]]*)\]  # noqa: E501"
            match = re.search(pattern, method_body)
            if match:
                existing_params = match.group(1)
                # Check if 'files' is already in the params or if a patch comment already exists
                all_params_line = match.group(0)
                patch_comment = "ebay_rest patch: multipart/form-data file uploads"
                if (
                    "'files'" not in existing_params
                    and '"files"' not in existing_params
                    and patch_comment not in all_params_line
                ):
                    new_params = (
                        existing_params + ", 'files'"
                        if existing_params.strip()
                        else "'files'"
                    )
                    new_pattern = f"all_params = [{new_params}]  # noqa: E501 - ebay_rest patch: multipart/form-data file uploads"
                    # Replace it in the method body
                    method_body = re.sub(pattern, new_pattern, method_body, count=1)
                    # Replace the method in the full data
                    data = (
                        data[: method_match.start()]
                        + method_body
                        + data[method_match.end() :]
                    )
                    file_was_modified = True

        # Patch 2: Handle files parameter in local_var_files (repurposes existing file handling)
        # Find the method again after the first patch
        method_match = re.search(method_pattern, data, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            target = "local_var_files = {}"
            # Check if a patch already exists to avoid duplicates
            patch_marker = "# ebay_rest patch: multipart/form-data file uploads"
            if target in method_body and patch_marker not in method_body:
                new_code = """local_var_files = {}
        # ebay_rest patch: multipart/form-data file uploads
        if 'files' in params and params['files']:
            local_var_files = params['files']"""
                # Only replace the first occurrence within this method
                method_body = method_body.replace(target, new_code, 1)
                # Replace the method in the full data
                data = (
                    data[: method_match.start()]
                    + method_body
                    + data[method_match.end() :]
                )
                file_was_modified = True

        # Patch 3: Add 'files' parameter documentation to docstrings
        # Patch docs for both the public method (for user docs) and the _with_http_info method (for consistency)
        for method_to_patch in [method_name, method_with_http_info]:
            method_def_pattern = rf"def {method_to_patch}\(.*?\):.*?(?=def |\Z)"
            method_match = re.search(method_def_pattern, data, re.DOTALL)
            if method_match:
                method_body = method_match.group(0)
                # Check if files parameter already documented in the docstring
                if re.search(
                    r":param\s+(dict\s+)?files.*?ebay_rest patch: multipart/form-data file uploads",
                    method_body,
                    re.DOTALL,
                ):
                    continue
                # Look for content_type parameter in docstring
                content_type_pattern = r"(:param str content_type:.*?multipart/form-data.*?\(required\))(\n)"
                match = re.search(content_type_pattern, method_body, re.DOTALL)
                if match:
                    content_type_line = match.group(1)
                    newline = match.group(2)
                    # Add files parameter documentation after content_type
                    files_doc = (
                        "\n        :param dict files: Dictionary mapping form field names to file paths. "
                        "For example: {'image': 'path/to/image.jpg'} or {'file': 'path/to/document.pdf'}. "
                        "This parameter is used to upload files in multipart/form-data requests. (optional)  # ebay_rest patch: multipart/form-data file uploads"
                    )
                    new_content_type_line = content_type_line + files_doc + newline
                    method_body = method_body.replace(
                        content_type_line + newline, new_content_type_line, 1
                    )
                    data = (
                        data[: method_match.start()]
                        + method_body
                        + data[method_match.end() :]
                    )
                    file_was_modified = True

        # Write the patched file if it was modified
        if file_was_modified:
            async with aiofiles.open(api_file_path, mode="w") as f:
                await f.write(data)
            logger = logging.getLogger(__name__)
            logger.info(
                "Patched file upload support for %s in %s", method_name, api_file_path
            )

        return file_was_modified

    @staticmethod
    async def patch_octet_stream_upload_method(
        api_file_path: str, method_name: str
    ) -> bool:
        """
        Patch a file upload method in an API file to support the 'files' parameter for application/octet-stream.

        This function adds 'files' to the all_params list, reads the file from the 'files' dict,
        and converts it to body_params for application/octet-stream uploads.

        :param api_file_path: Path to the API file to patch
        :param method_name: The name of the method to patch (e.g., 'upload_video')
        :return: True if the file was patched, False otherwise
        """
        try:
            async with aiofiles.open(api_file_path) as f:
                data = await f.read()
        except FileNotFoundError:
            return False

        # Check if this file contains the method we want to patch
        # We need to patch the _with_http_info method, not the wrapper
        method_with_http_info = f"{method_name}_with_http_info"
        if f"def {method_with_http_info}" not in data:
            return False

        file_was_modified = False

        # Patch 1: Add 'files' to the all_params list within the _with_http_info method
        method_pattern = rf"def {method_with_http_info}\(.*?\):.*?(?=def |\Z)"
        method_match = re.search(method_pattern, data, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            # Find all_params within this method
            pattern = r"all_params = \[([^\]]*)\]  # noqa: E501"
            match = re.search(pattern, method_body)
            if match:
                existing_params = match.group(1)
                # Check if 'files' is already in the params or if a patch comment already exists
                all_params_line = match.group(0)
                patch_comment = "ebay_rest patch: application/octet-stream file uploads"
                if (
                    "'files'" not in existing_params
                    and '"files"' not in existing_params
                    and patch_comment not in all_params_line
                ):
                    new_params = (
                        existing_params + ", 'files'"
                        if existing_params.strip()
                        else "'files'"
                    )
                    new_pattern = f"all_params = [{new_params}]  # noqa: E501 - ebay_rest patch: application/octet-stream file uploads"
                    # Replace it in the method body
                    method_body = re.sub(pattern, new_pattern, method_body, count=1)
                    # Replace the method in the full data
                    data = (
                        data[: method_match.start()]
                        + method_body
                        + data[method_match.end() :]
                    )
                    file_was_modified = True

        # Patch 2: Add 'import os' after the last import if not already present
        if "import os" not in data:
            # Find all import lines
            import_lines = re.findall(r"^import .+|^from .+", data, re.MULTILINE)
            if import_lines:
                # Get the last import line
                last_import = import_lines[-1]
                # Add os import after the last import
                data = data.replace(
                    last_import,
                    last_import
                    + "\nimport os  # noqa: F401  # ebay_rest patch: application/octet-stream file uploads",
                    1,
                )
                file_was_modified = True

        # Patch 3: Handle files parameter by reading file and converting to body_params
        # Find the method again after the first patch
        method_match = re.search(method_pattern, data, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            # Find where body_params is set
            target = "body_params = None\n        if 'body' in params:\n            body_params = params['body']"
            # Check if a patch already exists to avoid duplicates
            patch_marker = "# ebay_rest patch: application/octet-stream file uploads"
            if target in method_body and patch_marker not in method_body:
                new_code = """body_params = None
        # ebay_rest patch: application/octet-stream file uploads
        files = params.get('files')
        if files:
            # Read file from files dict and convert to body
            file_path = next(iter(files.values()))
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    body_params = f.read()
        body = params.get('body')
        if body:
            body_params = body"""
                # Only replace the first occurrence within this method
                method_body = method_body.replace(target, new_code, 1)
                # Replace the method in the full data
                data = (
                    data[: method_match.start()]
                    + method_body
                    + data[method_match.end() :]
                )
                file_was_modified = True

        # Patch 4: Add 'files' parameter documentation to docstrings
        # Patch docs for both the public method (for user docs) and the _with_http_info method (for consistency)
        for method_to_patch in [method_name, method_with_http_info]:
            method_def_pattern = rf"def {method_to_patch}\(.*?\):.*?(?=def |\Z)"
            method_match = re.search(method_def_pattern, data, re.DOTALL)
            if method_match:
                method_body = method_match.group(0)
                # Check if files parameter already documented in the docstring
                if re.search(
                    r":param\s+(dict\s+)?files.*?ebay_rest patch: application/octet-stream file uploads",
                    method_body,
                    re.DOTALL,
                ):
                    continue
                # Look for content_type parameter in docstring with application/octet-stream
                content_type_pattern = r"(:param str content_type:.*?application/octet-stream.*?\(required\))(\n)"
                match = re.search(content_type_pattern, method_body, re.DOTALL)
                if match:
                    content_type_line = match.group(1)
                    newline = match.group(2)
                    # Add files parameter documentation after content_type
                    files_doc = (
                        "\n        :param dict files: Dictionary mapping field names to file paths. "
                        "For example: {'file': 'path/to/video.mp4'}. "
                        "The file will be read and sent as the request body for application/octet-stream uploads. (optional)  # ebay_rest patch: application/octet-stream file uploads"
                    )
                    new_content_type_line = content_type_line + files_doc + newline
                    method_body = method_body.replace(
                        content_type_line + newline, new_content_type_line, 1
                    )
                    data = (
                        data[: method_match.start()]
                        + method_body
                        + data[method_match.end() :]
                    )
                    file_was_modified = True

        # Write the patched file if it was modified
        if file_was_modified:
            async with aiofiles.open(api_file_path, mode="w") as f:
                await f.write(data)
            logger = logging.getLogger(__name__)
            logger.info(
                "Patched application/octet-stream file upload support for %s in %s",
                method_name,
                api_file_path,
            )

        return file_was_modified

    @staticmethod
    async def patch_wrapper_methods_preserve_return_http_data_only(
        api_file_path: str,
    ) -> bool:
        """
        Patch wrapper methods to only set _return_http_data_only=True if not already in kwargs.
        This allows users to pass _return_http_data_only=False to get headers.

        :param api_file_path: Path to the API file to patch
        :return: True if the file was patched, False otherwise
        """
        try:
            async with aiofiles.open(api_file_path) as f:
                data = await f.read()
        except FileNotFoundError:
            return False

        file_was_modified = False

        # Find all wrapper methods (methods that call _with_http_info)
        pattern = "kwargs['_return_http_data_only'] = True"
        new_code = "if '_return_http_data_only' not in kwargs:  # ebay_rest patch\n            kwargs['_return_http_data_only'] = True"

        # Check if a patch already exists to avoid duplicates
        if pattern in data and new_code not in data:
            data = data.replace(pattern, new_code)
            file_was_modified = True

        if file_was_modified:
            async with aiofiles.open(api_file_path, mode="w") as f:
                await f.write(data)
            logger = logging.getLogger(__name__)
            logger.info(
                "Patched wrapper methods to preserve _return_http_data_only in %s",
                api_file_path,
            )

        return file_was_modified

    async def patch_generated(self) -> None:
        """
        If the generated code has an error, then patch it before making use of it.
        """

        # API calls that have a return type fail when there is no content. This is because
        # there is an attempt to deserialize an empty string. If there is no content indicated
        # by a 204 status, then don't deserialize.
        bad_code = "if response_type:"
        file_path = os.path.join(
            Locations.cache_path, self.data.name, self.data.name, "api_client.py"
        )
        try:
            async with aiofiles.open(file_path, mode="r") as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_path}.")
        else:
            if bad_code not in data:
                logging.error(
                    f"Maybe for {file_path} the 204 patch is not needed any longer."
                )
            else:
                # add a new condition before the colon
                data = data.replace(
                    bad_code,
                    bad_code[:-1]
                    + " and response_data.status != 204:       # ebay_rest patch",
                )
                async with aiofiles.open(file_path, mode="w") as f:
                    await f.write(data)

        # Patch in code for Digital Signatures
        file_path = os.path.join(
            Locations.cache_path, self.data.name, self.data.name, "rest.py"
        )
        try:
            async with aiofiles.open(file_path, mode="r") as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_path}.")
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
            # Patch to handle a bytes-body for application/octet-stream
            # Add support for a bytes-body before the else clause that raises exception
            # Find the else clause after the isinstance(body, str) block and insert before it
            target = """                else:
                    # Cannot generate the request from given parameters"""
            new_part = """                # ebay_rest patch: Handle bytes body for application/octet-stream
                elif isinstance(body, bytes):
                    r = signed_request(self.pool_manager, self.key_pair,  # ebay_rest patch
                        method, url,
                        body=body,
                        preload_content=_preload_content,
                        timeout=timeout,
                        headers=headers)
                else:
                    # Cannot generate the request from given parameters"""
            if target in data and new_part not in data:
                data = data.replace(target, new_part, 1)
            async with aiofiles.open(file_path, mode="w") as f:
                await f.write(data)

        # Patch file upload methods to support files parameter
        # This fixes the issue where local_var_files = {} and 'files' parameter is not accepted
        # Repurposes existing parameters to pass file information
        # Auto-detect methods by finding those with content_type parameter mentioning multipart/form-data
        api_files = []
        for root, _dirs, files in os.walk(
            os.path.join(Locations.cache_path, self.data.name)
        ):
            api_files.extend(
                os.path.join(root, file) for file in files if file.endswith("_api.py")
            )

        # Find all methods that need patching by scanning for content_type with multipart/form-data
        methods_to_patch_multipart = set()
        # Find all methods that need patching for application/octet-stream
        methods_to_patch_octet_stream = set()
        for api_file in api_files:
            try:
                async with aiofiles.open(api_file) as f:
                    file_content = await f.read()
                method_pattern = r"def (\w+)\([^)]*\):(.*?)(?=def |\Z)"
                all_methods = re.finditer(method_pattern, file_content, re.DOTALL)
                for method_match in all_methods:
                    method_name = method_match.group(1)
                    method_body = method_match.group(2)

                    # Check if this method has content_type with multipart/form-data in its docstring
                    if re.search(
                        r":param str content_type:.*?multipart/form-data",
                        method_body,
                        re.DOTALL,
                    ):
                        if (
                            not method_name.endswith("_with_http_info")
                            and not method_name.startswith("__")
                            and method_name not in ["__init__", "__new__", "__del__"]
                        ):
                            methods_to_patch_multipart.add(method_name)

                    # Check if this method has content_type with application/octet-stream in its docstring
                    if re.search(
                        r":param str content_type:.*?application/octet-stream",
                        method_body,
                        re.DOTALL,
                    ):
                        if (
                            not method_name.endswith("_with_http_info")
                            and not method_name.startswith("__")
                            and method_name not in ["__init__", "__new__", "__del__"]
                        ):
                            methods_to_patch_octet_stream.add(method_name)
            except (FileNotFoundError, Exception):
                continue

        # Patch each detected method for multipart/form-data
        for method_name in methods_to_patch_multipart:
            for api_file in api_files:
                await Contract.patch_file_upload_method(api_file, method_name)

        # Patch each detected method for application/octet-stream
        for method_name in methods_to_patch_octet_stream:
            for api_file in api_files:
                await Contract.patch_octet_stream_upload_method(api_file, method_name)

        # This allows users to pass _return_http_data_only=False to get headers
        for api_file in api_files:
            await Contract.patch_wrapper_methods_preserve_return_http_data_only(
                api_file
            )

    @staticmethod
    async def run_command(cmd: str) -> None:
        """
        Run a command line in a subprocess.
        """
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

    async def swagger_codegen(self) -> None:
        source = os.path.join(Locations.cache_path, self.data.file_name)
        destination = f"{Locations.cache_path}/{self.data.name}"

        # The generator will warn if there is no .swagger-codegen-ignore file
        if not os.path.isdir(destination):
            os.mkdir(destination)
        file_path = os.path.abspath(
            os.path.join(Locations.cache_path, ".swagger-codegen-ignore")
        )
        with open(file_path, "w") as file_handle:
            file_handle.write("")

        command = f" generate -l python -o {destination} -DpackageName={self.data.name} -i {source}"
        if sys.platform == "darwin":  # OS X or MacOS
            command = "swagger-codegen" + command
        elif sys.platform == "linux":  # Linux
            command = "java -jar swagger-codegen-cli.jar" + command
        else:
            assert False, f"Please extend main() for your {sys.platform} platform."
        await self.run_command(command)

    async def get_api_name(self) -> str:
        name = f"{self.data.category}_{self.data.call}"
        return name

    async def get_one_base_paths_and_flows(self) -> BasePathsAndFlows:
        """
        Process a UTF-8 JSON contract and extract three things for later use.
                1) the base_path for each category_call (e.g., buy_browse)
                2) the security flow for each scope in each category_call
                3) the scopes for each call in each category_call
        """
        source = os.path.join(Locations.cache_path, self.data.file_name)
        try:
            async with aiofiles.open(source, mode="r", encoding="utf-8") as f:
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
                logging.fatal(message)
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
                # Get the base path
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
                name = self.data.category + "_" + self.data.call
        return BasePathsAndFlows(
            base_path=base_path,
            flow_by_scope=flow_by_scope,
            name=name,
            operation_id_scopes=operation_id_scopes,
        )

    async def copy_library(self) -> None:
        """
        Copy the essential parts of the generated eBay library to within the src folder.
        """
        source_path = os.path.join(Locations.cache_path, self.data.name, self.data.name)
        destination_path = os.path.join(Locations.target_path, self.data.name)
        _destination = shutil.copytree(source_path, destination_path)

    async def fix_imports(self) -> None:
        """
        The deeper the directory, the more dots are needed to make the correct relative path.
        """
        await self._fix_imports_recursive(
            self.data.name, "..", os.path.join(Locations.target_path, self.data.name)
        )

    async def _fix_imports_recursive(self, name: str, dots: str, path: str) -> None:
        """
        This does the recursive part of fix_imports.
        """

        for _root, dirs, files in os.walk(path):
            swaps = [  # order is crucial, put more specific swaps before less
                SwapInfo(
                    original=f"import {name}.models",
                    replacement=f"from {dots}{name} import models",
                ),
                SwapInfo(
                    original=f"from models", replacement=f"from {dots}{name}.models"
                ),
                SwapInfo(original=f"import {name}", replacement=f"import {dots}{name}"),
                SwapInfo(original=f"from {name}", replacement=f"from {dots}{name}"),
                SwapInfo(original=f"{name}.models", replacement=f"models"),
            ]
            for file in files:
                target_file = os.path.join(path, file)
                new_lines = ""
                with open(target_file) as file_handle:
                    for old_line in file_handle:
                        for swap_info in swaps:
                            if swap_info.original in old_line:
                                old_line = old_line.replace(
                                    swap_info.original, swap_info.replacement
                                )
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
        """
        Get the library's requirements.
        """

        # compile the set of all unique requirements from the generated library
        start_tag = "REQUIRES = ["
        end_tag = "]\n"
        requirements = set()
        source_path = os.path.join(Locations.cache_path, self.data.name, "setup.py")
        try:
            with open(source_path) as file:
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
                f"The requirements for library {self.data.name} are unknown because a file is missing {source_path}."
            )

        return requirements

    async def get_includes(self) -> List[str]:
        """
        Get the includes for a library.
        """
        includes = list()
        includes.append(f"from .{Locations.target_directory} import {self.data.name}")
        line = (
            f"from .{Locations.target_directory}.{self.data.name}.rest import ApiException as "
            f"{await self._camel(self.data.name)}Exception"
        )
        includes.append(line)
        return includes

    async def get_methods(self) -> str:
        """
        For modules, get all code for its methods.
        """

        # Catalog the module files that contain all method implementations
        modules = []
        path = os.path.join(Locations.cache_path, self.data.name, self.data.name, "api")
        for root, _dirs, files in os.walk(path):
            for file in files:
                if file != "__init__.py":
                    modules.append(
                        ModuleInfo(
                            name=self.data.name,
                            module=file.replace(".py", ""),
                            path=os.path.join(root, file),
                        )
                    )

        # Catalog all methods in all modules
        methods: List[MethodInfo] = []
        method_marker_part = "_with_http_info"
        method_marker_whole = method_marker_part + "(self,"
        docstring_marker = '"""'
        bad_docstring_markers = (
            ">>> ",
            "synchronous",
            "async_req",
            "request thread",
        )

        for module_info in modules:
            step = 0
            with open(module_info.path) as file_handle:
                for line in file_handle:
                    if step == 0:  # Looking for the next method
                        if method_marker_whole in line:
                            if ")" in line:
                                method_and_params, _junk = line.split(")", maxsplit=1)
                                if "(" in method_and_params:
                                    method, params = method_and_params.split(
                                        "(", maxsplit=1
                                    )
                                    method = method.replace("    def ", "").strip()
                                    method = method.replace(
                                        method_marker_part, ""
                                    ).strip()
                                    params = params.replace("self, ", "").strip()
                                    step += 1
                                else:
                                    logging.warning(
                                        f"Expected '(' in method_and_params: {method_and_params}"
                                    )
                            else:
                                logging.warning(f"Expected ')' in line: {line}")

                    elif step == 1:  # Looking for the start of the docstring block
                        if docstring_marker in line:
                            docstring = line
                            step += 1

                    elif step == 2:  # Looking for the end of the docstring block
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
                                MethodInfo(
                                    name=module_info.name,
                                    module=module_info.module,
                                    path=module_info.path,
                                    method=method,
                                    params=params,
                                    docstring=docstring,
                                )
                            )
                            step = 0

        methods.sort()

        code = str()
        for method in methods:
            code += await self._make_method(method)

        return code

    async def get_process_result(self) -> ProcessResult:
        """
        Get a ProcessResult object containing the processed contract data.

        :return: ProcessResult: An object containing include, method, name, and requirement.
        """
        await self.process()
        name = self.data.name
        requirement_task = asyncio.create_task(self.get_requirements())
        include_task = asyncio.create_task(self.get_includes())
        method_task = asyncio.create_task(self.get_methods())
        requirement = await requirement_task
        include = await include_task
        method = await method_task
        return ProcessResult(
            include=include, method=method, name=name, requirement=requirement
        )

    @staticmethod
    async def clean_docstring(docstring: str) -> str:
        # strip HTML
        docstring = BeautifulSoup(docstring, features="html.parser").get_text()

        # fix typos
        typo_remedies = [  # pairs of typos found in docstrings and their remedy
            TypoRemedy(
                typo="AustraliaeBay", remedy="Australia eBay"  # noqa:
            ),  # noqa: - suppress flake8 compatible linters, misspelling is intended
            TypoRemedy(typo="cerate", remedy="create"),  # noqa:
            TypoRemedy(typo="distibuted", remedy="distributed"),  # noqa:
            TypoRemedy(typo="FranceeBay", remedy="Francee Bay"),  # noqa:
            TypoRemedy(typo="GermanyeBay", remedy="Germany eBay"),  # noqa:
            TypoRemedy(typo="http:", remedy="https:"),  # noqa:
            TypoRemedy(typo="identfier", remedy="identifier"),  # noqa:
            TypoRemedy(typo="ItalyeBay", remedy="Italy eBay"),  # noqa:
            TypoRemedy(typo="Limt", remedy="Limit"),  # noqa:
            TypoRemedy(typo="lisitng", remedy="listing"),  # noqa:
            TypoRemedy(typo="maketplace", remedy="marketplace"),  # noqa:
            TypoRemedy(typo="markeplace", remedy="marketplace"),  # noqa:
            TypoRemedy(typo="motorcyles", remedy="motorcycles"),  # noqa:
            TypoRemedy(typo="parmeter", remedy="parameter"),  # noqa:
            TypoRemedy(typo="publlish", remedy="publish"),  # noqa:
            TypoRemedy(typo="qroup", remedy="group"),  # noqa:
            TypoRemedy(typo="retrybable", remedy="retryable"),  # noqa:
            TypoRemedy(typo="takeback", remedy="take back"),  # noqa:
            TypoRemedy(typo="Takeback", remedy="Take back"),  # noqa:
            TypoRemedy(typo="theste", remedy="these"),  # noqa:
            TypoRemedy(typo="UKeBay", remedy="UK eBay"),  # noqa:
        ]
        for typo_remedy in typo_remedies:
            docstring = docstring.replace(typo_remedy.typo, typo_remedy.remedy)

        # Replace a single backslash before pipe (if any) with a double backslash
        docstring = docstring.replace(r"\|", r"\\|")

        # telling the linter to suppress long line warnings taints the Sphinx generated docs so filter them out
        docstring = docstring.replace("# noqa: E501", "")

        return docstring

    async def _make_method(self, method_info: MethodInfo) -> str:
        """
        Return the code for one python method.
        """

        module = method_info.module
        method = method_info.method
        params = method_info.params
        docstring = method_info.docstring
        base_paths_and_flows = await self.get_one_base_paths_and_flows()
        base_path = base_paths_and_flows.base_path
        flow_by_scope = base_paths_and_flows.flow_by_scope
        name = base_paths_and_flows.name
        operation_id_scopes = base_paths_and_flows.operation_id_scopes

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
            flows = set()
            for scope in scopes:
                if scope in flow_by_scope:
                    flows.add(flow_by_scope[scope])
                else:
                    logging.warning(
                        f"Scope {scope} not found in flow_by_scope for method {method}."
                    )
                    flows.add(
                        "clientCredentials"
                    )  # work around, assume the most common value
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
        (auth_method,) = flows  # note tuple unpacking of a set
        user_access_token = auth_method == "authorizationCode"

        # Create a SecurityInfo object to encapsulate security-related information
        security_info = SecurityInfo(
            operation_id=operation_id,
            security_scopes=scopes,
            flow_type=auth_method,
            user_access_token=user_access_token,
        )

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

        # Prepare the rate lookup information that will be used for throttling.
        resource_name_base = name.replace("_", ".")
        resource_name_module = module.replace("_api", "")

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
            f" {security_info.user_access_token},"
            f" ['{resource_name_base}', '{resource_name_module}'],"
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

    @staticmethod
    async def _camel(name: str) -> str:
        """
        Convert a name with underscore separators to upper-camel-case.
        """
        camel = ""
        for part in name.split("_"):
            camel += part.capitalize()
        return camel


class Contracts:
    """
    Class for operations involving multiple contracts.
    """

    def __init__(self) -> None:
        self.contracts = []

    async def load_contracts(self, contract_urls: List[str]) -> None:
        """
        Load Contract instances from the provided URLs.

        Args:
            contract_urls (List[str]): List of contract URLs to load.
        """
        for url in contract_urls:
            contract = Contract(url)
            self.contracts.append(contract)

    async def process_all_contracts(self) -> List[ProcessResult]:
        """
        Process all loaded contracts and return the results.

        Returns:
            List[ProcessResult]: List of processing results.
        """
        tasks = []
        for contract in self.contracts:
            task = asyncio.create_task(self._process_contract(contract))
            tasks.append(task)

        results = []
        for task in tasks:
            result = await task
            results.append(result)

        return results

    @staticmethod
    async def _process_contract(contract: Contract) -> ProcessResult:
        """
        Process a single contract and return the result.

        :param contract: The contract to process.
        :return: ProcessResult: The processing result.
        """
        return await contract.get_process_result()

    @staticmethod
    async def get_contract_urls() -> List[str]:
        """
        This asynchronous function is designed to get the contract URLs from eBay's developer site.

        :return: A sorted list of contract URLs.
        """
        logging.info("Get a list of URLs to eBay OpenAPI 3 JSON contracts.")

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

        # use the category urls to find unique URLs to API table pages with visible text containing 'APIs'
        async for url_pair in WebScraper.generate_url_text_and_urls(category_urls):
            if "APIs" in url_pair.text:
                table_urls.add(url_pair.url)

        # use the table urls to find unique URLs to overview pages which have urls ending with overview.html
        async for url_pair in WebScraper.generate_url_text_and_urls(table_urls):
            if url_pair.url.endswith("overview.html"):
                overview_urls.add(url_pair.url)

        # use the overview urls to find unique URLs to contracts which have urls ending with .json
        async for url_pair in WebScraper.generate_url_text_and_urls(overview_urls):
            if url_pair.url.endswith(".json"):
                contract_urls.add(url_pair.url)

        contract_urls_sorted = sorted(list(contract_urls))

        # safety check
        count = len(contract_urls_sorted)
        logging.info(f"Found contract {count} URLs.")
        if not (20 < count < 40):
            logging.warning(f"Having {count} contract URLs is unexpected!")

        return contract_urls_sorted

    @staticmethod
    async def deduplicate_contract_urls(contract_urls: Iterable[str]) -> List[str]:
        """
        Remove redundant contracts, drop Betas, and, lower versions.

        :param contract_urls: An iterable container of contract URLs.
        :return: A list of 'keeper' URLs which are unique based on their category, call, beta, and version.
        :raises AssertionError: If the total number of URLs is not equal to the sum of 'keepers' and 'junkers'.
        """

        keepers = []
        junkers = []

        contract_infos = await asyncio.gather(
            *[Contract.get_contract_info(url) for url in contract_urls]
        )

        sorted_contract_infos = sorted(
            contract_infos,
            key=lambda info: (info.category, info.call, info.beta, -info.version),
        )

        for _, group in groupby(
            sorted_contract_infos, key=lambda info: (info.category, info.call)
        ):
            group_list = list(group)
            if len(group_list) > 1:
                logging.info(f"group_list: {group_list}")
            keepers.append(group_list[0].url)
            junkers.extend([url_info.url for url_info in group_list[1:]])

        if len(contract_infos) != len(keepers) + len(junkers):
            logging.warning(
                "Lengths of URLs, keepers, and junkers do not add up correctly - possible loss of data."
            )

        return keepers

    @staticmethod
    async def process_url(contract_url: str) -> ProcessResult:
        """
        Process a contract URL to extract includes, methods, name, and requirements.

        :param contract_url: The contract URL to process.
        :return: ProcessResult: An object containing include, method, name, and requirement.
        """
        logging.info(f"Process overview URL {contract_url}.")
        c = Contract(contract_url)
        return await c.get_process_result()

    # This is no longer needed, ebay fixed the problem, but I'm leaving it here for reference.
    @staticmethod
    async def patch_contract_sell_fulfillment(file_name: str) -> None:
        # In the Sell Fulfillment API, the model 'Address' is returned with the attribute 'countryCode'.
        # However, the JSON specifies 'country' instead; thus Swagger generates the wrong API.
        file_path = os.path.join(Locations.cache_path, file_name)
        try:
            async with aiofiles.open(file_path, mode="r") as f:
                data = await f.read()
        except FileNotFoundError:
            logging.error(f"Can't open {file_path}.")
        else:
            data = json.loads(data)
            properties = data["components"]["schemas"]["Address"]["properties"]
            if "country" in properties:
                properties["countryCode"] = properties.pop(
                    "country"
                )  # Warning, alphabetical key order spoiled.
                data = json.dumps(data, sort_keys=True, indent=4)
                async with aiofiles.open(file_path, mode="w") as f:
                    await f.write(data)
            else:
                logging.warning(f"Patching {file_name} is no longer needed.")

    @staticmethod
    async def delete_folder_contents(path_to_folder: str) -> None:
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
    async def purge_existing() -> None:
        # purge what might already be there
        for filename in os.listdir(Locations.target_path):
            file_path = os.path.join(Locations.target_path, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)

    async def remove_duplicates(self, names) -> None:
        """
        De-duplicate identical .py files found in all APIs.
        For example, when comments are ignored, the rest.py files appear identical.
        """

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
        for item in catalog:
            if item.signature in signature_tally:
                signature_tally[item.signature] += 1
            else:
                signature_tally[item.signature] = 1

        # make a sub catalog that just includes signature repeaters
        catalog_repeaters = []
        for item in catalog:
            if (
                item.signature in signature_tally
                and signature_tally[item.signature] > 1
            ):
                catalog_repeaters.append(item)

        # TODO apply the DRY principle to the repeaters

    async def _remove_duplicates_recursive_catalog(self, name: str, path: str) -> list:
        """
        This does the recursive part of cataloging for remove_duplicates.
        """
        catalog = []
        for _root, dirs, files in os.walk(path):
            for file in files:
                if file != "__init__.py" and file.endswith(".py"):
                    target_file = os.path.join(path, file)
                    with open(target_file) as file_handle:
                        code_text = file_handle.read()
                        m = hashlib.sha256()
                        m.update(code_text.encode())
                        catalog.append(
                            CatalogItem(
                                name=name,
                                file=file,
                                path=target_file,
                                signature=m.digest(),
                            )
                        )

            for directory in dirs:
                catalog.extend(
                    await self._remove_duplicates_recursive_catalog(
                        name, os.path.join(path, directory)
                    )
                )

        return catalog

    async def generate_all(self) -> None:
        """
        Generate the contents of the api folder in src/ebay_rest and some code in a_p_i.py.

        For a complete directory of eBay's APIs, visit https://developer.ebay.com/docs. Ignore the "Traditional" APIs.

        For an introduction to OpenAPI and how to use eBay's Restful APIs,
        visit https://developer.ebay.com/api-docs/static/openapi-swagger-codegen.html.
        """
        await asyncio.gather(Locations.ensure_cache(), Contracts.purge_existing())

        limit = 100  # lower to expedite debugging with a reduced data set
        contract_urls = await Contracts.get_contract_urls()
        contract_urls_deduplicated = await Contracts.deduplicate_contract_urls(
            contract_urls
        )

        # Load contracts from URLs
        await self.load_contracts(contract_urls_deduplicated[:limit])

        # Process all loaded contracts
        records = await self.process_all_contracts()

        names = list()
        requirements = set()
        includes = list()
        methods = str()
        for record in records:
            if (
                len(record.include) == 0
                or record.method == ""
                or len(record.requirement) == 0
            ):
                if len(record.include) == 0:
                    logging.error(f"{record.name} has no includes.")
                if record.method == "":
                    logging.error(f"{record.name} has no methods.")
                if len(record.requirement):
                    logging.error(f"{record.name} has no requirements.")
            else:
                names.append(record.name)
                requirements.update(record.requirement)
                includes.extend(record.include)
                methods += record.method
        await CodeInjector().do(requirements, includes, methods)
        # await self.remove_duplicates(names)     # TODO uncomment the method call when work on it resumes


class CodeInjector:
    async def do(
        self, requirements: Set[str], includes: List[str], methods: str
    ) -> None:
        await self.insert_requirements(requirements)
        await self.insert_includes(includes)
        await self.insert_methods(methods)

    @staticmethod
    async def insert_requirements(requirements: Set[str]) -> None:
        """
        Merge the required libraries into the master.
        """
        requirements = list(requirements)
        requirements.sort()
        # include these with the other requirements for our package
        insert_lines = ""
        for requirement in requirements:
            insert_lines += f"    {requirement}\n"
        # TODO Finish this and don't repeat things that are required for other reasons.
        # self._put_anchored_lines(target_file=self.file_setup, anchor='setup.cfg', insert_lines=insert_lines)

    async def insert_includes(self, includes):
        """
        Insert the includes for all libraries.
        """
        insert_lines = "\n".join(includes) + "\n"
        await self._put_anchored_lines(
            target_file=Locations.file_ebay_rest,
            anchor="er_imports",
            insert_lines=insert_lines,
        )

    async def insert_methods(self, methods: str) -> None:
        """
        Make all the python methods and insert them where needed.
        """

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
        """
        In the file, replace what is between anchors with new lines of code.
        """

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


async def main() -> None:
    start = time.time()

    # while debugging, it is handy to change the log level from WARNING to INFO or DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(filename)s %(lineno)d %(funcName)s: %(message)s",  # noqa:
        level=logging.INFO,
    )

    contracts = Contracts()
    await asyncio.gather(contracts.generate_all(), References.generate_all())
    logging.info(f"Run time was {int(time.time() - start)} seconds.")
    return


if __name__ == "__main__":

    async def run_main():
        await main()

    # Use asyncio.Runner for better control in Python 3.14
    if sys.version_info >= (3, 11):
        with asyncio.Runner() as runner:
            runner.run(run_main())
    else:
        asyncio.run(main())  # Python 3.7-3.10
