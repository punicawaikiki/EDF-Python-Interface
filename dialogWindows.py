from PyQt5 import QtCore, QtGui
import sys
# importing Qt widgets 
from PyQt5.QtWidgets import *

class IPAddressDialog(QDialog):
    def __init__(self, parent=None):
        super(IPAddressDialog, self).__init__(parent)
        # set windows title
        self.setWindowTitle("IP Address Dialog")
        # create widget
        self.widget = QWidget()

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        # set Grid Layout
        self.layout = QGridLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.buttonBox, 1, 1, 1, 2)
        self.setLayout(self.layout)

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = IPAddressDialog()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())