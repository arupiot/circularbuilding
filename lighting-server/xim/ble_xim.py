#!/usr/bin/env python

"""
Library for interfacing to the XIM BLE modules via the BlueGiga BLED112 USB dongle

Based on the Bluegiga BGAPI/BGLib demo: Bluegiga "Cable Replacement Profile" collector

Xicato Changelog:
    V2.058 2016-08-11
        - Added uuid_light_control_scenes_characteristic
        - Added uuid_oem_service, uuid_access_oem_login_characteristic, and
            uuid_access_oem_data_characteristic
        - Added RequestBleScenesConfig, SetBleScenesConfig,
            RequestDaliAddressConfig, SetDaliAddressConfig,
            RequestDaliScenesConfig, SetDaliScenesConfig
        - Added WriteBankData
        - Added fadeMap lookup for recall scene. Also, sets the fade value
            to 0xFF when the fadeTime is None, so that the stored scene fade
            time is used
        - Only marks a service's attributesDiscovered field as complete when
            the procedure_completed event occurs. That way, if there's a
            disconnection, that service's attributes will be retrieved on the
            next connection
        - Changed CONNECT_ATTEMPT_TIMEOUT from 4.0 to 1.4
    V2.057 2016-07-28
        - Fixed the iXB logging when the packet can't be decrypted and added
            exception handling in ConvertListToSeparatedHexString
    V2.056 2016-07-22
        - Fixed the missing TransmitPacket for SetLightSetup (wasn't writing
            to the characteristic)
        - The Packet Log now shows the decrypted device ID and payload for
            normal X devices and iXBeacons.
        - Changed the Packet Log to show the data in hex format
        - Added support for temperature and intensity histogram characteristics
            (as opposed to doing a memory bank read)
        - Added a user login API for encrypted devices
        - Added status return values for the light setup APIs
        - Increased SERVICE_DISCOVERY_TIME from 6.5 to 7.0
    V2.055 2016-07-19
        - Added support for the new dali_light_config characteristic and
            uuid_dim_1_10V_config_characteristic
    V2.054 2016-07-13
        - Added support for the new (BLE FW V0.091) light setup characteristic.
            Added power_on_fade_time, power_on_start_time, dimming_curve, and
                fade_smoothing
        - Added use_fade_rate option for BroadcastLightLevel
        - Changed the default advertisemt request parameters. variability changed
            from 10 to 100ms, numBursts from 1 to 3, burstInterval from 10 to 40
        - Added uuid_sensor_general_characteristic,
            uuid_sensor_lux_characteristic, uuid_sensor_motion_characteristic
            for configuring the sensor
        - Added rounding of the intensity conversion so that the value isn't
            always truncated
        - Makes sure the group member storage doesn't overflow
    V2.053 2016-06-27
        - Added device type and packet type text descriptions to the packet log
        - Reads the FW version from the bootloader packet
        - Changed 'ledControllerVersion' to 'fwVersion' for GetScannedData
        - Changed 'sensorVersion' to 'fwVersion' for GetScannedSensorData
    V2.052 2016-06-25
        - If decryption with the RX key fails, it tries to decrypt with its TX
            key, since sensors use that key
        - Inserted NETWORK_PERM_CONFIG_BEACONS
        - Added sensor bootload packet detection
        - Added 2-byte logical address support for SetSensorResponse
        - Doesn't request groups from sensors (sensors don't scan)
        - Doesn't use OOB for sensors in encrypted mode (except when in
            Admin or Bootload mode)
    V2.051 2016-06-24
        - Added support for BLE Sensors V0.085+, which use the latest XBeacon
            packet structure
    V2.050 2016-06-22
        - Doesn't request group info when the device is in bootloader mode
    V2.049 2016-06-21
        - GetStoredGroups returns a copy of device.groups so that it can't
            get modified by the calling function
    V2.048 2016-06-20
        - Added GetStoredGroups to return the locally stored groups listed. Only
            returns the list if receivedAllGroups
    V2.047 2016-06-20
        - If the group info isn't received after the first burst request, it
            will keep trying every 30s (GROUP_REQUEST_RETRY_INTERVAL)
        - For new installs, the local device ID is a random number between
            0x7000 and 0x7FFF(LOCAL_DEVICE_ID_DEFAULT_MIN - MAX)
        - Added the new mapping for the override duration
        - Added iXBeacon logging to Packet_Logs
        - GetDevicesInGroup
        - Fixed BroadcastIXBAssigned to only encrypt when devices in the
            destination address have advertised encrypted
    V2.046 2016-06-16
        - Added the new network configuration for FW V0.084+ devices.
        - SetOobData requires the device to advertise as encrypted in order
            to use the network key for OOB
        - Added an adminMode where the admin key is used for encryption and OOB
            (currently disabled)
    V2.045 2016-06-15
        - Removed XBX_HEADER_ENCRYPTED_FLAG. When encryption is enabled, it always
        encrypts the header (using the headerKey).
    V2.0.44l 2016-06-15
        - Updated to support Linux as well as Windows. Primary change is in
          file handling, but also added the file cfg.py to set options
    V2.0.44 2016-06-13
        - Changed XBX_NETWORK_ID_PARTIAL_ID_MASK from 0x3F to 0x1F
    V2.0.43 2016-06-13
        - Added OOB support for secure devices. It checks the version of the
            device to know whether it can be used. It uses the adminKey when
            bootloadRunning
        - A XimBleDevice can be created when a ENCRYPTED_PACKET_TYPE_BOOTLOAD
            packet is detected
        - When re-connecting, it calls EnableConnections to advertise
        - Parses ENCRYPTED_PACKET_TYPE_BOOTLOAD to get the HW version and
            the BLE FW version
    V2.0.42 2016-06-10
        - Added a second key to try for admin key recovery
    V2.0.41 2016-06-09
        - Added support for encrypted headers
        - Handles encryption while already bonded (bonding is still disabled)
        - Enables indications for GetBankData
        - Added the new custom fade mapping table
        - Updated the network configuration APIs to be clearer how the
            device is secured
        - Added a workaround for admin key failing (V0.079 devices can
            get their admin key corrupted when there's a write to group membership)
        - Added test code for iXBeacon testing
    V2.0.40 2016-05-23
        - For testing, added BroadcastIXBUnassigned and BroadcastIXBAssigned
        - Limits the number of failed group requests to MAX_GROUP_REQUESTS (5)
        - Updated the local device ID to be a single integer (0 - 32767).
        - Fixed the HW version parsing of the scanned XDEV_INFO packet to be
            of the form x.y not x.yyy
        - Handles connections to bonded devices (TODO: handle when a bonded
            device no longer supports the bond and encryption keys need to be
            resent)
    V2.0.39 2016-05-23
        - BootloadWrite and BootloadRead will connect if the connection was
            dropped
        - BootloadWrite no longer re-transmits because that can make the update
            out of sync
        - in TransmitPacket, increased the packet error wait time from 0.2
            to MAX_CHUNK_WAIT_TIME (2.0 s)
    V2.0.38 2016-05-17
        - Added UNASSIGNED_BROADCAST_ADDRESS ([0xFF, 0xFF, 0xFF])
        - Added ENCRYPTED_PACKET_TYPE_XGROUP processing. Stores the values
            in groups and receivedAllGroups
        - Added ENCRYPTED_PACKET_TYPE_REQUEST_ADV advertising
        - Updated attributeList for the characteristics with removed CCCD's
            (uuid_dali_command_characteristic and uuid_dali_response_characteristic
                merged. uuid_xim_memory_location_characteristic and
                uuid_xim_memory_value_characteristic merged).
        - Added the field cccValue for storing received notifications/indications
        - Removed automatic DALI response CCCD indication enabling after connecting
        - Added support for ENCRYPTED_PACKET_TYPE_XDEV_INFO, including storing
            hwVersion, fwVersion, programmedFlux, and overloadTemperature
        - Updated to the new packet strucutures for BroadcastLightLevel,
            BroadcastIndicate, and EnableConnections for the V0.077 firmware
        - Stores the swVersion locally during RequestSoftwareRevision
    V2.0.37 2016-05-12
        - Adds devices that are only sending the Bootload mode packet
    V2.0.36 2016-05-11
        - Removed remaining network info code
        - Added group support, including group membership assignment
        - Renamed the old packet structure fields "_V0"
        - Preserved backward compatibility for transmitting advertisements
        - Combined the TX and RX network ID's into a single network ID, since
            PRoC FW V0.076 uses only one
        - Added EnableDaliResponse to manually enable indications for DALI
            response (since user permissions are required)
    V2.0.35 2016-05-04
        - Added support for the new packet structure with 2-byte assigned addresses
            and 3-byte unassigned addresses
        - Changed from a 21-bit SQN to a 32-bit. Removed netSqn and the Network
            Info packets
        - Added uuid_access_admin_login_characteristic and AdminLogin API
    V2.0.34 2016-04-20
        - Separately tracks the central and peripheral states so that advertising
            and scanning/connecting can be done independently
        - For SW V0.075+ devices, added uuid_access_network_select_characteristic,
            uuid_access_config_characteristic
        - The selected network is determined by variables selectedTxNetworkIndex
            and selectedRxNetworkIndex, instead of re-arranging the contents of
            BLE Network Config.txt.
        - Moved code into ProcessBootloadConnection and ProcessNormalConnection
        - When bonding fails, it calls ProcessNormalConnection, instead of letting
            the process time out
        - TransmitPacket waits for the response (device.packetStatus) before
            returning the status
        - Simplified adding to attributeList based on swVersion
        - RequestNetworkConfiguration simply returns the network by storing
            which id and key the application used to decrypt the advertisements
    V2.0.33 2016-04-15
        - No longer re-arranges the contents of BLE Network Config.txt. Instead
            SetLocalNetworkConfiguration determines which lines to use
    V2.0.32 2016-04-15
        - Advertises the Network Info packet every NETWORK_INFO_INTERVAL (5s),
            but only sends as a 50ms burst (1-2 packets).
        - Manages each network separately for Network Info processing
        - Supports the new XBN_NETWORK_INFO_REQUEST_PACKET
        - Moved code into the ProcessNetworkInfoPacket
        - Changed the netConfig dict to a new NetworkConfig object
        - Changed to netSqn
    V2.0.31 2016-04-05
        - In Connect, when it failed to send the connect_direct command, it
            will be treated as an error. The return value is True if the
            device isn't in STATE_STANDBY, instead of that it is connected
        - Added error checking for the swVersion
        - When receiving the value for SW version, it makes sure that it's not
            a notification/indication
    V2.0.30 2016-03-30
        - Changed the Network Info beacon to include the full sequence number and full
            IV index. These values (along with the source address) are in the nonce.
            The encrypted payload is only the upper 3 bytes of the network ID and
            one RFU (0) byte. This is more secure because the nonce is always changing
            (required for AES CCM). Despite the payload being shorter, a brute force
            attack would still require guessing the correct 32-bit MIC plus 24-bit
            network ID. That would take 45 million years to guess all combinations
            with a 20ms advertising interval.        -
    V2.0.29 2016-03-24
        - Fixed the COM port test sequence so that it can't get stuck if there's
            a COM port that keeps receiving data in < 1s intervals
        - When it tests a port , it resets the receive buffer (
            ble.bgapi_rx_buffer = [], ble.bgapi_rx_expected_length = 0)
    V2.0.28 2016-03-20
        - Added support for encryption with the XSensor device. It was missing
            uuid_access_control_characteristic. Created ProcessXSensorFields
        - Can discover and add an encrypted XIM or sensor to the network
    V2.0.27 2016-03-11
        - When bootloadRunning, if scanning is disabled, it makes sure that
            scanning is stopped
        - Added BroadcastICommand for testing iOS XBeacon advertisements
    V2.0.26 2016-03-04
        - Added SENSOR_CONTROL_VALUE (65532), BroadcastSensorControlMode, and
            SensorControlMode
    V2.0.25 2016-03-03
        - Added XSensorBleDevice and DEVICE_TYPE_XSENSOR
        - Updated for PRoC Sensor V0.006
        - Added PACKET_TYPE_XSENSOR_MOTION, PACKET_TYPE_XSENSOR_LUX
        - Added uuid_sensor_config_service, uuid_sensor_motion_characteristic,
            uuid_sensor_lux_characteristic
        - Added Sensor UUID Handle Map.csv
        - Properly handles connections to a sensor
    V2.0.24 2016-03-01
        - Detects the XSensor 1 beacon and logs it in the console
    V2.0.23 2016-02-09
        - The local device ID can be changed (stored in
            BLE Connection Parameters.txt) using SetLocalDeviceId
    V2.0.22 2016-02-05
        - Created TransmitAdvertisement which is called by BroadcastCommand
            and SetEncryptedPacket, so that the advertisement packet is
            always started the same way
        - Updated the missingNewHandle check for 0.061
        - The Broadcast commands (except SetConnectable) us IsEncryptedAdvEnabled
            to determine whether to send encrypted or not. IsEncryptedAdvEnabled
            is True if the host is using encryption and at least one of the
            devices in the destination is using encryption. For SetConnectable,
            it advertises on both if there are encrypted and unencrypted devices
            because an unconfigured device has device ID 255.255.255.255.
        - Stores unencrypted in BLE Network Config.txt as all 0's for ID and key
    V2.0.21 2016-02-03
        - uuid_access_control_characteristic is included only for V0.061+
        - Moved the network configuration variables into a single list of
            dictionaries (networkConfigs)
        - Verifies all 4 Network ID bytes in XBX_NETWORK_ID_NETWORK_INFO_PACKET
        - Aligned the code flow and naming with the PRoC encryption code
        - # Jeff TODO: Store SQNs per device
        - bleNetworkConfigFileName stores old network information when it isn't
            used and allows it to be recalled later
        - Added support for unencrypted or encrypted packets for all  Broadcast
            commands. EnableConnections supports both by waiting 100ms after
            the encrypted packet is sent before transmitting the unencrypted one
        - SetNetworkConfiguration no longer forces the local network configuration
    V2.0.20 2016-02-02
        - Changed the Network Info packet
        - Changed bleNetworkConfigFileName structure
        - Added IsDeviceEncryptedAdv
    V2.0.19 2016-02-01
        - Changed BLE\BLE SQN.txt to BLE\BLE Network Config.txt and add two
            configurations of Network ID, Key, SQN, IV Index
        - Added uuid_access_control_characteristic, along with
            RequestNetworkConfiguration and SetNetworkConfiguration
        - Uses encryptedAdv to track if a device is using encrypted advertising
        - Added WriteWithNotification to write a message and wait for a
            notification as the response
        - Each Broadcast command supports encrypted/un-encrypted devices
    V2.0.18 2016-01-28
        - In Disconnect, removed the condition
            not(device.connectionState in [STATE_LISTENING_DATA, STATE_STANDBY]
            when waiting for pending_write to be False
        - Added XBN_NETWORK_INFO_PACKET and SetNetworkInfoBeacon to
            send out the NETWORK_INFO packet when there's a MIC failure (every
            5 seconds MIC_FAIL_NETWORK_INFO_ADVERTISEMENT_INTERVAL) or it
            receives an NETWORK_INFO packet with a lower IV
            index (sends every 1 second MIN_NETWORK_INFO_ADVERTISEMENT_INTERVAL).
            Retries are NETWORK_INFO_RETRIES (2)
        - Increments the IV index when IV_INDEX_BIT_SHIFT flag is different
        - Parses the packet header in the encrypted payload
        - Supports encrypted XBeacon 2 packet
    V2.0.17 2016-01-27
        - Added IV index processing for transmitting encrypted packets. Stores
            the value at BLE\BLE SQN.txt
        - Added encrypted advertisments for RECALL_SCENE, INDICATE, and
            SET_CONNECTABLE
        - Added XBN_NETWORK_INFO_PACKET to advertised the network
            ID and complete IV index
    V2.0.16 2016-01-26
        - Added AES-CCM encryption (PyCrypto library)
        - Added xBeacon Encrypted generation in BroadcastEncryptedCommand and
            reception in my_ble_evt_gap_scan_response
        - Stores the latest sequence number to BLE\BLE SQN.txt
    V2.0.15 2016-01-13
        - Changed SERVICE_DISCOVERY_TIME from 6.0 to 6.5, accounting for new
            services and characteristics
    V2.0.14 2016-01-12
        - Added error checking device.connection_handle before sm_encrypt_start
        - Fixed the SERVICE_DISCOVERY_TIME extension for wait time to subtract
            the start_time. It was waiting for time.time()
    V2.0.13 2016-01-09
        - Added support for long reads (RequestData always uses read_long now)
        - Added uuid_sensor2_response_characteristic
    V2.0.12 2016-01-05
        - Added GetLocalAddress to get the BlueGiga dongle's BLE address
        - Added PACKET_TYPE_XBL for the bootloader advertisement type, which
            is used to determine if it is in bootload mode (instead of looking
            at the device name)
        - Added BLEX_EHSWITCH_PACKET and BroadcastEHSwitch for switches
        - Added the access config and access key characteristics as
            uuid_access_reserved1_characteristic and
            uuid_access_reserved2_characteristic
        - Added uuid_sensor_response_service, uuid_sensor1_response_characteristic,
            RequestSensorResponse, and SetSensorResponse for configuring the
            sensor response
        - Added support for bonding (BONDING_VALUE), but it is currently disabled
    V2.0.11 2015-12-27
        - Added encryption support
        - Added Cypress Bootloader support
        - Added support for large packet transfers (prepare_write, execute_write)
            in TransmitPacket
        - Added bootloaderMode to the GetScannedData return values
        - GetAddressList will also return devices that are in bootloader mode
        - Removed time.sleep(0.001) from Process()
    V2.0.10 2015-12-20
        - Added scanned Xicato advertisement packet logging to PacketLog.csv
        - In RequestData, fixed the if(value) check to be if(value != None) so
            that a value of 0 will evaluate as True
        - Starts networkConfigs[selectedTxNetworkIndex].txSqn with a random value so it won't always start at 0
        - Added SERVICE_DISCOVERY_TIME (6.0 s), which is used during Connect if
            the device is discovering services and characteristics
    V2.0.9 2015-11-09
        - Added XB1_EXTENDED_VIN_OFFSET for reading the finer resolution Vin
            and Vin Ripple bits
        - Added XB2_DALI_STATUS_OFFSET for reading the DALI address and status.
            Added uuid_dali_status_characteristic for GATT based reading.
        - Created CheckActivity to be able to catch exceptions
        - Attempts to re-start the BlueGiga connection if there are
            MAX_SERIAL_FAILURES (5)
    V2.0.8 2015-11-05
        - Added Indicate API for connection-based light indication
        - When end_procedure is completed, any device that was in the
            STATE_CONNECTING will be set to the STATE_STANDBY state
        - In the Disconnect API, if the device was in the STATE_CONNECTING
            state, it will no longer call ProcessFailedConnection
        - Added the optional logHandler argument to the Initialize API, so that
            the parent can pass in it's logHandler, for file logging
    V2.0.7 2015-10-20
        - Added GetDeviceId API
    V2.0.6  2015-09-30
        - Removed the list reversal of the device ID
        - The RequestLightSetup automatically picks the correct endianness
            if the address is for an existing device that has a swVersion.
            >= 0.043 is little-endian. Otherwise, it's big-endian.
    V2.0.5  2015-09-28
        - Renamed SetAdvertisingInterval to SetLocalAdvertisingInterval and
            added the advertising duration field
        - In EnableConnections, reversed the destination ID to match the order of
            the other APIs
        - When there's a scan response timeout, it stops scanning before trying
            to re-start it
        - Removed CENTRAL_STATE_ADVERTISING from the list of not(bgCentralState in .. values
            for IsSystemBusy
    V2.0.4  2015-09-27
        - Fixed RequestLightSetup bug. isSwapped should have been changed to
            isLittleEndian
        - Fixed SetLightSetup bug. For the 'Last' value, POWER_ON_LEVEL_LAST_VALUE
            doesn't need to be passed to the ConvertIntensityToValue function
        - Changed PENDING_WRITE_TIMEOUT from 30.0 to 1.0
        - Added a pending_write timeout check for BroadcastCommand
        - Added CENTRAL_STATE_ADVERTISING to the list of not(bgCentralState in .. values
            for IsSystemBusy
    V2.0.3  2015-09-23 Initial release

============================================
Copyright (c) 2015, Xicato Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of Xicato nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL XICATO BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

============================================

============================================
BGLib Python interface library code is placed under the MIT license
Copyright (c) 2014 Jeff Rowberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================

"""

"""
BASIC ARCHITECTURAL OVERVIEW:
    The program starts, initializes the dongle to a known state, then starts
    scanning. Each time an advertisement packet is found, a scan response
    event packet is generated. These packets are read by polling the serial
    port to which the BLE(D)11x is attached.

    The basic process is as follows:
      a. Scan for devices
      b. If the Xicato company ID is found in an ad packet, create an
            new XimBleDevice object and add it the list
      c. When an xBeacon 1 or xBeacon 2 advertisement packet is received, parse
            the data and store it in the corresponding XimBleDevice object, so
            that it can read out
      d. Provides APIs for the user to advertise data, connect to an XIM module,
            and read/write characteristics

"""

# NOTE: WINDOWS-ONLY without modifications, due to using "msvcrt" for keyboard input

import bglib, serial, time, datetime, optparse, signal, sys, os, cfg

if (cfg.WINDOWS):
    import msvcrt

import array
from Crypto.Cipher import AES
from bisect import bisect_left
from random import randint

import LogHandler


# ######################################
# BlueGiga
# ######################################

# Objects for using the bglib library
ble = 0
ser = 0

# BLE Controller States
CENTRAL_STATE_STANDBY = 0
CENTRAL_STATE_SCANNING = 1
CENTRAL_STATE_CONNECTING = 2
CENTRAL_STATE_STOPPING = 3

PERIPH_STATE_STANDBY = 0
PERIPH_STATE_ADVERTISING = 1
PERIPH_STATE_STOPPING = 2
##CENTRAL_STATE_ADVERTISING = 4

# BlueGiga State tracking
bgCentralState = CENTRAL_STATE_STANDBY
bgPeriphState = PERIPH_STATE_STANDBY
pending_write = False
ble_write_time = 0.0
last_connection_attempt_time = 0.0
blueGigaDeviceErrorCount = 0

# BlueGiga Initialization
hello_received = False
info_received = False
local_address = None

# Maximum allowed failures from the serial port before it is restarted
serialFailures = 0
MAX_SERIAL_FAILURES = 5

# Encryption Information
micFailed = False

# Bootload
bootloadRunning = False

ADMIN_KEY_DEFAULT = [0] * 16 # networkConfigs[selectedRxNetworkIndex].key


# ######################################
# File Storage
# ######################################

bleDirectory = "BLE"
workingDirectory = os.getcwd()
if (cfg.WINDOWS):
    bleComPortFileName = "{0}\\{1}\\BLE COM Port.txt".format(workingDirectory, bleDirectory)
    bleConnectParamsFileName = "{0}\\{1}\\BLE Connection Parameters.txt".format(workingDirectory, bleDirectory)
    bleRSSIFileName = "{0}\\{1}\\BLE RSSI Log.txt".format(workingDirectory, bleDirectory)
    uuidHandleMapFileName = "{0}\\{1}\\UUID Handle Map.csv".format(workingDirectory, bleDirectory)
    uuidHandleMapFileNameTemp = "{0}\\{1}\\UUID Handle Map.tmp".format(workingDirectory, bleDirectory)
    sensorUuidHandleMapFileName = "{0}\\{1}\\Sensor UUID Handle Map.csv".format(workingDirectory, bleDirectory)
    sensorUuidHandleMapFileNameTemp = "{0}\\{1}\\Sensor UUID Handle Map.tmp".format(workingDirectory, bleDirectory)
    bleNetworkConfigFileName = "{0}\\{1}\\BLE Network Config.txt".format(workingDirectory, bleDirectory)

if (cfg.LINUX or cfg.OSX):
    bleComPortFileName = "{0}/{1}/BLE_COM_Port.txt".format(workingDirectory, bleDirectory)
    bleConnectParamsFileName = "{0}/{1}/BLE_Connection_Parameters.txt".format(workingDirectory, bleDirectory)
    bleRSSIFileName = "{0}/{1}/BLE_RSSI_Log.txt".format(workingDirectory, bleDirectory)
    uuidHandleMapFileName = "{0}/{1}/UUID_Handle_Map.csv".format(workingDirectory, bleDirectory)
    uuidHandleMapFileNameTemp = "{0}/{1}/UUID_Handle_Map.tmp".format(workingDirectory, bleDirectory)
    sensorUuidHandleMapFileName = "{0}/{1}/Sensor_UUID_Handle_Map.csv".format(workingDirectory, bleDirectory)
    sensorUuidHandleMapFileNameTemp = "{0}/{1}/Sensor_UUID_Handle_Map.tmp".format(workingDirectory, bleDirectory)
    bleNetworkConfigFileName = "{0}/{1}/BLE_Network_Config.txt".format(workingDirectory, bleDirectory)



# ######################################
# Advertising and Scanning
# ######################################

# Advertising Parameters
ADVERTISING_INTERVAL_MIN = 20
ADVERTISING_INTERVAL_MAX = 50
ADVERTISING_WINDOW = 500
bleAdvertisingIntervalMin = ADVERTISING_INTERVAL_MIN
bleAdvertisingIntervalMax = ADVERTISING_INTERVAL_MAX
bleAdvertisingWindow = ADVERTISING_WINDOW

LOCAL_DEVICE_ID_DEFAULT_MIN = 0x7000
LOCAL_DEVICE_ID_DEFAULT_MAX = 0x7FFF
bleLocalDeviceId = LOCAL_DEVICE_ID_DEFAULT_MAX
bleLocalDeviceIdV0 = [254,254,254,254]

# Scanning State
scanningEnabled = True

# List of supported devices that have been scanned
peripheral_list = []

# Group polling
groupPollingIndex = 0
MAX_GROUP_REQUESTS = 5
GROUP_REQUEST_RETRY_INTERVAL = 30.0

# Type of device in peripheral_list
DEVICE_TYPE_XIM = 1
DEVICE_TYPE_XSENSOR = 2

# Advertisement Packet Types
ADV_PACKET_CONNECTABLE_ADV = 0
ADV_PACKET_NON_CONNECTABLE_ADV = 2
ADV_PACKET_TYPE_SCAN_RESPONSE = 4
ADV_PACKET_DISCOVERABLE_ADV = 8

# Advertisement Flags
AD1_LENGTH = 2
AD1_TYPE = 1
AD1_VALUE = 6

# xBeacon addresses
BLEX_UNICAST_ADDRESS_MAX = 0x7FFF
BLEX_GROUP_ADDRESS_MIN = 0xC000
BLEX_GROUP_ADDRESS_MAX = 0xFFFE
BLEX_BROADCAST_ADDRESS = 0xFFFF
UNASSIGNED_BROADCAST_ADDRESS = [0xFF, 0xFF, 0xFF]
ASSIGNED_ADDRESS_LENGTH = 2
UNASSIGNED_ADDRESS_LENGTH = 3
STORED_ADDRESS_LENGTH = 4

# Company ID
ADV_COMPANY_ID_XICATO = [0x53, 0x02]
XB_PACKET_TYPE_LENGTH = 1

# xBeacon1 field offsets
XB_COMPANY_ID_OFFSET = 0
XB_PACKET_TYPE_OFFSET = XB_COMPANY_ID_OFFSET + len(ADV_COMPANY_ID_XICATO)

# Xicato Advertisement Packet Types
PACKET_TYPE_XB1 = [0x01, 0x01]
PACKET_TYPE_XB2 = [0x02, 0x01]
PACKET_TYPE_XBL = [0x08, 0x01]
PACKET_TYPE_XSENSOR_MOTION = [0x10, 0x80]
PACKET_TYPE_XSENSOR_LUX = [0x20, 0x80]

XB_TYPE_UNASSIGNED_SOURCE = 0x03
XB_TYPE_UNASSIGNED_DEST = 0x04
XB_TYPE_UNENCRYPTED = 0x05
XB_TYPE_ENCRYPTED_FLAG = 0x80

UNASSIGNED_RESERVED_LENGTH = 4
UNASSIGNED_PAYLOAD_MAX_LENGTH = 12
XB_UNASSIGNED_SOURCE_ADDRESS_OFFSET = XB_PACKET_TYPE_OFFSET + XB_PACKET_TYPE_LENGTH
XB_UNASSIGNED_PAYLOAD_OFFSET = XB_UNASSIGNED_SOURCE_ADDRESS_OFFSET + UNASSIGNED_ADDRESS_LENGTH + UNASSIGNED_RESERVED_LENGTH

NUM_GROUPS = 16
GROUP_MEMBER_LENGTH = 2
ADV_GROUP_MEMBER_MAX = 5
XGROUP_LAST_PACKET_FLAG = 0x80
GROUP_MEMBER_UNASSIGNED = 0xFFFF

# xBeacon Legacy Support
XB_V0_PACKET_TYPE_LENGTH = 2
XB_V0_DEVICE_ID_LENGTH = 4
XB_V0_SEQUENCE_ID_LENGTH = 1
XB_V0_HOPS_LENGTH = 1

XB_V0_DEVICE_ID_OFFSET = XB_PACKET_TYPE_OFFSET + XB_V0_PACKET_TYPE_LENGTH
XB_V0_SEQUENCE_ID_OFFSET = XB_V0_DEVICE_ID_OFFSET + XB_V0_DEVICE_ID_LENGTH
XB_V0_HOPS_OFFSET = XB_V0_SEQUENCE_ID_OFFSET + XB_V0_SEQUENCE_ID_LENGTH


XB1_V0_PAYLOAD_OFFSET = XB_V0_HOPS_OFFSET + XB_V0_HOPS_LENGTH
XB2_V0_PAYLOAD_OFFSET = XB_V0_HOPS_OFFSET + XB_V0_HOPS_LENGTH + 3 # Skip the intensity and status bytes


MAX_INTENSITY = 10000
NUM_BLE_SCENES = 16
BLE_SCENE_SIZE = 6

# XBeacon Light Status 1 field lengths
XB1_INTENSITY_LENGTH = 2
XB1_STATUS_LENGTH = 1
XB1_TEMPERATURE_LENGTH = 1
XB1_POWER_LENGTH = 2
XB1_VIN_LENGTH = 1
XB1_VIN_RIPPLE_LENGTH = 1
XB1_LOCKOUT_TIME_LENGTH = 1
XB1_EXTENDED_VIN_LENGTH = 1
XB1_FIELD_LENGTH = 26

# XBeacon Light Status 1 field offsets
XB1_INTENSITY_OFFSET = 0
XB1_STATUS_OFFSET = XB1_INTENSITY_OFFSET + XB1_INTENSITY_LENGTH
XB1_POWER_OFFSET = XB1_STATUS_OFFSET + XB1_STATUS_LENGTH
XB1_LED_TEMPERATURE_OFFSET = XB1_POWER_OFFSET + XB1_POWER_LENGTH
XB1_PCB_TEMPERATURE_OFFSET = XB1_LED_TEMPERATURE_OFFSET + XB1_TEMPERATURE_LENGTH
XB1_VIN_OFFSET = XB1_PCB_TEMPERATURE_OFFSET + XB1_TEMPERATURE_LENGTH
XB1_VIN_RIPPLE_OFFSET = XB1_VIN_OFFSET + XB1_VIN_LENGTH
XB1_LOCKOUT_TIME_OFFSET = XB1_VIN_RIPPLE_OFFSET + XB1_VIN_RIPPLE_LENGTH
XB1_EXTENDED_VIN_OFFSET = XB1_LOCKOUT_TIME_OFFSET + XB1_LOCKOUT_TIME_LENGTH

# XBeacon Light Status 2 field lengths
XB2_PRODUCT_ID_LENGTH = 2
XB2_HOURS_LENGTH = 2
XB2_POWER_CYCLES_LENGTH = 2
XB2_LED_CYCLES_LENGTH = 2
XB2_OPERATION_EXTENSION_LENGTH = 1
XB2_DALI_STATUS_LENGTH = 1
XB2_FIELD_LENGTH = 26

# XBeacon Light Status 2 field offsets
##XB2_INTENSITY_OFFSET = 0
##XB2_STATUS_OFFSET = XB2_INTENSITY_OFFSET + XB1_INTENSITY_LENGTH
XB2_PRODUCT_ID_OFFSET = 0
XB2_HOURS_OFFSET = XB2_PRODUCT_ID_OFFSET + XB2_PRODUCT_ID_LENGTH
XB2_POWER_CYCLES_OFFSET = XB2_HOURS_OFFSET + XB2_HOURS_LENGTH
XB2_LED_CYCLES_OFFSET = XB2_POWER_CYCLES_OFFSET + XB2_POWER_CYCLES_LENGTH
XB2_OPERATION_EXTENSION_OFFSET = XB2_LED_CYCLES_OFFSET + XB2_LED_CYCLES_LENGTH
XB2_DALI_STATUS_OFFSET = XB2_OPERATION_EXTENSION_OFFSET + XB2_OPERATION_EXTENSION_LENGTH

# XBeacon Group field length
XBGROUP_HEADER_LENGTH = 1

# XBeacon Group field offsets
XBGROUP_HEADER_OFFSET = 0
XBGROUP_MEMBERS_OFFSET = 1


# XBeacon Device Info field lengths
XDEV_INFO_HW_VERSION_LENGTH = 1
XDEV_INFO_BLE_VERSION_LENGTH = 2
XDEV_INFO_LED_CONTROLLER_VERSION_LENGTH = 1
XDEV_INFO_PROGRAMMED_FLUX_LENGTH = 2
XDEV_INFO_OVERTEMP_THRESHOLD_VERSION_LENGTH = 1

# XBeacon Device Info field offsets
XDEV_INFO_PRODUCT_ID_OFFSET = 0
XDEV_INFO_HW_VERSION_OFFSET = XDEV_INFO_PRODUCT_ID_OFFSET + XB2_PRODUCT_ID_LENGTH
XDEV_INFO_BLE_VERSION_OFFSET = XDEV_INFO_HW_VERSION_OFFSET + XDEV_INFO_HW_VERSION_LENGTH
XDEV_INFO_LED_CONTROLLER_VERSION_OFFSET = XDEV_INFO_BLE_VERSION_OFFSET + XDEV_INFO_BLE_VERSION_LENGTH
XDEV_INFO_PROGRAMMED_FLUX_OFFSET = XDEV_INFO_LED_CONTROLLER_VERSION_OFFSET + XDEV_INFO_LED_CONTROLLER_VERSION_LENGTH
XDEV_INFO_OVERTEMP_THRESHOLD_VERSION_OFFSET = XDEV_INFO_PROGRAMMED_FLUX_OFFSET + XDEV_INFO_PROGRAMMED_FLUX_LENGTH

# XBeacon Bootload field offsets
XBOOT_BLE_VERSION_OFFSET = 0
XBOOT_DEVICE_TYPE_OFFSET = 2
XBOOT_FW_VERSION_OFFSET = 3

