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
action_up_now = gd.action_up_now
action_select_now = gd.action_select_now
action_down_now = gd.action_select_now
level = 1
n = 0

print list(layout.keys())

def button_callback(channel):
    """
    Two threaded callback functions.

    These run in another thread when our events are detected
    Args:
        channel: the button that was pressed
    """
    # allow access to our globals
    global disable, action_up_now, action_select_now, action_down_now, n, maxn, masterList, level, charSetIndex
    print "level: ", level

    # if a button is already pressed, return out of callback
    if action_up_now or action_select_now or action_down_now:
        print "simultaneous press", channel
        return

    if(17 == channel):
        action_up_now = True
    elif(18 == channel):
        action_down_now = True
    elif(27 == channel):
        action_select_now = True

    # level 1 in tree - we display the top level screens here
    if (level == 1):
        if (17 == channel):
            if (n == maxn):
                n = 0
            else:
                n = n + 1
            gc.screen_select(n)
        elif (18 == channel):
            if (n == 0):
                n = maxn
            else:
                n = n - 1
            gc.screen_select(n)
        elif (27 == channel):
            if(masterList[n].type == 'readOnly'):
                print "Not a selectable screen!"
                masterList[n].colorInvert()
            else:
                level = 2
                masterList[n].screenChosen()
    elif (level == 2):
        # level 2 in tree - we display sub-screens
        if(masterList[n].type == "subMenu" or masterList[n].type == "readOnly"):
            print(masterList[n].type)
            print(masterList[n].screens[0].type)
            if(channel == 17):
                masterList[n].childIndex = masterList[n].childIndex + 1
                if(masterList[n].childIndex > len(masterList[n].screens) - 1):
                    masterList[n].displayThis()
                    level = 1
                else:
                    masterList[n].screens[masterList[n].childIndex].displayThis()
            elif(channel == 18):
                masterList[n].childIndex = masterList[n].childIndex - 1
                if(masterList[n].childIndex < 0):
                    masterList[n].displayThis()
                    level = 1
                else:
                    masterList[n].screens[masterList[n].childIndex].displayThis()
            elif(channel == 27):
                if(masterList[n].screens[masterList[n].childIndex].type == "editable"):
                    level = 3
                    masterList[n].screens[masterList[n].childIndex].setChildIndex(0)
                    masterList[n].screens[masterList[n].childIndex].navigation = masterList[n].screens[masterList[n].childIndex].editLine
                    masterList[n].screens[masterList[n].childIndex].displayEdit(masterList[n].screens[masterList[n].childIndex].childIndex, 6)
                else:
                    gc.draw_warning("This Screen ", "cannot be editted. ", 255, 0, masterList[n].screens[masterList[n].childIndex])
        else:
            print(masterList[n].type)
    elif (level == 3):
        # level 3 in screen scrolling
        this = masterList[n].screens[masterList[n].childIndex]
        curIndex = this.childIndex
        if(channel == 17):
            this.editVal(this.childIndex, 1)
        elif(channel == 18):
            this.editVal(this.childIndex, 0)
        elif(channel == 27):
            print this.value, this.childIndex, this.valueLength
            if(curIndex < this.valueLength and "BooleanScreen" != this.screenType and "ListScreen" != this.screenType):
                this.childIndex = this.childIndex + 1
                this.editVal(this.childIndex, 2)
                charSetIndex = 0
            elif "confScreen" == this.screenType:
                this.navigation = this.incrLine
            else:
                this.edit = False
                this.childIndex = 0
                if(hasattr(this, 'interface') or this.screenType == "ListScreen") or this.screenType == "StringScreen":
                    this.changeConfig()
                this.navigation = this.incrLine
                this.displayThis()
                conf = this.getConfirmation()
                print conf
                gc.draw_confirmation(conf['line1'], conf['line2'], 255, 0, masterList[n].screens[masterList[n].childIndex])
                level = 2

    print(channel)
    action_up_now = False
    action_select_now = False
    action_down_now = False

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
    print screentype
    if screentype.lower() == "stringscreen":
        return screens.StringScreen(editable, title, value)
    elif screentype.lower() == "networkscreen":
        return screens.NetworkScreen(editable, title, value, interface)


def getInterfaceList():
    pass

def buildNetworkStatus():
    global masterList, layout
    networkStatusScreen = screens.Screen("subMenu", "Network Status", " ", "networkStatus")
    eth0 = screens.Screen("subMenu", "ethernet(eth0)", " ", "eth0")
    networkStatusScreen.screens.append(eth0)
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
            x = createScreen(res[1], item, res[0], val, "eth0")
            eth0.screens.append(x)
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
maxn = len(masterList) - 1


def detect_edges(callbackFn):
    """designate threaded callbacks for all button presses."""
    GPIO.add_event_detect(17, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=callbackFn, bouncetime=400)

detect_edges(button_callback)

try:
    raw_input("Press Enter to quit\n>")

except KeyboardInterrupt:
    GPIO.cleanup()	   # clean up GPIO on CTRL+C exit

print "done"
GPIO.cleanup()		   # clean up GPIO on normal exit
gd.draw_screen('Program ended', "", "", 200, 0)
