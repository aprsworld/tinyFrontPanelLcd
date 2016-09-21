import globalDependencies as gd
import validate
import getConfig
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as tdelta
from threading import Timer
import ctypes
import ctypes.util
import time
import math
import socket
import charlieimage

URL = gd.URL
URL2 = gd.URL2
URL3 = gd.URL3
humanTranslations = gd.humanTranslations
thisData = gd.thisData
charSetIndex = gd.charSetIndex
charSet = gd.charSet
inView = gd.inView

def resetFromStatic(interface):
    """Reset values when method changed from DHCP to Static."""
    global thisData
    thisData['config'][interface]['protocol']['inet'].pop('address', None)
    thisData['config'][interface]['protocol']['inet'].pop('netmask', None)
    thisData['config'][interface]['protocol']['inet'].pop('gateway', None)
    print thisData['config']


def changeSecurityType(interface, newSecurity, oldSecurity):
    """Change necessary screens and config keys when changing between wep and WPA."""
    global thisData
    # dictionaries to hold new and old values
    wepSecurity = {"ssid": "wireless-essid", "passphrase": "wireless-key"}
    wpaSecurity = {"ssid": "wpa-ssid", "passphrase": "wpa-psk"}
    noneSecurity = {"ssid": "wireless-essid", "passphrase": "wireless-key"}
    securityLookup = {"wep": wepSecurity, "wpa": wpaSecurity, "wpa2": wpaSecurity, "none": noneSecurity}
    print newSecurity, oldSecurity
    # variables to hold values for readability purposes
    newPassPhrase = securityLookup[newSecurity.lower()]["passphrase"]
    oldPassPhrase = securityLookup[oldSecurity.lower()]["passphrase"]
    old_ssid = securityLookup[oldSecurity.lower()]["ssid"]
    new_ssid = securityLookup[newSecurity.lower()]["ssid"]
    configAddress = thisData['config'][interface]["protocol"]["inet"]
    print "CHANGE SECURITY", "old_ssid:", old_ssid, "new_ssid", new_ssid

    if oldSecurity.lower() == "wep":
        if newSecurity.lower() == "none":
            if configAddress.get("wireless-key", False) is not False:
                configAddress.pop("wireless-key")
        elif newSecurity.lower() == "wpa" or newSecurity.lower() == "wpa2":
            if configAddress.get("wireless-essid", False) is not False:
                configAddress["wpa-ssid"] = configAddress.pop("wireless-essid")
            if configAddress.get("wireless-key", False) is not False:
                configAddress["wpa-psk"] = configAddress.pop("wireless-key")
            configAddress["wpa-scan-ssid"] = "1"
            configAddress["wpa-ap-scan"] = "1"
    elif oldSecurity.lower() == "wpa" or oldSecurity.lower() == "wpa2":
        if newSecurity.lower() == "none":
            if configAddress.get("wpa-scan-ssid", False) is not False:
                configAddress.pop("wpa-scan-ssid")
            if configAddress.get("wpa-ap-scan", False) is not False:
                configAddress.pop("wpa-ap-scan")
            if configAddress.get("wpa-psk", False) is not False:
                configAddress["wireless-key"] = configAddress.pop("wpa-psk")
            if configAddress.get("wpa-ssid", False) is not False:
                configAddress["wireless-essid"] = configAddress.pop("wpa-ssid")
        elif newSecurity.lower() == "wep":
            if configAddress.get("wpa-scan-ssid", False) is not False:
                configAddress.pop("wpa-scan-ssid")
            if configAddress.get("wpa-ap-scan", False) is not False:
                configAddress.pop("wpa-ap-scan")
            if configAddress.get("wpa-psk", False) is not False:
                configAddress["wireless-key"] = configAddress.pop("wpa-psk")
            if configAddress.get("wpa-ssid", False) is not False:
                configAddress["wireless-essid"] = configAddress.pop("wpa-ssid")
    elif oldSecurity.lower() == "none":
        if newSecurity.lower() == "wep":
            pass
        elif newSecurity.lower() == "wpa" or newSecurity.lower() == "wpa2":
            if configAddress.get("wireless-essid", False) is not False:
                configAddress["wpa-ssid"] = configAddress.pop("wireless-essid")
            if configAddress.get("wireless-key", False) is not False:
                configAddress["wpa-psk"] = configAddress.pop("wireless-key")
            configAddress["wpa-scan-ssid"] = "1"
            configAddress["wpa-ap-scan"] = "1"

    # loop through Screen List and change the title of the screen
    '''
    if newSecurity.lower() == "wep" and (oldSecurity.lower() == "wpa" or oldSecurity.lower() == "wpa2"):
        if configAddress.get("wpa-scan-ssid", False) is not False:
            configAddress.pop("wpa-scan-ssid")
        if configAddress.get("wpa-ap-scan", False) is not False:
            configAddress.pop("wpa-ap-scan")
        if configAddress.get("wpa-psk", False) is not False:
            configAddress.pop("wpa-psk")
        if configAddress.get("wpa-ssid", False) is not False:
            configAddress.pop("wpa-ssid")
    elif newSecurity.lower() == "none" and (oldSecurity.lower() == "wpa" or oldSecurity.lower() == "wpa2"):
        if configAddress.get("wpa-scan-ssid", False) is not False:
            configAddress.pop("wpa-scan-ssid")
        if configAddress.get("wpa-ap-scan", False) is not False:
            configAddress.pop("wpa-ap-scan")
        if configAddress.get("wpa-psk", False) is not False:
            configAddress.pop("wpa-psk")
        if configAddress.get("wpa-ssid", False) is not False:
            configAddress["wireless-essid"] = configAddress.pop("wpa-ssid")
    elif newSecurity.lower() == "none" and (oldSecurity.lower() == "wep"):
        if configAddress.get("wpa-scan-ssid", False) is not False:
            configAddress.pop("wpa-scan-ssid")
        if configAddress.get("wpa-ap-scan", False) is not False:
            configAddress.pop("wpa-ap-scan")
        if configAddress.get("wpa-psk", False) is not False:
            configAddress.pop("wpa-psk")
        if configAddress.get("wireless-key", False) is not False:
            configAddress.pop("wireless-key")
        if configAddress.get("wpa-ssid", False) is not False:
            configAddress["wireless-essid"] = configAddress.pop("wpa-ssid")
    elif oldSecurity.lower() == "wep":
        print 67, configAddress
        if configAddress.get("wireless-ssid", False) is not False:
            configAddress.pop("wireless-ssid")
        if configAddress.get("wireless-key", False) is not False:
            configAddress.pop("wireless-key")
    elif newSecurity.lower() == "wpa" or newSecurity.lower() == "wpa2":
        configAddress["wpa-scan-ssid"] = "1"
        configAddress["wpa-ap-scan"] = "1"
    '''

