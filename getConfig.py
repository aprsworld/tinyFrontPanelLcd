# display imports
"""Module gets configuration from another resource."""
import json
import urllib


def getData(url):
    """Get data from a resource defined at the top of the file."""
    data = urllib.urlopen(url).read()
    output = json.loads(data)
    return output
