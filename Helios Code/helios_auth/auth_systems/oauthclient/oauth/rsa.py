#!/usr/bin/python

"""
requires tlslite - http://trevp.net/tlslite/

"""

import binascii

from gdata.tlslite.utils import keyfactory
from gdata.tlslite.utils import cryptomath

# XXX andy: ugly local import due to module name, oauth.oauth
import gdata.oauth as oauth

class OAuthSignatureMethod_RSA_SHA1(oauth.OAuthSignatureMethod):
  def get_name(self):
    return "RSA-SHA1"

  def _fetch_public_cert(self, oauth_request):
    # not implemented yet, ideas are:
    # (1) do a lookup in a table of trusted certs keyed off of consumer
    # (2) fetch via http using a url provided by the requester
    # (3) some sort of specific discovery code based on request
    #
    # either way should return a string representation of the certificate
    raise NotImplementedError

  def _fetch_private_cert(self, oauth_request):
    # not implemented yet, ideas are:
    # (1) do a lookup in a table of trusted certs keyed off of consumer
    #
    # either way should return a string representation of the certificate
    raise NotImplementedError

  def build_signature_base_string(self, oauth_request, consumer, token):
      sig = (
          oauth.escape(oauth_request.get_normalized_http_method()),
          oauth.escape(oauth_request.get_normalized_http_url()),
          oauth.escape(oauth_request.get_normalized_parameters()),
      )
      key = ''
      raw = '&'.join(sig)
      return key, raw

  def build_signature(self, oauth_request, consumer, token):
    key, base_string = self.build_signature_base_string(oauth_request,
                                                        consumer,
                                                        token)

    # Fetch the private key cert based on the request
    cert = self._fetch_private_cert(oauth_request)

    # Pull the private key from the certificate
    privatekey = keyfactory.parsePrivateKey(cert)
    
    # Convert base_string to bytes
    #base_string_bytes = cryptomath.createByteArraySequence(base_string)
    
    # Sign using the key
    signed = privatekey.hashAndSign(base_string)
  
    return binascii.b2a_base64(signed)[:-1]
  
  def check_signature(self, oauth_request, consumer, token, signature):
    decoded_sig = base64.b64decode(signature);

    key, base_string = self.build_signature_base_string(oauth_request,
                                                        consumer,
                                                        token)

    # Fetch the public key cert based on the request
    cert = self._fetch_public_cert(oauth_request)

    # Pull the public key from the certificate
    publickey = keyfactory.parsePEMKey(cert, public=True)

    # Check the signature
    ok = publickey.hashAndVerify(decoded_sig, base_string)

    return ok


class TestOAuthSignatureMethod_RSA_SHA1(OAuthSignatureMethod_RSA_SHA1):
  def _fetch_public_cert(self, oauth_request):
    cert = """
-----BEGIN CERTIFICATE-----
MIIBpjCCAQ+gAwIBAgIBATANBgkqhkiG9w0BAQUFADAZMRcwFQYDVQQDDA5UZXN0
IFByaW5jaXBhbDAeFw03MDAxMDEwODAwMDBaFw0zODEyMzEwODAwMDBaMBkxFzAV
BgNVBAMMDlRlc3QgUHJpbmNpcGFsMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQC0YjCwIfYoprq/FQO6lb3asXrxLlJFuCvtinTF5p0GxvQGu5O3gYytUvtC2JlY
zypSRjVxwxrsuRcP3e641SdASwfrmzyvIgP08N4S0IFzEURkV1wp/IpH7kH41Etb
mUmrXSwfNZsnQRE5SYSOhh+LcK2wyQkdgcMv11l4KoBkcwIDAQABMA0GCSqGSIb3
DQEBBQUAA4GBAGZLPEuJ5SiJ2ryq+CmEGOXfvlTtEL2nuGtr9PewxkgnOjZpUy+d
4TvuXJbNQc8f4AMWL/tO9w0Fk80rWKp9ea8/df4qMq5qlFWlx6yOLQxumNOmECKb
WpkUQDIDJEoFUzKMVuJf4KO/FJ345+BNLGgbJ6WujreoM1X/gYfdnJ/J
-----END CERTIFICATE-----
"""
    return cert

  def _fetch_private_cert(self, oauth_request):
    cert = """
-----BEGIN PRIVATE KEY-----

-----END PRIVATE KEY-----
"""
    return cert
