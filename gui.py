from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import sys
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
import socket
import struct
from network import NetworkChecker, UDPReceiver
from globals import *
# import ptvsd


# create class for horizontal line
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("EDF GUI")
        self.resize(1920, 1080)
        # number of samples
        self.numberOfSamples = NUMBER_OF_SAMPLES
        # size of data array in one udp packet
        self.sizeOfUDPPacket = SAMPLE_ARRAY_SIZE
        # value of samples for fft combined from self.sizeOfUDPPacket * self.epoches
        self.epoches = EPOCHES
        # epoch counter for updating udp data and plot data
        self.epochesCnt = 0
        # init time array
        self.time = np.arange(self.numberOfSamples)
        # get local ip address
        # TODO: check if also working on linux
        self.sourceIpAddress = UDP_SOURCE_IP
        self.destinationIpAddress = UDP_DESTINATION_IP

        # sin signal preferences
        # amplitude:
        self.ampl1 = 1
        self.ampl2 = 2
        self.ampl3 = 3

        # # signal frequencies
        self.signal1Frequency = 10
        self.signal2Frequency = 50
        self.signal3Frequency = 200

        self.sinSignal = np.zeros(self.numberOfSamples)

        ## fft result variables
        self.fftResultsArray = np.zeros(FFT_SIZE)

        # thread for receiving udp data
        self.udpReceiver = UDPReceiver()
        self.thread1 = QtCore.QThread()
        self.udpReceiver.dataChanged.connect(self.updateFFTData)
        self.udpReceiver.moveToThread(self.thread1)
        self.thread1.started.connect(self.udpReceiver.process)
        self.thread1.start()

        # thread for checking if destination is reachable
        self.networkChecker = NetworkChecker()
        self.thread2 = QtCore.QThread()
        self.networkChecker.destinationStatus.connect(self.updateDestinationAddress)
        self.networkChecker.moveToThread(self.thread2)
        self.thread2.started.connect(self.networkChecker.checkDestination)
        self.thread2.start()
        # config window
        self.center()
        self.UiComponents()
        self.show()

        # create qt send timer
        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(10)
        self.timer1.timeout.connect(self.update_signals)
        self.timer1.start()

        # start pyqtsignal


    def UiComponents(self):
        # creating a widget object
        self.widget = QWidget()

        # IP Address of Connected Device
        self.ConnectedIpAddressLabel = QLabel(f'STM32 Status: -')
        self.ConnectedIpAddressLabel.setAlignment(QtCore.Qt.AlignCenter)

        # --------- Signal 1 --------
        # Frequency Widgets
        self.signal1Label = QLabel("Signal 1")
        self.signal1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal1FrequencyLabel = QLabel("Frequency:")
        self.signal1FrequencyTextBox = QLineEdit(f'{self.signal1Frequency}')
        self.signal1FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal1FrequencyTextBox.setFixedWidth(50)
        self.signal1FrequencyLabelUnits = QLabel("Hz")
        self.signal1FrequencyLabelUnits.setFixedWidth(20)
        # User Frequency Signal 1 change Button
        self.signal1FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal1FrequencyButton.setFixedWidth(30)
        self.signal1FrequencyButton.clicked.connect(self.signal1FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal1AmplitudeLabel = QLabel("Amplitude:")
        self.signal1AmplitudeTextBox = QLineEdit(f'{self.ampl1}')
        self.signal1AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal1AmplitudeTextBox.setFixedWidth(50)
        self.signal1AmplitudeLabelUnits = QLabel("V")
        self.signal1AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 1 change Button
        self.signal1AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal1AmplitudeButton.setFixedWidth(30)
        self.signal1AmplitudeButton.clicked.connect(self.signal1AmplitudeButton_clicked)

        # --------- Signal 2 --------
        # Frequency Widgets
        self.signal2Label = QLabel("Signal 2")
        self.signal2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal2FrequencyLabel = QLabel("Frequency:")
        self.signal2FrequencyTextBox = QLineEdit(f'{self.signal2Frequency}')
        self.signal2FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal2FrequencyTextBox.setFixedWidth(50)
        self.signal2FrequencyLabelUnits = QLabel("Hz")
        self.signal2FrequencyLabelUnits.setFixedWidth(20)
        # User Frequency Signal 2 change Button
        self.signal2FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal2FrequencyButton.setFixedWidth(30)
        self.signal2FrequencyButton.clicked.connect(self.signal2FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal2AmplitudeLabel = QLabel("Amplitude:")
        self.signal2AmplitudeTextBox = QLineEdit(f'{self.ampl2}')
        self.signal2AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal2AmplitudeTextBox.setFixedWidth(50)
        self.signal2AmplitudeLabelUnits = QLabel("V")
        self.signal2AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 2 change Button
        self.signal2AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal2AmplitudeButton.setFixedWidth(30)
        self.signal2AmplitudeButton.clicked.connect(self.signal2AmplitudeButton_clicked)

        # --------- Signal 3 --------
        # Frequency Widgets
        self.signal3Label = QLabel("Signal 3")
        self.signal3Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal3FrequencyLabel = QLabel("Frequency:")
        self.signal3FrequencyTextBox = QLineEdit(f'{self.signal3Frequency}')
        self.signal3FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal3FrequencyTextBox.setFixedWidth(50)
        self.signal3FrequencyLabelUnits = QLabel("Hz")
        self.signal3FrequencyLabelUnits.setFixedWidth(20)
        # User Frequency Signal 3 change Button
        self.signal3FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal3FrequencyButton.setFixedWidth(30)
        self.signal3FrequencyButton.clicked.connect(self.signal3FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal3AmplitudeLabel = QLabel("Amplitude:")
        self.signal3AmplitudeTextBox = QLineEdit(f'{self.ampl3}')
        self.signal3AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal3AmplitudeTextBox.setFixedWidth(50)
        self.signal3AmplitudeLabelUnits = QLabel("V")
        self.signal3AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 3 change Button
        self.signal3AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal3AmplitudeButton.setFixedWidth(30)
        self.signal3AmplitudeButton.clicked.connect(self.signal3AmplitudeButton_clicked)

        # Creating Plot Label for Input Signal
        self.inputSignalLabel = QLabel("Input Signal to STM32")
        self.inputSignalLabel.setMaximumHeight(10)
        # creating a plot window for input Signals
        self.inputSignalPlot = pg.plot()
        # plot color
        pen = pg.mkPen(color=(105, 105, 105))
        # create input Signal for FreeRTOS
        self.inputSignal = pg.PlotCurveItem(x = self.time, y = self.sinSignal, pen = pen)
        # add item to plot window
        self.inputSignalPlot.addItem(self.inputSignal)
        # set plot properties
        # self.inputSignalPlot.setXRange(0, 1024, padding=0)
        self.inputSignalPlot.setBackground('w')
        # add grid
        self.inputSignalGrid = pg.GridItem()
        self.inputSignalPlot.addItem(self.inputSignalGrid)
        # hide x and y axis
        self.inputSignalPlot.getPlotItem().hideAxis('bottom')
        self.inputSignalPlot.getPlotItem().hideAxis('left')

        # Creating Plot Label for fft results
        self.fftResultsLabel = QLabel("FFT Results")
        self.fftResultsLabel.setMaximumHeight(10)
        # creating a plot window for fft
        self.fftResultsPlot = pg.plot()
        # plot color
        pen = pg.mkPen(color=(0, 0, 0))
        # create fft Output signals
        self.fftOutput = pg.BarGraphItem(x = np.zeros(self.numberOfSamples), height = np.zeros(self.numberOfSamples), width=0.8, fillLevel=1, brush=(105, 105, 105))  
        # add item to plot window
        self.fftResultsPlot.addItem(self.fftOutput)
        # set plot properties
        self.fftResultsPlot.setXRange(0, 512, padding=0)
        self.fftResultsPlot.setBackground('w')

        # Creating a grid layout
        self.layout = QGridLayout()
        # setting this layout to the widget
        self.widget.setLayout(self.layout)

        # plot window goes on right side, spanning 3 rows
        self.layout.addWidget(QVLine(), 1, 1, 45, 1)
        self.layout.addWidget(QHLine(), 1, 1, 1, 48)
        self.layout.addWidget(self.ConnectedIpAddressLabel, 2, 2, 1, 4)
        self.layout.addWidget(QHLine(), 3, 1, 1, 8)
        self.layout.addWidget(self.signal1Label, 4, 3, 1, 3)
        self.layout.addWidget(self.signal1FrequencyLabel, 5, 2, 1, 2)
        self.layout.addWidget(self.signal1FrequencyTextBox, 5, 4, 1, 1)
        self.layout.addWidget(self.signal1FrequencyLabelUnits, 5, 5, 1, 1)
        self.layout.addWidget(self.signal1FrequencyButton, 5, 6, 1, 1 )
        self.layout.addWidget(self.signal1AmplitudeLabel, 6, 2, 1, 2)
        self.layout.addWidget(self.signal1AmplitudeTextBox, 6, 4, 1, 1)
        self.layout.addWidget(self.signal1AmplitudeLabelUnits, 6, 5, 1, 1)
        self.layout.addWidget(self.signal1AmplitudeButton, 6, 6, 1, 1)
        self.layout.addWidget(QHLine(), 7, 2, 1, 7)
        self.layout.addWidget(self.signal2Label, 8, 3, 1, 3)
        self.layout.addWidget(self.signal2FrequencyLabel, 9, 2, 1, 2)
        self.layout.addWidget(self.signal2FrequencyTextBox, 9, 4, 1, 1)
        self.layout.addWidget(self.signal2FrequencyLabelUnits, 9, 5, 1, 1)
        self.layout.addWidget(self.signal2FrequencyButton, 9, 6, 1, 1 )
        self.layout.addWidget(self.signal2AmplitudeLabel, 10, 2, 1, 2)
        self.layout.addWidget(self.signal2AmplitudeTextBox, 10, 4, 1, 1)
        self.layout.addWidget(self.signal2AmplitudeLabelUnits, 10, 5, 1, 1)
        self.layout.addWidget(self.signal2AmplitudeButton, 10, 6, 1, 1)
        self.layout.addWidget(QHLine(), 11, 2, 1, 7)
        self.layout.addWidget(self.signal3Label, 12, 3, 1, 3)
        self.layout.addWidget(self.signal3FrequencyLabel, 13, 2, 1, 2)
        self.layout.addWidget(self.signal3FrequencyTextBox, 13, 4, 1, 1)
        self.layout.addWidget(self.signal3FrequencyLabelUnits, 13, 5, 1, 1)
        self.layout.addWidget(self.signal3FrequencyButton, 13, 6, 1, 1 )
        self.layout.addWidget(self.signal3AmplitudeLabel, 14, 2, 1, 2)
        self.layout.addWidget(self.signal3AmplitudeTextBox, 14, 4, 1, 1)
        self.layout.addWidget(self.signal3AmplitudeLabelUnits, 14, 5, 1, 1)
        self.layout.addWidget(self.signal3AmplitudeButton, 14, 6, 1, 1)
        self.layout.addWidget(QHLine(), 15, 2, 1, 7)
        self.layout.addWidget(QVLine(), 1, 8, 45, 1)
        self.layout.addWidget(self.inputSignalLabel, 2, 9, 1, 40)
        self.layout.addWidget(self.inputSignalPlot, 3, 9, 20, 40)
        self.layout.addWidget(QHLine(), 23, 8, 1, 41)
        self.layout.addWidget(self.fftResultsLabel, 24, 9, 1, 40)
        self.layout.addWidget(self.fftResultsPlot, 25, 9, 20, 40)
        self.layout.addWidget(QHLine(), 45, 1, 1, 48)
        self.layout.addWidget(QVLine(), 1, 50, 45, 1)
        # setting this widget as central widget of the main window
        self.setCentralWidget(self.widget)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_signals(self):
        # buffer time and data array
        udpPacketTime = np.zeros(self.sizeOfUDPPacket)
        udpPacketData = np.zeros(self.sizeOfUDPPacket)
        # check if counter reached maximum of self.epoches
        if self.epochesCnt == self.epoches:
            self.epochesCnt = 0
        # replace self.sizeOfUDPPacket elements in self.sinSignal array
        for i in range(self.sizeOfUDPPacket):
            self.sinSignal[i + self.epochesCnt * self.sizeOfUDPPacket] \
                = udpPacketData[i] \
                    = float(self.generate_sin_signals(i + self.epochesCnt * self.sizeOfUDPPacket))
            udpPacketTime[i] = float(i + self.epochesCnt * self.sizeOfUDPPacket)
        # send self.sizeOfUDPPacket elements to stm32
        self.udpSendData( udpPacketData = udpPacketData )
        # update plot data
        self.inputSignal.setData(self.time, self.sinSignal)
        # increase epoch counter
        self.epochesCnt += 1

    @QtCore.pyqtSlot(np.ndarray)
    def updateFFTData(self, data):
        tpCount = self.numberOfSamples
        values = np.arange(int(tpCount/2))
        # self.fftOutput.setData(values, data)
        self.fftOutput.setOpts(x = values, height = data)
        max_index_col = np.argmax(data, axis=0)
        # print('FFT Data Updated')

    @QtCore.pyqtSlot(str)
    def updateDestinationAddress(self, strData):
        self.ConnectedIpAddressLabel.setText(f'<font color="black">STM32 Status: </font>{strData}')

    def udpSendData(self, udpPacketData):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        sample_struct = struct.pack('1i 256f', self.epochesCnt, *udpPacketData)
        sock.sendto(sample_struct, (UDP_DESTINATION_IP, UDP_SEND_PORT))


    def generate_sin_signals(self, time):
        amplitude1 = self.ampl1 * np.sin(2 * np.pi * self.signal1Frequency * time / self.numberOfSamples)
        amplitude2 = self.ampl2 * np.sin(2 * np.pi * self.signal2Frequency * time / self.numberOfSamples)
        amplitude3 = self.ampl3 * np.sin(2 * np.pi * self.signal3Frequency * time / self.numberOfSamples)
        return amplitude1 + amplitude2 + amplitude3

    # value of signal1FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal1FrequencyButton_clicked(self):
        self.signal1Frequency = int(self.signal1FrequencyTextBox.text())

    # value of signal1AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal1AmplitudeButton_clicked(self):
        self.ampl1 = float(self.signal1AmplitudeTextBox.text())

    # value of signal2FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal2FrequencyButton_clicked(self):
        self.signal2Frequency = int(self.signal2FrequencyTextBox.text())

    # value of signal2AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal2AmplitudeButton_clicked(self):
        self.ampl2 = float(self.signal2AmplitudeTextBox.text())

    # value of signal3FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal3FrequencyButton_clicked(self):
        self.signal3Frequency = int(self.signal3FrequencyTextBox.text())

    # value of signal2AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal3AmplitudeButton_clicked(self):
        self.ampl3 = float(self.signal3AmplitudeTextBox.text())


def main():
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()