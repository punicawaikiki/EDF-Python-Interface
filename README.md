# Earliest Deadline First (EDF) Python Interface

This project serves as an interface to connect to a [STM32F769I-Disc0](https://www.st.com/en/evaluation-tools/32f769idiscovery.html) board on which an [EDF Scheduler](https://gitlab.fa-wi.de/punicawaikiki/edf-python-interface) has been implemented.
The connection was made over UDP and supports a 2^11 (2048) fast fourier transform (FFT). Therefore the interface generates a signal which consists of up to 8 signals with different frequencies and amplitudes. The interface shows the generated signal as well as the result of the fft ot the STM32-board.

![Demo Interface](https://gitlab.fa-wi.de/punicawaikiki/edf-python-interface/blob/master/pictures/demo.png)


## Installation

to be continued

## Preferences

In der Datei globals.py befinden sich alle nötigen Verbindungseinstellungen, diese sehen wie folgt aus:

```python
UDP_DESTINATION_IP = "192.168.1.5"  # destination ip address(stm32)
UDP_SOURCE_IP = "192.168.1.1"   # local ip address
UDP_SEND_PORT = 55556   # UDP port to send data to stm32
UDP_RECEIVE_PORT = 55555    # UDP port to receive data from stm32
SAMPLE_ARRAY_SIZE = 256     # UDP Packet size -> 256 floats with one paket will be send
EPOCHES = 8 # number of UDP pakets will be send for one calculation
NUMBER_OF_SAMPLES = int( SAMPLE_ARRAY_SIZE * EPOCHES ) # Number of Samples
FFT_SIZE = int( SAMPLE_ARRAY_SIZE * EPOCHES / 2 ) # FFT Size
FFT_EPOCHES = int(FFT_SIZE / SAMPLE_ARRAY_SIZE) # number of UDP pakets will be send back to host
```

## Usage

to be continued
