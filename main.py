import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph
from pyqtgraph import PlotWidget
import pandas as pd
from GUI import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # self.ui.verticalSlider.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.ui.verticalSlider.setMaximum(40)
        self.ui.verticalSlider.setMinimum(0)
        self.ui.verticalSlider.setValue(4)
        # Variables Initialization
     

        # Links of GUI Elements to Methods:

    # Methods


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())