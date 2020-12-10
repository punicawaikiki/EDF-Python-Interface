from PyQt5 import QtCore
# importing Qt widgets 
from PyQt5.QtWidgets import *
import sys 
# from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import numpy as np
from random import randint

# Create own class for PlotCurveItem to ignore mouse wheel
class MyPlotCurveItem(pg.PlotCurveItem):
    def wheelEvent(self, event):
        event.accept()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("EDF GUI")
        self.resize(1920, 1080)
        # # number of samples
        self.numberOfSamples = 1024
        self.time = np.arange(self.numberOfSamples)

        # sin signal preferences
        # amplitude:
        self.ampl1 = 1
        self.ampl2 = 2
        self.ampl3 = 3

        # # signal frequencies
        self.signalFrequency1 = 10
        self.signalFrequency2 = 50
        self.signalFrequency3 = 200

        self.center()
        self.UiComponents()
        self.show()

    def UiComponents(self):
        # creating a widget object 
        self.widget = QWidget() 

        # User Frequency Signal 1
        self.signalFrequency1Label = QLabel("Signal 1 Frequency")
        self.signalFrequency1TextBox = QLineEdit(f'{self.signalFrequency1}')
        self.signalFrequency1TextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signalFrequency1TextBox.setFixedWidth(100)
        self.signalFrequency1LabelUnits = QLabel("Hz")

        # User Frequency Signal 2
        self.signalFrequency2Label = QLabel("Signal 2 Frequency")
        self.signalFrequency2TextBox = QLineEdit(f'{self.signalFrequency2}')
        self.signalFrequency2TextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signalFrequency2TextBox.setFixedWidth(100)
        self.signalFrequency2LabelUnits = QLabel("Hz")

        # User Frequency Signal 3
        self.signalFrequency3Label = QLabel("Signal 3 Frequency")
        self.signalFrequency3TextBox = QLineEdit(f'{self.signalFrequency3}')
        self.signalFrequency3TextBox.setAlignment(QtCore.Qt.AlignRight)
        self.signalFrequency3TextBox.setFixedWidth(100)
        self.signalFrequency3LabelUnits = QLabel("Hz")

        # creating a push button object 
        btn = QPushButton('Push Button') 
  
        # creating a line edit widget 
        text = QLineEdit("Line Edit") 
  
        # creating a check box widget 
        check = QCheckBox("Check Box") 
  
        # Creating Plot Label for Input Signal
        self.inputSignalLabel = QLabel("Input Signal to STM32")
        # creating a plot window for input Signals
        self.inputSignalPlot = pg.plot() 
        # plot color
        pen = pg.mkPen(color=(0, 0, 0))
        # create input Signal for FreeRTOS
        self.inputSignal = MyPlotCurveItem(x = self.time, y = self.generate_sin_signals(), pen = pen)  
        # add item to plot window 
        self.inputSignalPlot.addItem(self.inputSignal)
        # set plot properties
        self.inputSignalPlot.setXRange(0, 1024, padding=0) 
        self.inputSignalPlot.setBackground('w')


        # Creating Plto Label for fft results
        self.fftResultsLabel = QLabel("FFT Results")
        # creating a plot window for fft
        self.fftResultsPlot = pg.plot() 
        # plot color
        pen = pg.mkPen(color=(0, 0, 0))
        # create fft Output signals
        self.fftOutput = MyPlotCurveItem(x = np.zeros(1024), y = np.zeros(1024), pen = pen)  
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
        self.layout.addWidget(self.signalFrequency1Label, 3, 1, 1, 2)
        self.layout.addWidget(self.signalFrequency1TextBox, 3, 2, 1, 2)
        self.layout.addWidget(self.signalFrequency1LabelUnits, 3, 3, 1, 2)
        self.layout.addWidget(self.signalFrequency2Label, 4, 1, 1, 2)
        self.layout.addWidget(self.signalFrequency2TextBox, 4, 2, 1, 2)
        self.layout.addWidget(self.signalFrequency2LabelUnits, 4, 3, 1, 2)
        self.layout.addWidget(self.signalFrequency3Label, 5, 1, 1, 2)
        self.layout.addWidget(self.signalFrequency3TextBox, 5, 2, 1, 2)
        self.layout.addWidget(self.signalFrequency3LabelUnits, 5, 3, 1, 2)
        self.layout.addWidget(self.inputSignalLabel, 1, 4, 1, 15)
        self.layout.addWidget(self.inputSignalPlot, 2, 4, 5, 15)
        self.layout.addWidget(self.fftResultsLabel, 7, 4, 1, 15) 
        self.layout.addWidget(self.fftResultsPlot, 8, 4, 5, 15) 
        # setting this widget as central widget of the main widow 
        self.setCentralWidget(self.widget) 

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def generate_sin_signals(self):
        amplitude1 = self.ampl1 * np.sin(2 * np.pi * self.signalFrequency1 * self.time / self.numberOfSamples)
        amplitude2 = self.ampl2 * np.sin(2 * np.pi * self.signalFrequency2 * self.time / self.numberOfSamples)
        amplitude3 = self.ampl3 * np.sin(2 * np.pi * self.signalFrequency3 * self.time / self.numberOfSamples)
        return amplitude1 + amplitude2 + amplitude3


    def update_plot_sin_data(self):
        print('signal plot update')
        self.x = self.time
        self.y = self.generate_sin_signals()
        self.data_line.setData(self.x, self.y)  # Update the data.


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()