class Screen:
    """
    Our screen class.

    This is the base class for our screens - it is extended by other classes
    """

    dirLine = "<--    Select    -->"
    navLine = "<--              -->"
    incrLine = "<--     Edit     -->"
    editLine = "(-)     Next     (+)"

    def __init__(self, type, title, value, interface):
        """
        Our initialization for the screen class.

        Args:
            type: whether it is readonly or editable
            title: the label to display at the top of the screen when displayEdit
            value: the value stored to display on the second line of the screenType
            interface: the interface that this screen is associated with
        """
        # String: type of screen - "readOnly", "subMenu", "editable"
        global humanTranslations
        self.type = type
        self.screenType = "GeneralScreen"
        self.interfaceType = interface
        # String: Line one on the LCD Screen
        if title in gd.humanTranslations:
            self.title = gd.humanTranslations[title]
        else:
            self.title = title
        self.titleOrig = title
        self.dataName = title
        # String: line two on the LCD Screen
        self.value = value
        self.valueLength = 0
        self.childIndex = 0
        self.screens = []
        self.editMode = False
        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.dirLine
        else:
            self.navigation = self.incrLine
        self.underline_pos = 0
        self.underline_width = 0
        self.edit = False

    def initScreenList(self, screens):
        """
        Initialize the submenus for this screen.

        Args:
            screens: a list of screen objects
        """
        self.screens = screens
        self.valueLength = len(self.screens) - 1

    def insertScreenList(self, screen, index):
        if index > self.valueLength:
            self.valueLength = index
        self.screens.insert(index, screen)

    def prependScreenList(self, screen):
        """
        Add screen to beginning of screen list.

        Args:
            screen: the screen object to prepend to the screen list
        """
        self.screens.insert(0, screen)
        self.valueLength = len(self.screens) - 1

    def appendScreenList(self, screen):
        """
        Add screen to end of screen list.

        Args:
            screen: the screen object to prepend to the screen list
        """
        self.screens.append(screen)
        self.valueLength = len(self.screens) - 1

    def displayThis(self):
        """Draw our screen."""
        global inView
        inView = self
        gd.draw_screen(self.title, self.value, self.navigation, 255, 0)

    def displayEdit(self, underline_pos, underline_width):
        """
        screen to display when editting value.

        Args:
            underline_pos: the x value for the starting point of our underline_pos
            underline_width: the width of the underline
        """
        gd.draw_screen_ul(self.title, self.value, self.navigation, 255, 0, underline_pos, underline_width)

    def setChildIndex(self, value):
        """set child index of screen.

        Child index is used to determine what subscreen we are on
        Args:
            value: the value to set as childindex
        """
        self.childIndex = value

    def screenChosen(self):
        """Screen is chosen - sets child index to zero and displays first child."""
        print("screenChosen " + self.title)
        self.childIndex = 0
        print self.screens
        self.screens[self.childIndex].displayThis()

    def getTitle(self):
        """Gets the original title.

        Note: it is important that it gets the original title as this is used to
        set values in the config.
        """
        return self.titleOrig

    def setHrTitle(self, title):
        print 260, title
        self.title = title

    def setTitle(self, title):
        """Sets the displayed title"""
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.titleOrig = title

    def getInterfaceType(self):
        return self.interfaceType

    def changeType(self, type, navigation):
        self.type = type
        self.navigation = navigation

    def setConfirmation(self, conf1, conf2):
        self.conf1 = conf1
        self.conf2 = conf2

    def getConfirmation(self):
        if self.value == "Go back to main menu":
            return {"line1": "Returning to", "line2": "main menu"}
        elif not hasattr(self, 'conf1') or not hasattr(self, 'conf2'):
            return {"line1": self.title + ' has', "line2": "been saved to config"}
        else:
            return {"line1": self.conf1, "line2": self.conf2}

    def setWarning(self, warn1, warn2):
        self.warn1 = warn1
        self.warn2 = warn2

    def getWarning(self):
        if not hasattr(self, 'warning'):
            return {"line1": 'default warning', "line2": "line2"}
        else:
            return {"line1": self.warn1, "line2": self.warn2}
