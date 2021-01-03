from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import sys
from numpy.lib.function_base import iterable
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
import socket
import struct
import heapq
from network import NetworkChecker, UDPReceiver
from globals import *
# import ptvsd


# create class for horizontal line without zoom
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

# create class for vertikal line without zoom
class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

# gui class
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # set window title
        self.setWindowTitle("EDF GUI")
        # set window size
        self.resize(1820, 980)
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
        # set local ip address
        self.sourceIpAddress = UDP_SOURCE_IP
        # set destination ip address
        self.destinationIpAddress = UDP_DESTINATION_IP

        # signal preferences
        # amplitude: -> set all init amplitudes to 1
        self.signalAmplitudes = [1, 1, 1]

        # signal frequencies
        self.signalFrequencies = [10, 20, 30]

        # signal curve preferences
        self.signalCurvePreferences = [True, True, True]
        
        # signal activated 
        self.signalsActivated = np.zeros(3, dtype=bool)
        self.combinedSignal = np.zeros(self.numberOfSamples, dtype=float)

        self.fftHighest = np.zeros(len(self.signalFrequencies))

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
        self.signal1FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[0]}')
        self.signal1FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal1FrequencyTextBox.setFixedWidth(50)
        self.signal1FrequencyLabelUnits = QLabel("Hz")
        self.signal1FrequencyLabelUnits.setFixedWidth(20)
        self.signal1CheckBox = QCheckBox("Activated")
        self.signal1CheckBox.stateChanged.connect(self.updateCheckBox1)
        self.signal1CurveMenu = QComboBox()
        self.signal1CurveMenu.addItem("Sine")
        self.signal1CurveMenu.addItem("Cosine")
        self.signal1CurveMenu.currentIndexChanged.connect(self.updateComboBox1)
        # User Frequency Signal 1 change Button
        self.signal1FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal1FrequencyButton.setFixedWidth(30)
        self.signal1FrequencyButton.clicked.connect(self.signal1FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal1AmplitudeLabel = QLabel("Amplitude:")
        self.signal1AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[0]}')
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
        self.signal2FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[1]}')
        self.signal2FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal2FrequencyTextBox.setFixedWidth(50)
        self.signal2FrequencyLabelUnits = QLabel("Hz")
        self.signal2FrequencyLabelUnits.setFixedWidth(20)
        self.signal2CheckBox = QCheckBox("Activated")
        self.signal2CheckBox.stateChanged.connect(self.updateCheckBox2)
        self.signal2CurveMenu = QComboBox()
        self.signal2CurveMenu.addItem("Sine")
        self.signal2CurveMenu.addItem("Cosine")
        self.signal2CurveMenu.currentIndexChanged.connect(self.updateComboBox2)
        # User Frequency Signal 2 change Button
        self.signal2FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal2FrequencyButton.setFixedWidth(30)
        self.signal2FrequencyButton.clicked.connect(self.signal2FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal2AmplitudeLabel = QLabel("Amplitude:")
        self.signal2AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[1]}')
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
        self.signal3FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[2]}')
        self.signal3FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal3FrequencyTextBox.setFixedWidth(50)
        self.signal3FrequencyLabelUnits = QLabel("Hz")
        self.signal3FrequencyLabelUnits.setFixedWidth(20)
        self.signal3CheckBox = QCheckBox("Activated")
        self.signal3CheckBox.stateChanged.connect(self.updateCheckBox3)
        self.signal3CurveMenu = QComboBox()
        self.signal3CurveMenu.addItem("Sine")
        self.signal3CurveMenu.addItem("Cosine")
        self.signal3CurveMenu.currentIndexChanged.connect(self.updateComboBox3)
        # User Frequency Signal 3 change Button
        self.signal3FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal3FrequencyButton.setFixedWidth(30)
        self.signal3FrequencyButton.clicked.connect(self.signal3FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal3AmplitudeLabel = QLabel("Amplitude:")
        self.signal3AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[2]}')
        self.signal3AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal3AmplitudeTextBox.setFixedWidth(50)
        self.signal3AmplitudeLabelUnits = QLabel("V")
        self.signal3AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 3 change Button
        self.signal3AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal3AmplitudeButton.setFixedWidth(30)
        self.signal3AmplitudeButton.clicked.connect(self.signal3AmplitudeButton_clicked)

        # -------------- Output Signal Plot ------------------
        # Creating Plot Label for Input Signal
        self.inputSignalLabel = QLabel("Input Signal to STM32")
        self.inputSignalLabel.setMaximumHeight(10)
        # creating a plot window for input Signals
        self.inputSignalPlot = pg.plot()
        # plot color
        pen = pg.mkPen(color=(105, 105, 105))
        # create input Signal for FreeRTOS
        self.inputSignal = pg.PlotCurveItem(x = self.time, y = self.combinedSignal, pen = pen)
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
        self.inputSignalPlot.setXRange(0, NUMBER_OF_SAMPLES, padding=0)

        # --------------- FFT Result Plot --------------------
        # Creating Plot Label for fft results
        self.fftResultsLabel = QLabel("FFT Result")
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
        self.fftResultsPlot.setXRange(0, FFT_SIZE, padding=0)
        self.fftResultsPlot.setBackground('w')

        # Creating a grid layout
        self.layout = QGridLayout()
        # setting this layout to the widget
        self.widget.setLayout(self.layout)

        # -------------------- widget positions -------------------
        # vertical and horizontal lines for limitations
        self.layout.addWidget(QVLine(), 1, 1, 45, 1)
        self.layout.addWidget(QHLine(), 1, 1, 1, 48)
        self.layout.addWidget(QHLine(), 3, 1, 1, 5)
        self.layout.addWidget(QHLine(), 8, 2, 1, 4)
        self.layout.addWidget(QHLine(), 13, 2, 1, 4)
        self.layout.addWidget(QHLine(), 18, 2, 1, 4)
        self.layout.addWidget(QVLine(), 1, 6, 45, 1)
        self.layout.addWidget(QHLine(), 24, 8, 1, 41)
        self.layout.addWidget(QHLine(), 46, 1, 1, 48)
        self.layout.addWidget(QVLine(), 1, 50, 45, 1)
        # connection status widget
        self.layout.addWidget(self.ConnectedIpAddressLabel, 2, 2, 1, 4)
        # signal 1 preferences
        self.layout.addWidget(self.signal1Label, 4, 1, 1, 5)
        self.layout.addWidget(self.signal1CheckBox, 5, 2, 1, 1)
        self.layout.addWidget(self.signal1CurveMenu, 5, 4, 1, 2)
        self.layout.addWidget(self.signal1FrequencyLabel, 6, 2, 1, 1)
        self.layout.addWidget(self.signal1FrequencyTextBox, 6, 3, 1, 1)
        self.layout.addWidget(self.signal1FrequencyLabelUnits, 6, 4, 1, 1)
        self.layout.addWidget(self.signal1FrequencyButton, 6, 5, 1, 1 )
        self.layout.addWidget(self.signal1AmplitudeLabel, 7, 2, 1, 1)
        self.layout.addWidget(self.signal1AmplitudeTextBox, 7, 3, 1, 1)
        self.layout.addWidget(self.signal1AmplitudeLabelUnits, 7, 4, 1, 1)
        self.layout.addWidget(self.signal1AmplitudeButton, 7, 5, 1, 1)
        # signal 2 preferences
        self.layout.addWidget(self.signal2Label, 9, 1, 1, 5)
        self.layout.addWidget(self.signal2CheckBox, 10, 2, 1, 1)
        self.layout.addWidget(self.signal2CurveMenu, 10, 4, 1, 2)
        self.layout.addWidget(self.signal2FrequencyLabel, 11, 2, 1, 1)
        self.layout.addWidget(self.signal2FrequencyTextBox, 11, 3, 1, 1)
        self.layout.addWidget(self.signal2FrequencyLabelUnits, 11, 4, 1, 1)
        self.layout.addWidget(self.signal2FrequencyButton, 11, 5, 1, 1 )
        self.layout.addWidget(self.signal2AmplitudeLabel, 12, 2, 1, 1)
        self.layout.addWidget(self.signal2AmplitudeTextBox, 12, 3, 1, 1)
        self.layout.addWidget(self.signal2AmplitudeLabelUnits, 12, 4, 1, 1)
        self.layout.addWidget(self.signal2AmplitudeButton, 12, 5, 1, 1)
        # signal 3 preferences
        self.layout.addWidget(self.signal3Label, 14, 1, 1, 5)
        self.layout.addWidget(self.signal3CheckBox, 15, 2, 1, 1)
        self.layout.addWidget(self.signal3CurveMenu, 15, 4, 1, 2)
        self.layout.addWidget(self.signal3FrequencyLabel, 16, 2, 1, 1)
        self.layout.addWidget(self.signal3FrequencyTextBox, 16, 3, 1, 1)
        self.layout.addWidget(self.signal3FrequencyLabelUnits, 16, 4, 1, 1)
        self.layout.addWidget(self.signal3FrequencyButton, 16, 5, 1, 1 )
        self.layout.addWidget(self.signal3AmplitudeLabel, 17, 2, 1, 1)
        self.layout.addWidget(self.signal3AmplitudeTextBox, 17, 3, 1, 1)
        self.layout.addWidget(self.signal3AmplitudeLabelUnits, 17, 4, 1, 1)
        self.layout.addWidget(self.signal3AmplitudeButton, 17, 5, 1, 1)
        # signal plot
        self.layout.addWidget(self.inputSignalLabel, 2, 7, 1, 42)
        self.layout.addWidget(self.inputSignalPlot, 3, 7, 20, 42)
        # fft result plot
        self.layout.addWidget(self.fftResultsLabel, 26, 7, 1, 42)
        self.layout.addWidget(self.fftResultsPlot, 27, 7, 20, 42)
        # setting this widget as central widget of the main window
        self.setCentralWidget(self.widget)

    # set window into center of screen
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # update combinedSignal
    def update_signals(self):
        # buffer time and data array
        udpPacketTime = np.zeros(self.sizeOfUDPPacket)
        udpPacketData = np.zeros(self.sizeOfUDPPacket)
        # check if counter reached maximum of self.epoches
        if self.epochesCnt == self.epoches:
            self.epochesCnt = 0
        # replace self.sizeOfUDPPacket elements in self.combinedSignal array
        for i in range(self.sizeOfUDPPacket):
            self.combinedSignal[i + self.epochesCnt * self.sizeOfUDPPacket] \
                = udpPacketData[i] \
                    = float(self.generate_sin_signals(i + self.epochesCnt * self.sizeOfUDPPacket))
            udpPacketTime[i] = float(i + self.epochesCnt * self.sizeOfUDPPacket)
        # send self.sizeOfUDPPacket elements to stm32
        self.udpSendData( udpPacketData = udpPacketData )
        # update plot data
        self.inputSignal.setData(self.time, self.combinedSignal)
        # increase epoch counter
        self.epochesCnt += 1

    # update fft result
    @QtCore.pyqtSlot(np.ndarray)
    def updateFFTData(self, data):
        tpCount = self.numberOfSamples
        values = np.arange(int(tpCount/2))
        self.fftOutput.setOpts(x = values, height = data)
        self.fftHighest = np.sort(heapq.nlargest(np.sum(self.signalsActivated), range(len(data)), key=data.__getitem__))[::-1]

    # set connection status
    @QtCore.pyqtSlot(str)
    def updateDestinationAddress(self, strData):
        self.ConnectedIpAddressLabel.setText(f'<font color="black">STM32 Status: </font>{strData}')

    # send combinedSignal over UDP
    def udpSendData(self, udpPacketData):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        sample_struct = struct.pack('1i 256f', self.epochesCnt, *udpPacketData)
        sock.sendto(sample_struct, (UDP_DESTINATION_IP, UDP_SEND_PORT))

    # generate combined signal
    def generate_sin_signals(self, time):
        generatedSignal = 0
        for signalIteration, status in enumerate(self.signalsActivated):
            if status:
                if self.signalCurvePreferences[signalIteration]:
                    generatedSignal = generatedSignal + self.signalAmplitudes[signalIteration] * np.sin(2 * np.pi * self.signalFrequencies[signalIteration] * time / self.numberOfSamples)
                else:
                    generatedSignal = generatedSignal + self.signalAmplitudes[signalIteration] * np.cos(2 * np.pi * self.signalFrequencies[signalIteration] * time / self.numberOfSamples)
        return generatedSignal

    # value of signal1FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal1FrequencyButton_clicked(self):
        self.signalFrequencies[0] = float(self.signal1FrequencyTextBox.text())

    # value of signal1AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal1AmplitudeButton_clicked(self):
        self.signalAmplitudes[0] = float(self.signal1AmplitudeTextBox.text())

    # value of signal2FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal2FrequencyButton_clicked(self):
        self.signalFrequencies[1] = float(self.signal2FrequencyTextBox.text())

    # value of signal2AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal2AmplitudeButton_clicked(self):
        self.signalAmplitudes[1] = float(self.signal2AmplitudeTextBox.text())

    # value of signal3FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal3FrequencyButton_clicked(self):
        self.signalFrequencies[2] = float(self.signal3FrequencyTextBox.text())

    # value of signal2AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal3AmplitudeButton_clicked(self):
        self.signalAmplitudes[2]= float(self.signal3AmplitudeTextBox.text())

    # check status of checkbox 1 to enable or disable signal
    def updateCheckBox1(self):
        if self.signalsActivated[0] == False:
            self.signalsActivated[0] = True
        else:
            self.signalsActivated[0] = False

    # check status of checkbox 2 to enable or disable signal
    def updateCheckBox2(self):
        if self.signalsActivated[1] == False:
            self.signalsActivated[1] = True
        else:
            self.signalsActivated[1] = False

    # check status of checkbox 3 to enable or disable signal
    def updateCheckBox3(self):
        if self.signalsActivated[2] == False:
            self.signalsActivated[2] = True
        else:
            self.signalsActivated[2] = False

    # update user choosen preference to plot
    def updateComboBox1(self):
        if self.signal1CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[0] = True
        else:
            self.signalCurvePreferences[0] = False

    # update user choosen preference to plot
    def updateComboBox2(self):
        if self.signal2CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[1] = True
        else:
            self.signalCurvePreferences[1] = False

    # update user choosen preference to plot
    def updateComboBox3(self):
        if self.signal3CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[2] = True
        else:
            self.signalCurvePreferences[2] = False




def main():
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()