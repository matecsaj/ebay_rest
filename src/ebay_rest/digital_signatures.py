import hashlib
import base64


def signed_request(pool_manager, key_pair, method, url, *args, **kwargs):
    """If x-ebay-enforce_signature has been set, add digital signature.
    This function replaces the normal pool_manager.request function,
    and calls it with the same arguments after adding a digital
    signature (if requested).
    """
    print('sign_request')
    headers = kwargs.pop('headers', {})
    if 'x-ebay-enforce-signature' not in headers:
        return pool_manager.request(method, url, headers=headers, **kwargs)

    headers['x-ebay-signature-key'] = key_pair.jwe

    if body in kwargs:
        content = kwargs['body']
        h = hashlib.sha256(content).digest()
        headers['Content-Digest'] = f'sha-256=:{base64.b64encode(h)}:'

    return pool_manager.request(method, url, headers=headers, **kwargs)
