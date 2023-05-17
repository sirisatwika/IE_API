from cryptography import x509
from cryptography.hazmat.backends import default_backend
import datetime

# Load the certificate from a .pem file
with open('device_cert.pem', 'r') as f:
    cert = f.read()
    c = cert.split('\n')
    devcert = bytes('\n'.join(c[1:len(c)-1]),'utf-8')
    device_cert = x509.load_pem_x509_certificate(devcert, default_backend())

# Get the notAfter attribute from the certificate
not_after = device_cert.not_valid_after
print(not_after)

# Calculate the time remaining until the certificate expires
remaining_time = not_after - datetime.datetime.now(not_after.tzinfo)

print(remaining_time)

# Print the remaining time in days and seconds
print(f"Time remaining: {remaining_time.days} days, {remaining_time.seconds} seconds")