# --------------------End of Screen Class Definition -----------------------

class HostName(Screen):
    """displays host name."""
    def __init__(self, title):
        global humanTranslations
        self.type = "readOnly"
        self.screenType = "IntScreen"
        self.titleOrig = title
        self.interface = "hostname"
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.value = socket.gethostname()
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine
        self.editMode = False

class IntScreen(Screen):
    """A number screen class. Extends Screen."""
    def __init__(self, type, title, value, interface):
        """
        initialization for the intScreen subclass.

        """

        global humanTranslations
        self.type = type
        self.screenType = "IntScreen"
        self.titleOrig = title
        self.interface = interface
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.valueLength = len(str(value)) - 1
        self.value = self.formatVal(value)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine
        self.editMode = False

    def editVal(self, index, addorsub):
        """Edits the integer value of this screen."""
        if index is 0:
            addAmt = 1000
        elif index is 1:
            addAmt = 100
        elif index is 2:
            addAmt = 10
        elif index is 3:
            addAmt = 1

        if(addorsub == 0):
            addAmt = addAmt * -1
        if(addorsub == 2):
            addAmt = 0
        value = int(self.value)
        if(not value == 0):
            if(int(value) > 9999):
                print value
                value = value % 1000
            thous = (value / 1000) * 1000
            hunds = ((value - thous) / 100) * 100
            tens = ((value - thous - hunds) / 10) * 10
            ones = ((value - thous - hunds - tens) / 1) * 1
        else:
            hunds = 0
            tens = 0
            ones = 0
        print hunds, tens, ones
        value = value + addAmt
        if(value > 9999):
            if(addAmt == 1000):
                value = 0 + hunds + tens + ones
            if(addAmt == 100):
                value = 0 + tens + ones
            elif(addAmt == 10):
                value = 0 + ones
            else:
                value = 0
        elif(value < 0):
            if(addAmt == -1000):
                value = 9000 + hunds + tens + ones
            elif(addAmt == -100):
                value = 9000 + tens + ones
            elif(addAmt == -10):
                value = 9000 + ones
        self.value = self.formatVal(str(value))
        self.displayEdit(index, 6)

    def changeConfig(self):
        """Change the setting in the config so that we can send it to piNetConfig."""
        global thisData
        print thisData['config']
        thisData['config'][self.interface]['protocol']['inet'][self.titleOrig] = str(self.value)
        print thisData['config']

    def formatVal(self, val):
        """append spaces on to beginning of addresses."""
        length = len(val)
        for x in range(length, 4):
            val = " " + val
        return val

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
        global humanTranslations, dataUpdateDict
        self.type = type
        self.screenType = "NetworkScreen"
        # String: Line one on the LCD Screen
        self.titleOrig = title
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        # String: line two on the LCD Screen
        if addr is None:
            addr = "000.000.000.000"
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
        # dataUpdateDict[self.interface + "_" + self.dataName] = self
        # String: line Three on the LCD Screen
        # Can be either <--    Select    -->   OR   (-)    Select    (+)
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine
        self.editMode = False

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
            self.addr0 = gd.configureOctet(self.addr0, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum, 6)
        # xxx.___.xxx.xxx
        elif(addrNum <= 5):
            self.addr1 = gd.configureOctet(self.addr1, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 1, 6)
        # xxx.xxx.___.xxx
        elif(addrNum <= 8):
            self.addr2 = gd.configureOctet(self.addr2, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 2, 6)
        # xxx.xxx.xxx.___
        elif(addrNum <= 11):
            self.addr3 = gd.configureOctet(self.addr3, addAmt)
            self.value = self.formatAddr(str(self.addr0)) + "." + self.formatAddr(str(self.addr1)) + "." + self.formatAddr(str(self.addr2)) + "." + self.formatAddr(str(self.addr3))
            self.displayEdit(addrNum + 3, 6)
        # append everything into a network address string so that it can be shown on screen
        print(self.value)

    def updateValue(self, newValue):
        addr = newValue.split(".")
        self.addr0 = int(addr[0])
        self.addr1 = int(addr[1])
        self.addr2 = int(addr[2])
        self.addr3 = int(addr[3])
        self.value = newValue
        print self.value

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
        print thisData['config']
        gd.thisData['config'][self.interface]['protocol']['inet'][self.titleOrig] = str(self.addr0)+"."+str(self.addr1)+"."+str(self.addr2)+"."+str(self.addr3)
        print thisData['config']

    def displayThis(self):
        """Draw our screen."""
        global inView
        inView = self
        if gd.interfaceSettings[self.interface]["method"].lower() == "dhcp":
            self.type = "readonly"
            self.navigation = self.navLine
        elif self.editMode == True:
            self.type = "editable"
            self.navigation = self.editLine
        else:
            self.type = "editable"
            self.navigation = self.incrLine

        gd.draw_screen(self.title, self.value, self.navigation, 255, 0)

    def displayEdit(self, underline_pos, underline_width):
        """
        screen to display when editting value.

        Args:
            underline_pos: the x value for the starting point of our underline_pos
            underline_width: the width of the underline
        """
        if gd.interfaceSettings[self.interface]["method"].lower() is "dhcp":
            self.type = "readonly"
        else:
            self.type = "editable"
        gd.draw_screen_ul(self.title, self.value, self.navigation, 255, 0, underline_pos, underline_width)

