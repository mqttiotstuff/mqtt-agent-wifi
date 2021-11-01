#
# This script, connect to the freebox and use the freebox api
#
#

# migrated to python 3

import urllib,hmac,json,hashlib,time

class FbxCnx:
    def __init__(self,host="192.168.4.254"):
        self.host=host

    def register(self,appid,appname,devname):
        data={"app_id": appid,"app_name": appname,"device_name": devname}
        r=self._com("login/authorize/",data)["result"]
        trackid,token=r["track_id"],r["app_token"]
        s="pending"
        while s=="pending":
            s=self._com("login/authorize/%s"%trackid)["result"]["status"]
            time.sleep(1)
        return s=="granted" and token

    def _httpcall(self,rooturl,data=None,headers={}):
        assert rooturl.startswith('/')
        url = "http://"+self.host + rooturl
        if data: 
            data = json.dumps(data)
            data = bytearray(data.encode('utf-8'))

       
        request = urllib.request.Request(url,data,headers)
        with urllib.request.urlopen(request) as result:
            content = result.read()
            content = content.decode()
            return json.loads(content)


    def _com(self,freeboxmethod,data=None,headers={}):
        return self._httpcall("/api/v8/"+freeboxmethod, data, headers)

    def _mksession(self):
        challenge=self._com("login/")["result"]["challenge"]
        b = challenge.encode('utf-8')
        t = self.token.encode('utf-8')
        data={
          "app_id": self.appid,
          "password": hmac.new( bytearray(t), bytearray(b),hashlib.sha1).hexdigest()
        }
        return self._com("login/session/",data)["result"]["session_token"]

class FbxApp(FbxCnx):
    def __init__(self,appid,token,session=None,host="192.168.4.254"):
        FbxCnx.__init__(self,host)
        self.appid,self.token=appid,token
        self.session=session if session else self._mksession()
    def version(self):
        response = self._httpcall("/api_version")
        if 'api_version' in response:
            return response['api_version']
        raise Exception("cannot read the api version information, api_version is no longer in payload")

    def com(self,method,data=None):
        return self._com(method,data,{"X-Fbx-App-Auth": self.session})

    def dir(self,path='/Disque dur/'):
        return self.com( "fs/ls/" + path.encode("base64") )


