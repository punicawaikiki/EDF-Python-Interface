import socket
import numpy as np
import struct
from time import sleep

def float_to_hex(f):
    return hex(struct.unpack('<Q', struct.pack('<d', f))[0])

# Get x values of the sine wave

time = np.arange(0, 10, 0.1);

UDP_IP = "192.168.1.5"
UDP_PORT = 55556
# Your Parameters
amp = 1         # 1V        (Amplitude)
f = 1        # 1Hz      (Frequency)
fs = 64     # 64Hz    (Sample Rate)
T = 1/f
Ts = 1/fs

print(f"UDP target IP: {UDP_IP}")
print(f"UDP target Port: {UDP_PORT}")
message = b"TEST"


i = 0
while(True):
    x = np.arange(fs)
    packet_size = np.arange(4)
    y =[ amp*np.sin(2*np.pi*f * (i/fs)) for i in x]
    hex_array = [float_to_hex(float(x)) for x in y]
    string_array = ','.join(hex_array)
    sock = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM) #UDP
    sock.sendto(string_array.encode(), (UDP_IP, UDP_PORT))
    sock.sendto(message, (UDP_IP, UDP_PORT))
    print(f"Message send: Nr.{i}")
    i = i + 1
    sleep(1)