# --------------------End of NetworkScreen Class Definition -----------------------
class StringScreen(Screen):
    """Class for a screen with a string value. Extends Screen class."""

    def __init__(self, type, title, value):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        global humanTranslations
        self.type = type
        self.screenType = "StringScreen"
        # String: Line one on the LCD Screen
        if title in gd.humanTranslations:
            self.title = gd.humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.titleOrig = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.valueLength = 18
        self.edit = False
        self.editMode = False

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
        word = self.value
        print "|" + word[index - 1:index] + "|"

        # if we are at the end of the word we need to notify that we are
        if(word[index - 1:index] == '' and index != 0):
            self.childIndex = self.valueLength + 1
            return
        print charSetIndex, (len(charSet) - 1), index

        # If we have reached the end of the char set, we must flip the index
        # back to zero or vice-versa
        if(charSetIndex >= len(charSet) - 1):
            charSetIndex = 0
        if(charSetIndex < 0):
            charSetIndex = len(charSet) - 1
        if(addorsub == 0):
            addAmt = -1
        # when not at the end of the word, pressing the middle button shifts
        # the cursor one character over
        elif(addorsub == 2):
            self.displayEdit(index, 6)
            return
        else:
            addAmt = 1
        # this is used to locate the current character in the string
        # within the charset list
        if(index < len(word) and charSet.index(word[index]) + addAmt < len(charSet)):
            charSetIndex = charSet.index(word[index]) + addAmt
        else:
            charSetIndex = 0
        print charSetIndex
        char = charSet[charSetIndex]
        # insert the new char within the word
        word = word[:index] + char + word[index + 1:]
        self.value = word
        self.displayEdit(index, 6)

