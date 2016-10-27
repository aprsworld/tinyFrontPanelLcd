import getConfig
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
import getConfig
import validate
import sys
import os
import gc
from threading import Timer
from collections import defaultdict


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def clear(self):
        if self.size() == 0:
            return
        while self.size() > 1:
            self.pop()

class ResetableTimer:

    def __init__(self):
        self.timer = None

    def run(self, seconds):
        self.timer = Timer(seconds, self.callBack)
        self.timer.daemon = True
        self.timer.start()

    def reset(self, seconds):
        self.timer.cancel()
        self.run(seconds)

    def cancel(self):
        self.timer.cancel()

    def callBack(self):
        print "Default"


class ScreenSleepTimer(ResetableTimer):
    def callBack(self):
        global screenSleepFlag, disp
        if inView.editMode:
            pass
        else:
            dataUpdateTimer.cancel()
            screenSleepFlag = True
            print screenSleepFlag
            clear_screen()


class DataUpdateTimer(ResetableTimer):
    goback = False

    def drawAnts(self):
        global disp, n, maxn, Image, ImageDraw, draw, height, width, antOffSet

        if antOffSet < 12 and antOffSet > 0:
            if self.goback is False:
                antOffSet += 1
            else:
                antOffSet -= 1
        elif antOffSet >= 12:
            antOffSet = 11
            self.goback = True
        elif antOffSet <= 0:
            antOffSet = 1
            self.goback = False

    def callBack(self):
        global inView
        if screenSleepFlag or inView is None:
            pass
            self.run(updateLength)
        else:
            self.run(updateLength)
            inView.updateSelf()
            self.drawAnts()


class AutoVivification(dict):
    """
    Implementation of perl's autovivification feature.

    define tree data structure to make our life easier
    this allows for referencing keys in a dictionary that do not exists
    when referencing a non-existent key, it will create the key instead of throwing
    a key error
    """

    def __getitem__(self, item):
        """Override __getitem__."""
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def autoVivify(d):
    """
    Turn a regular dictionary into an AutoVivification dict.
    Args:
        d: is the dicionary to convert
    """
    if isinstance(d, dict):
        # recursive adaptation of child dictionary elements
        d = AutoVivification({k: autoVivify(v) for k, v in d.iteritems()})
    return d
# URLS for AJAX calls
URL = "http://localhost/piNetConfig/netconfig.php"
URL2 = "http://localhost/piNetConfig/netconfig.php"
URL3 = "http://localhost/piNetConfig/netconfig-scan.php"
LAYOUT_URL = "layout.json"
# initialize object that holds future incoming data
thisData = AutoVivification()
# load data into object
thisData.update(getConfig.getData(URL))
# make the config its own seperate object that is autovivified
thisConfig = thisData['config'] = autoVivify(thisData['config'])
# list of ethernet interfaces
ethernetInterfaces = list()
# list of wifi Interfaces
wifiInterfaces = list()
# masterList of screens used in old version, but not currently used
masterList = list()
# stack that we used to keep track of depth within menu structure
menuStack = Stack()
# current screen
screenChosen = None
# keeps track of top level menus
topLevelMenu = None
# variables to hold menu creation and deletion function for all files to access
menuCreate = None
menuDelete = None
# flag that keeps track of whether or not logo is being displayed
logoFlag = False
# global variable for keeping track of timeoutLength
timeOutLength = 30
# global variable that dictates time between current settings updates
updateLength = 1
# keeps track of whether the screen is asleep or not
screenSleepFlag = False
# dirty flag for keeping track of if the config has changed
configChangedFlag = False
# variables that allow access to timers
screenSleepTimer = ScreenSleepTimer()
dataUpdateTimer = DataUpdateTimer()
# dictionary that keeps track of interface settings
interfaceSettings = dict()
# list of wifi SSIDs and security that can be updated
wifiList = getConfig.getID_List(URL3)
# global variable so that end screen can be accessed by all files
endScreen = None
# global variable so that popSave screen (triggered by configChangedFlag) can be access by all files
popSave = None
# variable to hold udpated data
updatedData = AutoVivification()
antOffSet = 0

# OLED I2C display, 128x32 pixels
RST = 24
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
# Set up globals for drawing
width = disp.width
height = disp.height
print height

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
fillNum = 255
fillBg = 0
# Load default font.
font = ImageFont.load_default()
GPIO.setmode(GPIO.BCM)