# xSensor field offsets
XSENSOR_TEMPERATURE_OFFSET = 0
XSENSOR_VIN_OFFSET = XSENSOR_TEMPERATURE_OFFSET + 1
XSENSOR_STATUS_VINLOWER_OFFSET = XSENSOR_VIN_OFFSET + 1
XSENSOR_VALUE_OFFSET = XSENSOR_STATUS_VINLOWER_OFFSET + 1


# xBeacon Encrypted field lengths
XBX_NETWORK_ID_LENGTH = 1
XBX_SEQUENCE_ID_LENGTH = 4
XBX_SOURCE_ADDR_LENGTH = 2
XBX_RFU_LENGTH = 1
XBX_RFU_VALUE = 0
XBX_PAYLOAD_LENGTH = 12
XBX_MIC_LENGTH = 4
IV_INDEX_LENGTH = 4
IV_INDEX_BIT_SHIFT = 5
SEQUENCE_ID_IV_INDEX_MASK = 0x20
SEQUENCE_ID_MSB_MASK = 0x1F
NONCE_LENGTH = 13
NONCE_SOURCE_ADDR_OFFSET = 0
NONCE_SQN_OFFSET = NONCE_SOURCE_ADDR_OFFSET + ASSIGNED_ADDRESS_LENGTH
NONCE_RFU_OFFSET = NONCE_SQN_OFFSET + XBX_SEQUENCE_ID_LENGTH


# xBeacon Encrypted field offsets
XBX_COMPANY_ID_OFFSET = 0
XBX_NETWORK_ID_OFFSET = XBX_COMPANY_ID_OFFSET + len(ADV_COMPANY_ID_XICATO)
XBX_SOURCE_ADDR_OFFSET = XBX_NETWORK_ID_OFFSET + XBX_NETWORK_ID_LENGTH
XBX_SEQUENCE_ID_OFFSET = XBX_SOURCE_ADDR_OFFSET + XBX_SOURCE_ADDR_LENGTH
XBX_RFU_OFFSET = XBX_SEQUENCE_ID_OFFSET + XBX_SEQUENCE_ID_LENGTH
XBX_PAYLOAD_AND_MIC_OFFSET = XBX_RFU_OFFSET + XBX_RFU_LENGTH

# xBeacon Encrypted field values
XB_TYPE_ENCRYPTED_FLAG = 0x80
XBX_HEADER_ENCRYPTED_FLAG = 0x40
XBX_NETWORK_ID_PARTIAL_ID_MASK = 0x1F
XBX_SEQUENCE_ID_MAX_VALUE = 2 ** 32


# xBeacon Network Info field lengths
XBN_MIC_LENGTH = 4
XBN_PACKET_TYPE_LENGTH = 1
XBN_PARTIAL_NETWORK_ID_LENGTH = 1

# xBeacon Network Info field offsets
XBN_COMPANY_ID_OFFSET = 0
XBN_PACKET_TYPE_OFFSET = XBN_COMPANY_ID_OFFSET + len(ADV_COMPANY_ID_XICATO)
XBN_PARTIAL_NETWORK_ID_OFFSET = XBN_PACKET_TYPE_OFFSET + XBN_PACKET_TYPE_LENGTH
XBN_SOURCE_ADDR_OFFSET = XBN_PARTIAL_NETWORK_ID_OFFSET + XBN_PARTIAL_NETWORK_ID_LENGTH
XBN_SEQUENCE_ID_OFFSET = (XBN_SOURCE_ADDR_OFFSET + XBX_SOURCE_ADDR_LENGTH)
XBN_IV_INDEX_OFFSET = (XBN_SEQUENCE_ID_OFFSET + XBX_SEQUENCE_ID_LENGTH)
XBN_PAYLOAD_AND_MIC_OFFSET = (XBN_IV_INDEX_OFFSET + IV_INDEX_LENGTH)

# xBeacon Network Info Payload
EFIELD_NETWORK_INFO_ID_LENGTH = 3
EFIELD_NETWORK_INFO_RFU_LENGTH = 1
EFIELD_NETWORK_INFO_ID_OFFSET = 0
EFIELD_NETWORK_INFO_RFU_OFFSET = EFIELD_NETWORK_INFO_ID_OFFSET + EFIELD_NETWORK_INFO_ID_LENGTH
XBN_PAYLOAD_LENGTH = EFIELD_NETWORK_INFO_RFU_OFFSET + EFIELD_NETWORK_INFO_RFU_LENGTH


# Xicato Encrypted Advertisement Packet Types
ENCRYPTED_PACKET_TYPE_XB1 = 0x01
ENCRYPTED_PACKET_TYPE_XB2 = 0x02
ENCRYPTED_PACKET_TYPE_XDEV_INFO = 0x03
ENCRYPTED_PACKET_TYPE_XGROUP = 0x08
ENCRYPTED_PACKET_TYPE_BOOTLOAD = 0x0F
ENCRYPTED_PACKET_TYPE_LIGHT_CONTROL = 0x10
ENCRYPTED_PACKET_TYPE_RECALL_SCENE = 0x11
ENCRYPTED_PACKET_TYPE_INDICATE = 0x12
ENCRYPTED_PACKET_TYPE_SET_CONNECTABLE = 0x20
ENCRYPTED_PACKET_TYPE_REQUEST_ADV = 0x21
ENCRYPTED_PACKET_TYPE_SENSORS_ALL = 0x80
ENCRYPTED_PACKET_TYPE_SENSOR_MOTION = 0x10
ENCRYPTED_PACKET_TYPE_SENSOR_LUX = 0x20

# Network Config Mode
NETWORK_TX = 0
NETWORK_RX = 1
selectedTxNetworkIndex = 0
selectedRxNetworkIndex = 1
NETWORK_INFO_RETRIES = 2

NETWORK_ID_LENGTH = 4
NETWORK_KEY_LENGTH = 16
NETWORK_KEY_NONE = [0] * 16

NETWORK_PERM_ADV_XBEACON = 0x01
NETWORK_PERM_LIGHT_LEVEL = 0x02
NETWORK_PERM_SENSORS = 0x04
NETWORK_PERM_CONFIG_BEACONS = 0x08
NETWORK_PERM_LIGHT_SETUP_FIELD = 0x10
NETWORK_PERM_LIGHT_SETUP_OEM = 0x20
NETWORK_PERM_ALL = 0x3F
NETWORK_PERM_RX_ALL = 0x3E
NETWORK_PERM_CONNECTABLE = 0x3E

# xBootloadMode field offsets
XBL_FIELD_LENGTH = 8

# xBeacon Light Control values
BLEX_SENSOR_PACKET = [0x01, 0x00]
BLEX_SENSOR_LIGHT_CONTROL = 0x80
BLEX_SENSOR_RECALL_SCENE = 0x81
BLEX_SENSOR_INDICATE = 0x86

BLEX_ENABLE_CONNECTIONS_PACKET = [0x00, 0x01]
STOP_FADING_VALUE = 65535
POWER_ON_LEVEL_LAST_VALUE = 65535
POWER_ON_LEVEL_USE_OTHER = 65534
SENSOR_CONTROL_VALUE = 65532

BLE_SCENE_UNASSIGNED = 65535

BLEX_EHSWITCH_PACKET = [0x00, 0x02]

# ######################################
# Connecting
# ######################################

# Connection Parameters
MIN_INTERVAL = 12   # (units of 1.25ms)
MAX_INTERVAL = 80   # (units of 1.25ms)
CONN_TIMEOUT = 100  # (units of 10ms)
SLAVE_LATENCY = 2
RX_GAIN = 1
MIN_INTERVAL_LOWER_LIMIT = 6
MAX_CONNECTIONS = 3

# Connection Timeouts
CONNECT_ATTEMPT_WARNING = 0.8
CONNECT_ATTEMPT_TIMEOUT = 1.4
SERVICE_DISCOVERY_TIME = 7.0
DISCONNECT_TIMEOUT = CONN_TIMEOUT * 10.0 / 1000.0 + 0.010
CONNECTION_TEST_INTERVAL = 0.3
lastConnectionTest = 0.0
SCAN_RESPONSE_TIMEOUT = 5.0
PENDING_WRITE_TIMEOUT = 1.0

# Connection Error Counters
MAX_UNEXPECTED_DISCONNECTIONS = 3
MAX_FAILED_CONNECTION_ATTEMPTS = 3

# ######################################
# Encryption
# ######################################
ENCRYPTION_ENABLED = True
BONDING_VALUE = 0 # 1 = Bonding Enabled

adminKey = [0] * 16 # networkConfigs[selectedRxNetworkIndex].key
oemKey = [0] * 16
adminMode = False


# ######################################
# Services and Characteristics
# ######################################

readInProgress = False

# Standard BLE group types
uuid_service = [0x28, 0x00] # 0x2800
uuid_client_characteristic_configuration = [0x29, 0x02] # 0x2902

# Device Information Service and Characteristics
uuid_dis_service = [0x18, 0x0A]
uuid_dis_mfg_name_characteristic = [0x2A, 0x29]
uuid_dis_model_number_characteristic = [0x2A, 0x24]
uuid_dis_serial_number_characteristic = [0x2A, 0x25]
uuid_dis_hardware_rev_characteristic = [0x2A, 0x27]
uuid_dis_firmware_rev_characteristic = [0x2A, 0x26]
uuid_dis_software_rev_characteristic = [0x2A, 0x28]

# Eddystone-URL Service
uuid_uriBeacon_service = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x80, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_lock_state_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x81, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_lock_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x82, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_unlock_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x83, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_uri_data_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x84, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_flags_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x85, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_tx_power_levels_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x86, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_tx_power_mode_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x87, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_period_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x88, 0x20, 0x0C, 0xEE]))
uuid_uriBeacon_reset_characteristic = list(reversed([0xD8, 0x81, 0xC9, 0x1A, 0xB9, 0x99, 0x96, 0xAB, 0xBA, 0x40, 0x86, 0x87, 0x89, 0x20, 0x0C, 0xEE]))

EDDYSTONE_URI_PREFIXES = ["http://www.", "https://www.", "http://", "https://", "urn:uuid:"]
EDDYSTONE_URI_SUFFIXES = [".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/", ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov"]

# The following services are all Xicato-defined
# Light Control Service
uuid_light_control_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x10, 0x9F, 0xAA, 0x4C]))
uuid_light_control_level_control_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x11, 0x9F, 0xAA, 0x4C]))
uuid_light_control_indicate_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x12, 0x9F, 0xAA, 0x4C]))
uuid_light_control_setup_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x13, 0x9F, 0xAA, 0x4C]))
uuid_light_control_status_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x14, 0x9F, 0xAA, 0x4C]))
uuid_light_control_scenes_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x15, 0x9F, 0xAA, 0x4C]))

# XIM Access Service
uuid_xim_access_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x20, 0x9F, 0xAA, 0x4C]))
uuid_device_id_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x21, 0x9F, 0xAA, 0x4C]))
uuid_access_key_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x23, 0x9F, 0xAA, 0x4C]))
uuid_access_control_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x24, 0x9F, 0xAA, 0x4C]))

# V0.075+
uuid_group_membership_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x22, 0x9F, 0xAA, 0x4C]))
uuid_access_network_select_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x23, 0x9F, 0xAA, 0x4C]))
uuid_access_user_login_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x24, 0x9F, 0xAA, 0x4C]))
uuid_access_config_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x25, 0x9F, 0xAA, 0x4C]))
uuid_access_admin_login_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x26, 0x9F, 0xAA, 0x4C]))
uuid_access_network_list_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x27, 0x9F, 0xAA, 0x4C]))
uuid_access_network_config_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x28, 0x9F, 0xAA, 0x4C]))
uuid_access_network_header_key_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x29, 0x9F, 0xAA, 0x4C]))

uuid_access_id_list_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x28, 0x9F, 0xAA, 0x4C]))

# XIM Radio Configuration Service
uuid_xim_radio_configuration_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x30, 0x9F, 0xAA, 0x4C]))
uuid_rssi_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x31, 0x9F, 0xAA, 0x4C]))
uuid_tx_power_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x32, 0x9F, 0xAA, 0x4C]))
uuid_rx_gain_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x33, 0x9F, 0xAA, 0x4C]))
uuid_advertisement_settings_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x34, 0x9F, 0xAA, 0x4C]))

# XIM Data Service
uuid_xim_data_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x50, 0x9F, 0xAA, 0x4C]))
uuid_xim_priority_data_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x51, 0x9F, 0xAA, 0x4C]))
uuid_xim_memory_location_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x52, 0x9E, 0xAA, 0x4C]))
uuid_xim_memory_value_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x53, 0x9E, 0xAA, 0x4C]))
uuid_xim_temperature_histogram_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x53, 0x9E, 0xAA, 0x4C]))
uuid_xim_intensity_histogram_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x54, 0x9E, 0xAA, 0x4C]))
uuid_xim_historic_data_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x52, 0x9E, 0xAA, 0x4C]))
MAX_BANK_DATA_PAYLOAD_SIZE = 16

# iBeacon Service
uuid_iBeacon_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x60, 0x9F, 0xAA, 0x4C]))
uuid_iBeacon_uuid_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x61, 0x9F, 0xAA, 0x4C]))
uuid_iBeacon_major_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x62, 0x9F, 0xAA, 0x4C]))
uuid_iBeacon_minor_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x63, 0x9F, 0xAA, 0x4C]))
uuid_iBeacon_measured_power_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x64, 0x9F, 0xAA, 0x4C]))
uuid_iBeacon_period_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x65, 0x9F, 0xAA, 0x4C]))

# AltBeacon Service
uuid_altBeacon_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x80, 0x9F, 0xAA, 0x4C]))
uuid_altBeacon_company_id_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x81, 0x9F, 0xAA, 0x4C]))
uuid_altBeacon_beacon_id_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x82, 0x9F, 0xAA, 0x4C]))
uuid_altBeacon_mfg_data_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x83, 0x9F, 0xAA, 0x4C]))
uuid_altBeacon_measured_power_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x84, 0x9F, 0xAA, 0x4C]))
uuid_altBeacon_period_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x85, 0x9F, 0xAA, 0x4C]))

# Scan Response Configuration Service
uuid_scan_response_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x70, 0x9F, 0xAA, 0x4C]))
uuid_scan_response_device_name_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x71, 0x9F, 0xAA, 0x4C]))
uuid_scan_response_user_data_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x72, 0x9F, 0xAA, 0x4C]))

DEVICE_NAME_MAX_LENGTH = 20

# DALI Service
uuid_dali_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x40, 0x9E, 0xAA, 0x4C]))
uuid_dali_command_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x41, 0x9E, 0xAA, 0x4C]))

uuid_dali_status_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x43, 0x9E, 0xAA, 0x4C]))
uuid_dali_light_config_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x44, 0x9E, 0xAA, 0x4C]))
uuid_dali_address_config_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x45, 0x9E, 0xAA, 0x4C]))
uuid_dali_scenes_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x46, 0x9E, 0xAA, 0x4C]))


# 1-10V Service
uuid_dim_1_10V_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x30, 0x9E, 0xAA, 0x4C]))
uuid_dim_1_10V_status_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x31, 0x9E, 0xAA, 0x4C]))
uuid_dim_1_10V_config_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x32, 0x9E, 0xAA, 0x4C]))


#Legacy
uuid_dali_response_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x42, 0x9E, 0xAA, 0x4C]))

# Bootloader Service
uuid_bls_service = list(reversed([0x1B, 0xC5, 0xD5, 0xA5, 0x02, 0x00, 0xF4, 0xAB, 0xE4, 0x11, 0xCE, 0xF8, 0x00, 0x00, 0x06, 0x00]))
uuid_bls_command_characteristic = list(reversed([0x1B, 0xC5, 0xD5, 0xA5, 0x02, 0x00, 0xF4, 0xAB, 0xE4, 0x11, 0xCE, 0xF8, 0x01, 0x00, 0x06, 0x00]))

# Sensor Response Configuration Service
uuid_sensor_response_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x90, 0x9F, 0xAA, 0x4C]))
uuid_sensor1_response_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x91, 0x9F, 0xAA, 0x4C]))
uuid_sensor2_response_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x92, 0x9F, 0xAA, 0x4C]))
##uuid_scan_response_user_data_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0x92, 0x9F, 0xAA, 0x4C]))

# OEM Service
uuid_oem_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA0, 0x9F, 0xAA, 0x4C]))
uuid_access_oem_login_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA1, 0x9F, 0xAA, 0x4C]))
uuid_access_oem_data_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA2, 0x9F, 0xAA, 0x4C]))



# XSensor

# Sensor Configuration Service
uuid_sensor_config_service = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA0, 0x9F, 0xAA, 0x4C]))
uuid_sensor_general_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA1, 0x9F, 0xAA, 0x4C]))
uuid_sensor_lux_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA2, 0x9F, 0xAA, 0x4C]))
uuid_sensor_motion_characteristic = list(reversed([0x7A, 0xDF, 0x74, 0xF0, 0x0B, 0xD3, 0x15, 0x8E, 0xD3, 0x44, 0xDF, 0x2A, 0xA3, 0x9F, 0xAA, 0x4C]))

SERVICE_ATTRIBUTES_NONE = 0
SERVICE_ATTRIBUTES_FINDING = 1
SERVICE_ATTRIBUTES_FOUND = 2

# The ServiceInfo class stores the information about each service
class ServiceInfo(object):
    def __init__(self, id):
        self.uuid = id
        self.handle = None
        self.att_handle_start = None
        self.att_handle_end = None
        self.attributesDiscovered = SERVICE_ATTRIBUTES_NONE

# The AttributeInfo class stores the information about each characteristic
class AttributeInfo(object):
    def __init__(self, id, hasCCC = False):
        self.uuid = id
        self.handle = None
        self.value = None
        self.hasCCC = hasCCC
        self.cccHandle = None
        self.cccValue = None
        self.notifiedValue = None


# ######################################
# Device Information
# ######################################

# BleDevice states
STATE_STANDBY = 0
STATE_CONNECTING = 1
STATE_GET_VERSION = 2
STATE_FINDING_SERVICES = 3
STATE_FINDING_ATTRIBUTES = 4
STATE_ENABLING_NOTIFICATIONS = 5
STATE_LISTENING_DATA = 6
STATE_DISCONNECTING = 7
STATE_ENCRYPTING = 8

# The BleDevice class stores generic information about BLE device
class BleDevice(object):
    def __init__(self, ble, ser, address, address_type, deviceType):
        self.ble = ble #,
        self.ser = ser
        self.address = address #ble mac address
        self.swVersion = None
        self.hwVersion = None
        self.address_type = address_type
        self.deviceType = deviceType
        self.connection_handle = None
        self.connectionState = STATE_STANDBY
        self.connectionSent = False
        self.connectionAttemptTime = None
        self.disconnectTime = None
        self.unexpectedDisconnections = 0
        self.failedConnectionAttempts = 0
        self.longConnectionTime = None
        self.deviceName = None
        self.lastScanTime = None
        self.encryptionRequired = ENCRYPTION_ENABLED
        self.bootloaderMode= False
        self.bootloaderModeUpdateTime = 0.0
        self.packetStatus = None
        self.bulkPacketTransferred = False
        self.encryptedAdv = False
        self.adminLoggedIn = False
        self.hasEncryptedHeader = False
        self.txNetwork = None
        self.groups = [None] * NUM_GROUPS
        self.receivedAllGroups = False
        self.requestGroupAttempts = 0
        self.lastGroupRequestTime = 0.0

        self.serviceList = []
        self.attributeList = []

        self.blServiceList = [ServiceInfo(uuid_bls_service)]
        self.blAttributeList = [  AttributeInfo(uuid_bls_command_characteristic)]


    def IsConnected(self):
        return (self.connectionState == STATE_LISTENING_DATA) and (self.connection_handle != None)

    def IsConnecting(self):
        return (not(self.connectionState in [STATE_STANDBY, STATE_DISCONNECTING, STATE_LISTENING_DATA]))

    def IsDiscovering(self):
        return (self.connectionState in [STATE_FINDING_SERVICES, STATE_FINDING_ATTRIBUTES])

    def IsEncryptedAdv(self):
        return self.encryptedAdv

# The XimBleDevice class stores information that is specific to XIM BLE devices
class XimBleDevice(BleDevice):
    def __init__(self, ble, ser, address, address_type):
        BleDevice.__init__(self, ble, ser, address, address_type, DEVICE_TYPE_XIM)


        self.pcRssiValue = None

        # xBeacon1 Fields
        self.scannedDeviceId = None  #logical address
        self.scannedProductId = None
        self.scannedIntensity = None
        self.scannedPower = None
        self.scannedStatus = None
        self.scannedLedTemperature = None
        self.scannedPcbTemperature = None
        self.scannedVin = None
        self.scannedVinRipple = None
        self.scannedLockoutTimeRemaining = None

        # xBeacon2 Fields
        self.scannedHours = None
        self.scannedPowerCycles = None
        self.scannedLedCycles = None
        self.daliStatus = None
        self.scannedRssi = None

        self.ledControllerVersion = None
        self.programmedFlux = None
        self.overloadTemperature = None

        # Last time each xBeacon was received
        self.xb1UpdateTime = None
        self.xb2UpdateTime = None
        self.deviceInfoUpdateTime = None

        self.InitializeServiceAttributeList()

    def InitializeServiceAttributeList(self):
        # Contains the list of all supported services
        self.serviceList = [ServiceInfo(uuid_dis_service), ServiceInfo(uuid_xim_access_service), ServiceInfo(uuid_dali_service), ServiceInfo(uuid_xim_radio_configuration_service), ServiceInfo(uuid_xim_data_service),
                                     ServiceInfo(uuid_iBeacon_service), ServiceInfo(uuid_uriBeacon_service), ServiceInfo(uuid_altBeacon_service), ServiceInfo(uuid_scan_response_service),
                                     ServiceInfo(uuid_light_control_service)]



        # Contains the list of all supported characteristics
        self.attributeList = [  AttributeInfo(uuid_dis_mfg_name_characteristic), AttributeInfo(uuid_dis_model_number_characteristic), AttributeInfo(uuid_dis_serial_number_characteristic),
                                    AttributeInfo(uuid_dis_hardware_rev_characteristic), AttributeInfo(uuid_dis_firmware_rev_characteristic), AttributeInfo(uuid_dis_software_rev_characteristic),

                                AttributeInfo(uuid_rssi_characteristic), AttributeInfo(uuid_tx_power_characteristic), AttributeInfo(uuid_rx_gain_characteristic),
                                    AttributeInfo(uuid_advertisement_settings_characteristic),

                                AttributeInfo(uuid_xim_priority_data_characteristic),

                                AttributeInfo(uuid_iBeacon_uuid_characteristic), AttributeInfo(uuid_iBeacon_major_characteristic), AttributeInfo(uuid_iBeacon_minor_characteristic),
                                    AttributeInfo(uuid_iBeacon_measured_power_characteristic), AttributeInfo(uuid_iBeacon_period_characteristic),

                                AttributeInfo(uuid_uriBeacon_lock_state_characteristic), AttributeInfo(uuid_uriBeacon_lock_characteristic),
                                    AttributeInfo(uuid_uriBeacon_unlock_characteristic), AttributeInfo(uuid_uriBeacon_uri_data_characteristic), AttributeInfo(uuid_uriBeacon_flags_characteristic),
                                    AttributeInfo(uuid_uriBeacon_tx_power_levels_characteristic), AttributeInfo(uuid_uriBeacon_tx_power_mode_characteristic), AttributeInfo(uuid_uriBeacon_period_characteristic),
                                    AttributeInfo(uuid_uriBeacon_reset_characteristic),

                                AttributeInfo(uuid_altBeacon_company_id_characteristic), AttributeInfo(uuid_altBeacon_beacon_id_characteristic), AttributeInfo(uuid_altBeacon_mfg_data_characteristic),
                                    AttributeInfo(uuid_altBeacon_measured_power_characteristic), AttributeInfo(uuid_altBeacon_period_characteristic),

                                AttributeInfo(uuid_scan_response_device_name_characteristic), AttributeInfo(uuid_scan_response_user_data_characteristic),

                                AttributeInfo(uuid_light_control_level_control_characteristic), AttributeInfo(uuid_light_control_indicate_characteristic), AttributeInfo(uuid_light_control_setup_characteristic),
                                    AttributeInfo(uuid_light_control_status_characteristic)

                                ]

# The XSensorBleDevice class stores information that is specific to Xicato Sensor devices
class XSensorBleDevice(BleDevice):
    def __init__(self, ble, ser, address, address_type):
        BleDevice.__init__(self, ble, ser, address, address_type, DEVICE_TYPE_XSENSOR)

        self.blServiceList = [ServiceInfo(uuid_bls_service)]
        self.blAttributeList = [  AttributeInfo(uuid_bls_command_characteristic)]

        self.pcRssiValue = None

        # xBeacon1 Fields
        self.scannedDeviceId = None
        self.scannedProductId = None
        self.scannedStatus = None
        self.scannedTemperature = None
        self.scannedLux = None
        self.scannedMotion = None
        self.scannedVin = None

        # xBeacon2 Fields
##        self.scannedHours = None
##        self.scannedPowerCycles = None
##        self.scannedLedCycles = None
        self.scannedRssi = None
        self.fwVersion = None

        # Last time each xBeacon was received
        self.motionUpdateTime = None
        self.luxUpdateTime = None
        self.historyUpdateTime = None

        self.InitializeServiceAttributeList()


    def InitializeServiceAttributeList(self):
        # Contains the list of all supported services
        self.serviceList = [ServiceInfo(uuid_dis_service), ServiceInfo(uuid_xim_access_service), ServiceInfo(uuid_xim_radio_configuration_service),
                                     ServiceInfo(uuid_iBeacon_service), ServiceInfo(uuid_uriBeacon_service), ServiceInfo(uuid_altBeacon_service), ServiceInfo(uuid_scan_response_service),
                                     ServiceInfo(uuid_sensor_config_service)]


        # Contains the list of all supported characteristics
        self.attributeList = [  AttributeInfo(uuid_dis_mfg_name_characteristic), AttributeInfo(uuid_dis_model_number_characteristic), AttributeInfo(uuid_dis_serial_number_characteristic),
                                    AttributeInfo(uuid_dis_hardware_rev_characteristic), AttributeInfo(uuid_dis_firmware_rev_characteristic), AttributeInfo(uuid_dis_software_rev_characteristic),

                                AttributeInfo(uuid_rssi_characteristic), AttributeInfo(uuid_tx_power_characteristic), AttributeInfo(uuid_rx_gain_characteristic),
                                    AttributeInfo(uuid_advertisement_settings_characteristic),

                                AttributeInfo(uuid_iBeacon_uuid_characteristic), AttributeInfo(uuid_iBeacon_major_characteristic), AttributeInfo(uuid_iBeacon_minor_characteristic),
                                    AttributeInfo(uuid_iBeacon_measured_power_characteristic), AttributeInfo(uuid_iBeacon_period_characteristic),

                                AttributeInfo(uuid_uriBeacon_lock_state_characteristic), AttributeInfo(uuid_uriBeacon_lock_characteristic),
                                    AttributeInfo(uuid_uriBeacon_unlock_characteristic), AttributeInfo(uuid_uriBeacon_uri_data_characteristic), AttributeInfo(uuid_uriBeacon_flags_characteristic),
                                    AttributeInfo(uuid_uriBeacon_tx_power_levels_characteristic), AttributeInfo(uuid_uriBeacon_tx_power_mode_characteristic), AttributeInfo(uuid_uriBeacon_period_characteristic),
                                    AttributeInfo(uuid_uriBeacon_reset_characteristic),

                                AttributeInfo(uuid_altBeacon_company_id_characteristic), AttributeInfo(uuid_altBeacon_beacon_id_characteristic), AttributeInfo(uuid_altBeacon_mfg_data_characteristic),
                                    AttributeInfo(uuid_altBeacon_measured_power_characteristic), AttributeInfo(uuid_altBeacon_period_characteristic),

                                AttributeInfo(uuid_scan_response_device_name_characteristic), AttributeInfo(uuid_scan_response_user_data_characteristic)



                                ]


# ######################################
# Encryption
# ######################################

networkConfigs = []
aesNonce = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

##NETWORK_STATE_DISABLED = 0
##NETWORK_STATE_SCANNING = 1
##NETWORK_STATE_REQUESTING = 2
##NETWORK_STATE_SYNCED = 3
##
class NetworkConfig(object):
    def __init__(self, id, networkHeaderKey, key, sqn):
        self.id = id
        self.headerKey = networkHeaderKey
        self.key = key
        self.txSqn = sqn

    def Print(self):
        print("id: {0}, headerKey: {3}, key: {1}, txSqn: {2}".format(self.id, self.key, self.txSqn, self.headerKey))
##        if(isEnabled):
##            self.networkSyncState = NETWORK_STATE_SCANNING
##            self.networkSyncTime = time.time()
##        else:
##            self.networkSyncState = NETWORK_STATE_DISABLED
##            self.networkSyncTime = None
##        self.closestNeighborAddress = None
##        self.highestRssi = None


# ######################################
# BlueGiga Callback Description:
# ble_rsp are confirmations that command was executed
# ble_evt is an event
# ######################################


# ######################################
# Section: Advertisements - Internal Functions
# ######################################

# Converts an intensity (0-100%) to the format that the XIM uses (10000 = 100%)
def ConvertIntensityToValue(intensity):
    return int(round(intensity * 100.0, 0))

# Converts the format that the XIM uses (10000 = 100%) to an intensity (0-100%)
def ConvertValueToIntensity(value):
    return (float(value) / 100.0)

# Advertisement parameters are updated
def my_ble_rsp_gap_set_adv_parameters(sender, args):
    global pending_write
    pending_write = False

    if(args['result'] == 0):
        logHandler.printLog("{0}: set_adv_parameters command complete {1}".format(time.time(), args))
    else:
        logHandler.printLog("{0}: set_adv_parameters command failed {1}".format(time.time(), args))

# Set the data in the advertisement packet. advData is a list
def SetAdvertisingData(advData):
    # 0 means advertising data, non zero means scan response data
    ble.send_command(ser, ble.ble_cmd_gap_set_adv_data(0, advData))
    SetBusyFlag()

# Advertisement packet data is updated
def my_ble_rsp_gap_set_adv_data(sender, args):
    global pending_write
    pending_write = False

    if(args['result'] == 0):
        logHandler.printLog("{0}: set_adv_data command complete {1}".format(time.time(), args))
    else:
        logHandler.printLog("{0}: set_adv_data command failed {1}".format(time.time(), args))

# Enable/Disable advertising (state: True/False)
def SetAdvertisingState(state):
    global bgPeriphState
    global advertisingStartTime
    # Param 0: 4 means user data, 0 means not discoverable
    # Param 1: 0 means not connectable
    if(state):
        value = 4
        bgPeriphState = PERIPH_STATE_ADVERTISING
        advertisingStartTime = time.time()
    else:
        value = 0
        bgPeriphState = PERIPH_STATE_STOPPING

    ble.send_command(ser, ble.ble_cmd_gap_set_mode(value, 0))
    SetBusyFlag()

# Advertisement mode (enabled/disabled) is updated
def my_ble_rsp_gap_set_mode(sender, args):
    global pending_write, bgPeriphState
    pending_write = False

    if(args['result'] == 0):
        logHandler.printLog("{0}: set_mode command complete {1}".format(time.time(), args))

        if(bgPeriphState == PERIPH_STATE_STOPPING):
            bgPeriphState = PERIPH_STATE_STANDBY
    else:
        logHandler.printLog("{0}: set_mode command failed {1}".format(time.time(), args))

        if(bgPeriphState == PERIPH_STATE_STOPPING):
            bgPeriphState = PERIPH_STATE_ADVERTISING

def IsGroupAddress(address):
    return (len(address) == 1) and (address[0] >= BLEX_GROUP_ADDRESS_MIN)

# Transmits an advertisement packet  with xBeacon type packetType (1-byte integer)
#  and packet data txPacket (list)
def BroadcastCommand(packetType, txPacket):

    fullPacket = [2, 1, 6, 11 + len(txPacket), 0xFF] + ADV_COMPANY_ID_XICATO + packetType + bleLocalDeviceIdV0 + [networkConfigs[selectedTxNetworkIndex].txSqn % 256, 0] + txPacket
    networkConfigs[selectedTxNetworkIndex].txSqn = networkConfigs[selectedTxNetworkIndex].txSqn + 1
    if(networkConfigs[selectedTxNetworkIndex].txSqn >= XBX_SEQUENCE_ID_MAX_VALUE):
        networkConfigs[selectedTxNetworkIndex].txSqn = 1

    print ("fullPacket: {0}".format(fullPacket))

    TransmitAdvertisement(fullPacket)
    UpdateNetworkConfigFile()

def BroadcastIXBUnassigned(destination, payloadType, payload):
    payload = [payloadType] + destination [1:3] + payload
    xbUnassigned = [AD1_LENGTH, AD1_TYPE, AD1_VALUE, 17, 0x07]
    xbUnassigned.append(destination[0])
    xbUnassigned += [XBX_RFU_VALUE] * 4
    xbUnassigned += payload
    xbUnassigned += [0] * (11 - len(payload))
    xbUnassigned += [0x09, 0x09] # , 0x58, 0x49, 0x35, 0x42, 0x31, 0x32, 0x33, 0x34]
    xbUnassigned += [ord('X'), ord('I')]
    xbUnassigned += HexToAsciiList(XB_TYPE_UNASSIGNED_DEST)
    xbUnassigned += GetLocalSourceAsciiAddress()  # Source address

    logHandler.printLog("Unassigned iXB packet: {0}".format(xbUnassigned), True)
    TransmitAdvertisement(xbUnassigned)

def HexListToAsciiList(hexList):
    asciiList = []
    for hexValue in hexList:
        asciiList += HexToAsciiList(hexValue)
    return asciiList

def HexToAsciiList(hexValue):
    hexString = "%.2X" % hexValue
    return [ord(hexString[0]), ord(hexString[1])]

def GetLocalSourceAddress():
    return bleLocalDeviceId

def GetLocalSourceAsciiAddress():
    return HexListToAsciiList(ConvertIntToList(bleLocalDeviceId, 2))

def BroadcastIXBAssigned(destination, payloadType, payload):
    if(len(destination) == 1):
        destinationList = ConvertIntToList(destination[0], 2)

    payload = [payloadType] + destinationList + payload

    networkConfigs[selectedTxNetworkIndex].txSqn += 1
    if(networkConfigs[selectedTxNetworkIndex].txSqn >= XBX_SEQUENCE_ID_MAX_VALUE):
        networkConfigs[selectedTxNetworkIndex].txSqn = 1


