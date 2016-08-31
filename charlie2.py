#screens
import Adafruit_SSD1306
import globalDependencies as gd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import PIL.ImageOps
import math
import RPi.GPIO as GPIO
import time
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as tdelta
import charlieimage
import getConfig
import validate
import sys
import os
import gc
import screens
from threading import Timer
from collections import defaultdict

layout = dict()
layout = getConfig.get_layout(gd.LAYOUT_URL)
layoutKeys = layout.keys()
masterList = gd.masterList
print gd.thisData.keys()
thisData = gd.thisData

print list(layout.keys())

def retrieveData(physical, logical, requestedData):
    global thisData
    dataDict = {
        "address": safeget(thisData, physical, logical, "inet", requestedData),
        "gateway": safeget(thisData, physical, logical, "inet", requestedData),
        "netmask": safeget(thisData, physical, logical, "inet", requestedData),
        "state": safeget(thisData, physical, requestedData)
    }
    return dataDict[requestedData]

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def createScreen(editable, title, screentype, value, interface):
    if screentype.lower() is "stringscreen":
        return screens.StringScreen(editable, title, value)
    elif screentype.lower() is "networkscreen":
        return screens.NetworkScreen(editable, title, value, interface)

def getInterfaceList():
    pass

def buildNetworkStatus():
    global masterList, layout
    networkStatusScreen = screens.Screen("subMenu", "Network Status", " ", "networkStatus")
    for item in layout["network-status"]["eth-iface"]:
        if isinstance(layout["network-status"]["eth-iface"][item], dict):
            for subItem in layout["network-status"]["eth-iface"][item]:
                if isinstance(layout["network-status"]["eth-iface"][item][subItem], dict):
                    pass
                else:
                    pass
        else:
            val = retrieveData("eth0", "eth0", item)
            res = layout["network-status"]["eth-iface"][item]
            createScreen(res[1], item, res[0], val, "eth0")
    return networkStatusScreen


def buildMagWebProStatus():
    global masterList, layout
    magWebProStatus = screens.Screen("subMenu", "MagWebPro Status", " ", "magWebProStatus")
    return magWebProStatus


def buildDateAndTime():
    global masterList, layout
    dateAndTime = screens.Screen("subMenu", "Date and Time", " ", "dateAndTime")
    return dateAndTime


def mainSetupMenu():
    global masterList, layout
    mainSetupMenu = screens.Screen("subMenu", "Main Setup", " ", "mainSetupMenu")
    return mainSetupMenu

if "network-status" in layoutKeys:
    masterList.append(buildNetworkStatus())

masterList[0].displayThis()
print retrieveData("eth0", "eth1", "address")
