# Earliest Deadline First (EDF) Python Interface

This project serves as an interface to connect to a [STM32F769I-Disc0](https://www.st.com/en/evaluation-tools/32f769idiscovery.html) board on which an [EDF Scheduler](https://gitlab.fa-wi.de/punicawaikiki/freertos-ethernet-edf) has been implemented.
The connection was made over UDP and supports a 2048 fast fourier transform (FFT). Therefore the interface generates a signal which consists of up to 8 signals with different frequencies and amplitudes. The interface shows the generated signal as well as the result of the fft ot the STM32-board.

![Demo Interface](http://gitlab.fa-wi.de/punicawaikiki/edf-python-interface/-/raw/master/pictures/demo.png)

## Installation

* If you only want to use the interface with no custom modifications, you need to download the "dist" folder and execute "gui.exe" (only for windows machines).
* When you want to modify this project by yourself, you need to clone this repository and activate the python virtual environment ([venv](https://docs.python.org/3/library/venv.html)). The advantage of this use is the independence of the platform is used, like windows, linux or mac.
## Properties

In the file globals.py you will find all necessary connection settings, the look like this:

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

In the left upper corner is a status indicator, which tells you the connection state to the STM32 board.
Below the status indicator, there are 8 Signals with predefined signal properties and all deactivated on startup. Here you can activate and/or modify every signal.
In the upper half of the whole gui there will be displayed the resulting signal of all user choosen signal properties.
In the lower half of the interface there will be the result of the FFT-Calculation displayed.

## Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