##    if(((networkConfigs[selectedTxNetworkIndex].key != NETWORK_KEY_NONE) and IsGroupAddress(destination)) or (IsEncryptedAdvEnabled(destination))):
    if((IsEncryptedAdvEnabled(destination)) and (adminMode or (networkConfigs[selectedTxNetworkIndex].key != NETWORK_KEY_NONE))):

        aesNonce[NONCE_SOURCE_ADDR_OFFSET: NONCE_SOURCE_ADDR_OFFSET + XBX_SOURCE_ADDR_LENGTH] = ConvertIntToList(GetLocalSourceAddress(), 2)
        aesNonce[NONCE_SQN_OFFSET: NONCE_SQN_OFFSET + XBX_SEQUENCE_ID_LENGTH] = ConvertIntToList(networkConfigs[selectedTxNetworkIndex].txSqn, XBX_SEQUENCE_ID_LENGTH)
##        aesNonce[NONCE_RFU_OFFSET: NONCE_RFU_OFFSET + XBX_RFU_LENGTH] = [0] * XBX_RFU_LENGTH

        logHandler.printLog("aesNonce: {0}".format(aesNonce))
        logHandler.printLog("aesKey: {0}".format(networkConfigs[selectedTxNetworkIndex].key))

        eMsg, eMic = AesCcmEncrypt(networkConfigs[selectedTxNetworkIndex].key, aesNonce, payload)


        headerByte = (XB_TYPE_ENCRYPTED_FLAG + (networkConfigs[selectedTxNetworkIndex].id[0] & XBX_NETWORK_ID_PARTIAL_ID_MASK))


        header = ConvertIntToList(bleLocalDeviceId, 2) + ConvertIntToList(networkConfigs[selectedTxNetworkIndex].txSqn, XBX_SEQUENCE_ID_LENGTH) + [0] * XBX_RFU_LENGTH
        logHandler.printLog("Header: {0}".format(header))
        logHandler.printLog("Header key: {0}".format(networkConfigs[selectedTxNetworkIndex].headerKey))

##        if((IsEncryptedHeaderEnabled(destination)) and (len(networkConfigs[selectedTxNetworkIndex].headerKey) == NETWORK_KEY_LENGTH) and (networkConfigs[selectedTxNetworkIndex].headerKey != [0] * NETWORK_KEY_LENGTH)):
##            headerByte |= XBX_HEADER_ENCRYPTED_FLAG
        payloadAndMic = eMsg + eMic
        headerNonce = [0] * NONCE_LENGTH
        tempLength = min(NONCE_LENGTH, len(payloadAndMic))
        for i in range(tempLength):
            headerNonce[i] = payloadAndMic[i]

        logHandler.printLog("headerKey: {0}, headerNonce: {1}".format(networkConfigs[selectedTxNetworkIndex].headerKey, headerNonce))
        header, unusedMic = AesCcmEncrypt(networkConfigs[selectedTxNetworkIndex].headerKey, headerNonce, header) #[0x31, 0x32, 0x33, 0x34] # Source address)
        logHandler.printLog("TX Encrypted header: {0}".format(header))

        xbAssigned = [AD1_LENGTH, AD1_TYPE, AD1_VALUE, 10 + len(payload), 0x07]
        xbAssigned += header[XBX_SOURCE_ADDR_LENGTH:XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH]
        xbAssigned += header[XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH:XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH + XBX_RFU_LENGTH]
        xbAssigned += eMsg + eMic

        xbAssigned += [0x09, 0x09] # , 0x58, 0x49, 0x35, 0x42, 0x31, 0x32, 0x33, 0x34]
        xbAssigned += [ord('X'), ord('I')]

        print ("headerByte: {0}".format(headerByte))
        xbAssigned += HexToAsciiList(headerByte)
##        xbAssigned += [ord('0'), ord('5')]
        xbAssigned += HexListToAsciiList(header[:XBX_SOURCE_ADDR_LENGTH])

        logHandler.printLog("Encrypted assigned iXB packet: {0}".format(xbAssigned), True)
    else:
        xbAssigned = [AD1_LENGTH, AD1_TYPE, AD1_VALUE, 17, 0x07]
        xbAssigned += ConvertIntToList(networkConfigs[selectedTxNetworkIndex].txSqn, XBX_SEQUENCE_ID_LENGTH)
        xbAssigned.append(XBX_RFU_VALUE)
        xbAssigned += payload
        xbAssigned += [0] * (11 - len(payload))
        xbAssigned += [0x09, 0x09] # , 0x58, 0x49, 0x35, 0x42, 0x31, 0x32, 0x33, 0x34]
        xbAssigned += [ord('X'), ord('I')]
        xbAssigned += HexToAsciiList(XB_TYPE_UNENCRYPTED)
        xbAssigned += GetLocalSourceAsciiAddress() # Source address

        logHandler.printLog("Unencrypted assigned iXB packet: {0}".format(xbAssigned), True)


    TransmitAdvertisement(xbAssigned)

    UpdateNetworkConfigFile()

def IsOobSupported(destination):
    devices = GetDevicesInGroup(destination)

    isSupported = (len(devices) > 0)
    for device in devices:
        if(device.deviceType == DEVICE_TYPE_XIM):
            try:
                swVersionValue = float(device.swVersion)
                if(swVersionValue < 0.081):
                    isSupported = False
            except:
                isSupported = False
        else:
            isSupported = False

##        if(device.encryptedAdv == False):
##            isSupported = False

    print ("IsOobSupported: {0}".format(isSupported))
    return isSupported


def SetOobData(destination):

    start_time = time.time()
    while(pending_write and ((time.time() - start_time) < 0.2)):
        CheckActivity(ser)

    if(len(destination) == 1):
        if(bootloadRunning or adminMode): #  (adminMode and IsEncryptedAdvEnabled(destination))
            oobData = ADMIN_KEY_DEFAULT
        elif((IsEncryptedAdvEnabled(destination)) and (networkConfigs[selectedTxNetworkIndex].key != NETWORK_KEY_NONE) and (IsOobSupported(destination))):
            oobData = networkConfigs[selectedTxNetworkIndex].key
        else:
            oobData = []
    else:
        oobData = []
    logHandler.printLog("Setting OOB Data to {0}".format(oobData), True)
    ble.send_command(ser, ble.ble_cmd_sm_set_oob_data(oobData)) # [2] * 16

def SetAdminMode(value):
    global adminMode
    adminMode = value

def SetXBPacket(destination, payloadType, payload):
    if(len(destination) > 3):
        destination = destination[:3]
    if(len(destination) == 3):
        SetXBUnassignedPacket(destination, payloadType, payload)
##        BroadcastIXBUnassigned(destination, payloadType, payload)
    else:
        SetXBAssignedPacket(destination, payloadType, payload)
##        BroadcastIXBAssigned(destination, payloadType, payload)

def SetXBUnassignedPacket(destination, payloadType, payload):
    xbUnassigned = [AD1_LENGTH, AD1_TYPE, AD1_VALUE, 11 + len(payload) + len(destination), 0xFF, 0x53, 0x02]

    xbUnassigned.append(XB_TYPE_UNASSIGNED_DEST)
    xbUnassigned += ConvertIntToList(bleLocalDeviceId, 2) # Source address
    xbUnassigned.append(destination[0])
    xbUnassigned += [0] * 4
    xbUnassigned.append(payloadType)
    xbUnassigned += destination [1:3]
    xbUnassigned += payload
    logHandler.printLog("xbUnassigned: {0}".format(xbUnassigned))

    TransmitAdvertisement(xbUnassigned)


def SetXBAssignedPacket(destination, payloadType, payload):
    if(len(destination) == 1):
        destinationList = ConvertIntToList(destination[0], 2)

    payload = [payloadType] + destinationList + payload

    networkConfigs[selectedTxNetworkIndex].txSqn += 1
    if(networkConfigs[selectedTxNetworkIndex].txSqn >= XBX_SEQUENCE_ID_MAX_VALUE):
        networkConfigs[selectedTxNetworkIndex].txSqn = 1


    if((IsEncryptedAdvEnabled(destination)) and (adminMode or (networkConfigs[selectedTxNetworkIndex].key != NETWORK_KEY_NONE))):

        if(adminMode):
            applicationKey = adminKey
        else:
            applicationKey = networkConfigs[selectedTxNetworkIndex].key
        aesNonce[NONCE_SOURCE_ADDR_OFFSET: NONCE_SOURCE_ADDR_OFFSET + XBX_SOURCE_ADDR_LENGTH] = ConvertIntToList(bleLocalDeviceId, 2)
        aesNonce[NONCE_SQN_OFFSET: NONCE_SQN_OFFSET + XBX_SEQUENCE_ID_LENGTH] = ConvertIntToList(networkConfigs[selectedTxNetworkIndex].txSqn, XBX_SEQUENCE_ID_LENGTH)
##        aesNonce[NONCE_RFU_OFFSET: NONCE_RFU_OFFSET + XBX_RFU_LENGTH] = [0 * XBX_RFU_LENGTH]

        logHandler.printLog("aesNonce: {0}".format(aesNonce))
        logHandler.printLog("aesKey: {0}".format(applicationKey))

        eMsg, eMic = AesCcmEncrypt(applicationKey, aesNonce, payload)

        headerByte = XB_TYPE_ENCRYPTED_FLAG + (networkConfigs[selectedTxNetworkIndex].id[0] & XBX_NETWORK_ID_PARTIAL_ID_MASK)
##        headerByte |= 0x40
        header = ConvertIntToList(bleLocalDeviceId, 2) + ConvertIntToList(networkConfigs[selectedTxNetworkIndex].txSqn, XBX_SEQUENCE_ID_LENGTH) + [0] * XBX_RFU_LENGTH
        logHandler.printLog("Header: {0}".format(header))
        logHandler.printLog("Header key: {0}".format(networkConfigs[selectedTxNetworkIndex].headerKey))

##        if((IsEncryptedHeaderEnabled(destination)) and (len(networkConfigs[selectedTxNetworkIndex].headerKey) == NETWORK_KEY_LENGTH)) and (networkConfigs[selectedTxNetworkIndex].headerKey != [0] * NETWORK_KEY_LENGTH):
##            headerByte |= XBX_HEADER_ENCRYPTED_FLAG
        payloadAndMic = eMsg + eMic
        headerNonce = [0] * NONCE_LENGTH
        tempLength = min(NONCE_LENGTH, len(payloadAndMic))
        for i in range(tempLength):
            headerNonce[i] = payloadAndMic[i]

        logHandler.printLog("headerKey: {0}, headerNonce: {1}".format(networkConfigs[selectedTxNetworkIndex].headerKey, headerNonce))
        header, unusedMic = AesCcmEncrypt(networkConfigs[selectedTxNetworkIndex].headerKey, headerNonce, header) #[0x31, 0x32, 0x33, 0x34] # Source address)
        logHandler.printLog("TX Encrypted header: {0}".format(header))

##        if((len(headerKey) == NETWORK_KEY_LENGTH) and (headerKey != [0] * NETWORK_KEY_LENGTH)):
##            headerByte |= XBX_HEADER_ENCRYPTED_FLAG
##            aesNonce[NONCE_SOURCE_ADDR_OFFSET: NONCE_SOURCE_ADDR_OFFSET + XBX_SOURCE_ADDR_LENGTH] = [0] * XBX_SOURCE_ADDR_LENGTH
##            sourceAddress, unusedMic = AesCcmEncrypt(headerKey, aesNonce, ConvertIntToList(bleLocalDeviceId, 2)) #[0x31, 0x32, 0x33, 0x34] # Source address)
##            print "Encrypted sourceAddress: {0}".format(sourceAddress)
##        else:
##            sourceAddress = ConvertIntToList(bleLocalDeviceId, 2)

        xbAssigned = [AD1_LENGTH, AD1_TYPE, AD1_VALUE, 15 + len(payload), 0xFF, 0x53, 0x02]
        xbAssigned.append(headerByte)
        xbAssigned += header[:XBX_SOURCE_ADDR_LENGTH]
        xbAssigned += header[XBX_SOURCE_ADDR_LENGTH:XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH]
        xbAssigned += header[XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH:XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH + XBX_RFU_LENGTH]
        xbAssigned += eMsg + eMic
        logHandler.printLog("Encrypted assigned packet: {0}".format(xbAssigned))

    else:
        xbAssigned = [AD1_LENGTH, AD1_TYPE, AD1_VALUE, 11 + len(payload), 0xFF, 0x53, 0x02]
        xbAssigned.append(XB_TYPE_UNENCRYPTED)
        xbAssigned += ConvertIntToList(bleLocalDeviceId, 2) # Source address
        xbAssigned += ConvertIntToList(networkConfigs[selectedTxNetworkIndex].txSqn, XBX_SEQUENCE_ID_LENGTH)
        xbAssigned.append(XBX_RFU_VALUE)
        xbAssigned += payload
        logHandler.printLog("Unencrypted assigned packet: {0}".format(xbAssigned))


##    print "xbAssigned: {0}".format(xbAssigned)

    TransmitAdvertisement(xbAssigned)

    UpdateNetworkConfigFile()

##    print "Encrypted time: {0}".format(time.time() - start_time)


def TransmitAdvertisement(packet):
    start_time = time.time()
    while(pending_write and ((time.time() - start_time) < 0.2)):
        CheckActivity(ser)
##    EndProcedure()
##    CheckActivity(ser, 1)

    SetAdvertisingData(packet)
    CheckActivity(ser, 1)
    scanningEnabled = False
    SetAdvertisingState(True)


# ######################################
# Section: Scanning - Internal Functions
# ######################################

# Starts Scanning
def Discover():
    global bgCentralState
    logHandler.printLog("{0}: Discover".format(time.time()))
    ble.send_command(ser, ble.ble_cmd_gap_discover(1))
    bgCentralState = CENTRAL_STATE_SCANNING
    SetBusyFlag()

# Confirmation that scanning has started
def my_ble_rsp_gap_discover(sender, args):
    global pending_write, bgCentralState
    pending_write = False

    if(args['result'] == 0):
        logHandler.printLog("{0}: discover command complete {1}".format(time.time(), args))
        bgCentralState = CENTRAL_STATE_SCANNING
    else:
        logHandler.printLog("{0}: discover command failed {1}".format(time.time(), args))

# Stops scanning, advertising, or any connection attempts
def EndProcedure():
    global bgCentralState
    bgCentralState = CENTRAL_STATE_STOPPING
    logHandler.printLog("{0}: End connection and scanning procedures".format(time.time()))
    ble.send_command(ser, ble.ble_cmd_gap_end_procedure())
    SetBusyFlag()

# Confirmation the end_procedure was completed
def my_ble_rsp_gap_end_procedure(sender, args):
    global pending_write, bgCentralState
    bgCentralState = CENTRAL_STATE_STANDBY
    pending_write = False
    logHandler.printLog("{0}: end_procedure complete {1}".format(time.time(), args))

    # Any device that was attempting to connect will no longer be connected
    for device in peripheral_list:
        if(device.connectionState == STATE_CONNECTING):
            device.connectionState = STATE_STANDBY

# Advertisement Packet or Scan Response Packet Received
def my_ble_evt_gap_scan_response(sender, args):
    global lastScanResponse

    lastScanResponse = time.time()

    # Initialise variables
    ad_services = []
    this_field = []
    deviceName = ""
    bytes_left = 0
    companyId = None
    logText = ""

    # Check if the device is in the peripheral_list
    device = GetDeviceWithAddress(args['sender'])

##    print ("Scanned {0}".format(args['data']))

    # Parse the packet data
    for b in args['data']:
        # Start of new field
        if bytes_left == 0:
            bytes_left = b
            this_field = []
        else:
            # Buffer the bytes in the field
            this_field.append(b)
            bytes_left = bytes_left - 1

            # Complete field received
            if bytes_left == 0:
                # partial or complete list of 16-bit UUIDs
                if this_field[0] == 0x02 or this_field[0] == 0x03:
                    for i in xrange((len(this_field) - 1) / 2):
                        ad_services.append(this_field[-1 - i*2 : -3 - i*2 : -1])

                # partial or complete list of 32-bit UUIDs
                if this_field[0] == 0x04 or this_field[0] == 0x05:
                    for i in xrange((len(this_field) - 1) / 4):
                        ad_services.append(this_field[-1 - i*4 : -5 - i*4 : -1])

                # partial or complete list of 128-bit UUIDs
                if this_field[0] == 0x06 or this_field[0] == 0x07:
                    for i in xrange((len(this_field) - 1) / 16):
                        ad_services.append(this_field[-1 - i*16 : -17 - i*16 : -1])

                # Device Name
                if this_field[0] == 0x09:
                    for i in xrange(1, len(this_field)):
                        deviceName += chr(this_field[i])

                    if(device):
                        if(device.deviceName != deviceName):
                            logHandler.printLog ("Stored device name {0} for device {1}".format(deviceName, device.address))
                        device.deviceName = deviceName

                # iXBeacon packet
                if(len(ad_services) == 1) and (len(ad_services[0]) == 16) and (len(deviceName) == 8):
                    logText = "{0},{1},{2},{3},".format(time.time(), ConvertListToSeparatedString(list(reversed(args['sender'])),':'), args['rssi'], ConvertListToSeparatedHexString(args['data'], ' '))
                    logText += deviceName + ", "

                    packetType = int(deviceName[2:4],16)
                    srcAddr = [int(deviceName[4:6], 16), int(deviceName[6:8], 16)]
                    iXBUuidField = list(reversed(ad_services[0]))
                    header = srcAddr + iXBUuidField[0:5]
                    payloadAndMic = iXBUuidField[5:16]
                    print ("nameField {0} uuidField {1}".format(deviceName, iXBUuidField))
                    print ("iXB packetType {0}, header {1}, payload {2}".format(packetType, header, payloadAndMic))
                    if(packetType & XB_TYPE_ENCRYPTED_FLAG):

                        if((packetType & XBX_NETWORK_ID_PARTIAL_ID_MASK) == (networkConfigs[selectedRxNetworkIndex].id[0] & XBX_NETWORK_ID_PARTIAL_ID_MASK)):
                            header, decryptedData, isValid = XDecrypt(header, payloadAndMic)
                            if(isValid):
                                deviceId = ConvertListToInt(header[:2])
                                sqn = ConvertListToInt(header[2:6])
                                payloadType = GetPayloadTypeText([packetType], decryptedData[0:], True)
                                payload = decryptedData[1:]
                        else:
                            isValid = False
                    else:
                        deviceId = ConvertListToInt(header[:2])
                        sqn = ConvertListToInt(header[2:6])
                        payloadType = GetPayloadTypeText([packetType], payloadAndMic[0:], True)
                        payload = payloadAndMic[1:-4]
                        isValid = True

                    if(isValid):
                        logText += "{0},".format(deviceId)
    ##                    logText += "iXBeacon,"
                        logText += "{0},".format(payloadType)
                        logText += "{0},".format(ConvertListToSeparatedHexString(payload, ' '))
                    else:
                        logText += "Unknown,Unknown,Unknown,"
                    packetLogger.printLog(logText)



                # Manufacturer-specific data
                if this_field[0] == 0xFF:
                    this_field.pop(0)

                    if(len(this_field) >= 2):
                        companyId = this_field[:2]

                        # Xicato packet
                        if(companyId == ADV_COMPANY_ID_XICATO):
                            logText = "{0},{1},{2},{3}".format(time.time(), ConvertListToSeparatedString(list(reversed(args['sender'])),':'), args['rssi'], ConvertListToSeparatedHexString(args['data'], ' '))
                            logTextPayloadType = ""
                            logTextPayload = None

                            # xBeacon data is in advertisment packets (not scan response)
                            if(args['packet_type'] != ADV_PACKET_TYPE_SCAN_RESPONSE):


                                if(this_field[XBX_NETWORK_ID_OFFSET] & XB_TYPE_ENCRYPTED_FLAG):
##                                    logHandler.printLog("XBX field: {0}, len:{1}".format(this_field, len(this_field)))

                                    if((this_field[XBX_NETWORK_ID_OFFSET] & XBX_NETWORK_ID_PARTIAL_ID_MASK) == (networkConfigs[selectedRxNetworkIndex].id[0] & XBX_NETWORK_ID_PARTIAL_ID_MASK)):

                                        payloadAndMic = this_field[XBX_PAYLOAD_AND_MIC_OFFSET:]
                                        header = this_field[XBX_SOURCE_ADDR_OFFSET: XBX_SOURCE_ADDR_OFFSET + (XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH + XBX_RFU_LENGTH)]
                                        header, decryptedData, isValid = XDecrypt(header, payloadAndMic)

                                        if(isValid):
                                            sourceAddress = header[:XBX_SOURCE_ADDR_LENGTH]
                                            rxSqnTemp = ConvertListToInt(header[XBX_SOURCE_ADDR_LENGTH:(XBX_SOURCE_ADDR_LENGTH + XBX_SEQUENCE_ID_LENGTH)])
                                            logTextPayloadType = GetPayloadTypeText(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2], decryptedData[0:])
                                            logTextPayload = decryptedData[1:]

                                            # Jeff TODO: Store SQNs per device
##                                            rxSqnTemp = this_field[XBX_SEQUENCE_ID_OFFSET] + (this_field[XBX_SEQUENCE_ID_OFFSET + 1] * 256) + ((this_field[XBX_SEQUENCE_ID_OFFSET + 2] & SEQUENCE_ID_MSB_MASK) * 65536)
##                                            print "rxSqnTemp: {0}".format(rxSqnTemp)
                                            if(rxSqnTemp > networkConfigs[selectedRxNetworkIndex].txSqn):
                                                networkConfigs[selectedRxNetworkIndex].txSqn = rxSqnTemp

                                            if(device == None):
                                                if((decryptedData[0] in [ENCRYPTED_PACKET_TYPE_XB1, ENCRYPTED_PACKET_TYPE_XB2, ENCRYPTED_PACKET_TYPE_XGROUP]) or
                                                    (((decryptedData[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD) and (decryptedData[1 + XBOOT_DEVICE_TYPE_OFFSET] & 0x80) == 0))):
                                                    device = XimBleDevice(ble, ser, args['sender'], args['address_type'])
                                                    peripheral_list.append(device)
                                                    logHandler.printLog("Added XIM peripheral_list: {0}".format(peripheral_list))
                                                elif((decryptedData[0] == ENCRYPTED_PACKET_TYPE_SENSORS_ALL) or
                                                    (((decryptedData[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD) and (decryptedData[1 + XBOOT_DEVICE_TYPE_OFFSET] & 0x80)))):
                                                    device = XSensorBleDevice(ble, ser, args['sender'], args['address_type'])
                                                    peripheral_list.append(device)
                                                    logHandler.printLog("Added XSensor to peripheral_list: {0}".format(peripheral_list))

                                            if(device):
                                                device.encryptedAdv = True
                                                device.hasEncryptedHeader = True # isHeaderEncrypted
                                                device.txNetwork = {'id': networkConfigs[selectedRxNetworkIndex].id, 'key': networkConfigs[selectedRxNetworkIndex].key}
                                                device.scannedRssi = args['rssi']
                                                device.lastScanTime = time.time()
                                                device.scannedDeviceId = [ConvertListToInt(sourceAddress)]
                                                ProcessXBPacket(device, decryptedData)

                                else:
                                    if(device == None) and (GetDeviceTypeFromPacket(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2], this_field[XB_UNASSIGNED_PAYLOAD_OFFSET:]) == DEVICE_TYPE_XIM):
                                        device = XimBleDevice(ble, ser, args['sender'], args['address_type'])
                                        peripheral_list.append(device)
                                        logHandler.printLog("Added XIM peripheral_list: {0}".format(peripheral_list))
                                    elif(device == None) and (GetDeviceTypeFromPacket(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2], this_field[XB_UNASSIGNED_PAYLOAD_OFFSET:]) == DEVICE_TYPE_XSENSOR):
                                        device = XSensorBleDevice(ble, ser, args['sender'], args['address_type'])
                                        peripheral_list.append(device)
                                        logHandler.printLog("Added XSensor to peripheral_list: {0}".format(peripheral_list))

                                    # Try legacy packets first. This will get overwritten if a new packet is detected
                                    logTextPayloadType = GetPayloadTypeText(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2], [])


                                    # xBeacon1 packet
##                                    if(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2] == PACKET_TYPE_XB1) and (len(this_field) == XB1_FIELD_LENGTH):
                                    if(this_field[XB_PACKET_TYPE_OFFSET] in [XB_TYPE_UNASSIGNED_SOURCE, XB_TYPE_UNENCRYPTED]):
                                        logTextPayloadType = GetPayloadTypeText(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2], this_field[XB_UNASSIGNED_PAYLOAD_OFFSET:])
                                        if(device):
                                            device.encryptedAdv = False
                                            device.txNetwork = None
                                            device.scannedRssi = args['rssi']
                                            device.lastScanTime = time.time()

                                            if(this_field[XB_PACKET_TYPE_OFFSET] == XB_TYPE_UNASSIGNED_SOURCE):
##                                                print "{0:.3f}: XB_TYPE_UNASSIGNED_SOURCE {1}".format(time.time() % 100.0, this_field)
                                                device.scannedDeviceId = this_field[XB_UNASSIGNED_SOURCE_ADDRESS_OFFSET:XB_UNASSIGNED_SOURCE_ADDRESS_OFFSET + UNASSIGNED_ADDRESS_LENGTH]
                                                payload = this_field[XB_UNASSIGNED_PAYLOAD_OFFSET:]
                                            else:
##                                                print "{0:.3f}: XB_TYPE_UNENCRYPTED {1}".format(time.time() % 100.0, this_field)
                                                device.scannedDeviceId = [ConvertListToInt(this_field[XBX_SOURCE_ADDR_OFFSET:XBX_SOURCE_ADDR_OFFSET + XBX_SOURCE_ADDR_LENGTH])]
                                                payload = this_field[XB_UNASSIGNED_PAYLOAD_OFFSET:]

##                                            print "this_field[XB_UNASSIGNED_PAYLOAD_OFFSET]: {0}, XB_UNASSIGNED_PAYLOAD_OFFSET: {1}".format(this_field[XB_UNASSIGNED_PAYLOAD_OFFSET], XB_UNASSIGNED_PAYLOAD_OFFSET)
                                            ProcessXBPacket(device, payload)
                                            logTextPayload = payload


                                    # xBeacon1 packet
                                    elif(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2] == PACKET_TYPE_XB1)  and (len(this_field) == XB1_FIELD_LENGTH):
                                        if(device):
                                            device.bootloaderMode = False
                                            device.scannedRssi = args['rssi']
                                            device.lastScanTime = time.time()
                                            device.scannedDeviceId = this_field[XB_V0_DEVICE_ID_OFFSET:XB_V0_DEVICE_ID_OFFSET + XB_V0_DEVICE_ID_LENGTH]
                                            ProcessXBeacon1Fields(device, this_field[XB1_V0_PAYLOAD_OFFSET:])
                                            logTextPayload = this_field[XB1_V0_PAYLOAD_OFFSET:]

                                    # xBeacon2 packet
                                    elif(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2] == PACKET_TYPE_XB2)  and (len(this_field) == XB2_FIELD_LENGTH):
                                        if(device):
                                            device.bootloaderMode = False
                                            device.scannedRssi = args['rssi']
                                            device.lastScanTime = time.time()
                                            device.scannedDeviceId = this_field[XB_V0_DEVICE_ID_OFFSET:XB_V0_DEVICE_ID_OFFSET + XB_V0_DEVICE_ID_LENGTH]
                                            ProcessXBeacon2Fields(device, this_field[XB2_V0_PAYLOAD_OFFSET:])
                                            logTextPayload = this_field[XB1_V0_PAYLOAD_OFFSET:]


                                    # Bootloader Mode packet
                                    elif(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2] == PACKET_TYPE_XBL)  and (len(this_field) == XBL_FIELD_LENGTH):
    ##                                        device.xb2UpdateTime = time.time()
                                        logHandler.printLog("{0}: Bootloader Mode Detected for {1}".format(time.time(), args['sender']))
                                        if(device):
                                            device.bootloaderMode = True
                                            device.scannedRssi = args['rssi']
                                            device.lastScanTime = time.time()
        ##                                        print "xBootload Packet: {0}".format(this_field)
                                            device.scannedDeviceId = this_field[XB_V0_DEVICE_ID_OFFSET:XB_V0_DEVICE_ID_OFFSET + XB_V0_DEVICE_ID_LENGTH]
                                            logTextPayload = []

    ##                                        # If in bootloader mode, the regular mode service and attribute list should be cleared
    ##                                        if(GetHandle(device, uuid_scan_response_user_data_characteristic)):
    ##                                            logHandler.printLog("Clearing old UUID handle map for device: {0}".format(device.scannedDeviceId))
    ##                                            device.InitializeServiceAttributeList()

                                    # XSensor packet
                                    elif(this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2] in [PACKET_TYPE_XSENSOR_MOTION, PACKET_TYPE_XSENSOR_LUX]): #  and (len(this_field) == XBL_FIELD_LENGTH):
    ##                                        print "this_field: {0}".format(this_field)
    ##                                        device.xb2UpdateTime = time.time()
##                                        logHandler.printLog("{0}: XSensor Detected {1}".format(time.time(), this_field))
##                                        if(device == None):
##                                            device = XSensorBleDevice(ble, ser, args['sender'], args['address_type'])
##                                            peripheral_list.append(device)
##                                            logHandler.printLog("Added XSensor to peripheral_list: {0}".format(peripheral_list))

                                        if(device):
                                            ProcessXSensorFields(device, this_field[XB_PACKET_TYPE_OFFSET: XB_PACKET_TYPE_OFFSET + 2], this_field[XB1_V0_PAYLOAD_OFFSET:])
                                            device.bootloaderMode = False
                                            device.scannedRssi = args['rssi']
                                            device.lastScanTime = time.time()        ##
                                            device.scannedDeviceId = this_field[XB_V0_DEVICE_ID_OFFSET:XB_V0_DEVICE_ID_OFFSET + XB_V0_DEVICE_ID_LENGTH]
                                            logTextPayload = this_field[XB1_V0_PAYLOAD_OFFSET:]


                                    else:
                                        if(device):
                                            device.bootloaderMode = False
                                        logHandler.printLog("{0}: Other Packet Detected {1}".format(time.time(), this_field))

                            # Can only store the scanned data if the device is in the peripheral_list
                            try:
                                if(logTextPayload == None):
                                    logTextPayload = "Unknown"
                                else:
                                    logTextPayload = ConvertListToSeparatedHexString(logTextPayload, ' ')
                            except:
                                logTextPayload = "Unknown"

                            if(device):
                                logText += ",{0},{1},{2},{3}".format(device.deviceName, ConvertListToSeparatedString(device.scannedDeviceId, '.'), logTextPayloadType, logTextPayload)
                            else:
                                logText += ", , , ,"

                            packetLogger.printLog(logText)
        # To log all packets
##        if(logText == ""):
##            logText = "{0},{1},{2},{3}".format(time.time(), ConvertListToSeparatedString(list(reversed(args['sender'])),':'), args['rssi'], ConvertListToSeparatedString(args['data'], ' '))
##            packetLogger.printLog(logText)

def XDecrypt(header, payloadAndMic):
    payloadLength = len(payloadAndMic) - XBX_MIC_LENGTH
    headerLength = len(header)

    headerNonce = [0] * NONCE_LENGTH
    tempLength = min(NONCE_LENGTH, payloadLength + XBX_MIC_LENGTH)
    for i in range(tempLength):
        headerNonce[i] = payloadAndMic[i]

    logHandler.printLog("RX Encrypted header: {0}.".format(header))
    # This decryption isn't authenticated, so ignore isValid
    header, isValid = AesCcmDecrypt(networkConfigs[selectedRxNetworkIndex].headerKey, headerNonce, header, [0] * XBX_MIC_LENGTH)
    logHandler.printLog("RX Decrypted header: {0}. Using key {1} and nonce {2}".format(header, networkConfigs[selectedRxNetworkIndex].headerKey, headerNonce))

##    isHeaderEncrypted = True

    aesNonce[:(headerLength - XBX_RFU_LENGTH)] = header[:(headerLength - XBX_RFU_LENGTH)]
##   print "aesNonce: {0}".format(aesNonce)
    outMic = payloadAndMic[payloadLength:payloadLength + XBX_MIC_LENGTH]

    decryptedData, isValid = AesCcmDecrypt(networkConfigs[selectedRxNetworkIndex].key, aesNonce, payloadAndMic[:payloadLength], outMic)

    if(isValid == False):
        decryptedData, isValid = AesCcmDecrypt(networkConfigs[selectedTxNetworkIndex].key, aesNonce, payloadAndMic[:payloadLength], outMic)
    logHandler.printLog("DecryptedData Out: {0}".format(decryptedData))


##    logHandler.printLog("isValid: {0}".format(isValid))
##    print "aesNonce: {0}".format(aesNonce)
##    print "networkConfigs[selectedRxNetworkIndex].key: {0}".format(networkConfigs[selectedRxNetworkIndex].key)
##    print "outMic: {0}".format(outMic)
##    print "decryptedData: {0}".format(decryptedData)
##    print "isValid: {0}".format(isValid)
    return header, decryptedData, isValid

