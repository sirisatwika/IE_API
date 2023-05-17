import requests
from cryptography import x509
import paramiko
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

def verifySymkey(devicename,host, path,service):
    #print(devicename,host, path)
    if host == 'localhost' or host == '127.0.0.1':
        DEVICE_KEY = path +"/"+devicename+"_sym.key"
        #print(DEVICE_CERT,DEVICE_KEY)
        device_key_pem = ''
        with open(DEVICE_KEY, "r") as f:
            device_key = f.read()

        apiurl = "http://127.0.0.1:8200/v1/secret/edgex/"+service+"/symkey"
        resp = requests.get(apiurl)
        edgex_key = resp.json()['data']['edgexkey']

        res = keyverify(device_key,edgex_key)
        
        print(res)

        return res
        
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
            device_key = f.read()

        apiurl = "http://127.0.0.1:8200/v1/secret/edgex/"+service+"/symkey"
        resp = requests.get(apiurl)
        edgex_key = resp.json()['edgexkey']

        res = keyverify(device_key,edgex_key)
        
        print(res)

        return res

def keyverify(devkey,edgexkey):
    if devkey == edgexkey:
        return True
    else:
        return False