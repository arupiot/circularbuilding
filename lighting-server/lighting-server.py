# lighting control passthough (halcyon and xim)
# Ben Hussey - Sept 16

from bottle import route, run, HTTPError

from config import STATES, ROOMS
from halcyon import halcyon_state, halcyon_level
from xim import xim_state

@route('/level/<room>/<level>/')
def level(room, level):
    if int(room) not in ROOMS:
        return HTTPError(404, "Page not found")
    if 0 > int(level) or int(level) > 100:
        return HTTPError(404, "Page not found")
    return halcyon_level(int(room), int(level))


@route('/state/<state>/')
def state(state):
    if int(state) not in STATES:
        return HTTPError(404, "Page not found")
    halcyon_state(int(state))
    xim_state(int(state))

run(host='0.0.0.0', port=8000, debug=True, threaded=True)
