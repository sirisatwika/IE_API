import requests
import json
from datetime import datetime, timedelta
import time
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from createcacert import createX509
from influxdb import InfluxDBClient
from flask_httpauth import HTTPBasicAuth
from collections import OrderedDict
from verifyx509 import verifyX509
from getcert import getX509
from createkey import createSymkey
from getkey import getSymkey
from verifysymkey import verifySymkey
from renewcert import renewX509
from renewkey import renewSymkey
from flask_restx import Api, Resource, fields


# creating a Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
auth = HTTPBasicAuth()
api = Api(app, title='Intelligent Edge APIs', description = 'APIs used for Intelligent Edge Solution based on EdgeX Foundry platform',version="1.0",doc='/swagger')

# Define a namespace for your API routes
ns = api.namespace('gatewaydata', description='Fetching gateway data operations')


@ns.route('/api/v1/welcome')
class Home(Resource):
     '''Welcome message'''
     @ns.doc('welcome')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Welcome message'''
         return "Welcome to Inteligent Edge!!!"

@ns.route('/api/v1/count/provisioned')
class GatewayProvisionCount(Resource):
     '''Count of provisioned gateways'''
     @ns.doc('ProvisionedCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the total gateways provisioned'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gatewaycount = response.json()['totalCount']
             return str(gatewaycount)
         except Exception as e:
             return e

@ns.route('/api/v1/count/unprovisioned')
class GatewayUnProvisionCount(Resource):
     '''Count of unprovisioned gateways'''
     @ns.doc('UnprovisionedCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the total gateways unprovisioned'''
         try:
            apiurl_prov = "http://localhost:59881/api/v2/device/all?limit=-1"
            response_prov = requests.get(apiurl_prov)
            gatewaycount_prov = response_prov.json()['totalCount']
            
            apiurl_tot = "http://localhost:59881/api/v2/deviceprofile/all?limit=-1"
            response_tot = requests.get(apiurl_tot)
            gatewaycount_tot = response_tot.json()['totalCount']
            return str(gatewaycount_tot - gatewaycount_prov)
         except Exception as e:
            return e

