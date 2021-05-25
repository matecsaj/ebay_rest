# ebay_rest
A tread-safe Python 3 pip package that conveniently wraps eBay’s REST APIs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ebay_rest.

```bash
pip install ebay_rest    # Use pip3 if your computer happens to also have Python 2 installed.
```

## Setup

Follow the instructions [here](https://github.com/matecsaj/ebay_rest/blob/main/tests/ebay_rest_EXAMPLE.json). 

## Usage

```python
from ebay_rest import API, DateTime, Error, Reference

print(f"eBay's official date and time is {DateTime.to_string(DateTime.now())}.\n")

print("All valid eBay global id values, also known as site ids.")
print(Reference.get_global_id_values(), '\n')

try:
    api = API(sandbox=False)
except Error as error:
    print(f'Error {error.number} is {error.reason}  {error.detail}.\n')
else:
    try:
        print("The five least expensive iPhone things now for sale on-eBay:")
        for item in api.buy_browse_search(q='iPhone', sort='price', limit=5):
            print(f"item id: {item['item_id']} {item['item_web_url']}")
    except Error as error:
        print(f'Error {error.number} is {error.reason} {error.detail}.\n')
    else:
        pass

print("\nClass documentation:")
print(help(API))    # Over a hundred methods are available!
print(help(DateTime))
print(help(Error))
print(help(Reference))
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

**A:** Prioritized, do the first things first.
1. Reuse the API object.
1. Some calls have filtering options; omit unneeded data.
1. When the call returns a list, make the call in a ["for" loop](https://docs.python.org/3/reference/compound_stmts.html#for). 
1. Use [threading](https://docs.python.org/3/library/threading.html) to make calls in parallel but don't exhaust RAM.
1. Use multiprocessing. -- Multiprocessing support is a future goal. -- A safe workaround is to concurrently run copies of your program and divide the work among each.
1. Switch to a faster internet connection. 
1. Switch to computer with faster cores.
##
**Q:** How are paged calls/results handled? 

**A:** A [simple generator](https://www.python.org/dev/peps/pep-0255/#specification-yield) is implemented.
* To be clear, "Paging" is eBay's term for repeating a call while advancing a record offset to get all records.
* eBay documentation has the word "Page" in the return type of paging calls. 
* Do NOT supply a record "offset" parameter when making a paging call.
* The "limit" parameter is repurposed to control how many records from the entire set you want.
* To get all possible records, don't supply a limit.
* eBay imposes a hard limit on some calls, typically 10,000 records. Use filters to try and keep below the limit. Use try-except to handle going over.
* Avoid exhausting memory by making the call within a ["for" loop](https://docs.python.org/3/reference/compound_stmts.html#for).

## Contributing
* Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
* Error handling. Make a debug [logs](https://docs.python.org/3/library/logging.html?highlight=logging#module-logging) for maintainers. Throw exceptions for end-user errors.
* Follow Uncle Bob's SOLID principles; see a [text description](https://en.wikipedia.org/wiki/SOLID) & [video tutorial](https://www.youtube.com/watch?v=pTB30aXS77U).
* Note the error number guide documented in the Error class definition. 
* Please make sure to update tests as appropriate.

## Legal
* [MIT](https://github.com/matecsaj/ebay_rest/blob/main/LICENSE) licence.
* "Python" is a trademark of the [Python Software Foundation](https://www.python.org/psf/).
* "eBay" is a trademark of [eBay Inc](https://www.ebay.com).
* Official endorsement by [eBay Inc](https://www.ebay.com) is not claimed or implied.
* The oath code was derived from this [eBay Oauth Python Client](https://github.com/eBay/ebay-oauth-python-client).