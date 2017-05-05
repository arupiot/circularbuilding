"""
Name: XimSecureNetwork.py
Purpose: Contains the APIs for creating a Xicato Secure Network over BLE

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
"""

import ble_xim
import time # Only needed for testing (main)

NETWORK_ID_GENERATOR_KEY = [0x4B, 0xFB, 0x4A, 0x1A, 0x6F, 0xA5, 0x32, 0xD5, 0x45, 0x8D, 0x10, 0x24, 0x5B, 0x05, 0x20, 0x99]
TXKEY_GENERATOR_KEY = [0xCC, 0xB2, 0x7F, 0x49, 0x98, 0x08, 0xC5, 0x85, 0x57, 0x28, 0x60, 0x74, 0x20, 0x37, 0x56, 0x7B]
RXKEY_GENERATOR_KEY = [0xBD, 0x90, 0xA9, 0xB6, 0xA4, 0xDA, 0x67, 0x94, 0x44, 0xBA, 0x82, 0xF7, 0x21, 0x74, 0x44, 0x24]
NETWORK_HEADER_KEY_GENERATOR_KEY = [0x84, 0xD7, 0x63, 0x2E, 0x7C, 0x1F, 0x93, 0x13, 0x33, 0xD5, 0x1E, 0x49, 0x6B, 0x1B, 0x63, 0x45]
GENERATOR_NONCE = [0x8F, 0x43, 0xBB, 0x26, 0x86, 0x7E, 0x4E, 0x6A, 0x71, 0x0B, 0x52, 0x1F, 0xAF]

bleNetworkList = []

# Creates the network credentials based on the strings networkName and networkPassword
def CreateNetworkCredentials(networkName, networkPassword):
    networkId, mic = ble_xim.AesCcmEncrypt(NETWORK_ID_GENERATOR_KEY, GENERATOR_NONCE, map(ord,list(networkName)))
    networkId = networkId[:4]

    # Repeat the string until it fills 16 characters
    while(len(networkPassword) < 16):
        networkPassword += networkPassword[:max(0, 16 - len(networkPassword))]

    txNetworkKey, mic = ble_xim.AesCcmEncrypt(TXKEY_GENERATOR_KEY, GENERATOR_NONCE, map(ord,list(networkPassword)))
    txNetworkKey = txNetworkKey[:16]

    rxNetworkKey, mic = ble_xim.AesCcmEncrypt(RXKEY_GENERATOR_KEY, GENERATOR_NONCE, map(ord,list(networkPassword)))
    rxNetworkKey = rxNetworkKey[:16]

    networkHeaderInput = networkName
    while(len(networkHeaderInput) < 16):
        networkHeaderInput += networkName[:max(0, 16 - len(networkHeaderInput))]
    networkHeaderKey, mic = ble_xim.AesCcmEncrypt(NETWORK_HEADER_KEY_GENERATOR_KEY, GENERATOR_NONCE, map(ord,list(networkHeaderInput)))

    print "networkId: {0}".format(networkId)
    print "networkPassword: {0}".format(networkPassword)
    print "networkHeaderInput: {0}".format(networkHeaderInput)
    print "txNetworkKey: {0}, rxNetworkKey: {1}, networkHeaderKey: {2}".format(txNetworkKey, rxNetworkKey, networkHeaderKey)
    bleNetworkList.append({'name': networkName, 'netId': networkId, 'txKey': txNetworkKey, 'rxKey': rxNetworkKey, 'headerKey': networkHeaderKey})


# Sets the local network credentials
def SetLocalNetworkConfiguration(isEncrypted, networkSlot):
    if(isEncrypted == False):
        networkId = [0] * 4
        networkHeaderKey = [0] * 16
        txValues = {'key': [0] * 16, 'permissions': ble_xim.NETWORK_PERM_ALL}
        rxValues = {'key': [0] * 16, 'permissions': ble_xim.NETWORK_PERM_ALL}
    else:
        networkInfo = bleNetworkList[networkSlot]
        networkId = networkInfo['netId']
        networkHeaderKey = networkInfo['headerKey']
        txValues = {'key': networkInfo['txKey'], 'permissions': ble_xim.NETWORK_PERM_ADV_XBEACON}
        rxValues = {'key': networkInfo['rxKey'], 'permissions': ble_xim.NETWORK_PERM_RX_ALL}

    ble_xim.SetLocalNetworkConfiguration(networkId, networkHeaderKey, rxValues, txValues)


# Sets the XIM (with bleAddress) network credentials
def SetXimNetworkConfig(bleAddress, isEncrypted, networkSlot):

    if(isEncrypted == False):
        networkId = [0] * 4
        networkHeaderKey = [0] * 16
        txValues = {'key': [0] * 16, 'permissions': ble_xim.NETWORK_PERM_ALL}
        rxValues = {'key': [0] * 16, 'permissions': ble_xim.NETWORK_PERM_ALL}
    else:
        networkInfo = bleNetworkList[networkSlot]
        networkId = networkInfo['netId']
        networkHeaderKey = networkInfo['headerKey']
        txValues = {'key': networkInfo['txKey'], 'permissions': ble_xim.NETWORK_PERM_ADV_XBEACON}
        rxValues = {'key': networkInfo['rxKey'], 'permissions': ble_xim.NETWORK_PERM_RX_ALL}

    accessConfigList = [txValues, rxValues]

    ble_xim.AdminLogin(bleAddress)
    ble_xim.SetNetworkConfiguration(bleAddress, networkId, networkHeaderKey, accessConfigList, 0.5)

if __name__ == '__main__':
    ble_xim.Initialize()
    ble_xim.Start()

    startTime = time.time()
    while((time.time() - startTime) < 3.0):
        ble_xim.Process()


    CreateNetworkCredentials("NameTest", "PasswordTest")
    SetLocalNetworkConfiguration(True, 0)

    deviceId = [1]
    bleAddress = [35, 69, 103, 80, 160, 0]
    ble_xim.EnableConnections(deviceId)
    connectionSuccess = ble_xim.Connect(bleAddress, ble_xim.CONNECT_ATTEMPT_TIMEOUT)
    SetXimNetworkConfig(bleAddress, True, 0)
    ble_xim.Disconnect(bleAddress)



