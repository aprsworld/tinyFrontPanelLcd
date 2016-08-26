# display imports
"""Module gets configuration from another resource."""
import json
import urllib
import urllib2

def getData(url):
    """Get data from a resource defined bu url."""
    data = urllib.urlopen(url).read()
    output = json.loads(data)
    return output

def sendConfig(url, data):
    """Send data to a resource defined by url."""
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps({"config":data}))
    print response.read()

def getID_List(url):
    """gets list of current ssids."""
    data = urllib.urlopen(url).read()
    output = json.loads(data)
    return output[output.keys()[0]].keys()
