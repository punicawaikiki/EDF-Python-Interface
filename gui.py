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
        self.signalAmplitudes = [1, 1, 1, 1, 1, 1, 1 ,1]

        # signal frequencies
        self.signalFrequencies = [10, 20, 30, 40, 50, 60, 70, 80]

        # signal curve preferences
        self.signalCurvePreferences = [True, True, True, True, True, True, True, True]
        
        # signal activated 
        self.signalsActivated = np.zeros(8, dtype=bool)
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

        # --------- Signal 4 --------
        # Frequency Widgets
        self.signal4Label = QLabel("Signal 4")
        self.signal4Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal4FrequencyLabel = QLabel("Frequency:")
        self.signal4FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[3]}')
        self.signal4FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal4FrequencyTextBox.setFixedWidth(50)
        self.signal4FrequencyLabelUnits = QLabel("Hz")
        self.signal4FrequencyLabelUnits.setFixedWidth(20)
        self.signal4CheckBox = QCheckBox("Activated")
        self.signal4CheckBox.stateChanged.connect(self.updateCheckBox4)
        self.signal4CurveMenu = QComboBox()
        self.signal4CurveMenu.addItem("Sine")
        self.signal4CurveMenu.addItem("Cosine")
        self.signal4CurveMenu.currentIndexChanged.connect(self.updateComboBox4)
        # User Frequency Signal 4 change Button
        self.signal4FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal4FrequencyButton.setFixedWidth(40)
        self.signal4FrequencyButton.clicked.connect(self.signal4FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal4AmplitudeLabel = QLabel("Amplitude:")
        self.signal4AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[3]}')
        self.signal4AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal4AmplitudeTextBox.setFixedWidth(50)
        self.signal4AmplitudeLabelUnits = QLabel("V")
        self.signal4AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 4 change Button
        self.signal4AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal4AmplitudeButton.setFixedWidth(40)
        self.signal4AmplitudeButton.clicked.connect(self.signal4AmplitudeButton_clicked)

        # --------- Signal 5 --------
        # Frequency Widgets
        self.signal5Label = QLabel("Signal 5")
        self.signal5Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal5FrequencyLabel = QLabel("Frequency:")
        self.signal5FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[4]}')
        self.signal5FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal5FrequencyTextBox.setFixedWidth(50)
        self.signal5FrequencyLabelUnits = QLabel("Hz")
        self.signal5FrequencyLabelUnits.setFixedWidth(20)
        self.signal5CheckBox = QCheckBox("Activated")
        self.signal5CheckBox.stateChanged.connect(self.updateCheckBox5)
        self.signal5CurveMenu = QComboBox()
        self.signal5CurveMenu.addItem("Sine")
        self.signal5CurveMenu.addItem("Cosine")
        self.signal5CurveMenu.currentIndexChanged.connect(self.updateComboBox5)
        # User Frequency Signal 5 change Button
        self.signal5FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal5FrequencyButton.setFixedWidth(40)
        self.signal5FrequencyButton.clicked.connect(self.signal5FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal5AmplitudeLabel = QLabel("Amplitude:")
        self.signal5AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[4]}')
        self.signal5AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal5AmplitudeTextBox.setFixedWidth(50)
        self.signal5AmplitudeLabelUnits = QLabel("V")
        self.signal5AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 5 change Button
        self.signal5AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal5AmplitudeButton.setFixedWidth(40)
        self.signal5AmplitudeButton.clicked.connect(self.signal5AmplitudeButton_clicked)

        # --------- Signal 6 --------
        # Frequency Widgets
        self.signal6Label = QLabel("Signal 6")
        self.signal6Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal6FrequencyLabel = QLabel("Frequency:")
        self.signal6FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[5]}')
        self.signal6FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal6FrequencyTextBox.setFixedWidth(50)
        self.signal6FrequencyLabelUnits = QLabel("Hz")
        self.signal6FrequencyLabelUnits.setFixedWidth(20)
        self.signal6CheckBox = QCheckBox("Activated")
        self.signal6CheckBox.stateChanged.connect(self.updateCheckBox6)
        self.signal6CurveMenu = QComboBox()
        self.signal6CurveMenu.addItem("Sine")
        self.signal6CurveMenu.addItem("Cosine")
        self.signal6CurveMenu.currentIndexChanged.connect(self.updateComboBox6)
        # User Frequency Signal 6 change Button
        self.signal6FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal6FrequencyButton.setFixedWidth(40)
        self.signal6FrequencyButton.clicked.connect(self.signal6FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal6AmplitudeLabel = QLabel("Amplitude:")
        self.signal6AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[5]}')
        self.signal6AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal6AmplitudeTextBox.setFixedWidth(50)
        self.signal6AmplitudeLabelUnits = QLabel("V")
        self.signal6AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 6 change Button
        self.signal6AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal6AmplitudeButton.setFixedWidth(40)
        self.signal6AmplitudeButton.clicked.connect(self.signal6AmplitudeButton_clicked)

        # --------- Signal 7 --------
        # Frequency Widgets
        self.signal7Label = QLabel("Signal 7")
        self.signal7Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal7FrequencyLabel = QLabel("Frequency:")
        self.signal7FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[6]}')
        self.signal7FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal7FrequencyTextBox.setFixedWidth(50)
        self.signal7FrequencyLabelUnits = QLabel("Hz")
        self.signal7FrequencyLabelUnits.setFixedWidth(20)
        self.signal7CheckBox = QCheckBox("Activated")
        self.signal7CheckBox.stateChanged.connect(self.updateCheckBox7)
        self.signal7CurveMenu = QComboBox()
        self.signal7CurveMenu.addItem("Sine")
        self.signal7CurveMenu.addItem("Cosine")
        self.signal7CurveMenu.currentIndexChanged.connect(self.updateComboBox7)
        # User Frequency Signal 7 change Button
        self.signal7FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal7FrequencyButton.setFixedWidth(40)
        self.signal7FrequencyButton.clicked.connect(self.signal7FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal7AmplitudeLabel = QLabel("Amplitude:")
        self.signal7AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[6]}')
        self.signal7AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal7AmplitudeTextBox.setFixedWidth(50)
        self.signal7AmplitudeLabelUnits = QLabel("V")
        self.signal7AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 7 change Button
        self.signal7AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal7AmplitudeButton.setFixedWidth(40)
        self.signal7AmplitudeButton.clicked.connect(self.signal7AmplitudeButton_clicked)

        # --------- Signal 8 --------
        # Frequency Widgets
        self.signal8Label = QLabel("Signal 8")
        self.signal8Label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal8FrequencyLabel = QLabel("Frequency:")
        self.signal8FrequencyTextBox = QLineEdit(f'{self.signalFrequencies[7]}')
        self.signal8FrequencyTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal8FrequencyTextBox.setFixedWidth(50)
        self.signal8FrequencyLabelUnits = QLabel("Hz")
        self.signal8FrequencyLabelUnits.setFixedWidth(20)
        self.signal8CheckBox = QCheckBox("Activated")
        self.signal8CheckBox.stateChanged.connect(self.updateCheckBox8)
        self.signal8CurveMenu = QComboBox()
        self.signal8CurveMenu.addItem("Sine")
        self.signal8CurveMenu.addItem("Cosine")
        self.signal8CurveMenu.currentIndexChanged.connect(self.updateComboBox8)
        # User Frequency Signal 8 change Button
        self.signal8FrequencyButton = QPushButton('OK')
        # setting geometry of button
        self.signal8FrequencyButton.setFixedWidth(40)
        self.signal8FrequencyButton.clicked.connect(self.signal8FrequencyButton_clicked)
        # Amplitude Widgets
        self.signal8AmplitudeLabel = QLabel("Amplitude:")
        self.signal8AmplitudeTextBox = QLineEdit(f'{self.signalAmplitudes[7]}')
        self.signal8AmplitudeTextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signal8AmplitudeTextBox.setFixedWidth(50)
        self.signal8AmplitudeLabelUnits = QLabel("V")
        self.signal8AmplitudeLabelUnits.setFixedWidth(20)
        # User Frequency Signal 8 change Button
        self.signal8AmplitudeButton = QPushButton('OK')
        # setting geometry of button
        self.signal8AmplitudeButton.setFixedWidth(40)
        self.signal8AmplitudeButton.clicked.connect(self.signal8AmplitudeButton_clicked)

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

        # create highest frequencies found
        self.fftFrequenciesResults = QLabel("")

        # -------------------- widget positions -------------------
        # vertical and horizontal lines for limitations
        self.layout.addWidget(QVLine(), 1, 1, 46, 1)
        self.layout.addWidget(QHLine(), 1, 1, 1, 48)
        self.layout.addWidget(QHLine(), 3, 1, 1, 5)
        self.layout.addWidget(QHLine(), 8, 2, 1, 4)
        self.layout.addWidget(QHLine(), 13, 2, 1, 4)
        self.layout.addWidget(QHLine(), 18, 2, 1, 4)
        self.layout.addWidget(QHLine(), 23, 2, 1, 4)
        self.layout.addWidget(QHLine(), 28, 2, 1, 4)
        self.layout.addWidget(QHLine(), 33, 2, 1, 4)
        self.layout.addWidget(QHLine(), 38, 2, 1, 4)
        self.layout.addWidget(QVLine(), 1, 6, 46, 1)
        self.layout.addWidget(QHLine(), 23, 6, 1, 41)
        self.layout.addWidget(QHLine(), 47, 1, 1, 48)
        self.layout.addWidget(QVLine(), 1, 50, 46, 1)
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
        # signal 4 preferences
        self.layout.addWidget(self.signal4Label, 19, 1, 1, 5)
        self.layout.addWidget(self.signal4CheckBox, 20, 2, 1, 1)
        self.layout.addWidget(self.signal4CurveMenu, 20, 4, 1, 2)
        self.layout.addWidget(self.signal4FrequencyLabel, 21, 2, 1, 1)
        self.layout.addWidget(self.signal4FrequencyTextBox, 21, 3, 1, 1)
        self.layout.addWidget(self.signal4FrequencyLabelUnits, 21, 4, 1, 1)
        self.layout.addWidget(self.signal4FrequencyButton, 21, 5, 1, 1 )
        self.layout.addWidget(self.signal4AmplitudeLabel, 22, 2, 1, 1)
        self.layout.addWidget(self.signal4AmplitudeTextBox, 22, 3, 1, 1)
        self.layout.addWidget(self.signal4AmplitudeLabelUnits, 22, 4, 1, 1)
        self.layout.addWidget(self.signal4AmplitudeButton, 22, 5, 1, 1)

        # signal 5 preferences
        self.layout.addWidget(self.signal5Label, 24, 1, 1, 5)
        self.layout.addWidget(self.signal5CheckBox, 25, 2, 1, 1)
        self.layout.addWidget(self.signal5CurveMenu, 25, 4, 1, 2)
        self.layout.addWidget(self.signal5FrequencyLabel, 26, 2, 1, 1)
        self.layout.addWidget(self.signal5FrequencyTextBox, 26, 3, 1, 1)
        self.layout.addWidget(self.signal5FrequencyLabelUnits, 26, 4, 1, 1)
        self.layout.addWidget(self.signal5FrequencyButton, 26, 5, 1, 1 )
        self.layout.addWidget(self.signal5AmplitudeLabel, 27, 2, 1, 1)
        self.layout.addWidget(self.signal5AmplitudeTextBox, 27, 3, 1, 1)
        self.layout.addWidget(self.signal5AmplitudeLabelUnits, 27, 4, 1, 1)
        self.layout.addWidget(self.signal5AmplitudeButton, 27, 5, 1, 1)

        # signal 6 preferences
        self.layout.addWidget(self.signal6Label, 29, 1, 1, 5)
        self.layout.addWidget(self.signal6CheckBox, 30, 2, 1, 1)
        self.layout.addWidget(self.signal6CurveMenu, 30, 4, 1, 2)
        self.layout.addWidget(self.signal6FrequencyLabel, 31, 2, 1, 1)
        self.layout.addWidget(self.signal6FrequencyTextBox, 31, 3, 1, 1)
        self.layout.addWidget(self.signal6FrequencyLabelUnits, 31, 4, 1, 1)
        self.layout.addWidget(self.signal6FrequencyButton, 31, 5, 1, 1 )
        self.layout.addWidget(self.signal6AmplitudeLabel, 32, 2, 1, 1)
        self.layout.addWidget(self.signal6AmplitudeTextBox, 32, 3, 1, 1)
        self.layout.addWidget(self.signal6AmplitudeLabelUnits, 32, 4, 1, 1)
        self.layout.addWidget(self.signal6AmplitudeButton, 32, 5, 1, 1)

        # signal 7 preferences
        self.layout.addWidget(self.signal7Label, 34, 1, 1, 5)
        self.layout.addWidget(self.signal7CheckBox, 35, 2, 1, 1)
        self.layout.addWidget(self.signal7CurveMenu, 35, 4, 1, 2)
        self.layout.addWidget(self.signal7FrequencyLabel, 36, 2, 1, 1)
        self.layout.addWidget(self.signal7FrequencyTextBox, 36, 3, 1, 1)
        self.layout.addWidget(self.signal7FrequencyLabelUnits, 36, 4, 1, 1)
        self.layout.addWidget(self.signal7FrequencyButton, 36, 5, 1, 1 )
        self.layout.addWidget(self.signal7AmplitudeLabel, 37, 2, 1, 1)
        self.layout.addWidget(self.signal7AmplitudeTextBox, 37, 3, 1, 1)
        self.layout.addWidget(self.signal7AmplitudeLabelUnits, 37, 4, 1, 1)
        self.layout.addWidget(self.signal7AmplitudeButton, 37, 5, 1, 1)

        # signal 8 preferences
        self.layout.addWidget(self.signal8Label, 39, 1, 1, 5)
        self.layout.addWidget(self.signal8CheckBox, 40, 2, 1, 1)
        self.layout.addWidget(self.signal8CurveMenu, 40, 4, 1, 2)
        self.layout.addWidget(self.signal8FrequencyLabel, 41, 2, 1, 1)
        self.layout.addWidget(self.signal8FrequencyTextBox, 41, 3, 1, 1)
        self.layout.addWidget(self.signal8FrequencyLabelUnits, 41, 4, 1, 1)
        self.layout.addWidget(self.signal8FrequencyButton, 41, 5, 1, 1 )
        self.layout.addWidget(self.signal8AmplitudeLabel, 42, 2, 1, 1)
        self.layout.addWidget(self.signal8AmplitudeTextBox, 42, 3, 1, 1)
        self.layout.addWidget(self.signal8AmplitudeLabelUnits, 42, 4, 1, 1)
        self.layout.addWidget(self.signal8AmplitudeButton, 42, 5, 1, 1)

        # signal plot
        self.layout.addWidget(self.inputSignalLabel, 2, 7, 1, 42)
        self.layout.addWidget(self.inputSignalPlot, 3, 7, 20, 42)
        # fft result plot
        self.layout.addWidget(self.fftResultsLabel, 24, 7, 1, 42)
        self.layout.addWidget(self.fftResultsPlot, 25, 7, 20, 42)

        # detected frequency results
        self.layout.addWidget(self.fftFrequenciesResults, 46, 24, 1, 25) 

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
        stringBuffer = '<font color="black">Calculated Frequencies: </font>'
        tpCount = self.numberOfSamples
        values = np.arange(int(tpCount/2))
        self.fftOutput.setOpts(x = values, height = data)
        self.fftHighest = np.sort(heapq.nlargest(np.sum(self.signalsActivated), range(len(data)), key=data.__getitem__))
        for frequence in self.fftHighest:
            stringBuffer = stringBuffer + f'</font><font color="blue">{frequence}Hz              </font>'
        self.fftFrequenciesResults.setText(stringBuffer)

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

    # value of signal3AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal3AmplitudeButton_clicked(self):
        self.signalAmplitudes[2]= float(self.signal3AmplitudeTextBox.text())

    # value of signal4FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal4FrequencyButton_clicked(self):
        self.signalFrequencies[3] = float(self.signal4FrequencyTextBox.text())

    # value of signal4AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal4AmplitudeButton_clicked(self):
        self.signalAmplitudes[3]= float(self.signal4AmplitudeTextBox.text())

    # value of signal5FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal5FrequencyButton_clicked(self):
        self.signalFrequencies[4] = float(self.signal5FrequencyTextBox.text())

    # value of signal5AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal5AmplitudeButton_clicked(self):
        self.signalAmplitudes[4]= float(self.signal5AmplitudeTextBox.text())

    # value of signal6FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal6FrequencyButton_clicked(self):
        self.signalFrequencies[5] = float(self.signal6FrequencyTextBox.text())

    # value of signal6AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal6AmplitudeButton_clicked(self):
        self.signalAmplitudes[5]= float(self.signal6AmplitudeTextBox.text())

    # value of signal7FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal7FrequencyButton_clicked(self):
        self.signalFrequencies[6] = float(self.signal7FrequencyTextBox.text())

    # value of signal7AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal7AmplitudeButton_clicked(self):
        self.signalAmplitudes[6]= float(self.signal7AmplitudeTextBox.text())

    # value of signal8FrequencyTextbox has changed
    @QtCore.pyqtSlot()
    def signal8FrequencyButton_clicked(self):
        self.signalFrequencies[7] = float(self.signal8FrequencyTextBox.text())

    # value of signal8AmplitudeTextBox has changed
    @QtCore.pyqtSlot()
    def signal8AmplitudeButton_clicked(self):
        self.signalAmplitudes[7]= float(self.signal8AmplitudeTextBox.text())

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

    # check status of checkbox 4 to enable or disable signal
    def updateCheckBox4(self):
        if self.signalsActivated[3] == False:
            self.signalsActivated[3] = True
        else:
            self.signalsActivated[3] = False

    # check status of checkbox 5 to enable or disable signal
    def updateCheckBox5(self):
        if self.signalsActivated[4] == False:
            self.signalsActivated[4] = True
        else:
            self.signalsActivated[4] = False

    # check status of checkbox 6 to enable or disable signal
    def updateCheckBox6(self):
        if self.signalsActivated[5] == False:
            self.signalsActivated[5] = True
        else:
            self.signalsActivated[5] = False

    # check status of checkbox 7 to enable or disable signal
    def updateCheckBox7(self):
        if self.signalsActivated[6] == False:
            self.signalsActivated[6] = True
        else:
            self.signalsActivated[6] = False

    # check status of checkbox 8 to enable or disable signal
    def updateCheckBox8(self):
        if self.signalsActivated[7] == False:
            self.signalsActivated[7] = True
        else:
            self.signalsActivated[7] = False

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

    # update user choosen preference to plot
    def updateComboBox4(self):
        if self.signal4CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[3] = True
        else:
            self.signalCurvePreferences[3] = False

    # update user choosen preference to plot
    def updateComboBox5(self):
        if self.signal5CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[4] = True
        else:
            self.signalCurvePreferences[4] = False

    # update user choosen preference to plot
    def updateComboBox6(self):
        if self.signal6CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[5] = True
        else:
            self.signalCurvePreferences[5] = False

    # update user choosen preference to plot
    def updateComboBox7(self):
        if self.signal7CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[6] = True
        else:
            self.signalCurvePreferences[6] = False

    # update user choosen preference to plot
    def updateComboBox8(self):
        if self.signal8CurveMenu.currentText() == "Sine":
            self.signalCurvePreferences[7] = True
        else:
            self.signalCurvePreferences[7] = False



def main():
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()