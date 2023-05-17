import paramiko
from cryptography.fernet import Fernet
import base64
import datetime
import requests
import json

def renewSymkey(devicename,host, path,port):
    if host == 'localhost' or host == '127.0.0.1':
        # Generate a 256-bit symmetric key
        key = Fernet.generate_key()

        ctime = datetime.datetime.now()

        ct = {
            "creationtime": ctime
        }
        
        # Convert the key to a base64-encoded string
        device_symkey = base64.b64encode(key).decode('utf-8')
        
        DEVICE_SYMKEY = path +"/"+devicename+"_sym.key"
        DEVICE_SYMKEY_CT = path +"/"+devicename+"_sym_ct.json"

        with open(DEVICE_SYMKEY, "wt") as f:
            f.write(device_symkey)
        with open(DEVICE_SYMKEY_CT,"w") as f:
            f.write(json.dumps(ct))

        secret = json.dumps({
                "apiVersion": "v2",
                "path": "symkey",
                "secretData": [
                    {
                        "key": "edgexkey",
                        "value": ctime
                    }
                ]
            })
        secretresp = requests.post('http://localhost:'+str(port)+'/api/v2/secret', data=secret)
    else:
       # Generate a 256-bit symmetric key
        key = Fernet.generate_key()

        ctime = datetime.datetime.now()

        ct = {
            "creationtime": ctime
        }
        
        # Convert the key to a base64-encoded string
        device_symkey = base64.b64encode(key).decode('utf-8')

        DEVICE_SYMKEY = devicename+"_sym.key"
        DEVICE_SYMKEY_CT = devicename+"_sym_ct.json"
        with open(DEVICE_SYMKEY, "wt") as f:
            f.write(device_symkey)
        with open(DEVICE_SYMKEY_CT,"w") as f:
            f.write(json.dumps(ct))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname= host)
        
        # set up SFTP connection
        sftp = ssh.open_sftp()
        
        # copy file
        local_file_path = DEVICE_SYMKEY
        remote_file_path = path +"/"+devicename+"_sym.key"
        sftp.put(local_file_path, remote_file_path)

        # copy file
        local_file_path = DEVICE_SYMKEY_CT
        remote_file_path = path +"/"+devicename+"_sym_ct.json"
        sftp.put(local_file_path, remote_file_path)
        
        # close connections
        sftp.close()
        ssh.close()

        secret = json.dumps({
                "apiVersion": "v2",
                "path": "symkey",
                "secretData": [
                    {
                        "key": "edgexkey",
                        "value": ctime
                    }
                ]
            })
        secretresp = requests.post('http://localhost:'+str(port)+'/api/v2/secret', data=secret)