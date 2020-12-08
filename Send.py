import numpy as np
import socket
import matplotlib.pyplot as plotter
from time import sleep
import struct

 
udp_struct_size = 64



# How many time points are needed i,e., Sampling Frequency

samplingFrequency   = 102.4

 

# At what intervals time points are sampled

samplingInterval       = 1 / samplingFrequency;

 

# Begin time period of the signals

beginTime           = 0

 

# End time period of the signals

endTime             = 10 

 

# Frequency of the signals

signal1Frequency     = 4

# signal2Frequency     = 7

 

# Time points

time        = np.arange(beginTime, endTime, samplingInterval)

 
N_samples = 1024
amp = 1
t = np.arange(N_samples)

# Create two sine waves
amplitude1 = amp * np.sin(2 * np.pi * 50 * t / N_samples)
amplitude2 = amp * np.sin(2 * np.pi * 100 * t / N_samples)
amplitude3 = amp * np.sin(2 * np.pi * 15 * t / N_samples)
amplitude = amplitude1 + amplitude2 + amplitude3
# amplitude1 = np.sin(2*np.pi*signal1Frequency*time)

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
epoch_amplitude = np.array_split(amplitude, 16)
epoch_time = np.array_split(time, 16)

# # Create subplot
# figure, axis = plotter.subplots(2, 1)
# plotter.subplots_adjust(hspace=1)

# # Time domain representation for sine wave 1

# axis[0].set_title('Sine wave with a frequency of 4 Hz')
# axis[0].plot(time, amplitude1)
# axis[0].set_xlabel('Time')
# axis[0].set_ylabel('Amplitude')

# # Frequency domain representation

# fourierTransform = np.fft.fft(amplitude1)/len(amplitude1)           # Normalize amplitude

# fourierTransform = fourierTransform[range(int(len(amplitude1)/2))] # Exclude sampling frequency

# tpCount     = len(amplitude1)
# values      = np.arange(int(tpCount/2))
# timePeriod  = tpCount/samplingFrequency
# frequencies = values/timePeriod

# test = abs(fourierTransform)

# # Frequency domain representation

# axis[1].set_title('Fourier transform depicting the frequency components')
# axis[1].plot(frequencies, abs(fourierTransform))
# axis[1].set_xlabel('Frequency')
# axis[1].set_ylabel('Amplitude')

# plotter.show()


while(True):
    for messageNumber in range(0, int(len(time) / udp_struct_size)):
        sock = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM) #UDP
        sample_struct = struct.pack('1i 64d 64d', messageNumber, *epoch_time[messageNumber], *epoch_amplitude[messageNumber])
        sock.sendto(sample_struct, (UDP_IP, UDP_PORT))
        print(struct.unpack('1i 64d 64d', sample_struct))
        cnt += 1
        sleep(0.1)
    print('Sample finshed to send')
    sleep(1)