class WifiCreds(StringScreen):
    """
    Class definition for WifiCredentials class.

    Used for changing wifi passwords in WEP and WPA/WPA2 formats
    Extends String Screen
    """

    def __init__(self, type, title, value, interface):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        global humanTranslations
        self.type = type
        self.screenType = "StringScreen"
        # String: Line one on the LCD Screen
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.titleOrig = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.valueLength = 18
        self.edit = False
        self.interface = interface
        self.titleOrig = title
        self.editMode = False
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
        security = gd.interfaceSettings[self.interface]["security"]
        if security == "WEP":
            thisSet = gd.charHexaSet
        else:
            thisSet = charSet
        word = self.value
        print "|"+word[index - 1:index]+"|"
        if(word[index - 1:index] == '' and index != 0):
            self.childIndex = self.valueLength + 1
            return
        print charSetIndex, (len(thisSet) - 1), index
        if(charSetIndex >= len(thisSet) - 1):
            charSetIndex = 0
        if(charSetIndex < 0):
            charSetIndex = len(thisSet) - 1
        if(addorsub == 0):
            addAmt = -1
        elif(addorsub == 2):
            self.displayEdit(index, 6)
            return
        else:
            addAmt = 1
        if(index < len(word) and word[index] in thisSet and thisSet.index(word[index]) + addAmt < len(thisSet)):
            charSetIndex = thisSet.index(word[index]) + addAmt
        else:
            charSetIndex = 0
        print charSetIndex
        char = thisSet[charSetIndex]
        word = word[:index] + char + word[index + 1:]
        self.value = word
        self.displayEdit(index, 6)

    def changeConfig(self):
        """Change the setting in the config so that we can send it to piNetConfig."""
        global thisData
        print thisData['config']
        print self.value.lower()
        # WPA keys need quotes around them
        security = gd.interfaceSettings[self.interface]["security"]
        if not security == "WEP" or security is None:
            thisData['config'][self.interface]['protocol']['inet']['wpa-psk'] = '\"' + self.value.strip() + '\"'
        else:
            thisData['config'][self.interface]['protocol']['inet']['wireless-key'] = self.value.strip()
        print thisData['config']

