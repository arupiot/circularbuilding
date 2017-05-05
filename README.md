# Circular Building Code

This is the repository for the code used for the Circular Building, a showcase as part of the London Design Festival 2016 to demonstrate how circular economy thinking can be applied to the built environment.

## Hardware

The core control systems ran on a RaspberryPi, with a secondary RPi providing GPIO output at a remote location for the Velux actuation. Lighting control was by bluetooth (XIM track lighting) and 6LoWPAN via a Halcyon interface connected to the building ethernet network.
A Tinkerforge masterbrick stack with PoE extension provides the sensor inputs (direct integration with OpenHab) and touch interface input.

## Software

There are various modules to provide certain functionality, modules are generally independant REST API endpoints which talk to each other and allow integration into the OpenHab platform.

* pi-gpio-server - a fork of https://github.com/projectweekend/Pi-GPIO-Server which allows REST based control of the GPIO pins. This was used for switching 24V power supplies and for actuation of the velux blinds and windows.
* veluxcontroller - the logic and state monitoring behind the velux blind and window actuation. due to power limitations, not all windows/blinds were allowed to open at once. Uses pi-gpio-server to control the pins.
* tinkerforge_watcher - a script to monitor the state of the capacitive touch inputs (connected via a Tinkerforge hardware stack) which then triggers the appropriate endpoints via the OpenHab REST API.
* lighting-server - an endpoint to provide control the the building lighting systems, parses requests for specific lighting states and forwards commands to halcyon and XIM HTTP APIs.
* circular_sensors - Displays sensor values as coloured circles (behind a physical veneer over the display to the left of the desk)

## Credits
Ben Hussey <ben.hussey@arup.com>
