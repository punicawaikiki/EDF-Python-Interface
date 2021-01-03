import platform    # For getting the operating system name
import subprocess  # For executing a shell command
from globals import *
from PyQt5 import QtCore
from time import sleep
from subprocess import PIPE
import ptvsd
import numpy as np
import socket
import struct


# TODO: May Check of UDP Port is possible?
class NetworkChecker(QtCore.QObject):
    destinationStatus = QtCore.pyqtSignal(str)

    # send pings to host and returns True if reachable
    def ping(self):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', UDP_DESTINATION_IP]
        return subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    QtCore.pyqtSlot()
    def checkDestination(self):
        ptvsd.debug_this_thread()
        while True:
            status = self.ping()
            if status is False:
                statusStr = '<font color="red">disconnected</font>'
            elif status is True:
                statusStr = '<font color="green">Connected</font>'
            else:
                statusStr = ""
            self.destinationStatus.emit(statusStr)
            print(str)
            sleep(5)

class UDPReceiver(QtCore.QObject):
    dataChanged = QtCore.pyqtSignal(np.ndarray)
    def start(self):
        print('woker.start() called')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_SOURCE_IP, UDP_RECEIVE_PORT))

    @QtCore.pyqtSlot()
    def process(self):
        # ptvsd.debug_this_thread()
        self.continue_run = True # provide a bool run condition for the class
        self.fftpacketNumberArray = np.zeros(FFT_EPOCHES)
        self.fftResultsArray = np.zeros(FFT_SIZE)
        self.start()
        print('process called')
        while self.continue_run:
            data, addr = self.sock.recvfrom(1032)
            receivedData = struct.unpack(f'1i {SAMPLE_ARRAY_SIZE}f', data)
            receivedPacketNumber = int (receivedData[0])
            receivedFFTArray = receivedData[1:]
            for sample in range(SAMPLE_ARRAY_SIZE):
                if self.fftpacketNumberArray[receivedPacketNumber] == 0:
                    self.fftResultsArray[sample + receivedPacketNumber * SAMPLE_ARRAY_SIZE] = receivedFFTArray[sample]
                else:
                    break
            self.fftpacketNumberArray[receivedPacketNumber] = 1
            if (np.count_nonzero(self.fftpacketNumberArray) == FFT_EPOCHES):
                self.dataChanged.emit(self.fftResultsArray)
                self.fftpacketNumberArray = np.zeros(FFT_EPOCHES)

    def stop(self):
        self.continue_run = False # set the run condition to false on stop

if __name__ == '__main__':
    test = NetworkChecker()
    test.checkDestination()
    print('finished')