def GetPayloadTypeText(packetTypeList, payload, isIXBeacon = False):
    if(packetTypeList == PACKET_TYPE_XB1):
        return "XIM,Status 1 (Legacy)"
    elif(packetTypeList == PACKET_TYPE_XB2):
        return "XIM,Status 2 (Legacy)"
    elif(packetTypeList == PACKET_TYPE_XBL):
        return "XIM,Bootloader (Legacy)"
    elif(packetTypeList == PACKET_TYPE_XSENSOR_MOTION):
        return "XSensor,Motion (Legacy)"
    elif(packetTypeList == PACKET_TYPE_XSENSOR_LUX):
        return "XSensor,Lux (Legacy)"

    if(isIXBeacon):
        controllerName = "iX Controller"
    else:
        controllerName = "X Controller"
    if((len(payload) > 0) and ((packetTypeList[0] in [XB_TYPE_UNASSIGNED_SOURCE, XB_TYPE_UNENCRYPTED]) or (packetTypeList[0] & XB_TYPE_ENCRYPTED_FLAG))):
        if(payload[0] == ENCRYPTED_PACKET_TYPE_XB1):
            return "XIM,Status 1"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_XB2):
            return "XIM,Status 2"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_XDEV_INFO):
            return "XIM,Device Info"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_XGROUP):
            return "X Device,Group Info"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_LIGHT_CONTROL):
            return controllerName + ",Light Control"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_RECALL_SCENE):
            return controllerName + ",Recall Scene"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_INDICATE):
            return controllerName + ",Indicate"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_SET_CONNECTABLE):
            return controllerName + ",Enable Connections"
        elif(payload[0] == ENCRYPTED_PACKET_TYPE_REQUEST_ADV):
            return controllerName + ",Request Data"
        elif((payload[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD) and ((payload[1 + XBOOT_DEVICE_TYPE_OFFSET] & 0x80) == 0)):
            return "XIM,Bootloader"
        elif(payload[0] in [ENCRYPTED_PACKET_TYPE_SENSORS_ALL]) and (len(payload) > 1):
            if(payload[1] == ENCRYPTED_PACKET_TYPE_SENSOR_MOTION):
                return "XSensor,Motion"
            elif(payload[1] == ENCRYPTED_PACKET_TYPE_SENSOR_LUX):
                return "XSensor,Lux"
        elif((payload[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD) and ((payload[1 + XBOOT_DEVICE_TYPE_OFFSET] & 0x80))):
            return "XSensor,Bootloader"
    return "Unknown"


def GetDeviceTypeFromPacket(packetTypeList, payload):
##    print "packetTypeList {0}, payload {1}".format(packetTypeList, payload)
    if(packetTypeList in  [PACKET_TYPE_XB1, PACKET_TYPE_XB2, PACKET_TYPE_XBL]):
        return DEVICE_TYPE_XIM
    elif(packetTypeList in [PACKET_TYPE_XSENSOR_MOTION, PACKET_TYPE_XSENSOR_LUX]):
        return DEVICE_TYPE_XSENSOR
    if(packetTypeList[0] in [XB_TYPE_UNASSIGNED_SOURCE, XB_TYPE_UNENCRYPTED]) or (packetTypeList[0] & XB_TYPE_ENCRYPTED_FLAG):
        if((payload[0] in [ENCRYPTED_PACKET_TYPE_XB1, ENCRYPTED_PACKET_TYPE_XB2]) or
            ((payload[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD) and ((payload[1 + XBOOT_DEVICE_TYPE_OFFSET] & 0x80) == 0))):
            return DEVICE_TYPE_XIM
        elif((payload[0] in [ENCRYPTED_PACKET_TYPE_SENSORS_ALL])  or
            ((payload[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD) and ((payload[1 + XBOOT_DEVICE_TYPE_OFFSET] & 0x80)))):
             return DEVICE_TYPE_XSENSOR
    return None

#    logHandler.printLog ("{1}: Ad Services from address {2}: {0}".format(ad_services, time.time(), args['sender']))

def ProcessXBPacket(device, payload):
    if(payload[0] == ENCRYPTED_PACKET_TYPE_XB1):
        ProcessXBeacon1Fields(device, payload[1:])
    elif(payload[0] == ENCRYPTED_PACKET_TYPE_XB2):
        ProcessXBeacon2Fields(device, payload[1:])
    elif(payload[0] == ENCRYPTED_PACKET_TYPE_XDEV_INFO):
        ProcessXDevInfoFields(device, payload[1:])
    elif(payload[0] == ENCRYPTED_PACKET_TYPE_XGROUP):
        ProcessXBeaconGroupFields(device, payload[1:])
    elif(payload[0] == ENCRYPTED_PACKET_TYPE_BOOTLOAD):
        ProcessXBBootloadFields(device, payload[1:])
    elif(payload[0] == ENCRYPTED_PACKET_TYPE_SENSORS_ALL):
        ProcessXSensorFields(device, list(reversed(payload[:2])), payload[2:])


def ProcessXBeacon1Fields(device, this_field):
##    print "ProcessXBeacon1Fields: {0}".format(this_field)
    device.bootloaderMode = False
    device.xb1UpdateTime = time.time()
    device.scannedStatus = this_field[XB1_STATUS_OFFSET]
    device.scannedIntensity = (this_field[XB1_INTENSITY_OFFSET] + this_field[XB1_INTENSITY_OFFSET + 1] * 256) / 100.0
    device.scannedLedTemperature = this_field[XB1_LED_TEMPERATURE_OFFSET]
    device.scannedPcbTemperature = this_field[XB1_PCB_TEMPERATURE_OFFSET]
    device.scannedPower = float(this_field[XB1_POWER_OFFSET] + this_field[XB1_POWER_OFFSET + 1] * 256) * 0.1
    device.scannedVin = this_field[XB1_VIN_OFFSET] * 0.25 + float((this_field[XB1_EXTENDED_VIN_OFFSET] & 0xF0) >> 4) * 0.025
    device.scannedVinRipple = (this_field[XB1_VIN_RIPPLE_OFFSET] * 0.05 + float((this_field[XB1_EXTENDED_VIN_OFFSET] & 0x0F) * 0.005)) * 1000.0
    device.scannedLockoutTimeRemaining = this_field[XB1_LOCKOUT_TIME_OFFSET] * 10

def ProcessXBeacon2Fields(device, this_field):
    logHandler.printLog("ProcessXBeacon2Fields: {0}".format(this_field))
    device.bootloaderMode = False
    device.xb2UpdateTime = time.time()
    device.scannedProductId = this_field[XB2_PRODUCT_ID_OFFSET: XB2_PRODUCT_ID_OFFSET + XB2_PRODUCT_ID_LENGTH]
    device.scannedHours = this_field[XB2_HOURS_OFFSET] + this_field[XB2_HOURS_OFFSET + 1] * 256
    device.scannedPowerCycles = this_field[XB2_POWER_CYCLES_OFFSET] + this_field[XB2_POWER_CYCLES_OFFSET + 1] * 256
    device.scannedLedCycles = this_field[XB2_LED_CYCLES_OFFSET] + this_field[XB2_LED_CYCLES_OFFSET + 1] * 256
    device.daliStatus = this_field[XB2_DALI_STATUS_OFFSET]

def ProcessXDevInfoFields(device, this_field):
    logHandler.printLog("ProcessXDevInfoFields: {0}".format(this_field))
    device.bootloaderMode = False
    device.deviceInfoUpdateTime = time.time()
##    print "{0:.3f}: XDevInfo: {1}".format(time.time() % 100.0, this_field)
    device.scannedProductId = this_field[XDEV_INFO_PRODUCT_ID_OFFSET: XDEV_INFO_PRODUCT_ID_OFFSET + XB2_PRODUCT_ID_LENGTH]
    device.hwVersion = "{0}.{1}".format(this_field[XDEV_INFO_HW_VERSION_OFFSET] >> 4, this_field[XDEV_INFO_HW_VERSION_OFFSET] & 0x0F)
##    device.swVersion = GetVersionString(this_field[XDEV_INFO_BLE_VERSION_OFFSET], this_field[XDEV_INFO_BLE_VERSION_OFFSET + 1])

    if(device.deviceType == DEVICE_TYPE_XSENSOR):
        device.fwVersion = GetVersionString(this_field[XDEV_INFO_HW_VERSION_OFFSET] >> 4, this_field[XDEV_INFO_LED_CONTROLLER_VERSION_OFFSET])
    else:
        device.ledControllerVersion = GetVersionString(this_field[XDEV_INFO_HW_VERSION_OFFSET] >> 4, this_field[XDEV_INFO_LED_CONTROLLER_VERSION_OFFSET])
    device.programmedFlux = ConvertListToInt(this_field[XDEV_INFO_PROGRAMMED_FLUX_OFFSET: XDEV_INFO_PROGRAMMED_FLUX_OFFSET + XDEV_INFO_PROGRAMMED_FLUX_LENGTH])
    device.overloadTemperature = this_field[XDEV_INFO_OVERTEMP_THRESHOLD_VERSION_OFFSET]

    ProcessSwVersion(device, GetVersionString(this_field[XDEV_INFO_BLE_VERSION_OFFSET], this_field[XDEV_INFO_BLE_VERSION_OFFSET + 1]))

def ProcessXBBootloadFields(device, this_field):
    logHandler.printLog("ProcessXBBootloadFields: {0}".format(this_field))
    device.bootloaderMode = True
    device.bootloaderModeUpdateTime = time.time()

    if(len(this_field) >= XBOOT_DEVICE_TYPE_OFFSET + 1):

        if(device.hwVersion and (len(device.hwVersion) > 2)):
            hwVersionMajor = device.hwVersion.split('.')[0]
        else:
            hwVersionMajor = "2"

        deviceType = this_field[XBOOT_DEVICE_TYPE_OFFSET] & 0x0F

        device.fwVersion = GetVersionString(this_field[XBOOT_FW_VERSION_OFFSET], this_field[XBOOT_FW_VERSION_OFFSET + 1])
        device.hwVersion = "{0}.{1}".format(hwVersionMajor, deviceType)
        ProcessSwVersion(device, GetVersionString(this_field[XBOOT_BLE_VERSION_OFFSET], this_field[XBOOT_BLE_VERSION_OFFSET + 1]))
        logHandler.printLog("Bootload fields HW {0} and BLE FW {1}".format(device.hwVersion, device.swVersion))





def GetVersionString(major, minor):
    if(minor < 10):
        return "{0}.00{1}".format(major, minor)
    elif(minor < 100):
        return "{0}.0{1}".format(major, minor)
    else:
        return "{0}.{1}".format(major, minor)

def ProcessXBeaconGroupFields(device, this_field):
    device.bootloaderMode = False
    logHandler.printLog("{0:.3f}: Device {1}, XBeaconGroup: {2}".format(time.time() % 100.0, device.scannedDeviceId, this_field), True)
    groupOffset = this_field[XBGROUP_HEADER_OFFSET] & ~XGROUP_LAST_PACKET_FLAG
##    print "groupOffset: {0}".format(groupOffset)
    numAdvGroups = (len(this_field) - XBGROUP_HEADER_LENGTH) / GROUP_MEMBER_LENGTH
##    print "numAdvGroups: {0}".format(numAdvGroups)

    device.requestGroupAttempts = 0

    for i in range(numAdvGroups):
        if(groupOffset + i < len(device.groups)):
            device.groups[groupOffset + i]  = ConvertListToInt(this_field[XBGROUP_MEMBERS_OFFSET + (i * GROUP_MEMBER_LENGTH): XBGROUP_MEMBERS_OFFSET + (i * GROUP_MEMBER_LENGTH) + GROUP_MEMBER_LENGTH])

    if(this_field[XBGROUP_HEADER_OFFSET] & XGROUP_LAST_PACKET_FLAG):
        device.groups[groupOffset + numAdvGroups:] = [GROUP_MEMBER_UNASSIGNED] * (NUM_GROUPS - (groupOffset + numAdvGroups))
        device.receivedAllGroups = not(None in device.groups[:groupOffset + numAdvGroups])
##        print "device.receivedAllGroups: {0}".format(device.receivedAllGroups)

##    print "device.groups: {0}".format(device.groups)

def ProcessXSensorFields(device, packetType, this_field):
    device.bootloaderMode = False
##    logHandler.printLog("{0:.3f}: Device {1}, XSensor: {2}".format(time.time() % 100.0, device.scannedDeviceId, this_field), True)

    temp = this_field[XSENSOR_TEMPERATURE_OFFSET]
    if(temp >= 0x80):
        temp = temp - 256
    device.scannedTemperature = temp

    vin = this_field[XSENSOR_VIN_OFFSET] * 250 + ((this_field[XSENSOR_STATUS_VINLOWER_OFFSET] & 0x0F) * 25)
    device.scannedVin = vin
    device.scannedStatus = this_field[XSENSOR_STATUS_VINLOWER_OFFSET] & 0xF0


##    print "packetType: {0}".format(packetType)
    if(packetType == PACKET_TYPE_XSENSOR_MOTION):
##        logHandler.printLog("{0:.3f}: Device {1}, XSensor: {2}".format(time.time() % 100.0, device.scannedDeviceId, this_field), True)
        device.motionUpdateTime = time.time()
        if(this_field[XSENSOR_VALUE_OFFSET] >= 254):
            motion = "None"
##            print "{0:.1f} motion: None".format(time.time() % 100)
            device.scannedMotion = None
        else:
            motion = "{0} ms".format(this_field[XSENSOR_VALUE_OFFSET] * 50)
            device.scannedMotion = this_field[XSENSOR_VALUE_OFFSET] * 50
##            print "{1:.1f} motion: {0}".format(device.scannedMotion, time.time() % 100)
##                                            print "{4:.3f}: xSensor Motion. ID: {0}, Time since Motion: {1}, Temp: {2} C, Vin: {3} mV".format('.'.join(map(str,this_field[4:8])), motion, temp, vin, time.time() % 100)
    elif(packetType == PACKET_TYPE_XSENSOR_LUX):

        device.luxUpdateTime = time.time()

        lux = this_field[XSENSOR_VALUE_OFFSET] + this_field[XSENSOR_VALUE_OFFSET + 1] * 256
##        print "{1:.1f} lux: {0}".format(lux, time.time() % 100)
        device.scannedLux = lux
##                                            print "{4:.3f}: xSensor Lux. ID: {0}, Lux: {1}, Temp: {2} C, Vin: {3} mV".format('.'.join(map(str,this_field[4:8])), lux, temp, vin, time.time() % 100)

# Converts the provided list to a string separated by the provided separator character
def ConvertListToSeparatedString(inList, separator):
    outString = ""
    if(inList):
        for value in inList:
            outString += "{0}{1}".format(value, separator)
        outString = outString[:-1]
    return outString

def ConvertListToSeparatedHexString(inList, separator):
    outString = ""
    if(inList):
        for value in inList:
            try:
                hexString = hex(value)[2:].upper()
                if(len(hexString) == 1):
                    hexString = "0" + hexString
            except:
                hexString = "  "
            outString += "{0}{1}".format(hexString, separator)

        outString = outString[:-1]
    return outString

# ######################################
# Section: Connection - Internal Functions
# ######################################

# Request the status of each connection
def TestConnection():
    global testConnectionHandle
    ble.send_command(ser, ble.ble_cmd_system_get_connections())
    SetBusyFlag()

# Confirmation that Connection Get Status command was received
def my_ble_rsp_connection_get_status(sender, args):
    global pending_write
    pending_write = False
    logHandler.printLog("{0}: connection get status command complete {1}".format(time.time(), args))

# Confirmation that Get Alls Connections command was received
def my_ble_rsp_system_get_connections(sender, args):
    global pending_write
    pending_write = False
    logHandler.printLog("{0}: get connections command complete {1}".format(time.time(), args))

# Confirmation that Disconnect command was received
def my_ble_rsp_connection_disconnect(sender, args):
    global pending_write
    logHandler.printLog("{0}: Disconnected response {1}".format(time.time(), args))
    pending_write = False

# Confirmation that Connect command was received
def my_ble_rsp_gap_connect_direct(sender, args):
    global pending_write
    global blueGigaDeviceErrorCount

    device = FindConnectingDevice()

    if(args['result'] == 0):
        logHandler.printLog("{0}: Connected command complete {1}, sender {2}".format(time.time(), args, sender))
        if(device):
            device.connectionSent = True
        pending_write = False
    else:
        logHandler.printLog("{0}: Connected command error {1}, sender {2}".format(time.time(), args, sender), True)
        if(device):
            device.connectionState = STATE_STANDBY
            device.connectionSent = False
        ble.send_command(ser, ble.ble_cmd_gap_end_procedure())
        SetBusyFlag()


# Event that is triggered when a new connection occurs or a connection status update is requested
def my_ble_evt_connection_status(sender, args):
    global bgCentralState

##    logHandler.printLog("{0}: State: {1}, Connection Status: {2}, ".format(time.time(), state, args))

    # Connected when flag is non-zero
    if (args['flags'] != 0x00):

        device = GetDeviceWithAddress(args['address'])

        if(device):
            logHandler.printLog("{0}: Connection Status: {1}, Connection State: {2}".format(time.time(), args, device.connectionState))
        else:
            logHandler.printLog("{0}: Connection Status: {1}".format(time.time(), args))

        # New connection stops discovery process
        if(args['flags'] & 0x04):
            bgCentralState = CENTRAL_STATE_STANDBY


        if ((args['flags'] & 0x05) in [0x01, 0x05]):
            # connected, now perform service discovery
##            logHandler.printLog("Connected to handle {0} address {1}".format(args['connection'], ':'.join(['%02X' % b for b in args['address'][::-1]])))

            if(device):
                device.failedConnectionAttempts = 0

                if(device.connectionState == STATE_STANDBY):
                    device.connection_handle = args['connection']
                    logHandler.printLog("{0}: Unexpected connection for address {1}. Disconnecting. ".format(time.time(), device.address))
                    Disconnect(device.address)

                elif(device.connection_handle != args['connection'] or device.connectionState in [STATE_CONNECTING, STATE_ENCRYPTING]):
                    device.connection_handle = args['connection']

                    if(device.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]):
                        if(args['bonding'] != 255):
                            logHandler.printLog("{0}: Connected to bonded device. Index: {1}".format(time.time(), args['bonding']), True)

                        # 0x02 means encryted connection
                        if((args['flags'] & 0x02) or (device.encryptionRequired == False and device.bootloaderMode == False)):
                            if(args['flags'] & 0x02):
                                logHandler.printLog("{0}: Encryption complete. flags: {1}".format(time.time(), args['flags']), True)



                            if(device.bootloaderMode):
                                ProcessBootloadConnection(device, args['connection'])
                            else:
                                ProcessNormalConnection(device, args['connection'])

                        elif(device.connectionState in [STATE_CONNECTING]):
                            # Jeff Test - Added 200ms wait for connection parameter negotiation
                            startTime = time.time()
                            while((time.time() - startTime) < 0.2):
                                CheckActivity(ser)

                            if(device.connection_handle != None):
                                logHandler.printLog("{0}: Start encryption. pending_write = {1}".format(time.time(), pending_write))
                                ble.send_command(ser, ble.ble_cmd_sm_encrypt_start(device.connection_handle, BONDING_VALUE))
                                SetBusyFlag()

                # Connection parameter update
                elif (args['flags'] == 0x09):
                    logHandler.printLog("{0}: Connection Parameter Update {1}".format(time.time()))

            else:
                logHandler.printLog("Address {0} not in peripheral_list. Disconnecting".format(args['address']), True)
                ble.send_command(ser, ble.ble_cmd_connection_disconnect(args['connection']))
                SetBusyFlag()

        # Disconnect if we weren't expecting it
        else:
            if(device):
                logHandler.printLog("Unexpected connection. Will disconnect")

                device.connectionState = STATE_DISCONNECTING
                device.disconnectTime = time.time()
                ble.send_command(ser, ble.ble_cmd_connection_disconnect(args['connection']))
                SetBusyFlag()


def ProcessNormalConnection(device, connHandle):
    tempHandle = GetHandle(device, uuid_scan_response_user_data_characteristic)
    if(tempHandle == None):
        logHandler.printLog("{0}: Get SW Version. pending_write = {1}".format(time.time(), pending_write))
        device.connectionState = STATE_GET_VERSION
        ble.send_command(ser, ble.ble_cmd_attclient_read_by_type(connHandle, 0x0001, 0xFFFF, list(reversed(uuid_dis_software_rev_characteristic))))
        SetBusyFlag()

    else:
        device.connectionState = STATE_LISTENING_DATA

def ProcessBootloadConnection(device, connHandle):
    tempHandle = GetHandle(device, uuid_bls_command_characteristic)
    if(tempHandle == None):
        logHandler.printLog("{0}: Find Bootloader Services. pending_write = {1}".format(time.time(), pending_write), True)
        device.connectionState = STATE_FINDING_SERVICES
        ble.send_command(ser, ble.ble_cmd_attclient_read_by_group_type(connHandle, 0x0001, 0xFFFF, list(reversed(uuid_service))))
        SetBusyFlag()
    else:
        ProcessDiscoveredBootloaderXim(device)

# Event that is triggered when a disconnection occurs or a connection status update is requested
def my_ble_evt_connection_disconnected(sender, args):
    global pending_write

    logHandler.printLog("{0}: Disconnected event {1}".format(time.time(), args))

    pending_write = False
    reconnecting = False

    # Unexpected disconnection
    if(args['reason'] == 574):
        logHandler.printLog("{0}: Error 574".format(time.time()))

    device = GetDeviceWithConnectionHandle(args['connection'])

##    logHandler.printLog("{0}: Device {1}".format(time.time(), device.connection_handle))
    if(device):
        device.connection_handle = None

        # Unexpected disconnection
        if(not(device.connectionState in [STATE_DISCONNECTING, STATE_STANDBY])):

            device.unexpectedDisconnections += 1
            device.connectionState = STATE_STANDBY

            logHandler.printLog("\n ********************\nUnexpected disconnection {0}".format(device.unexpectedDisconnections), True)

            TestConnection()

            # If it didn't connect after TestConnection, then try to connect now
            if(device.connection_handle == None):

                if(device.unexpectedDisconnections <= MAX_UNEXPECTED_DISCONNECTIONS):
                    logHandler.printLog("{0}: Re-connecting to {1}".format(time.time(), device.address))
                    EnableConnections((device.scannedDeviceId))
                    Connect(device.address)
                    reconnecting = True

        else:
            device.unexpectedDisconnections = 0


    # If not trying to re-connect, then go back to standby
    if(reconnecting == False):
        if(device):
            device.connectionState = STATE_STANDBY
            device.connection_handle = None
            logHandler.printLog("{0}: Disconnected State {1}".format(time.time(), device.connectionState))

def my_ble_rsp_sm_set_bondable_mode(sender, args):
    global pending_write
    logHandler.printLog("{0}: Set Bondable response {1}".format(time.time(), args))
    pending_write = False

def my_ble_rsp_sm_encrypt_start(sender, args):
    global pending_write
    device = GetDeviceWithConnectionHandle(args['handle'])
    logHandler.printLog("{0}: Encrypt Start response {1}".format(time.time(), args))

    if(device and args['result'] == 0):
        device.connectionState = STATE_ENCRYPTING
    pending_write = False


def my_ble_evt_sm_bonding_fail(sender, args):
    logHandler.printLog("{0}: Encryption/Bonding Failed {1}".format(time.time(), args), True)

    device = GetDeviceWithConnectionHandle(args['handle'])
    if(device):

        if(args['result'] == 0x0305):
            logHandler.printLog("{0}: Pairing not supported".format(time.time()))
            device.encryptionRequired = False
        if(device.connectionState in [STATE_ENCRYPTING]):
            device.connectionState = STATE_CONNECTING
            ProcessNormalConnection(device, args['handle'])

def my_ble_rsp_sm_get_bonds(sender, args):
    logHandler.printLog("{0}: Get Bonds Response {1}".format(time.time(), args), True)


def my_ble_evt_sm_bond_status(sender, args):
    logHandler.printLog("{0}: Bond Status {1}".format(time.time(), args), True)

def my_ble_rsp_sm_set_oob_data(sender, args):
    logHandler.printLog("{0}: Set OOB Data Response {1}".format(time.time(), args), True)

# Handles a failed connection.
def ProcessFailedConnection(device):
    if(device):
        device.connectionState = STATE_STANDBY
        device.connectionSent = False
        EndProcedure()

        device.failedConnectionAttempts += 1
        if(device.failedConnectionAttempts >= MAX_FAILED_CONNECTION_ATTEMPTS):
            device.failedConnectionAttempts = 0
            logHandler.printLog("{0}: failedConnectionAttempts for device {1}".format(time.time(), device.address))



# Initalizes the connection parameters and stores to the file bleConnectParamsFileName
def InitializeConnectionParameters():
    global DISCONNECT_TIMEOUT, bleMinInterval, bleMaxInterval, bleConnTimeout, bleSlaveLatency, bgRxGain, bleAdvertisingIntervalMin, bleAdvertisingIntervalMax, bleAdvertisingWindow, bleLocalDeviceId

    bleMinInterval = MIN_INTERVAL
    bleMaxInterval = MAX_INTERVAL
    bleConnTimeout = CONN_TIMEOUT
    bleSlaveLatency = SLAVE_LATENCY
    bgRxGain = RX_GAIN
    bleAdvertisingIntervalMin = ADVERTISING_INTERVAL_MIN
    bleAdvertisingIntervalMax = ADVERTISING_INTERVAL_MAX
    bleAdvertisingWindow = ADVERTISING_WINDOW
    bleLocalDeviceId = randint(LOCAL_DEVICE_ID_DEFAULT_MIN, LOCAL_DEVICE_ID_DEFAULT_MAX)

    fileNeedsUpdate = False

    if(os.path.isfile(bleConnectParamsFileName) == False):
        with open(bleConnectParamsFileName, 'w') as f:
            SetConnectionParameters(MIN_INTERVAL, MAX_INTERVAL, CONN_TIMEOUT, SLAVE_LATENCY, RX_GAIN, ADVERTISING_INTERVAL_MIN, ADVERTISING_INTERVAL_MAX, ADVERTISING_WINDOW)
    else:
        try:
            with open(bleConnectParamsFileName, 'r') as f:
                textLines = f.readlines()
                textLineList = textLines[0].split(':')
                bleMinInterval = GetIntervalValue(textLineList[1])
                textLineList = textLines[1].split(':')
                bleMaxInterval = GetIntervalValue(textLineList[1])
                textLineList = textLines[2].split(':')
                bleConnTimeout = GetTimeoutValue(textLineList[1])
                textLineList = textLines[3].split(':')
                bleSlaveLatency = int(textLineList[1])

                if(len(textLines) > 4):
                    textLineList = textLines[4].split(':')
                    bgRxGain = int(textLineList[1])
                    if(bgRxGain > 1):
                        bgRxGain = 1

                if(len(textLines) > 5):
                    textLineList = textLines[5].split(':')
                    bleAdvertisingIntervalMin = int(textLineList[1])

                if(len(textLines) > 6):
                    textLineList = textLines[6].split(':')
                    bleAdvertisingIntervalMax = int(textLineList[1])

                if(len(textLines) > 7):
                    textLineList = textLines[7].split(':')
                    bleAdvertisingWindow = float(textLineList[1])

                if(len(textLines) > 8):
                    textLineList = textLines[8].split(':')
##                    try:
                    addressArray = textLineList[1].split('.')

                    if(len(addressArray) >= 2):
                        if(addressArray[1][-1] == "\n"):
                            addressArray[1] = addressArray[1][:-1]
                        bleLocalDeviceId = int(addressArray[0]) + int(addressArray[1]) * 256
                    else:
                        if(addressArray[0][-1] == "\n"):
                            addressArray[0] = addressArray[0][:-1]
                        bleLocalDeviceId = int(addressArray[0])
##                    except:
##                        bleLocalDeviceId = LOCAL_DEVICE_ID_DEFAULT



                else:
                    fileNeedsUpdate = True

                logHandler.printLog("Min Interval: {0}, Max Interval: {1}, Connection Timeout: {2}, Slave Latency: {3}, Rx Gain: {4}".format(GetIntervalMs(bleMinInterval), GetIntervalMs(bleMaxInterval), GetTimeoutMs(bleConnTimeout), bleSlaveLatency, bgRxGain), True)
        except:
            fileNeedsUpdate = True


    if(fileNeedsUpdate):
        logHandler.printLog("Error while reading data from {0}. Restoring values.".format(bleConnectParamsFileName), True)
        SetConnectionParameters(bleMinInterval, bleMaxInterval, bleConnTimeout, bleSlaveLatency, bgRxGain, bleAdvertisingIntervalMin, bleAdvertisingIntervalMax, bleAdvertisingWindow, bleLocalDeviceId)

    DISCONNECT_TIMEOUT = bleConnTimeout * 10.0 / 1000.0 + 0.010


# Sets the connection parameters using the real world values (milliseconds for times)
def SetConnectionParametersRealValues(minIntervalMs, maxIntervalMs, connTimeoutMs, slaveLatency):
    SetConnectionParameters(GetIntervalValue(minIntervalMs), GetIntervalValue(maxIntervalMs), GetTimeoutValue(connTimeoutMs), slaveLatency)

# Sets the connection parameters using the BlueGiga format)
def SetConnectionParameters(minInterval, maxInterval, connTimeout, slaveLatency, rxGain = None, advertisingIntervalMin = None, advertisingIntervalMax = None, advertisingWindow = None, localDeviceId = None):
    global DISCONNECT_TIMEOUT, bleMinInterval, bleMaxInterval, bleConnTimeout, bleSlaveLatency, bgRxGain, bleAdvertisingIntervalMin, bleAdvertisingIntervalMax, bleAdvertisingWindow, bleLocalDeviceId

    bleMinInterval = minInterval
    bleMaxInterval = maxInterval
    bleConnTimeout = connTimeout
    bleSlaveLatency = slaveLatency


    if(rxGain != None):
        bgRxGain = rxGain

    if(advertisingIntervalMin != None):
        bleAdvertisingIntervalMin = advertisingIntervalMin
        bleAdvertisingIntervalMax = advertisingIntervalMax
        bleAdvertisingWindow = advertisingWindow

    if(localDeviceId != None):
        bleLocalDeviceId = localDeviceId

    with open(bleConnectParamsFileName, 'w') as f:
        f.write("min_interval:{0}\n".format(GetIntervalMs(minInterval)))
        f.write("max_interval:{0}\n".format(GetIntervalMs(maxInterval)))
        f.write("timeout:{0}\n".format(GetTimeoutMs(connTimeout)))
        f.write("latency:{0}\n".format(slaveLatency))
        f.write("rx_gain:{0}\n".format(bgRxGain))

        f.write("adv_interval_min:{0}\n".format(bleAdvertisingIntervalMin))
        f.write("adv_interval_max:{0}\n".format(bleAdvertisingIntervalMax))
        f.write("adv_window:{0}\n".format(bleAdvertisingWindow))
        f.write("local_address:{0}\n".format(bleLocalDeviceId))


# Returns the connection parameters using the real world values (milliseconds for times)
def GetConnectionParametersRealValues():
    return GetIntervalMs(bleMinInterval), GetIntervalMs(bleMaxInterval), GetTimeoutMs(bleConnTimeout), bleSlaveLatency

# Converts BlueGiga scaled value to milliseconds
def GetIntervalMs(value):
    return float(value) * 1.25

# Converts milliseconds to the BlueGiga scaled value
def GetIntervalValue(time):
    value = int(round(float(time) / 1.25))
    if(value < MIN_INTERVAL_LOWER_LIMIT):
        logHandler.printLog("Interval must be at least 7.5ms", True)
        value == MIN_INTERVAL_LOWER_LIMIT
    return value

# Converts BlueGiga scaled timeout value to milliseconds
def GetTimeoutMs(value):
    return float(value) * 10.0

# Converts milliseconds to the BlueGiga scaled timeout value
def GetTimeoutValue(time):
    return int(round(float(time) / 10.0))

# ######################################
# Section: Attributes - Internal Functions
# ######################################


def IsCombinedNotification(device):
##    print "device.swVersion: {0}".format(device.swVersion)
    try:
        swVersionValue = float(device.swVersion)
        isCombined = (swVersionValue >= 0.076)
    except:
        isCombined = True
##    print "allIisCombinednOne: {0}".format(isCombined)
    return isCombined

# Sends the 2-byte DALI command and waits for the response or the timeout to expire - To be deprecated
def SendDaliCommand(address, byte1, byte2, bleLoopbackMode = False, timeout = -1):
    if(bleLoopbackMode):
        txPacket = [0xFC, 0xFF]
    else:
        txPacket = [byte1, byte2]

    response = None

    device = GetDeviceWithAddress(address)
    if(device):

        if(IsCombinedNotification(device)):
            SetDeviceAttributeValue(device, uuid_dali_command_characteristic, None, True)
        else:
            SetDeviceAttributeValue(device, uuid_dali_response_characteristic, None)
        TransmitPacket(device.address, txPacket, uuid_dali_command_characteristic)

        if(timeout > 0):
            start_time = time.time()
            while((time.time() - start_time) < timeout):
                Process()

                if(IsCombinedNotification(device)):
                    response = GetDeviceAttributeValue(device, uuid_dali_command_characteristic, True)
                else:
                    response = GetDeviceAttributeValue(device, uuid_dali_response_characteristic)
                if(response != None):
                    break

    else:
        logHandler.printLog("{0}: No device to send DALI packet to".format(time.time()))

    return response


# Retrieves 'length' bytes of memory bank data from bank 'bank' starting at offset 'offset' - To be deprecated
def GetBankData(address, bank, offset, length, timeout):
    receivedBytes = 0

    device = GetDeviceWithAddress(address)

    bankDataList = []

    if(device):

##        print "device.swVersion: {0}".format(device.swVersion)
        try:
            swVersionValue = float(device.swVersion)
            allInOne = (swVersionValue >= 0.076)
        except:
            allInOne = True
##        print "allInOne: {0}".format(allInOne)

        EnableBankDataResponse(address)

        while(receivedBytes < length):
            if(receivedBytes + MAX_BANK_DATA_PAYLOAD_SIZE < length):
                numBytes = MAX_BANK_DATA_PAYLOAD_SIZE
            else:
                numBytes = length - receivedBytes

            txPacket = [bank, offset + receivedBytes, numBytes]
            receivedBytes += numBytes

            logHandler.printLog ("{0} Get Bank Data packet {1} sent to BLE address {2}".format(time.time(), txPacket, device.address))

            if(allInOne):
                SetDeviceAttributeValue(device, uuid_xim_memory_location_characteristic, None, True)
            else:
                SetDeviceAttributeValue(device, uuid_xim_memory_value_characteristic, None, True)
            TransmitPacket(device.address, txPacket, uuid_xim_memory_location_characteristic)

            start_time = time.time()

            values = None
            if(timeout):
                while(values == None and (time.time() - start_time < timeout)):
                    if(allInOne):
                        values = GetDeviceAttributeValue(device, uuid_xim_memory_location_characteristic, True)
                    else:
                        values = GetDeviceAttributeValue(device, uuid_xim_memory_value_characteristic, True)
                    Process()

                if(values and len(values) == numBytes):
                    bankDataList += values
    else:
        logHandler.printLog("{0}: No device to get bank data from".format(time.time()))

    logHandler.printLog ("bankDataList: {0}, length: {1}".format(bankDataList, length))
    if(len(bankDataList) != length):
        bankDataList = None

    return bankDataList

# Returns the DALI response - To be deprecated
def GetDaliResponse(address):
    device = GetDeviceWithAddress(address)
    if(device):
        if(IsCombinedNotification(device)):
            return GetDeviceAttributeValue(device, uuid_dali_command_characteristic, True)
        else:
            return GetDeviceAttributeValue(device, uuid_dali_response_characteristic)
    else:
        return None

# Retrieves 'length' bytes of memory bank data from bank 'bank' starting at offset 'offset' - To be deprecated
def WriteBankData(address, bank, offset, length, values):

    txSuccess = False
    if(len(values) == length):
        receivedBytes = 0

        device = GetDeviceWithAddress(address)

        txOffset = 0
        while(txOffset < length):
            if((length - txOffset) > 16):
                txLength = 16
            else:
                txLength = (length - txOffset)
            txValues = values[txOffset:txOffset + txLength]

            txPacket = [bank, offset + txOffset, txLength] + txValues
            txSuccess = TransmitPacket(address, txPacket, uuid_xim_memory_location_characteristic)
            print ("WriteBankData: {0} for packet {1}".format(txSuccess, txPacket))
            txOffset += txLength
            if(txSuccess == False):
                break


    return txSuccess



def BootloadWrite(address, txPacket):
    logHandler.printLog("BootloadWrite")
    device = GetDeviceWithAddress(address)

    if(device):
        if(device.IsConnected() == False):
            Connect(address, CONNECT_ATTEMPT_TIMEOUT)

    if(device and device.IsConnected()):
        SetDeviceAttributeValue(device, uuid_bls_command_characteristic, None, True)
        txSuccess = TransmitPacket(address, txPacket, uuid_bls_command_characteristic)
    else:
        logHandler.printLog("BootloadWrite cancelled. Device not connected {0}".format(address), True)
        return False

    if(txSuccess == False):
        logHandler.printLog("BootloadWrite failure for address {0}".format(address), True)
        return False
    return True


def BootloadRead(address):
    device = GetDeviceWithAddress(address)
    if(device):
        if(device.IsConnected() == False):
            Connect(address, CONNECT_ATTEMPT_TIMEOUT)

    if(device and device.IsConnected()):
        return GetDeviceAttributeValue(device, uuid_bls_command_characteristic, True)
    else:
##        logHandler.printLog("BootloadRead cancelled. Device not connected {0}".format(address), True)
        return None


MAX_GATT_WRITE_SIZE = 20
MAX_GATT_CHUNK_WRITE_SIZE = 18
MAX_CHUNK_WAIT_TIME = 2.0

# Writes the packet to the characteristic with the given UUID of the given address
def TransmitPacket(address, txPacket, uuid, timeout = 1.0):

    device = GetDeviceWithAddress(address)


    if(device and (device.IsConnected() or device.IsDiscovering())):

        start_time = time.time()
        while(pending_write and ((time.time() - start_time) < 0.2)):
            CheckActivity(ser)

        handle = GetHandle(device, uuid)
        logHandler.printLog("handle {0} for uuid {1}".format(handle, uuid))

        if(pending_write == False and handle and device.connection_handle != None):
            if(len(txPacket) <= MAX_GATT_WRITE_SIZE):
                logHandler.printLog("{0}: TX {4} to {1} handle:{2} attr:{3}".format(time.time(), device.address, device.connection_handle, handle, txPacket))

                device.packetStatus = None

                # if we're connected and we have data, then send it
                ble.send_command(ser, ble.ble_cmd_attclient_attribute_write(device.connection_handle, handle, txPacket))
                SetBusyFlag()

                start_time = time.time()
                while((device.packetStatus == None) and ((time.time() - start_time) < MAX_CHUNK_WAIT_TIME)):
                    CheckActivity(ser)

                if(device.packetStatus == 0):
                    return True
                else:
                    logHandler.printLog("TransmitPacket error: {0}".format(device.packetStatus))
                    return False

            else:
                logHandler.printLog("{0}: Bulk TX {4} to {1} handle:{2} attr:{3}".format(time.time(), device.address, device.connection_handle, handle, txPacket))
                packetOffset = 0
                bulkTxFailure = 0

                while((len(txPacket) - packetOffset) > 0):
                    if((len(txPacket) - packetOffset) >= MAX_GATT_CHUNK_WRITE_SIZE):
                        chunkSize = MAX_GATT_CHUNK_WRITE_SIZE
                    else:
                        chunkSize = len(txPacket) - packetOffset

                    device.bulkPacketTransferred = False

##                    logHandler.printLog("{0}: Prepare write TX {4} to {1} handle:{2} attr:{3}, offset: {5}".format(time.time(), device.address, device.connection_handle, handle, txPacket[packetOffset: packetOffset + chunkSize], packetOffset))
                    ble.send_command(ser, ble.ble_cmd_attclient_prepare_write(device.connection_handle, handle, packetOffset, txPacket[packetOffset: packetOffset + chunkSize]))
                    SetBusyFlag()

                    start_time = time.time()
                    while((pending_write or (device.bulkPacketTransferred == False)) and ((time.time() - start_time) < MAX_CHUNK_WAIT_TIME)):
                        CheckActivity(ser)

                    if(device.bulkPacketTransferred) and (device.packetStatus == 0):
                        packetOffset += chunkSize
                        bulkTxFailure = 0
                    else:
                        logHandler.printLog("TransmitPacket Bulk error: {0}. Status {1}".format(device.bulkPacketTransferred, device.packetStatus), True)
                        return False
##                        packetOffset = 0
##                        bulkTxFailure += 1
##                        if(bulkTxFailure == 5):
##                            break

                device.bulkPacketTransferred = False
                ble.send_command(ser, ble.ble_cmd_attclient_execute_write(device.connection_handle, 1))
                SetBusyFlag()

                start_time = time.time()
                while((pending_write or (device.bulkPacketTransferred == False)) and ((time.time() - start_time) < MAX_CHUNK_WAIT_TIME)):
                    CheckActivity(ser)

                if(device.bulkPacketTransferred) and (device.packetStatus == 0):
                    pass
                else:
                    logHandler.printLog("TransmitPacket Bulk Execute error: {0}. Status {1}".format(device.bulkPacketTransferred, device.packetStatus), True)
                    return False

            return True

    return False


# Requests data from the characteristic with the given UUID of the given address.
#   If timeout is greater than 0, it will wait for the response until the timeout (in seconds) expires
def RequestData(address, uuid, timeout = -1):
    global readInProgress
    value = None

    device = GetDeviceWithAddress(address)
    tempHandle = GetHandle(device, uuid)

    if(device and device.IsConnected() and tempHandle):
        start_time = time.time()
        while(pending_write and ((time.time() - start_time) < 0.2)):
            CheckActivity(ser)

        SetDeviceAttributeValue(device, uuid, None)

        if(pending_write == False and device.connection_handle != None):
            # Request the value from the server
            logHandler.printLog("{0}: Request from {1} handle:{2}".format(time.time(), device.address, tempHandle))
            readInProgress = True
##            ble.send_command(ser, ble.ble_cmd_attclient_read_by_handle(device.connection_handle, tempHandle))
            ble.send_command(ser, ble.ble_cmd_attclient_read_long(device.connection_handle, tempHandle))
            SetBusyFlag()

            if(timeout > 0):
                start_time = time.time()
                while(time.time() - start_time < timeout):
                    Process()

                    value = GetDeviceAttributeValue(device, uuid)
                    if(value != None) and (readInProgress == False):
                        break
    return value


# Writes to the given UUID, then waits for the response
def WriteWithNotification(address, uuid, txPacket, timeout = -1):
    global readInProgress
    value = None

    device = GetDeviceWithAddress(address)
    tempHandle = GetHandle(device, uuid)

    if(device and device.IsConnected() and tempHandle):
        start_time = time.time()
        while(pending_write and ((time.time() - start_time) < 0.2)):
            CheckActivity(ser)

        if(pending_write == False and device.connection_handle != None):
            # Request the value from the server
            logHandler.printLog("{0}: Notification request from {1} handle:{2}".format(time.time(), device.address, tempHandle))
            readInProgress = True

            SetDeviceAttributeValue(device, uuid, None)
            TransmitPacket(address, txPacket, uuid)

            if(timeout > 0):
                start_time = time.time()
                while(time.time() - start_time < timeout):
                    Process()

                    value = GetDeviceAttributeValue(device, uuid)
                    if(value != None) and (readInProgress == False):
                        break
    return value

def HasService(device, uuid):
    for service in device.serviceList:
        if(service.uuid == uuid):
            return True
    return False

def HasCharacteristic(device, uuid):
    for char in device.attributeList:
        if(char.uuid == uuid):
            return True
    return False

# Sets the stored attribute value of the given device with the given characteristic UUID
def SetDeviceAttributeValue(device, uuid, value, isCCC = False):
    if(device):
        if(device.bootloaderMode):
            thisList = device.blAttributeList
        else:
            thisList = device.attributeList
        for attr in thisList:
            if(attr.uuid == uuid):
                if(isCCC):
                    attr.cccValue = value
                else:
                    attr.value = value
                break

# Gets the stored attribute value of the given device with the given characteristic UUID
def GetDeviceAttributeValue(device, uuid, isCCC = False):
    if(device):
        if(device.bootloaderMode):
            thisList = device.blAttributeList
        else:
            thisList = device.attributeList
        for attr in thisList:
            if(attr.uuid == uuid):
                if(isCCC):
                    return attr.cccValue
                else:
                    return attr.value
    return None

# Gets the stored characterisitc handle of the given device with the given characteristic UUID
def GetHandle(device, uuid):
    if(device):
        if(device.bootloaderMode):
            thisList = device.blAttributeList
        else:
            thisList = device.attributeList
        for attr in thisList:
            if(attr.uuid == uuid):
                return attr.handle
    return None
# Gets the stored client characterisitc configuration handle of the given device with the given characteristic UUID
def GetCCCHandle(device, uuid):
    if(device):
        if(device.bootloaderMode):
            thisList = device.blAttributeList
        else:
            thisList = device.attributeList
        for attr in thisList:
            if(attr.uuid == uuid) and (attr.cccHandle):
                return attr.cccHandle
    return None

# attclient_group_found handler
def my_ble_evt_attclient_group_found(sender, args):

    logHandler.printLog("Attributes: {0}".format(args['uuid']), True)

    device = GetDeviceWithConnectionHandle(args['connection'])
    if(device):
        if(device.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]):
            if(device.bootloaderMode):
                thisServiceList = device.blServiceList
            else:
                thisServiceList = device.serviceList
            for service in thisServiceList:
                if service.uuid == list(reversed(args['uuid'])):
                    logHandler.printLog("Found attribute group for service {0}: start={1}, end={2}".format(service.uuid, args['start'], args['end']), True  )
                    service.att_handle_start = args['start']
                    service.att_handle_end = args['end']

# Loads the UUID->Handle mapping of each characteristic for the given device
def GetAttributeInfoFromFile(device):
    missingInfo = True

    if(device.bootloaderMode):
        thisList = device.blAttributeList
    else:
        thisList = device.attributeList

    if(device.deviceType == DEVICE_TYPE_XIM):
        fileName = uuidHandleMapFileName
    else:
        fileName = sensorUuidHandleMapFileName

    with open(fileName, 'r') as f:
        lines = f.readlines()
        for line in lines:
            deviceInfo = line.split(',')
            if(len(deviceInfo) > 1):
                if(deviceInfo[0] == device.swVersion):
##                    logHandler.printLog ("Found matching version in file!")

                    missingInfo = False

                    for attr in thisList:

                        matchFound = False
                        for attrString in deviceInfo[1:]:
                            attrInfo = attrString.split(':')
                            if(len(attrInfo) > 1):
                                uuidList = [int(attrInfo[0][i:i+2],16) for i in range(0,len(attrInfo[0]), 2)]
##                                logHandler.printLog ("AttrInfo uuidList: {0}".format(uuidList))
                                if(attr.uuid == uuidList):
##                                    logHandler.printLog ("Found AttrInfo match!")

                                    handleText = attrInfo[1]

                                    if(handleText != "None"):
                                        attr.handle = int(handleText)
                                        matchFound = True
                                    if(len(attrInfo) > 2):
                                        try:
                                            attr.cccHandle = int(attrInfo[2])
                                        except ValueError:
                                            pass
##                                            logHandler.printLog ("Invalid ccdHandle file value Error")
                                    break
                        if(matchFound == False):
                            logHandler.printLog ("missingInfo for attr.uuid: {0}".format(attr.uuid), True)
                            missingInfo = True
                    if(missingInfo == False):
                        break
    return missingInfo

# Updates the UUID->Handle mapping of each characteristic for the given device
def UpdateAttributeInfoFile(device):

    if(device.bootloaderMode):
        thisList = device.blAttributeList
    else:
        thisList = device.attributeList

    if(device.deviceType == DEVICE_TYPE_XIM):
        fileName = uuidHandleMapFileName
        fileNameTemp = uuidHandleMapFileNameTemp
    else:
        fileName = sensorUuidHandleMapFileName
        fileNameTemp = sensorUuidHandleMapFileNameTemp

    with open(fileName, 'r') as f:
        lines = f.readlines()

    logHandler.printLog ("Adding new attribute info line for version {0}".format(device.swVersion))
    newLine = "{0}".format(device.swVersion)
    hasNullHandle = False

    for attr in thisList:
        newLine += ",{0}:{1}:{2}".format("{0}".format(str(bytearray(attr.uuid)).encode('hex').upper()), attr.handle, attr.cccHandle)
        if(attr.handle == None):
            logHandler.printLog ("attr.handle for uuid {0} is None".format(attr.uuid), True)
            hasNullHandle = True

        if(attr.hasCCC and attr.cccHandle == None):
            logHandler.printLog ("attr.cccHandle for uuid {0} is None".format(attr.uuid), True)
            hasNullHandle = True

    newLine += "\n"
    lines.append(newLine)

    if(hasNullHandle == False):
        with open(fileNameTemp, 'w') as f:
##            logHandler.printLog ("Lines: {0}".format(lines))

            if(len(lines) > 0):
                for line in lines:
                    f.write(line)

        logHandler.RenameSafely(fileNameTemp, fileName)


def GetNetworkInfoFromFile():
    global networkConfigs
    networkConfigs = []
    if(os.path.isfile(bleNetworkConfigFileName)):
        with open(bleNetworkConfigFileName, 'r') as f:
            configLines = f.readlines()
##            print "configLines: {0}".format(configLines)
            for line in configLines:

##            networkConfigs[selectedTxNetworkIndex] = GetNetworkInfoFromLine(f.readline())
##            networkConfigs[selectedRxNetworkIndex] = GetNetworkInfoFromLine(f.readline())

                netStringList = line.split(',')
                if(len(netStringList) >= 3):
                    idString = netStringList[0]
                    keyString = netStringList[1]
                    networkId = [int(idString[i:i+2],16) for i in range(0,len(idString), 2)]
                    aesKey = [int(keyString[i:i+2],16) for i in range(0,len(keyString), 2)]
                    if(len(netStringList) == 3):
                        sqn = int(netStringList[2])
                        networkHeaderKey = [0] * 16
                    else:
                        keyString = netStringList[2]
                        networkHeaderKey = [int(keyString[i:i+2],16) for i in range(0,len(keyString), 2)]
                        sqn = int(netStringList[3])
                    networkConfigs.append(NetworkConfig(networkId, networkHeaderKey, aesKey, sqn))

##    print "networkConfigs: {0}".format(networkConfigs)

    for i in range(2 - len(networkConfigs)):
        networkConfigs.append(NetworkConfig([0] * 4, [0] * 16, NETWORK_KEY_NONE, 0))

##    print "networkConfigs: {0}".format(networkConfigs)

def UpdateNetworkConfigFile():
    with open(bleNetworkConfigFileName, 'w') as f:
        for netConfig in networkConfigs:
            f.write("{0},{1},{2},{3}\n".format(str(bytearray(netConfig.id)).encode('hex'), str(bytearray(netConfig.key)).encode('hex'), str(bytearray(netConfig.headerKey)).encode('hex'), netConfig.txSqn))


def ProcessSwVersion(device, swVersion):
##    logHandler.printLog ("ProcessSwVersion {0} for device {1} with existing version {2}".format(swVersion, device.scannedDeviceId, device.swVersion), True)
    if(device):
        if(swVersion != device.swVersion) and (swVersion != None):
            device.swVersion = swVersion
##            device.InitializeServiceAttributeList(swVersion)

##        GetAttributeInfoFromFile(device)

# attclient_find_information_found handler
def my_ble_evt_attclient_find_information_found(sender, args):

    logHandler.printLog ("Attribute {0} Handle {1}".format(args['uuid'], args['chrhandle']), True)

    device = GetDeviceWithConnectionHandle(args['connection'])

    if(device):

        if(device.bootloaderMode):
            thisList = device.blAttributeList
        else:
            thisList = device.attributeList

        for attr in thisList:
            if args['uuid'] == list(reversed(attr.uuid)):
                logHandler.printLog("Found matching uuid {0} with handle {1}".format(args['uuid'], args['chrhandle']))
                attr.handle = args['chrhandle']
                break
            elif args['uuid'] == list(reversed(uuid_client_characteristic_configuration)) and (attr.handle) and (args['chrhandle'] == attr.handle + 1):
                logHandler.printLog("Found CCC with handle {1}".format(args['uuid'], args['chrhandle']))
                attr.cccHandle = args['chrhandle']


# attclient_procedure_completed handler
def my_ble_evt_attclient_procedure_completed(sender, args):
    global pending_write
    global readInProgress

    pending_write = False
    readInProgress = False

    device = GetDeviceWithConnectionHandle(args['connection'])

    logHandler.printLog("{0}: procedure_completed: {1}".format(time.time(), args))

    if(device):

        if(device.connectionState == STATE_GET_VERSION):
            logHandler.printLog("Found SW Version: {0}".format(device.swVersion))
            if(device.swVersion != None):
                try:
                    swVersionValue = float(device.swVersion)
                # Assume it's the newest version
                except ValueError:
                    swVersionValue = None
                if(swVersionValue != None):
                    if(device.deviceType == DEVICE_TYPE_XIM):
                        if(float(device.swVersion) >= 0.040):

                            if(float(device.swVersion) >= 0.055):
                                device.serviceList.append(ServiceInfo(uuid_sensor_response_service))

                                newChars = [uuid_sensor1_response_characteristic, uuid_sensor2_response_characteristic]
                                newCharsWithCCC = []
                                if(float(device.swVersion) >= 0.075):
                                    newChars += [uuid_device_id_characteristic, uuid_group_membership_characteristic, uuid_access_network_select_characteristic, uuid_access_user_login_characteristic,
                                        uuid_access_config_characteristic, uuid_access_admin_login_characteristic, uuid_access_network_list_characteristic]
                                    logHandler.printLog("Adding new Network Chars: {0}".format(newChars))

                                    if(float(device.swVersion) >= 0.077):
                                        newChars += [uuid_xim_temperature_histogram_characteristic,uuid_xim_intensity_histogram_characteristic] # uuid_xim_historic_data_characteristic

                                    if(float(device.swVersion) >= 0.080) and (float(device.swVersion) <= 0.083):
                                        newChars += [uuid_access_network_header_key_characteristic]

                                    if(float(device.swVersion) >= 0.084):
                                        newChars += [uuid_access_network_config_characteristic]

                                    if(float(device.swVersion) >= 0.093):
                                        device.serviceList.append(ServiceInfo(uuid_dim_1_10V_service))
                                        newChars += [uuid_dali_light_config_characteristic, uuid_dali_address_config_characteristic, uuid_dali_scenes_characteristic,
                                                        uuid_dim_1_10V_status_characteristic, uuid_dim_1_10V_config_characteristic]

                                    if(float(device.swVersion) >= 0.098):
                                        device.serviceList.append(ServiceInfo(uuid_oem_service))
                                        newChars += [uuid_access_oem_login_characteristic, uuid_access_oem_data_characteristic, uuid_light_control_scenes_characteristic]
##                                    # Jeff Test
                                    newChars += [uuid_dali_command_characteristic, uuid_dali_status_characteristic]
                                    newCharsWithCCC += [uuid_xim_memory_location_characteristic]
                                else:
                                    newChars += [uuid_xim_memory_location_characteristic, uuid_dali_command_characteristic]
                                    newCharsWithCCC += [uuid_xim_memory_value_characteristic, uuid_dali_response_characteristic]
                                    if(float(device.swVersion) >= 0.061):
                                        newChars += [uuid_device_id_characteristic, uuid_access_key_characteristic, uuid_access_control_characteristic]

                                for newChar in newChars:
                                    if(HasCharacteristic(device, newChar) == False):
                                        device.attributeList.append(AttributeInfo(newChar))

                                for newChar in newCharsWithCCC:
                                    if(HasCharacteristic(device, newChar) == False):
                                        device.attributeList.append(AttributeInfo(newChar, True))

                                missingInfo = GetAttributeInfoFromFile(device)
                                missingNewHandle = False

                                for newChar in newChars:
                                    if(GetHandle(device, newChar) == None):
                                        missingNewHandle = True
                                        break
                            else:
                                missingInfo = GetAttributeInfoFromFile(device)
                                missingNewHandle = (None in [GetCCCHandle(device, uuid_dali_response_characteristic)])


                        else:
                            missingInfo = GetAttributeInfoFromFile(device)
                            missingNewHandle = (None in [GetHandle(device, uuid_dis_firmware_rev_characteristic)])

                            if(len(device.serviceList) > 1):
                                device.serviceList = [ServiceInfo(uuid_dis_service)]

                            if(len(device.attributeList) > 6):
                                device.attributeList = [  AttributeInfo(uuid_dis_mfg_name_characteristic), AttributeInfo(uuid_dis_model_number_characteristic), AttributeInfo(uuid_dis_serial_number_characteristic),
                                                            AttributeInfo(uuid_dis_hardware_rev_characteristic), AttributeInfo(uuid_dis_firmware_rev_characteristic), AttributeInfo(uuid_dis_software_rev_characteristic)]

                    elif(device.deviceType == DEVICE_TYPE_XSENSOR):

                        newChars = []
                        newCharsWithCCC = []
                        if(float(device.swVersion) >= 0.075):
                            newChars += [uuid_device_id_characteristic, uuid_group_membership_characteristic, uuid_access_network_select_characteristic, uuid_access_user_login_characteristic,
                                uuid_access_config_characteristic, uuid_access_admin_login_characteristic, uuid_access_network_list_characteristic]
                            logHandler.printLog("Adding new Network Chars: {0}".format(newChars))

                            if(float(device.swVersion) >= 0.084):
                                newChars += [uuid_access_network_config_characteristic]

                            if(float(device.swVersion) >= 0.088):
                                newChars += [uuid_sensor_general_characteristic, uuid_sensor_lux_characteristic, uuid_sensor_motion_characteristic]
                        else:
                            newChars += [uuid_device_id_characteristic, uuid_access_key_characteristic, uuid_access_control_characteristic]

                        for newChar in newChars:
                            if(HasCharacteristic(device, newChar) == False):
                                device.attributeList.append(AttributeInfo(newChar))

                        for newChar in newCharsWithCCC:
                            if(HasCharacteristic(device, newChar) == False):
                                device.attributeList.append(AttributeInfo(newChar, True))

                        missingInfo = GetAttributeInfoFromFile(device)
                        missingNewHandle = False

                        for newChar in newChars:
                            if(GetHandle(device, newChar) == None):
                                missingNewHandle = True
                                break

                    logHandler.printLog("{0}: Find services. missingInfo = {1}, missingNewHandle = {2}".format(time.time(), missingInfo, missingNewHandle))
                    if(missingInfo or missingNewHandle):
                        logHandler.printLog("{0}: Find services. pending_write = {1}".format(time.time(), pending_write))
                        if(device.bootloaderMode):
                            thisServiceList = device.blServiceList
                        else:
                            thisServiceList = device.serviceList

                        for service in thisServiceList:
                            if(service.attributesDiscovered == SERVICE_ATTRIBUTES_FINDING):
                                service.attributesDiscovered = SERVICE_ATTRIBUTES_NONE

                        device.connectionState = STATE_FINDING_SERVICES
                        ble.send_command(ser, ble.ble_cmd_attclient_read_by_group_type(args['connection'], 0x0001, 0xFFFF, list(reversed(uuid_service))))
##                        device.connectionState = STATE_FINDING_ATTRIBUTES
##                        ble.send_command(ser, ble.ble_cmd_attclient_find_information(device.connection_handle, 14, 0xFFFF))
                        SetBusyFlag()

                    else:
                        ProcessDiscoveredDevice(device)

        # check if we just finished searching for services
        elif device.connectionState == STATE_FINDING_SERVICES:

            if(device.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]):
                pending_write = False
                undiscoveredCount = 0

                if(device.bootloaderMode):
                    thisServiceList = device.blServiceList
                else:
                    thisServiceList = device.serviceList

                for service in thisServiceList:
                    if(service.attributesDiscovered == SERVICE_ATTRIBUTES_FINDING):
                        service.attributesDiscovered = SERVICE_ATTRIBUTES_FOUND
                        logHandler.printLog("Found attribute information for service {0} in range {1}-{2}...".format(service.uuid, service.att_handle_start, service.att_handle_end), True)
                    elif(service.attributesDiscovered == SERVICE_ATTRIBUTES_NONE):

                        logHandler.printLog("Undiscovered service {0} with range {1}-{2}...".format(service.uuid, service.att_handle_start, service.att_handle_end), True)

                        if(service.att_handle_end and pending_write == False):
                            logHandler.printLog("Found service {0}. Finding attribute information in range {1}-{2}...".format(service.uuid, service.att_handle_start, service.att_handle_end), True)
                            ble.send_command(ser, ble.ble_cmd_attclient_find_information(device.connection_handle, service.att_handle_start, service.att_handle_end))
                            SetBusyFlag()
                            service.attributesDiscovered = SERVICE_ATTRIBUTES_FINDING
                        else:
                            undiscoveredCount += 1

                logHandler.printLog("undiscoveredCount: {0}".format(undiscoveredCount), True)
                if(undiscoveredCount == 0):
                    device.connectionState = STATE_FINDING_ATTRIBUTES

        # check if we just finished searching for attributes
        elif device.connectionState == STATE_FINDING_ATTRIBUTES:

            if(device.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]):

                if(device.bootloaderMode):
                    ProcessDiscoveredBootloaderXim(device)
                else:
                    ProcessDiscoveredDevice(device)
                    UpdateAttributeInfoFile(device)
            else:
                logHandler.printLog("Connection problem in STATE_FINDING_ATTRIBUTES")

        elif(device.connectionState == STATE_ENABLING_NOTIFICATIONS):
            logHandler.printLog("{0}: Finished STATE_ENABLING_NOTIFICATIONS".format(time.time()))

            if(device.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]):
                device.connectionState = STATE_LISTENING_DATA

        else:
            device.packetStatus = args['result']
            if(device.bulkPacketTransferred == False):
