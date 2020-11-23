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
f = 1        # 1Hz      (Frequency)
fs = 64     # 64Hz    (Sample Rate)
T = 1/f
Ts = 1/fs

print(f"UDP target IP: {UDP_IP}")
print(f"UDP target Port: {UDP_PORT}")

while(True):
    i = 0;
    test = 1.4
    x = np.arange(fs)
    packet_size = np.arange(4)
    y =[ amp*np.sin(2*np.pi*f * (i/fs)) for i in x]
    sock = socket.socket(socket.AF_INET,
                    socket.SOCK_DGRAM) #UDP
    for value in x:
        sample_struct = struct.pack('!fff', float(i), float(x[i]), float(y[i]))
        sock.sendto(sample_struct, (UDP_IP, UDP_PORT))
        # test_pack = struct.pack('!f', test)
        # print(test)
        # print(test_pack)
        # sock.sendto(test_pack, (UDP_IP, UDP_PORT))
        print(i)
        print(sample_struct)
        print(struct.unpack('>fff', sample_struct))
        # print(f"Message send: Nr.{i} with: {i}, {x[i]}, {y[i]}")
        i += 1
        sleep(1)
    sleep(1)