# velux window controller (via Pi-GPIO-Server)
# Ben Hussey - Sept 16

import time
import requests
from datetime import datetime, timedelta
from config import THINGS, ACTIONS, STATES

class VeluxController():
    all_things = []
    action_queue = []
    current_action = None

    def __init__(this):
        this.all_things = []
        for tid in THINGS:
            Thing(this, tid)
            this.all_things.append(Thing(this, tid))
        this.set_off()

    def get_state(this, tid):
        this.update()
        for thing in this.all_things:
            if thing.tid == tid:
                return thing.state
        return None

    def set_state(this, tid, state):
        for thing in this.all_things:
            if thing.tid == tid:
                thing.state = state
        return None

    def add_action(this, tid, action):
        this.update()
        for thing in this.all_things:
            if thing.tid == tid:
                thing = thing
        if not this.current_action:
            this.current_action = Action(this, tid, action)
            this.current_action.trigger_action()
        else:
            for queue in this.action_queue:
                if queue.tid == tid:
                    this.action_queue.remove(queue)
            this.action_queue.append(Action(this, tid, action))
            if tid != this.current_action.tid:
                this.set_state(tid, 5)

    def set_off(this):
        for tid in THINGS:
            for pin in THINGS[tid]["pins"]:
                url = ("http://" + pin["device"] +
                       "/api/v1/pin/" + str(pin["pin"]))
                data = {"value": 1}
                # print "sent " + str(data) + " to " + url
                try:
                    requests.patch(url, data=data, timeout=0.5)
                except:
                    pass
        time.sleep(0.3)

    def update(this):
        if this.current_action:
            if this.current_action.completed:
                if this.current_action.completed < datetime.now():
                    if this.current_action.action == 0:
                        this.set_state(this.current_action.tid, 1)
                    if this.current_action.action == 1:
                        this.set_state(this.current_action.tid, 2)
                    this.current_action = None
                    if not this.action_queue:
                        this.set_off()
        if this.action_queue and not this.current_action:
            this.current_action = this.action_queue.pop(0)
            this.current_action.trigger_action()


class Action():
    controller = None
    completed = None
    tid = None
    action = None

    def __init__(this, v, tid, action):
        this.controller = v
        this.tid = tid
        this.action = action

    def trigger_action(this):
        this.controller.set_off()
        for pin in THINGS[this.tid]["pins"]:
            if pin["action"] == ACTIONS[this.action]:
                url = ("http://" + pin["device"] +
                       "/api/v1/pin/" + str(pin["pin"]))
                data = {"value": 0}
                # print "sent " + str(data) + " to " + url
                try:
                    requests.patch(url, data=data, timeout=0.5)
                except:
                    pass
        if this.action == 0:
            this.controller.set_state(this.tid, 3)
        if this.action == 1:
            this.controller.set_state(this.tid, 4)
        this.completed = datetime.now() + timedelta(seconds=THINGS[this.tid]["time"])


class Thing():
    controller = None
    tid = None
    state = 0

    def __init__(this, v, tid):
        this.controller = v
        this.tid = tid
