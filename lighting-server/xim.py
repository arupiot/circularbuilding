# lighting control passthough (halcyon and xim)
# Ben Hussey - Sept 16

import requests
import time
from config import STATES

GATEWAY = "http://10.0.0.10:9000/"

def xim_level(device, level):
    data={"intensity": level,}
    return requests.get(GATEWAY + 'devices/' + device, data=data).content

def xim_state(state):
    for group in STATES[state]["xim_levels"]:
        data={"intensity": group[1],}
        for device in group[0]:
            requests.post(GATEWAY + 'devices/' + str(device), json=data).content
            #time.sleep(0.1)
