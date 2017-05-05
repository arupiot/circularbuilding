XIM-BLE Gateway/Webserver readme.txt
Date: 12 Aug 2016

The XIM-BLE Gateway/Webserver reference application code base provided 
in this repository has been confirmed to run on a Raspberry Pi 3 running 
Raspbian GNU/Linux 8 (jessie). To run the application code, a 
Bluegiga BLED112 dongle will need to be installed in one of the USB 
ports - yes, the Raspberry Pi 3 has a native Bluetooth Low Energy 
interface integrated onboard, but the primary API function library 
(ble_xim.py) was developed to interface to the BLED112 dongle and the
port to the native interface is work to be completed... 

As of today (12 Aug 2016):
--------------------------
- The primary API function library (ble_xim.py)
as well as the underlying BLED112 API library (bglib.py) can be 
considered completed and reasonably well vetted since both are the 
underpinnings of our PC based Control Panel application. The only item
to note is that ble_xim.py is updated on a regular basis as we continue
to enhance the functionality of our XIM-BLE modules.

- The gateway (ximGateway.py) and webserver (XIMWebServer.py) code can 
best be described as work in progress and they only scratch the surface
of what the XIM-BLE is capable of. They both run, but they are a bit 
clunky and limited. It also needs to be pointed out that XIMWebServer.py
only uses Flask's built-in server and IS NOT SUITABLE FOR PRODUCTION. It
is fine for development and debugging, but should not be used in a real
world deployment.

- Documentation is non-existant. The code is supplied as-is with no 
promises of either real or implied usability or support. You will need 
to read the code to determine how to collect data from a BLE enabled XIM
device and how to control BLE enabled XIM devices. The gateway and 
webserver code provide a basic example of function calls into the API
library.

The application is designed/developed for Python 2.7, and the following
preparation steps should be taken prior to trying to run the 
application.

$ sudo apt-get update        #update and upgrade built-in libraries
$ sudo apt-get upgrade
$ sudo apt-get dist-upgrade
$ sudo shutdown -r now       #reboot to apply changes
$ #pi-bluetooth should already be installed, but it doesn't hurt to check
$ sudo 	 
$ sudo apt-get install python-pip #install the Python pip installer
$ sudo apt-get install python-flask #Python 2.7 Flask microframework
$ sudo apt-get install python-crypto #encryption libraries
$ #avahi-daemon should be installed, but it doesn't hurt to check
$ sudo apt-get install avahi-daemon #provides local mDNS name services

The following may also need to be installed:

$ sudo pip install pycryptodome #encryption library extensions

Additional useful tools:

$ sudo apt-get install xrdp #x-windows remote desktop
$ sudo apt-get install geany #geany editor/IDE 
$ sudo apt-get install iceweasel #firefox browser
$ sudo apt-get install codeblocks #codeblocks IDE