class BooleanScreen(Screen):
    """Class for true/false options screens. Extends Screen."""

    def __init__(self, type, title, value, val0, val1):
        """Our initialization for the screen boolean class."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        global humanTranslations
        self.type = type
        self.screenType = "BooleanScreen"
        self.valueLength = 0
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title

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
        self.editMode = False

    def editVal(self, index, addorsub):
        if(addorsub == 0):
            self.value = self.val0
        elif(addorsub == 1):
            self.value = self.val1
        elif(addorsub == 2):
            self.value = self.value
        self.displayThis()

class DateTimeScreen(Screen):
    """Class for dateTime screens. Extends Screen."""

    def __init__(self, type, title):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        global humanTranslations
        self.type = type
        self.screenType = "DateTimeScreen"

        # String: Line one on the LCD Screen
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
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
        self.editMode = False

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
        if(addorsub == 2 and index > 5):
            self.underline_pos = 0
            self.underline_width = 0
            self.childIndex == self.valueLength + 1
        self.timeChange = tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)

        print self.timeChange
        self.date = dt.now() + self.timeChange
        self.value = self.date.strftime("%Y-%m-%d %H:%M:%S")
        self.displayEdit(self.underline_pos, self.underline_width)

    def print_time(self):
        """update the value of the time screen print_some_times calls this every second."""
        global timeScreen, masterList
        self.date = dt.now() + self.timeChange
        self.value = self.date.strftime("%Y-%m-%d %H:%M:%S")
        self.print_some_times()

        # If we are on the time screen, update the screen every second as well
        if not inView == None and gd.screenSleepFlag is False:
            if inView.title == self.title and gd.logoFlag and not gd.action_up_now and not gd.action_select_now and not gd.action_select_now:
                # if inView.title == self.title:
                print "update"
                gd.action_screen_update = True
                if(self.edit):
                    self.displayEdit(self.underline_pos, self.underline_width)
                else:
                    self.displayThis()
                gd.action_screen_update = False
            elif inView.title == self.title or gd.action_up_now or gd.action_down_now:
                print "conflict"

    def print_some_times(self):
        """call print_time every second."""
        try:
            self.timer = Timer(1, self.print_time)
            self.timer.daemon = True
            self.timer.start()
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

    def changeConfig1(self):
        print self.year
        thisdate = dt.now() + tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)
        print thisdate.year, thisdate.month, thisdate.day, thisdate.hour, thisdate.minute, thisdate.second, int(math.floor(dt.now().microsecond*.001))
        pass

    def changeConfig(self):
        thisdate = dt.now() + tdelta(years=self.year, months=self.month, days=self.day, hours=self.hour, minutes=self.minute, seconds=self.second)
        time_tuple = ( thisdate.year, thisdate.month, thisdate.day, thisdate.hour, thisdate.minute, thisdate.second, int(math.floor(dt.now().microsecond*.001)))

        CLOCK_REALTIME = 0

        class timespec(ctypes.Structure):
            _fields_ = [("tv_sec", ctypes.c_long),
                        ("tv_nsec", ctypes.c_long)]

        librt = ctypes.CDLL(ctypes.util.find_library("rt"))

        ts = timespec()
        ts.tv_sec = int( time.mktime( dt( *time_tuple[:6]).timetuple() ) )
        ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

        # http://linux.die.net/man/3/clock_settime
        librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))
        self.value = dt.now()
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0

class ListScreen(Screen):
    """Class for more than two options. extends screen."""

    def __init__(self, type, title, valsList):
        """Our initialization for the screen list class."""
        global humanTranslations
        self.type = type
        self.screenType = "ListScreen"
        self.valueLength = 0
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title

        self.childIndex = 0
        self.value = valsList[self.childIndex]
        self.valList = valsList
        self.incrLine = "<--    Select    -->"
        self.editLine = "Prev   Choose   Next"
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        print self.valList
        if(addorsub == 0):
            self.childIndex += -1
            if(self.childIndex < 0):
                self.childIndex = len(self.valList) - 1
        elif(addorsub == 1):
            self.childIndex += 1
            if(self.childIndex > len(self.valList) - 1):
                self.childIndex = 0
        elif(addorsub == 2):
            # create interface
            pass
        print self.valList, self.childIndex

        self.value = self.valList[self.childIndex]

        self.displayEdit(index, 6)

class TempScreen(StringScreen):
    """Screen used for Manual SSID Entry."""

    def changeConfig(self):
        prevMenu = gd.menuStack.peek()
        prevMenu.value = self.value
        print 967, prevMenu.value
        prevMenu.changeConfig()
        prevMenu.valList.insert(0,self.value)
        gd.screenChosen = gd.menuStack.pop()
        gd.screenChosen.childIndex = 0
        gd.screenChosen.navigation = gd.screenChosen.incrLine

manualEntry = TempScreen("editable", "Manual SSID Entry", "ssidname")


class SsidChooser(ListScreen):
    """
    Class for changing SSID.

    extends listscreen class
    """

    def __init__(self, type, title, valsList, interface):
        """Our initialization for the screen list class."""
        global humanTranslations, ssidListGlobal
        self.type = type
        self.screenType = "ListScreen"
        self.valueLength = -1
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.interface = interface
        self.titleOrig = title
        self.childIndex = 0
        self.valList = gd.getConfig.hasKeys(gd.wifiList)
        self.valList.append("Manual Entry")
        self.value = self.valList[0]
        self.editLine = "Prev   Choose   Next"
        self.editMode = False
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        global manualEntry
        print self.valList
        if(addorsub == 0):
            self.childIndex += -1
            if(self.childIndex < 0):
                self.childIndex = len(self.valList) - 1
            self.value = self.valList[self.childIndex]
            self.displayEdit(index, 0)

        elif(addorsub == 1):
            self.childIndex += 1
            if(self.childIndex > len(self.valList) - 1):
                self.childIndex = 0
            self.value = self.valList[self.childIndex]
            self.displayEdit(index, 0)

        elif(addorsub == 2):
            if self.valList[self.childIndex] == "Manual Entry":
                gd.menuStack.push(self)
                manualEntry.editMode = True
                gd.screenChosen = manualEntry
                gd.screenChosen.displayThis()
            else:
                pass
                self.displayEdit(index, 0)


    def setVal(self, val):
        self.value = val

    def changeConfig(self):
        global thisData
        security = gd.interfaceSettings[self.interface]["security"]
        print 1040, security, self.value
        if (security is not None) and (security.lower() == "wpa" or security.lower() == "wpa2"):
            print 1042
            thisData['config'][self.interface]['protocol']['inet']["wpa-ssid"] = self.value
        else:
            print 1045
            thisData['config'][self.interface]['protocol']['inet']["wireless-essid"] = self.value

    def screenChosen(self):
        """Screen is chosen - sets child index to zero and displays first child."""
        print("screenChosen " + self.title)
        self.valsList = gd.getConfig.hasKeys(gd.wifiList)
        self.valList.append("Manual Entry")
        self.valueLength = len(self.valsList)
        self.childIndex = 0
        self.screens[self.childIndex].displayThis()

    def displayThis(self):
        global inView
        inView = self
        self.valList = gd.getConfig.hasKeys(gd.wifiList)
        self.valList.append("Manual Entry")
        gd.draw_screen(self.title, self.value, self.navigation, 255, 0)


class SecurityChanger(ListScreen):
    """
    Class for changing security settings.

    extends listing screen
    """

    def __init__(self, type, title, interface, security):
        """Our initialization for the screen list class."""
        global humanTranslations
        self.type = type
        self.screenType = "ListScreen"
        self.valueLength = 0
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.interface = interface
        self.titleOrig = title
        self.childIndex = 0
        self.valList = ['WPA', 'WPA2', 'WEP', 'NONE']
        if(security is False or security == None):
            security = "NONE"
            self.value = "NONE"
            self.prevVal = "NONE"
        else:
            self.prevVal = security.upper()
            self.value = security.upper()
        self.editMode = False
        # check if in list. if so, then set the index to that item
        if(self.value in self.valList):
            self.childIndex = self.valList.index(self.value)
        self.editLine = "Prev   Choose   Next"
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        print self.valList
        if(addorsub == 0):
            self.childIndex += -1
            if(self.childIndex < 0):
                self.childIndex = len(self.valList) - 1
        elif(addorsub == 1):
            self.childIndex += 1
            if(self.childIndex > len(self.valList) - 1):
                self.childIndex = 0
        elif(addorsub == 2):
            pass
        print 1169, self.valList, self.childIndex
        self.value = self.valList[self.childIndex]
        self.displayEdit(index, 0)

    def changeConfig(self):
        # update config and screens for this interface
        global thisData
        changeSecurityType(self.interface, self.value, self.prevVal)
        gd.interfaceSettings[self.interface]["security"] = self.value
        self.prevVal = self.value
        print thisData['config']


class MethodScreen(Screen):
    """Class for true/false options screens. Extends Screen."""

    def __init__(self, type, title, value, interface):
        """Our initialization for the screen stringclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        global humanTranslations
        self.type = type
        self.screenType = "BooleanScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title
        self.titleOrig = title
        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = humanTranslations[value]
        self.val0 = "static"
        self.val1 = "DHCP"
        self.interface = interface
        self.editLine = self.val0 + "< Confirm >" + self.val1
        self.editMode = False
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
            print type(thisData['config'])
            print thisData['config']
            thisData['config'][self.interface]['protocol']['inet']['method'] = self.value.lower()
            print thisData
            # thisData['config'][masterList[n].interfaceType]['protocol']['inet'].update({'method': self.value})
        elif(addorsub == 1):
            self.value = self.val1
            thisData['config'][self.interface]['protocol']['inet']['method'] = self.value.lower()
            resetFromStatic(self.interface)
        elif(addorsub == 2):
            thisData['config'][self.interface]['protocol']['inet']['method'] = self.value.lower()
            print thisData['config'][self.interface]['protocol']['inet']['method']
            self.value = self.value
            print self.value
        self.displayThis()

    def changeConfig(self):
        # update config and screens for this interface
        global thisData
        # changeSecurityType(self.interface, self.value, self.prevVal)
        gd.interfaceSettings[self.interface]["method"] = self.value.lower()
        print thisData['config']


