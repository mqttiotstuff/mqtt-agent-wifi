
#
# MQTT agent to measure the freebox wifi device emitting power
# permit to interpolate the device position
#

# 2020-11 migrating to python 3

import paho.mqtt.client as mqtt
import random
import time
import re
import configparser
import os.path

import sys
import traceback

config = configparser.RawConfigParser()


WIFI_ROOT = "home/agents/wifi"


import freebox
import json
import time
import string

import functools


#############################################################
## MAIN

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
   raise Exception("config file " + conffile + " not found")

config.read(conffile)

username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

client2 = mqtt.Client()

# client2 is used to send time oriented messages, without blocking the receive one
client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()

app_id = "fr.freebox.dom" 
j = json.load(open("result_auth"))
app_token = str(j["result"]["app_token"]) # freebox don't like unicode

f = freebox.FbxApp(app_id,app_token)

cnx_reconnect = 100

while True:
    time.sleep(1)
    try:
    # reconnect if needed
        cnx_reconnect = cnx_reconnect - 1
        if cnx_reconnect < 0:
            f = freebox.FbxApp(app_id,app_token)
            cnx_reconnect = 100

    # query the box
        for i in ['0','1']: 
            response = f.com("wifi/ap/" + i + "/stations") 
            ap = response['result']

            result = map(lambda x:(x['mac'],x['hostname'],x["signal"],x["rx_bytes"],x["tx_bytes"]), ap)
            for (mac,hostname,signal,rx,tx) in result:
                hostname = hostname.replace("+","_")
                client2.publish(WIFI_ROOT + "/hostname/" + hostname, str(signal))
                client2.publish(WIFI_ROOT + "/machostname/" + mac, str(hostname))
                client2.publish(WIFI_ROOT + "/mac/" + mac, str(signal))
                client2.publish(WIFI_ROOT + "/rx/" + mac, str(rx))
                client2.publish(WIFI_ROOT + "/tx/" + mac, str(tx))

            s = functools.reduce(lambda a,x: a+";"+str(x[0]), result,"")
            client2.publish(WIFI_ROOT + "/all",str(s))
            client2.loop(0.1)
    except Exception as e:
        traceback.print_exc();
        # continue


