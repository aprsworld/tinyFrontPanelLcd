#screens
import Adafruit_SSD1306
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
import globalDependencies as gd
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
level = 1
n = 0
wifiList = gd.wifiList
draw = gd.draw
font = gd.font
disp = gd.disp
print list(layout.keys())
menuStack = gd.menuStack
topLevelMenu = screens.Screen("topMenu", "Top Menu", "", "")

def button_callback(channel):
    """
    Two threaded callback functions.

    These run in another thread when our events are detected
    Args:
        channel: the button that was pressed
    """
    global thisData, disable, charSetIndex
    if gd.action_screen_update:
        print "sleeping"
        time.sleep(.1)
    if gd.action_up_now or gd.action_select_now or gd.action_down_now or gd.action_screen_update:
        print "simultaneous press", channel
        return
    print "button press"

    if(17 == channel):
        gd.action_up_now = True
    elif(18 == channel):
        gd.action_down_now = True
    elif(27 == channel):
        gd.action_select_now = True

    if channel == 17:
        if gd.screenChosen.editMode == True:
            gd.screenChosen.editVal(gd.screenChosen.childIndex, 1)
        else:
            if gd.screenChosen.childIndex == gd.screenChosen.valueLength:
                if not gd.screenChosen.type == topLevelMenu.type:
                    gd.screenChosen.setChildIndex(0)
                    gd.screenChosen = menuStack.pop()
                    draw_confirmation("End Reached", "Returning to", "parent menu.", gd.fillNum, gd.fillBg)
                else:
                    gd.screenChosen.childIndex = 0
                    gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()
            else:
                gd.screenChosen.childIndex += 1
                gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()
    elif channel == 18:
        if gd.screenChosen.editMode == True:
            gd.screenChosen.editVal(gd.screenChosen.childIndex, 0)
        else:
            if gd.screenChosen.childIndex == 0:
                if not gd.screenChosen.type == topLevelMenu.type:
                    gd.screenChosen.setChildIndex(0)
                    gd.screenChosen = menuStack.pop()
                    draw_confirmation("End Reached", "Returning to", "parent menu.", gd.fillNum, gd.fillBg)
                else:
                    gd.screenChosen.childIndex = gd.screenChosen.valueLength
                    gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()
            else:
                gd.screenChosen.childIndex -= 1
                gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()
    elif channel == 27:
        print gd.screenChosen.type
        if gd.screenChosen.type == "subMenu" or gd.screenChosen.type == "topMenu":
            print 97, gd.screenChosen.screens
            if hasattr(gd.screenChosen.screens[gd.screenChosen.childIndex], "screens") and len(gd.screenChosen.screens[gd.screenChosen.childIndex].screens) < 1:
                pass
            else:
                menuStack.push(gd.screenChosen)
                gd.screenChosen = gd.screenChosen.screens[gd.screenChosen.childIndex]
                print 112, gd.screenChosen.type
                if gd.screenChosen.type == "subMenu" or gd.screenChosen.type == "topMenu":
                    print 114, "sub"
                    gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()
                elif gd.screenChosen.type == "editable":
                    print 117, gd.screenChosen.editLine

                    print gd.screenChosen.title
                    gd.screenChosen.editMode = True
                    gd.screenChosen.navigation = gd.screenChosen.editLine
                    gd.screenChosen.editVal(gd.screenChosen.childIndex, 2)
                else:
                    gd.screenChosen = menuStack.pop()
        elif gd.screenChosen.type == "editable":
            print 117, gd.screenChosen.value
            if gd.screenChosen.editMode == True and (gd.screenChosen.screenType == "DateTimeScreen" or gd.screenChosen.screenType == "StringScreen" or gd.screenChosen.screenType == "NetworkScreen"):
                print True
                gd.screenChosen.childIndex += 1
                print gd.screenChosen.childIndex
                print gd.screenChosen.valueLength
            gd.screenChosen.editMode = True
            gd.screenChosen.navigation = gd.screenChosen.editLine
            gd.screenChosen.editVal(gd.screenChosen.childIndex, 2)
            if not gd.screenChosen.value == "Manual Entry" and (gd.screenChosen.childIndex > gd.screenChosen.valueLength or gd.screenChosen.screenType == "BooleanScreen"):
                print "else"
                gd.screenChosen.childIndex = 0
                gd.screenChosen.editMode = False
                gd.screenChosen.navigation = gd.screenChosen.incrLine
                gd.screenChosen.changeConfig()
                print thisData["config"]
                gd.screenChosen = menuStack.pop()
                draw_confirmation("S A V E D !", " Returning", "to previous menu.", gd.fillNum, gd.fillBg)
                # gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()
        elif gd.screenChosen.type == "readOnly":
            pass
    gd.action_up_now = False
    gd.action_select_now = False
    gd.action_down_now = False

