UDP_DESTINATION_IP = "192.168.1.5"  # destination ip address(stm32)
UDP_SOURCE_IP = "192.168.1.1"   # local ip address
UDP_SEND_PORT = 55556   # UDP port to send data to stm32
UDP_RECEIVE_PORT = 55555    # UDP port to receive data from stm32
SAMPLE_ARRAY_SIZE = 256     # UDP Packet size -> 256 floats with one paket will be send
EPOCHES = 8 # number of UDP pakets will be send for one calculation
NUMBER_OF_SAMPLES = int( SAMPLE_ARRAY_SIZE * EPOCHES ) # Number of Samples
FFT_SIZE = int( SAMPLE_ARRAY_SIZE * EPOCHES / 2 ) # FFT Size
FFT_EPOCHES = int(FFT_SIZE / SAMPLE_ARRAY_SIZE) # number of UDP pakets will be send back to host
