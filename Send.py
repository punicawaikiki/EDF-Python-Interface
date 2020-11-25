import numpy as np
import socket
import matplotlib.pyplot as plt
from time import sleep
import struct

 
udp_struct_size = 64



# How many time points are needed i,e., Sampling Frequency

samplingFrequency   = 100

 

# At what intervals time points are sampled

samplingInterval       = 1 / samplingFrequency;

 

# Begin time period of the signals

beginTime           = 0

 

# End time period of the signals

endTime             = 10.24 

 

# Frequency of the signals

signal1Frequency     = 4

# signal2Frequency     = 7

 

# Time points

time        = np.arange(beginTime, endTime, samplingInterval)

 

# Create two sine waves

amplitude1 = np.sin(2*np.pi*signal1Frequency*time)

# amplitude2 = np.sin(2*np.pi*signal2Frequency*time)

 # Frequency domain representation

# fourierTransform = np.fft.fft(amplitude1)/len(amplitude1)           # Normalize amplitude

# fourierTransform = fourierTransform[range(int(len(amplitude1)/2))] # Exclude sampling frequency

 

# tpCount     = len(amplitude1)

# values      = np.arange(int(tpCount/2))

# timePeriod  = tpCount/samplingFrequency

# frequencies = values/timePeriod

# Time domain representation for sine wave 1

UDP_IP = "192.168.1.5"
UDP_PORT = 55556
cnt = 0
epoch_amplitude1 = np.array_split(amplitude1, 16)
epoch_time = np.array_split(time, 16)
while(True):
    for i in range(0, int(len(time) / udp_struct_size)):
        sock = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM) #UDP
        sample_struct = struct.pack('64d 64d', *epoch_time[i], *epoch_amplitude1[i])
        sock.sendto(sample_struct, (UDP_IP, UDP_PORT))
        print(sample_struct)
        print(struct.unpack('64d 64d', sample_struct))
        cnt += 1
        sleep(0.1)
    print('Sample finshed to send')
    sleep(1)