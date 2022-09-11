
#
# Mqttagent that measure the existance of several wifi id,  
#
#
# 2020-11 : migrating to python 3



import paho.mqtt.client as mqtt
import random
import time
import re
import configparser
import os.path
import freebox
import json

import traceback

config = configparser.RawConfigParser()


PRESENCE = "home/agents/presence"
NET_CONNECT = "home/agents/netconnect"


#############################################################
## MAIN

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
   raise Exception("config file " + conffile + " not found")

config.read(conffile)


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

aliases = config.get("presence","aliases")
if not aliases:
   raise Exception("presence key not found")

aliases = json.loads(aliases)
print("aliases for presence :" + str(json.dumps(aliases)))


client2 = mqtt.Client()

# client2 is used to send events to wifi connection in the house 
client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()



# connect to freebox

app_id = "fr.freebox.dom" 
j = json.load(open("result_auth"))
app_token = str(j["result"]["app_token"]) # freebox don't like unicode


f = freebox.FbxApp(app_id,app_token)

def listActualConnectedDevices():

   apresponse = f.com("wifi/ap/")
   assert "result" in apresponse
   idlist = list(map(lambda x:x['id'],apresponse['result'])) 
   result = []
   for apid in idlist:
      # list connected devices
      stationsresponse = f.com("wifi/ap/" + str(apid) + "/stations/")
      if not 'result' in stationsresponse:
         print("no result in response : " + str(stationsresponse))
         continue
      ap = stationsresponse['result']
      print("station result :" + str(ap))
      # extract the mac / name
      couplelist = map(lambda x:(x['mac'],x['hostname']), ap)
      print("extracted mac, hostname couple") 
      print(result)
      result.extend(couplelist)

   return toHash(result)

def listDHCPHosts():
   response = f.com("dhcp/static_lease/")
   assert "result" in response
   idliststatic = list(map(lambda x:(x['mac'],x['ip']),response['result'])) 

   response = f.com("dhcp/dynamic_lease/")
   assert "result" in response
   idlistdyn = list(map(lambda x:(x['mac'],x['ip']),response['result'])) 
   l = idliststatic + idlistdyn
   return toHash(l)


def toHash(l):
   h = {}
   if not l is None:
      for (m,host) in l:
         h[m]= host
   return h

lastActivated = None

def sendWithAlias(m,host, state):
   if m in aliases:
      host = aliases[m]
   client2.publish(PRESENCE + "/" + host, str(state), qos=1, retain=True)

reconnect = 100

while True:
   try:
       time.sleep(3)
       reconnect = reconnect - 1
       if reconnect < 0:
          f = freebox.FbxApp(app_id,app_token) 
          reconnect = 100

       connected = listDHCPHosts()
       for k in connected:
           client2.publish(NET_CONNECT + "/" + connected[k], str(k), qos=1, retain=True)


       old = lastActivated
       lastActivated = listActualConnectedDevices()
       print("actuel elements :" + str(lastActivated))
       if old is not None:
          # compare the new and missing
          for k in lastActivated:
             if not (k in old):
                sendWithAlias(k, lastActivated[k],1)

          for k in old:
             if not (k in lastActivated):
                sendWithAlias(k, old[k],0)
       client2.publish(PRESENCE + "/WATCHDOG", 1) 

   except Exception:
       traceback.print_exc()

   



