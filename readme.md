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


### Readme TODO

* screen flow diagrams
* sample Configurations
* screen explanations
