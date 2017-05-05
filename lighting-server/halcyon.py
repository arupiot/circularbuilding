# lighting control passthough (halcyon and xim)
# Ben Hussey - Sept 16

import requests
from config import STATES

DEVICE = "http://10.0.0.60/"
AUTH = ('admin', 'gup1t1m3')

def halcyon_level(room, level):
    data={"roomId": room, "luminanceTarget": level,}
    return requests.get(DEVICE + 'api/rooms/luminanceTarget',
                        auth=AUTH, data=data).content

def halcyon_state(state):
    for room, level in STATES[state]["halcyon_levels"].items():
        data={"roomId": room, "luminanceTarget": level,}
        print requests.post(DEVICE + 'api/rooms/luminanceTarget',
                     auth=AUTH, json=data).content
