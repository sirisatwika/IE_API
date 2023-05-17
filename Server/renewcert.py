import json
import requests
import paramiko

def renewX509(devicename, host, path):
    root_token = 's.up6ofuB4XGe5tPQUyzultZjz'
    rolename = 'my-role' 
    headers = {
      'X-Vault-Token': root_token,
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = json.dumps({
             "common_name": "edgex.com",
             "ttl":"20000"
    })
    print(data)
    if host == 'localhost' or host == '127.0.0.1':
        resp1=requests.post('http://127.0.0.1:8200/v1/pki/issue/'+rolename, headers=headers, data= data)
        #print(resp1.json())
        device_cert_pem = resp1.json()['data']['certificate']
        device_key_pem = resp1.json()['data']['private_key']
        DEVICE_CERT = path +"/"+devicename+"_cert.pem"
        DEVICE_KEY = path +"/"+devicename+"_key.pem"
        with open(DEVICE_CERT, "wt") as f:
            f.write(device_cert_pem)
        with open(DEVICE_KEY, "wt") as f:
            f.write(device_key_pem)
    else:
        resp1=requests.post('http://127.0.0.1:8200/v1/pki/issue/'+rolename, headers=headers, data= data)
        device_cert_pem = resp1.json()['data']['certificate']
        device_key_pem = resp1.json()['data']['private_key']
        DEVICE_CERT = devicename+"_cert.pem"
        DEVICE_KEY = devicename+"_key.pem"
        with open(DEVICE_CERT, "wt") as f:
            f.write(device_cert_pem)
        with open(DEVICE_KEY, "wt") as f:
            f.write(device_key_pem)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname= host)
        
        # set up SFTP connection
        sftp = ssh.open_sftp()
        
        # copy file
        local_file_path = DEVICE_CERT 
        remote_file_path = path +"/"+devicename+"_cert.pem"
        sftp.put(local_file_path, remote_file_path)

        local_file_path = DEVICE_KEY
        remote_file_path = path +"/"+devicename+"_key.pem"
        sftp.put(local_file_path, remote_file_path)
        
        # close connections
        sftp.close()
        ssh.close()