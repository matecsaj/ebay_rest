# ebay-rest
A Python 3 pip package that conveniently wraps eBay’s REST APIs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ebay-rest.

```bash
pip install ebay-rest
```

## Usage

```python
import ebay-rest

er = ebay-rest()
er.pluralize('word') # returns 'words'
er.pluralize('goose') # returns 'geese'
er.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)