##                logHandler.printLog("{0}: Successfully transmitted bulk packet".format(time.time()), True)
                device.bulkPacketTransferred = True

    else:
        logHandler.printLog("{0}: ERROR: procedure_completed for unconnected device. args: {1}".format(time.time(), args))

# Determines the capabilities of the discovered XIM, based on its software version
def ProcessDiscoveredDevice(device):
    global pending_write
    device.connectionState = STATE_LISTENING_DATA


def ProcessDiscoveredBootloaderXim(device):
    tempHandle = GetCCCHandle(device, uuid_bls_command_characteristic)
    if tempHandle:
        logHandler.printLog("Found Bootloader Command CCC attribute with handle {0}".format(tempHandle), True)

        ble.send_command(ser, ble.ble_cmd_attclient_attribute_write(device.connection_handle, tempHandle, [0x01, 0x00]))
        SetBusyFlag()
        device.connectionState = STATE_ENABLING_NOTIFICATIONS
    else:
        logHandler.printLog("Bootloader Command CCC attribute not found", True)

def my_ble_rsp_attclient_find_information(sender, args):
##    global pending_write
##    pending_write = False
    logHandler.printLog("{0}: Find information command complete {1}".format(time.time(), args))

# Confirmation that the read_by_group_type command was received
def my_ble_rsp_attclient_read_by_group_type(sender, args):
##    global pending_write
##    pending_write = False
    logHandler.printLog("{0}: Read by Group Type command complete {1}".format(time.time(), args))


# Confirmation that the read_by_type command was received
def my_ble_rsp_attclient_read_by_type(sender, args):
    logHandler.printLog("{0}: Read by Type command complete {1}".format(time.time(), args))

# Confirmation that the attribute_write command was received
def my_ble_rsp_attclient_attribute_write(sender, args):
    logHandler.printLog("{0}: Attribute write command complete {1}".format(time.time(), args))

def my_ble_rsp_attclient_prepare_write(sender, args):
    logHandler.printLog("{0}: Prepare write command complete {1}".format(time.time(), args))

def my_ble_rsp_attclient_execute_write(sender, args):
    logHandler.printLog("{0}: Execute write command complete {1}".format(time.time(), args))

# Event that is triggered when an attribute read returns a value
def my_ble_evt_attclient_attribute_value(sender, args):
    global pending_write

    # Read_by_handle is acknowledged here. Notifications and Indications (type 1 and 2) are not. Writes are acknowledged in procedure_completed
    if(not(args['type'] in [1, 2])):
        pending_write = False

    device = GetDeviceWithConnectionHandle(args['connection'])

    logHandler.printLog("{0}: Value received: {1} ".format(time.time(), args))

    if(device):
        # Since this used read_by_type, it's not possible to verify the received handle,
        #   so at least make sure it's not a notification or indication
        if(device.connectionState == STATE_GET_VERSION) and (args['type'] == 3):
            ProcessSwVersion(device, ''.join(chr(i) for i in args['value']))
        else:
            isInList = False

            if(device.bootloaderMode):
                thisList = device.blAttributeList
            else:
                thisList = device.attributeList
            for attr in thisList:

                if(args['atthandle'] == attr.handle):
                    logHandler.printLog("{0}: Value received: {1} for attribute in list".format(time.time(), args))

                    isInList = True
                    if(args['type'] in [1, 2]):
                        if(attr.cccValue == None):
                            attr.cccValue = args['value']
                        else:
                            logHandler.printLog("{0} Appending {1} to {2}".format(time.time(), args['value'], attr.cccValue), True)
                            attr.cccValue += args['value']
                    else:
                        if(attr.value == None):
                            attr.value = args['value']
                        else:
                            logHandler.printLog("{0} Appending {1} to {2}".format(time.time(), args['value'], attr.value), True)
                            attr.value += args['value']

            if(isInList == False):
                logHandler.printLog("{0}: Value received: {1} for attribute not in list".format(time.time(), args))
    else:
        logHandler.printLog("{0}: Value received: {1} for missing connection".format(time.time(), args))



# ######################################
# Section: Device Management - Internal Functions
# ######################################


# ######################################
# Section: Main System - Internal Functions
# ######################################

def CheckActivity(ser, timeout = 0):
    global serialFailures

    try:
        ble.check_activity(ser, timeout)
    except:
        e = sys.exc_info()[0]
        logHandler.printLog("Exception thrown during check_activity. {0}".format(e), True)
        serialFailures += 1
        raise


# BGAPI parser timed out
def my_timeout(sender, args):
    global pending_write

    logHandler.printLog("BGAPI parser timed out. Make sure the BLE device is in a known/idle state.")
    pending_write = False

# BlueGiga module rebooted
def my_ble_evt_system_boot(sender, args):
    print ("{0}: Reset complete".format(time.time()))

# Hello Response (Ping) from BlueGiga Dongle
def my_ble_rsp_system_hello(sender, args):
    global hello_received
    logHandler.printLog("{0}: Hello Response received! {1}".format(time.time(), args))
    hello_received = True

# Address Response (Ping) from BlueGiga Dongle
def my_ble_rsp_system_address_get(sender, args):
    global info_received
    global local_address
    logHandler.printLog("{0}: Address Response received! {1}".format(time.time(), args))
    local_address = args['address']
    info_received = True

# Confirmation that the dongle's Rx Gain was set
def my_ble_rsp_hardware_set_rxgain(sender, args):
    logHandler.printLog("{0}: Rx Gain Set {1}".format(time.time(), args))

# RSSI received
def my_ble_rsp_connection_get_rssi(sender, args):
    global pending_write

    device = GetDeviceWithConnectionHandle(args['connection'])
    if(device):
        device.pcRssiValue = args["rssi"]
        logHandler.printLog ("{0}: Received internal RSSI: {1} for device {2}".format(time.time(), args["rssi"], device.address))
    else:
        logHandler.printLog ("{0}: Received internal RSSI: {1} for unknown device".format(time.time(), args["rssi"]))
    pending_write = False

# Indicate that a new command was sent to the BlueGiga module.
def SetBusyFlag():
    global pending_write, ble_write_time
    pending_write = True
    ble_write_time = time.time()


# Gets the last used COM port for the BlueGiga dongle
def GetLastPort():

    if(os.path.isfile("{0}".format(bleComPortFileName)) == False):
        logHandler.printLog("Created {0}".format(bleComPortFileName))
        with open("{0}".format(bleComPortFileName), 'w') as f:
            pass

    with open("{0}".format(bleComPortFileName), 'r') as f:
        portTest = f.readline()

    return portTest

# Tests if the selected COM port (portTest) works
def TestPort(portTest):
    global ble, ser
    global hello_received, info_received

    portFound = False

    try:
        ser.close()
    except:
        pass

    try:
        # create serial port object
        #print(dir(cfg))
        if (cfg.WINDOWS):
            ser = serial.Serial(port="COM{0}".format(portTest), baudrate=115200, timeout=1, writeTimeout=1)
        if (cfg.LINUX):
            if (cfg.PI3):
                ser = serial.Serial(port="/dev/ttyACM{0}".format(portTest), baudrate=115200, timeout=1, writeTimeout=1)
        if (cfg.OSX):
            ser = serial.Serial(port="/dev/tty.usbmodem1".format(portTest), baudrate=115200, timeout=1, writeTimeout=1)

        ser.close()
        ser.open()
        # flush buffers
        ser.flushInput()
        ser.flushOutput()
    except serial.SerialException as e:
        if (cfg.WINDOWS):
            logHandler.printLog("No serial port at COM{0}".format(portTest))
        if (cfg.LINUX):
            if (cfg.PI3):
                logHandler.printLog("No serial port at /dev/ttyACM{0}".format(portTest))
    else:

        ble.bgapi_rx_buffer = []
        ble.bgapi_rx_expected_length = 0
        ble.send_command(ser, ble.ble_cmd_system_hello())
        start_time = time.time()
        while((time.time() - start_time) < 0.1):
            CheckActivity(ser)

            if(hello_received):
                break

        if(hello_received):
            ble.send_command(ser, ble.ble_cmd_system_address_get())

            start_time = time.time()
            while((time.time() - start_time) < 0.1):
                CheckActivity(ser)

                if(info_received):
                    break

        if(info_received):
            info_received = False
            if (cfg.WINDOWS):
                logHandler.printLog("Working BLE Port found at COM{0}".format(portTest))
            if (cfg.LINUX):
                if (cfg.PI3):
                    logHandler.printLog("Working BLE Port found at /dev/ttyACM{0}".format(portTest))
            portFound = True
            with open("{0}".format(bleComPortFileName), 'w') as f:
                f.write("{0}".format(portTest))

            SendInitSequence()
        else:
            ser.close()

    return portFound

# Sends the commands for initializing the BlueGiga module
def SendInitSequence():
    global pending_write
    global peripheral_list

    global scanningEnabled

    try:
        logHandler.printLog("**************** Init Sequence")

        # disconnect if we are connected already
        TestConnection()

        peripheral_list = []

        # stop advertising if we are advertising already
        ble.send_command(ser, ble.ble_cmd_gap_set_mode(0, 0))
        CheckActivity(ser, 1)

        # stop scanning if we are scanning already
        ble.send_command(ser, ble.ble_cmd_gap_end_procedure())
        CheckActivity(ser, 1)

        # set scan parameters
        ble.send_command(ser, ble.ble_cmd_gap_set_scan_parameters(200, 200, 1))
        CheckActivity(ser, 1)

        # set RX Gain
        ble.send_command(ser, ble.ble_cmd_hardware_set_rxgain(bgRxGain))
        CheckActivity(ser, 1)

        # set advertising interval
        SetLocalAdvertisingInterval(bleAdvertisingIntervalMin, bleAdvertisingIntervalMax, bleAdvertisingWindow)
        CheckActivity(ser, 1)

        ble.send_command(ser, ble.ble_cmd_sm_set_bondable_mode(BONDING_VALUE))
        CheckActivity(ser, 1)


        # Jeff Test
        ble.send_command(ser, ble.ble_cmd_sm_delete_bonding(0xFF))
        CheckActivity(ser, 1)

        ble.send_command(ser, ble.ble_cmd_sm_get_bonds())
        CheckActivity(ser, 1)

        # Jeff Test
        ble.send_command(ser, ble.ble_cmd_sm_set_oob_data([])) # [2] * 16
        CheckActivity(ser, 1)


        # start scanning now
        logHandler.printLog("Scanning for BLE peripherals...")
        Discover()
        CheckActivity(ser, 1)

    except:
        print("BLE Initialization Error. Make sure the BLE dongle is not being used by another application")

