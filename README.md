

# Python Mqtt agent, publishing freebox connection informations

This permit to :
- Make integrity checks on connected devices / stations
- Measures the network activity for childrens, and raise alarms
- Be aware of people in the location of the Wifi State (presence) 

## prerequisis

- mqtt-paho library
- python 3


## published topics


![](images/topics_illustration.png)


## Authentication notes

launch the command to renew the token :

 curl -d @content http://mafreebox.freebox.fr/api/v4/login/authorize/ > result_auth

click on the button on the freebox

take the trackid in json

 curl http://mafreebox.freebox.fr/api/v3/login/authorize/5  > authorize_result