# allow access to GPIO as input and turn on pull up resistors
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# global flags
action_up_now = False
action_select_now = False
action_down_now = False
action_screen_update = False
n = 0
inView = None

# dictionary that translates incoming data into human readable values
humanTranslations = {
    'method': 'Addressing Method',
    'dhcp': 'DHCP',
    'static': 'Static',
    'brd': 'Broadcast Address',
    'broadcast': 'Broadcast Address',
    'netmask': 'Netmask',
    'gateway': 'Gateway',
    'address': 'IP Address',
    'scope': 'Address Scope',
    'hwaddress': 'Hardware Address',
    'mtu': 'Maximum Trans Unit',
    'state': 'Link State',
    'mode': 'Mode',
    'qlen': 'Transmit Queue Length',
    'qdisc': 'Queueing Discipline',
    'group': 'Group',
    'ESSID': 'Extended SSID',
    'ssid': 'Wireless SSID',
    'RTS thr': 'RTS Threshold',
    'Framgent thr': 'Fragment Threshold',
    'securityType': 'Security Type',
    'wpa-ssid': 'WPA Wireless SSID',
    'wpa-psk': 'WPA Password',
    'ESSID': 'Current WIFI SSID',
    'dateAndTime': 'Date and Time',
    'magWebProStatus': 'MagWebPro Status',
    'mainSetupMenu': 'Main Setup Menu',
    'signallevel': 'Signal Level',
    'linkquality': 'Link Quality',
    'restartscript': 'Discard All Changes',
    'sendconfig': 'Save Changes/Reboot'
}

