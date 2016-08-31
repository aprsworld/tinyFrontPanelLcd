import globalDependencies as gc
humanTranslations = gc.humanTranslations


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
        if title in humanTranslations:
            self.title = humanTranslations[title]
        else:
            self.title = title
        self.titleOrig = title
        self.dataName = title
        # String: line two on the LCD Screen
        self.value = value
        self.childIndex = 0
        self.screens = []
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

    def prependScreenList(self, screen):
        """
        Add screen to beginning of screen list.

        Args:
            screen: the screen object to prepend to the screen list
        """
        self.screens.insert(0, screen)

    def displayThis(self):
        """Draw our screen."""
        global inView
        inView = self
        gc.draw_screen(self.title, self.value, self.navigation, 255, 0)

    def displayEdit(self, underline_pos, underline_width):
        """
        screen to display when editting value.

        Args:
            underline_pos: the x value for the starting point of our underline_pos
            underline_width: the width of the underline
        """
        gc.draw_screen_ul(self.title, self.value, self.navigation, 255, 0, underline_pos, underline_width)

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
        thisData['config'][self.interface]['protocol']['inet'][self.titleOrig] = str(self.addr0)+"."+str(self.addr1)+"."+str(self.addr2)+"."+str(self.addr3)
        print thisData['config']


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
            self.childIndex = self.valueLength
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