class confSend(Screen):
    """Class for sending config. Extends Screen."""

    def __init__(self, type, title, value):
        """Our initialization for the confSend subclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "confScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        global humanTranslations
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title

        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.val0 = "Yes"
        self.val1 = "No"
        self.incrLine = "<--    Send    -->"
        self.editLine = self.val0 + "          " + self.val1
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        global level
        if(addorsub == 0):
            print thisData['config']
            result = validate.config_validate(thisData['config'])
            print result
            if result is True:
                # TEMPORARY
                # with open("Output.txt", "w") as text_file:
                #     text_file.write("Data: {0}".format(thisData['config']))
                getConfig.sendConfig(URL2, thisData['config'])
                self.navigation = self.incrLine
                charlieimage.dispLogo("Saved! Restarting...")
                # gd.draw_confirmation("S A V E D !", "Sent valid config", "RESTARTING", 255, 0)
                # print thisData['config']
            else:
                print result
                self.navigation = self.incrLine
                gd.draw_confirmation('FAILED', result['message'], '', 255, 0)
        elif(addorsub == 1):
            self.navigation = self.incrLine
            gd.screenChosen = gd.menuStack.pop()
            gd.draw_confirmation('CANCELED', 'Returning to main menu', '', 255, 0)
        elif(addorsub == 2):
            self.displayThis()

    def displayEdit(self, underline_pos, underline_width):
        """screen to display when editting value."""
        gd.draw_screen_ul(self.title, "Are You Sure?", self.navigation, 255, 0, 0, 0)

class RestartScript(Screen):
    """Class for sending config. Extends Screen."""

    def __init__(self, type, title, value):
        """Our initialization for the confSend subclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "confScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        global humanTranslations
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title

        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = value
        self.val0 = "Yes"
        self.val1 = "No"
        self.incrLine = "<--    Send    -->"
        self.editLine = self.val0 + "          " + self.val1
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        global level
        if(addorsub == 0):
            print thisData['config']
            gd.menuDelete()
        elif(addorsub == 1):
            self.navigation = self.incrLine
        elif(addorsub == 2):
            self.displayThis()

    def displayEdit(self, underline_pos, underline_width):
        """screen to display when editting value."""
        gd.draw_screen_ul(self.title, " ", self.navigation, 255, 0, 0, 0)


