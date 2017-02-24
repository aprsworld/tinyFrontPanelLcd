# Readme

### Requires

#### Adafruit Python SSD1306 Library
https://github.com/adafruit/Adafruit_Python_SSD1306

Install with ````sudo python setup.py install````

#### Adafruit Python GPIO Library
https://github.com/adafruit/Adafruit_Python_GPIO

Install with instructions from README.md

#### python-pil 
````apt-get install python-pil````

#### python-dateutil
````apt-get install python-dateutil````

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

#### Classes that extend screen:

**StringScreen**

  This screen has a value that represents a string. It is used for things like manual entry of SSID or wifi pass key. It can also be used to display a read only setting. For items that are not readonly, it will reference a character map which is essentially an array of characters. It iterates through the indexes in the array and displays a character depending on the numerical index.

**NetworkScreen**

  This screen has a value that consists of 4 octets. It is used to display an ip4 address.
  When editing this screen, the octets are treated as integers  between 0-255. The user can edit the hundreds place, tens place, and ones place. This allows the user to quickly increment the number instead of tapping the button 255 times.

**BooleanScreen**

  This screen has two values passed to its __init__ method. The actual value of the screen will be one of these values.

**DateTimeScreen**

  This screen has a value that represents date in the following format: YYYY-MM-DD hh:mm:ss. It can be read only or editable.

**ListScreen**

  This screen is meant for any setting that has a list of possible values. An use case is a list of SSIDs to choose from. The __init__ function accepts an argument called "valsList" which is the array that holds all of the possible values.

All other screen classes are slight variations of the above with their own specific use case.

### Sample Configurations

#### Configuration example 1

This is a configuration with eth0 and wlan0 interfaces. The wlan0 is configured to connect to an SSID (aprsworld) using WPA/WPA2 encryption.

```
"config": {
      "lo": {
          "allow": "auto",
          "protocol": {
              "inet": {
                  "method": "loopback"
              }
          }
      },
      "eth0": {
          "allow": "auto",
          "protocol": {
              "inet": {
                  "method": "dhcp"
              }
          }
      },
      "wlan0": {
          "allow": [
              "hotplug",
              "auto"
          ],
          "protocol": {
              "inet": {
                  "method": "dhcp",
                  "wpa-ssid": "aprsworld",
                  "wpa-ap-scan": "1",
                  "wpa-scan-ssid": "1",
                  "wpa-psk": "\"zestopenguin\""
              }
          }
      },
      "system": []
  }
```

#### Configuration example 2

This is a configuration with eth0 and wlan0 interfaces. The wlan0 is configured to connect to an SSID (linksys) using WEP encryption and static addressing.

```
"config": {
      "lo": {
          "allow": "auto",
          "protocol": {
              "inet": {
                  "method": "loopback"
              }
          }
      },
      "eth0": {
          "allow": "auto",
          "protocol": {
              "inet": {
                  "method": "dhcp"
              }
          }
      },
      "wlan0": {
          "allow": [
              "hotplug",
              "auto"
          ],
          "protocol": {
              "inet": {
                  "method": "static",
                  "wireless-essid": "linksys",
                  "wireless-key": "086FE7A474",
                  "address": "192.168.10.247",
                  "netmask": "255.255.255.0",
                  "gateway": "192.168.10.1"

              }
          }
      },
      "system": []
  }
```

### dhcpcd.conf

  There was an issue where two IP addresses would be assigned to the same interface. This was because /etc/network/interfaces and /etc/dhcpcd.conf were both assigning DHCP leases to the interface in question. In order to avoid this, there is a line at the bottom of dhcpcd.conf that tells the service to ignore certain interfaces. This needs to be configured at setup to deny all interfaces that are set up on the device. The line within the file is delimited by spaces and looks like this:

  denyinterfaces eth0 wlan0

  any other interfaces that need to be added to the list can just be added to the end separated by spaces.

### Startup script

  There is a way to enable the python scripts at startup and have it startup by itself. This is beneficial because when the user makes changes to the configuration and reboots the system, it will come up automatically after it starts up. This is done by putting this line:

  ```
  /home/pi/Adafruit_Python_SSD1306/tiny_front_panel_lcd/startup.sh &
  ```

  within the /etc/rc.local script which already runs on boot. What this line does, is it gives an absolute path (since the environment isn't set up) to a script within the project folder that runs all of our scripts. You can find startup.sh within this repository to see exactly what it is doing.

### Readme TODO

* screen flow diagrams
