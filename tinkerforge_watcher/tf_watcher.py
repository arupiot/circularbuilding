# tinkerforce sensor watching script
# Ben Hussey - Sept 16

import requests
import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_multi_touch import BrickletMultiTouch

LIGHTING = "http://10.0.0.10:8000/"
VELUX = "http://10.0.0.10:7000/"

HOST = "10.0.0.40"
PORT = 4223
UID = "zzs"

# Callback function for touch state callback
def cb_touch_state(state):
    if state & (1 << 12):
        pass

    if (state & 0xfff) == 0:
        pass
    else:
        try:
            if state & (1 << 0):
                # Party Mode
                #"Party Mode"
                requests.get(LIGHTING + 'state/0/', timeout=2).content
            if state & (1 << 1):
                # Work Mode
                #"Work Mode"
                requests.get(LIGHTING + 'state/1/', timeout=2).content
            if state & (1 << 2):
                # Relax Mode
                #"Relax Mode"
                requests.get(LIGHTING + 'state/2/', timeout=2).content
            if state & (1 << 3):
                # Sleep Mode
                #"Sleep Mode"
                requests.get(LIGHTING + 'state/3/', timeout=2).content
            if state & (1 << 4):
                # Toggle Windows
                #"Toggle Windows"
                requests.get(VELUX + 'toggle/1/', timeout=2).content
                requests.get(VELUX + 'toggle/3/', timeout=2).content
            if state & (1 << 5):
                # Toggle Blinds
                #"Toggle Blinds"
                requests.get(VELUX + 'toggle/2/', timeout=2).content
                requests.get(VELUX + 'toggle/4/', timeout=2).content
        except:
            pass


if __name__ == "__main__":
    ipcon = IPConnection()
    mt = BrickletMultiTouch(UID, ipcon)

    ipcon.connect(HOST, PORT)
    time.sleep(1)

    mt.recalibrate()
    mt.register_callback(mt.CALLBACK_TOUCH_STATE, cb_touch_state)

    #previos_state = ""
    #while True:
    #    state = mt.get_touch_state()
    #    if state != previous_state:
    #        cb_touch_state(state)
    #    previous_state = state
    #    time.sleep(0.5)

    raw_input("Press key to exit\n") # Use input() in Python 3
    ipcon.disconnect()
