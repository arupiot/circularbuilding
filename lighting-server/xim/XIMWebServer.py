
# Flask-based web server using REST API and JSON packets
# V1.2.4

"""
Revision History:

V1.0.1
- Added ximGateway.py
- Changed the device real-time data url from /xim to /device
- Added /device/history for providing the histograms and hours
- Added /devices for providing the device information (name, flux, etc) of all
    devices
- Added multi-threading for running ximGateway (POOL_TIME interval is 0.01 s)
- Handles POST of intensity, not indicate
- Added a CTRL-C handler so that the connections are closed

V1.0.2
- Removed console printouts of data
- Removed CORS usage

V1.0.3
- Added CORS back

V1.0.4
- Added functionality for 'intensity' and 'indicate'

V1.1.1
- Interprets POST commands to /devices URL as a broadcast command

V1.1.5
- Added exception logging to ExceptionLog.txt

V1.2.4
- For the SetIntensity function's deviceId parameter, changed the broadcast value
    from None to ximGateway.DEMO_ID_ALL_DEVICES (-1)

Unless otherwise stated, the XimWebServer is updated to match the ximGateway
version number
"""


import threading
import atexit
import time
import signal
from flask import Flask,  request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
#from flask_cors import CORS

import json
import sys

import ximGateway, cfg


##try:
##    # The typical way to import flask-cors
##    from flask.ext.cors import CORS
##except ImportError:
##    # Path hack allows examples to be run without installation.
##    import os
##    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
##    os.sys.path.insert(0, parentdir)
##
##    from flask.ext.cors import CORS


POOL_TIME = 0.01 #Seconds

# variables that are accessible from anywhere
commonDataStruct = {}

# lock to control access to variables
dataLock = threading.Lock()

# thread handler
yourThread = threading.Thread()
yourThread.daemon = True

threadStarted = False

def create_app():
    global threadStarted

    app = Flask(__name__)
#    cors = CORS(app)

    def interrupt():
        global yourThread
        yourThread.cancel()

    def doStuff():
        global commonDataStruct
        global yourThread
        with dataLock:
            # Do your stuff with commonDataStruct Here
            ximGateway.Run()

        # Set the next thread to happen
        try:
            yourThread = threading.Timer(POOL_TIME, doStuff, ())
            yourThread.daemon = True
            yourThread.start()
        except KeyboardInterrupt:
            print("Ctrl-c pressed ...")
            sys.exit(1)

    def doStuffStart():
        # Do initialisation stuff here
        global yourThread
        global threadStarted

        ximGateway.Start()
        # Create your thread
        if(threadStarted == False):
            try:
                yourThread = threading.Timer(POOL_TIME, doStuff, ()) #this is where doStuff is launched the first time
                yourThread.start()
                threadStarted = True
            except KeyboardInterrupt:
                print("Ctrl-c pressed ...")
                sys.exit(1)

    # Initiate
    doStuffStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app

app = create_app()


# Index page
@app.route('/')
def index():
    return "XIM Server. Data is available at /devices/(Index)"

# List of all devices
@app.route('/devices', methods=['GET', 'POST'])
def ximAllDevices():
    if request.method == 'POST':
        data = request.get_json()
        if(data and 'intensity' in data):

            try:
                intensity = float(data['intensity'])

                ximGateway.SetIntensity(ximGateway.DEMO_ID_ALL_DEVICES, intensity)
                responseData = {'intensity': intensity}

            except IOError:
                responseData = {'error':'Invalid value for intensity: {0}. Must be a number'.format(data['intensity'])}
    else:
#        DeviceList = ximGateway.ximList()
#        for ListIndex in DeviceList:

        responseData = {'deviceList':ximGateway.ReadAllDeviceInfo()}
    ##    print("\ndata: {0}\n".format(responseData))

    # Reply as a JSON packet
    jData = jsonify(responseData)
    print("\njData: {0}\n".format(jData))
    return jData

# Device-specific XIM
@app.route('/devices/<int:DeviceId>', methods=['GET', 'POST'])
def ximDeviceSpecific(DeviceId):

    if(ximGateway.IsValidDeviceByIndex(DeviceId)):

        # Writing data - Only intensity is supported
        if request.method == 'POST':
            data = request.get_json()
            if(data and 'intensity' in data):

                try:
                    intensity = float(data['intensity'])
#                    print("Received intensity: {0}".format(intensity))

                    ximGateway.SetIntensity(DeviceId, intensity)
                    responseData = ximGateway.ReadRealTimeData(DeviceId)

                except IOError:
                    responseData = {'error':'Invalid value for intensity: {0}. Must be a number'.format(data['intensity'])}

            elif(data and 'indicate' in data):
                try:
                    indicateState = float(data['indicate'])
                    ximGateway.SetIndicate(DeviceId)
                    responseData = ximGateway.ReadRealTimeData(DeviceId)
                except IOError:
                    responseData = {'error':'Invalid value for indicate: {0}. Must be a number (0 = off, non-0 = active)'.format(data['intensity'])}
            else:
                responseData = {'error':'Needs JSON packet with intensity field.'}

        # Reading data - currently returns the part number, temperature, and voltage
        else:
            responseData = ximGateway.ReadRealTimeData(DeviceId)

    else:
        responseData = {'error':'Device {0} not found'.format(DeviceId)}

    # Reply as a JSON packet
    jData = jsonify(responseData)
    print("\njData: {0}\n".format(jData))
    return jData

# Device-specific XIM History
@app.route('/device/<int:deviceNumber>/history', methods=['GET'])
def ximDeviceSpecificHistory(deviceNumber):

    if(ximGateway.IsValidDevice(deviceNumber)):
        responseData = ximGateway.ReadDeviceHistory(deviceNumber)
##        print("\ndata: {0}\n".format(responseData))

    else:
        responseData = {'error':'Device {0} not found'.format(deviceNumber)}

    # Reply as a JSON packet
    jData = jsonify(responseData)
    print("\njData: {0}\n".format(jData))
    return jData

# Indicate function
@app.route('/device/indicate/<int:DeviceId>', methods=['GET', 'POST'])
def ximDeviceIndicate(DeviceId):

    if(ximGateway.IsValidDeviceByIndex(DeviceId)):
        ximGateway.SetIndicate(DeviceId)
        responseData = {'indicate': 'sent command to Device {0}'.format(DeviceId)}

    else:
        responseData = {'error':'Device {0} not found'.format(DeviceId)}

    # Reply as a JSON packet
    jData = jsonify(responseData)
    print("\njData: {0}\n".format(jData))
    return jData

def ctrl_c_handler(signal, frame):
    ximGateway.Close()
    yourThread.cancel()
    print('Goodbye!')
    sys.exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

def myExceptHook():
    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(type, value, tb))
    with open('ExceptionLog.txt','a') as f:
        f.write(message)
    print(message)


#app = Flask(__name__)

#@app.route("/")
#def hello():
#    return "Hello World!"

# Run application
if __name__ == '__main__':
##    app.debug = True

    with open("ExceptionLog.txt","w") as f:
        pass

    sys.excepthook = myExceptHook

    app.run(host='0.0.0.0', port=9000, debug=True, threaded=True)

