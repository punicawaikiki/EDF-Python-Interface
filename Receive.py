import numpy as np
import socket
import struct
import matplotlib.pyplot as plotter

EPOCHES = 16
FFT_EPOCHES = int(EPOCHES / 2)
SAMPLE_ARRAY_SIZE = 64
UDP_IP = "192.168.1.1"
UDP_PORT = 55555

samplingFrequency = 100
packetNumberArray = np.zeros(FFT_EPOCHES)
dataArray = np.zeros(SAMPLE_ARRAY_SIZE * FFT_EPOCHES)
sock = socket.socket(socket.AF_INET,
                    socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))
cnt = 0
while True:
    data, addr = sock.recvfrom(1512) # buffer size
    receivedData = struct.unpack(f'1d {SAMPLE_ARRAY_SIZE}d', data)
    receivedPacketNumber = int (struct.unpack(f'1d {SAMPLE_ARRAY_SIZE}d', data)[0])
    receivedStruct = struct.unpack(f'1d {SAMPLE_ARRAY_SIZE}d', data)[1:SAMPLE_ARRAY_SIZE + 1]
    for sample in range(SAMPLE_ARRAY_SIZE):
        if packetNumberArray[receivedPacketNumber] == 0:
            dataArray[sample + receivedPacketNumber * SAMPLE_ARRAY_SIZE] = receivedStruct[sample]
        else:
            break
    packetNumberArray[receivedPacketNumber] = 1
    if (np.count_nonzero(packetNumberArray) == FFT_EPOCHES):
        print(f'Array number: {cnt}')
        for i, item in enumerate(dataArray):
            if dataArray[i] > 1:
                print(f'frequency: {i}')

        # Create subplot
        figure, axis = plotter.subplots(2, 1)
        plotter.subplots_adjust(hspace=1)
        tpCount     = 1024

        values      = np.arange(int(tpCount/2))

        timePeriod  = tpCount/samplingFrequency

        frequencies = values
        # Frequency domain representation
        axis[0].set_title('Fourier transform depicting the frequency components')
        axis[0].plot(frequencies, dataArray)
        axis[0].set_xlabel('Frequency')
        axis[0].set_ylabel('Amplitude')



        plotter.show()
        # cnt+=1