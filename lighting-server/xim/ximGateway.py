# XIM Gateway that collectes the XIM data
# V1.2.5
"""
Revision History:

V1.0.1
- Added power histogram  ['<2W','2-7W','7-14W'] to the historical data
- Store ximIdList.txt in \BLE directory
- Added demoAirQuality to the real-time data
- Turned off console printing
- Exits if it can't connect to the BLED dongle
- Changed the SIMULATE_DEVICE values to be closer to the margins

V1.0.2
- Added units to cri, cct, and flux when reporting the values

V1.0.3
- Added functionality for the SetIntensity and SetIndicate functions

V1.0.4
- Added the BLE address to the GetInfo response

V1.0.5
- Changed the Run process to disconnect after pulling data, so that only a max
    of connection is maintained at a time
- Created commandQueue to keep track of the address, intensity, and time
    for sending the intensity packets (including indicate).
- Indicate is set to have INDICATE_FLASH_INTERVAL = 0.5 and INDICATE_FLASHES = 3
- Changed rssiThresholds elements from 6 to 5
- Added fixture information to the GetInfo response
- Changed demoAirQuality to 500 +/10% random
- Added importing of ble_xim.py from /DALI Master
- Added error checking on intensityHistogram before updating powerHistogram

V1.0.6
- Incorporates the ble_xim V1.15 updates

V1.0.7
- Incorporates the ble_xim V1.16 updates

V1.0.8
- Fixed the length check after FetchHistogram (buckets make length smaller than
    bytes)
- Changed HISTORY_UPDATE_INTERVAL from 30.0 to 180.0
- Changed REAL_TIME_UPDATE_INTERVAL from 0.5 to 1.0
- Reads fixtureManufacturer (field 3) and fixturePartNumber (field 4) from
    ximIdList.txt
- Added fwVersionIsNewest field, but havent implemented the functionality
    behind it yet
- Added a third device for SIMULATE_DEVICES
- Incorporates the ble_xim V1.17 updates

V1.0.9
- Added DISCOVER_DURATION to give the BLE master time to discover new devices
- Added PERSISTENT_CONNECTION option (currently disabled)
- Incorporates the ble_xim V1.18 updates
- Added a check for ble_xim_IsDeviceConnecting while waiting for the connection

V1.0.10
- Incorporates the ble_xim V1.19 updates

V1.0.11
- Changed sendIntensityQueue to a DALI commandQueue so that RECALL_MAX, etc
    can be included
- Added minLevel, maxLevel, and fadeTime to the ximIdList
- At startup, it will send commands to set the minLevel, maxLevel, and fadeTime
- The 0-100.0 intensity value from the server will be converted to a DALI level
    where 0 = off, 1 = DALI minimum level, 100 = DALI maximum level, 50 =
    50/99 of (DALI max - DALI min)
- Changed ximIdList to a csv file and changed the address representation from
    [x,x,x,x,x,x] to x.x.x.x.x.x, since commas would throw off the csv format.
    Also added a header row.
- Added AVERAGE_CONNECT_DURATION (0.5s) to the start of the flash sequence
    to give time for the initial connection to take place. Otherwise, the first
    flash can be really short
- When the commandQueue is processed, it first handles the connection
    of the device that is in the data collecting section (pollingDevice)
- Removed UPDATE_DEVICE_INFO and just call FetchDeviceInfo when
    (device.partNumber == None)
- Incorporates the ble_xim V1.20 updates

V1.0.12
- Fixed the missing disconnectDevice = False statement in the commandQueue
    handler
- Added Gateway version printout
- Incorporates the ble_xim V1.21 updates

V1.0.13
- Added fields in ximIdList.csv to simulate temperature and intensity histograms,
    input voltage offset, and a maximum temperature with a time constant
- For the simulated max temperature, the simulated temperature is calculated by
    newTemperature = coreTemperature + (simTemperatureMax - coreTemperature) *
    intensity / 100.0
  This value is filtered using an IIR filter using the time constant as follows:
      f[n] = (f[n - 1] * (TC - 1) + input) / TC
- It makes sure that there's valid temperature and intensity histograms and
    valid operating hours before it waits for HISTORY_UPDATE_INTERVAL
- Incorporates the ble_xim V1.22 updates

V1.0.14
- Fixed the ximIdList initialization for new devices or a new file

V1.0.15
- Set the filtered temperature immediately to the new simulated temperature
    (newTemperature) when the system first starts up

V1.0.16
- Changed the signal strength to report 0 if there are MAX_CONNECTION_FAILS (3)
    consecutive connection fails or if the packet success rate is less than
    SUCCESS_RATE_FAIL_LEVEL (50%). It reports 1 if the packet success rate is
    less than SUCCESS_RATE_WARNING_LEVEL (95%). The packet rate is measured
    over the last MAX_PACKET_LOG_LENGTH (30) packets.
    Otherwise, the signal strength is based on RSSI and is reported as a
    number between 1 (<-90dBm) to 5 (>-60dBm)
- Incorporates the ble_xim V1.23 updates

V1.0.17
- Added Success Rate Parameters.txt to allow configurability of how the
    signal_strength is reported when there are packet failures
- Packet failures don't change the signalBars variable. Instead, the reported
    signal_strength is only modified in GetRealTimeDataList so that when
    the packet success rate improves, the signalBars will still be accurate.
    Demo_UpdateSignalStrength is still called when the successRate is low.
- Removed connectionFails, so only successRate is used
- Moved the packetSuccessLog.pop before the successRate calculation so that
    the proper length is averaged.

V1.0.18
- Added success_rate_null_data_on_error to show/not show all zero's when
    there is a success rate error. Configurable in Success Rate Parameters.txt

V1.0.19
- Set PERSISTENT_CONNECTION to True and limited the number of devices to 3

V1.0.20
- Created the file Gateway Parameters.txt to set the peristent connection
    and maximum devices to connect to
- Disables scanning when it has found max_devices and all devices have been
    successfully connected to in the last MAX_LAST_CONNECTION_PERIOD (10 s)

V1.0.21
- In persistent_connection mode, made sure it doesn't disconnect the
    pollingDevice

V1.0.22
- Disables scanning when it has found max_devices and all devices have
    connected at least once. Scanning will never be enabled again (until
    application is restarted)

V1.1.0
- Added DALI support. Can find addressed and un-addressed devices
- Created DALI directory to store separate ximIdList
- In Gateway Parameters.txt, added protocol select for BLE or DALI
    (default is DALI) and moved this file to the main directory
- Made capturing all of the log data optional (CAPTURE_ALL_LOG_DATA). By
    default, this is off, so that it doesn't waste time collecting data that
    isn't used
- Created SendDaliCommand and GetBankData to abstract out the BLE/DALI selection
- Moved ProcessPacketComm from FetchDiagnosticData to GetBankData
- Moved FetchDiagnosticData from an if to an elsif so that a history update and
    real-time update can't happen in the same cycle
- Incorporates the ble_xim V1.31 updates

V1.1.1
- When multiple devices have the same DALI address, it clears their addresses
- For DALI, it will broadcast set intensity commands when all devices have
    the same minimum and maximum levels or if the intensity is 0
- Added in sendTwice and isQuery parameters for SendDaliCommand

V1.1.2
- Incorporates the ble_xim V1.33 updates, including faster UUID discovery
- Automatically switches between DALI and BLE if the first try failed

V1.1.3
- Handles devices that don't have a matching GTIN in DeviceInfo.txt
- Incorporates the ble_xim V1.34 updates (configurable whitelisting)

V1.1.4
- The reported device name is retrieved from the scan response packet and the
    name is stored in ximIdList.csv

V1.1.5
- Incorporates the ble_xim V1.38 updates


V1.1.6
- Changed the default persistent_connection to False ('N')
- Removed the simulated offsets from ximIdList (SIMULATED_OFFSET_ADD_ENABLED =
    False)
- In ximIdList.csv, changed the max and min levels to be intensity percentages
- Added exception logging to ExceptionLog.txt
- Incorporates the ble_xim V1.39 updates

V1.2.0
- Incorporates ble_xim V2.0.2 updates
- Removed DALI code
- Changed signal bars to be affected by the time since the lastScanTime, not
    connection success rate
- Updated intensity histogram to use the new 4-byte seconds buckets and ranges
- Updated power histogram to use 5W buckets and to calculate the powerMultiplier
    from the model number
- Uses the model number, instead of the GTIN to get the flux,les,cct,cri info
- Retrieves the real-time data from the scanned data
- Only connects once to get all of the device information, configure the levels
    and get the histograms. Then, connects once every 3 minutes for the histograms
- Removed Vf Histograms and the historical data (except hours, power/LED cycles)
- Removed SIMULATE_DEVICES code
- Fixed the intensity scaling
- Updated Demo_InitializeConfiguration to use the SetLightSetup API
- Updated SetIntensity and SetIndicate to use the commandQueue to store the
    ble_xim.BroadcastLightLevel and ble_xim.BroadcastIndicate APIs
- Changed FIXTURE_PART_NUMBER_DEFAULT from LFI0001 to Fixture 1
- Added the Device ID (Logical Address) to ximIdList.csv file. If a device
    doesn't have a device ID (i.e. is 255.255.255.255), it will look at the
    device ID's in the ximIdList.csv, find the maximum and increment by 1

V1.2.1
- Moved the max/min intensity and fade time configuration from ximIdList to
    Gateway Parameters. A single value is used for all devices
- When the max/min intensity fields in Gateway Parameters are not a number
    (e.g. Unchanged), the max/min levels will not be written to the device.
- Added connectable configuration in Gateway Parameters. Changed the default
    to be not-connectable. It will always send the Set Connectable advertisement
    to the corresponding device before it connects.
- If there are MAX_CONNECTION_FAILS (3) consecutive connection fails, the signal
    bars will be set to 1 and the connection will be tested every 1 minute
- Incorporates ble_xim.py V2.0.5 updates

V1.2.2
- Added max_device (default 10) to Gateway Parameters.txt. It limits the number
    of devices that the gateway will store
- Added group_mask (default 255.255.255.255) to Gateway Parameters.txt. The
    gateway will only add devices that are within the mask and broadcast
    commands will only get sent to the group mask
- Changed MAX_INTENSITY_DEFAULT to 100.0 and MIN_INTENSITY_DEFAULT to 1.0
- Only writes the minimum level if the desired level is less than what is
    currently stored in the device

V1.2.3
- Returns an integer for the intensity level, so that the GUI's pop-out
    intensity control doesn't show a long decimal value during the fade
- When the scaled intensity is negative (due to fade to off and the web server's
    minimum intensity not being stored in the device), it reports the scaled
    intensity as 1

V1.2.4
- Cleaned up for customer release. Added comments, renamed the demo-specifig
    functions (Demo_FunctionName) and variables (demoVariableName)
- For the SetIntensity function's deviceId parameter, changed the broadcast value
    from None to ximGateway.DEMO_ID_ALL_DEVICES (-1)
- Incorporates ble_xim V2.0.6 (device ID no longer reversed)

V1.2.5
- Uses the new LogHandler and stores the EventLog file to the \Event_Logs
    directory. The LogHandler will append the timestamp and store the 5 most
    recent event logs.
- Incorporates ble_xim V2.0.8 and LogHandler V2.1 updates

V1.2.6l
- Port to linux (Raspberry Pi initially, then BeagleBone)
    - need to figure out options to use same code base for linux & windows,
    but for now just hard port to linux
- Ripped out all items that were tied to the original LFI demo GUI and would
    not be used in real world deployments.
- Restructured data collection loop to only look at data provided by XBeacon
    advertisements. Connections should only be made for collecting histogram
    data or configuring a device


TODO:
Review
newDevice.demoMaxDaliLevel scaling (including in ximIdListDefaults)
SIMULATED_OFFSET_ADD_ENABLED


******** Update GATEWAY_VERSION *****
"""