# Sets the flag that indicates that scanning is enabled
def SetScanningEnabled(value):
    global scanningEnabled
    scanningEnabled = value

# Clears the flag that indicates that scanning is enabled
def GetScanningEnabled():
    global scanningEnabled
    return scanningEnabled

# Returns True if the stack isn't waiting for a command to be processed by the BlueGiga module
def IsLinkReady():
    global pending_write
    return not pending_write

# Returns True if the stack is in a state where it is busy.
def IsSystemBusy():
    return (not(bgCentralState in [CENTRAL_STATE_STANDBY, CENTRAL_STATE_SCANNING]))

def IsPeripherialBusy():
    return not(bgPeriphState in [PERIPH_STATE_STANDBY])

# ######################################
# Section: Value Conversion
# ######################################
def ConvertListToInt(thisList, isLittleEndian = True):
    total = 0
    multiplier = 1
    if(isLittleEndian == False):
        thisList = list(reversed(thisList))
    for value in thisList:
        total += value * multiplier
        multiplier *= 256
    return total

def ConvertIntToList(value, length, isLittleEndian = True):
    outList = []
    divisor = 256 ** (length - 1)

    while(length > 0):
        valueItem = int(value / divisor)
        outList.append(valueItem)
        value -= valueItem * divisor
        divisor /= 256
        length -= 1

    if(isLittleEndian):
        outList = list(reversed(outList))
    return outList



# ######################################
# Section: Advertisements - APIs
# ######################################


"""
API Name: GetLocalDeviceId
Returns the local device ID as a 4-integer list
"""
def GetLocalDeviceId():
    return bleLocalDeviceId

"""
API Name: SetLocalDeviceId
Sets the local device ID. The parameter must be an integer 0 - 32767
"""
def SetLocalDeviceId(deviceId):
    global bleLocalDeviceId

    if(deviceId <= 32767):
        bleLocalDeviceId = deviceId
        SetConnectionParameters(bleMinInterval, bleMaxInterval, bleConnTimeout, bleSlaveLatency, bgRxGain, bleAdvertisingIntervalMin, bleAdvertisingIntervalMax, bleAdvertisingWindow, deviceId)


"""
API Name: SetLocalAdvertisingInterval
Sets the min and max advertising interval range and sets the duration of the
    advertisement (how long it advertises for). advMin, advMax, and advDuration
    are in milliseconds
"""
#
def SetLocalAdvertisingInterval(advMin, advMax, advDuration = ADVERTISING_WINDOW):
    global bleAdvertisingWindow
    advMinValue = int(round(advMin / 0.625))
    advMaxValue = int(round(advMax / 0.625))
    bleAdvertisingWindow = advDuration
    # 0x07 means use all 3 advertisement channels
    ble.send_command(ser, ble.ble_cmd_gap_set_adv_parameters(advMinValue, advMaxValue, 0x07))
    SetBusyFlag()

"""
API Name: BroadcastLightLevel
Advertises a light control packet to destination device ID (4-byte list),
with values:
    'light_level': New light intensity. Float between 0.0 - 100.0%
    'fade_time': Time to fade from the current intensity to the new intensity,
        in milliseconds (0 - 60000)
    'response_time': Delay (in milliseconds) from when XIM receives the device to
        when it starts changing the intensity.
        The XIM's resolution is 10 millisecond steps
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.
    'use_fade_rate': Use a constant fade rate
"""
def BroadcastLightLevel(destination, values):
##    print "Intensity in {0}, out {1}".format(values['light_level'], ConvertIntensityToValue(values['light_level']))
    BroadcastLightControl(destination, ConvertIntensityToValue(values['light_level']), values['fade_time'], values)

"""
API Name: BroadcastStopFading
Advertises a light control packet that stops fading to destination device ID (4-byte list),
  with values:
    'response_time': Delay (in milliseconds) from when XIM receives the device to
        when it starts changing the intensity.
        The XIM's resolution is 10 millisecond steps
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.

"""
def BroadcastStopFading(destination, values):
    BroadcastLightControl(destination, STOP_FADING_VALUE, 0, values)

"""
API Name: BroadcastSensorControlMode
Advertises a light control packet that stops fading to destination device ID (4-byte list),
  with values:
    'response_time': Delay (in milliseconds) from when XIM receives the device to
        when it starts changing the intensity.
        The XIM's resolution is 10 millisecond steps
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.
"""
def BroadcastSensorControlMode(destination, values):
    BroadcastLightControl(destination, SENSOR_CONTROL_VALUE, 0, values)


##FADE_MAP_DOWNSCALE_FACTOR_1 = 10
##FADE_MAP_DOWNSCALE_FACTOR_2 = 512
##FADE_MAP_DOWNSCALE_INDEX = 90
##FADE_MAP_MAX_INDEX = 122
##MAX_FADE_TIME_V2_29 = 60000
fadeMap = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900,
1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900,
2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250,
4500, 4750, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500,
9000, 9500, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000,
18000, 19000, 20000, 22500, 25000, 27500, 30000, 35000, 40000, 45000,
50000, 55000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 135000,
150000, 165000, 180000, 195000, 210000, 225000, 240000, 255000, 270000, 285000,
300000, 330000, 360000, 390000, 420000, 450000, 480000, 510000, 540000, 570000,
600000, 660000, 720000, 780000, 840000, 900000, 960000, 1020000, 1080000, 1140000,
1200000, 1350000, 1500000, 1650000, 1800000, 2100000, 2400000, 2700000, 3000000, 3300000,
3600000, 4200000, 4800000, 5400000, 6000000, 6600000, 7200000, 8100000, 9000000, 9900000,
10800000, 12600000, 14400000]
def TableIndexLookup(table, value):
    pos = bisect_left(table, value)
    if pos == 0:
        return 0
    if pos == len(table):
        return len(table) - 1
    before = table[pos - 1]
    after = table[pos]
    if after - value < value - before:
       return pos
    else:
       return pos - 1

overrideMap = [0, 10, 20, 30, 60, 120, 300, 600]

def BroadcastLightControl(destination, intensityInteger, fadeTimeInteger, values):

    txPacket = ConvertIntToList(intensityInteger, 2)
    if(len(destination) == 4):

        txPacket += ConvertIntToList(fadeTimeInteger, 2)
        txPacket.append(int(values['response_time'] / 10))
        txPacket.append(int(values['override_time'] / 10))
        if(values['lock_light_control']):
            txPacket.append(1)
        else:
            txPacket.append(0)

        BroadcastCommand(BLEX_SENSOR_PACKET, [0, BLEX_SENSOR_LIGHT_CONTROL] + destination + txPacket + [0, 0, 0])
    else:
        newFadeIndex = TableIndexLookup(fadeMap, fadeTimeInteger)

##        print "newFadeIndex {0} for fade time {1}".format(newFadeIndex, fadeTimeInteger)
##        txPacket.append(min(255, int(round(fadeTimeInteger / 100))))

        try:
            if(values['use_fade_rate']):
                newFadeIndex |= 0x80
        except:
            pass

        txPacket.append(newFadeIndex)

        txResponseTime = min(7, int(round(values['response_time'] / 50)))
        txOverrideTime = min(7, TableIndexLookup(overrideMap, values['override_time']))
        if(values['lock_light_control']):
            txLockout = 1
        else:
            txLockout = 0
        txPacket.append((txLockout << 7) + (txOverrideTime << 3) + txResponseTime)
##        print "txOverrideTime: {0}".format(txOverrideTime)
##        print "LightLevel: {0}".format(txPacket)

        SetXBPacket(destination, ENCRYPTED_PACKET_TYPE_LIGHT_CONTROL, txPacket)


"""
API Name: BroadcastRecallScene
Advertises a recall scene packet to destination device ID (4-byte list),
with values:
    'scene_number': Scene number
    'fade_time': Time to fade from the current intensity to the scene's intensity,
        in milliseconds
    'response_time': Delay (in milliseconds) from when XIM receives the device to
        when it starts changing the intensity.
        The XIM's resolution is 10 millisecond steps
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.
"""
def BroadcastRecallScene(destination, values):
    txPacket = ConvertIntToList(values['scene_number'], 2)
    if(len(destination) == 4):

        txPacket += ConvertIntToList(values['fade_time'], 2)
        txPacket.append(int(values['response_time'] / 10))
        txPacket.append(int(values['override_time'] / 10))
        if(values['lock_light_control']):
            txPacket.append(1)
        else:
            txPacket.append(0)

        BroadcastCommand(BLEX_SENSOR_PACKET, [0, BLEX_SENSOR_RECALL_SCENE] + destination + txPacket + [0, 0, 0])
    else:

        if(values['fade_time'] == None):
            txPacket.append(0xFF)
        else:

            newFadeIndex = TableIndexLookup(fadeMap, values['fade_time'])

            try:
                if(values['use_fade_rate']):
                    newFadeIndex |= 0x80
            except:
                pass
            txPacket.append(newFadeIndex)

        txResponseTime = min(7, int(round(values['response_time'] / 50)))
        txOverrideTime = min(7, int(round(values['override_time'] / 10)))
        if(values['lock_light_control']):
            txLockout = 1
        else:
            txLockout = 0
        txPacket.append((txLockout << 7) + (txOverrideTime << 3) + txResponseTime)
        print ("Recall Scene: {0}".format(txPacket))

        SetXBPacket(destination, ENCRYPTED_PACKET_TYPE_RECALL_SCENE, txPacket)



"""
API Name: BroadcastIndicate
Advertises a recall scene packet to destination device ID (4-byte list),
with values:
    'num_flashes': Number of flashes. 0 - 10
    'period': Period of the flash (in milliseconds). 0 - 25000.
            The XIM's resolution is 100 millisecond steps
    'high_level': Intensity of the high level of the flash. 0.0 - 100.0
    'low_level': Intensity of the high level of the flash. 0.0 - 100.0
"""
def BroadcastIndicate(destination, values):


    if(len(destination) == 4):
        txPacket = [values['num_flashes']]
        txPacket.append(int(values['period'] / 100))

        intensity = ConvertIntensityToValue(values['high_level'])
        txPacket += ConvertIntToList(intensity, 2)

        intensity = ConvertIntensityToValue(values['low_level'])
        txPacket += ConvertIntToList(intensity, 2)
        BroadcastCommand(BLEX_SENSOR_PACKET, [0, BLEX_SENSOR_INDICATE] + destination + txPacket + [0, 0, 0, 0])
    else:
        txPacket = [values['num_flashes']]
        txPacket.append(int(values['period'] / 100))

        txPacket.append(int(round(values['high_level'])))
        txPacket.append(int(round(values['low_level'])))
        SetXBPacket(destination, ENCRYPTED_PACKET_TYPE_INDICATE, txPacket)

##    if(IsEncryptedAdvEnabled(destination)):
##        SetXBPacket(destination, ENCRYPTED_PACKET_TYPE_INDICATE, txPacket)
##    else:
##        BroadcastCommand(BLEX_SENSOR_PACKET, [0, BLEX_SENSOR_INDICATE] + txPacket + [0, 0, 0, 0])


"""
API Name: EnableConnections
Enables the  destination device ID (4-byte list) to be connectable for
the specified duration:
        'duration': Connectable duration (in milliseconds)
"""
def EnableConnections(destination, values = {'duration':3000, 'interval': 100}):


    if(len(destination) == 4):
        txPacket = ConvertIntToList(values['duration'], 2)
        BroadcastCommand(BLEX_ENABLE_CONNECTIONS_PACKET, destination + txPacket + [0])
    else:
        SetOobData(destination)

        txPacket = [min(255, int(round(values['duration'] / 100))), min(255, int(round(values['interval'] / 10)))]
        SetXBPacket(destination, ENCRYPTED_PACKET_TYPE_SET_CONNECTABLE, txPacket)


def FindClosestValue(inputValue, valueList):
    return min(valueList, key=lambda x:abs(x - inputValue))

def FindOffsetOfClosestValue(inputValue, valueList):
    closestValue = min(valueList, key=lambda x:abs(x - inputValue))
    return valueList.index(closestValue)

"""
API Name: BroadcastRequestAdv
Reqeusts the destination device to start advertising :
        'packetType': XBeacon Advertsisement Packet Type
        'numAdv': Number of advertisements (0 = Stop or resume default behavior, 255 = continuous)
        'advInterval': Advertisment interval (in ms)
        'numBursts': Number of additional advetisements in an advertisement burst
        'burstInterval': Interval between the bursts
"""
def BroadcastRequestAdv(destination, packetType, parameters = {'delay': 100, 'variability': 100, 'numBursts': 3, 'burstInterval': 40}):
    txPacket = packetType

    if(len(packetType) == 1):
        txPacket.append(0)

    delayValues =  [0, 5, 10, 20, 50, 100, 200, 500]
    txDelay = FindOffsetOfClosestValue(parameters['delay'], delayValues)
    txVariability = FindOffsetOfClosestValue(parameters['variability'], delayValues)
    txPacket.append((txDelay << 4) + txVariability)

    if(parameters['numBursts'] > 7):
        txNumBursts = 7
    else:
        txNumBursts = parameters['numBursts']
    txBurstInterval = int(round(parameters['burstInterval'] / 10))
    if(txBurstInterval > 31):
        txBurstInterval = 31
    txPacket.append((txNumBursts << 5) + txBurstInterval)

##    print "RequestAdv packet: {0}".format(txPacket)

    if(len(destination) in [1,3]):
        SetXBPacket(destination, ENCRYPTED_PACKET_TYPE_REQUEST_ADV, txPacket)
        return True
    else:
        return False

"""
API Name: BroadcastEHSwitch
Advertises the switch state
"""
def BroadcastEHSwitch(values):
    txPacket = values
    BroadcastCommand(BLEX_EHSWITCH_PACKET, txPacket)

    start_time = time.time()
    while(pending_write and ((time.time() - start_time) < 0.2)):
        CheckActivity(ser)

    EndProcedure()
    CheckActivity(ser, 1)

    fullPacket = [2, 1, 6, 9 + len(txPacket), 0xFF] + ADV_COMPANY_ID_XICATO + BLEX_EHSWITCH_PACKET + bleLocalDeviceIdV0 + txPacket
##    print "BroadcastEHSwitch fullPacket: {0}".format(fullPacket)
    SetAdvertisingData(fullPacket)

    CheckActivity(ser, 1)
    scanningEnabled = False
    SetAdvertisingState(True)


# ######################################
# Section: Scanning - APIs
# ######################################

"""
API Name: GetScannedData
Returns the scanned data from the xBeacon advertisements of device with BLE address.
Returned values are:
    'lastScanTime': Most recent time that any advertisement packet was received from this device. Value is in seconds.
    'lastRealTimeUpdate': Most recent time than an xBeacon 1 packet was received
    'lastHistoryUpdate': Most recent time than an xBeacon 2 packet was received
    'deviceId': 4-byte ID of the device
    'deviceName': Value of the device name in the scan response packet. String.
    'productId': 2-byte value representing the product ID
    'intensity': intensity percentage. 0 - 100%
    'power': Power consumption (in Watts)
    'status': XIM status. b6:4 is temperature status (000 is normal), b3:2 is input voltage status (01 is normal), b1:0 is Vf Status (00 is normal)
    'coreTemperature': Core temperature, in degress Celcius.
    'pcbTemperature': PCB temperature, in degress Celcius.
    'vin': Input voltage (in volts).
    'vinRipple': Input voltage ripple (in millivolts)
    'hours': Operating hours
    'rssi': Receive signal strength.
    'lockoutTimeRemaining': Time remaining that the device has light level control locked out from other device. Value is in seconds, XIM resolution is 10s steps.
    'powerCycles': Number of times the XIM has been power cycled
    'ledCycles': Number of times the XIM's light has turned on
    'bootloaderMode': True if in the bootloader state
    'lastBootloaderUpdate': Most recent time that a bootloader mode packet was received
"""
def GetScannedData(address):
    for device in peripheral_list:
        if(device.address == address):
            if(device.deviceType == DEVICE_TYPE_XIM):
                return {'lastScanTime':device.lastScanTime, 'lastRealTimeUpdate':device.xb1UpdateTime, 'lastHistoryUpdate':device.xb2UpdateTime, 'lastDeviceInfoUpdate': device.deviceInfoUpdateTime,
                        'deviceId':device.scannedDeviceId,  'deviceName': device.deviceName, 'productId': device.scannedProductId,
                        'intensity':device.scannedIntensity, 'power':device.scannedPower, 'status':device.scannedStatus,
                        'coreTemperature': device.scannedLedTemperature, 'pcbTemperature': device.scannedPcbTemperature, 'vin': device.scannedVin, 'vinRipple': device.scannedVinRipple,
                        'hours':device.scannedHours, 'rssi':device.scannedRssi,
                        'lockoutTimeRemaining': device.scannedLockoutTimeRemaining,
                        'powerCycles': device.scannedPowerCycles , 'ledCycles': device.scannedLedCycles,
                        'daliStatus': device.daliStatus,
                        'bootloaderMode': device.bootloaderMode, 'lastBootloaderUpdate': device.bootloaderModeUpdateTime,
                        'encryptedAdv': device.encryptedAdv,
                        'swVersion': device.swVersion, 'hwVersion': device.hwVersion, 'fwVersion': device.ledControllerVersion,
                        'programmedFlux': device.programmedFlux,
                        'overloadTemperature': device.overloadTemperature
                        }

    return None


"""
API Name: GetScannedSensorData
Returns the scanned data from the xBeacon advertisements of device with BLE address.
Returned values are:
    'lastScanTime': Most recent time that any advertisement packet was received from this device. Value is in seconds.
    'lastRealTimeUpdate': Most recent time than an xBeacon 1 packet was received
    'lastHistoryUpdate': Most recent time than an xBeacon 2 packet was received
    'deviceId': 4-byte ID of the device
    'deviceName': Value of the device name in the scan response packet. String.
    'productId': 2-byte value representing the product ID
    'intensity': intensity percentage. 0 - 100%
    'power': Power consumption (in Watts)
    'status': XIM status. b6:4 is temperature status (000 is normal), b3:2 is input voltage status (01 is normal), b1:0 is Vf Status (00 is normal)
    'temperature': PCB temperature, in degress Celcius.
    'vin': Input voltage (in volts).
    'rssi': Receive signal strength.
##    'powerCycles': Number of times the XIM has been power cycled
##    'ledCycles': Number of times the XIM's light has turned on
    'bootloaderMode': True if in the bootloader state
    'lastBootloaderUpdate': Most recent time that a bootloader mode packet was received
"""
def GetScannedSensorData(address):
    for device in peripheral_list:
        if(device.address == address):
            if(device.deviceType == DEVICE_TYPE_XSENSOR):
                return {'lastScanTime':device.lastScanTime, 'lastMotionUpdate':device.motionUpdateTime, 'lastLuxUpdate':device.luxUpdateTime,
                    'lastHistoryUpdate':device.historyUpdateTime,
                    'deviceId':device.scannedDeviceId,  'deviceName': device.deviceName, 'productId': device.scannedProductId,
                    'status':device.scannedStatus, 'vin': device.scannedVin, 'temperature': device.scannedTemperature,
                    'motion': device.scannedMotion, 'lux': device.scannedLux,
##                     'pcbTemperature': device.scannedPcbTemperature, 'vinRipple': device.scannedVinRipple, 'hours':device.scannedHours,
                    'rssi':device.scannedRssi,
##                    'powerCycles': device.scannedPowerCycles , 'ledCycles': device.scannedLedCycles,
                    'bootloaderMode': device.bootloaderMode, 'lastBootloaderUpdate': device.bootloaderModeUpdateTime,
                    'encryptedAdv': device.encryptedAdv,
                    'swVersion': device.swVersion, 'hwVersion': device.hwVersion, 'fwVersion': device.fwVersion,
                    }

    return None


def GetGroupMembers(address):
    for device in peripheral_list:
        if(device.address == address):
            return device.groups

"""
API Name: RequestRSSI
Requests the latest RSSI value for the given BLE address.
    address: 6-byte BLE address
    timeout: When greater than 0, this will wait until the RSSI value is retrieved.
            Otherwise if it is 0, then GetRSSI must be called.
"""
def RequestRSSI(address, timeout = -1):
    global pending_write
    value = None

    device = GetDeviceWithAddress(address)

    if(device and device.IsConnected()):
        start_time = time.time()
        while(pending_write and ((time.time() - start_time) < 0.2)):
            CheckActivity(ser)
##            Process()

        device.pcRssiValue = None

        logHandler.printLog ("Request Rssi for device {0}:".format(address))

        if(device.connection_handle != None):
            # Request the value from the RSSI value
            ble.send_command(ser, ble.ble_cmd_connection_get_rssi(device.connection_handle))
            SetBusyFlag()

            if(timeout > 0):
                start_time = time.time()
                while(time.time() - start_time < timeout):
                    Process()

                    value = device.pcRssiValue
                    if(value != None):
                        break

    return value

"""
API Name: GetRSSI
Retrieves the latest RSSI value for the given BLE address. Does not request a new value.
RequestRSSI must be sent at least once before calling this.
    address: 6-byte BLE address
"""
def GetRSSI(address):
    global peripheral_list

    for device in peripheral_list:
        if(device.address == address):
            return device.pcRssiValue
    return None


# ######################################
# Section: Connection - APIs
# ######################################
"""
API Name: Connect
Attempts to connect to the device with BLE address addressValue. Waits for a connection event until the timeout.
    addressValue: BLE address (6 bytes)
    timeout: Amount of time (in seconds) to wait for the connection to occur.
"""
def Connect(addressValue, timeout = -1):
    global pending_write, bgCentralState

    device = GetDeviceWithAddress(addressValue)

    isConnected = False
    connectionSuccess = False

    if(device):
        logHandler.printLog ("device.connectionState = {0}, device.connection_handle = {1}".format(device.connectionState, device.connection_handle))
        if(device.IsConnected()):
            isConnected = True
            connectionSuccess = True

        else:
            device.connectionSent = False
            start_time = time.time()

            logHandler.printLog("\n{0}: Before connect attempt to {1}. connection_handle: {2} connectionSent: {3}, bgCentralState: {4}, pending_write: {5}".format(time.time(), device.address, device.connection_handle, device.connectionSent, bgCentralState, pending_write))

            while(device.connectionSent == False and (time.time() - start_time) < DISCONNECT_TIMEOUT):

                Process()

                if(device.connection_handle == None) and (device.connectionSent == False) and (IsSystemBusy() == False) and (pending_write == False):
                    device.connectionState = STATE_CONNECTING
                    bgCentralState = CENTRAL_STATE_CONNECTING
                    device.connectionAttemptTime = time.time()
                    logHandler.printLog("\n{0}: Connect to {1}".format(time.time(), device.address))
                    if(device.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]):
                        ble.send_command(ser, ble.ble_cmd_gap_connect_direct(device.address, device.address_type, bleMinInterval, bleMaxInterval, bleConnTimeout, bleSlaveLatency))
                        SetBusyFlag()
                        connectionSuccess = True

            logHandler.printLog("\n{0}: After connect attempt to {1}. connection_handle: {2} connectionSent: {3}, bgCentralState: {4}, pending_write: {5}, connectionSent: {6}".format(time.time(), device.address, device.connection_handle, device.connectionSent, bgCentralState, pending_write, device.connectionSent))

            if(timeout > 0):
                if(device.connectionSent):
                    start_time = time.time()
                    waitTime = timeout
                    timeExtended = False
                    while(time.time() - start_time < waitTime):
                        Process()
                        if(device.IsConnected()):
                            isConnected = True
                            break
                        elif(device.IsDiscovering() and timeExtended == False):
                            logHandler.printLog("Extending WaitTime for address {0}".format(addressValue), True)
                            waitTime = time.time() - start_time + SERVICE_DISCOVERY_TIME
                            timeExtended = True

                    if(device.connectionState == STATE_CONNECTING):
                        ProcessFailedConnection(device)
                        connectionSuccess = False
                else:
                    ProcessFailedConnection(device)
                    connectionSuccess = False

        return (device.connectionState != STATE_STANDBY)
    else:
        return False

"""
API Name: Disconnect
Disconnects from the device with BLE address addressValue. Waits for a disconnection event until the timeout.
    addressValue: BLE address (6 bytes)
    timeout: Amount of time (in seconds) to wait for the disconnection to occur.
"""
def Disconnect(addressValue, timeout = None):
    global pending_write

    device = None
    if(addressValue == None):
        for deviceTest in peripheral_list:
            if (deviceTest.deviceType in [DEVICE_TYPE_XIM, DEVICE_TYPE_XSENSOR]) and deviceTest.IsConnected():
                device = deviceTest
                break
    else:
        device = GetDeviceWithAddress(addressValue)

    if(device):

        start_time = time.time()
        while(pending_write and ((time.time() - start_time) < 0.2)):
            Process()

        if(device.connectionState == STATE_CONNECTING):
            logHandler.printLog("{0}: Disconnect attempt while device {1} is trying to connect.".format(time.time(), device.address))

        elif(device.connection_handle != None):
            device.connectionState = STATE_DISCONNECTING
            device.disconnectTime = time.time()
            logHandler.printLog("{0}: Disconnect from {1}".format(time.time(), device.address))
            ble.send_command(ser, ble.ble_cmd_connection_disconnect(device.connection_handle))
            SetBusyFlag()

            if(timeout):
                start_time = time.time()
                while(time.time() - start_time < timeout):
##                    logHandler.printLog("{0}: device.connectionState {1}".format(time.time(), device.connectionState))
                    Process()
                    if(device.connectionState == STATE_STANDBY):
                        break

                if(device.connectionState == STATE_DISCONNECTING):
                    device.connectionState = STATE_STANDBY
##                    device.connection_handle = None
        else:
            logHandler.printLog("{0}: Device {1} is already disconnected. Go to STATE_STANDBY {1}".format(time.time(), device.address))
            device.connectionState = STATE_STANDBY


# ######################################
# Section: Attributes - APIs
# ######################################

# Device Information
"""
API Name: RequestModelNumber
Requests the model number for the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    If a value is received, it will return the value as a string.
    If the value is not received, it will return None.
"""
def RequestModelNumber(address, timeout):
    values = RequestData(address, uuid_dis_model_number_characteristic, timeout)
    if(values):
        return ''.join(chr(i) for i in values)
    return None

"""
API Name: RequestSerialNumber
Requests the serial number for the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    If a value is received, it will return the value as a string.
    If the value is not received, it will return None.
"""
def RequestSerialNumber(address, timeout):
    values = RequestData(address, uuid_dis_serial_number_characteristic, timeout)
    if(values):
        return ''.join(chr(i) for i in values)
    return None

"""
API Name: RequestHardwareRevision
Requests the hardware revision for the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    If a value is received, it will return the value as a string.
    If the value is not received, it will return None.
"""
def RequestHardwareRevision(address, timeout):
    values = RequestData(address, uuid_dis_hardware_rev_characteristic, timeout)
    if(values):
        return ''.join(chr(i) for i in values)
    return None

"""
API Name: RequestFirmwareRevision
Requests the firmware revision for the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    If a value is received, it will return the value as a string.
    If the value is not received, it will return None.
"""
def RequestFirmwareRevision(address, timeout):
    values = RequestData(address, uuid_dis_firmware_rev_characteristic, timeout)
    if(values):
        return ''.join(chr(i) for i in values)
    return None

"""
API Name: RequestSoftwareRevision
Requests the software revision for the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    If a value is received, it will return the value as a string.
    If the value is not received, it will return None.
"""
def RequestSoftwareRevision(address, timeout):
    values = RequestData(address, uuid_dis_software_rev_characteristic, timeout)
    if(values):
        device = GetDeviceWithAddress(address)
        strValue = ''.join(chr(i) for i in values)
        device.swVersion = strValue
        return strValue
    return None



def RequestTemperatureHistogram(address, timeout):
    values = RequestData(address, uuid_xim_temperature_histogram_characteristic, timeout)
    if(values):
        histogram = []
        i = 0
        bucketSize = 3
        while(i + bucketSize <= len(values)):
            histogram.append(ConvertListToInt(values[i:i + bucketSize]))
            i += bucketSize
        print ("Temperature histogram: {0}".format(histogram))
        return histogram


    return None

def RequestIntensityHistogram(address, timeout):
    values = RequestData(address, uuid_xim_intensity_histogram_characteristic, timeout)
    if(values):
        histogram = []
        i = 0
        bucketSize = 4
        while(i + bucketSize <= len(values)):
            histogram.append(ConvertListToInt(values[i:i + bucketSize]))
            i += bucketSize
        print ("Intensity histogram: {0}".format(histogram))
        return histogram

    return None



"""
API Name: SetLightLevel
Writes to the light level control characteristic of the given BLE address to set
    the light level.
    address: 6-byte BLE address list
    'light_level': New light intensity. Float between 0.0 - 100.0%
    'fade_time': Time to fade from the current intensity to the new intensity,
        in milliseconds (0 - 60000)
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.
"""
def SetLightLevel(address, values):

    txPacket = []
    intensity = ConvertIntensityToValue(values['light_level'])
    txPacket += ConvertIntToList(intensity, 2)
    txPacket += ConvertIntToList(values['fade_time'], 2)
    txPacket.append(int(round(values['override_time'] / 10)))
    if(values['lock_light_control']):
        txPacket.append(1)
    else:
        txPacket.append(0)
    TransmitPacket(address, txPacket, uuid_light_control_level_control_characteristic)

"""
API Name: StopFading
Writes to the light level control characteristic of the given BLE address to stop
    a fade in progress.
    address: 6-byte BLE address list
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.
"""
def StopFading(address, values):
    txPacket = ConvertIntToList(STOP_FADING_VALUE, 2)
    txPacket += [0, 0]
    txPacket.append(int(round(values['override_time'] / 10)))
    if(values['lock_light_control']):
        txPacket.append(1)
    else:
        txPacket.append(0)

    TransmitPacket(address, txPacket, uuid_light_control_level_control_characteristic)


"""
API Name: SensorControlMode
Writes to the light level control characteristic of the given BLE address to stop
    a fade in progress.
    address: 6-byte BLE address list
    'override_time': Duration (in seconds) that the XIM stays at light_level for
        before returning to the master-controlled intensity.
        When 0, it represents a master-controlled intensity, which the XIM will
        stay at until a new light control command is received.
        Re-sending this command will restart an already active override.
        The XIM's resolution is 10 second steps.
    'lock_light_control': When True, the XIM will only react to light level
        commands from this BLE address until the override expires.
        It is ignored if override_time is 0.
"""
def SensorControlMode(address, values):
    txPacket = ConvertIntToList(SENSOR_CONTROL_VALUE, 2)
    txPacket += [0, 0]
    txPacket.append(int(round(values['override_time'] / 10)))
    if(values['lock_light_control']):
        txPacket.append(1)
    else:
        txPacket.append(0)

    TransmitPacket(address, txPacket, uuid_light_control_level_control_characteristic)


"""
API Name: Indicate
Writes to the light indicate characteristic of the given BLE address to flash
    the light.
    address: 6-byte BLE address list
    'num_flashes': Number of flashes. 0 - 10
    'period': Period of the flash (in milliseconds). 0 - 25000.
            The XIM's resolution is 100 millisecond steps
    'high_level': Intensity of the high level of the flash. 0.0 - 100.0
    'low_level': Intensity of the high level of the flash. 0.0 - 100.0
"""
def Indicate(address, values):

    txPacket = []
    txPacket.append(values['num_flashes'])
    txPacket.append(int(values['period'] / 100))

    intensity = ConvertIntensityToValue(values['high_level'])
    txPacket += ConvertIntToList(intensity, 2)

    intensity = ConvertIntensityToValue(values['low_level'])
    txPacket += ConvertIntToList(intensity, 2)

    TransmitPacket(address, txPacket, uuid_light_control_indicate_characteristic)

def RequestSensorResponse(address, sensorId, timeout):
    if(sensorId == 1):
        values = RequestData(address, uuid_sensor2_response_characteristic, timeout)
    else:
        values = RequestData(address, uuid_sensor1_response_characteristic, timeout)
##    print "RequestSensorResponse len(values): {0} values: {1}".format(len(values), values)
    if(values and len(values) >= 23):
        address_type = values[0]
        address = values[1:7]
        componentValues = values[7:]

        sensorResponseDict =  {'address_type':address_type, 'address':address,
            'component_values':componentValues}

        return sensorResponseDict
    else:
        return None

def SetSensorResponse(address, sensorId, values):
##    logHandler.printLog( "SetSensorResponse values: {0}".format(values), True)
    # Fill address to 6 bytes long
    txPacket = [values['address_type']] + values['address'] + ([0] * (max(0, 6 - len(values['address'])))) + values['component_values']
    logHandler.printLog( "SetSensorResponse txPacket: {0}".format(txPacket))
    if(sensorId == 1):
        return TransmitPacket(address, txPacket, uuid_sensor2_response_characteristic)
    else:
        return TransmitPacket(address, txPacket, uuid_sensor1_response_characteristic)

def SetSensorGeneralConfiguration(address, values = {'sleep_time': 1000}):
    txPacket = ConvertIntToList(values['sleep_time'], 2)
    result = TransmitPacket(address, txPacket, uuid_sensor_general_characteristic)
    logHandler.printLog( "SetSensorConfiguration txPacket: {0}. Result {1}".format(txPacket, result), True)

def SetLuxConfiguration(address, values = {'adv_interval': 5000, 'burst_count': 2, 'burst_interval': 50, 'lux_delta_threshold': 10, 'lux_delta_min_interval': 500}):
    txPacket = ConvertIntToList(values['adv_interval'], 2) + [values['burst_count']] + ConvertIntToList(values['burst_interval'], 2) + ConvertIntToList(values['lux_delta_threshold'], 2) + ConvertIntToList(values['lux_delta_min_interval'], 2)
    result = TransmitPacket(address, txPacket, uuid_sensor_lux_characteristic)
    logHandler.printLog( "SetLuxConfiguration txPacket: {0}. Result {1}".format(txPacket, result), True)