def button_callback2(channel):
    """
    Two threaded callback functions.

    These run in another thread when our events are detected
    Args:
        channel: the button that was pressed
    """
    # allow access to our globals
    global disable, n, maxn, masterList, level, charSetIndex
    print "level: ", level

    # if a button is already pressed, return out of callback
    if gd.action_up_now or gd.action_select_now or gd.action_down_now:
        print "simultaneous press", channel
        return

    if(17 == channel):
        gd.action_up_now = True
    elif(18 == channel):
        gd.action_down_now = True
    elif(27 == channel):
        gd.action_select_now = True

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
                masterList[n].gd.screenChosen()
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
    gd.action_up_now = False
    gd.action_select_now = False
    gd.action_down_now = False

def retrieveData(physical, logical, requestedData):
    global thisData
    print 258, requestedData
    if physical.startswith("eth"):
        dataDict = {
            "address": safeget(thisData, physical, logical, "inet", requestedData),
            "method": safeget(thisData, "config", logical, "protocol", "inet", requestedData),
            "gateway": safeget(thisData, physical, logical, "inet", requestedData),
            "netmask": safeget(thisData, physical, logical, "inet", requestedData),
            "state": safeget(thisData, physical, requestedData),
            "hwaddress": safeget(thisData, physical, requestedData)
        }
    else:
        dataDict = {
            "address": safeget(thisData, physical, logical, "inet", requestedData),
            "gateway": safeget(thisData, physical, logical, "inet", requestedData),
            "method": safeget(thisData, "config", logical, "protocol", "inet", requestedData),
            "netmask": safeget(thisData, physical, logical, "inet", requestedData),
            "state": safeget(thisData, physical, requestedData),
            "ssid": safeget(thisData, physical, "wireless", "settings", "ESSID"),
            "password": safeget(thisData, "config", logical, "protocol", "inet", "wireless-key") or safeget(thisData, "config", logical, "protocol", "inet", "wpa-psk"),
            "securityType": safeget(wifiList, physical, safeget(thisData, physical, "wireless", "settings", "ESSID").replace('\"',''), "auth"),
            "hwaddress": safeget(thisData, physical, requestedData)
        }
    if requestedData == "ssid" or requestedData == "password":
        print 280, requestedData
        return safeget(dataDict, requestedData).replace('\"', '')
    elif requestedData == "method":
        result = safeget(dataDict, requestedData)
        if result is None:
            return "DHCP"
        else:
            return result
    else:
        return safeget(dataDict, requestedData)

def drawAndEnable():
    gd.screenChosen.screens[gd.screenChosen.childIndex].displayThis()

