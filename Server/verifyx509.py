import requests
from cryptography import x509
import paramiko
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

def verifyX509(devicename,host, path):
    #print(devicename,host, path)
    if host == 'localhost' or host == '127.0.0.1':
        resp1 = requests.get('http://127.0.0.1:8200/v1/pki/ca/pem')
        #print(resp1)
        ca_cert_pem = resp1.text
        #print(ca_cert_pem)
        DEVICE_CERT = path +"/"+devicename+"_cert.pem"
        DEVICE_KEY = path +"/"+devicename+"_key.pem"
        #print(DEVICE_CERT,DEVICE_KEY)
        device_cert_pem = ''
        device_key_pem = ''
        with open(DEVICE_CERT, "r") as f:
            device_cert_pem = f.read()
        with open(DEVICE_KEY, "r") as f:
            device_key_pem = f.read()
            
        #print(device_cert_pem)
        #print(device_key_pem)

        cacert = bytes(ca_cert_pem,'utf-8')
        ca_cert = x509.load_pem_x509_certificate(cacert, default_backend())
        print(ca_cert)
        
        devcert = bytes(device_cert_pem,'utf-8')
        device_cert = x509.load_pem_x509_certificate(devcert, default_backend())
        print(device_cert)

        res = certverify(device_cert,ca_cert)
        
        print(res)

        return res
        
    else:
        resp1 = requests.get('http://127.0.0.1:8200/v1/pki/ca/pem')
        ca_cert_pem = resp1.text
        DEVICE_CERT = devicename+"_cert.pem"
        DEVICE_KEY = devicename+"_key.pem"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname= host)
        
        # set up SFTP connection
        sftp = ssh.open_sftp()
        
        # copy file
        local_file_path = DEVICE_CERT 
        remote_file_path = path +"/"+devicename+"_cert.pem"
        sftp.put( remote_file_path, local_file_path)
        
        # close connections
        sftp.close()
        ssh.close()

        device_cert_pem = ''
        device_key_pem = ''
        with open(DEVICE_CERT, "r") as f:
            f.read(device_cert_pem)
        with open(DEVICE_KEY, "r") as f:
            f.read(device_key_pem)

        cacert = bytes(ca_cert_pem,'utf-8')
        ca_cert = x509.load_pem_x509_certificate(cacert, default_backend())
        print(ca_cert)
        
        devcert = bytes(device_cert_pem,'utf-8')
        device_cert = x509.load_pem_x509_certificate(devcert, default_backend())
        print(device_cert)

        res = certverify(device_cert,ca_cert)
        
        print(res)

        return res

def certverify(device_cert,ca_cert):
    public_key = ca_cert.public_key()
    try:
        public_key.verify(
            device_cert.signature,
            device_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            SHA256()
            )
        return True
    except Exception as e:
        return False
