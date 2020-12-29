UDP_DESTINATION_IP = "192.168.1.5"
UDP_SOURCE_IP = "192.168.1.1"
UDP_SEND_PORT = 55556
UDP_RECEIVE_PORT = 55555
SAMPLE_ARRAY_SIZE = 256
EPOCHES = 8
FFT_SIZE = int( SAMPLE_ARRAY_SIZE * EPOCHES / 2 ) 
NUMBER_OF_SAMPLES = int( SAMPLE_ARRAY_SIZE * EPOCHES ) 
FFT_EPOCHES = int(FFT_SIZE / SAMPLE_ARRAY_SIZE)