@ns.route('/api/v1/count/total')
class GatewayTotalCount(Resource):
     '''Count of total gateways'''
     @ns.doc('TotalCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the total gateways count'''
         try:
            apiurl_tot = "http://localhost:59881/api/v2/deviceprofile/all?limit=-1"
            response_tot = requests.get(apiurl_tot)
            gatewaycount_tot = response_tot.json()['totalCount']
            return str(gatewaycount_tot)
         except Exception as e:
            return e

@ns.route('/api/v1/count/online')
class GatewayOnlineCount(Resource):
     '''Count of online gateways'''
     @ns.doc('OnlineCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the online gateways count'''
         try:
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            devicelist = response.json()['devices']
            cnt = 0
            for d in devicelist:
                if d['operatingState'] == "UP":
                    cnt += 1
            return str(cnt)
         except Exception as e:
            return e

@ns.route('/api/v1/count/offline')
class GatewayOfflineCount(Resource):
     '''Count of offline gateways'''
     @ns.doc('OfflineCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the offline gateways count'''
         try:
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            devicelist = response.json()['devices']
            cnt = 0
            for d in devicelist:
                if d['operatingState'] == "DOWN":
                    cnt += 1
            return str(cnt)
         except Exception as e:
            return e

@ns.route('/api/v1/count/active')
class GatewayActiveCount(Resource):
     '''Count of active gateways'''
     @ns.doc('ActiveCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the active gateways count'''
         try:
            curr_time = time.time_ns()
            #print(curr_time)
            prev_time = datetime.now() - timedelta(seconds = 2)
            prev_ns = int(time.mktime(prev_time.timetuple()) * pow(10, 9))
            #print(prev_ns)
            apiurl = "http://localhost:59880/api/v2/event/start/"+ str(prev_ns)+"/end/"+ str(curr_time)
            response = requests.get(apiurl)
            #print(response.json())
            events = response.json()['events']
            devnameset = set({})
            for e in events:
                devname =e['deviceName']
                devnameset.add(devname)
                #print('active' + devname)
            return str(len(devnameset))
         except Exception as e:
            return e

@ns.route('/api/v1/count/inactive')
class GatewayInActiveCount(Resource):
     '''Count of inactive gateways'''
     @ns.doc('InactiveCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the active gateways count'''
         try:
            apiurl_prov = "http://localhost:59881/api/v2/device/all?limit=-1"
            response_prov = requests.get(apiurl_prov)
            gatewaycount_prov = response_prov.json()['totalCount']
            
            curr_time = time.time_ns()
            #print(curr_time)
            prev_time = datetime.now() - timedelta(seconds = 2)
            prev_ns = int(time.mktime(prev_time.timetuple()) * pow(10, 9))
            #print(prev_ns)
            apiurl = "http://localhost:59880/api/v2/event/start/"+ str(prev_ns)+"/end/"+ str(curr_time)
            response = requests.get(apiurl)
            #print(response.json())
            events = response.json()['events']
            devnameset = set({})
            for e in events:
                devname =e['deviceName']
                devnameset.add(devname)            
            activecnt = len(devnameset)
            cnt = gatewaycount_prov - activecnt
            return str(cnt)
         except Exception as e:
            return e

@ns.route('/api/v1/name/getdevicenames/all')
class GatewayDeviceNamesAll(Resource):
     '''List of all devicenames connected'''
     @ns.doc('Devicenamesall')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the list of all device names connected'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             devicelist = response.json()['devices']
             lst = []
             for d in devicelist:
                 lst.append(d['name'])
             return lst                                                                      
         except Exception as e:
            return e

@ns.route('/api/v1/name/getdevicenames')
class GatewayDeviceNames(Resource):
     '''List of devicenames connected'''
     @ns.doc('Devicenames')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the list of device names connected'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             devicelist = response.json()['devices']
             lst = []
             for d in devicelist:
                 if 'protocols' in d:
                    for k,v in d['protocols'].items():
                       if 'Address' in v:
                          ip = v['Address']
                 apiurl2 = "http://"+ip+":5000/gatewaydata/api/v1/name/getdevicenames"
                 res2 = requests.get(apiurl2)
                 dev = {}
                 dev['name']=d['name']
                 dev['devices'] = res2.json()
                 lst.append(dev)
             return lst                                                                      
         except Exception as e:
             return e

@ns.route('/api/v1/getiotdevices/<devicename>')
class GatewayIoTDeviceslist(Resource):
     '''Fetch gateway IoT Devices List'''
     @ns.doc('GatewayIoTDevicesList')
     @api.param('devicename','Name of device to fetch IP',type='string',required=True)
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     @cross_origin()
     def get(self,devicename):
         '''Get the list of IoT Devices connected to the gateway'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/name/"+devicename
             print(apiurl)
             response = requests.get(apiurl)
             print(response.json())
             p = response.json()['device']['protocols']
             print(p)
             ip = '127.0.0.1'
             for k,v in p.items():
                  print(v)
                  if 'Address' in v:
                      ip = v['Address']                                                
             apiurl2='http://'+ip+':59881/api/v2/device/all?limit=-1'
             response2 = requests.get(apiurl2)
             devicelist = response2.json()['devices']
             devnames=[]
             for d in devicelist:
                   devnames.append(d['name'])
             return devnames
         except Exception as e:
            return e



@ns.route('/api/v1/telemetrydata/<gatewayname>/all')
class GatewayTelemetryDataAll(Resource):
     '''Telemetry data for all devices'''
     @ns.doc('TelemetryDataAll')
     @cross_origin()
     @api.param('gatewayname','Name of gateway',type='string',required=True)
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self,gatewayname):
         '''Get the telemetry data from all devices'''
         try:
             apiurl1 = "http://localhost:59881/api/v2/device/name/"+str(gatewayname)
             res = requests.get(apiurl1)
             g = res.json()['device']
             ip = '127.0.0.1'
             if 'protocols' in g:
                for k,v in g['protocols'].items():
                     if 'Address' in v:
                         ip = v['Address']
             apiurl2 = "http://"+ip+":5000/gatewaydata/api/v1/telemetrydata/all"
             res2 = requests.get(apiurl2)
             return res2.json()                                                               
         except Exception as e:
             return e



# InfluxDB configuration
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USERNAME = 'admin'
INFLUXDB_PASSWORD = 'admin'
INFLUXDB_DATABASE = 'sensorsedgex'

# Create InfluxDB client
client = InfluxDBClient(host=INFLUXDB_HOST,port=INFLUXDB_PORT,username=INFLUXDB_USERNAME,
password=INFLUXDB_PASSWORD,
database=INFLUXDB_DATABASE)





@ns.route('/api/v1/count/gatewaywrtmanu')
class GatewayWrtManufacturer(Resource):
     '''Gateway Details per manufacturer '''
     @ns.doc('GatewayDetailsManufacturer')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the gateway details with respect to manufacturer'''
         try:
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            devicelist = response.json()['devices']
            manulist=[]
            for d in devicelist:
                apiurl2="http://localhost:59881/api/v2/deviceprofile/name/"+d['profileName']
                response = requests.get(apiurl2)
                devmanu = response.json()['profile']['manufacturer']
                manulist.append(devmanu)
            mp = {}
            cnt = 0
            for m in manulist:
                if m in mp:
                    mp[m] += 1
                else:
                    mp[m] = 1       
            return json.dumps(mp)                                                                 
         except Exception as e:
             return e


@ns.route('/api/v1/count/gatewayconfigdata')
class GatewayConfigData(Resource):
     '''Gateway configuration Details  '''
     @ns.doc('GatewayConfigdetails')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the gateway config details'''
         try:
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            devicelist = response.json()['devices']
            mp = {}
            listd = []
            for d in devicelist:
                id_val =d['id']
                name = d['name']
                desc = d['description']
                service = d['servieName']
                profile = d['profileName']
                listd.append({"id": id_val,"name":name})
            #print(listd)         
            return str(listd)                                                               
         except Exception as e:
             return e


@ns.route('/api/v1/profiles')
class GatewayProfiles(Resource):
     '''Gateway Profiles List  '''
     @ns.doc('GatewayProfiles')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the gateway profiles'''
         try:
            apiurl = "http://localhost:59881/api/v2/deviceprofile/all?limit=-1"
            response = requests.get(apiurl)
            return response.json()                                                             
         except Exception as e:
             return e

@ns.route('/api/v1/services')
class GatewayProfiles(Resource):
     '''Gateway Device Services List  '''
     @ns.doc('GatewayDeviceServices')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the list of gateway device services '''
         try:
            apiurl = "http://localhost:59881/api/v2/deviceservice/all"
            response = requests.get(apiurl)
            return response.json()                                                            
         except Exception as e:
             return e     

# Define a namespace for your API routes
dps = api.namespace('provision', description='Device provisioning operations')

@dps.route('/api/v1/service/list')
class DeviceServiceNames(Resource):
     '''Device Services Names'''
     @ns.doc('GatewayDeviceServiceslist')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the list of device service names'''
         try:
            response = requests.get("http://localhost:59881/api/v2/deviceservice/all")
            services = response.json()['services']
            devservices = set({})
            for s in services:
                devservices.add(s['name'])
            return list(devservices)                                                           
         except Exception as e:
             return e 

AEvent = api.model('AutoEvents',{
   "interval":fields.String(required=True,description='Interval indicates how often the specific resource needs to be polled. It represents as a duration string. The format of this field is to be an unsigned integer followed by a unit which may be "ns", "us" (or "µs"), "ms", "s", "m", "h" representing nanoseconds, microseconds, milliseconds, seconds, minutes or hours. Eg, "100ms", "24h"'),
   "onChange":fields.Boolean(required=False,default=False,description='OnChange indicates whether the device service will generate an event only, if the reading value is different from the previous one. If true, only generate events when readings change'),
   "sourceName": fields.String(required=False,description='SourceName indicates the name of the resource or device command in the device profile which describes the event to generate')
})

Protoc = api.model('ProtocolModel',{
      "Protocol":fields.String(required=True,description='Protocol name'),
      "Address": fields.String(required=True, description='Host Name/IP adddress'),
      "Port": fields.String(required=True, description='Port number'),
      "UnitID": fields.String(required=True,desciption='UnitID')
})

DevModel = api.model('DeviceModel',{
   "name": fields.String(required=True, description='Gateway/Device name provisioned'),
   "description": fields.String(required=True, description='Description of the gateway/device'),
   "adminState": fields.String(required=False, description='Admin state of the gateway/device',enum=['LOCKED','UNLOCKED']),
   "operatingState": fields.String(required=False, description='Admin state of the gateway/device',enum=['UP','DOWN','UNLOCKED']),
   "labels": fields.List(fields.String() ,required=False,description='Other information to help search/retrieve devices'),
   "location": fields.String(required=False, description='Gateway/Device Location'),
   "serviceName": fields.String(required=True, description='Associated deviceservice name'),
   "profileName": fields.String(required=True, description='Associated deviceprofile name'),
    "autoEvents": fields.List(fields.Nested(AEvent) ,required=False,description='Auto event information'),
    "protocols": fields.Nested(Protoc,required=True,description='Protocol details'),
    "authMethod": fields.String(required=True, description='Authentication method',enum=['X509','Symmetric Key']),
    "path": fields.String(required=True, description='Secure device path to store secrets'),
    "notify": fields.Boolean(required=False,default=True,description='If the notify property is set to true, the device service managing the device will receive a notification')
})

create_args = api.model('CreateSecretData',{
    "apiVersion": fields.String(required=False, description='The api version'),
    "device": fields.Nested(DevModel,required=True,description='Device/Gateway details')
  }) 

@dps.route('/api/v1/gateway/create')
class CreateSecret(Resource):
     '''Create secret'''
     @api.expect(create_args, validate=True)
     @ns.doc('CreateSecret')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def post(self):
         '''Create secret for gateway'''
         try:
             req_data = json.loads(request.data)
             devcreatemethod = req_data ['device']['authMethod']
             if devcreatemethod == 'X509':
                 response = requests.post("http://localhost:5000/api/v1/gateway/create/x509cert",json = req_data)
                 return response.text, response.status_code
             elif devcreatemethod == 'Symmetric Key':
                 response = requests.post("http://localhost:5000/api/v1/gateway/create/symkey",json = req_data)
                 return response.text, response.status_code
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/create/x509cert')
class CreateX509(Resource):
     '''Create secret X509 Certificate'''
     @api.expect(create_args, validate=True)
     @ns.doc('CreateSecretX509')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def post(self):
         '''Create secret X509 Certificate for gateway'''
         try:
             device_data = json.loads(request.data)
             devhost = ''
             devname = device_data['device']['name']
             devprotocol = device_data['device']['protocols']
             for k,v in devprotocol.items():
                 devhost = v['Address']
             print(devhost)
             devprovpath = device_data['device']['path']
             createX509(devname,devhost, devprovpath)
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/create/symkey')
class CreateSymkey(Resource):
     '''Create secret Symmetric Key'''
     @api.expect(create_args, validate=True)
     @ns.doc('CreateSecretSymkey')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def post(self):
         '''Create secret Symmetric Key for gateway'''
         try:
             device_data = json.loads(request.data)
             devhost = ''
             devname = device_data['device']['name']
             devprotocol = device_data['device']['protocols']
             for k,v in devprotocol.items():
                 devhost = v['Address']
             print(devhost)

             dsname = device_data['device']['serviceName']
             dsresp = requests.get('http://localhost:59881/api/v2/deviceservice/name/'+dsname)
             devprovpath = device_data['device']['path']
             dsaddr = dsresp.json()['service']['baseAddress']
             dsport = dsaddr.split(':')[-1]

             createSymkey(devname,devhost, devprovpath, dsport)
         except Exception as e:
             return e

provision_args = api.model('ProvisionData',{
    "apiVersion": fields.String(required=False, description='The api version'),
    "device": fields.Nested(DevModel,required=True,description='Device/Gateway details')
  }) 
       
@dps.route('/api/v1/gateway/provision')
class ProvisionGateway(Resource):
     '''Provision gateway'''
     @api.expect(provision_args, validate=True)
     @ns.doc('GatewayProvision')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def post(self):
         '''Provision gateway'''
         try:
             req_data = json.loads(request.data)
             devprovmethod = req_data ['device']['authMethod']
             if devprovmethod == 'X509':
                 response = requests.post("http://localhost:5000/api/v1/gateway/provision/x509cert",json = req_data)
                 return response.text, response.status_code
             elif devprovmethod == 'Symmetric Key':
                 response = requests.post("http://localhost:5000/api/v1/gateway/provision/symkey",json = req_data)
                 return response.text, response.status_code
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/provision/x509cert')
class ProvisionX509(Resource):
     '''Provision gateway using X509 certificate'''
     @api.expect(provision_args, validate=True)
     @ns.doc('GatewayProvisionX509')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def post(self):
         '''Provision gateway using X509 Certificate'''
         try:
             device_data = json.loads(request.data)
             devhost = ''
             devname = device_data['device']['name']
             devprotocol = device_data['device']['protocols']
             for k,v in devprotocol.items():
                 devhost = v['Address']
             print(devhost)
             devprovpath = device_data['device']['path']
             print(devprovpath)
             #createX509(devname,devhost, devprovpath)
             if not verifyX509(devname,devhost,devprovpath):
                 print("Device certificate is not valid and not trusted")
                 return "Device certificate is not valid and not trusted"
             else:
                 dsname = device_data['device']['serviceName']
                 #print(dsname)
                 dsresp = requests.get('http://localhost:59881/api/v2/deviceservice/name/'+dsname)
                 #print('Device service:',dsresp)
                 dsaddr = dsresp.json()['service']['baseAddress']
                 dsport = dsaddr.split(':')[-1]
                 #print(dsaddr,dsport)
                 secret = json.dumps({
                     "apiVersion": "v2",
                     "path": "credentials",
                     "secretData": [
                         {
                             "key": devname + "-" + device_data['device']['authMethod'] + "@" + devprovpath,
                             "value": getX509(devname,devhost,devprovpath)
                         }
                     ]
                 })
                 try:
                    secretresp = requests.post('http://localhost:'+str(dsport)+'/api/v2/secret', data=secret)
                 except Exception as e:
                    print(e) 
                 #print(secretresp)
                 device_json = json.dumps([
                 {
                     "apiVersion": device_data['apiVersion'],
                     "device": {
                         "name": device_data['device']['name'],
                         "description": device_data['device']['description'],
                         "adminState": device_data['device']['adminState'],
                         "operatingState": device_data['device']['operatingState'],
                         "labels": device_data['device']['labels'],
                         "location": device_data['device']['location'],
                         "serviceName": device_data['device']['serviceName'],
                         "profileName": device_data['device']['profileName'],
                         "autoEvents": device_data['device']['autoEvents'],
                         "protocols": device_data['device']['protocols'],
                         "notify": device_data['device']['notify']
                     }
                 }
                 ])
                 #print(device_json)
                 try:
                     resp = requests.post('http://localhost:59881/api/v2/device',data = device_json)
                     return 'Device provisioned'
                 except Exception as e:
                     print(e)
                 #print('Device provisioning:',resp)
                 return 'Error in device provisioning'                                                               
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/provision/symkey')
class ProvisionSymkey(Resource):
     '''Provision gateway using symmetric key'''
     @api.expect(provision_args, validate=True)
     @ns.doc('GatewayProvisionSymkey')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def post(self):
         '''Provision gateway using symmetric key'''
         try:
             device_data = json.loads(request.data)
             devhost = ''
             devname = device_data['device']['name']
             devprotocol = device_data['device']['protocols']
             for k,v in devprotocol.items():
                 devhost = v['Address']
             print(devhost)
             devprovpath = device_data['device']['path']
             print(devprovpath)

             dsname = device_data['device']['serviceName']

             if not verifySymkey(devname,devhost,devprovpath,dsname):
                 print("Device symmetric key is not valid and not trusted")
                 return "Device symmetric key is not valid and not trusted"
             else:
                 dsname = device_data['device']['serviceName']
                 #print(dsname)
                 dsresp = requests.get('http://localhost:59881/api/v2/deviceservice/name/'+dsname)
                 #print('Device service:',dsresp)
                 dsaddr = dsresp.json()['service']['baseAddress']
                 dsport = dsaddr.split(':')[-1]
                 #print(dsaddr,dsport)
                 secret = json.dumps({
                     "apiVersion": "v2",
                     "path": "credentials",
                     "secretData": [
                         {
                             "key": devname + "-" + device_data['device']['authMethod'] + "@" + devprovpath ,
                             "value": getSymkey(devname,devhost,devprovpath)
                         }
                     ]
                 })
                 try:
                     secretresp = requests.post('http://localhost:'+str(dsport)+'/api/v2/secret', data=secret)
                 except Exception as e:
                     print(e) 
                 #print(secretresp)
                 device_json = json.dumps([
                 {
                     "apiVersion": device_data['apiVersion'],
                     "device": {
                         "name": device_data['device']['name'],
                         "description": device_data['device']['description'],
                         "adminState": device_data['device']['adminState'],
                         "operatingState": device_data['device']['operatingState'],
                         "labels": device_data['device']['labels'],
                         "location": device_data['device']['location'],
                         "serviceName": device_data['device']['serviceName'],
                         "profileName": device_data['device']['profileName'],
                         "autoEvents": device_data['device']['autoEvents'],
                         "protocols": device_data['device']['protocols'],
                         "notify": device_data['device']['notify']
                     }
                 }
                 ])
                 #print(device_json)
                 try:
                     resp = requests.post('http://localhost:59881/api/v2/device',data = device_json)
                     return 'Device provisioned'
                 except Exception as e:
                     print(e)
                 #print('Device provisioning:',resp)
                 return 'Error in device provisioning'                                                               
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/renew/<string:devicename>')
class RenewGatewaySecret(Resource):
     '''Renew secrets for gateway'''
     @api.param('service','Device service name',type='string',required=True)
     @api.param('host','Gateway host name/ip',type='string',required=True)
     @api.param('path','path where secret stored in gateway securely',type='string',required=True)
     @ns.doc('GatewayRenew',params = {'devicename' : 'Gateway name for which to renew X509 certificate'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def put(self,devicename):
         '''Renew secret generated for a gateway '''
         try:
             query = request.args
             devcreatemethod = query.auth
             path = query.get('path')
             host = query.get('host')
             dsname = query.get('service')
             if devcreatemethod == 'X509':
                 response = requests.post("http://localhost:5000/api/v1/gateway/renew/x509cert/"+devicename+"?path="+path+"&host="+host+"&service="+dsname)
                 return response.text, response.status_code
             elif devcreatemethod == 'Symmetric Key':
                 response = requests.post("http://localhost:5000/api/v1/gateway/renew/symkey"+devicename+"?path="+path+"&host="+host+"&service="+dsname)
                 return response.text, response.status_code                                                               
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/renew/x509cert/<string:devicename>')
class RenewX509(Resource):
     '''Renew X509 certificate for a gateway'''
     @api.param('service','Device service name',type='string',required=True)
     @api.param('host','Gateway host name/ip',type='string',required=True)
     @api.param('path','path where x509 certificate stored in gateway securely',type='string',required=True)
     @ns.doc('GatewayRenewX509',params = {'devicename' : 'Gateway name for which to renew X509 certificate'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def put(self,devicename):
         '''Renew Symmetric key generated for a gateway '''
         try:
             query = request.args
             path = query.get('path')
             host = query.get('host')
             renewX509(devicename, host, path)
             dsname = query.get('service')
             dsresp = requests.get('http://localhost:59881/api/v2/deviceservice/name/'+dsname)
             dsaddr = dsresp.json()['service']['baseAddress']
             dsport = dsaddr.split(':')[-1]
             secret = json.dumps({
                 "apiVersion": "v2",
                 "path": "credentials",
                 "secretData": [
                     {
                         "key": devicename + "-" + 'X509' + "@" + path ,
                         "value": getX509(devicename,host,path)
                     }
                 ]
             })
             secretresp = requests.post('http://localhost:'+str(dsport)+'/api/v2/secret', data=secret)
             return 'Renewed Certificate'                                                               
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/renew/symkey/<string:devicename>')
class RenewSymKey(Resource):
     '''Renew symmetric key for a gateway'''
     @api.param('service','Device service name',type='string',required=True)
     @api.param('host','Gateway host name/ip',type='string',required=True)
     @api.param('path','path where symmetric key stored in gateway securely',type='string',required=True)
     @ns.doc('GatewayRenewSymkey',params = {'devicename' : 'Gateway name for which to renew symmetric key'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def put(self,devicename):
         '''Renew Symmetric key generated for a gateway '''
         try:
            query = request.args
            path = query.get('path')
            host = query.get('host')
            dsname = query.get('service')
            dsresp = requests.get('http://localhost:59881/api/v2/deviceservice/name/'+dsname)
            dsaddr = dsresp.json()['service']['baseAddress']
            dsport = dsaddr.split(':')[-1]
            renewSymkey(devicename, host, path, dsport)
            secret = json.dumps({
                "apiVersion": "v2",
                "path": "credentials",
                "secretData": [
                    {
                        "key": devicename + "-" + 'X509' + "@" + path ,
                        "value": getSymkey(devicename,host,path)
                    }
                ]
            })
            secretresp = requests.post('http://localhost:'+str(dsport)+'/api/v2/secret', data=secret)
            return 'Renewed Symmetric Key'                                                                 
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/deprovision/<string:devicename>')
class DeprovisionGateway(Resource):
     '''Deprovision Gateway'''
     @api.param('auth','Authentication Type',type='string',enum=['X509','Symmetric Key'],required=True)
     @api.param('service','Device service name',type='string',required=True)
     @api.param('serialnum','Certificate serial number',type='string',required=True)
     @ns.doc('GatewayDeprovision',params = {'devicename' : 'Gateway name to deprovision'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def delete(self,devicename):
         '''Deprovision a gateway'''
         try:
             query = request.args
             devcreatemethod = query.auth
             serialnum = query.serialnum
             service = query.service
             if devcreatemethod == 'X509':
                 response = requests.delete("http://localhost:5000/api/v1/gateway/deprovision/x509cert/"+devicename+"?serialnum="+serialnum+"&service="+service)
                 return response.text, response.status_code
             elif devcreatemethod == 'Symmetric Key':
                 response = requests.delete("http://localhost:5000/api/v1/gateway/deprovision/symkey"+devicename+"?service="+service)
                 return response.text, response.status_code                                                               
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/deprovision/x509cert/<string:devicename>')
class DeprovisionX509(Resource):
     '''Deprovision Gateway using X509 certificate '''
     @api.param('service','Device service name',type='string',required=True)
     @api.param('serialnum','Certificate serial number',type='string',required=True)
     @ns.doc('GatewayDeprovisionX509',params = {'devicename' : 'Gateway name to deprovision'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def delete(self,devicename):
         '''Deprovision a gateway using X509 Certificate'''
         try:
            snum = request.args.serialnum
            service = request.args.service
            root_token = 's.up6ofuB4XGe5tPQUyzultZjz' 
            headers = {
                'X-Vault-Token': root_token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = json.dumps({
                "serial_number": snum
            })
            resp1=requests.post('http://127.0.0.1:8200/v1/pki/revoke', headers=headers, data= data)
            requests.delete("https://127.0.0.1:8200/v1/secret/edgex/"+service+"credentials/"+devicename, headers=headers)
            requests.delete("http://127.0.0.1:59881/api/v2/device/name/"+devicename)
            return "Successfully deprovisioned the device"                                                                 
         except Exception as e:
             return e

@dps.route('/api/v1/gateway/deprovision/symkey/<string:devicename>')
class DeprovisionSymKey(Resource):
     '''Deprovision Gateway using symmetric key '''
     @api.param('service','Device service name',type='string',required=True)
     @ns.doc('GatewayDeprovisionSymkey',params = {'devicename' : 'Gateway name to deprovision'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def delete(self,devicename):
         '''Deprovision a gateway using Symmetric key'''
         try:
            service = request.args.service
            root_token = 's.up6ofuB4XGe5tPQUyzultZjz' 
            headers = {
                'X-Vault-Token': root_token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            requests.delete("https://127.0.0.1:8200/v1/secret/edgex/"+service+"credentials/"+devicename, headers=headers)
            requests.delete("http://127.0.0.1:59881/api/v2/device/name/"+devicename)
            return "Successfully deprovisioned the device"                                                                 
         except Exception as e:
             return e
             
# Define a namespace for your API routes
zt = api.namespace('network', description='zerotier - network operations')

@zt.route('/api/v1/ips/<string:networkid>')
class ListIPs(Resource):
     '''List IPs'''
     @ns.doc('ListIPs',params={'networkid':'id of zerotier network to fetch member IPs'})
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self,networkid):
         '''List all IPs of the devices/gateways connected to the zerotier network'''
         try:
             headers = {"Authorization": "token EqRuRoIeUUAw4O1G4DeM3ajL6PZMMEla"} 
             response = requests.get('https://api.zerotier.com/api/v1/network/'+networkid+'/member',headers=headers)
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

iotd = api.namespace('iotdevicedata', description='Fetching iot device data operations')

@iotd.route('/api/v1/count/provisioned')
class IoTDeviceProvisionCount(Resource):
     '''Count of provisioned IoT Devices'''
     @ns.doc('IoTDeviceProvisionedCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the total IoT Devices provisioned'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             #print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 #print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 #print(gatewayip)
                 apiurl2 = "http://"+gatewayip+":59881/api/v2/device/all?limit=-1"
                 #print(apiurl2)  
                 response2 = requests.get(apiurl2)
                 #print(response2.json())
                 iotdevicecnt += response2.json()['totalCount']   
             return str(iotdevicecnt)
         except Exception as e:
             return e

@iotd.route('/api/v1/count/unprovisioned')
class IoTDeviceUnProvisionCount(Resource):
     '''Count of unprovisioned IoT Devices'''
     @ns.doc('IoTDevicesUnprovisionedCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the total IoT Devices unprovisioned'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 print(gatewayip)
                 
                 apiurl2 = "http://"+gatewayip+":59881/api/v2/device/all?limit=-1"
                 response_prov = requests.get(apiurl2)
                 gatewaycount_prov = response_prov.json()['totalCount']
                 
                 apiurl3 = "http://"+gatewayip+":59881/api/v2/deviceprofile/all?limit=-1"
                 response_tot = requests.get(apiurl3)
                 gatewaycount_tot = response_tot.json()['totalCount']
                 
                 iotdevicecnt += (gatewaycount_tot - gatewaycount_prov)
             return str(iotdevicecnt)
         except Exception as e:
            return e

@iotd.route('/api/v1/count/total')
class IoTDeviceTotalCount(Resource):
     '''Count of total IoT Devices'''
     @ns.doc('IoTDevicesTotalCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the total IOT Devices count'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 print(gatewayip)
                 
                 apiurl3 = "http://"+gatewayip+":59881/api/v2/deviceprofile/all?limit=-1"
                 response_tot = requests.get(apiurl3)
                 gatewaycount_tot = response_tot.json()['totalCount']
                 
                 iotdevicecnt += gatewaycount_tot
             return str(iotdevicecnt)
         except Exception as e:
            return e

@iotd.route('/api/v1/count/online')
class IoTDeviceOnlineCount(Resource):
     '''Count of online IoT Devices'''
     @ns.doc('IoTDeviceOnlineCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the online IoT Devices count'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 print(gatewayip)
                 
                 apiurl2 = "http://"+gatewayip+":59881/api/v2/device/all?limit=-1"
                 response_prov = requests.get(apiurl2)
                 gateway_devices = response_prov.json()['devices']
                 
                 for gd in gateway_devices:
                      if gd['operatingState'] == "UP":
                           iotdevicecnt+=1        
             return str(iotdevicecnt)
         except Exception as e:
             return e

@iotd.route('/api/v1/count/offline')
class IoTDeviceOfflineCount(Resource):
     '''Count of offline IoT Devices'''
     @ns.doc('IoTDeviceOfflineCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the offline IoT Devices count'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 print(gatewayip)
                 
                 apiurl2 = "http://"+gatewayip+":59881/api/v2/device/all?limit=-1"
                 response_prov = requests.get(apiurl2)
                 gateway_devices = response_prov.json()['devices']
                 
                 for gd in gateway_devices:
                      if gd['operatingState'] == "DOWN":
                           iotdevicecnt+=1
             return str(iotdevicecnt)    
         except Exception as e:
             return e

@iotd.route('/api/v1/count/active')
class IoTDeviceActiveCount(Resource):
     '''Count of active IoT Device'''
     @ns.doc('IoTDeviceActiveCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the active IoT Device count'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 print(gatewayip)
 
                 curr_time = time.time_ns()
                 print(curr_time)
                 prev_time = datetime.now() - timedelta(seconds = 10)
                 prev_ns = int(time.mktime(prev_time.timetuple()) * pow(10, 9))
                 print(prev_ns)
                 apiurl2 = "http://"+gatewayip+":59880/api/v2/event/start/"+ str(prev_ns)+"/end/"+ str(curr_time)+"?limit=-1"
                 print(apiurl2)
                 response2 = requests.get(apiurl2)
                 #print(response.json())
                 events = response2.json()['events']
                 print(events)
                 devnameset = set({})
                 for e in events:
                     devname =e['deviceName']
                     devnameset.add(devname)
                     #print('active' + devname)
                 iotdevicecnt+=(len(devnameset))
             return str(iotdevicecnt)
         except Exception as e:
             return e

@iotd.route('/api/v1/count/inactive')
class IoTDeviceInActiveCount(Resource):
     '''Count of inactive IoT Devices'''
     @ns.doc('IoTDeviceInactiveCount')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the inactive IoT Device count'''
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             gateways = response.json()['devices']
             print(gateways)
             iotdevicecnt = 0
             for g in gateways:
                 gatewayip = '127.0.0.1'
                 pdata={}
                 for k,v in g['protocols'].items():
                     pdata=v
                 print(pdata)
                 if 'Address' in pdata:
                      gatewayip = pdata['Address']
                 print(gatewayip)
 
                 apiurl2 = "http://"+gatewayip+":59881/api/v2/device/all?limit=-1"
                 response_prov = requests.get(apiurl2)
                 gatewaycount_prov = response_prov.json()['totalCount']
                 
                 curr_time = time.time_ns()
                 print(curr_time)
                 prev_time = datetime.now() - timedelta(seconds = 10)
                 prev_ns = int(time.mktime(prev_time.timetuple()) * pow(10, 9))
                 print(prev_ns)
                 
                 apiurl3 = "http://"+gatewayip+":59880/api/v2/event/start/"+ str(prev_ns)+"/end/"+ str(curr_time)+"?limit=-1"
                 print(apiurl3)
                 response3 = requests.get(apiurl3)
                 #print(response.json())
                 events = response3.json()['events']
                 print(events)
                 devnameset = set({})
                 for e in events:
                     devname =e['deviceName']
                     devnameset.add(devname)
                     #print('active' + devname)
                 iotdevicecnt+=(gatewaycount_prov-(len(devnameset)))
             return str(iotdevicecnt)
         except Exception as e:
             return e
             

@iotd.route('/api/v1/name/getiotdevicedetails/all')
class IoTDeviceDetailsDataCollection(Resource):
    '''List of IoT Devices details for data collection'''
    @ns.doc('IoTdevicesdetailDataCollection')
    @cross_origin()
    @api.response(200,'Success..')
    @api.response(400,'Invalid input')
    @api.response(404,'Page Not Found')
    @api.response(500,'Internal Server Error')
    def get(self):
        '''Get the list of IoT Devices detail for configuration'''
        unique_device_names = set()
        devices_info = []
        unique_gateway_names = set()
        try:  
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            print(response.json())
            p = response.json()['devices']
             #print(p)
             #print("next IP")
            for gp in p:
                gateway_name = gp['name']
                if gateway_name not in unique_gateway_names:  
                    unique_gateway_names.add(gateway_name)   
                    ip = '127.0.0.1'
                    port = '5000'
                    if 'protocols' in gp:
                        for k,v in gp['protocols'].items():
                            print(v)
                            if 'Address' in v:
                                ip = v['Address'] 
                            if 'Port' in v:
                                port = v['Port']   
                    print("printing IP")
                    print(ip)                                                     
                    apiurl2='http://'+ip+':59881/api/v2/device/all?limit=-1'
                    #print(apiurl2)
                    response2 = requests.get(apiurl2)
                    devicelist = response2.json()['devices']
                    for g in devicelist:
                        device_name = g['name']
                        #print(device_name)
                        if device_name not in unique_device_names:
                            unique_device_names.add(device_name)
                            #print(unique_device_names)
                            gatewayip = ip
                            gatewayport = port
                            pdata={}
                            if 'protocols' in g:
                                for k,v in g['protocols'].items():
                                    pdata=v
                                if 'Address' in pdata:
                                    gatewayip = pdata['Address']
                                if 'Port' in pdata:
                                    gatewayport = pdata['Port']
                            print(gatewayip)
                            print("\n")
                            status = ''
                            createdtime = g['created']
                            time_in_sec = createdtime / pow(10,9)
                            dt = datetime.fromtimestamp(time_in_sec)
                            form_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
                            #print(form_dt)
                            modifiedtime = g['modified']
                            time_in_sec_m = modifiedtime / pow(10,9)
                            dt_m = datetime.fromtimestamp(time_in_sec_m)
                            form_dt_m = dt_m.strftime('%Y-%m-%d %H:%M:%S')
                            apiurl3 = "http://"+gatewayip+":59881/api/v2/deviceprofile/name/"+g['profileName']
                            print(apiurl3)
                            res_devpro = requests.get(apiurl3)
                            manufacturername = res_devpro.json()['profile']['manufacturer']
                            print(manufacturername)
                            if g['operatingState'] == "UP":
                                status = 'online'
                            else:
                                status = 'offline'
                            device_info = [
                                    g['id'],
                                    g['name'],
                                    g['description'],
                                    gatewayip,
                                    gatewayport,
                                    'Hyderabad',
                                    gateway_name,
                                    gp['id'],
                                    g['profileName'],
                                    g['serviceName'],
                                    status,
                                    manufacturername,
                                    'provisioned',
                                    form_dt,
                                    'Active',
                                    form_dt_m,
                                ]
                            devices_info.append(device_info)
                            print(device_info)
                            print("\n")
            return devices_info
        except Exception as e:
            return str(e)

@ns.route('/api/v1/name/getgatewayconfigdetails/all')
class GatewayDetailsConfig(Resource):
    '''List of gateways details for data collection'''
    @ns.doc('GatewaysdetailDataCollection')
    @cross_origin()
    @api.response(200,'Success..')
    @api.response(400,'Invalid input')
    @api.response(404,'Page Not Found')
    @api.response(500,'Internal Server Error')
    def get(self):
        '''Get the list of gateways detail for configuration'''
        unique_device_names = set()
        devices_info = []
        try:           
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            gateways = response.json()['devices']
            for g in gateways:
                device_name = g['name']
                if device_name not in unique_device_names:
                    unique_device_names.add(device_name)
                    gatewayip = '127.0.0.1'
                    gatewayport = '5000'
                    pdata={}
                    if 'protocols' in g:
                        for k,v in g['protocols'].items():
                            pdata=v
                        if 'Address' in pdata:
                            gatewayip = pdata['Address']
                        if 'Port' in pdata:
                            gatewayport = pdata['Port']
                    status = ''
                    createdtime = g['created']
                    time_in_sec = createdtime / pow(10,9)
                    dt = datetime.fromtimestamp(time_in_sec)
                    form_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
                    modifiedtime = g['modified']
                    time_in_sec_m = modifiedtime / pow(10,9)
                    dt_m = datetime.fromtimestamp(time_in_sec_m)
                    form_dt_m = dt_m.strftime('%Y-%m-%d %H:%M:%S')
                    apiurl2 = "http://localhost:59881/api/v2/deviceprofile/name/"+g['profileName']
                    res_devpro = requests.get(apiurl2)
                    manufacturername = res_devpro.json()['profile']['manufacturer']
                    if g['operatingState'] == "UP":
                        status = 'online'
                    else:
                        status = 'offline'
                    if 'location' not in g:
                        g['location']='Mysore'
                    device_info = [
                        g['id'],
                        g['name'],
                        gatewayip,
                        gatewayport,
                        g['location'],
                        g['serviceName'],
                        g['profileName'],
                        g['description'],
                        status,
                        'provisioned',
                        'Default',
                        form_dt,
                        'Active',
                        form_dt_m,
                        'NA',
                        '',
                        '',
                        'Ubuntu 22.04',
                        '',
                        'NA',
                        '',
                        'NA',
                        ''
                    ]
                    devices_info.append(device_info)
                #print(devices_info)
            return devices_info
        except Exception as e:
            return str(e)


@ns.route('/api/v1/name/getgatewayconfigdetailsoverview/all')
class GatewayDetailsConfigOverview(Resource):
    '''List of gateways details for data collection'''
    @ns.doc('GatewaysdetailDataCollection')
    @cross_origin()
    @api.response(200,'Success..')
    @api.response(400,'Invalid input')
    @api.response(404,'Page Not Found')
    @api.response(500,'Internal Server Error')
    def get(self):
        '''Get the list of gateways detail for configuration'''
        unique_device_names = set()
        devices_info = []
        try:           
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            gateways = response.json()['devices']
            for g in gateways:
                device_name = g['name']
                if device_name not in unique_device_names:
                    unique_device_names.add(device_name)
                    gatewayip = '127.0.0.1' 
                    if 'protocols' in g:
                        for k,v in g['protocols'].items():
                            if 'Address' in v:
                                gatewayip = v['Address']
                    device_info = [
                        g['id'],
                        g['name'],
                        gatewayip,
                        '',
                        '',                       
                        ''
                    ]
                    devices_info.append(device_info)
                #print(devices_info)
            return devices_info
        except Exception as e:
            return str(e)

@ns.route('/api/v1/name/getgatewaydetails/all')
class GatewayDetailsAll(Resource):
     '''List of gateway and their details'''
     @ns.doc('Gatewaydetails')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the list of gateways and their details'''
         unique_device_names = set({})
         devices_info = []
         try:
             apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
             response = requests.get(apiurl)
             deviceslist = response.json()['devices']
             print(deviceslist)
             for device in deviceslist:
                 device_name = device['name']
                 if device_name not in unique_device_names:
                     unique_device_names.add(device_name)
                     status = ''
                     createdtime = device['created']
                     #print(createdtime)
                     time_in_sec = createdtime / pow(10,9)
                     dt = datetime.fromtimestamp(time_in_sec)
                     form_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
                     modifiedtime = device['modified']
                     #print(modifiedtime)
                     time_in_sec_m = modifiedtime / pow(10,9)
                     dt_m = datetime.fromtimestamp(time_in_sec_m)
                     form_dt_m = dt_m.strftime('%Y-%m-%d %H:%M:%S')
                     
                     protocolname = ''
                     protocolinfo={}
                     
                     print(device['protocols'].items())
                     for k,v in device['protocols'].items():
                         protocolname = k
                         protocolinfo = v  
                     apiurldevprofile = 'http://localhost:59881/api/v2/deviceprofile/name/'+device['profileName']
                     resp_devprofile=requests.get(apiurldevprofile)
                     device_profile = resp_devprofile.json()['profile']
                     
                     print(device_profile)
                         
                     if 'location' not in device:
                         device['location'] = 'Mysore'
                     if device['operatingState'] == "UP":
                         status = 'online'
                     else:
                         status = 'offline'
                     device_info = [
                         device['id'],
                         device_name,
                         v['Address'],
                         v['Port'], 
                         device['location'],
                         '',
                         device_profile['model'],
                         device_profile['manufacturer'],
                         device['profileName'],
                         device['serviceName'],
                         device['description'],
                         status,
                         'Provisioned',
                         'Default',
                         form_dt,
                         'Active',
                         form_dt_m,
                         '',
                         'Ubuntu 22.04',
                         'NA',
                         'Active',
                         '23.45.67',
                         'Active'                    
                     ]
                     devices_info.append(device_info)
             return devices_info                                                                    
         except Exception as e:
            return e

@iotd.route('/api/v1/name/getdeviceconfigdetails/all')
class DeviceDetailsConfig(Resource):
    '''List of IoT Device details for config'''
    @ns.doc('IoTDeviceDetailConfig')
    @cross_origin()
    @api.response(200,'Success..')
    @api.response(400,'Invalid input')
    @api.response(404,'Page Not Found')
    @api.response(500,'Internal Server Error')
    def get(self):
        '''Get the list of IoT Device detail for configuration'''
        unique_device_names = set()
        devices_info = []
        unique_gateway_names = set()
        try:  
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            print(response.json())
            p = response.json()['devices']
             #print(p)
             #print("next IP")
            for gp in p:
                gateway_name = gp['name']
                if gateway_name not in unique_gateway_names:  
                    unique_gateway_names.add(gateway_name)   
                    ip = '127.0.0.1'
                    port = '5000'
                    if 'protocols' in gp:
                        for k,v in gp['protocols'].items():
                            print(v)
                            if 'Address' in v:
                                ip = v['Address'] 
                            if 'Port' in v:
                                port = v['Port']   
                    print("printing IP")
                    print(ip)                                                     
                    apiurl2='http://'+ip+':59881/api/v2/device/all?limit=-1'
                    #print(apiurl2)
                    response2 = requests.get(apiurl2)
                    devicelist = response2.json()['devices']
                    for g in devicelist:
                        device_name = g['name']
                        #print(device_name)
                        if device_name not in unique_device_names:
                            unique_device_names.add(device_name)
                            #print(unique_device_names)
                            gatewayip = ip
                            gatewayport = port
                            pdata={}
                            if 'protocols' in g:
                                for k,v in g['protocols'].items():
                                    pdata=v
                                if 'Address' in pdata:
                                    gatewayip = pdata['Address']
                                if 'Port' in pdata:
                                    gatewayport = pdata['Port']
                            print(gatewayip)
                            print("\n")
                            status = ''
                            createdtime = g['created']
                            time_in_sec = createdtime / pow(10,9)
                            dt = datetime.fromtimestamp(time_in_sec)
                            form_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
                            #print(form_dt)
                            modifiedtime = g['modified']
                            time_in_sec_m = modifiedtime / pow(10,9)
                            dt_m = datetime.fromtimestamp(time_in_sec_m)
                            form_dt_m = dt_m.strftime('%Y-%m-%d %H:%M:%S')
                            apiurl3 = "http://"+gatewayip+":59881/api/v2/deviceprofile/name/"+g['profileName']
                            print(apiurl3)
                            res_devpro = requests.get(apiurl3)
                            manufacturername = res_devpro.json()['profile']['manufacturer']
                            print(manufacturername)
                            if g['operatingState'] == "UP":
                                status = 'online'
                            else:
                                status = 'offline'
                            device_info = {
                                    'IotDeviceID':g['id'],
                                    'IOTDeviceName':g['name'],
                                    'IPAddress':gatewayip,
                                    'PortNumber':gatewayport,
                                    'location':'Hyderabad',
                                    'AssociatedServiceProtocol':g['serviceName'],
                                    'AssociatedGatewayProfile':g['profileName'],
                                    'description':g['description'],
                                    'Status':status,
                                    'ProvisionedStatus':'provisioned',
                                    'ProvisionedMethod':'Default',
                                    'ProvisionedDateTime':form_dt,
                                    'ActiveInactive':'Active',
                                    'LastCommunicatedTime':form_dt_m
                                }
                            devices_info.append(device_info)
                            print(device_info)
                            print("\n")
            return devices_info
        except Exception as e:
            return str(e)

@iotd.route('/api/v1/<gatewayname>/telemetrydata/<devicename>')
class GatewayTelemetryDataDevice(Resource):
     '''Telemetry data for a particular device '''
     @ns.doc('TelemetryDataDevice')
     @api.param('gatewayname','Name of gateway to fetch data', type='string',required=True)
     @api.param('iotdevicename','Name of iotdevice to fetch data', type='string',required=True)
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self,gatewayname,devicename):
         '''Get the telemetry data for the device specified'''
         try:
            apiurl1 = "http://localhost:59881/api/v2/device/name/"+str(gatewayname)
            res = requests.get(apiurl1)
            g = res.json()['device']
            ip = '127.0.0.1'
            if 'protocols' in g:
               for k,v in g['protocols'].items():
                    if 'Address' in v:
                        ip = v['Address']
            apiurl2 = "http://"+ip+":5000/gatewaydata/api/v1/telemetrydata/"+str(devicename)
            res2 = requests.get(apiurl2)
            return res2.json()                                                                   
         except Exception as e:
             return e

@iotd.route('/api/v1/data/<gatewayname>/minmax/<devicename>')
class GatewayMinMaxdataDevice(Resource):
     '''Maximum and minimum data values for a particular device '''
     @ns.doc('MinMaxDevice')
     @cross_origin()
     @api.param('gatewayname','Name of gateway',type='string',required=True)
     @api.param('devicename','Name of device',type='string',required=True)
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self,gatewayname,devicename):
         '''Get the minimum and maximum data values for the device specified to render a slider'''
         try:
            apiurl1 = "http://localhost:59881/api/v2/device/name/"+str(gatewayname)
            res = requests.get(apiurl1)
            g = res.json()['device']
            ip = '127.0.0.1'
            if 'protocols' in g:
               for k,v in g['protocols'].items():
                    if 'Address' in v:
                        ip = v['Address']
            apiurl2 = "http://"+ip+":5000/gatewaydata/api/v1/data/minmax/"+str(devicename)
            res2 = requests.get(apiurl2)
            return res2.json()                                                                   
         except Exception as e:
             return e

@ns.route('/api/v1/count/gatewaywrtservice')
class GatewayWrtService(Resource):
     '''Gateway Details per device service '''
     @ns.doc('GatewayDetailsDeviceService')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the gateway details with respect to device service'''
         try:
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            devicelist = response.json()['devices']
            mp = {}
            cnt = 0
            for d in devicelist:
                if d['serviceName'] in mp:
                    mp[d['serviceName']] += 1
                else:
                    mp[d['serviceName']] = 1
            #print(mp)         
            return json.dumps(mp)                                                                
         except Exception as e:
             return e
             
@iotd.route('/api/v1/data/<gatewayname>/linegraph/<devicename>')
class GatewayLinegraphdataDevice(Resource):
     '''Data for Linegraph for a particular device '''
     @ns.doc('LinegraphDevice')
     @cross_origin()
     @api.param('devicename','Name of device',type='string',required=True)
     @api.param('gatewayname','Name of gateway',type='string',required=True)  
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self,gatewayname,devicename):
         '''Get the data for the device specified to plot line graph'''
         try:
            apiurl1 = "http://localhost:59881/api/v2/device/name/"+str(gatewayname)
            res = requests.get(apiurl1)
            g = res.json()['device']
            ip = '127.0.0.1'
            if 'protocols' in g:
               for k,v in g['protocols'].items():
                    if 'Address' in v:
                        ip = v['Address']
            apiurl2 = "http://"+ip+":5000/gatewaydata/api/v1/data/linegraph/"+str(devicename)
            res2 = requests.get(apiurl2)
            return res2.json()                                                                   
         except Exception as e:
             return e

@iotd.route('/api/v1/count/gatewaywrtservice')
class GatewayWrtService(Resource):
     '''Gateway Details per device service '''
     @ns.doc('GatewayDetailsDeviceService')
     @cross_origin()
     @api.response(200,'Success..')
     @api.response(400,'Invalid input')
     @api.response(404,'Page Not Found')
     @api.response(500,'Internal Server Error')
     def get(self):
         '''Get the gateway details with respect to device service'''
         try:
            apiurl = "http://localhost:59881/api/v2/device/all?limit=-1"
            response = requests.get(apiurl)
            devicelist = response.json()['devices']
            mp = {}
            cnt = 0
            for d in devicelist:
                ip = '127.0.0.1'
                if 'protocols' in d:
                    for k,v in d['protocols'].items():
                        if 'Address' in v:
                            ip = v['Address']
                apiurl2 = "http://"+ip+":59881/api/v2/device/all?limit=-1"   
                resp2 = requests.get(apiurl2)
                iotdevlist = resp2.json()['devices']
                for iotdev in iotdevlist:
                    if iotdev['serviceName'] in mp:
                       mp[iotdev['serviceName']] += 1
                    else:
                       mp[iotdev['serviceName']] = 1
            #print(mp)         
            return json.dumps(mp)                                                                
         except Exception as e:
             return e


if __name__ == '__main__':
    app.run('0.0.0.0',5000,debug = True)
