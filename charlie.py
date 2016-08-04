# display imports
"""This module outputs to an lcd screen."""
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
from threading import Timer

# URL that we are getting data from
URL = "http://localhost/piNetConfig/current_settings.php"

LOGO_DISPLAY_TIME = 1
editableSet = ['gateway', 'address', 'netmask']
charSet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

charSetPass = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

charSetIndex = 0
thisData = getConfig.getData(URL)
inView = ""

# global flag that determines level of "Directory" that we are on
level = 1

# starting time to display on unit
thisTime = time.strftime("%Y-%m-%d %H:%M:%S")

# global flag for when logo should stop displaying
ready = False


def setReady():
    """Simple method that is called when program is ready."""
    global ready
    ready = True

# timer to change screen once device is ready
Timer(LOGO_DISPLAY_TIME, setReady).start()
charlieimage.dispLogo()

# pauses program while stuff is being set up
while(not ready):
    # do nothing
    pass


def print_time():
    """update the value of the time screen print_some_times calls this every second."""
    global timeScreen
    print_some_times()
    timeScreen.value = time.strftime("%Y-%m-%d %H:%M:%S")
    # If we are on the time screen, update the screen every second as well
    if(masterList[n].title == "Time and Date"):
        # masterList[n].displayThis()
        pass


def print_some_times():
    """call print_time every second."""
    try:
        t = Timer(1, print_time)
        t.daemon = True
        t.start()
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting threads.\n'
        return


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
disable = False
n = 0


# now we'll define two threaded callback functions
# these will run in another thread when our events are detected
def button_callback(channel):
    """two threaded callback functions."""
    # allow access to our globals
    global disable, action_up_now, action_select_now, action_down_now, n, maxn, masterList, level, charSetIndex
    print "level: ", level

    # if a button is already pressed, return out of callback
    if action_up_now or action_select_now or action_down_now or disable:
        print "similtaneous press", channel
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
            screen_select(n)
        elif (18 == channel):
            if (n == 0):
                n = maxn
            else:
                n = n - 1
            screen_select(n)
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
                    draw_warning("This Screen ", "cannot be editted. ", 255, 0, masterList[n].screens[masterList[n].childIndex])
                    level = 4
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
            if(curIndex < this.valueLength and "BooleanScreen" != this.screenType):
                this.childIndex = this.childIndex + 1
                this.editVal(this.childIndex, 2)
                charSetIndex = 0
            elif "confScreen" == this.screenType:
                this.navigation = this.incrLine
            else:
                this.edit = False
                this.childIndex = 0
                if(hasattr(this, 'interface')):
                    this.changeConfig()
                this.navigation = this.incrLine
                this.displayThis()
                disable = True
                draw_confirmation(this.title + " has been", "saved to config", 255, 0, masterList[n].screens[masterList[n].childIndex])
                disable = False
                level = 4
    elif(level == 4):
        print "got here"
        this = masterList[n].screens[masterList[n].childIndex]
        level = 2
        if(channel == 17):
            this.displayThis()
        elif(channel == 18):
            this.displayThis()
        elif(channel == 27):
            this.displayThis()

    print(channel)
    action_up_now = False
    action_select_now = False
    action_down_now = False


# detect button falling edges
def detect_edges(callbackFn):
    """designate threaded callbacks for all button presses."""
    GPIO.remove_event_detect(17)
    GPIO.remove_event_detect(18)
    GPIO.remove_event_detect(27)
    GPIO.add_event_detect(17, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=callbackFn, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=callbackFn, bouncetime=300)


