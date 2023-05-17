import requests
from cryptography import x509
import paramiko
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

def getSymkey(devicename,host, path):
    #print(devicename,host, path)
    if host == 'localhost' or host == '127.0.0.1':
        DEVICE_KEY = path +"/"+devicename+"_sym.key"

        device_key = ''
        with open(DEVICE_KEY, "r") as f:
            device_key = f.read()

        return device_key
        
    else:
        
        DEVICE_KEY = devicename+"_sym.key"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname= host)
        
        # set up SFTP connection
        sftp = ssh.open_sftp()
        
        # copy file
        local_file_path = DEVICE_KEY
        remote_file_path = path +"/"+devicename+"_sym.key"
        sftp.put( remote_file_path, local_file_path)
        
        # close connections
        sftp.close()
        ssh.close()

        device_key = ''
        with open(DEVICE_KEY, "r") as f:
            f.read(device_key)

        return device_key