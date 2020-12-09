import numpy as np
import socket
import matplotlib.pyplot as plotter
from time import sleep
import struct
import matplotlib.pyplot as plt
 
UDP_STRUCT_SIZE = 64

# How many time points are needed i,e., Sampling Frequency
samplingFrequency   = 102.4

# At what intervals time points are sampled
samplingInterval       = 1 / samplingFrequency;

# Begin time period of the signals
beginTime           = 0

# End time period of the signals
endTime             = 10 

# Frequency of the signals
signal1Frequency     = 10
signal2Frequency     = 50
signal3Frequency     = 200

# Time points
time        = np.arange(beginTime, endTime, samplingInterval)
 
N_samples = 1024
amp1 = 1
amp2 = 2
amp3 = 3
t = np.arange(N_samples)

# Create two sine waves
amplitude1 = amp1 * np.sin(2 * np.pi * signal1Frequency * t / N_samples)
amplitude2 = amp2 * np.sin(2 * np.pi * signal2Frequency * t / N_samples)
amplitude3 = amp3 * np.sin(2 * np.pi * signal3Frequency * t / N_samples)
amplitude = amplitude1 + amplitude2 + amplitude3

# plt.plot(t, amplitude)
# plt.show()

UDP_IP = "192.168.1.5"
UDP_PORT = 55556
cnt = 0
epoch_amplitude = np.array_split(amplitude, 16)
epoch_time = np.array_split(time, 16)

while(True):
    for messageNumber in range(0, int(len(time) / UDP_STRUCT_SIZE)):
        sock = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM) #UDP
        sample_struct = struct.pack('1i 64d 64d', messageNumber, *epoch_time[messageNumber], *epoch_amplitude[messageNumber])
        sock.sendto(sample_struct, (UDP_IP, UDP_PORT))
        print(struct.unpack('1i 64d 64d', sample_struct))
        cnt += 1
    print('Sample finshed to send')
    sleep(0.1)