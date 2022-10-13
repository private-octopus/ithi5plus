#!/usr/bin/python
# coding=utf-8
#
# testing how to acuqire the certificate information from server name.


import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Server address

serverHost = "privateoctopus.com";

serverPort = "443";

serverAddress = (serverHost, serverPort);

 

# Retrieve the server certificate in PEM format

cert_pem = ssl.get_server_certificate(serverAddress);
# print(cert_pem);
cert_bytes = bytes(cert_pem, 'utf-8')

cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())

issued_to = str(cert.subject)
issued_by = str(cert.issuer)
print("issued_to: " + issued_to)
print("issued_by: " + issued_by)

try:
    san_ext = certificate.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
    san_ext_value = cast(x509.SubjectAlternativeName, san_ext.value)
    subj_alt_names = san_ext_value.get_values_for_type(DNSName)
except ExtensionNotFound:
    print("Extension not found")
    pass
except DuplicateExtension:
    # Fix for https://github.com/nabla-c0d3/sslyze/issues/420
    # Not sure how browsers behave in this case but having a duplicate extension makes the certificate invalid
    # so we just return no SANs (likely to make hostname validation fail, which is fine)
    print("Duplicate")
    pass