import time
import datetime
from os import rename
from os import remove
import os
from math import log10, log
from random import random

import sys
import traceback
##import json

import LogHandler
import cfg


GATEWAY_VERSION = "1.2.6l"

import ble_xim

NEWEST_FW_VERSION = 0.083

DISCOVER_DURATION = 2.0 # Should be greater than the maximum advertising interval
AVERAGE_CONNECT_DURATION = 0.5
MAX_CONNECTION_FAILS = 3
MAX_LAST_CONNECTION_PERIOD = 10.0
MAX_CONNECTION_FAILS = 3
BAD_CONNECTION_TEST_DURATION = 60.0

LAST_SCAN_TIME_ERROR = 10.0
LAST_SCAN_TIME_WARNING = 5.0
SIGNAL_ERROR_CAUSES_NULL_DATA = True

BLE_READ_TIMEOUT = 0.5

UPDATE_OFF = 0
UPDATE_HISTORY = 1

wasStarted = False
connectionAttempted = False
connectionEnableSent = False
commandQueue = []

rssiThresholds = [-90, -80, -70, -60]
RSSI_HYSTERESIS = 3.0

# >>> the following should go into the config file
INDICATE_FLASH_INTERVAL = 1000
INDICATE_FLASHES = 3
INDICATE_MIN_INTENSITY = 0.0
INDICATE_MAX_INTENSITY = 25.0
HISTORY_UPDATE_INTERVAL = 180.0       # 3 minutes
REAL_TIME_UPDATE_INTERVAL = 1.0       # 1 second
LAST_VALID_CONNECTION_TIME_MAX = 3.0
LOOP_DELAY = 0.1
AutoAssign = False  # if True, automatically assign logical addresses to devices that are unassigned >>> need to implement
debugMsg = False
ShowLegacy = True   # if True, show modules with BLE FW earlier than 0.079 >>> need to implement


