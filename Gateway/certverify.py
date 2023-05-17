
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

# Load the device certificate
with open('device_cert.pem', 'r') as f:
    cert = f.read()
    c = cert.split('\n')
    devcert = bytes('\n'.join(c[1:len(c)-1]),'utf-8')
    device_cert = x509.load_pem_x509_certificate(devcert, default_backend())

# Load the CA certificate
with open('ca_cert.pem', 'r') as f:
    cert = f.read()
    c = cert.split('\n')
    cacert = bytes('\n'.join(c[1:len(c)-1]),'utf-8')
    ca_cert = x509.load_pem_x509_certificate(cacert, default_backend())

# Verify that the device certificate is signed by the CA
public_key = ca_cert.public_key()
try:
    public_key.verify(
        device_cert.signature,
        device_cert.tbs_certificate_bytes,
        padding.PKCS1v15(),
        SHA256()
    )
    print('Device certificate is valid')
except Exception as e:
    print('Device certificate is invalid:', str(e))