class WifiScan(Screen):
    """Class for scanning wifi networks. Extends Screen."""
    def __init__(self, type, title):
        """Our initialization for the confSend subclass."""
        # String: type of screen - "readOnly", "subMenu", "editable"
        self.type = type
        self.screenType = "BooleanScreen"
        self.valueLength = 0
        # String: Line one on the LCD Screen
        global humanTranslations
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.dataName = title

        # String: line two on the LCD Screen
        self.childIndex = 0
        self.value = "Scan for Wifi Networks"
        self.val0 = "Yes"
        self.val1 = "No"
        self.incrLine = "<--    Scan    -->"
        self.editLine = ""
        self.editMode = False
        if(self.type == "readOnly"):
            self.navigation = self.navLine
        elif(self.type == "subMenu"):
            self.navigation = self.navLine
        else:
            self.navigation = self.incrLine

    def editVal(self, index, addorsub):
        self.value = "Scanning..."
        self.displayThis()
        gd.wifiList = getConfig.getID_List(URL3)
        self.editMode = False
        self.value = "Scan for Wifi Networks"
        self.navigation = self.incrLine
        print gd.wifiList
        gd.screenChosen = gd.menuStack.pop()
        gd.draw_confirmation("Finished Scanning", "Returning to", "parent menu.", gd.fillNum, gd.fillBg)
