import requests
from cryptography import x509
import paramiko
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

def getX509(devicename,host, path):
    #print(devicename,host, path)
    if host == 'localhost' or host == '127.0.0.1':
        DEVICE_CERT = path +"/"+devicename+"_cert.pem"
        DEVICE_KEY = path +"/"+devicename+"_key.pem"
        
        device_cert_pem = ''
        device_key_pem = ''
        with open(DEVICE_CERT, "r") as f:
            device_cert_pem = f.read()
        with open(DEVICE_KEY, "r") as f:
            device_key_pem = f.read()
            
        #print(device_cert_pem)
        #print(device_key_pem)

        return device_cert_pem
        
    else:
        
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

        return device_cert_pem
