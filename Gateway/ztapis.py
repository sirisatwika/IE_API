import json
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS,cross_origin

# creating a Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
  
@app.route('/')
def home():
    return "Welcome to Inteligent Edge!!!"

@app.route('/api/v1/ips')
@cross_origin()
def getips():
    try:
        headers = {"Authorization": "token EqRuRoIeUUAw4O1G4DeM3ajL6PZMMEla"} 
        response = requests.get('https://api.zerotier.com/api/v1/network/35c192ce9b6faf61/member',headers=headers)
        members = response.json()
        iplist = []
        for m in members:
            for ip in m['config']['ipAssignments']:
                print(ip)
                iplist.append(ip)
        res = {
            "ips": iplist
        }
        return res
    except Exception as e:
        return e

if __name__ == '__main__':
    app.run('0.0.0.0',5000,debug = True)