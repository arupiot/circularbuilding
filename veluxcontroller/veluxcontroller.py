# velux window controller (via Pi-GPIO-Server)
# Ben Hussey - Sept 16

from bottle import route, run, HTTPError

from logic import VeluxController
from config import THINGS, ACTIONS, STATES

v = VeluxController()


@route('/statuses/')
def statuses():
    v.update()
    text = ""
    for thing in v.all_things:
        text = text + str(thing.tid) + " " + STATES[thing.state] + "<br/>"
    return text


@route('/status/<tid>/')
def status(tid):
    if int(tid) not in THINGS:
        return HTTPError(404, "Page not found")
    return STATES[v.get_state(int(tid))]


@route('/action/<tid>/<action>/')
def action(tid, action):
    if int(tid) not in THINGS:
        return HTTPError(404, "Page not found")
    if int(action) not in ACTIONS:
        return HTTPError(404, "Page not found")
    return v.add_action(int(tid), int(action))

@route('/toggle/<tid>/')
def toggle(tid):
    if int(tid) not in THINGS:
        return HTTPError(404, "Page not found")
    if not v.get_state(int(tid)) or v.get_state(int(tid)) == 0:
        return v.add_action(int(tid), 0)
    if v.get_state(int(tid)) == 1:
        return v.add_action(int(tid), 1)
    if v.get_state(int(tid)) == 2:
        return v.add_action(int(tid), 0)
    if v.get_state(int(tid)) == 4:
        return v.add_action(int(tid), 0)
    if v.get_state(int(tid)) == 5:
        return v.add_action(int(tid), 0)

run(host='0.0.0.0', port=7000, debug=True)
