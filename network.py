import platform    # For getting the operating system name
import subprocess  # For executing a shell command

class NetworkChecker():
    def __init__(self, ip):
        self.ip = ip

    def ping(self, host=None):
        if host is None:
            print(f'[WARNING:] Class IP ({self.ip}) is used')
            host = self.ip
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]

        return subprocess.call(command) == 0

if __name__ == '__main__':
    test = NetworkChecker('192.168.1.5')
    la = test.ping()
    print('finished')