charSetIndex = 0
# charset for passwords
charSet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
           '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '$', '@', '^', '`', '|', '%', ';', '.', '~', '(', ')', '/', '{', '}',
           ':', '?', '[', ']', '=', '-', '+', '_', '#', '!', ' ']
# charset for WEP keys
charHexaSet = [' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
ipSet = ['.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
pingDict = {
    'type': 'ip',
    'address': '8.8.8.8',
    'numPackets': 4
}

def detect_edges(callbackFn):
    """designate threaded callbacks for all button presses."""
    GPIO.add_event_detect(17, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=callbackFn, bouncetime=400)

def screen_select(screenNum):
    """for changing screens."""
    global ip, lo, masterList

    # find and display the screen in the list based on our passed int value
    masterList[screenNum].displayThis()

def drawAndEnable():
    global screenChosen, action_screen_update, updateLength
    screenChosen.screens[screenChosen.childIndex].displayThis()
    screenChosen.screens[screenChosen.childIndex].editMode = False
    action_screen_update = False
    dataUpdateTimer.reset(updateLength)

def switchToWifiList():
    global screenChosen, action_screen_update, updateLength
    for idx, screen in enumerate(screenChosen.screens):
        if screenChosen.screens[idx].objectType == "ssidchooser":
            screenChosen.childIndex = idx
            menuStack.push(screenChosen)
            screenChosen = screenChosen.screens[screenChosen.childIndex]
            screenChosen.editMode = True
            screenChosen.navigation = screenChosen.editLine
            screenChosen.editVal(screenChosen.childIndex, 2)
            action_screen_update = False
            break
    else:
        global screenChosen, action_screen_update, updateLength
        screenChosen.screens[screenChosen.childIndex].displayThis()
        screenChosen.screens[screenChosen.childIndex].editMode = False
        action_screen_update = False
        dataUpdateTimer.reset(updateLength)

def draw_confirmation(line1, line2, line3, fillNum, fillBg):
    """for drawing an error."""
    global disp, n, maxn, Image, ImageDraw, draw, font, action_screen_update
    # Draw a black filled fox to clear the image.
    print 309
    action_screen_update = True
    draw.rectangle((0, 0, width - 1, height - 1), outline=1, fill=fillBg)
    print 311

    top = 2
    draw.rectangle((1, 0, width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((center_text(line1, 0), top), line1, font=font, fill=fillBg)
    draw.text((center_text(line2, 0), top + 9), line2, font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 18), line3, font=font, fill=fillNum)
    print 318

    disp.image(image.rotate(180))
    disp.display()
    print 326
    t = Timer(1.5, drawAndEnable)
    print 329
    t.setDaemon(True)
    t.start()
    print 331

def draw_wifi_conf(line1, line2, line3, fillNum, fillBg):
    """for drawing confirmation screen for wifi"""
    global disp, n, maxn, Image, ImageDraw, draw, font, action_screen_update
    # Draw a black filled fox to clear the image.
    print 309
    action_screen_update = True
    draw.rectangle((0, 0, width - 1, height - 1), outline=1, fill=fillBg)
    print 311

    top = 2
    draw.rectangle((1, 0, width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((center_text(line1, 0), top), line1, font=font, fill=fillBg)
    draw.text((center_text(line2, 0), top + 9), line2, font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 18), line3, font=font, fill=fillNum)
    print 318

    disp.image(image.rotate(180))
    disp.display()
    print 326
    t = Timer(1.5, switchToWifiList)
    print 329
    t.setDaemon(True)
    t.start()
    print 331

def clear_screen():
    draw.rectangle((-10, -10, width + 10, height + 10), outline=0, fill=fillBg)
    disp.image(image.rotate(180))
    disp.display()

def draw_screen_center(s, line2, line3, fillNum, fillBg):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw, font, antOffSet

    # Draw a black filled box to clear the image.
    draw.rectangle((-10, -10, width + 10, height + 10), outline=0, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 1, width - 1, top + 9), outline=1, fill=fillNum)
    draw.rectangle((0, 1, width - 1, 1), fill=0)
    draw.rectangle([(antOffSet * 10) + 1, 1, (antOffSet * 10) + 11, 1], fill=255)

    draw.text((center_text(s, 0), top), str(s), font=font, fill=fillBg)
    draw.text((center_text(line2, 0), top + 10), str(line2), font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 20), str(line3), font=font, fill=fillNum)

    disp.image(image.rotate(180))

    # disp.image(image)
    disp.display()

# function for drawing a screen - called by most screen objects within their displaythis() method
def draw_screen(s, line2, line3, fillNum, fillBg):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw, font, antOffSet
    # Draw a black filled box to clear the image.
    draw.rectangle((-10, -10, width + 10, height + 10), outline=0, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 1, width - 1, top + 9), outline=1, fill=fillNum)
    draw.rectangle((0, 1, width - 1, 1), fill=0)
    draw.rectangle([(antOffSet * 10) + 1, 1, (antOffSet * 10) + 11, 1], fill=255)

    draw.text((center_text(s, 0), top), str(s), font=font, fill=fillBg)
    draw.text((x, top + 10), str(line2), font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 20), str(line3), font=font, fill=fillNum)

    disp.image(image.rotate(180))

    # disp.image(image)
    disp.display()

# function for editing a screen - called by most screen objects within their editVal() method
def draw_screen_ul(s, line2, line3, fillNum, fillBg, underline_pos, underline_width):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw

    # Draw a black filled box to clear the image.
    draw.rectangle((-10, -10, width + 10, height + 10), outline=0, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 1, width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((center_text(s, 0), top), s, font=font, fill=fillBg)
    draw.text((x, top + 10), line2, font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 20), line3, font=font, fill=fillNum)

    draw.line([underline_pos * underline_width, 22, (underline_pos + 1) * underline_width - 1, 22], fill=255)

    disp.image(image.rotate(180))
    # disp.image(image)
    disp.display()

# centers text on a screen
def center_text(text, borderWidth):
    """Center text on the LCD Screen."""
    strlen = len(str(text)) * 6
    return (128 + borderWidth - strlen) / 2

# keeps a valid octet when adding and subtracting
def configureOctet(value, addAmt):
    """chooses what to display in an ip address' octet."""
    if(not value == 0):
        hunds = value - (value % 100)
        ones = value % 100 % 10
        if value < 100:
            tens = (value % 100) - ones
        else:
            tens = value % (hunds + ones)
    else:
        hunds = 0
        tens = 0
        ones = 0
    print hunds, tens, ones
    value = value + addAmt
    if(value > 255):
        if(addAmt == 100):
            value = 0 + tens + ones
        elif(addAmt == 10):
            value = 0 + ones
        else:
            value = 0
    elif(value < 0):
        if(addAmt == -100):
            if tens + ones > 55:
                value = 100 + tens + ones
            else:
                value = 200 + tens + ones
        elif(addAmt == -10):
            if ones >= 5:
                value = 250
            else:
                if(tens >= 50):
                    value = 250 + ones
                else:
                    value = 200 + tens + ones
        else:
            value = 255
    return value
