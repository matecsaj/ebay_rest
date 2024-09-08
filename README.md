# ebay_rest
A Python 3 pip package that wraps eBay’s REST APIs.

## BASIC Installation
Start with the basic installation of the package. It is easier to install, saves storage and is often enough.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ebay_rest.  Substitute pip3 for pip if your computer also has Python 2 installed.
```bash
pip install ebay_rest
```

## COMPLETE Installation
The complete installation has an extra ability; it can use browser automation to get what eBay calls a user token.

When installing the library, utilize the 'extra' we named complete.
```bash
pip install ebay_rest[complete]
```
And, then with [Playwright](https://playwright.dev/python/) install [Chromium](https://www.chromium.org/Home/).
```bash
playwright install chromium
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
        print(f'Error {error.number} is {error.reason} {error.detail}.\n')
    else:
        pass

print("\nClass documentation:")
print(help(API))    # Over a hundred methods are available!
print(help(DateTime))
print(help(Error))
print(help(Reference))
```

## FAQ - Frequently Asked Questions

**Question:** How are API results organized?

**Answer:**  
* Elemental information is stored in dates, integers, strings and other basic [built-in types](https://docs.python.org/3/library/stdtypes.html).
* [Dictionaries](https://docs.python.org/3/library/stdtypes.html#dict) contain related elements.
* [Lists](https://docs.python.org/3/library/stdtypes.html#list) contain information organized repetitively; expect zero or more contents.
* Dicts and Lists may be nested.
* eBay classifies data as optional or mandatory. Optional elements, dicts or lists are omitted. Manditories have a [None](https://docs.python.org/3/library/constants.html?highlight=none#None) value.

##
**Q:** How are paged calls/results handled? In other words, what happens with the result contains zero or more records? 

**A:** A [Python generator](https://www.python.org/dev/peps/pep-0255/#specification-yield) is implemented; a [Python list](https://docs.python.org/3/tutorial/datastructures.html#) is not returned.
* To be clear, "Paging" is eBay's term for repeating a call while advancing a record offset to get all records.
* eBay documentation has the word "Page" in the return type of paging calls. 
* Do NOT supply a record "offset" parameter when making a paging call.
* The "limit" parameter is repurposed to control how many records from the entire set you want.
* To get all possible records, don't supply a limit.
* eBay imposes a hard limit on some calls, typically 10,000 records. Use filters to help keep below the limit. Use try-except to handle going over.
* Avoid exhausting memory by making the call within a ["for" loop](https://docs.python.org/3/reference/compound_stmts.html#for).

##
**Q:** What should I do when the browser automation opens pops a window open on my computer? 

**A:** Watch and be ready to act.
* At the beginning, you may see a captcha; you need to complete it within 30-seconds.
* Near the end, you may see a 2FA (two-factor authentication) prompt; you need to complete it within 30-seconds.
* Otherwise, be patient, give the whole thing up to 2-minutes to complete, the pop-up will close automatically.

##
**Q:** Can the browser automation be stopped? 

**A1:** Quoting a user of this library, "I use ebay_rest for a web server application and don't use [browser automation] to get refresh tokens. I use JS to push people to the right eBay web page when they click an 'authorize' button; they then fill in their login on the eBay site and I pick up the consent token on our 'live' server (the one specified on the eBay token details). The live server then builds a redirect which goes to the machine that actually requested the token originally (all this happens in the browser, including the original eBay redirect, so it all works fine with localhost addresses)."

**A2:** Reusing the result of the browser pop-up is possible. After running your program, check your terminal/console or [info level logger](https://docs.python.org/3.7/library/logging.html) to see your “production_refresh_token” and “refresh_token_expiry”.

When the following are blank, browser automation is used to get refresh tokens.
```
    "refresh_token": "",
    "refresh_token_expiry": ""
```

Instead, do something like this, with, of course, your token info.
```
    "refresh_token": "production_refresh_token",
    "refresh_token_expiry": "production_token_expiry"
```

Use of an ebay_rest.json file is optional; the Class initializer accepts relevant keyword parameters.
```
        :param application (str or dict, optional) :
        Supply the name of the desired application record in ebay_rest.json or a dict with application credentials.

        Can omit when ebay_rest.json contains only one application record.
        :param user (str or dict, optional) :
        Supply the name of the desired user record in ebay_rest.json or a dict with user credentials.
        Can omit when ebay_rest.json contains only one user record.

        :param header (str or dict, optional) :
        Supply the name of the desired header record in ebay_rest.json or a dict with header credentials.
        Can omit when ebay_rest.json contains only one header record.

        :param key_pair (str or dict, optional) :
        Supply the name of the desired key_pair record in ebay_rest.json or a dict with key_pair credentials.
        Can omit when ebay_rest.json contains only one key_pair record. This section is fully optional.
```

Sample code.
```python
from ebay_rest import API, Error

application = {
    "app_id": "placeholder-placeholder-PRD-placeholder-placeholder",
    "cert_id": "PRD-placeholder-placeholder-placeholder-placeholder-placeholder",
    "dev_id": "placeholder-placeholder-placeholder-placeholder-placeholder",
    "redirect_uri": "placeholder-placeholder-placeholder-placeholder"
}

user = {
    "email_or_username": "<production-username>",
    "password": "<production-user-password>",
    "scopes": [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.marketing",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
    ],
    "refresh_token": "production-refresh_token",
    "refresh_token_expiry": "production-token_expiry"
}

header = {
    "accept_language": "en-US",
    "affiliate_campaign_id": "",
    "affiliate_reference_id": "",
    "content_language": "en-CA",
    "country": "CA",
    "currency": "CAD",
    "device_id": "",
    "marketplace_id": "EBAY_ENCA",
    "zip": ""
}

key_pair = {
    "private_key": "placeholder-placeholder-placeholder-placeholder-placeholder-plac",
    "signing_key_id": "placeholder-placeholder-placeholder-"
}

try:
    api = API(application=application, user=user, header=header)
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
        print(f'Error {error.number} is {error.reason} {error.detail}.\n')
    else:
        pass

```
When using eBay's sandbox:
1. Omit "scopes."
2. Your credentials will contain 'SBX' instead of 'PRD.'

Output.
```
The five least expensive iPhone things now for sale on eBay:
item id: v1|110551100598|410108380484 https://www.sandbox.ebay.com/itm/Retro-Magnetic-Wallet-Leather-Case-For-Apple-iPhone-13-Pro-Max-12-11-XR-8-Cover-/110551100598?hash=item19bd5becb6:g:aXsAAOSwaiFiyAV9
item id: v1|110551164737|410108400925 https://www.sandbox.ebay.com/itm/For-iPhone-6-6-7-8-Plus-LCD-Display-Touch-Screen-Replacement-Home-Button-Camera-/110551164737?hash=item19bd5ce741:g:6hcAAOSwE3Ni45Qu
item id: v1|110551164738|410108400957 https://www.sandbox.ebay.com/itm/For-iPhone-6-6-7-8-Plus-LCD-Display-Touch-Screen-Replacement-Home-Button-Camera-/110551164738?hash=item19bd5ce742:g:4BcAAOSwG8Ni45Ra
item id: v1|110551164739|410108400989 https://www.sandbox.ebay.com/itm/For-iPhone-6-6-7-8-Plus-LCD-Display-Touch-Screen-Replacement-Home-Button-Camera-/110551164739?hash=item19bd5ce743:g:4CEAAOSwG8Ni45SQ
```

Note that the “production_refresh_token” and “refresh_token_expiry” are dumped to the log file. 

That happens in this file https://github.com/matecsaj/ebay_rest/blob/main/src/ebay_rest/token.py, where the following line is located.
message = f'Edit to your ebay_rest.json file to avoid the browser pop-up.\n'

If your project uses log-level info or higher, the info will appear in your log. Alternately, put a breakpoint after the line of code, and cut-paste the values.

##
**Q:** How do I use ebay_rest with [eBay Digital Signatures](https://developer.ebay.com/develop/guides/digital-signatures-for-apis)?

**A:** In the words of eBay, "Due to regulatory requirements applicable to our EU/UK sellers, for certain APIs, developers need to add digital signatures to the respective HTTP call." These calls are (currently) all calls in the Finances API, issueRefund in the Fulfillment API, and some calls in 'traditional' APIs not handled by ebay_rest.

To use Digital Signatures, pass the parameter `digital_signatures` set to `True` at the initialization of the API instance The optional parameter `key_pair` should also be set, as for application, user and header, to either the name of a `key_pairs` section (in the ebay_rest.json file) or a dict. An example using a dict parameter:
```
# application, user and header set as in previous examples

key_pair = {
    "private_key": "placeholder-placeholder-placeholder-placeholder-placeholder-plac",
    "signing_key_id": "placeholder-placeholder-placeholder-"
}

api = API(application=application, user=user, header=header, key_pair=key_pair, digital_signatures=True)
```
Digital signatures apply to _all_ calls made using this API instance _except_ calls to the Developer Key Management API. This API creates and obtains the public/private key pairs used to apply digital signatures. Keep your private key secure.
The complete set of options in the key_pair parameter or for an entry in the key_pairs section in ebay_rest is:
```
{
    'creation_time': '2023-01-01T00:00:00.000Z',
    'expiration_time': '2026-01-01T00:00:00.000Z',
    'jwe': 'placeholder-placeholder-placeholder',
    'private_key': 'placeholder-placeholder-placeholder-placeholder-placeholder-plac',
    'public_key': 'placeholder-placeholder-placeholder-placeholder-placeholder-',
    'signing_key_cipher': 'ED25519',
    'signing_key_id': 'placeholder-placeholder-placeholder-'
}
```
If at least the 'private_key', 'jwe' and 'expiration_time' values are supplied, and the key is in date according to the supplied expiration_time, it will be used. However, only the private key value and signing_key_id are required to use an existing key; a getSigningKey call will be made from the KeyManagement API to load the remaining details and check the expiration date. Note that only the ED25519 cipher is supported by ebay_rest.

**WARNING** There is no way to delete key pairs from an eBay account, and creating a large number of key pairs is probably not a good idea. The new `key_pair` can be extracted from the API instance, as described in the next question.

##
**Q:** How do I get an eBay Digital Signatures public/private key pair?

**A:** A new public/private key pair can be obtained using the `get_digital_signature_key` method on an `API` instance, e.g.
```
key = API.get_digital_signature_key(create_new=True)
```
The API must have been initialized with `digital_signatures=True`. If there is a current valid key pair (either from ebay_rest.json or from a key_pair parameter), the key pair will be returned, otherwise an error will be raised. If (and only if) required, a new key pair will be created when the `create_new` parameter is set to `True`. For `create_new=False`, an error will be raised if no valid key pair has been supplied to ebay_rest.

The retrieved key should then be kept somewhere secure and reused for subsequent calls. It is *not* possible to recover a lost private key as eBay does not store the private key after key generation. Keeping the private_key and the signing_key_id is sufficient to recover the key and only these fields need to be added to ebay_rest.json or the key_pair parameter.

##
**Q:** Why is eBay giving an "Internal Error" or "Internal Server Error"? 

**A:** Rapidly repeating an API call with the same parameter values can trigger this.
##
**Q:** Parallelism, is it safe to do [threading](https://docs.python.org/3/library/threading.html) or [multiprocessing](https://docs.python.org/3/library/multiprocessing.html)?

**A:** Yes, for threading. Multiprocessing is unknown, [help wanted](https://github.com/matecsaj/ebay_rest/issues/20).
##
**Q:** How to optimize API calls?

**A:** Prioritized, do the first things first.
1. Cache results to avoid repeating calls with identical parameter values.
2. Some calls have filtering options; omit unneeded data.
3. When the call returns a list, make the call in a ["for" loop](https://docs.python.org/3/reference/compound_stmts.html#for). 
4. Use [threading](https://docs.python.org/3/library/threading.html) to make calls in parallel but don't exhaust RAM.
5. Use multiprocessing. -- Multiprocessing support is a [goal](https://github.com/matecsaj/ebay_rest/issues/20). -- A safe workaround is to concurrently run copies of your program and divide the work among each.
6. Reuse the API object.
7. Switch to a faster internet connection. 
8. Switch to computer with faster cores.

##
**Q:** How to get data from a response header?

**A:** It is not currently possible; it is an [open issue](https://github.com/matecsaj/ebay_rest/issues/38).
Workarounds:
1. In some cases, another call can get the information; a demonstration is in the [unit tests](https://github.com/matecsaj/ebay_rest/blob/main/tests/ebay_rest.py), search for test_sell_feed_create_inventory_task and task_id_new.
2. You could fork this library, and hack the call you need, so that it returns that needed data.
3. You could write code from scratch to make the RestFul call.
##
**Q:** How to upload a file?

**A:** It is not currently possible; it is an [open issue](https://github.com/matecsaj/ebay_rest/issues/60).
Workarounds:
1. In some cases, another call can be made for each record instead of doing a bulk upload.
2. You could fork this library, and hack the call you need, to force-feed it to your file location.
3. You could write code from scratch to make the RestFul call.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your changes. Make sure to follow the coding standards outlined in the CONTRIBUTING.md file.

## Legal
* [MIT](https://github.com/matecsaj/ebay_rest/blob/main/LICENSE) licence.
* "Python" is a trademark of the [Python Software Foundation](https://www.python.org/psf/).
* "eBay" is a trademark of [eBay Inc](https://www.ebay.com).
* Official endorsement by [eBay Inc](https://www.ebay.com) is not claimed or implied.
* The origin of the oath code is [eBay Oauth Python Client](https://github.com/eBay/ebay-oauth-python-client).
