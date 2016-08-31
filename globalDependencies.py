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

URL = "http://localhost/piNetConfig/netconfig.php"
URL2 = "http://localhost/piNetConfig/netconfig.php"
URL3 = "http://localhost/piNetConfig/netconfig-scan.php"
LAYOUT_URL = "layout.json"
thisData = AutoVivification()
thisData.update(getConfig.getData(URL))
thisConfig = thisData['config'] = autoVivify(thisData['config'])
ethernetInterfaces = list()
wifiInterfaces = list()
masterList = list()

# OLED I2C display, 128x32 pixels
RST = 24
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Set up globals for drawing
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

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
n = 0


humanTranslations = {
    'method': 'Addressing Method',
    'dhcp': 'DHCP',
    'static': 'Static',
    'brd': 'Broadcast',
    'broadcast': 'Broadcast',
    'netmask': 'Netmask',
    'gateway': 'Gateway',
    'address': 'IP Address',
    'scope': 'Address Scope',
    'hwaddress': 'Hardware Address',
    'mtu': 'Maximum Trans Unit',
    'state': 'State',
    'mode': 'Mode',
    'qlen': 'Transmit Queue Length',
    'qdisc': 'Queueing Discipline',
    'group': 'Group',
    'ESSID': 'Extended SSID',
    'RTS thr': 'RTS Threshold',
    'Framgent thr': 'Fragment Threshold',
    'securityType': 'Security Type',
    'wpa-ssid': 'WPA Wireless SSID',
    'wpa-psk': 'WPA Password',
    'ESSID': 'Current WIFI SSID'
}


def draw_screen(s, line2, line3, fillNum, fillBg):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw, font
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width + 10, height + 10), outline=0, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 0, width - 1, top + 9), outline=1, fill=fillNum)

    draw.text((center_text(s, 0), top), str(s), font=font, fill=fillBg)
    draw.text((x, top + 10), str(line2), font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 20), str(line3), font=font, fill=fillNum)

    disp.image(image.rotate(180))

    # disp.image(image)
    disp.display()


def center_text(text, borderWidth):
    """Center text on the LCD Screen."""
    strlen = len(str(text)) * 6
    return (128 + borderWidth - strlen) / 2
