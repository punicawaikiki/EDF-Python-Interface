# from PyQt5 import QtCore, QtWidgets
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

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("EDF GUI")
        self.resize(1920, 1080)
        # self.setGeometry(100, 100, 600, 500)
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


        # self.x = self.time
        # self.y = self.generate_sin_signals()

        # pen = pg.mkPen(color=(0, 0, 0))
        # self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(500)
        # self.timer.timeout.connect(self.update_plot_sin_data)
        # self.timer.start()

        # self.initUI()

    def UiComponents(self):
        # creating a widget object 
        self.widget = QWidget() 
  
        # creating a push button object 
        btn = QPushButton('Push Button') 
  
        # creating a line edit widget 
        text = QLineEdit("Line Edit") 
  
        # creating a check box widget 
        check = QCheckBox("Check Box") 
  
        # creating a plot window for input Signals
        self.inputSignalPlot = pg.plot() 

        # create input Signal for FreeRTOS
        self.inputSignal = pg.PlotCurveItem(x = self.time, y = self.generate_sin_signals())  
        # add item to plot window 
        self.inputSignalPlot.addItem(self.inputSignal) 


        # creating a plot window for fft
        self.fftOutputPlot = pg.plot() 

        # create fft Output signals
        self.fftOutput = pg.PlotCurveItem(x = np.zeros(1024), y = np.zeros(1024))  
        # add item to plot window 
        self.fftOutputPlot.addItem(self.fftOutput) 

        self.inputSignalLabel = QLabel("Input Signal to STM32")

  
        # Creating a grid layout 
        self.layout = QGridLayout() 
  
        # setting this layout to the widget 
        self.widget.setLayout(self.layout) 
  
        # adding widgets in the layout in their proper positions 
        # button goes in upper-left 
        # self.layout.addWidget(btn, 0, 0) 
  
        # # text edit goes in middle-left 
        # self.layout.addWidget(text, 1, 0) 
  
        # # check box widget goes in bottom-left 
        # self.layout.addWidget(check, 3, 0) 
  
        # plot window goes on right side, spanning 3 rows 
        self.layout.addWidget(self.inputSignalLabel, 0, 0)
        self.layout.addWidget(self.inputSignalPlot, 1, 4) 
        self.layout.addWidget(self.fftOutputPlot, 2, 4) 
        # setting this widget as central widget of the main widow 
        self.setCentralWidget(self.widget) 

    def initUI(self):
        # self.resize(1920, 1080)
        # self.center()
        # self.setWindowTitle('EDF GUI')

        self.widget = QtWidgets.QWidget()
        self.button = QtWidgets.QPushButton('Push Button')

        # creating a plot window 
        self.plot = pg.plot()

        # create list for y-axis 
        y1 = [5, 5, 7, 10, 3, 8, 9, 1, 6, 2] 
  
        # create horizontal list i.e x-axis 
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
  
        # create pyqt5graph bar graph item 
        # with width = 0.6 
        # with bar colors = green
        # self.input_signal = pg.GraphicsItem(x = self.x, height = self.y, width = 0.6, brush ='g')
        self.bargraph = pg.BarGraphItem(x = x, height = y1, width = 0.6, brush ='g') 

        # add item to plot window 
        # adding bargraph item to the plot window 
        # self.plot.addItem(self.input_signal) 
        self.plot.addItem(self.bargraph) 

        # self.init_signal_UI()
        self.show()

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