
#
# Integration test for freebox service in dom
#     using this url for api description : http://dev.freebox.fr/sdk/os/wifi/
#     reuse the code for freebox connection : http://www.manatlan.com/blog/freeboxv6_api_v3_avec_python
#
#

import freebox
import json

# read the authorize_result file

app_id = "fr.freebox.dom" 
j = json.load(open("result_auth"))
app_token = str(j["result"]["app_token"]) # freebox don't like unicode

# print app_token


f = freebox.FbxApp(app_id,app_token)

print (f.dir())

def listActualConnectedDevices():
    # list connected devices
    ap = f.com("wifi/ap/0/stations")['result']
    # extract the mac / name
    couplelist = map(lambda x:(x['mac'],x['hostname']), ap)
    return couplelist


# nintendo yann : (u'9C:E6:35:ED:CF:7A', u'Nintendo 3DS')
# nintendo quentin : (u'E0:0C:7F:69:41:02', u'Nintendo 3DS')
# tel pfr : (u'24:4B:81:C3:B9:9B', u'android-c3aa00f846d21a05')
# tel corinne :  (u'50:F0:D3:D9:81:8C', u'android-d244f64c376175fa')


 
