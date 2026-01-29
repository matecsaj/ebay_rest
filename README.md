# ebay_rest
A Python 3 pip package that wraps eBay’s REST APIs.

## Table of Contents
- [Installation](#installation)
  - [Basic Installation](#basic-installation)
  - [Complete Installation](#complete-installation)
- [Setup](#setup)
- [Usage](#usage)
- [FAQ](#faq)
- [Optimization & Performance](#optimization--performance)
- [Contributing](#contributing)
- [Legal](#legal)

---

## Installation

### Basic Installation
The basic installation provides core functionality without browser automation. It is lighter, easier to install, and sufficient for most use cases.

```bash
pip install ebay_rest
```

### Complete Installation
The complete installation includes browser automation for getting eBay user tokens.

```bash
pip install ebay_rest[complete]
```
After installing the package, install Playwright and Chromium:
```bash
playwright install chromium
```
**Note:** Playwright may require additional system dependencies. See [Playwright installation guide](https://playwright.dev/python/docs/intro) for details.

---

## Setup
Follow the setup instructions in the [example configuration file](https://github.com/matecsaj/ebay_rest/blob/main/ebay_rest_EXAMPLE.json).

---

## Usage
Here is a basic example of using `ebay_rest` to retrieve eBay's global site IDs and search for iPhones:

```python
from ebay_rest import API, DateTime, Error, Reference

print(f"eBay's official date and time is {DateTime.to_string(DateTime.now())}.\n")

print("All valid eBay global id values, also known as site ids.")
print(Reference.get_global_id_values(), '\n')

try:
    api = API(application='production_1', user='production_1', header='US')
except Error as error:
    print(f'Error {error.number} is {error.reason}  {error.detail}.\n')
else:
    try:
        print("The five least expensive iPhone things now for sale on-eBay:")        
        for record in api.buy_browse_search(q='iPhone', sort='price', limit=5):
            if 'record' not in record:
                pass    # TODO Refer to non-records, they contain optimization information.
            else:
                item = record['record']
                print(f"item id: {item['item_id']} {item['item_web_url']}")
    except Error as error:
        print(error)    # Another way to print an error.
    else:
        pass

print("\nClass documentation:")
print(help(API))    # Over a hundred methods are available!
print(help(DateTime))
print(help(Error))
print(help(Reference))
```

Look to the [unit tests](https://github.com/matecsaj/ebay_rest/blob/main/tests/test_ebay_rest.py) for more example code.


---

## FAQ

<details>
  <summary><strong>How are API results structured?</strong></summary>
  <ul>
    <li>Basic types: strings, integers, dates.</li>
    <li><code>dict</code> (objects): Groups related elements.</li>
    <li><code>list</code> (arrays): Repetitive structures with one or more elements.</li>
    <li>Optional elements may be omitted, mandatory elements are set to <code>None</code> if empty.</li>
  </ul>
</details>

<details>
  <summary><strong>How are paged API results handled?</strong></summary>
  <ul>
    <li>A Python <a href="https://www.python.org/dev/peps/pep-0255/">generator</a> is used instead of a list.</li>
    <li>Do <strong>not</strong> supply an "offset" parameter.</li>
    <li>"limit" controls how many records to retrieve.</li>
    <li>To retrieve all records, omit "limit." Be aware of eBay's 10,000 record count limit.</li>
  </ul>
</details>

<details>
  <summary><strong>Can the browser automation be avoided?</strong></summary>
  <p>Yes, reuse the refresh token after the first retrieval. Modify your <code>ebay_rest.json</code> file:</p>
  <pre>
"refresh_token": "your_refresh_token",
"refresh_token_expiry": "your_token_expiry"
  </pre>
</details>

<details>
  <summary><strong>Does this library support threading/multiprocessing?</strong></summary>
  <p>Threading is safe. Multiprocessing is untested (<a href="https://github.com/matecsaj/ebay_rest/issues/20">help wanted</a>).</p>
</details>

<details>
  <summary><strong>Why does eBay return "Internal Error"?</strong></summary>
  <p>Making repeated calls with the same parameters in a short time can trigger this error.</p>
</details>

<details>
  <summary><strong>How can I upload a file?</strong></summary>
  <p>See the sample code in the <a href="https://github.com/matecsaj/ebay_rest/blob/main/tests/test_ebay_rest.py">unit tests</a>. Search for usages of <code>get_upload_sample_path_file</code> to find working examples.</p>
</details>

<details>
  <summary><strong>How can I get data from a response header?</strong></summary>
  <p>See the sample code in the <a href="https://github.com/matecsaj/ebay_rest/blob/main/tests/test_ebay_rest.py">unit tests</a>. Search for <code>test_commerce_media_upload_video</code> to find a working example.</p>
</details>

<details>
  <summary><strong>How can I implement eBay’s publish/subscribe workflow?</strong></summary>
  <p>Push delivery is not possible with this library; a workaround is to use the <em>Client Alerts (poll)</em> option seen on a screenshot on <a href="https://developer.ebay.com/develop/guides-v2/marketplace-user-account-deletion/marketplace-user-account-deletion#overview">this page</a>.</p>
</details>

---

## Optimization & Performance
To optimize API calls:
1. **Cache responses** to avoid redundant API calls.
2. **Use filters** to limit response data.
3. **Use generators** instead of lists for paged results.
4. **Utilize threading** (but be mindful of rate limits).
5. **Reuse the API instance** to avoid unnecessary authentication overhead.
6. **Optimize your network** (faster internet connection, lower latency).

---

## Contributing
Contributions are welcome! Please fork this repository and submit a pull request. Follow the coding standards outlined in [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Legal
- Licensed under [MIT](https://github.com/matecsaj/ebay_rest/blob/main/LICENSE).
- "Python" is a trademark of the [Python Software Foundation](https://www.python.org/psf/).
- "eBay" is a trademark of [eBay Inc](https://www.ebay.com).
- This project is **not affiliated with or endorsed by eBay Inc.**