def SetMotionConfiguration(address, values = {'sensitivity': 0, 'motion_burst_count': 2, 'motion_burst_interval': 50, 'motion_continue_interval': 5000, 'motion_timeout': 7000, 'absence_count': 1, 'absence_burst_count': 2, 'absence_burst_interval': 2}):
    txPacket = [values['sensitivity'], values['motion_burst_count']] + ConvertIntToList(values['motion_burst_interval'], 2) + ConvertIntToList(values['motion_continue_interval'], 2)
    txPacket += ConvertIntToList(values['motion_timeout'], 2) + [values['absence_count'], values['absence_burst_count']] + ConvertIntToList(values['absence_burst_interval'], 2)
    result = TransmitPacket(address, txPacket, uuid_sensor_motion_characteristic)
    logHandler.printLog( "SetMotionConfiguration txPacket: {0}. Result {1}".format(txPacket, result), True)


def EnableDaliResponse(address):
    device = GetDeviceWithAddress(address)
    if(device):
        try:
            swVersionValue = float(device.swVersion)
        except:
            swVersionValue = 0.076

        if(swVersionValue >= 0.075):
            tempHandle = GetCCCHandle(device, uuid_dali_response_characteristic)
        else:
            tempHandle = GetCCCHandle(device, uuid_dali_command_characteristic)
        if(tempHandle != None and device.connection_handle != None):
            start_time = time.time()
            while(pending_write and ((time.time() - start_time) < 0.2)):
                CheckActivity(ser)
            ble.send_command(ser, ble.ble_cmd_attclient_attribute_write(device.connection_handle, tempHandle, [0x02, 0x00]))
            SetBusyFlag()

def EnableBankDataResponse(address):
    device = GetDeviceWithAddress(address)
    if(device):
        try:
            swVersionValue = float(device.swVersion)
        except:
            swVersionValue = 0.076
        if(swVersionValue >= 0.075):
            tempHandle = GetCCCHandle(device, uuid_xim_memory_location_characteristic)
        else:
            tempHandle = GetCCCHandle(device, uuid_xim_memory_value_characteristic)
        if(tempHandle != None and device.connection_handle != None):
            start_time = time.time()
            while(pending_write and ((time.time() - start_time) < 0.2)):
                CheckActivity(ser)

            ble.send_command(ser, ble.ble_cmd_attclient_attribute_write(device.connection_handle, tempHandle, [0x02, 0x00]))
            SetBusyFlag()

def GetLocalNetworkConfiguration(networkIndex):
    if(networkIndex == NETWORK_TX):
        selectedIndex = selectedTxNetworkIndex
    else:
        selectedIndex = selectedRxNetworkIndex
    return {'id': networkConfigs[selectedIndex].id, 'key': networkConfigs[selectedIndex].key}

def SetLocalNetworkConfiguration(networkId, networkHeaderKey, txConfig, rxConfig):
    global selectedRxNetworkIndex, selectedTxNetworkIndex
    matchFound = False

    for networkIndex in [NETWORK_TX, NETWORK_RX]:
        if(networkIndex == NETWORK_TX):
            testKey = txConfig['key']
        else:
            testKey = rxConfig['key']

        for i, netConfig in enumerate(networkConfigs):
            if(netConfig.id == networkId) and (netConfig.key == testKey):
                netConfig.headerKey = networkHeaderKey
                matchFound = True
                newIndex = i
                break

        if(matchFound == False):
            networkConfigs.append(NetworkConfig(networkId, networkHeaderKey, testKey, 0))
            newIndex = len(networkConfigs) - 1

        if(networkIndex == NETWORK_TX):
            selectedTxNetworkIndex = newIndex
        else:
            selectedRxNetworkIndex = newIndex

    UpdateNetworkConfigFile()

def IsEncryptedAdvEnabled(destination):

    if(networkConfigs[selectedTxNetworkIndex].key == NETWORK_KEY_NONE):
        return False
    else:
        devices = GetDevicesInGroup(destination)
        encryptedDevices = GetDevicesFromListWithField(devices, "encryptedAdv", True)
        return (len(encryptedDevices) > 0)

def IsEncryptedHeaderEnabled(destination):
    if(networkConfigs[selectedTxNetworkIndex].key == NETWORK_KEY_NONE):
        return False
    else:
        devices = GetDevicesInGroup(destination)
        encryptedDevices = GetDevicesFromListWithField(devices, "hasEncryptedHeader", True)
        logHandler.printLog( "IsEncryptedHeaderEnabled: {0} vs {1}".format(devices, encryptedDevices))
        # Every device must have an encrypted header
        return (len(encryptedDevices) > 0) and (len(encryptedDevices) == len(devices))

##    return (networkConfigs[selectedTxNetworkIndex].key != NETWORK_KEY_NONE)


def RequestNetworkConfiguration(address, networkIndex, timeout):
    # Directions are swapped because the XIM transmit network is received by the local receive network
    if(networkIndex == NETWORK_TX):
        netIndex = selectedRxNetworkIndex
    else:
        netIndex = selectedTxNetworkIndex
    return {'id': networkConfigs[netIndex].id, 'key': networkConfigs[netIndex].key}


def UserLogin(address, timeout = 1.0):
    device = GetDeviceWithAddress(address)
    if(device and device.encryptedAdv):
        txPacket = networkConfigs[selectedTxNetworkIndex].id + [1]
        result = TransmitPacket(address, txPacket, uuid_access_network_select_characteristic)
        logHandler.printLog("Network Select result: {0}".format(result), True)
        txPacket = networkConfigs[selectedTxNetworkIndex].key

        # Older revs except the key to be in bytes 1:17
        if(float(device.swVersion) <= 0.094):
            txPacket = [0] + txPacket
        result = TransmitPacket(address, txPacket, uuid_access_user_login_characteristic)
        logHandler.printLog("User Login result: {0}".format(result), True)


adminKeyIndex = 0
def AdminLogin(address, timeout = 1.0):
    global adminKeyIndex



##    print "adminKey: {0}".format(adminKey)

    result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
    logHandler.printLog("AdminLogin result: {0}".format(result), True)

    if(result == False):
##        if(adminKeyIndex < 16):
##            adminKey = ([0xFF] * adminKeyIndex) + [0x00] * (16 - adminKeyIndex)
##        else:
##            adminKey = ([0x00] * (adminKeyIndex - 16)) + [0xFF] * (32 - adminKeyIndex)


##        adminKey = ([0xFF] * adminKeyIndex) + [0x00] * (16 - adminKeyIndex)
##        result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
##        if(result == False):
##            adminKey = ([0x00] * adminKeyIndex) + [0xFF] * (16 - adminKeyIndex)
##            result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
##
##        if(result):
##            logHandler.printLog("\n\nAdminLogin Recovered  with key {0}\n\n".format(adminKey), True)
##            adminKey = [0] * 16
##            result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
##            logHandler.printLog("AdminLogin re-assignment result: {0}".format(result), True)
##
##
##        if(adminKeyIndex < 16):
##            adminKeyIndex += 1
##        else:
##            adminKeyIndex = 0

        testAdminKey = [0] * 3 + [0xFF] * 13
        result = TransmitPacket(address, testAdminKey, uuid_access_admin_login_characteristic)

        if(result == False):
            testAdminKey = [0xFF] * 9 + [0] * 7
            result = TransmitPacket(address, testAdminKey, uuid_access_admin_login_characteristic)
##        for i in range(16):
##            adminKey = [0xFF] * i + [0] * (16-i)
##            result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
##            logHandler.printLog("AdminLogin retry {1} result: {0}".format(result, i), True)
##            if(result):
##                break
##
##        if(result == False):
##            for i in range(16):
##                adminKey = [0x00] * i + [0xFF] * (16-i)
##                result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
##                logHandler.printLog("AdminLogin retry {1} result: {0}".format(result, i + 16), True)
##                if(result):
##                    break

        if(result):
            logHandler.printLog("\n\nAdminLogin Recovered  with key {0}\n\n".format(adminKey), True)
##            adminKey = [0] * 16
            result = TransmitPacket(address, adminKey, uuid_access_admin_login_characteristic)
            logHandler.printLog("AdminLogin re-assignment result: {0}".format(result), True)


def OemLogin(address, timeout = 1.0):
    result = TransmitPacket(address, oemKey, uuid_access_oem_login_characteristic)
    logHandler.printLog("OemLogin result: {0}".format(result), True)
    return result


def SetNetworkConfiguration(address, networkId, networkHeaderKey, accessConfigList, timeout):

    device = GetDeviceWithAddress(address)


    if(device):
        try:
            swVersionValue = float(device.swVersion)
        except:
            swVersionValue = 0.084
        if(swVersionValue >= 0.075):
##            AdminLogin(address, timeout)

            if(swVersionValue >= 0.084):
                if(networkId == ([0] * NETWORK_ID_LENGTH)):
                    txPacket = networkId
                    result = TransmitPacket(address, txPacket, uuid_access_network_list_characteristic)
                    print( "Clear Network Config Result {1} for packet {0}".format(txPacket, result))
                else:
                    txPacket = networkId + networkHeaderKey
                    for networkIndex, accessConfig in enumerate(accessConfigList):
                        txPacket += accessConfig['key']
                        txPacket += ConvertIntToList(accessConfig['permissions'], 2)

                    result = TransmitPacket(address, txPacket, uuid_access_network_config_characteristic)
                    print ("Set Network Config Result {1} for packet {0}".format(txPacket, result))
            else:
                networkList = RequestData(address, uuid_access_network_list_characteristic, timeout)
                print ("Network List Read Values: {0}".format(networkList))
                i = 0
                if(networkList):
                    while(i + NETWORK_ID_LENGTH < len(networkList)):
                        if(networkList[i: i + NETWORK_ID_LENGTH] in [[0] * NETWORK_ID_LENGTH, networkId]):
                            print ("Found for i = {0}".format(i))
                            break
                        i += NETWORK_ID_LENGTH
                    networkList[i: i + NETWORK_ID_LENGTH] = networkId
                    print ("Network List Write values: {0}".format(networkList))

                    result = TransmitPacket(address, networkList, uuid_access_network_list_characteristic)

                    networkList = RequestData(address, uuid_access_network_list_characteristic, timeout)
                    print ("Network List Read Values 2: {0}".format(networkList))

                    if(swVersionValue >= 0.080):
                        # The access ID is irrelevant for setting the network header key
                        txPacket = networkId + [0]
                        result = TransmitPacket(address, txPacket, uuid_access_network_select_characteristic)
                        print ("Network Select result: {0} for {1}".format(result, txPacket))
                        print ("Set networkHeaderKey {0}".format(networkHeaderKey))
                        result = TransmitPacket(address, networkHeaderKey, uuid_access_network_header_key_characteristic)

                    for networkIndex, accessConfig in enumerate(accessConfigList):
                        txPacket = networkId + [networkIndex]
                        result = TransmitPacket(address, txPacket, uuid_access_network_select_characteristic)
                        print ("Network Select result: {0} for {1}".format(result, txPacket))


                        txPacket = accessConfig['key']
                        print ("Key txPacket: {0}".format(txPacket))
                        result = TransmitPacket(address, txPacket, uuid_access_user_login_characteristic)
                        print ("Key Write result: {0}".format(result))

                        txPacket = [accessConfig['permissions']]
                        print ("Permissions txPacket: {0}".format(txPacket))
                        result = TransmitPacket(address, txPacket, uuid_access_config_characteristic)
                        print ("Access Config result: {0}".format(result))

        else:
            return False





"""
API Name: RequestLightSetup
Reads from the light setup characteristic of the given BLE address.
    address: 6-byte BLE address list
    isLittleEndian: For BLE XIM software version 0.042 and older, the endianness
        of the multi-byte fields is swapped.
Returns:
    'max_level': Maximum allowed intensity. Float between 0.0 - 100.0%
    'min_level': Minimum allowed intensity, not including off. Float between
        0.1 - 100.0%
    'power_on_level': Intensity when XIM is powered on. Float between 0.0 - 100.0%
        or string 'Last', which means that the XIM will return to the last
        commanded intensity before power down.
    'power_on_fade_time': Time (in milliseconds) to fade to the power on level
        when XIM is powered on. Float between 0 - 6500000.
    'power_on_start_time': Time (in milliseconds) to start fading to the power on
        level when XIM is powered on. Float between 0 - 2500.
    'dimming_curve': When 1, linear smoothing is enabled, 0 is logarithmic.
    'fade_smoothing': When 1, fade smoothing is enabled, which means that any
        fade will use a smoothing function, which slows down the fade as it
        approaches the new intensity.
"""
def RequestLightSetup(address, timeout, isLittleEndian = False):
    device = GetDeviceWithAddress(address)
    if(device and device.swVersion):
        isLittleEndian = (float(device.swVersion) >= 0.043)

    values = RequestData(address, uuid_light_control_setup_characteristic, timeout)
##    print "RequestLightSetup : {0}".format(values)
    if(values and len(values) >= 9):
        isValid = True
        maxLevel = ConvertValueToIntensity(ConvertListToInt(values[0:2], isLittleEndian))
        minLevel = ConvertValueToIntensity(ConvertListToInt(values[2:4], isLittleEndian))
        powerOnLevel = ConvertListToInt(values[4:6], isLittleEndian)
        if(device and float(device.swVersion) >= 0.091):
            if(len(values) >= 10):
                powerOnStartTime = values[6] * 10
                powerOnFadeTime = ConvertListToInt(values[7:9], isLittleEndian) * 100
                fadeSmoothing = (values[9] >> 2) & 0x03
                dimmingCurve = values[9] & 0x01
            else:
                isValid = False
        else:
            powerOnFadeTime = ConvertListToInt(values[6:8], isLittleEndian)
            powerOnStartTime = 600
            fadeSmoothing = values[8]
            dimmingCurve = None

        if(isValid):
            if(powerOnLevel == POWER_ON_LEVEL_LAST_VALUE):
                powerOnLevel = 'Last'
            elif(powerOnLevel <= MAX_INTENSITY):
                powerOnLevel =  ConvertValueToIntensity(powerOnLevel)
            else:
                powerOnLevel = 'Other'

            lightSetupDict =  {'max_level':maxLevel, 'min_level':minLevel,
                'power_on_level':powerOnLevel, 'power_on_fade_time':powerOnFadeTime,
                'power_on_start_time': powerOnStartTime,
                'fade_smoothing':fadeSmoothing, 'dimming_curve':dimmingCurve}
        else:
            lightSetupDict = None

##        print "lightSetupDict: {0}".format(lightSetupDict)

        return lightSetupDict
    else:
        return None

"""
API Name: SetLightSetup
Writes to the light setup characteristic of the given BLE address.
    address: 6-byte BLE address list
    'max_level': Maximum allowed intensity. Float between 0.0 - 100.0%
    'min_level': Minimum allowed intensity, not including off. Float between
        0.1 - 100.0%
    'power_on_level': Intensity when XIM is powered on. Float between 0.0 - 100.0%
        or string 'Last', which means that the XIM will return to the last
        commanded intensity before power down.
    'power_on_fade_time': Time (in milliseconds) to fade to the power on level
        when XIM is powered on. Float between 0 - 6500000.
    'power_on_start_time': Time (in milliseconds) to start fading to the power on
        level when XIM is powered on. Float between 0 - 2500.
    'dimming_curve': When 1, linear smoothing is enabled, 0 is logarithmic.
    'fade_smoothing': When 1, fade smoothing is enabled, which means that any
        fade will use a smoothing function, which slows down the fade as it
        approaches the new intensity.
    'fade_smoothing': When 1, fade smoothing is enabled, which means that any
        fade will use a smoothing function, which slows down the fade as it
        approaches the new intensity.

"""
def SetLightSetup(address, values):
    txPacket = []
    txPacket += ConvertIntToList(ConvertIntensityToValue(values['max_level']), 2)
    txPacket += ConvertIntToList(ConvertIntensityToValue(values['min_level']), 2)

    if(values['power_on_level'] == 'Last'):
        txPacket += ConvertIntToList(POWER_ON_LEVEL_LAST_VALUE, 2)
    elif(values['power_on_level'] == 'Other'):
        txPacket += ConvertIntToList(POWER_ON_LEVEL_USE_OTHER, 2)
    else:
        txPacket += ConvertIntToList(ConvertIntensityToValue(values['power_on_level']), 2)

    device = GetDeviceWithAddress(address)
    if(device and float(device.swVersion) >= 0.091):
        txPacket.append(int(round(values['power_on_start_time'] / 10)))
        txPacket += ConvertIntToList(int(round(values['power_on_fade_time'] / 100)), 2)
        fadeMode = (values['fade_smoothing'] & 0x03) << 2
        fadeMode |= (values['dimming_curve'] & 0x01)
        txPacket.append(fadeMode)
    else:
        txPacket += ConvertIntToList(values['power_on_fade_time'], 2)
        txPacket.append (values['fade_smoothing'])
    isSuccess = TransmitPacket(address, txPacket, uuid_light_control_setup_characteristic)

    return isSuccess




def RequestBleScenesConfig(address, timeout):
##    device = GetDeviceWithAddress(address)
    scenes = []
    values = RequestData(address, uuid_light_control_scenes_characteristic, timeout)
##    print "RequestBleScenesConfig : {0}".format(values)
    if(values and len(values) >= (NUM_BLE_SCENES * BLE_SCENE_SIZE)):
        for i in range(0, ((NUM_BLE_SCENES - 1) * BLE_SCENE_SIZE) + 1, BLE_SCENE_SIZE):
            sceneNumber = ConvertListToInt(values[i: i + 2])

            intensityValue = ConvertListToInt(values[i + 2: i + 4])
            if(intensityValue > MAX_INTENSITY):
                intensityValue = MAX_INTENSITY
            intensity = ConvertValueToIntensity(intensityValue)

            scenes.append({'sceneNumber': sceneNumber, 'intensity': intensity, 'fadeTime': fadeMap[values[i + 4]], 'delayTime': fadeMap[values[i + 5]] / 10})
##            print "SI {1}: {0}".format(scenes[-1], len(scenes))
        return scenes
    else:
        return None

def SetBleScenesConfig(address, scenes):
    isSuccess = False

    if(len(scenes) >= NUM_BLE_SCENES):
        values = []

        for i in range(NUM_BLE_SCENES):
            scene = scenes[i]

            values += ConvertIntToList(scene['sceneNumber'], 2)

            if(scene['intensity'] > MAX_INTENSITY):
                scene['intensity'] = MAX_INTENSITY

            values += ConvertIntToList(ConvertIntensityToValue(scene['intensity']), 2)

            values.append(TableIndexLookup(fadeMap, scene['fadeTime']))
            values.append(TableIndexLookup(fadeMap, scene['delayTime'] * 10))


        isSuccess = TransmitPacket(address, values, uuid_light_control_scenes_characteristic)
        print ("SetBleScenesConfig : {0} for {1}".format(isSuccess, values))
    return isSuccess


# Supported by V0.093+
def RequestDaliAddressConfig(address, timeout):
##    device = GetDeviceWithAddress(address)

    values = RequestData(address, uuid_dali_address_config_characteristic, timeout)
##    print "RequestDaliAddressConfig : {0}".format(values)
    if(values and len(values) == 3):
        valuesDict = {'address':values[0], 'groups':values[1] + values[2] * 256}
        print ("valuesDict: {0}".format(valuesDict))
        return valuesDict
    else:
        return None

def SetDaliAddressConfig(address, values):
    txPacket =[values['address'], values['groups'] & 0xFF, values['groups'] / 256]
    isSuccess = TransmitPacket(address, txPacket, uuid_dali_address_config_characteristic)
##    print "SetDaliAddressConfig : {0}".format(isSuccess)
    return isSuccess

def RequestDaliScenesConfig(address, timeout):
##    device = GetDeviceWithAddress(address)

    values = RequestData(address, uuid_dali_scenes_characteristic, timeout)
    print ("RequestDaliScenesConfig : {0}".format(values))
    if(values and len(values) == 16):
        return values
    else:
        return None

def SetDaliScenesConfig(address, scenes):
    isSuccess = TransmitPacket(address, scenes, uuid_dali_scenes_characteristic)
    print ("SetDaliScenesConfig : {0}".format(isSuccess))
    return isSuccess

def RequestDaliLightSetup(address, timeout):
    device = GetDeviceWithAddress(address)

    values = RequestData(address, uuid_dali_light_config_characteristic, timeout)
    print ("RequestDaliLightSetup : {0}".format(values))
    if(values and len(values) >= 8):
        lightSetupDict = {'max_level':values[0], 'min_level':values[1],
                'power_on_level':values[2], 'system_failure_level':values[3],
                'dimming_curve':values[4], 'fade_rate':values[5],
                'fade_time':values[6], 'fast_fade_time':values[7]}
        print ("lightSetupDict: {0}".format(lightSetupDict))
        return lightSetupDict

    else:
        return None

def SetDaliLightSetup(address, values):

    txPacket =[values['max_level'], values['min_level'], values['power_on_level'], values['system_failure_level'],
                values['dimming_curve'], values['fade_rate'], values['fade_time'], values['fast_fade_time']]
    isSuccess = TransmitPacket(address, txPacket, uuid_dali_light_config_characteristic)
    return isSuccess


def Request1_10VLightSetup(address, timeout):
    device = GetDeviceWithAddress(address)
    values = RequestData(address, uuid_dim_1_10V_config_characteristic, timeout)
    print ("Request1_10VLightSetup : {0}".format(values))
    if(values and len(values) >= 4):
        lightSetupDict = {'modes': values[0], 'min_level': ConvertValueToIntensity(ConvertListToInt(values[1:3])),
                'warmup_time':values[3] * 100}
        print ("lightSetupDict: {0}".format(lightSetupDict))
        return lightSetupDict

    else:
        return None

def Set1_10VLightSetup(address, values):

    txPacket =[values['modes']] + ConvertIntToList(ConvertIntensityToValue(values['min_level']), 2) + [min(255, int(round(values['warmup_time'] / 100.0)))]
    isSuccess = TransmitPacket(address, txPacket, uuid_dim_1_10V_config_characteristic)
    return isSuccess

def GetStoredGroups(address):
    device = GetDeviceWithAddress(address)
    if(device.receivedAllGroups):
        return device.groups[:]
    else:
        return None

def RequestGroupMembership(address, timeout):
    groupList = []
    values = RequestData(address, uuid_group_membership_characteristic, timeout)
    print ("values: {0}".format(values))
    for i in range(0, len(values), 2):
        groupList.append(values[i] + values[i + 1] * 256)

    device = GetDeviceWithAddress(address)
    if(len(groupList) > 0) and (device):
        UpdateGroupMembership(device, groupList)

    return groupList

def SetGroupMembership(address, values):
    txPacket = []
    for value in values:
        txPacket += ConvertIntToList(value, 2)

    isSuccess = TransmitPacket(address, txPacket, uuid_group_membership_characteristic)

    device = GetDeviceWithAddress(address)
    if(isSuccess) and (device):
        UpdateGroupMembership(device, values)


def UpdateGroupMembership(device, groupList):
    device.groups = []
    for group in groupList:
        if(group != GROUP_MEMBER_UNASSIGNED):
            device.groups.append(group)

    device.receivedAllGroups = True

    logHandler.printLog("Updated group membership to {0}".format(device.groups), True)





"""
API Name: SetDeviceId
Writes to the Device ID characteristic of the given BLE address.
    address: 6-byte BLE address list
    deviceId: logical address of the device
Returns:
    True if the write was successful
"""
def SetDeviceId(address, deviceId):
    if(len(deviceId) == 1):
        if(deviceId[0] > 0xBFFF):
            return False
        else:
            txPacket = [1, deviceId[0] % 256, deviceId[0] / 256]
    elif(len(deviceId) == 3):
        if(deviceId == ([255] * 3)):
            return False
        else:
            txPacket = [0] + deviceId
    elif(len(deviceId) == 4):
        txPacket = deviceId
    else:
        return False

    logHandler.printLog("Transmit Set ID packet {0} to address {1} at UUID {2}".format(deviceId, address, uuid_device_id_characteristic))
    result = TransmitPacket(address, txPacket, uuid_device_id_characteristic)
    return result

"""
API Name: RequestXimRSSI
Requests the XIM's measured RSSI from the RSSI characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The RSSI value if the read was successful, None otherwise
"""
def RequestXimRSSI(address, timeout):
    values = RequestData(address, uuid_rssi_characteristic, timeout)
    if(values and len(values) > 0):
        ximRssi = values[0]
        if(ximRssi > 127):
            ximRssi = ximRssi - 256
        return ximRssi
    else:
        return None

"""
API Name: RequestTxPower
Requests the XIM's transmitted power level from the TX Power characteristic of
    the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The transmit power level if the read was successful, None otherwise.
    0: -18dBm, 1: -12dBm, 2: -6dBm, 3: -3dBm, 4: -2dBm, 5: -1dBm, 6: 0dBm , 7: 3dBm
"""
def RequestTxPower(address, timeout):
    return RequestData(address, uuid_tx_power_characteristic, timeout)

"""
API Name: SetTxPower
Writes the power level to the TX Power characteristic  of the given BLE address.
    address: 6-byte BLE address list
    txPower: 0: -18dBm, 1: -12dBm, 2: -6dBm, 3: -3dBm, 4: -2dBm, 5: -1dBm,
        6: 0dBm , 7: 3dBm
"""
def SetTxPower(address, txPower):
    txPacket = [txPower]
    TransmitPacket(address, txPacket, uuid_tx_power_characteristic)

"""
API Name: RequestRxGain
Requests the XIM's receive gain level from the RX Gain characteristic of
    the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The receive gain level if the read was successful, None otherwise.
    0: Normal Gain, 1: High Gain
"""
def RequestRxGain(address, timeout):
    return RequestData(address, uuid_rx_gain_characteristic, timeout)

"""
API Name: SetRxGain
Writes the gain level to the RX Gain characteristic  of the given BLE address.
    address: 6-byte BLE address list
    rxGain: 0: Normal Gain, 1: High Gain
"""
def SetRxGain(address, rxGain):
    txPacket = [rxGain]
    TransmitPacket(address, txPacket, uuid_rx_gain_characteristic)

"""
API Name: RequestAdvertisementSettings
Requests the XIM's advertisement settings from the Advertisement Settings
    characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The following values if the read was successful, None otherwise.
    'xbeacon1Interval': xBeacon 1 advertisement interval (in milliseconds)
    'xbeacon2Interval': xBeacon 2 advertisement interval (in milliseconds)
    'connectable': When True, then by default, the XIM can be connected to. When
        False, the XIM must received a Set Connectable advertisement packet
        in order to be connectable (See EnableConnections API).
"""
def RequestAdvertisementSettings(address, timeout):
    response = RequestData(address, uuid_advertisement_settings_characteristic, timeout)
    if(response and len(response) >= 4):
        xbeacon1Interval = ConvertListToInt(response[0:2])
        xbeacon2Interval = ConvertListToInt(response[2:4])
        return {'xbeacon1Interval':xbeacon1Interval, 'xbeacon2Interval':xbeacon2Interval, 'connectable':(response[4] == 0)}
    return None

"""
API Name: SetAdvertisementSettings
Writes the XIM's advertisement settings to the Advertisement Settings
    characteristic of the given BLE address.
    address: 6-byte BLE address list
    'xbeacon1Interval': xBeacon 1 advertisement interval (in milliseconds)
    'xbeacon2Interval': xBeacon 2 advertisement interval (in milliseconds)
    'connectable': When True, then by default, the XIM can be connected to. When
        False, the XIM must received a Set Connectable advertisement packet
        in order to be connectable (See EnableConnections API).
"""
def SetAdvertisementSettings(address, values):
    if(values['connectable']):
        connectableByte = 0
    else:
        connectableByte = 1
    txPacket = []
    txPacket += ConvertIntToList(values['xbeacon1Interval'], 2)
    txPacket += ConvertIntToList(values['xbeacon2Interval'], 2)
    txPacket.append(connectableByte)
    TransmitPacket(address, txPacket, uuid_advertisement_settings_characteristic)


# iBeacon
"""
API Name: RequestIBeaconUUID
Requests the iBeacon Profile UUID from the iBeacon UUID characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The 16-byte UUID as a list if the read was successful, None otherwise.
"""
def RequestIBeaconUUID(address, timeout):
    return RequestData(address, uuid_iBeacon_uuid_characteristic, timeout)

"""
API Name: SetIBeaconUUID
Writes the iBeacon Profile UUID to the iBeacon UUID characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    uuid: the 16-byte UUID as a list
"""
def SetIBeaconUUID(address, uuid):
    txPacket = uuid
    TransmitPacket(address, txPacket, uuid_iBeacon_uuid_characteristic)

"""
API Name: RequestIBeaconMajor
Requests the iBeacon Major ID from the iBeacon Major characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The major ID (integer) if the read was successful, None otherwise.
"""
def RequestIBeaconMajor(address, timeout):
    values = RequestData(address, uuid_iBeacon_major_characteristic, timeout)
    if(values != None):
        # iBeacon major ID is advertised as big-endian
        return ConvertListToInt(values[0:2], False)
    return None

"""
API Name: SetIBeaconMajor
Writes the iBeacon Major ID to the iBeacon Major characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    value: the major ID
"""
def SetIBeaconMajor(address, value):
    # iBeacon major ID is advertised as big-endian
    txPacket = ConvertIntToList(value, 2, False)
    TransmitPacket(address, txPacket, uuid_iBeacon_major_characteristic)

"""
API Name: RequestIBeaconMinor
Requests the iBeacon Minor ID from the iBeacon Minor characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The minor ID (integer) if the read was successful, None otherwise.
"""
def RequestIBeaconMinor(address, timeout):
    values = RequestData(address, uuid_iBeacon_minor_characteristic, timeout)
    if(values != None):
        # iBeacon minor ID is advertised as big-endian
        return ConvertListToInt(values[0:2], False)
    return None

"""
API Name: SetIBeaconMinor
Writes the iBeacon Minor ID to the iBeacon Minor characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    value: the minor ID
"""
def SetIBeaconMinor(address, value):
    # iBeacon minor ID is advertised as big-endian
    txPacket = ConvertIntToList(value, 2, False)
    TransmitPacket(address, txPacket, uuid_iBeacon_minor_characteristic)

"""
API Name: RequestIBeaconMeasuredPower
Requests the iBeacon Measured Power from the iBeacon Major characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The power in dBm (integer) if the read was successful, None otherwise.
"""
def RequestIBeaconMeasuredPower(address, timeout):
    values = RequestData(address, uuid_iBeacon_measured_power_characteristic, timeout)
    if(values != None):
        value = values[0]
        if(value > 127):
            value = value - 256
        return value
    return None

"""
API Name: SetIBeaconMeasuredPower
Writes the iBeacon Minor ID to the iBeacon Minor characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    value: the power, in dBm (integer)
"""
def SetIBeaconMeasuredPower(address, value):
    if(value < 0):
        value += 256
    txPacket = [value]
    TransmitPacket(address, txPacket, uuid_iBeacon_measured_power_characteristic)

"""
API Name: RequestIBeaconPeriod
Requests the iBeacon Period from the iBeacon Period characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The period in milliseconds (integer) if the read was successful, None otherwise.
"""
def RequestIBeaconPeriod(address, timeout):
    values = RequestData(address, uuid_iBeacon_period_characteristic, timeout)
    if(values and len(values) == 2):
        return ConvertListToInt(values[0:2])
    else:
        return None

"""
API Name: SetIBeaconPeriod
Writes the iBeacon Period to the iBeacon Period characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    value: The period in milliseconds (integer)
"""
def SetIBeaconPeriod(address, value):
    txPacket = ConvertIntToList(value, 2)
    TransmitPacket(address, txPacket, uuid_iBeacon_period_characteristic)


# Eddystone - URL
"""
API Name: RequestUriBeaconURI
Requests the Eddystone-URL URI from the Eddystone URI characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The URL as a string, None otherwise.
"""
def RequestUriBeaconURI(address, timeout):
    uriBytes = RequestData(address, uuid_uriBeacon_uri_data_characteristic, timeout)

    logHandler.printLog( "uriBytes = {0}".format(uriBytes), True)
    if(uriBytes):
        if(len(uriBytes) > 0 and uriBytes[0] < len(EDDYSTONE_URI_PREFIXES)):
            uriString = EDDYSTONE_URI_PREFIXES[uriBytes[0]]
        else:
            uriString = chr(uriBytes[0])

        for uriByte in uriBytes[1:]:
            if(uriByte < len(EDDYSTONE_URI_SUFFIXES)):
                uriString += EDDYSTONE_URI_SUFFIXES[uriByte]
            else:
                uriString += chr(uriByte)

##        logHandler.printLog( "uriString = {0}".format(uriString), True)
        return uriString
    return None

"""
API Name: SetUriBeaconURI
Writes the Eddystone-URL URI to the Eddystone URI characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    uriString: the URI (string)
"""
def SetUriBeaconURI(address, uriString):
    uriBytes = []
    uriByteIndex = 0
    if(len(uriString) > 0):
        for i, prefix in enumerate(EDDYSTONE_URI_PREFIXES):
            if(uriString[uriByteIndex:uriByteIndex + len(prefix)] == prefix):
                logHandler.printLog("Found prefix match {0}".format(uriString), True)
                uriBytes.append(i)
                uriByteIndex += len(prefix)
                break

        while(uriByteIndex < len(uriString)):
            suffixFound = False
            for i, suffix in enumerate(EDDYSTONE_URI_SUFFIXES):
                if(uriString[uriByteIndex:uriByteIndex + len(suffix)] == suffix):
                    logHandler.printLog("Found suffix match {0}".format(uriString), True)
                    uriBytes.append(i)
                    uriByteIndex += len(suffix)
                    suffixFound = True
                    break
            if(suffixFound == False):
                uriBytes.append(ord(uriString[uriByteIndex]))
                uriByteIndex += 1

        # Remove trailing spaces
        while(True):
            if(uriBytes[-1] == ord(' ')):
                uriBytes.pop(-1)
            else:
                break

##    logHandler.printLog( "uriBytes = {0}".format(uriBytes), True)

    TransmitPacket(address, uriBytes, uuid_uriBeacon_uri_data_characteristic)


"""
API Name: RequestUriBeaconFlags
Requests the Eddystone-URL Flags from the Eddystone Flags characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The flags as an integer, None otherwise.
"""
def RequestUriBeaconFlags(address, timeout):
    response = RequestData(address, uuid_uriBeacon_flags_characteristic, timeout)
    if(response and len(response) == 1):
        return response[0]
    return None

"""
API Name: SetUriBeaconFlags
Writes the Eddystone-URL URI to the Eddystone URI characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    flags: the flags (integer)
"""
def SetUriBeaconFlags(address, flags):
    txPacket = [flags]
    TransmitPacket(address, txPacket, uuid_uriBeacon_flags_characteristic)


"""
API Name: RequestUriBeaconTxPowerMode
Requests the Eddystone-URL Tx Power Mode from the Eddystone Tx Power Mode characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The power mode as an integer, None otherwise.
    0 = Lowest, 1 = Low, 2 = Medium, 3 = High
"""
def RequestUriBeaconTxPowerMode(address, timeout):
    response = RequestData(address, uuid_uriBeacon_tx_power_mode_characteristic, timeout)
    if(response and len(response) == 1):
        return response[0]
    return None

