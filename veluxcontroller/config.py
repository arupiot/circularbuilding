# velux window controller (via Pi-GPIO-Server)
# Ben Hussey - Sept 16

DEVICES = {
    "near": "10.0.0.10:5000",
    "far": "10.0.0.20:5000"
}

THINGS = {
    3: {
        "tid": 1, "label": "Office Windows", "time": 45, "pins":
        [
            {"pin": 25, "device": DEVICES['near'], "action": "open", },
            {"pin": 25, "device": DEVICES['far'], "action": "open", },
            {"pin": 24, "device": DEVICES['near'], "action": "close", },
            {"pin": 24, "device": DEVICES['far'], "action": "close", }
        ]},
    4: {
        "tid": 2, "label": "Office Blinds", "time": 30, "pins":
        [
            {"pin": 14, "device": DEVICES['near'], "action": "open", },
            {"pin": 8, "device": DEVICES['far'], "action": "open", },
            {"pin": 18, "device": DEVICES['near'], "action": "close", },
            {"pin": 7, "device": DEVICES['far'], "action": "close", }
        ]},
    1: {
        "tid": 3, "label": "Kitchen Windows", "time": 45, "pins":
        [
            {"pin": 23, "device": DEVICES['near'], "action": "open", },
            {"pin": 14, "device": DEVICES['far'], "action": "open", },
            {"pin": 15, "device": DEVICES['near'], "action": "close", },
            {"pin": 15, "device": DEVICES['far'], "action": "close", }
        ]},
    2: {
        "tid": 4, "label": "Kitchen Blinds", "time": 30, "pins":
        [
            {"pin": 7, "device": DEVICES['near'], "action": "open", },
            #{"pin": 8, "device": DEVICES['far'], "action": "open", },
            {"pin": 8, "device": DEVICES['near'], "action": "close", },
            #{"pin": 7, "device": DEVICES['far'], "action": "close", }
        ]},
}

ACTIONS = {
    1: "open",
    0: "close",
}

STATES = {
    0: "Unknown/Stopped",
    1: "Closed",
    2: "Open",
    3: "Closing",
    4: "Opening",
    5: "Waiting",
}