class Screen:
    """Our screen class."""

    navLine = "<--    Select    -->"
    incrLine = "<--    Edit    -->"
    editLine = "(-)     Next     (+)"

    def __init__(self, type, title, value, interface):
        """Our initialization for the screen class."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "GeneralScreen"
        self.interfaceType = interface
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.value = value
        self.childIndex = 0
        self.screens = []
        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine
        self.underline_pos = 0
        self.underline_width = 0
        self.edit = False

    def initScreenList(self, screens):
        """Initialize the submenus for this screen."""
        self.screens = screens

    def displayThis(self):
        """Draw our screen."""
        global inView
        inView = self
        draw_screen(self.title, self.value, self.navigation, 255, 0)

    def displayEdit(self, underline_pos, underline_width):
        """screen to display when editting value."""
        draw_screen_ul(self.title, self.value, self.navigation, 255, 0, underline_pos, underline_width)

    def colorInvert(self):
        """Flash screen to symbolize error."""
        draw_screen(self.title, self.value, self.navigation, 255, 0)
        time.sleep(.05)
        draw_screen(self.title, self.value, self.navigation, 0, 255)
        time.sleep(.05)
        draw_screen(self.title, self.value, self.navigation, 255, 0)
        time.sleep(.05)
        draw_screen(self.title, self.value, self.navigation, 0, 255)
        time.sleep(.05)
        draw_screen(self.title, self.value, self.navigation, 255, 0)

    def setChildIndex(self, value):
        """set child index of screen.

        Child index is used to determine what subscreen we are on
        """
        self.childIndex = value

    def screenChosen(self):
        """Screen is chosen - sets child index to zero and displays first child."""
        print("screenChosen " + self.title)
        self.childIndex = 0
        self.screens[self.childIndex].displayThis()

    def changeType(self, type, navigation):
        self.type = type
        self.navigation = navigation

# --------------------End of Screen Class Definition -----------------------


class NetworkScreen(Screen):
    """A networking screen class. Extends Screen."""

    def __init__(self, type, title, addr, interface):
        """
        Our initialization for the screen class.

           addr0 represents addr0.xxx.xxx.xxx in a network Address
           addr1 represents xxx.addr1.xxx.xxx in a network Address
           addr2 represents xxx.xxx.addr2.xxx in a network Address
           addr3 represents xxx.xxx.xxx.addr3 in a network Address

           This is done so that the network address can easilly be editted
        """
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "NetworkScreen"
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        addr = addr.split(".")
        self.addr0 = addr0 = int(addr[0])
        self.addr1 = addr1 = int(addr[1])
        self.addr2 = addr2 = int(addr[2])
        self.addr3 = addr3 = int(addr[3])
        self.value = self.formatAddr(str(addr0)) + "." + self.formatAddr(str(addr1)) + "." + self.formatAddr(str(addr2)) + "." + self.formatAddr(str(addr3))
        self.childIndex = 0
        self.valueLength = 11
        self.edit = False
        self.interface = interface

        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, addrNum, addorsub):
        """Edit the value of a network screen.

        addrNum is the digit within the address that we are editing
        addorsub determines whether we are adding or subtracting
        """
        # find ammount we need to add based on index passed
        addAmt = 1
        print("addrnum: " + str(addrNum))
        if(addrNum == 0 or addrNum == 3 or addrNum == 6 or addrNum == 9):
            addAmt = 100
        elif(addrNum == 1 or addrNum == 4 or addrNum == 7 or addrNum == 10):
            addAmt = 10
        else:
            addAmt = 1
        print(addAmt)
        # switch to subtraction
        if(addorsub == 0):
            addAmt = addAmt * -1
        if(addorsub == 2):
            addAmt = 0
        # ___.xxx.xxx.xxx
        if(addrNum <= 2):
            self.addr0 = configureOctet(self.addr0, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum, 6)
        # xxx.___.xxx.xxx
        elif(addrNum <= 5):
            self.addr1 = configureOctet(self.addr1, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 1, 6)
        # xxx.xxx.___.xxx
        elif(addrNum <= 8):
            self.addr2 = configureOctet(self.addr2, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 2, 6)
        # xxx.xxx.xxx.___
        elif(addrNum <= 11):
            self.addr3 = configureOctet(self.addr3, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 3, 6)
        # append everything into a network address string so that it can be shown on screen
        print(self.value)

    def getVal(self, addrNum):
        """get the val of the specified octet."""
        if(addrNum == 0):
            return self.addr0
        elif(addrNum == 1):
            return self.addr1
        elif(addrNum == 2):
            return self.addr2
        elif(addrNum == 3):
            return self.addr3

    def formatAddr(self, address):
        """append spaces on to beginning of addresses."""
        length = len(address)
        for x in range(length, 3):
            address = " " + address
        return address

    def changeConfig(self):
        """Change the setting in the config so that we can send it to piNetConfig."""
        global thisData
        thisData['config'][self.interface]['protocol']['inet'][self.title] = str(self.addr0)+"."+str(self.addr1)+"."+str(self.addr2)+"."+str(self.addr3)
        print thisData['config']


# --------------------End of NetworkScreen Class Definition -----------------------
class StringScreen(Screen):
    """Class for a screen with a string value. Extends String."""

    def __init__(self, type, title, value):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "StringScreen"
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.valueLength = 18
        self.edit = False

        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        global charSet, charSetIndex
        if(charSetIndex > len(charSet) - 1):
            charSetIndex = 0
        if(charSetIndex < 0):
            charSetIndex = len(charSet) - 1
        if(addorsub == 0):
            addAmt = -1
        elif(addorsub == 2):
            self.displayEdit(index, 6)
            return
        else:
            addAmt = 1
        charSetIndex = charSetIndex + addAmt

        char = charSet[charSetIndex]
        word = self.value
        word = word[:index] + char + word[index + 1:]
        self.value = word
        self.displayEdit(index, 6)

# --------------------End of StringScreen Class Definition -----------------------


class DateTimeScreen(Screen):
    """Class for dateTime screens. Extends Screen."""

    def __init__(self, type, title):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "DateTimeScreen"

        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.date = dt.now()
        self.value = self.date.strftime("%Y-%m-%d %H:%M:%S")
        self.valueLength = 5
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.second = 0
        self.minute = 0
        self.edit = False

        self.timeChange = tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)
        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine
        self.print_some_times()

    def editVal(self, index, addorsub):
        """edit val of screen with new data."""
        global draw
        self.edit = True
        if(index == 0):
            self.editYear(addorsub)
            self.underline_pos = 0
            self.underline_width = 24
        elif(index == 1):
            self.editMonth(addorsub)
            self.underline_pos = 2.5
            self.underline_width = 12
        elif(index == 2):
            self.editDay(addorsub)
            self.underline_pos = 4
            self.underline_width = 12
        elif(index == 3):
            self.editHour(addorsub)
            self.underline_pos = 5.5
            self.underline_width = 12
        elif(index == 4):
            self.editMinute(addorsub)
            self.underline_pos = 7
            self.underline_width = 12
        elif(index == 5):
            self.editSecond(addorsub)
            self.underline_pos = 8.5
            self.underline_width = 12
        self.timeChange = tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)
        self.date = dt.now() + self.timeChange
        self.value = self.date.strftime("%Y-%m-%d %H:%M:%S")
        self.displayEdit(self.underline_pos, self.underline_width)

    def print_time(self):
        """update the value of the time screen print_some_times calls this every second."""
        global timeScreen, masterList
        self.print_some_times()
        self.date = dt.now() + self.timeChange
        self.value = self.date.strftime("%Y-%m-%d %H:%M:%S")
        # If we are on the time screen, update the screen every second as well
        if(inView.title == self.title):
            if(self.edit):
                self.displayEdit(self.underline_pos, self.underline_width)
            else:
                self.displayThis()

    def print_some_times(self):
        """call print_time every second."""
        try:
            t = Timer(1, self.print_time)
            t.daemon = True
            t.start()
        except (KeyboardInterrupt, SystemExit):
            print '\n! Received keyboard interrupt, quitting threads.\n'
            return

    def editYear(self, addorsub):
        """edit year of value on screen."""
        print(self.year)
        if(addorsub == 0):
            self.year = self.year - 1
        elif(addorsub == 1):
            self.year = self.year + 1
        else:
            print('else')

    def editMonth(self, addorsub):
        """edit month of value on screen."""
        if(addorsub == 0):
            self.month = self.month - 1
        elif(addorsub == 1):
            self.month = self.month + 1
        else:
            print('else')

    def editDay(self, addorsub):
        """edit day of value on screen."""
        if(addorsub == 0):
            self.day = self.day - 1
        elif(addorsub == 1):
            self.day = self.day + 1
        else:
            print('else')

    def editHour(self, addorsub):
        """edit hour of value on screen."""
        if(addorsub == 0):
            self.hour = self.hour - 1
        elif(addorsub == 1):
            self.hour = self.hour + 1
        else:
            print('else')

    def editMinute(self, addorsub):
        """edit minute of value on screen."""
        if(addorsub == 0):
            self.minute = self.minute - 1
        elif(addorsub == 1):
            self.minute = self.minute + 1
        else:
            print('else')

    def editSecond(self, addorsub):
        """edit Second of value on screen."""
        if(addorsub == 0):
            self.second = self.second - 1
        elif(addorsub == 1):
            self.second = self.second + 1
        else:
            print('else')


# ------------------End of DateTimeScreen Class Definition ---------------------
class BooleanScreen(Screen):
    """Class for true/false options screens. Extends Screen."""

    def __init__(self, type, title, value, val0, val1):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "BooleanScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.val0 = val0
        self.val1 = val1
        self.editLine = self.val0 + "< Confirm >" + self.val1
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        if(addorsub == 0):
            self.value = self.val0
        elif(addorsub == 1):
            self.value = self.val1
        elif(addorsub == 2):
            self.value = self.value
        self.displayThis()


# ------------------End of BooleanScreen Class Definition ---------------------
class MethodScreen(Screen):
    """Class for true/false options screens. Extends Screen."""

    def __init__(self, type, title, value, val0, val1):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "BooleanScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.val0 = val0
        self.val1 = val1
        self.editLine = self.val0 + "< Confirm >" + self.val1
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        print ":test"
        if(addorsub == 0):
            self.value = self.val0
            thisData['config'][masterList[n].interfaceType]['protocol']['inet']['method'] = self.value
            for childScreen in masterList[n].screens:
                if childScreen.screenType == 'NetworkScreen' and childScreen.title in editableSet:
                    print childScreen.type
                    if(self.value == self.val0):
                        childScreen.changeType("editable", self.incrLine)
                    elif(self.value == self.val1):
                        childScreen.changeType("editable", self.navLine)
                    print childScreen.type

        elif(addorsub == 1):
            self.value = self.val1
            thisData['config'][masterList[n].interfaceType]['protocol']['inet']['method'] = self.value
            for childScreen in masterList[n].screens:
                if childScreen.screenType == 'NetworkScreen' and childScreen.title in editableSet:
                    print childScreen.type

                    if(self.value == self.val0):
                        childScreen.changeType("editable", self.incrLine)
                    elif(self.value == self.val1):
                        childScreen.changeType("readOnly", self.navLine)

                    print childScreen.type

        elif(addorsub == 2):
            thisData['config'][masterList[n].interfaceType]['protocol']['inet']['method'] = self.value
            print thisData['config'][masterList[n].interfaceType]['protocol']['inet']['method']
            self.value = self.value
            print self.value

        self.displayThis()

# ------------------End of MethodScreen Class Definition ---------------------


class confSend(Screen):
    """Class for true/false options screens. Extends Screen."""

    def __init__(self, type, title, value):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "confScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.val0 = "Yes"
        self.val1 = "No"
        self.incrLine = "<--    Send    -->"
        self.editLine = self.val0 + "<       >" + self.val1
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        global level
        if(addorsub == 0):
            result = validate.config_validate(thisData['config'])
            print result
            if result is True:
                # TEMPORARY
                with open("Output.txt", "w") as text_file:
                    text_file.write("Data: {0}".format(thisData['config']))
                level = 4
                self.navigation = self.incrLine
                draw_confirmation("Config Valid", "Config Sent", 255, 0, masterList[n])
                print thisData['config']
            else:
                level = 4
                print result
                self.navigation = self.incrLine
                draw_warning2(result['message'], 255, 0, masterList[n])
        elif(addorsub == 1):
            level = 4
            self.navigation = self.incrLine
            draw_warning('canceled', 'Returning to main menu', 255, 0, masterList[n])
        elif(addorsub == 2):
            self.displayThis()

    def displayEdit(self, underline_pos, underline_width):
        """screen to display when editting value."""
        draw_screen_ul(self.title, "Are You Sure?", self.navigation, 255, 0, 0, 0)


#  ******* Comment block denoting screen section
# *
# *
#   *****  This is where we initialize all of our screens
#        *
#        *
# *******

# initializes the list that keeps track of top-level screens
masterList = []


def determineScreenType(value, title, method):
    """Determine what type of screen.

    takes in value and title of a screen. Value is parsed to check if it
    is an ip4 address. if not, it is assumed it is a string.
    TODO: check for boolean options.
    """
    ip = validate.parse_ip4_address(value)
    print ip
    screendict = {'type': 'none', 'editable': 'none'}
    print screendict
    if ip:
        screendict['type'] = 'ip'
    else:
        screendict['type'] = 'str'
    if title in editableSet and method == "static":
        screendict['editable'] = 'editable'
    else:
        screendict['editable'] = 'readOnly'
    return screendict


def createTop2():
    global masterList, thisData
    count = 0
    for blah, (k, v) in enumerate(thisData.iteritems(), 1):
        if(k == "config" or k == "lo"):
            pass
        elif(k.startswith("eth")):
            keyList = thisData[k].keys()
            if any("eth" in s for s in keyList):
                for k1, v1 in thisData[k].iteritems():
                    if(k1.startswith("eth")):
                        print k1
                        masterList.append(Screen("subMenu", "Ethernet (" + k1 + ")", " ", k1))
                        if hasattr(thisData["config"][k1]["protocol"]["inet"], "method"):
                            method = thisData["config"][k1]["protocol"]["inet"]["method"]
                        else:
                            method = "dhcp"
                        masterList[count].screens.append(MethodScreen("editable", "method", method, "static", "dhcp"))
                        for k2, v2 in thisData[k][k1]["inet"].iteritems():
                            screendict = determineScreenType(v2, k2, method)
                            if screendict['type'] == 'str':
                                masterList[count].screens.append(StringScreen(screendict['editable'], k2, v2))
                            elif screendict['type'] == 'ip':
                                masterList[count].screens.append(NetworkScreen(screendict['editable'], k2, str(v2), k1))
                        for k2, v2 in thisData[k].iteritems():
                            if(k2.startswith("eth")):
                                pass
                            else:
                                screendict = determineScreenType(v2, k2, method)
                                if screendict['type'] == 'str':
                                    masterList[count].screens.append(StringScreen(screendict['editable'], k2, v2))
                                elif screendict['type'] == 'ip':
                                    masterList[count].screens.append(NetworkScreen(screendict['editable'], k2, str(v2), k1))

                        count = count + 1
            else:
                masterList.append(Screen("subMenu", "Ethernet (" + k + ")", " ", k1, k1))
                for k1, v1 in thisData[k].iteritems():
                    masterList[count].screens.append(Screen("readOnly", k1, v1))
                count = count + 1
        elif(k.startswith("wlan")):
            '''
            keyList = thisData[k].keys()
            if any("wlan" in s for s in keyList):
                for k1, v1 in thisData[k].iteritems():
                    if(k1.startswith("wlan")):
                        print k1
                        masterList.append(Screen("subMenu", "wlan (" + k1 + ")", " "))
                        for k2, v2 in thisData[k][k1].iteritems():
                            for k3, v3 in thisData[k][k1][k2].iterItems():
                                masterList[count].screens.append(Screen("readOnly", k3 + " " + k2, v2))
                        for k2, v2 in thisData[k].iteritems():
                            if(k2.startswith("wlan")):
                                pass
                            else:
                                masterList[count].screens.append(Screen("readOnly", k2, v2))
                        count = count + 1
            else:
                masterList.append(Screen("subMenu", "wlan (" + k + ")", " "))
                for k1, v1 in thisData[k].iteritems():
                    masterList[count].screens.append(Screen("readOnly", k1, v1))
                count = count + 1
                '''
        else:
            print k
            masterList.append(Screen("subMenu", k, " "))
            for count1, (k1, v1) in enumerate(thisData[k].iteritems()):
                if isinstance(v1, dict):
                    pass
                else:
                    masterList[count].screens.append(Screen("readOnly", k1, v1, k1))
            count = count + 1

createTop2()

timeScreen = Screen("subMenu", "Time and Date", " ", 'time')
# intialize time screens
timeEdit = DateTimeScreen("editable", "Time Edit")

timeScreen.initScreenList([timeEdit])
masterList.append(timeScreen)

configurationScreen = Screen("subMenu", "Configurations", " ", "config")
# initialize configuration screens
configSend = confSend("editable", "Validate/Send Config", "")

configurationScreen.initScreenList([configSend])
masterList.append(configurationScreen)
# Set the number of menu items to the size of the list
# Since the list counts from one, we must subtract one
maxn = len(masterList) - 1

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


def replaceChar(word, index, char):
    word = word[:index] + char + word[index + 1:]
    return word


def draw_warning(line2, line3, fillNum, fillBg, currentScreen):
    """for drawing an error."""
    global disp, n, maxn, Image, ImageDraw, draw, font
    # Draw a black filled fox to clear the image.

    draw.rectangle((0, 0, width - 1, height - 1), outline=1, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 0, width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((center_text('A L E R T', 0), top), "A L E R T", font=font, fill=fillBg)
    draw.text((center_text(line2, 0), top + 9), line2, font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 18), line3, font=font, fill=fillNum)
    disp.image(image.rotate(180))

    disp.display()

def draw_warning2(line2, fillNum, fillBg, currentScreen):
    """for drawing an error."""
    global disp, n, maxn, Image, ImageDraw, draw, font
    # Draw a black filled fox to clear the image.

    draw.rectangle((0, 0, width - 1, height - 1), outline=1, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 0, width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((center_text('A L E R T', 0), top), "A L E R T", font=font, fill=fillBg)
    if len(line2) * 6 > 21:
        chunks = line2.split(" ")
        length1 = math.floor(len(chunks) / 2)
        length2 = len(chunks)
        print length1, length2
        lineone = ' '.join(chunks[int(0):int(length1 + 1)])
        linetwo = ' '.join(chunks[int(length1 + 1):int(length2 + 1)])
        draw.text((center_text(line2, 0), top + 9), lineone, font=font, fill=fillNum)
        draw.text((center_text(line2, 0), top + 18), linetwo, font=font, fill=fillNum)
    else:
        draw.text((center_text(line2, 0), top + 9), line2, font=font, fill=fillNum)

    disp.image(image.rotate(180))

    disp.display()


def draw_confirmation(line2, line3, fillNum, fillBg, currentScreen):
    """for drawing an error."""
    global disp, n, maxn, Image, ImageDraw, draw, font
    # Draw a black filled fox to clear the image.
    draw.rectangle((0, 0, width-1, height-1), outline=1, fill=fillBg)

    x = 0
    top = 2
    draw.rectangle((1, 0, width - 1, top + 9), outline=1, fill=fillNum)
    draw.text((center_text("S A V E D", 0), top), "S A V E D", font=font, fill=fillBg)
    draw.text((center_text(line2, 0), top + 9), line2, font=font, fill=fillNum)
    draw.text((center_text(line3, 0), top + 18), line3, font=font, fill=fillNum)
    disp.image(image.rotate(180))

    disp.display()

def center_text(text, borderWidth):
    strlen = len(str(text)) * 6
    return (128 + borderWidth - strlen) / 2

def draw_screen(s, line2, line3, fillNum, fillBg):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw, font
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width + 10, height + 10), outline=0, fill=fillBg)

    x = 0
    top = 2
    draw.text((x, top), s, font=font, fill=fillNum)
    draw.text((x, top + 10), line2, font=font, fill=fillNum)
    draw.text((x, top + 20), line3, font=font, fill=fillNum)

    disp.image(image.rotate(180))

    # disp.image(image)
    disp.display()


def draw_screen_ul(s, line2, line3, fillNum, fillBg, underline_pos, underline_width):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=fillBg)

    x = 0
    top = 2
    draw.text((x, top), s, font=font, fill=fillNum)
    draw.text((x, top + 10), line2, font=font, fill=fillNum)
    draw.text((x, top + 20), line3, font=font, fill=fillNum)

    draw.line([underline_pos * underline_width, 22, (underline_pos + 1) * underline_width - 1, 22], fill=255)

    disp.image(image.rotate(180))
    # disp.image(image)
    disp.display()

def draw_text(s):
    """for drawing the next screen."""
    global disp, n, maxn

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Load default font.
    font = ImageFont.load_default()

    x = 0
    top = 2
    draw.text((x, top), s, font=font, fill=255)
    draw.text((x, top + 10), '', font=font, fill=255)
    draw.text((x, top + 20), '', font=font, fill=255)

    underline_pos = n
    underline_width = 6

    draw.line([underline_pos * underline_width, 22, (underline_pos + 1) * underline_width - 1, 22], fill=255)

    # Display image.
    disp.image(image.rotate(180))
    # disp.image(image)
    disp.display()
    time.sleep(0.1)


def screen_select(screenNum):
    """for changing screens."""
    global ip, lo, masterList

    # find and display the screen in the list based on our passed int value
    masterList[screenNum].displayThis()

detect_edges(button_callback)
# startup text
screen_select(n)

try:
    raw_input("Press Enter to quit\n>")

except KeyboardInterrupt:
    GPIO.cleanup()	   # clean up GPIO on CTRL+C exit
    draw_text('Interrupted...')

GPIO.cleanup()		   # clean up GPIO on normal exit
draw_screen('Program ended', "", "", 200, 0)