def draw_confirmation(line1, line2, line3, fillNum, fillBg):
    """for drawing an error."""
    global disp, n, maxn, Image, ImageDraw, draw, font
    # Draw a black filled fox to clear the image.
    print 309
    draw.rectangle((0, 0, gd.width - 1, gd.height - 1), outline=1, fill=fillBg)
    print 311

    top = 2
    draw.rectangle((1, 0, gd.width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((gd.center_text(line1, 0), top), line1, font=font, fill=fillBg)
    draw.text((gd.center_text(line2, 0), top + 9), line2, font=font, fill=fillNum)
    draw.text((gd.center_text(line3, 0), top + 18), line3, font=font, fill=fillNum)
    print 318

    disp.image(gd.image.rotate(180))
    disp.display()
    print 326
    t = Timer(1, drawAndEnable)
    print 329
    t.setDaemon(True)
    t.start()
    print 331


def createIfaceTitle(iface):
    if(iface.startswith("wlan")):
        return "Wireless (" + iface + ")"
    elif(iface.startswith("eth")):
        return "Ethernet (" + iface + ")"
    else:
        return iface


def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def createScreen(editable, title, screentype, value, interface):
    print screentype
    if editable.lower() == "readonly":
        editable = "readOnly"
    if screentype.lower() == "submenu":
        screentype = "subMenu"
    if screentype.lower() == "stringscreen":
        return screens.StringScreen(editable, title, value)
    elif screentype.lower() == "networkscreen":
        return screens.NetworkScreen(editable, title, value, interface)
    elif screentype.lower() == "submenu":
        return screens.Screen(screentype, title, value, interface)
    elif screentype.lower() == "securitychanger":
        gd.interfaceSettings[interface]["security"] = value
        print gd.interfaceSettings
        return screens.SecurityChanger(editable, title, interface, value)
    elif screentype.lower() == "ssidchooser":
        return screens.SsidChooser(editable, title, "", interface)
    elif screentype.lower() == "wificreds":
        return screens.WifiCreds(editable, title, value, interface)
    elif screentype.lower() == "methodscreen":
        gd.interfaceSettings[interface]["method"] = value
        print gd.interfaceSettings
        return screens.MethodScreen(editable, title, value, interface)
    elif screentype.lower() == "confsend":
        return screens.confSend(editable, title, value)
    elif screentype.lower() == "datetimescreen":
        return screens.DateTimeScreen(editable, title)

def getInterfaceList():
    global thisData
    interfaceList = list()
    for key in thisData.keys():
        if key.startswith("eth") or key.startswith("wlan"):
            if key.startswith("eth"):
                keyType = "eth-iface"
            elif key.startswith("wlan"):
                keyType = "wifi-iface"
            for subkey in thisData[key].keys():
                if subkey.startswith(key) and not subkey.endswith("secondary"):
                    interfaceList.append({"key": key, "subkey": subkey, "keyType": keyType})
    print 253, interfaceList
    return interfaceList

def buildNetworkStatus():
    global layout, topLevelMenu
    networkStatusScreen = screens.Screen("subMenu", "Network Status", " ", "networkStatus")
    iFaceList = getInterfaceList()
    for iface in iFaceList:
        newScreen = screens.Screen("subMenu", createIfaceTitle(iface["subkey"]), " ", iface["subkey"])
        print 366, iface
        for item in layout["network-status"][iface["keyType"]]:
            if isinstance(layout["network-status"][iface["keyType"]][item], dict):
                x = createScreen("", item, "subMenu", "", item)
                for subItem in layout["network-status"][iface["keyType"]][item]:
                    if isinstance(layout["network-status"][iface["keyType"]][item][subItem], dict):
                        pass
                    else:
                        val = retrieveData(iface["key"], iface["subkey"], subItem)
                        res = layout["network-status"][iface["keyType"]][item][subItem]
                        subscreen = createScreen(res[1], subItem, res[0], val, iface["key"])
                        x.appendScreenList(subscreen)
                newScreen.appendScreenList(x)
            else:
                val = retrieveData(iface["key"], iface["subkey"], item)
                res = layout["network-status"][iface["keyType"]][item]
                x = createScreen(res[1], item, res[0], val, iface["key"])
                newScreen.appendScreenList(x)
                print newScreen.screens
        networkStatusScreen.appendScreenList(newScreen)
    print networkStatusScreen.screens
    return networkStatusScreen


def buildMagWebProStatus():
    global masterList, layout
    magWebProStatus = screens.Screen("subMenu", "MagWebPro Status", " ", "magWebProStatus")
    return magWebProStatus


def buildDateAndTime():
    global layout, topLevelMenu
    dateAndTime = screens.DateTimeScreen("readOnly", "Date and Time")
    return dateAndTime


def buildTools():
    global layout, topLevelMenu
    toolsScreen = screens.Screen("subMenu", "Tools", " ", "tools")
    for item in layout["tools"]:
        res = layout["tools"][item]
        x = createScreen(res[1], item, res[0], "", "")
        toolsScreen.appendScreenList(x)
    return toolsScreen

def buildMainSetupMenu():
    global masterList, layout
    iFaceList = getInterfaceList()
    mainSetupMenu = screens.Screen("subMenu", "Main Setup Menu", " ", "mainSetupMenu")
    toplevel = "mainSetupMenu"
    for key in layout["mainSetupMenu"].keys():
        if key.lower() == "allowwebconfig":
            mainSetupMenu.appendScreenList(screens.BooleanScreen("editable", "Allow Web Configuration", "Allow", "Allow", "Don't Allow"))
        elif key.lower() == "settime":
            mainSetupMenu.appendScreenList(screens.DateTimeScreen("editable", "Edit Date and Time"))
        elif key.lower() == "network-setup":
            networkSettings = createScreen("", "Network Setup", "submenu", "", "Network Setup")
            for iface in iFaceList:
                gd.interfaceSettings[iface["subkey"]] = dict()
                newScreen = screens.Screen("subMenu", createIfaceTitle(iface["subkey"]), " ", iface["subkey"])
                for item in layout[toplevel]["network-setup"][iface["keyType"]]:
                    if isinstance(layout[toplevel]["network-setup"][iface["keyType"]][item], dict):
                        x = createScreen("", item, "subMenu", "", item)
                        for subItem in layout["network-status"][iface["keyType"]][item]:
                            if isinstance(layout["network-status"][iface["keyType"]][item][subItem], dict):
                                pass
                            else:
                                val = retrieveData(iface["key"], iface["subkey"], subItem)
                                res = layout["network-status"][iface["keyType"]][item][subItem]
                                subscreen = createScreen(res[1], subItem, res[0], val, iface["key"])
                                x.appendScreenList(subscreen)
                        newScreen.appendScreenList(x)
                    else:
                        val = retrieveData(iface["key"], iface["subkey"], item)
                        res = layout[toplevel]["network-setup"][iface["keyType"]][item]
                        x = createScreen(res[1], item, res[0], val, iface["key"])
                        newScreen.appendScreenList(x)
                        print newScreen.screens
                networkSettings.appendScreenList(newScreen)
            mainSetupMenu.appendScreenList(networkSettings)
    return mainSetupMenu

if "network-status" in layoutKeys:
    topLevelMenu.appendScreenList(buildNetworkStatus())
if "magWebProStatus" in layoutKeys:
    topLevelMenu.appendScreenList(buildMagWebProStatus())
if "dateAndTime" in layoutKeys:
    topLevelMenu.appendScreenList(buildDateAndTime())
if "tools" in layoutKeys:
    topLevelMenu.appendScreenList(buildTools())
if "mainSetupMenu" in layoutKeys:
    topLevelMenu.appendScreenList(buildMainSetupMenu())

topLevelMenu.screens[0].displayThis()
gd.screenChosen = topLevelMenu
maxn = len(masterList) - 1


def detect_edges(callbackFn):
    """designate threaded callbacks for all button presses."""
    GPIO.add_event_detect(17, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=callbackFn, bouncetime=300)

detect_edges(button_callback)
print wifiList
try:
    raw_input("Press Enter to quit\n>")

except KeyboardInterrupt:
    GPIO.cleanup()	   # clean up GPIO on CTRL+C exit

print "done"
GPIO.cleanup()		   # clean up GPIO on normal exit
gd.draw_screen('Program ended', "", "", 200, 0)
