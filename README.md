# ebay_rest
A tread-safe Python 3 pip package that conveniently wraps eBay’s REST APIs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ebay_rest.

```bash
pip install ebay_rest
```

## Usage

```python
from ebay_rest import EbayRest, EbayRestError

try:
    er = EbayRest('Hello, World!')
except EbayRestError as error:
    print(f'Error {error.number} is {error.message}.')
else:
    er.print()
```

## Contributing
* Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
* Follow Uncle Bob's SOLID principles; see a [text description](https://en.wikipedia.org/wiki/SOLID) & [video tutorial](https://www.youtube.com/watch?v=pTB30aXS77U).
* Please make sure to update tests as appropriate.

## Legal
* [MIT](https://github.com/matecsaj/ebay_rest/blob/main/LICENSE) licence.
* "Python" is a trademark of the [Python Software Foundation](https://www.python.org/psf/).
* "eBay" is a trademark of [eBay Inc](https://www.ebay.com).
* Official endorsement by [eBay Inc](https://www.ebay.com) is not claimed or implied.
* The oath code was derived from this [eBay Oauth Python Client](https://github.com/eBay/ebay-oauth-python-client).