# Readme

### Files

* charlie2.py (rename)

  This is the main script. It sets up the button callbacks, builds all of the menus, defines the dictionary for retrieving data, and initializes the screen objects and timers.

* globalDependencies.py

  This is where most global values are declared so that they may be used by different files in the project. Helper classes such as Autovivification and stack are also declared here.

* layout.json

  This is the structure for the menu. The json is parsed and is used as an instruction of sorts to build the menu. For instance:

  ```
  "wifi-iface": {
      "SSID Selection": {
          "ssid": [
              "stringscreen",
              "readonly",
              "Current SSID"
          ],
          "wifiScan": [
              "wifiscan",
              "editable",
              "Wifi Scan"
          ],
          "networks": [
              "ssidChooser",
              "editable",
              "Choose an SSID"
          ],
          "manualEntry": [
            "HiddenSSID",
            "editable",
            "Manual SSID Entry"
          ]
      },
```

  The JSON above is instructions on how to handle the SSID setup menu for any WIFI Interface that is detected. It states that there is a wifi interfaces (which will programmatically issued a human-readable title). Within the wifi interface menu, there is an SSID Selection submenu with four screens: "Current SSID", "Wifi Scan", "Choose an SSID", and "Manual Entry". Each member of the array in each screen serves a purpose. For instance, the manualEntry array has "HiddenSSID", "editable", and "Manual SSID Entry" as its first, second and third values respectively. The first value dictates the class of the screen, the second value determines whether or not it is able to be edited by the user at runtime, and the third value is the human readable title for the screen.

  Charlie2.py is ultimately what builds the menu structure from the JSON file.

* getConfig.py (poorly named)

  This is the file that holds most of the communication to outside sources. One such communication is grabbing information from piNetConfig, which is used in combination with layout.json to build certain menu structures and populate screens with real data.

* screens.py

  This file contains all of the screen class definitions for the project. It also contains most functions that deals with the screens.

* validate.py

  This file is used for validating configurations before sending off to piNetConfig - it allows the application to display warning messages that piNetConfig would not normally sending

* charlieimage.py (rename)

  Used to display startup splash image on LCD

### Top-Level Screens

* Network Status

  This is where current network information is stored. Information within this menu is updated on an interval while it is in view. The submenus of Network Status consist of the various interfaces found on the device, and within those are current settings such as the ip address, host name, SSID, etc.

* MagWebPro Status

  Currently, the only information within this is the Host name of the device

* Date and Time

  This consists of one screen which displays the date and time - it updates every second. The date and time can be changed in a menu under the main setup menu.

* Tools

  Currently, this houses screens that allow the user to ping, save changes, or restart the program. This may be removed and have its contents divided amongst other parts of the structure at some point.

* Main Setup Menu

  This is where settings such as Date and Time can be adjusted. This is also where certain network settings can be configured.

### Class Descriptions

This section is mainly regarding the classes for Screens. The main screen class is the only one that will have its attributes and methods defined explicitly in this section. There are many different classes that extend the main screen class.

#### Screen

  This class sets up the model and creates the means for the view for a "screen" on the LCD.

  **Class Attributes:**
  * **screenType**
  * **objectType**
  * **interfaceType**
    This is the type of interface that this screen belongs to - it assists certain functions when building the menu structure
  * **title**
    The human readable title to display on the LCD
  * **titleOrig**
    The non human readable title to identify the screen with
  * **value**
    the non-human readable value that is added to the config
  * **valueLength**
    the length of the string that represents the value - this is used when editing the value at run time. It allows certain methods to check if the end of the value is reached and end "editing mode"
  * **screens []**
    This is for screen objects that serve as menus - this is where all child-screens are stored so that we can iterate through them and display them in order
  * **childIndex**
    For screens that serve as menus, this is used to keep track of which screen is being displayed. For screens that do not serve as menus, this is a means of keeping track of which character in a string that we are editing.
  * **editMode**
    This is used to keep track of whether or not this screen is being edited
  * **navigation**
    this is used to determine which navigation style is shown on the third line of the LCD.
  * **underline_pos and underline_width**
    passed to methods that display the screen on the lcd. These are used to determine the size and position of the cursor that appears under characters in the value string.

  **Class Methods:**

  * **initScreenList(self, screens)**
    Takes in an array of screens and initializes the screens attribute of the object

  * **insertScreenList(self, screen, index)**
    Takes in a screen object and an index, and inserts that screen within the screen list at the index specified

  * **prependScreenList(self, screen)**
    Adds a screen to the beginning of the screen list

  * **appendScreenList(self, screen):**
    adds a screen to the end of the screen list

  * **displayThis(self)**
    sets global inView to the screen being displayed, calls the draw_screen function which displays the screens values on the LCD

  * **setChildIndex(self, value)**
    sets the childIndex attribute of the object to a the passed values

  * **screenChosen(self)**
    displays the first screen in this object's list of screens

  * **getTitle(self)**
    getter for the title attribute

  * **setHrtitle(self, title)**
    setter for the human readable titleOrig

  * **getInterfaceType(self)**
    getter for interfacetype attribute

  * **changeType(type, navigation)**
    changes the type to the passed arg as well as the navigation

  * **setConfirmation(self, conf1, conf2)**
    sets line1 and line2 of the confirmation screen for this object

  * **getConfirmation(self)**
    gets the confirmation lines for this object

  * **updateSelf(self)**
    used for current settings screens: updates the value depending on which class extends


### Readme TODO

* screen flow diagrams
* sample Configurations
* screen explanations
