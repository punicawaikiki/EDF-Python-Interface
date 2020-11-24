import socket
import numpy as np
import struct
from time import sleep

def float_to_hex(f):
    return hex(struct.unpack('<q', struct.pack('<d', f))[0])

# Get x values of the sine wave

time = np.arange(0, 10, 0.1);

UDP_IP = "192.168.1.5"
UDP_PORT = 55556
# Your Parameters
amp = 1         # 1V        (Amplitude)
f = 2.5        # 1Hz      (Frequency)
fs = 10     # 64Hz    (Sample Rate)
T = 1/f
Ts = 1/fs

print(f"UDP target IP: {UDP_IP}")
print(f"UDP target Port: {UDP_PORT}")

while(True):
    x = np.arange(fs)
    y =[ amp*np.sin(2*np.pi*f * (i/fs)) for i in x]
    sock = socket.socket(socket.AF_INET,
                    socket.SOCK_DGRAM) #UDP
    sample_struct = struct.pack('10d 10d 10d', *x, *x, *y)
    sock.sendto(sample_struct, (UDP_IP, UDP_PORT))
    print(sample_struct)
    print(struct.unpack('10d 10d 10d', sample_struct))
    sleep(1)