thermalHistogramLabels = ['<50C','50-55C','55-60C','60-65C','65-70C','70-75C','75-80C','80-85C','85-90C','90-95C','>95C']
intensityHistogramLabels = ['0%','0.1-1.0%','1.0-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%','80%-90%','90-100%']
#powerHistogramLabels = ['<1W','1-5W','5-10W','10-15W','15-20W','20-25W','25-30W','>30W']

intensityBucketPercentages = [0, 1.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
powerBucketWattages = [1, 5, 10, 15, 20, 25, 30, 1000]


DEMO_ID_ALL_DEVICES = -1

XIMLIST_DEVID_OFFSET = 0
XIMLIST_LOGICAL_ADDRESS_OFFSET = 1
XIMLIST_BLE_ADDRESS_OFFSET = 2
XIMLIST_NAME_OFFSET = 3
XIMLIST_FIXTURE_MFG_OFFSET = 4
XIMLIST_FIXTURE_PN_OFFSET = 5

FIXTURE_MANUFACTURER_DEFAULT = "Fixture Co"
FIXTURE_PART_NUMBER_DEFAULT = "Fixture PN"
MIN_LEVEL_DEFAULT = 1
MAX_LEVEL_DEFAULT = 254
MIN_INTENSITY_DEFAULT = 1.0
MAX_INTENSITY_DEFAULT = 100.0
FADE_TIME_DEFAULT = 700
MAX_DEVICES_DEFAULT = 10
GROUP_MASK_DEFAULT = ble_xim.BLEX_BROADCAST_ADDRESS



bleDirectory = "BLE"
workingDirectory = os.getcwd()

if (cfg.WINDOWS):
    ximIdListFileName = ".\{0}\\ximIdList.csv".format(bleDirectory)
    ximIdListTempFileName = ".\{0}\\ximIdList.tmp".format(bleDirectory)

if (cfg.LINUX or cfg.OSX):
    ximIdListFileName = "{0}/{1}/ximIdList.csv".format(workingDirectory, bleDirectory)
    ximIdListTempFileName = "{0}/{1}/ximIdList.tmp".format(workingDirectory, bleDirectory)

ximIdListHeaderRow = ["Dev ID", "Logical Address", "BLE Address", "Module Name", "Type", "Part Number", "XIM FW", "BLE FW", "BLE HW"] #,"Fixture Mfg", "Fixture PN"]
ximIdListDefaults = ["", "", "", "", "", "", "", "", ""] #FIXTURE_MANUFACTURER_DEFAULT, FIXTURE_PART_NUMBER_DEFAULT]

demoFadeTime = FADE_TIME_DEFAULT
demoConnectable = False
demoMaxDevices = MAX_DEVICES_DEFAULT
demoGroupMask = GROUP_MASK_DEFAULT

# The XimDevice class stores all the information that is retrieved from the XIM BLE devices
class XimDevice(object):
    def __init__(self, bleAddr):

        self.bleAddress = bleAddr #device ble mac address

        # Device Information
        self.deviceId = None      #device logical address
        self.name = None
        self.manufacturer = 'Xicato'
        self.partNumber = None
        self.ximFW_ver = None
        self.bleFW_ver = None
        self.ximHW_ver = None
        self.flux = None
        self.cct = None
        self.cri = None
        self.les = None
        self.rev = None
        self.power = 0.0
        self.deviceIdAssigned = False

        # Real-time diagnostics
        self.rssi = None
        self.coreTemperature = None
        self.pcbTemperature = None
        self.vin = 0.0
        self.vinRipple = None
        self.intensity = None
        self.status = None

        # Historical Data
        self.onHours = None
        self.powerCycles = None
        self.ledCycles = None

        # Histograms
        self.temperatureHistogram = []
        self.intensityHistogram = []

        # State Information
#        self.totalAdvRecd = 0 #total count of XBx advertisements received from the device
        self.lastScanTime = 0
        self.lastHistoryUpdate = time.time() - HISTORY_UPDATE_INTERVAL
        self.needsHistoryUpdate = False
        self.lastRealTimeUpdate = time.time() - REAL_TIME_UPDATE_INTERVAL
        self.updateInterval = 0.0
        self.lastConnectionTime = 0.0
        self.lastConnectionAttemptTime = 0.0
        self.connectionFails = 0

        # Demo
        self.IdListIndex = None          #List index (row count)
        self.demoFilteredRssi = None
        self.demoFwVersionIsNewest = 1

        self.demoFixtureManufacturer = FIXTURE_MANUFACTURER_DEFAULT
        self.demoFixturePartNumber = FIXTURE_PART_NUMBER_DEFAULT
        self.demoFixtureFlux = None

        self.demoFadeTime = FADE_TIME_DEFAULT
        self.demoIsConfigInitialized = False # >>> need to clean up...

    def GetInfo(self): #looks good, but need to add decoder on status.
        return {'00. Index':self.IdListIndex, '01. Device ID':Demo_ConvertListToDottedString(self.deviceId,"."), '02. Name':self.name,
            '03. Device':self.partNumber,
            '04. Intensity':self.intensity,
            '05. Power':round(self.power,1),
            '06. Tc temperature':self.coreTemperature,
            '07. supply_voltage':round(self.vin,2),
            '08. on_hours':self.onHours, '09. signal_strength':self.rssi, '10. status':self.status,
            '11. Last Update':self.lastRealTimeUpdate , '12. Adv Interval':round(self.updateInterval,1)
            }

    def GetRealTimeDataList(self):

#        # Set the signal bars to 0 if an advertisement packet hasn't been received for a long time or there have been too many connection fails.
#        if((time.time() - self.lastScanTime) > LAST_SCAN_TIME_ERROR) or (self.connectionFails >= MAX_CONNECTION_FAILS):
#            demoAdjustedSignalBars = 0
#            logHandler.printLog ("ximGateway.GetRealTimeDataList: Last scan time error {1} or connection fail {2} for device {0}".format(self.deviceId, self.lastScanTime, self.connectionFails), True)
#            if(SIGNAL_ERROR_CAUSES_NULL_DATA):
#                return {'temperature':0, 'input_voltage':0, 'intensity':0, 'signal_strength':demoAdjustedSignalBars, 'air_quality':1}
#
#        # Set the signal bars to 1 if an advertisement packet hasn't been received recently
#        elif((time.time() - self.lastScanTime) > LAST_SCAN_TIME_WARNING):
#            logHandler.printLog ("ximGateway.GetRealTimeDataList: Last scan time warning {1} for device {0}".format(self.deviceId, self.lastScanTime), True)
#            demoAdjustedSignalBars = 1
#        else:
#            demoAdjustedSignalBars = self.demoSignalBars

        return {'Device_ID':Demo_ConvertListToDottedString(self.deviceId,"."), 'Name':self.name, 'fixture_manufacturer':self.demoFixtureManufacturer,
            'fixture_part_number':self.demoFixturePartNumber, 'manufacturer':self.manufacturer, 'Xicato_PN':self.partNumber,
            'BLE Address':Demo_ConvertListToDottedString(self.bleAddress,"."), 'flux':'{0}lm'.format(self.flux), 'color_temp':'{0}K'.format(self.cct),
            'cri':'Ra {0}'.format(self.cri),
            'fixture_flux':'{0}lm'.format(self.flux), # >>> use programmed flux value for this
            'intensity':round(self.intensity,2), 'power':round(self.power,1),
            'Tc temperature':self.coreTemperature, 'PCB temperature':self.pcbTemperature,
            'supply_voltage':round(self.vin,2), 'supply_ripple':int(self.vinRipple), 'status':self.status, 'signal_strength':self.rssi, 'on_hours':self.onHours,
            'LED_cycles':self.ledCycles, 'power_cycles':self.powerCycles, 'HW_version':self.ximHW_ver, 'XIM_FW_ver':self.ximFW_ver,
            'BLE_FW_ver':self.bleFW_ver}

    def GetTemperatureHistogram(self):
        return self.MakeDictList(thermalHistogramLabels, self.temperatureHistogram)

    def GetIntensityHistogram(self):
        return self.MakeDictList(intensityHistogramLabels, self.intensityHistogram)

    def GetAllHistory(self):
        return {'temperature':self.GetTemperatureHistogram(), 'intensity':self.GetIntensityHistogram(), 'hours':self.onHours} #, 'power':self.GetPowerHistogram(), 'warranty':self.demoWarrantyHours}

    def MakeDictList(self, list1, list2):
        outList = []
        for i in range(min(len(list1), len(list2))):
            outList.append({list1[i]:list2[i]})
        return outList


# ######################################
# Section: Device Management - Internal Functions
# ######################################
ximList = []

# Checks if any new XIMs were found and adds them to the list
def UpdateXimList():
    ximAddressList = ble_xim.GetAddressList() #get the XIM address list

##    logHandler.printLog ("ximAddressList: {0}".format(ximAddressList), True)

    for bleAddr in ximAddressList:    # read through the list of devices discovered
        if (debugMsg):
            logHandler.printLog("{0} ximGateway.UpdateXimList: for address in ximAddressList is: {1}".format(time.time(), bleAddr))

        inList = FindInList(bleAddr)  # and see if they are in the gateway list

        if (inList): #we can update the XBeacon received count
            device = GetDevice(bleAddr)

#            if (debugMsg):
#                logHandler.printLog(">>>> ximGateway.UpdateXimList: Device in address list, received count is: {0}".format(device.totalAdvRecd))


        # Add a new device to the list if we haven't seen the device before
        #  This would be the place to add an address filter, but we're not
        # going to worry about implementing at this point in time - we'll
        # push it to the next level up (i.e., whatever collects the data
        # from multiple gateways.
        if(inList == False): # and (len(ximList) < demoMaxDevices) and (Demo_IsInGroup(deviceId)):
            #let's collect a little more data from the device first
            deviceId = ble_xim.GetDeviceId(bleAddr)
            deviceIdAssigned = False

            if (debugMsg):
                logHandler.printLog(">>>> ximGateway.UpdateXimList: didn't find address in ximAddressList, ID is {0}, with length={1}".format(deviceId, len(deviceId)))

            if (len(deviceId) == 4): # then it's a legacy packet format
                LegacyFormat = True

            if (len(deviceId) == 1 or len(deviceId) == 3): # send out get info advertising requests
                ble_xim.BroadcastRequestAdv(deviceId, [0x02])
                ble_xim.BroadcastRequestAdv(deviceId, [0x03])
                LegacyFormat = False
                if (len(deviceId) == 1):
                    deviceIdAssigned = True # the address has been assigned
                #else:
                #    deviceIdAssigned = False

            newDevice = XimDevice(bleAddr)
            newDevice.IdListIndex = Add_ListId(bleAddr)
            newDevice.deviceId = deviceId
            newDevice.deviceIdAssigned = deviceIdAssigned
            newDevice.name = ble_xim.GetDeviceName(bleAddr) #'Lamp {0}'.format(newDevice.IdListIndex)
#            newDevice.totalAdvRecd = 1
            Demo_LoadDeviceInformation(newDevice)
            ximList.append(newDevice)


# Returns True if there's an XimDevice object with the specified BLE address
def FindInList(bleAddr):
    for device in ximList:
        if(device.bleAddress == bleAddr):
            return True
    return False

# Returns the device with the matching BLE address
def GetDevice(bleAddr):
##    logHandler.printLog ("ximList {0}".format(ximList))
    for device in ximList:
        if(device.bleAddress == bleAddr):
            return device
    return None

def GetDeviceByDevIndex(ListIndex):
##    logHandler.printLog ("ximList {0}".format(ximList))
    if (debugMsg):
        logHandler.printLog(">>> ximGateway.GetDeviceByDevIndex: ID requested is {0}".format(ListIndex))
    for device in ximList:
        if(device.IdListIndex == ListIndex):
            return device
    return None

# Returns True if a device exists with the provided BLE address
def IsValidDevice(bleAddr):
    device = GetDevice(bleAddr)
    if(device):
        return True
    else:
        return False

# Returns True if a device exists with the provided Logical address
def IsValidDeviceByIndex(ListIndex):
    if (debugMsg):
        logHandler.printLog(">>> ximGateway.IsValidDeviceByIndex: ID requested is {0}".format(ListIndex))
    device = GetDeviceByDevIndex(ListIndex)
    if(device):
        return True
    else:
        return False

# Returns the real-time data for the provided IdListIndex
def ReadRealTimeData(ListIndex):
    device = GetDeviceByDevIndex(ListIndex)
    if(device):
        realTimeList = device.GetRealTimeDataList()
        return realTimeList

# Returns the historical data for the provided IdListIndex
def ReadDeviceHistory(DeviceId):
    device = GetDeviceByDevIndex(IdListIndex)
    if(device):
        historyList = device.GetAllHistory()
        return historyList

# Returns a list of all of the device's device information (each a list)
def ReadAllDeviceInfo():
    infoList = []
    for device in ximList:
        infoList.append(device.GetInfo())
    return infoList

# Returns True if the specified device ID is included the demo's group mask
# It is included if for each byte in the device ID, it is either 255,
#   the corresponding group mask's byte is 255, or the corresponding bytes are equal.
def Demo_IsInGroup(deviceId):
    inGroup = False
    if(deviceId and len(deviceId) == 4):
        inGroup = True
        for i in range(len(deviceId)):
            if((demoGroupMask[i] != 255) and (deviceId[i] != 255) and (demoGroupMask[i] != deviceId[i])):
                inGroup = False
                break
    return inGroup

# Converts a string to a list of integers
def Demo_GetIntListFromString(text, separator):
    try:
        return map(int,eval("{0}".format(text.split(separator))))
    except:
        return None

# For the demo, retrieves information about the device from ximIdList.csv
def Demo_LoadDeviceInformation(newDevice):

    with open(ximIdListFileName, 'r') as f:
        lines = f.readlines()
        if(len(lines) > 1):
            lines = lines[1:]
        for line in lines:
            line = line.rstrip('\r\n')
            if(len(line) > 0):
                try:
                    ximInfo = line.split(',')
    ##                logHandler.printLog ("ximInfo: {0}".format(ximInfo), True)

                    if(eval(ximInfo[XIMLIST_DEVID_OFFSET]) == newDevice.IdListIndex):
                        newDevice.demoFixtureManufacturer = ximInfo[XIMLIST_FIXTURE_MFG_OFFSET]
                        newDevice.demoFixturePartNumber = ximInfo[XIMLIST_FIXTURE_PN_OFFSET]
#                        if(demoMinIntensity != None):
#                            newDevice.demoMinDaliLevel = Demo_ConvertIntensityToDaliLevel(demoMinIntensity)
#                        else:
#                            newDevice.demoMinDaliLevel = MIN_LEVEL_DEFAULT

#                        if(demoMaxIntensity != None):
#                            newDevice.demoMaxDaliLevel = Demo_ConvertIntensityToDaliLevel(demoMaxIntensity)
#                        else:
#                            newDevice.demoMaxDaliLevel = MAX_LEVEL_DEFAULT
                        newDevice.demoFadeTime = demoFadeTime

                except:
                    logHandler.printLog ("ximGateway.LoadDeviceInformation: Invalid file structure in ximIdList.txt", True)

# For the demo, searches ximIdList.csv for a device with a matching address.
#   If none is found, it creates an ID and writes the device information to
#   the file.
def Add_ListId(bleAddr):

    IdListIndex = None
    idList = []
    with open(ximIdListFileName, 'r') as f:
        lines = f.readlines()
        if(len(lines) > 1):
            lines = lines[1:]
            matchFound = False

            # Search for a matching address
            for line in lines:
                line = line.rstrip('\r\n')
                try:

                    dataInfo = line.split(',')
                    try:
                        testId = int(dataInfo[XIMLIST_DEVID_OFFSET])
                    except:
                        logHandler.printLog ("ximGateway.Add_ListId: id is not an integer", True)
                        testId = None
                    else:
                        idList.append(testId) #didn't find a match, so append it to the list

                        try:
                            testAddress = map(int, eval("{0}".format(dataInfo[XIMLIST_BLE_ADDRESS_OFFSET].split('.'))))
    ##                        logHandler.printLog ("fileAddress:{0}, address: {1}".format(testAddress, address), True)

                            if(testAddress == bleAddr):
                                IdListIndex = testId
                                break
                        except:
                            logHandler.printLog ("ximGateway.Add_ListId: Address needs to be in the for x.x.x.x.x.x where x is a decimal", True)
                except:
                    logHandler.printLog ("ximGateway.Add_ListId: Invalid file structure in ximIdList.txt", True)

##    logHandler.printLog ("IdListIndex: {0}".format(IdListIndex), True)

    # No match found, so add the device to the list
    if IdListIndex == None:
        i = 1
        while(True):
            # Found an unused IdListIndex
            if(not(i in idList)):
                logHandler.printLog ("ximGateway.Add_ListId: New device found: {1}. Adding to list with IdListIndex {0}".format(i, bleAddr), True)
                IdListIndex = i
                with open(ximIdListFileName, 'a') as f:

                    addressString = Demo_ConvertListToDottedString(bleAddr, '.')

                    f.write("{0},,{1},Lamp {0},".format(IdListIndex, addressString))
                    for i in range(4, len(ximIdListDefaults)):
                        f.write("{0}".format(ximIdListDefaults[i]))
                        if(i < len(ximIdListDefaults) - 1):
                            f.write(",")
                    f.write("\n")
                break
            i += 1

    return IdListIndex

# Converts the provided list to a string separated by the provided separator character
def Demo_ConvertListToDottedString(inList, separator):
    outString = ""
    if(inList):
        for value in inList:
            outString += "{0}{1}".format(value, separator)
        outString = outString[:-1]
    return outString


# Finds a new device ID by determining the largest device ID in the ximIdList.csv
#   file and then incrementing by 1
def FindNewDeviceId():

    maxId = [1,1,1,1]
    testIdList = []
    with open(ximIdListFileName, 'r') as f:
        lines = f.readlines()
        if(len(lines) > 1):
            lines = lines[1:]
            for i, line in enumerate(lines):
                info = line.split(',')
                testId = map(int, info[XIMLIST_LOGICAL_ADDRESS_OFFSET].split('.'))
                testIdList.append(testId)
                if(testId != ble_xim.BLEX_UNASSIGNED_ADDRESS) and (testId > maxId):
                    maxId = testId

    newId = maxId[:]

    matchFound = True
    while(matchFound == True):
        logHandler.printLog("ximGateway.FindNewDeviceId newId: {0} testIdList: {1}".format(newId, testIdList), True)
        if not(newId in testIdList):
            matchFound = False
            break
        else:
            for i in range(3, -1, -1):
                if(newId[i] == 254):
                    newId[i] = 1
                else:
                    newId[i] += 1
                    break
    logHandler.printLog ("newId: {0}, testIdList: {1}".format(newId, testIdList), True)
    return newId


# Retrieves device information (part number, flux, CCT, CRI, LES, revision)
#   from the provided device
def FetchDeviceInfo(device):
    if(device):
        modelNumber = ble_xim.RequestModelNumber(device.bleAddress, BLE_READ_TIMEOUT)
        logHandler.printLog ("{0}: Model Number is: {1}".format(time.time(), modelNumber))

        if(modelNumber and (modelNumber[:3] == "XIM") and (len(modelNumber) >= 14)):
            device.partNumber = modelNumber
            lesString = modelNumber[3:5]
            criString = modelNumber[5:7]
            cctString = modelNumber[7:9]
            fluxString = modelNumber[9:11]
            revisionString = modelNumber[13]

            if(lesString == "09"):
                device.les = 9
            else:
                device.les = 19

            device.cri = criString
            device.cct = int(cctString) * 100
            device.flux = int(fluxString) * 100
            device.rev = revisionString

        else:
            device.partNumber = "Unknown"
            device.flux = "?"
            device.cct = "?"
            device.cri = "?"
            device.les = "?"
            device.rev = "?"
#            device.powerMultiplier = 13.00

        # Retrieve the BLE firmware version and check if it is up to date
#        fwVersion = ble_xim.RequestSoftwareRevision(device.bleAddress, BLE_READ_TIMEOUT)
#        if(fwVersion != None):
#            device.fwVersion = float(fwVersion)
#            if(float(fwVersion) >= NEWEST_FW_VERSION):
#                device.demoFwVersionIsNewest = 1
#            else:
#                device.demoFwVersionIsNewest = 0

        logHandler.printLog ("{0}: Device info is: {1}".format(time.time(), device.GetInfo()))

# Retrieves the diagnostic data from the provided device
def FetchDiagnosticData(device):

    scannedData = ble_xim.GetScannedData(device.bleAddress)
##    logHandler.printLog("Retrieved scannedData: {0}".format(scannedData), True)

    if(scannedData and (scannedData['intensity'] != None) and (scannedData['status'] != None)):
        answerReceived = True

        if(scannedData['lastScanTime'] > device.lastScanTime):
            device.lastScanTime = scannedData['lastScanTime']
            logHandler.printLog ("{0}: ximGateway.FetchDiagData: Received packet from {1}, {2}, {3}, {4}, {5}".format(time.time(), scannedData['deviceId'], device.name, scannedData['hwVersion'], scannedData['fwVersion'], device.bleFW_ver))

        deviceId = scannedData['deviceId']
        name = scannedData['deviceName']
        bleFW_ver = scannedData['swVersion']
        ximHW_ver = scannedData['hwVersion']
        ximFW_ver = scannedData['fwVersion']

        if(bleFW_ver != None) and (bleFW_ver != device.bleFW_ver):
            device.bleFW_ver = bleFW_ver;

        if(ximHW_ver != None) and (ximHW_ver != device.ximHW_ver):
            device.ximHW_ver = ximHW_ver;

        if(ximFW_ver != None) and (ximFW_ver != device.ximFW_ver):
            device.ximFW_ver = ximFW_ver;

        if(name != device.name) or (deviceId != device.deviceId):
            device.name = name
            device.deviceId = deviceId
            Demo_UpdateStoredDeviceName(device)

        device.rssi = scannedData['rssi']
#        Demo_UpdateSignalStrength(device)

        device.intensity = scannedData['intensity']
        device.onHours = scannedData['hours']
        device.powerCycles = scannedData['powerCycles']
        device.ledCycles = scannedData['ledCycles']

        device.status = scannedData['status']
        device.coreTemperature = scannedData['coreTemperature']
        device.pcbTemperature = scannedData['pcbTemperature']
        device.vin = scannedData['vin']
        device.vinRipple = scannedData['vinRipple']
        device.power = scannedData['power']
#        device.totalAdvRecd += 1

# Retrieve the temperature histogram for the provided device
def FetchTemperatureHistogram(device):
    if(device):
        length = 33
        histogram = FetchHistogram(device, 3, 3, length, 3)
        if(len(histogram) > 0):

#            if(SIMULATED_OFFSET_ADD_ENABLED):
#                for i in range(min(len(histogram), len(device.simTemperatureHistogramOffset))):
#                    histogram[i] += device.simTemperatureHistogramOffset[i]

            device.temperatureHistogram = histogram
            logHandler.printLog ("{0}: Thermal histogram: {1}".format(time.time(), device.GetTemperatureHistogram()))

# Retrieve the intensity histogram for the provided device
def FetchIntensityHistogram(device):
    if(device):
        length = 48
        histogram = FetchHistogram(device, 4, 3, length, 4)

        if(len(histogram) > 0):
            for i in range(len(histogram)):
                histogram[i] = (float(histogram[i]) / 3600.0)

            device.intensityHistogram = histogram
            logHandler.printLog ("{0}: Max Intensity histogram: {1}".format(time.time(), device.GetIntensityHistogram()))


# Retrieves a list of values from the provided device and converts them into
#   a list of integers, which represent the histogram.
# Note that ble_xim.GetBankData will be deprecated in a future release
def FetchHistogram(device, bank, offset, numBytes, bytesPerBucket):

    histogram = []
    values = ble_xim.GetBankData(device.bleAddress, bank, offset, numBytes, 0.5)
    if(values and len(values) == numBytes):
        i = 0
        while i < len(values):
            histogram.append(ConvertBytesToValue(values[i:i + bytesPerBucket]))
            i += bytesPerBucket

    return histogram

# Converts a list of bytes (big-endian) to a value
def ConvertBytesToValue(bytes):
    value = 0
    factor = 1
    length = len(bytes)
    while(length > 0):
        value += bytes[length - 1] * factor
        factor *= 256
        length -= 1
    return value

# >>> Gateway API Call
# >>> Need to replace IdListIndex with the logical address
# Sets the intensity of the device with the provided IdListIndex
# The provided intensity is scaled according to the device's minimum and maximum
#  levels.
# When the IdListIndex is DEMO_ID_ALL_DEVICES, the intensity will be sent to all
#   devices
# Note that the required BLE API call is not called here, but is buffered, so
#   that the Run API can properly manage when it is sent
def SetIntensity(IdListIndex, intensity):
    global sendIntensity

    # Set the intensity for all devices
#    if(IdListIndex == DEMO_ID_ALL_DEVICES):
#        if(len(ximList) > 0):

            #allSameLevels = True

#            commandQueue.append({'function':ble_xim.BroadcastLightLevel, 'deviceId':demoGroupMask, 'values':values, 'time':time.time()})

    # Set the intensity for one device
#    else:
    device = GetDeviceByDevIndex(IdListIndex)
    if(device):
#        values = {"light_level":Demo_ReverseScaleIntensity(device, intensity), "fade_time":device.demoFadeTime, "response_time":0, "override_time":0, "lock_light_control":False}
        values = {"light_level": intensity, "fade_time":1000, "response_time":1, "override_time":0, "lock_light_control":True}
        commandQueue.append({'function':ble_xim.BroadcastLightLevel, 'deviceId':device.deviceId, 'values': values, 'time':time.time()})


# >>> Gateway API call
# >>> Need to replace IdListIndex with the logical address
# Sends the indicate command, which will flash the device's light to indicate its location
# Note that the required BLE API call is not called here, but is buffered, so
#   that the Run API can properly manage when it is sent
def SetIndicate(IdListIndex):
    device = GetDeviceByDevIndex(IdListIndex)
    if(device):
        values = {'num_flashes':INDICATE_FLASHES, 'period':INDICATE_FLASH_INTERVAL, 'high_level':INDICATE_MAX_INTENSITY, 'low_level':INDICATE_MIN_INTENSITY}
        commandQueue.append({'function':ble_xim.BroadcastIndicate, 'deviceId':device.deviceId, 'values':values, 'time':time.time()})


# Returns the next command in the queue (FIFO)
# Note that this doesn't remove the command from the queue
def GetCommandFromQueue():
    global commandQueue

    for i, commandInfo in enumerate(commandQueue):
        return commandInfo, i
    return None, None

# Removes the next command in the queue (FIFO)
def RemoveCommandFromQueue(i):
    global commandQueue
    commandQueue.pop(i)

# Updates the name of the provided device in the ximIdList.csv file
def Demo_UpdateStoredDeviceName(device):
    lines = None

    testAddress = Demo_ConvertListToDottedString(device.bleAddress, '.')

    needsUpdate = False
    with open(ximIdListFileName, 'r') as f:
        lines = f.readlines()
    if(len(lines) > 1):
        for i, line in enumerate(lines):
            info = line.split(',')
            if(testAddress == info[XIMLIST_BLE_ADDRESS_OFFSET]):
                if(info[XIMLIST_NAME_OFFSET] != device.name):
                    needsUpdate = True
                    info[XIMLIST_NAME_OFFSET] = device.name
                if(info[XIMLIST_LOGICAL_ADDRESS_OFFSET] != Demo_ConvertListToDottedString(device.deviceId, '.')):
                    needsUpdate = True
                    info[XIMLIST_LOGICAL_ADDRESS_OFFSET] = Demo_ConvertListToDottedString(device.deviceId, '.')

                if(needsUpdate):
                    lines[i] = Demo_ConvertListToDottedString(info, ',')

    if(needsUpdate):
        with open(ximIdListTempFileName, 'w') as f:
            for line in lines:
                f.write(line)
        logHandler.RenameSafely(ximIdListTempFileName, ximIdListFileName)

# Initializes the ximIdList.csv file and makes sure it has the proper fields
def LoadXimList():

    global ximIdListFileName

    if not os.path.exists(bleDirectory): #probably doesn't belong here...
        os.makedirs(bleDirectory)

    if(os.path.isfile(ximIdListFileName) == False):  #ximIdList.csv file doesn't exist
        with open(ximIdListFileName, 'w') as f:
            for i in range(len(ximIdListHeaderRow)):
                f.write("{0}".format(ximIdListHeaderRow[i]))
                if(i < len(ximIdListHeaderRow) - 1):
                    f.write(",")
            f.write("\n")
    else:
        with open(ximIdListFileName, 'r') as f:      #ximIdList.csv exists, so open it
            lines = f.readlines()
            if(len(lines) > 0):
                headerLine = lines[0][-1]

            with open(ximIdListTempFileName, 'w') as destination:
                for i in range(len(ximIdListHeaderRow)):
                    destination.write("{0}".format(ximIdListHeaderRow[i]))
                    if(i < len(ximIdListHeaderRow) - 1):
                        destination.write(",")
                destination.write("\n")

                for line in lines[1:]:
                    line = line[:-1]
                    destination.write(line)

                    ximInfo = line.split(',')
                    logHandler.printLog ("ximGateway.LoadXimList: {0}".format(ximInfo)) #print out list values to log file
                    if(len(ximInfo) > 0):
                        destination.write(",")

                    for i in range(len(ximInfo), len(ximIdListDefaults)):
                        logHandler.printLog ("write: {0}".format(ximIdListDefaults[i]))
                        destination.write("{0}".format(ximIdListDefaults[i]))
                        if(i < len(ximIdListDefaults) - 1):
                            destination.write(",")
                    destination.write("\n")

        logHandler.RenameSafely(ximIdListTempFileName, ximIdListFileName)

# Loads the demo's configuration values from GatewayParameters.txt
""" #def Demo_LoadConfiguration():
#    global demoMinIntensity, demoMaxIntensity, demoFadeTime, demoConnectable, demoMaxDevices, demoGroupMask
#
#    valuesLoaded = False
#    if (cfg.LINUX):
#        ximGatewayFileName = "./GatewayParameters.txt"
#    if(os.path.isfile(ximGatewayFileName) == True):
#        with open(ximGatewayFileName, 'r') as f:
#            lines = f.readlines()
#            if(len(lines) >= 6):
#                valuesLoaded = True
#                try:
#                    value = lines[0].split(':')[1]
#                    demoMinIntensity = float(value)
                except ValueError:
                    logHandler.printLog("Min intensity not found in ximGatewayParameters. Marking as unchanged", True)
                    demoMinIntensity = None

                try:
                    value = lines[1].split(':')[1]
                    demoMaxIntensity = float(value)
                except ValueError:
                    logHandler.printLog("Max intensity not found in ximGatewayParameters. Marking as unchanged", True)
                    demoMaxIntensity = None

                try:
                    value = lines[2].split(':')[1]
                    demoFadeTime = int(value)
                except ValueError:
                    logHandler.printLog("Fade time not found in ximGatewayParameters. Setting to default", True)
                    demoFadeTime = FADE_TIME_DEFAULT
                    valuesLoaded = False

                try:
                    value = lines[3].split(':')[1]
                    demoConnectable = value[0] in ['y','Y']
                except ValueError:
                    logHandler.printLog("Connectable not found in ximGatewayParameters. Setting to default", True)
                    demoConnectable = False
                    valuesLoaded = False

                try:
                    value = lines[4].split(':')[1]
                    demoMaxDevices = int(value)
                except ValueError:
                    logHandler.printLog("Max devices not found in ximGatewayParameters. Setting to default", True)
                    demoMaxDevices = MAX_DEVICES_DEFAULT
                    valuesLoaded = False

                try:
                    value = lines[5].split(':')[1]
                    demoGroupMask = map(int, value.split('.'))
                except ValueError:
                    logHandler.printLog("Group mask not found in ximGatewayParameters. Setting to default", True)
                    demoGroupMask = GROUP_MASK_DEFAULT
                    valuesLoaded = False

            else:
                logHandler.printLog("Missing parameters in ximGatewayParameters. Setting to default", True)

    if(valuesLoaded == False):
        with open(ximGatewayFileName, 'w') as f:
            if(demoMinIntensity == None):
                f.write("min_intensity:Unchanged\n")
            else:
                f.write("min_intensity:{0:.3f}\n".format(demoMinIntensity))

            if(demoMaxIntensity == None):
                f.write("max_intensity:Unchanged\n")
            else:
                f.write("max_intensity:{0:.3f}\n".format(demoMaxIntensity))
            f.write("fade_time:{0}\n".format(demoFadeTime))
            if(demoConnectable):
                connectableString = "Y"
            else:
                connectableString = "N"
            f.write("connectable:{0}\n".format(connectableString))
            f.write("max_devices:{0}\n".format(demoMaxDevices))
            f.write("group_mask:{0}\n".format(Demo_ConvertListToDottedString(demoGroupMask, '.')))
"""
# Starts the gateway
def Start():
    global logHandler
    global wasStarted
    global deviceIndex
    global pauseTime
    global lastValidConnectionTime


    if(wasStarted == False):
        wasStarted = True

        if (cfg.WINDOWS):
            logHandler = LogHandler.LogHandler(".\Event_Logs", "eventLog.txt", True, 5)
        if (cfg.LINUX or cfg.OSX):
            logHandler = LogHandler.LogHandler("./Event_Logs", "eventLog.txt", True, 5)

        logHandler.EnableCleanUp(60.0, 50000)

        ble_xim.Initialize(logHandler)

        isSuccess = ble_xim.Start()    # look for the BLE interface and make sure it's available

        logHandler.printLog("{0} ximGateway.Start: *** Running XIM Gateway version {1} ***".format(time.time(), GATEWAY_VERSION), True)

        if(isSuccess):       #initialize gateway values
            deviceIndex = 0
            pauseTime = time.time() + DISCOVER_DURATION
            lastValidConnectionTime = time.time()

            LoadXimList()        # Dump the list contents to the log file
#            Demo_LoadConfiguration()  # not needed

        else:
            logHandler.printLog ("Unable to initialize communication. Exiting the application", True)
            time.sleep(3)
            exit(0)

# Runs the gateway.
def Run():
    global deviceIndex
    global connectionAttempted, connectionEnableSent, lastValidConnectionTime
    global pauseTime
    global commandQueue

    try:
        if (debugMsg):
            logHandler.printLog ("{0} ximGateway.Run: *** starting ble_xim.Process ***".format(time.time()))

        ble_xim.Process() # run the stack

        if (debugMsg):
            logHandler.printLog("{0} ximGateway.Run: *** starting UpdateXimList ***".format(time.time()))

        UpdateXimList() # create an entry in the device list
#        UpdateXsensorList() # need to create this function

        if (debugMsg):
            logHandler.printLog("{0} ximGateway.Run: *** completed UpdateXimList ***".format(time.time()))

        # Doesn't require a connection to get the real-time data
        for device in ximList:
            logHandler.printLog("{0} ximGateway.Run: for device in ximList is: {1}, {2}".format(time.time(),device.IdListIndex, device.deviceId))
#            device.updateInterval = time.time() - device.lastRealTimeUpdate
            if(time.time() - device.lastRealTimeUpdate > REAL_TIME_UPDATE_INTERVAL):
#            if(device.updateInterval > REAL_TIME_UPDATE_INTERVAL):
                device.updateInterval = time.time() - device.lastRealTimeUpdate
                device.lastRealTimeUpdate = time.time()
                if (device.deviceId != None):
                    ble_xim.BroadcastRequestAdv(device.deviceId, [0x02])
                    ble_xim.BroadcastRequestAdv(device.deviceId, [0x03])
                FetchDiagnosticData(device)

        if(len(ximList) > 0 and ble_xim.IsLinkReady() and ble_xim.IsSystemBusy() == False):

            commandInfo, commandIndex = GetCommandFromQueue()
            if(commandInfo and time.time() >= commandInfo['time']):
                commandInfo['function'](commandInfo['deviceId'], commandInfo['values'])
                RemoveCommandFromQueue(commandIndex)

            elif(time.time() >= pauseTime):
##                logHandler.printLog ("{0}: Checking Connections".format(time.time()), True)
                device = ximList[deviceIndex]
                if (device.deviceIdAssigned == True):
                    goToNextConnection = False
                    ##        logHandler.printLog ("{0}: Device {1}".format(time.time(), device.bleAddress), True)
                    # Check if the history needs updating
                    if(device.needsHistoryUpdate == False and ((time.time() - device.lastHistoryUpdate > HISTORY_UPDATE_INTERVAL) or (device.temperatureHistogram == []) or (device.intensityHistogram == []))):
                        device.lastHistoryUpdate = time.time()
                        device.needsHistoryUpdate = True

                    if(device and device.bleAddress and device.deviceId and ((device.connectionFails < MAX_CONNECTION_FAILS)
                        or ((time.time() - device.lastConnectionAttemptTime) > BAD_CONNECTION_TEST_DURATION)) and
                        (device.demoIsConfigInitialized == False or device.partNumber == None or device.needsHistoryUpdate)):

                        if(ble_xim.IsDeviceConnected(device.bleAddress)):
                            device.connectionFails = 0

                            if(time.time() - lastValidConnectionTime > LAST_VALID_CONNECTION_TIME_MAX):
                                logHandler.printLog ("{0} ximGateway.Run: Last valid connection time was {1}s ago".format(time.time(), time.time() - lastValidConnectionTime), True)

                            lastValidConnectionTime = time.time()
                            device.lastConnectionTime = time.time()

                            if(device.partNumber == None):
                                FetchDeviceInfo(device)
#                        	if(device.demoIsConfigInitialized == False):
#                           	 device.demoIsConfigInitialized = Demo_InitializeConfiguration(device)

                            if(device.needsHistoryUpdate):
#                           	 FetchTemperatureHistogram(device) #will need to fix, but comment out for now
#                            	FetchIntensityHistogram(device)

                                device.needsHistoryUpdate = False

                            disconnectDevice = True

                        else:
                            if(connectionAttempted):
                                if(ble_xim.IsDeviceConnecting(device.bleAddress) == False):
                                    disconnectDevice = True
                                    device.connectionFails += 1

                                else:
                                    disconnectDevice = False

                            elif(connectionEnableSent):
                                logHandler.printLog ("{0} ximGateway.Run: Gateway connect to {1}".format(time.time(), device.bleAddress), True)
                                ble_xim.Connect(device.bleAddress)
                                connectionAttempted = True
                                connectionEnableSent = False
                                disconnectDevice = False
                                device.lastConnectionAttemptTime = time.time()
                            else:
                                logHandler.printLog ("{0} ximGateway.Run: Enable connections for address {1} id {2}".format(time.time(), device.bleAddress, device.deviceId), True)
                                ble_xim.EnableConnections(device.deviceId)
##                            	ble_xim.EnableConnections(ble_xim.BLEX_BROADCAST_ADDRESS)
                                connectionEnableSent = True
                                disconnectDevice = False

                        if(disconnectDevice):
                            logHandler.printLog ("{0} ximGateway.Run: Gateway disconnect from {1}".format(time.time(), device.bleAddress), True)
                            ble_xim.Disconnect(device.bleAddress)

                            connectionAttempted = False
                            goToNextConnection = True
                            pauseTime = time.time() + DISCOVER_DURATION
                    else:
                        connectionAttempted = False
                        goToNextConnection = True
                        pauseTime = time.time()

                    if(goToNextConnection):

                        deviceIndex += 1
                        if(deviceIndex == len(ximList)):

                            deviceIndex = 0

    except Exception as err:
        message = 'Uncaught exception:\n{0}\n'.format(traceback.format_exc())
##        message += ''.join(traceback.format_exception(type, value, tb))
        with open('ExceptionLog.txt','a') as f:
            f.write(message)
        print(message)
        raise




def Close():
    for device in ximList:
        if(ble_xim.IsDeviceConnected(device.bleAddress)):
            ble_xim.Disconnect(device.bleAddress)



if __name__ == '__main__':

    Start()   # Initialize and start the gateway

    while(1): # run loop
        time.sleep(LOOP_DELAY)
        Run()
