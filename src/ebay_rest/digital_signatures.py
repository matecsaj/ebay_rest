import base64
import hashlib
import time
import urllib.parse


def signed_request(pool_manager, key_pair, method, url, *_args, **kwargs):
    """If x-ebay-enforce_signature has been set, add digital signature.
    This function replaces the normal pool_manager.request function,
    and calls it with the same arguments after adding a digital
    signature (if requested).
    """
    headers = kwargs.pop('headers')
    if 'x-ebay-enforce-signature' not in headers:
        return pool_manager.request(method, url, headers=headers, **kwargs)

    headers['x-ebay-signature-key'] = key_pair['jwe']
    created_time = int(time.time())

    # If we have a body, we need to add a Content-Digest field
    if 'body' in kwargs:
        content = kwargs['body']
        h = hashlib.sha256(content).digest()
        content_digest = f'sha-256=:{base64.b64encode(h)}:'
        headers['Content-Digest'] = content_digest
        signature_fields = {'content-digest': content_digest}
    else:
        signature_fields = {}

    # Build the signature fields from the URL and headers
    url_parts = urllib.parse.urlparse(url)
    signature_fields.update({
        'x-ebay-signature-key': key_pair['jwe'],
        '@method': method,
        '@path': url_parts.path,
        '@authority': url_parts.netloc
    })

    # TODO Query not currently required?
    # if url_parts.query:
    #     signature_fields['query'] = f'?{url_parts.query}'

    # Create Signature-Input header showing what components are included
    covered_components = ' '.join(f'"{key}"' for key in signature_fields)
    signature_input = f'({covered_components});created={created_time}'
    headers['Signature-Input'] = f'sig1={signature_input}'

    # Create signature base to be signed
    signature_parameters = [
        f'"{key}": {value}' for key, value in signature_fields.items()
    ]
    signature_parameters.append(f'"@signature-params": {signature_input}')
    signature_base = '\n'.join(signature_parameters)

    # Create signature by signing signature base with private key
    signature = base64.b64encode(
        key_pair['private_key'].sign(signature_base.encode('utf-8'))
    ).decode('ascii')

    # Create Signature header from signature
    headers['Signature'] = f'sig1=:{signature}:'

    return pool_manager.request(method, url, headers=headers, **kwargs)
