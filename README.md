# ebay_rest
A tread-safe Python 3 pip package that conveniently wraps eBay’s REST APIs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ebay_rest.

```bash
pip install ebay_rest
```

## Setup

Follow the instructions [here](https://github.com/matecsaj/ebay_rest/blob/main/tests/ebay_rest_EXAMPLE.json). 

## Usage

```python
from ebay_rest import API, DateTime, Error, Reference

try:
    api = API(use_sandbox=True)
except Error as error:
    print(f'Error {error.number} is {error.reason}  {error.detail}.\n')
else:
    try:
        for item in api.buy_browse_get_items():
            print('item id: ' + item['item_id'] + '\n')
    except Error as error:
        print(f'Error {error.number} is {error.reason} {error.detail}.\n')
    else:
        pass

print('An item is composed of the following.\n')
print(Reference.get_item_fields())

print('The official eBay date and time is ', DateTime.now(), '\n')
```

## FAQ | Frequently Asked Questions

**Question:** How are API results organized?

**Answer:**  
* Elemental information is stored in dates, integers, strings and other basic [built-in types](https://docs.python.org/3/library/stdtypes.html).
* [Dictionaries](https://docs.python.org/3/library/stdtypes.html#dict) contain related elements.
* [Lists](https://docs.python.org/3/library/stdtypes.html#list) contain information organized repetitively; expect zero or more contents.
* Dicts and Lists may be nested.
* eBay classifies data as optional or mandatory. Optional elements, dicts or lists are omitted. Manditories have a [None](https://docs.python.org/3/library/constants.html?highlight=none#None) value.
##
**Q:** How to make API calls faster?

**A:**  
* Reuse the API object.
* Some calls have filtering options; omit unneeded data.
* When the call returns a list, make the call in a ["for" loop](https://docs.python.org/3/reference/compound_stmts.html#for). 
* Use [threading](https://docs.python.org/3/library/threading.html) to make calls in parallel but don't exhaust RAM.
##
**Q:** Blah

**A:** Blah
##
**Q:** Blah

**A:** Blah
##
**Q:** Blah

**A:** Blah

## Contributing
* Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
* Error handling. Make a debug [logs](https://docs.python.org/3/library/logging.html?highlight=logging#module-logging) for maintainers. Throw exceptions for end-user errors.
* Follow Uncle Bob's SOLID principles; see a [text description](https://en.wikipedia.org/wiki/SOLID) & [video tutorial](https://www.youtube.com/watch?v=pTB30aXS77U).
* Please make sure to update tests as appropriate.

## Legal
* [MIT](https://github.com/matecsaj/ebay_rest/blob/main/LICENSE) licence.
* "Python" is a trademark of the [Python Software Foundation](https://www.python.org/psf/).
* "eBay" is a trademark of [eBay Inc](https://www.ebay.com).
* Official endorsement by [eBay Inc](https://www.ebay.com) is not claimed or implied.
* The oath code was derived from this [eBay Oauth Python Client](https://github.com/eBay/ebay-oauth-python-client).