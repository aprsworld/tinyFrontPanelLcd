# display imports
"""Module gets configuration from another resource."""
import json
import urllib
import urllib2
import collections
import globalDependencies
from collections import OrderedDict
def getData(url):
    """Get data from a resource defined bu url."""
    data = urllib.urlopen(url).read()
    output = json.loads(data)
    return output

def orderIface(data):
    print data
    print "         "
    for interface in data:
        if interface.startswith("wlan"):
            if data[interface].get("protocol", False) is not False:
                if data[interface]["protocol"].get("inet", False) is not False:
                    mydict = data[interface]["protocol"].get("inet")
                    mydict = collections.OrderedDict(sorted(mydict.iteritems()))
                    data[interface]["protocol"]["inet"] = mydict
    print data

def sendConfig(url, data):
    """Send data to a resource defined by url."""
    orderIface(data)
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps({"config":data}))
    print response.read()

def checkForInterfaces(url, interfaceList):
    """checks current interface list against interfaces in currentsettings.

    Returns list of interfaces that need to be implemented
    """
    checkData = getData(url)
    keyList = []
    for k in checkData.keys():
        if k in interfaceList:
            pass
        else:
            keyList.append(k)
    return {"keys": keyList, "newData": checkData}

def hasKeys(ssidListGlobal):
    if(len(ssidListGlobal) > 0):
        ssids = ssidListGlobal[ssidListGlobal.keys()[0]].keys()
    else:
        ssids = ['none in range']
    return ssids

def getID_List(url):
    """gets list of current ssids."""
    data = urllib.urlopen(url).read()
    output = json.loads(data)
    return output
    # output[output.keys()[0]].keys()

def get_layout2(url):
    with open(url) as json_data:
        print json_data
        d = json.load(json_data)
        return d

def get_layout(url):
    data = urllib.urlopen(url).read()
    d = json.load(open(url), object_pairs_hook=OrderedDict)
    return d
