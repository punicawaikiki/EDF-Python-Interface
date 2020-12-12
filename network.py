import platform    # For getting the operating system name
import subprocess  # For executing a shell command
from globals import *
from PyQt5 import QtCore
from time import sleep


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
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0

    QtCore.pyqtSlot()
    def checkDestination(self):
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

if __name__ == '__main__':
    test = NetworkChecker()
    test.checkDestination()
    print('finished')