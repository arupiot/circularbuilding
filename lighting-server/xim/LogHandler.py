
"""
Library for printing messages to a file and the console

Xicato Changelog:
    V2.3 2016-06-24
        - Added exception handling when the file is in use
    V2.2 2015-12-20
        - Allows file extensions other than .txt
        - No longer writes "Message Event Log\n" at the start
    V2.1 2015-11-05
        - Supports creating the file in a new directory
        - Supports appending a timestamp to the file name
        - Supports automatically removing old log files. It will keep up to
            self.maxFiles files and removes the oldest files that start with
            the same fileName
        - When the maxLines are reached, a new file is created

    V2.0 2015-09-23
        - Initial release

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
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

============================================
"""

import os
from os import remove, rename
import time, datetime


class LogHandler(object):
    def __init__(self, directory, fileName, hasTimeStamp = False, maxFiles = 0):

        self.directory = directory
        self.maxFiles = maxFiles
        self.hasTimeStamp = hasTimeStamp

        self.cleanUp = False
        self.lastCleanUp = None
        self.cleanInterval = None
        self.maxLines = None

        if not os.path.exists(directory):
            os.makedirs(directory)

        # Remove the extension if there is one
        extensionIndex = fileName.find(".")

        if(extensionIndex >= 0):
            self.fileNameExtension = "{0}".format(fileName[extensionIndex:])
            fileName = fileName[:extensionIndex]
        else:
            self.fileNameExtension = ".txt"
        self.fileNamePrefix = fileName


        # Build up the list of files in the given directory and sort them
        #   by creation date, so that the RemoveOldFiles function will
        #   know which device to remove first.
        self.fileTimeList = []
        if(maxFiles > 0):
            for name in os.listdir(directory):
                fullName = os.path.join(directory, name)
                if (os.path.isfile(fullName) and (name[:len(fileName)] == fileName)):
                    newTime = os.path.getmtime(fullName)

                    insertIndex = 0
                    for fileTime in self.fileTimeList:
                        if(newTime < fileTime[1]):
                            break
                        insertIndex += 1

                    self.fileTimeList.insert(insertIndex, [fullName, newTime])

        # Create the new file and remove any old files
        self.CreateLogFile()
        self.RemoveOldFiles()

    # Creates a new log file, based on the arguments provided when the
    #   LogHandler object was created
    def CreateLogFile(self):

        suffix = self.fileNameExtension
        if(self.hasTimeStamp):
            self.fullFileName = "{0}_{1}{2}".format(os.path.join(self.directory, self.fileNamePrefix), datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S"), suffix)
        else:
            self.fullFileName = "{0}{1}".format(os.path.join(self.directory, self.fileNamePrefix), suffix)

        if(os.path.isfile(self.fullFileName)):
            i = 1
            while(1):
                testFileName = "{0}_{1}{2}".format(self.fullFileName[:-4], i, self.fullFileName[-4:])
                if(os.path.isfile(testFileName) == False):
                    os.rename(self.fullFileName, testFileName)
                    break
                i += 1

        with open(self.fullFileName, 'w') as f:
            pass

        newTime = os.path.getctime(self.fullFileName)
        self.fileTimeList.append([self.fullFileName, newTime])

    # Removes old files based on when they were created.
    # The directory will store up to self.maxFiles
    def RemoveOldFiles(self):
        if(self.maxFiles > 0):
            numRemoveFiles = len(self.fileTimeList) - self.maxFiles

            for i in range(0, numRemoveFiles, 1):
                try:
                    print("Removed {0}".format(self.fileTimeList[0][0]))
                    os.remove(self.fileTimeList[0][0])
                    self.fileTimeList.pop(0)
                except:
                    pass

    # Enables the file to not get too large. The actual clean up will be
    #   called from printLog
    #   interval: interval (in seconds) at which it will check if it needs clean up
    #   maxLines: the maximum number of lines that the file is allowed to have
    def EnableCleanUp(self, interval, maxLines):
        self.cleanUp = True
        self.cleanInterval = interval
        self.maxLines = maxLines

    # Disables file clean up
    def DisableCleanUp(self):
        self.cleanUp = False

    # When the number of lines exceeds the allowed maxLines, a new file is
    #    created and any old files (more than self.maxFiles) are removed
    def CleanLog(self):
        self.lastCleanUp = time.time()
        tempFileName = self.fullFileName.split('.')[0] + ".tmp"
        lines = []

        try:
            with open(self.fullFileName) as f:
                lines = f.readlines()

            if(self.maxLines and len(lines) > self.maxLines):
                print("Starting a new file")
                self.CreateLogFile()
                self.RemoveOldFiles()
        except IOError:
            if(os.path.isfile(self.fullFileName) == False):
                with open(tempFileName, 'w') as f:
                    pass

    # Renames the file and reports an error if there's an exception
    def RenameSafely(self, newFileName, oldFileName):
        try:
            attempts = 0
            while(attempts < 3 and os.path.isfile(oldFileName) and os.path.isfile(newFileName)):
                remove(oldFileName)
                attempts += 1
                start_time = time.time()
                while(os.path.isfile(oldFileName) and (time.time() - start_time < 0.2)):
                    pass
            if(os.path.isfile(oldFileName) == False and os.path.isfile(newFileName)):
                rename(newFileName, oldFileName)
        except IOError:
            self.printLog("Error when renaming {0} to {1}".format(newFileName, oldFileName), True)
            if(os.path.isfile(oldFileName) == False):
                self.printLog("{0} is missing. Will create a blank file".format(oldFileName), True)
                with open(oldFileName, 'w') as f:
                    pass

    # Writes the message to a file and if enabled, prints to the console
    #   message: the string to be written
    #   consolePrint: When True, the message will be printed to the console
    def printLog(self, message, consolePrint = False):
        try:
            with open(self.fullFileName, 'a') as f:
                f.write(message + "\n")
        except IOError:
            pass

        if(consolePrint):
            print( message)

        if(self.cleanUp and (self.lastCleanUp == None or (time.time() - self.lastCleanUp > self.cleanInterval))):
            self.CleanLog()
