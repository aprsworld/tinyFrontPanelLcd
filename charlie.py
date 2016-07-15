# display imports
"""This module outputs to an lcd screen."""
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import PIL.ImageOps
import RPi.GPIO as GPIO
import os
import time
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as tdelta
import charlieimage
from threading import Timer

LOGO_DISPLAY_TIME = 1

charSet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

charSetPass = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

charSetIndex = 0
f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
ff = os.popen('ifconfig lo | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
ip = f.read()
lo = ff.read()

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
    """updates the value of the time screen print_some_times calls this every second."""
    global timeScreen
    print_some_times()
    timeScreen.value = time.strftime("%Y-%m-%d %H:%M:%S")
    # If we are on the time screen, update the screen every second as well
    if(masterList[n].title == "Time and Date"):
        # masterList[n].displayThis()
        pass


def print_some_times():
    """This calls print_time every second."""
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


# now we'll define two threaded callback functions
# these will run in another thread when our events are detected
def button_callback(channel):
    """two threaded callback functions."""
    # allow access to our globals
    global action_up_now, action_select_now, action_down_now, n, maxn, masterList, level, charSetIndex
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
            if(curIndex < this.valueLength):
                this.childIndex = this.childIndex + 1
                this.editVal(this.childIndex, 2)
                charSetIndex = 0
            else:
                this.childIndex = 0
                level = 2
                this.navigation = this.incrLine
    print(channel)


# detect button falling edges
def detect_edges(callbackFn):
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

    def __init__(self, type, title, value):
        """Our initialization for the screen class."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.value = value
        self.childIndex = 0
        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def initScreenList(self, screens):
        """Initialize the submenus for this screen."""
        self.screens = screens

    def displayThis(self):
        """Draw our screen."""
        draw_screen(self.title, self.value, self.navigation, 255, 0)

    def displayEdit(self, underline_pos, underline_width):
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
        self.childIndex = value

    def screenChosen(self):
        """Screen is chosen - sets child index to zero and displays first child."""
        print("screenChosen " + self.title)
        self.childIndex = 0
        self.screens[self.childIndex].displayThis()

# --------------------End of Screen Class Definition -----------------------


class NetworkScreen(Screen):
    """A networking screen class. Extends Screen."""

    def __init__(self, type, title, addr0, addr1, addr2, addr3):
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
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.addr0 = addr0
        self.addr1 = addr1
        self.addr2 = addr2
        self.addr3 = addr3
        self.value = self.formatAddr(str(addr0)) + "." + self.formatAddr(str(addr1)) + "." + self.formatAddr(str(addr2)) + "." + self.formatAddr(str(addr3))
        self.childIndex = 0
        self.valueLength = 11
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
            self.addr0 = self.addr0 + addAmt
            if(self.addr0 > 255):
                self.addr0 = 0
            if(self.addr0 < 0):
                self.addr0 = 255
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum, 6)
        # xxx.___.xxx.xxx
        elif(addrNum <= 5):
            self.addr1 = self.addr1 + addAmt
            if(self.addr1 > 255):
                self.addr1 = 0
            if(self.addr1 < 0):
                self.addr1 = 255
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 1, 6)
        # xxx.xxx.___.xxx
        elif(addrNum <= 8):
            self.addr2 = self.addr2 + addAmt
            if(self.addr2 > 255):
                self.addr2 = 0
            if(self.addr2 < 0):
                self.addr2 = 255
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 2, 6)
        # xxx.xxx.xxx.___
        elif(addrNum <= 11):
            self.addr3 = self.addr3 + addAmt
            if(self.addr3 > 255):
                self.addr3 = 0
            if(self.addr3 < 0):
                self.addr3 = 255
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 3, 6)


        # append everything into a network address string so that it can be shown on screen
        print(self.value)

    def getVal(self, addrNum):
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

# --------------------End of NetworkScreen Class Definition -----------------------

class StringScreen(Screen):
    """Class for a screen with a string value. Extends String."""

    def __init__(self, type, title, value):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        # String: Line one on the LCD Screen
        self.title = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.valueLength = len(self.value)
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
        char = charSet[charSetIndex]
        word = self.value
        word = word[:index] + char + word[index + 1:]
        self.value = word
        charSetIndex = charSetIndex + addAmt
        self.displayEdit(index, 6)

# --------------------End of StringScreen Class Definition -----------------------


class DateTimeScreen(Screen):
    """Class for dateTime screens. Extends Screen."""

    def __init__(self, type, title):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
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
        self.timeChange = tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)
        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        global draw
        if(index == 0):
            self.editYear(addorsub)
            underline_pos = 0
            underline_width = 24
        elif(index == 1):
            self.editMonth(addorsub)
            underline_pos = 2.5
            underline_width = 12
        elif(index == 2):
            self.editDay(addorsub)
            underline_pos = 4
            underline_width = 12
        elif(index == 3):
            self.editHour(addorsub)
            underline_pos = 5.5
            underline_width = 12
        elif(index == 4):
            self.editMinute(addorsub)
            underline_pos = 7
            underline_width = 12
        elif(index == 5):
            self.editSecond(addorsub)
            underline_pos = 8.5
            underline_width = 12
        self.timeChange = tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)
        self.date = dt.now() + self.timeChange
        self.value = self.date.strftime("%Y-%m-%d %H:%M:%S")
        self.displayEdit(underline_pos, underline_width)

    def editYear(self, addorsub):
        print("got here")
        print(self.year)
        if(addorsub == 0):
            self.year = self.year - 1
        elif(addorsub == 1):
            self.year = self.year + 1
        else:
            print('else')

    def editMonth(self, addorsub):
        if(addorsub == 0):
            self.month = self.month - 1
        elif(addorsub == 1):
            self.month = self.month + 1
        else:
            print('else')

    def editDay(self, addorsub):
        if(addorsub == 0):
            self.day = self.day - 1
        elif(addorsub == 1):
            self.day = self.day + 1
        else:
            print('else')

    def editHour(self, addorsub):
        if(addorsub == 0):
            self.hour = self.hour - 1
        elif(addorsub == 1):
            self.hour = self.hour + 1
        else:
            print('else')

    def editMinute(self, addorsub):
        if(addorsub == 0):
            self.minute = self.minute - 1
        elif(addorsub == 1):
            self.minute = self.minute + 1
        else:
            print('else')

    def editSecond(self, addorsub):
        if(addorsub == 0):
            self.second = self.second - 1
        elif(addorsub == 1):
            self.second = self.second + 1
        else:
            print('else')

# ------------------End of DateTimeScreen Class Definition ---------------------


# initialize screens
ethScreen = Screen("subMenu", "eth0", " ")
loScreen = Screen("subMenu", "Lo", " ")
wifiCreds = Screen("subMenu", "WiFi Credentials", " ")
timeScreen = Screen("subMenu", "Time and Date", " ")
# print_some_times()

# initialize subscreens in eth0
ethIP = NetworkScreen("editable", "Eth0 IP Address", 192, 168, 10, 234)
ethIP2 = Screen("readOnly", "Eth0 IP Address 2", "test2")
ethIP3 = Screen("readOnly", "Eth0 IP Address 3", "test3")
ethIP4 = Screen("readOnly", "Eth0 IP Address 4", "test4")

ethScreen.initScreenList([ethIP, ethIP2, ethIP3, ethIP4])

# initialize subscreens in Lo
loIP = Screen("readOnly", "Lo IP Address", lo)
loIP2 = Screen("readOnly", "Lo IP Address", "screen 2")
loIP3 = Screen("readOnly", "Lo IP Address", "screen 3")

loScreen.initScreenList([loIP, loIP2, loIP3])

# intialize time screens
timeEdit = DateTimeScreen("editable", "Time Edit")

timeScreen.initScreenList([timeEdit])

# initialize wifi credentials screens
wifiName = StringScreen("editable", "wifiName", "aprsworld")
wifiPass = StringScreen("editable", "wifiPass", "zestoPenguin")

wifiCreds.initScreenList([wifiName, wifiPass])

# list of all the top-level screen objects
masterList = [ethScreen, loScreen, wifiCreds, timeScreen]

# Set the number of menu items to the size of the list
# Since the list counts from one, we must subtract one
maxn = len(masterList) - 1


def replaceChar(word, index, char):
    word = word[:index] + char + word[index + 1:]
    return word


def draw_screen(s, line2, line3, fillNum, fillBg):
    """for drawing the next screen."""
    global disp, n, maxn, Image, ImageDraw, draw

    disp.clear()

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=fillBg)

    # Load default font.
    font = ImageFont.load_default()

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

    disp.clear()

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=fillBg)

    # Load default font.
    font = ImageFont.load_default()

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

    # draw.text((x, top),    'IP: 192.168.200.201',  font=font, fill=255)
    # draw.text((x, top),    'IP: ' + IP,  font=font, fill=255)
    # draw.text((x, top+10), 'MA: 255.255.255.0', font=font, fill=255)
    # draw.text((x, top+20), 'GW: 192.168.200.1', font=font, fill=255)

    # Display image.
    disp.image(image.rotate(180))
    # disp.image(image)
    disp.display()


def screen_chosen(screenNum):
    """For Chosen Screen."""
    if (screenNum == 0):
        draw_screen("YOU CHOSE", "", " Jim", 200, 0)
    else:
        draw_screen("YOU CHOSE", "", " Andrew", 200, 0)


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
draw_text('Shutting down...')
