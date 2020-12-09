from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import numpy as np
from random import randint

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.initUI()
    
        # sin signal preferences
        # amplitude:
        self.ampl1 = 1
        self.ampl2 = 2
        self.ampl3 = 3

        # signal frequencies
        self.signalFrequency1 = 10
        self.signalFrequency2 = 50
        self.signalFrequency3 = 200

        # number of samples
        self.numberOfSamples = 1024
        self.time = np.arange(self.numberOfSamples)

        self.x = self.time
        self.y = self.generate_sin_signals()

        pen = pg.mkPen(color=(0, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_plot_sin_data)
        self.timer.start()

    def initUI(self):
        self.resize(1920, 1080)
        self.center()
        self.setWindowTitle('EDF GUI')
        self.init_signal_UI()
        self.show()
    
    def init_signal_UI(self):
        self.graphWidget = pg.PlotWidget()
        # self.
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')

    def center(self):

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
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
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()