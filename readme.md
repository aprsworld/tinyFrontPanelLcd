# Readme

### Top-Level Screens

* Wireless Interface Screens

  These are typically in the format: "wlan(wlan0)" This is where you can see current settings for a wireless interface and configure a select number.

* Ethernet Interface Screens

  These are typically in the format: "Ethernet (eth0)" Just like wlan screens, you can configure and see current settings for ethernet interfaces.

* Configurations

  This is the top-level menu that is used for options having to do with the configuration. Currently the only option this contains is "send config" which validates and sends a copy of the configuration to the back-end

* Manage Interfaces

  This is the top-level menu for Adding and deleting interfaces. Currently, logical and virtual interfaces may be added. Interfaces may also be deleted using one of the menu items within this top-level menu.

* Time and Date

  The system time and date may be viewed here. It can also be editted, though this currently is not sent anywhere and resets once the program is restarted. In the future, this may need to be used to actually edit the date and time on the system.

### Files

* charlie.py (needs renaming)

  This does the majority of the work. It sets up the various screen classes as well as the logic for navigating between the screens.
  It also is in charge of editing the configuration.

* getConfig.py (should also be renamed)

  This was originally used for just getting the config. I did not know how extensive it would be so I put the function in its own file. The file is now in charge of sending the config among other operations.

* charlieimage.py (should also be renamed)

  This is in charge of displaying the logo for the first few seconds of run time

### Readme TODO

* screen flow diagrams
* sample Configurations
* screen explanations