"""
API Name: SetUriBeaconTxPowerMode
Writes the Eddystone-URL URI to the Eddystone URI characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    value: The power mode as an integer. 0 = Lowest, 1 = Low, 2 = Medium, 3 = High
"""
def SetUriBeaconTxPowerMode(address, value):
    txPacket = [value]
    TransmitPacket(address, txPacket, uuid_uriBeacon_tx_power_mode_characteristic)


"""
API Name: RequestUriBeaconTxPowerLevels
Requests the Eddystone-URL Tx Power Levels from the Eddystone Tx Power Levels characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The power levels as a 4-element list of integers, representing the value in dBm for
    each Tx Power mode.
"""
def RequestUriBeaconTxPowerLevels(address, timeout):
    response = RequestData(address, uuid_uriBeacon_tx_power_levels_characteristic, timeout)
    if(response and len(response) == 4):
        return response
    return None

"""
API Name: SetUriBeaconTxPowerLevels
Writes the Eddystone-URL Tx Power Levels to the Eddystone Tx Power Levels characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    values: The power levels as a 4-element list of integers, representing the value
    in dBm for each Tx Power mode.
"""
def SetUriBeaconTxPowerLevels(address, values):
    txPacket = values
    TransmitPacket(address, txPacket, uuid_uriBeacon_tx_power_levels_characteristic)

"""
API Name: RequestUriBeaconPeriod
Requests the Eddystone-URL Period from the Eddystone-URL Period characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The period in milliseconds (integer) if the read was successful, None otherwise.
"""
def RequestUriBeaconPeriod(address, timeout):
    response = RequestData(address, uuid_uriBeacon_period_characteristic, timeout)
    if(response and len(response) == 2):
        return ConvertListToInt(response[0:2])
    return None

"""
API Name: SetUriBeaconPeriod
Writes the Eddystone-URL Period to the Eddystone-URL Period characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    value: The period in milliseconds (integer)
"""
def SetUriBeaconPeriod(address, value):
    txPacket = ConvertIntToList(value, 2)
    TransmitPacket(address, txPacket, uuid_uriBeacon_period_characteristic)


# AltBeacon
"""
API Name: RequestAltBeaconCompanyId
Requests the AltBeacon company ID from the AltBeacon Company ID characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The company ID as a 2-element list of integers (each 0-255)
"""
def RequestAltBeaconCompanyId(address, timeout):
    return RequestData(address, uuid_altBeacon_company_id_characteristic, timeout)

"""
API Name: SetAltBeaconCompanyId
Writes the AltBeacon company ID to the AltBeacon Company ID characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    uuid: The company ID as a 2-element list of integers (each 0-255)
"""
def SetAltBeaconCompanyId(address, uuid):
    txPacket = uuid
    TransmitPacket(address, txPacket, uuid_altBeacon_company_id_characteristic)

"""
API Name: RequestAltBeaconBeaconId
Requests the AltBeacon beaon ID from the AltBeacon Beacon ID characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The company ID as a 18-element list of integers (each 0-255)
"""
def RequestAltBeaconBeaconId(address, timeout):
    return RequestData(address, uuid_altBeacon_beacon_id_characteristic, timeout)

"""
API Name: SetAltBeaconBeaconId
Writes the AltBeacon beacon ID to the AltBeacon Beacon ID characteristic
    of the given BLE address.
    address: 6-byte BLE address list
    uuid: The beacon ID as a 18-element list of integers (each 0-255)
"""
def SetAltBeaconBeaconId(address, uuid):
    txPacket = uuid
    TransmitPacket(address, txPacket, uuid_altBeacon_beacon_id_characteristic)

"""
API Name: RequestAltBeaconMfgData
Requests the AltBeacon manufacturer byte from the AltBeacon Manufacturer data
    characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The manufacture byte is an integer (0-255)
"""
def RequestAltBeaconMfgData(address, timeout):
    values = RequestData(address, uuid_altBeacon_mfg_data_characteristic, timeout)
    if(values != None):
        return values[0]
    return None

"""
API Name: SetAltBeaconMfgData
Writes the AltBeacon manufacturer byte to the AltBeacon Manufacturer Data
    characteristic of the given BLE address.
    address: 6-byte BLE address list
    value: The manufacture byte is an integer (0-255)
"""
def SetAltBeaconMfgData(address, value):
    txPacket = [value]
    TransmitPacket(address, txPacket, uuid_altBeacon_mfg_data_characteristic)

"""
API Name: RequestAltBeaconMeasuredPower
Requests the AltBeacon measured power from the AltBeacon Measured Power
    characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The measured power in dBm (integer)
"""
def RequestAltBeaconMeasuredPower(address, timeout):
    values = RequestData(address, uuid_altBeacon_measured_power_characteristic, timeout)
    if(values and len(values) == 1):
        value = values[0]
        if(value > 127):
            value = value - 256
        return value

"""
API Name: SetAltBeaconMeasuredPower
Writes the AltBeacon measured power to the AltBeacon Measured Power
    characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
    value: The measured power in dBm (integer)
"""
def SetAltBeaconMeasuredPower(address, value):
    if(value < 0):
        value += 256
    txPacket = [value]
    TransmitPacket(address, txPacket, uuid_altBeacon_measured_power_characteristic)

"""
API Name: RequestAltBeaconPeriod
Requests the AltBeacon period from the AltBeacon Period characteristic
     of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The period in milliseconds (integer) if the read was successful, None otherwise.
"""
def RequestAltBeaconPeriod(address, timeout):
    response = RequestData(address, uuid_altBeacon_period_characteristic, timeout)
    if(response and len(response) == 2):
        return ConvertListToInt(response[0:2])
    else:
        return None

"""
API Name: SetAltBeaconPeriod
Writes the AltBeacon period to the AltBeacon Period characteristic
     of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
    value: The period in milliseconds (integer)
"""
def SetAltBeaconPeriod(address, value):
    txPacket = ConvertIntToList(value, 2)
    TransmitPacket(address, txPacket, uuid_altBeacon_period_characteristic)

# Scan Response
"""
API Name: RequestScanResponseDeviceName
Requests the Scan Response Device Name from the Scan Response Device Name
     characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The device name (string) if the read was successful, None otherwise.
"""
def RequestScanResponseDeviceName(address, timeout):
    deviceNameBytes = RequestData(address, uuid_scan_response_device_name_characteristic, timeout)
    if(deviceNameBytes != None):
        deviceNameString = ''.join(chr(i) for i in deviceNameBytes)
        return deviceNameString
    return None

"""
API Name: RequestScanResponseDeviceName
Writes the Scan Response Device Name to the Scan Response Device Name
     characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
    deviceNameString: The device name (string)
"""
def SetScanResponseDeviceName(address, deviceNameString):
    deviceNameBytes =[ord(i) for i in deviceNameString]
    if(len(deviceNameString) < DEVICE_NAME_MAX_LENGTH):
        deviceNameBytes.append(0)
    logHandler.printLog( "deviceNameBytes = {0}".format(deviceNameBytes), True)

    txPacket = deviceNameBytes
    result = TransmitPacket(address, txPacket, uuid_scan_response_device_name_characteristic)
    return result

"""
API Name: RequestScanResponseUserData
Requests the Scan Response User data from the Scan Response User Data
     characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
Returns:
    The 16-element user data list if the read was successful, None otherwise.
"""
def RequestScanResponseUserData(address, timeout):
    return RequestData(address, uuid_scan_response_user_data_characteristic, timeout)

"""
API Name: SetScanResponseUserData
Writes the Scan Response User Data to the Scan Response User Data
     characteristic of the given BLE address.
    address: 6-byte BLE address list
    timeout: Waits for this duration (in seconds) until the value is retrieved.
    data: The 16-element user data (0-255 each)
"""
def SetScanResponseUserData(address, data):
    txPacket = data
    TransmitPacket(address, txPacket, uuid_scan_response_user_data_characteristic)


# ######################################
# Section: Device Management - APIs
# ######################################

"""
API Name: GetLocalAddress
Returns the BLE address of the BlueGiga dongle
"""
def GetLocalAddress():
    return local_address

"""
API Name: GetDeviceWithAddress
Returns the XimBleDevice object that has a matching BLE address
"""
def GetDeviceWithAddress(address):
    for device in peripheral_list:
        if device.address == address:
            return device
    return None

"""
API Name: GetDeviceWithConnectionHandle
Returns the XimBleDevice object that has a matching connection handle
"""
def GetDeviceWithConnectionHandle(connectionHandle):
    for device in peripheral_list:
        if(device.connection_handle == connectionHandle):
            return device
    return None

"""
API Name: GetDevicesInGroup
Returns the XimBleDevice objects that are within the groupId
"""
def GetDevicesInGroup(groupId):
    inGroupList = []
    if(len(groupId) == 1):
        for device in peripheral_list:

            if (groupId[0] == BLEX_BROADCAST_ADDRESS) or (device.scannedDeviceId == groupId):
                inGroupList.append(device)
            elif(groupId[0] >= BLEX_GROUP_ADDRESS_MIN) and (groupId[0] <= BLEX_GROUP_ADDRESS_MAX):
                realGroupNumber = groupId[0] - BLEX_GROUP_ADDRESS_MIN
##                print "Test realGroupNumber {0} for device {2} in groups {1}".format(realGroupNumber, device.groups, device.scannedDeviceId)
                if(realGroupNumber in device.groups):
##                    print "Found {0} for device {2} in groups {1}".format(realGroupNumber, device.groups, device.scannedDeviceId)
                    inGroupList.append(device)
    elif(len(groupId) == 3):
        for device in peripheral_list:
            if(device.scannedDeviceId == groupId):
                inGroupList.append(device)
    elif(len(groupId) == 4):

        for device in peripheral_list:
            isValid = False
    ##        print "groupId: {0}, device.scannedDeviceId: {1}, device.address: {2}".format(groupId, device.scannedDeviceId, device.address)
            if (device.scannedDeviceId and (len(device.scannedDeviceId) == 4)):
                isValid = True
                for i in range(4):
                    if((groupId[i] != 255) and (groupId[i] != device.scannedDeviceId[i])):
                        isValid = False
            if(isValid):
                inGroupList.append(device)
    return inGroupList

"""
API Name: GetDevicesFromListWithField
Returns the XimBleDevice objects that have the matching attrValue for the given
    attrName
"""
def GetDevicesFromListWithField(deviceList, fieldName, fieldValue):
    matchingList = []
    for device in deviceList:
        if hasattr(device, fieldName) and getattr(device, fieldName) == fieldValue:
            matchingList.append(device)
    return matchingList

"""
API Name: FindConnectingDevice
Returns the first XimBleDevice object that is currently trying to be connected
"""
def FindConnectingDevice():
    for device in peripheral_list:
        if device.connectionState == STATE_CONNECTING:
            return device

"""
API Name: GetDeviceName
Returns the name of the device that has a matching BLE address
"""
def GetDeviceName(address):
    for device in peripheral_list:
        if(device.address == address):
            return device.deviceName
    return None


"""
API Name: GetDeviceId
Returns the logical address of the device that has a matching BLE address
"""
def GetDeviceId(address):
    for device in peripheral_list:
        if(device.address == address):
            return device.scannedDeviceId
    return None


"""
API Name: IsDeviceConnected
Returns True if the device that has a matching BLE address is currently connected
"""
def IsDeviceConnected(address):
    for device in peripheral_list:
        if(device and device.address == address):
            return device.IsConnected()
    return False

"""
API Name: IsDeviceConnecting
Returns True if the device that has a matching BLE address is trying to be connected
"""
def IsDeviceConnecting(address):
    for device in peripheral_list:
        if(device and device.address == address):
            return device.IsConnecting()
    return False

"""
API Name: IsDeviceDiscovering
Returns True if the device that has a matching BLE address is trying to discover
    services and characteristics
"""
def IsDeviceDiscovering(address):
    for device in peripheral_list:
        if(device and device.address == address):
            return device.IsDiscovering()
    return False

"""
API Name: IsDeviceEncryptedAdv
Returns True if the device that has a matching BLE address is using encrypted
    advertisements
"""
def IsDeviceEncryptedAdv(address):
    for device in peripheral_list:
        if(device and device.address == address):
            return device.IsEncryptedAdv()
    return False

"""
API Name: IsDeviceEncryptedHeader
Returns True if the device that has a matching BLE address is using encrypted
    header in its advertisements
"""
def IsDeviceEncryptedHeader(address):
    for device in peripheral_list:
        if(device and device.address == address):
            return device.hasEncryptedHeader
    return False


"""
API Name: GetAddressList
Returns a list of 6-byte BLE addresses of all of the discovered XIM devices
"""
def GetAddressList():
    global peripheral_list
    addressList = []
    for device in peripheral_list:
        if(device and (device.deviceType in [DEVICE_TYPE_XIM]) and (device.scannedDeviceId != None or device.bootloaderMode)):
            addressList.append(device.address)
    return addressList

"""
API Name: GetSensorAddressList
Returns a list of 6-byte BLE addresses of all of the discovered XSensor devices
"""
def GetSensorAddressList():
    global peripheral_list
    addressList = []
    for device in peripheral_list:
        if(device and (device.deviceType in [DEVICE_TYPE_XSENSOR]) and (device.scannedDeviceId != None or device.bootloaderMode)):
            addressList.append(device.address)
    return addressList

"""
API Name: RemoveDevice
Removes the XIM device that has a matching BLE address from the device list
"""
def RemoveDevice(bleAddress):
    global peripheral_list
    for device in peripheral_list:
        if(device.address == bleAddress):
            peripheral_list.remove(device)
            logHandler.printLog("Updated peripheral_list after removal: {0}".format(peripheral_list))
            break

# ######################################
# Section: Main System
# ######################################

"""
API Name: Initialize
Initialize the stack
newLogHandler: A LogHandler object for writing log data to a file
"""
def Initialize(newLogHandler = None):
    global ble, ser
    global logHandler
    global packetLogger

    # create and setup BGLib object
    ble = bglib.BGLib()
    ble.packet_mode = False
    ble.debug = False

    # add handler for BGAPI timeout condition (hopefully won't happen)
    ble.on_timeout += my_timeout

    # add handlers for BGAPI events
    ble.ble_rsp_connection_get_status += my_ble_rsp_connection_get_status
    ble.ble_rsp_system_get_connections += my_ble_rsp_system_get_connections
    ble.ble_evt_gap_scan_response += my_ble_evt_gap_scan_response
    ble.ble_rsp_connection_get_rssi += my_ble_rsp_connection_get_rssi
    ble.ble_evt_connection_status += my_ble_evt_connection_status
    ble.ble_rsp_connection_disconnect += my_ble_rsp_connection_disconnect
    ble.ble_evt_connection_disconnected += my_ble_evt_connection_disconnected
    ble.ble_rsp_gap_connect_direct += my_ble_rsp_gap_connect_direct
    ble.ble_evt_attclient_group_found += my_ble_evt_attclient_group_found
    ble.ble_rsp_attclient_find_information += my_ble_rsp_attclient_find_information
    ble.ble_evt_attclient_find_information_found += my_ble_evt_attclient_find_information_found
    ble.ble_evt_attclient_procedure_completed += my_ble_evt_attclient_procedure_completed
    ble.ble_evt_attclient_attribute_value += my_ble_evt_attclient_attribute_value
    ble.ble_rsp_attclient_attribute_write += my_ble_rsp_attclient_attribute_write
    ble.ble_rsp_attclient_read_by_type += my_ble_rsp_attclient_read_by_type
    ble.ble_rsp_attclient_read_by_group_type += my_ble_rsp_attclient_read_by_group_type

    ble.ble_rsp_sm_set_bondable_mode += my_ble_rsp_sm_set_bondable_mode
    ble.ble_rsp_sm_encrypt_start += my_ble_rsp_sm_encrypt_start
    ble.ble_evt_sm_bonding_fail += my_ble_evt_sm_bonding_fail
    ble.ble_rsp_sm_get_bonds += my_ble_rsp_sm_get_bonds
    ble.ble_evt_sm_bond_status += my_ble_evt_sm_bond_status
    ble.ble_rsp_sm_set_oob_data += my_ble_rsp_sm_set_oob_data

    ble.ble_rsp_attclient_prepare_write += my_ble_rsp_attclient_prepare_write
    ble.ble_rsp_attclient_execute_write += my_ble_rsp_attclient_execute_write


    ble.ble_evt_system_boot += my_ble_evt_system_boot

    #
    ble.ble_rsp_system_hello += my_ble_rsp_system_hello
    ble.ble_rsp_system_address_get += my_ble_rsp_system_address_get


    ble.ble_rsp_gap_end_procedure += my_ble_rsp_gap_end_procedure
    ble.ble_rsp_gap_discover += my_ble_rsp_gap_discover

    ble.ble_rsp_gap_set_adv_parameters += my_ble_rsp_gap_set_adv_parameters
    ble.ble_rsp_gap_set_adv_data += my_ble_rsp_gap_set_adv_data
    ble.ble_rsp_gap_set_mode += my_ble_rsp_gap_set_mode



    if(newLogHandler == None):
        if (cfg.WINDOWS):
            logHandler = LogHandler.LogHandler("{0}\Event_Logs".format(os.getcwd()), "eventLog.txt", True, 5)
        if (cfg.LINUX):
            logHandler = LogHandler.LogHandler("{0}/Event_Logs".format(os.getcwd()), "eventLog.txt", True, 5)
        logHandler.EnableCleanUp(60.0, 20000)
    else:
        logHandler = newLogHandler

    if (cfg.WINDOWS):
        packetLogger = LogHandler.LogHandler("{0}\Packet_Logs".format(os.getcwd()), "PacketLog.csv", True, 5)
    if (cfg.LINUX or cfg.OSX):
        packetLogger = LogHandler.LogHandler("{0}/Packet_Logs".format(os.getcwd()), "PacketLog.csv", True, 5)
    packetLogger.EnableCleanUp(60.0, 50000)
    packetLogger.printLog("BLE Packet Log", False)
    packetLogger.printLog("Time,BLE Address,RSSI,Data,Name,Device ID,Device Type,Payload Type,Payload", False)


"""
API Name: Start
Starts the stack
"""
def Start():
    global bgCentralState, lastScanResponse

    if not os.path.exists(bleDirectory):
        os.makedirs(bleDirectory)

    if(os.path.isfile(uuidHandleMapFileName) == False):
        with open(uuidHandleMapFileName, 'w') as f:
            pass

    if(os.path.isfile(sensorUuidHandleMapFileName) == False):
        with open(sensorUuidHandleMapFileName, 'w') as f:
            pass

    lastScanResponse = time.time()

    GetNetworkInfoFromFile()



##            except ValueError:
##                pass

    UpdateNetworkConfigFile()

    InitializeConnectionParameters()


    bgCentralState = CENTRAL_STATE_STANDBY
    bgPeriphState = PERIPH_STATE_STANDBY

    lastPort = GetLastPort()
    logHandler.printLog("Last active port was: {0}".format(lastPort))

    try:
        portFound = TestPort(int(lastPort))
    except:
        logHandler.printLog("Couldn't find last active port")
        portFound = False


    if(portFound == False):
        for portTest in range(0,20):
            portFound = TestPort(portTest)

            if(portFound):
                break

    if(portFound == False):
        logHandler.printLog("\n================================================================")
        logHandler.printLog("No valid COM port found. Make sure it is not being used by another application", True)
        logHandler.printLog("================================================================")

    return portFound

"""
API Name: Stop
Stops the stack
"""
def Stop():

    try:
        logHandler.printLog("Stopped BLE")

        for device in peripheral_list:
            if(device.connectionState != STATE_STANDBY) and (device.connection_handle != None):
                ble.send_command(ser, ble.ble_cmd_connection_disconnect(device.connection_handle))
                CheckActivity(ser, 1)
                device.connectionState = STATE_STANDBY
##                device.connection_handle = None

        EndProcedure()
        CheckActivity(ser, 1)
        ser.close()
    except:
        logHandler.printLog("Failed to stop BLE connection")

"""
API Name: Process
Runs the stack
"""
def Process():
    global pending_write, bgCentralState
    global ble_write_time, lastScanResponse
    global peripheral_list
    global lastConnectionTest
    global serialFailures

##    time.sleep(0.001)

    if(serialFailures > MAX_SERIAL_FAILURES):
        logHandler.printLog("{0}: Re-starting the serial connection".format(time.time()), True)
        serialFailures = 0
        Stop()
        Start()


    # check for all incoming data (no timeout, non-blocking)
    CheckActivity(ser)

##    if((pending_write) and (time.time() - ble_write_time > DISCONNECT_TIMEOUT + 0.1)):
    if((pending_write) and (time.time() - ble_write_time > PENDING_WRITE_TIMEOUT + 0.1)):
        logHandler.printLog("{0}: pending_write timeout {1}".format(time.time(), time.time() - ble_write_time), True)
        pending_write = False

    isBusy = False
    connectionProblem = False

    for device in peripheral_list:
        if(device.connectionState == STATE_DISCONNECTING and time.time() - device.disconnectTime > DISCONNECT_TIMEOUT):
            device.connectionState = STATE_STANDBY

        # Connection is taking a long time
        if(device.connectionState == STATE_CONNECTING and time.time() - device.connectionAttemptTime > CONNECT_ATTEMPT_WARNING):
            device.longConnectionTime = time.time() - device.connectionAttemptTime
            connectionProblem = True


        # Connection is taking too long, so stop trying
        if(device.connectionState == STATE_CONNECTING and time.time() - device.connectionAttemptTime > CONNECT_ATTEMPT_TIMEOUT):
            logHandler.printLog("{0}: ERROR: Long Connection time: {1}".format(time.time(), time.time() - device.connectionAttemptTime ), True)
            device.longConnectionTime = None

            ProcessFailedConnection(device)

        # Only print the message once after it finishes connecting
        elif(device.connectionState != STATE_CONNECTING and device.longConnectionTime):
            logHandler.printLog("{0}: WARNING: Long Connection time: {1}, state: {2}".format(time.time(), device.longConnectionTime, device.connectionState ), True)
            device.longConnectionTime = None


##        if (device.connectionState in [STATE_FINDING_SERVICES, STATE_FINDING_ATTRIBUTES]) and (device.encryptedAdv) and (device.adminLoggedIn == False) and (GetHandle(device, uuid_access_admin_login_characteristic) != None):
####            logHandler.printLog("{0}: AdminLogin Waiting while finding attributes for {1}".format(time.time(), device.address), True)
##            if(pending_write == False):
##                logHandler.printLog("\n\n!!!!!!!!!!!!!\n\n{0}: AdminLogin while finding attributes for {1}".format(time.time(), device.address), True)
##                AdminLogin(device.address)
##                device.adminLoggedIn = True



    if(pending_write == False):
        if(bootloadRunning):
            if(scanningEnabled == False and bgCentralState == CENTRAL_STATE_SCANNING):
                logHandler.printLog("{0}: Disable scanning".format(time.time()), True)
                EndProcedure()
        else:

##            elif((scanningEnabled) and (bgCentralState in [CENTRAL_STATE_SCANNING, CENTRAL_STATE_STOPPING]) and (time.time() - lastScanResponse > SCAN_RESPONSE_TIMEOUT)):
##                logHandler.printLog("{0}: Scan response timeout. bgCentralState: {1}".format(time.time(), bgCentralState))
##                EndProcedure()
##                lastScanResponse = time.time()


            if((scanningEnabled) and (bgCentralState == CENTRAL_STATE_STANDBY)):
                lastScanResponse = time.time()
                Discover()

            elif(scanningEnabled == False and bgCentralState == CENTRAL_STATE_SCANNING):
                logHandler.printLog("{0}: Disable scanning".format(time.time()), True)
                EndProcedure()

            elif(bgPeriphState == PERIPH_STATE_ADVERTISING) and (time.time() - advertisingStartTime > (bleAdvertisingWindow / 1000.0)):
##                print "Stopped after {0:.3f}".format(time.time() - advertisingStartTime)
                SetAdvertisingState(False)


##            elif(time.time() - lastConnectionTest > CONNECTION_TEST_INTERVAL ):
##                lastConnectionTest = time.time()
##                TestConnection()


def PollForGroupMembership():
    global groupPollingIndex

    if(groupPollingIndex >= len(peripheral_list)):
        groupPollingIndex = 0

    while(groupPollingIndex < len(peripheral_list)):
        device = peripheral_list[groupPollingIndex]
##        logHandler.printLog("{0:.3f}: Test Group: {1}, ReceivedGroups: {2}, requestGroupAttempts: {3}".format(time.time() % 100.0, device.scannedDeviceId, device.receivedAllGroups, device.requestGroupAttempts), True)
        if(len(device.scannedDeviceId) == 1) and (device.receivedAllGroups == False) and (device.deviceType == DEVICE_TYPE_XIM) and  (device.bootloaderMode == False) and  ((device.requestGroupAttempts < MAX_GROUP_REQUESTS) or ((time.time() - device.lastGroupRequestTime) > GROUP_REQUEST_RETRY_INTERVAL)):
            logHandler.printLog("{0:.3f}: Request Group: {1}".format(time.time() % 100.0, device.scannedDeviceId), True)

            # If it entered here, it means device.lastGroupRequestTime was a while ago. Restart the counter.
            if(device.requestGroupAttempts >= MAX_GROUP_REQUESTS):
                device.requestGroupAttempts = 0

            BroadcastRequestAdv(device.scannedDeviceId, [ENCRYPTED_PACKET_TYPE_XGROUP])
            device.requestGroupAttempts += 1
            device.lastGroupRequestTime = time.time()
            return True
        groupPollingIndex += 1
    return False

def SetBootloadActive(state):
    global bootloadRunning
    bootloadRunning = state


def AesCcmEncrypt(key, nonce, inData):
    cipher = AES.new(BytesToString(key), AES.MODE_CCM, BytesToString(nonce), mac_len = 4)

    # Add 1 byte of additional authentication data to match the Cypress method
    cipher.update(BytesToString([1]))
    return StringToBytes(cipher.encrypt(BytesToString(inData))), StringToBytes(cipher.digest())

def AesCcmDecrypt(key, nonce, inData, mac):
    cipher = AES.new(BytesToString(key), AES.MODE_CCM, BytesToString(nonce), mac_len = 4)

    # Add 1 byte of additional authentication data to match the Cypress method
    cipher.update(BytesToString([1]))
    outData = cipher.decrypt(BytesToString(inData))
    outData = StringToBytes(outData)
    try:
        cipher.verify(BytesToString(mac))
        isValid = True
    except:
        isValid = False

    return outData, isValid

def BytesToString(bytes):
    return "".join(chr(val) for val in bytes)

def StringToBytes(str):
    return map(ord,list(str))

def IntListToHexString(intList):
    return str(bytearray(intList)).encode('hex')

def HexStringToIntList(hexString):
    return [int(hexString[i:i+2],16) for i in range(0,len(hexString), 2)]



def EncryptTest():

    header = HexStringToIntList("4875891c000000")

    packetBytes = HexStringToIntList("10ffff00000a00")
##    aesNonce = [0xc5, 0x7c, 0x10, 0x00, 0x00, 0x00]
    aesNonce[:] = header[:]
    aesNonce += [0] * (13 - len(aesNonce))
    payload = packetBytes
    eMsg, eMic = AesCcmEncrypt(networkConfigs[selectedTxNetworkIndex].key, aesNonce, packetBytes)
    print ("eMsg: {0}, eMic: {1}".format(IntListToHexString(eMsg), IntListToHexString(eMic)))

    payloadAndMic = eMsg + eMic
    aesNonce = eMsg + eMic
    aesNonce = aesNonce[:13]
    aesNonce += [0] * (13 - len(aesNonce))
    print ("Header aesNonce: {0}, header: {1}".format(IntListToHexString(aesNonce), IntListToHexString(header)))

    header, unusedMic = AesCcmEncrypt(networkConfigs[selectedTxNetworkIndex].headerKey, aesNonce, header)
    print ("Header eMsg: {0}, eMic: {1}".format(IntListToHexString(header), IntListToHexString(unusedMic)))
    return header, payloadAndMic


# Base application

if __name__ == '__main__':

    txKey = [0xc2, 0x96, 0x19, 0x91, 0x38, 0x89, 0xaa, 0x0f, 0x9f, 0x28, 0xd0, 0x64, 0x3c, 0xcd, 0xc3, 0xaf]
    rxKey = [0x1c, 0xd0, 0x97, 0xbc, 0xcb, 0x4a, 0xa2, 0x05, 0xaf, 0x43, 0xa0, 0xe6, 0xd9, 0x3e, 0x1b, 0x18]
    headerKey = [0x2d, 0x26, 0xdd, 0x7b, 0xeb, 0xf6, 0xee, 0xc2, 0x21, 0x0c, 0xfd, 0x69, 0x36, 0x9d, 0x19, 0xff]

##    headerKey =

##    msg = BytesToString([0xa4, 0xd4, 0x83, 0xa8 , 0x94, 0x85, 0x58, 0x6b , 0x81, 0x4a, 0xc3, 0xe6 , 0x51, 0xab, 0x60])
##    msg = [0xa4, 0xd4, 0x83, 0xa8 , 0x94, 0x85, 0x58, 0x6b , 0x81, 0x4a, 0xc3, 0xe6 , 0x51, 0xab, 0x60]
##    aesNonce = [0x32, 0x00, 0x2e, 0x47] + [0] * 9

##    aesNonce = [0x32, 0x00, 0x2f, 0x47] + [0] * 9
##    payload = [0x97, 0xab , 0xdc, 0x54, 0x52, 0x12 , 0xec, 0x27, 0xdc, 0x72 , 0x86, 0xf7]
##    mic = [0x9d, 0xc3, 0x68, 0x34]

##    packetString = "A7 21 00 00 00 82 71 78 B5 62 41 BF 75 12 69 C1"
##    packetString = "10 D9 E8 DB 07 01 00"
##    packetStringList = packetString.split(' ')
##    packetBytes = []
##    for packetText in packetStringList:
##        packetBytes.append(eval("0x{0}".format(packetText)))
##    print "packetBytes: {0}".format(packetBytes)
##    sourceAddress = [0x0a, 0x06]
##    aesNonce = sourceAddress + packetBytes[:5]
    header = HexStringToIntList("4875875e000000")

    packetBytes = HexStringToIntList("21ffff08007764")
##    aesNonce = [0xc5, 0x7c, 0x10, 0x00, 0x00, 0x00]
    aesNonce[:] = header[:]
    aesNonce += [0] * (13 - len(aesNonce))
    payload = packetBytes
    eMsg, eMic = AesCcmEncrypt(txKey, aesNonce, packetBytes)
    print ("eMsg: {0}, eMic: {1}".format(IntListToHexString(eMsg), IntListToHexString(eMic)))


    aesNonce = eMsg + eMic
    aesNonce = aesNonce[:13]
    aesNonce += [0] * (13 - len(aesNonce))
    print ("Header aesNonce: {0}, header: {1}".format(IntListToHexString(aesNonce), IntListToHexString(header)))

    eMsg, eMic = AesCcmEncrypt(headerKey, aesNonce, header)
    print ("Header eMsg: {0}, eMic: {1}".format(IntListToHexString(eMsg), IntListToHexString(eMic)))

##    payload = packetBytes[5:12] # [0x62, 0xAB, 0x05, 0xB9, 0x0E, 0x81, 0xFC]
##    mic = packetBytes[12:16] # [0x97, 0xAC, 0x78, 0x48]

##    msg = "a4d483a89485586b814ac3e651ab60"
##    cipher = AES.new(BytesToString(txAesKey), AES.MODE_CCM, BytesToString(aesNonce), mac_len = 4)
##    cipher.update(BytesToString([1]))
##    eMsg = StringToBytes(cipher.encrypt(msg))
##    eMic = StringToBytes(cipher.digest())
##    print "eMsg: {0}, \nmic: {1}\n".format(eMsg, eMic)

##    packetString = "80 50 04 66 B0 F8 C2 C8 1B 15 4B A6 A0 AE 00 BF"
##    packetString = "d7 a4 76 ee 97 b5 2c 26 11 98 70 0c 13 9a 0a 67"
##    packetStringList = packetString.split(' ')
##    packetBytes = []
##    for packetText in packetStringList:
##        packetBytes.append(eval("0x{0}".format(packetText)))
##    print "packetBytes: {0}".format(packetBytes)
##
##    aesNonce = packetString[-11:] + [0, 0]
##    payload = packetString[:5]


##    packetBytes = [2 1 6 27 255 83 2 139,
##    aesNonce = [50, 0, 74, 115, 0, 0, 0]
##    aesNonce = [0x34, 0xCB, 0x03, 0xA0, 0x9C, 0xDB, 0xBD, 0xD5, 0x36, 0x09, 0x31, 0x35, 0x07]
##    packetBytes = [217, 126, 131, 216, 186, 124, 2, 34, 20, 15, 20, 207, 52, 17, 145, 123]
##    packetBytes = [0xDF, 0x8B, 0x50, 0x9E, 0x54, 0xE3, 0x67]
##    aesNonce = packetBytes[7:20]
##    packetBytes = packetBytes[:7]
##    packetBytes += [0] * 4

##    aesNonce = [0x32, 0x00, 0x84, 0xDF, 0x01]
##    aesNonce += [0] * (13 - len(aesNonce))
##    payload = packetBytes[:-4] # [0x62, 0xAB, 0x05, 0xB9, 0x0E, 0x81, 0xFC]
##    mic = packetBytes[-4:] # [0x97, 0xAC, 0x78, 0x48]
##
##    print "aesNonce: {0}".format(aesNonce)
##    print "payload: {0}".format(payload)
##    print "mic: {0}".format(mic)
##
##
##    decryptedData, isValid = AesCcmDecrypt(headerKey, aesNonce, payload, mic)
##    print "decryptedData: {0}, isValid: {1}".format(decryptedData, isValid)

##    packetString = "7e95087838be7f03cf3a4ead775a7d03"
##    packetBytes = list(reversed(HexStringToIntList(packetString)))
##    print "packetBytes: {0}".format(packetBytes)
##    sourceAddress = HexStringToIntList("2B83")
##
##    aesNonce = packetBytes[:11] + [0, 0]
##    encryptedHeader = sourceAddress + packetBytes[11:]
##    decryptedData, isValid = AesCcmDecrypt(headerKey, aesNonce, encryptedHeader, [0] * 4)
##    print "decryptedData: {0}, isValid: {1}".format(decryptedData, isValid)


##    packetString = "12 32 00 03 08 19 05"
##    packetStringList = packetString.split(' ')
##    packetBytes = []
##    for packetText in packetStringList:
##        packetBytes.append(eval("0x{0}".format(packetText)))
##    print "packetBytes: {0}".format(packetBytes)
##    eMsg, eMic = AesCcmEncrypt(testKey, aesNonce, packetBytes)
##    print "eMsg: {0}, eMic: {1}".format(eMsg, eMic)

##    Initialize()
##
##    Start()
##
##    while(1):
##        Process()
