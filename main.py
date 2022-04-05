import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph
from pyqtgraph import PlotWidget
import pandas as pd
from GUI import Ui_MainWindow
from scipy.io import wavfile
import scipy.fft
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import signal
from PyQt5.QtWidgets import*
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Variables Initialization
        self.samplingRate = None
        self.originalMusicSignal = None
        self.equilizedMusicSignal = None
        self.fourierTransformOfOriginalMusicSignal = None

        self.instrumentsDataList = [ { "Instrument": "Bass", "Starting Frequency": 0, "Ending Frequency": 128, "Gain": 1 }, { "Instrument": "Trombone", "Starting Frequency": 128, "Ending Frequency": 550, "Gain": 0 }, { "Instrument": "E-Flat Clarinet", "Starting Frequency": 550, "Ending Frequency": 1000, "Gain": 0 }, { "Instrument": "Piccolo", "Starting Frequency": 1000, "Ending Frequency": 2000, "Gain": 1 }, { "Instrument": "Viola", "Starting Frequency": 2000, "Ending Frequency": 20000, "Gain": 1 } ]
        self.instrumentsUIElementsList = [ { "Instrument": "Bass", "Slider": self.ui.BassGainVerticalSlider, "Gain Value Label": self.ui.BassGainValueTextLabel }, { "Instrument": "Trombone", "Slider": self.ui.TromboneGainVerticalSlider, "Gain Value Label": self.ui.TromboneGainValueTextLabel }, { "Instrument": "E-Flat Clarinet", "Slider": self.ui.E_FlatClarinetGainVerticalSlider, "Gain Value Label": self.ui.E_FlatClarinetGainValueTextLabel }, { "Instrument": "Piccolo", "Slider": self.ui.PiccoloGainVerticalSlider, "Gain Value Label": self.ui.PiccoloGainValueTextLabel }, { "Instrument": "Viola", "Slider": self.ui.ViolaGainVerticalSlider, "Gain Value Label": self.ui.ViolaGainValueTextLabel } ]

        # self.figure = plt.figure(figsize=(15,5))
        # self.Canvas = FigureCanvas(self.figure)
        # self.ui.SpectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)

        # for instrumentDictionary in self.instrumentsUIElementsList:
        #     instrumentDictionary["Slider"].setMinimum(0)
        #     instrumentDictionary["Slider"].setMaximum(40)
        #     instrumentDictionary["Slider"].setValue(4)
        #     instrumentDictionary["Gain Value Label"].setText("1x")

        
        # Links of GUI Elements to Methods:
        self.ui.actionOpen.triggered.connect(lambda: self.OpenFile())
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].valueChanged.connect(self.EquilizeMusicSignal)

    # Methods

    def OpenFile(self):

        self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Music File", directory="", filter="wav (*.wav)")[0]
        if  self.fileName:
            self.samplingRate, self.originalMusicSignal = wavfile.read(self.fileName)
            self.clearSpectrogram()
            self.plotSpectrogram()
            self.fourierTransformOfOriginalMusicSignal = scipy.fft.rfft(self.originalMusicSignal)

    def EquilizeMusicSignal(self):

        musicSignalMagnitudeValues = np.abs(self.fourierTransformOfOriginalMusicSignal)
        musicSignalPhaseValues = np.angle(self.fourierTransformOfOriginalMusicSignal)
        musicSignalFrequencyComponents = scipy.fft.rfftfreq(len(self.originalMusicSignal), 1/self.samplingRate)

        for dictionaryIndex, instrumentDictionary in enumerate(self.instrumentsUIElementsList):
            gainValue = round(( instrumentDictionary["Slider"].value() / 40 ) * 10, 2)
            instrumentDictionary["Gain Value Label"].setText(str(gainValue) + "x")
            self.instrumentsDataList[dictionaryIndex]["Gain"] = gainValue

        for instrumentDictionary in self.instrumentsDataList:
            startingFrequencyIndex = FindIndexOfNearestValue(musicSignalFrequencyComponents, instrumentDictionary["Starting Frequency"])
            endingFrequencyIndex = FindIndexOfNearestValue(musicSignalFrequencyComponents, instrumentDictionary["Ending Frequency"])
            musicSignalMagnitudeValues[startingFrequencyIndex : endingFrequencyIndex + 1] *= instrumentDictionary["Gain"]

        fourierTransformOfEquilizedMusicSignal = musicSignalMagnitudeValues * np.exp(1j * musicSignalPhaseValues)  
        self.equilizedMusicSignal = np.fft.irfft(fourierTransformOfEquilizedMusicSignal)

        #------>>>>> FOR SEEING ONLY IF IT WORKS BEFORE IMPLEMENTING PLAY: TO REMOVED BEFORE SUBMISSION
        wavfile.write('Equilized Ode To Joy.wav', 48000, self.equilizedMusicSignal.astype(np.int16))
    
    def plotSpectrogram(self):
        # first = self.originalMusicSignal[:int(self.samplingRate*125)]
        plt.specgram(self.originalMusicSignal, Fs=self.samplingRate)
        plt.draw()
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        self.Canvas.draw()
    
    def clearSpectrogram(self):
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
        self.ui.SpectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)
# Global Functions


def FindIndexOfNearestValue(arrayToFindNearestValueIn, value):
    arrayToFindNearestValueIn = np.asarray(arrayToFindNearestValueIn)
    indexOfNearestValue = (np.abs(arrayToFindNearestValueIn - value)).argmin()
    return indexOfNearestValue


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())