########## Imports ##########

#! check for repetition
from re import T
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph
from pyqtgraph import PlotWidget
import pandas as pd
from GUINew import Ui_MainWindow
from scipy.io import wavfile
import scipy.fft
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import signal
from PyQt5.QtWidgets import*
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import Qt, QUrl
import pandas as pd
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import wave
import pygame

#! --------------------------------------------------------------------------------------------------------------------------------------------------- #

                                                #?######### Class Definition ##########

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icons/icon.png'))
        self.setWindowTitle("Musical Instruments")
        
        ##########? Class Attributes Initialization ##########
        
        # initialize the sound library
        pygame.mixer.pre_init(
            channels=1, allowedchanges=0, buffer=512, frequency=44100)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(65)
        self.counter=0
        self.play = True
        self.samplingRate = None
        self.originalMusicSignal = None
        self.equilizedMusicSignal = None
        self.fourierTransformOfOriginalMusicSignal = None
        self.pianoMode = 'Major'
        self.xylophoneMode = 'Mode 1'
        self.pianoSettings()
        self.xylophoneSettings()
        self.instrumentsDataList = [ { "Instrument": "Bass", "Starting Frequency": 0, "Ending Frequency": 128, "Gain": 1 }, { "Instrument": "Trombone", "Starting Frequency": 128, "Ending Frequency": 550, "Gain": 0 }, { "Instrument": "E-Flat Clarinet", "Starting Frequency": 550, "Ending Frequency": 1000, "Gain": 0 }, { "Instrument": "Piccolo", "Starting Frequency": 1000, "Ending Frequency": 2000, "Gain": 1 }, { "Instrument": "Viola", "Starting Frequency": 2000, "Ending Frequency": 20000, "Gain": 1 } ]
        self.instrumentsUIElementsList = [ { "Instrument": "Bass", "Slider": self.ui.BassGainVerticalSlider, "Gain Value Label": self.ui.BassGainValueTextLabel }, { "Instrument": "Trombone", "Slider": self.ui.TromboneGainVerticalSlider, "Gain Value Label": self.ui.TromboneGainValueTextLabel }, { "Instrument": "E-Flat Clarinet", "Slider": self.ui.E_FlatClarinetGainVerticalSlider, "Gain Value Label": self.ui.E_FlatClarinetGainValueTextLabel }, { "Instrument": "Piccolo", "Slider": self.ui.PiccoloGainVerticalSlider, "Gain Value Label": self.ui.PiccoloGainValueTextLabel }, { "Instrument": "Viola", "Slider": self.ui.ViolaGainVerticalSlider, "Gain Value Label": self.ui.ViolaGainValueTextLabel } ]
        self.timer= QtCore.QTimer()
        self.player = QMediaPlayer()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.timer.setInterval(400)
        
        #?######### Links of GUI Elements to Methods ##########
        
        self.ui.actionOpen.triggered.connect(lambda: self.OpenFile())
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].valueChanged.connect(self.EquilizeMusicSignal)
        self.timer.timeout.connect(self.updatePlot)
        self.ui.PlayAndPausePushButton.clicked.connect(lambda: self.palyAndPause())
        self.ui.VolumeUpDownHorizontalSlider.valueChanged.connect(lambda: self.changeVolume())
        self.ui.pianoKeysPushButton.clicked.connect(self.ui.showAndHideKey)
        self.ui.equaliseEmphasizerPushButton.clicked.connect(self.equalise)
        #!repetition
        self.ui.BongosMKeyPushButton.clicked.connect(lambda: self.mixerPlay('bongos/Bongos_bongo1.wav'))
        self.ui.BongosNKeyPushButton.clicked.connect(lambda: self.mixerPlay('bongos/Bongos_bongo2.wav'))
        self.ui.pianoMajorPushButton.clicked.connect(self.pianoModes)
        self.ui.pianoMinorPshButton.clicked.connect(self.pianoModes)
        self.ui.pianoMajorPushButton.clicked.connect(self.pianoSettings)
        self.ui.pianoMinorPshButton.clicked.connect(self.pianoSettings)
        self.ui.XylophoneModeOnePushButton.clicked.connect(self.xylophoneModes)
        self.ui.XylophoneModeTwoPushButton.clicked.connect(self.xylophoneModes)
        self.ui.XylophoneModeOnePushButton.clicked.connect(self.xylophoneSettings)
        self.ui.XylophoneModeTwoPushButton.clicked.connect(self.xylophoneSettings)

#! ---------------------------------------------------------------------------------------------------------------------------------------------- #

                                            ##########? Class Methods ##########

                                        #?#######>> Tab 1 Player & Emphasizer <<########
                                        
    #?### Main Methods ####

    def OpenFile(self):
        self.ui.SongGraphGraphicsView.clear()
        self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Music File", directory="", filter="wav (*.wav)")[0]
        if  self.fileName:
            self.samplingRate, self.originalMusicSignal = wavfile.read(self.fileName) 
            self.clearAndPlotSpectrogram(self.originalMusicSignal, self.samplingRate)
            self.fourierTransformOfOriginalMusicSignal = scipy.fft.rfft(self.originalMusicSignal)
            self.playMusic(self.fileName)

    #! Check code repetition
    def palyAndPause(self):
        if self.ui.PlayAndPausePushButton.isChecked() and self.play == True:
            self.timer.start()
            self.player.play()
            self.ui.PlayAndPausePushButton.setIcon(QtGui.QIcon('icons/pause.png'))
            self.play = False
        else:
            self.player.pause()
            self.timer.stop()
            self.ui.PlayAndPausePushButton.setIcon(QtGui.QIcon('icons/play.png'))
            self.play = True
            
    def playMusic(self, file):
        spf = wave.open(file, "r")
        self.signal = spf.readframes(-1)
        self.signal = np.frombuffer(self.signal, "int16")
        self.fs = spf.getframerate()
        self.time = np.linspace(0, len(self.signal) / self.fs, num=len(self.signal))
        url = QUrl.fromLocalFile(file)
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.counter = 0
        self.play = True
        self.palyAndPause()

    def updatePlot(self):
        self.ui.SongGraphGraphicsView.clear()
        increment = int((self.samplingRate/2))
        self.ui.SongGraphGraphicsView.setYRange(min(self.signal),max(self.signal))
        self.ui.SongGraphGraphicsView.setXRange(self.time[self.counter],self.time[self.counter+increment] )
        self.ui.SongGraphGraphicsView.plot(self.time[self.counter:self.counter+increment], self.signal[self.counter:self.counter+increment])
        self.counter+=increment
  
    def changeVolume(self):
        self.sliderValue=self.ui.VolumeUpDownHorizontalSlider.value()
        currentVolume = self.player.volume() 
        print(currentVolume)
        self.player.setVolume(self.sliderValue)
         
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

    def plotSpectrogram(self, sample, sample_rate):
        plt.specgram(sample, Fs=sample_rate)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        self.Canvas.draw()

    def clearSpectrogram(self):
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
        self.ui.spectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)
     
    def equalise(self):
        wavfile.write('Equilized Ode To Joy.wav', 48000, self.equilizedMusicSignal.astype(np.int16))
        self.playMusic('Equilized Ode To Joy.wav')
        self.clearAndPlotSpectrogram(self.equilizedMusicSignal, self.samplingRate)

#! --------------------------------------------------------------------------------------------------------------------------------------------- #

                                            #?#####>> Tab 2 Virtual  Musical Instrumnets <<######
    
    #?### Main Methods ####

    def pianoModes(self):
        if self.ui.pianoMinorPshButton.isChecked(): self.pianoMode = 'Minor'
        else: self.pianoMode = 'Major'
    
    #!repetition
    def pianoSettings(self):
        if self.pianoMode == 'Major':
            self.ui.PianoCKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-c_C_major.wav'))
            self.ui.PianoDKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-d_D_major.wav'))
            self.ui.PianoEKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-e_E_major.wav'))
            self.ui.PianoFKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-f_F_major.wav')) 
            self.ui.PianoGKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-g_G_major.wav')) 
            self.ui.PianoAKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-a_A_major.wav')) 
            self.ui.PianoBKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-b_B_major.wav'))
            self.ui.PianoQKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-c_C#_major.wav'))
            self.ui.PianoWKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-eb_D#_major.wav'))
            self.ui.PianoRKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-f_F#_major.wav'))
            self.ui.PianoTKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-g_G#_major.wav'))
            self.ui.PianoZKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-bb_A#_major.wav'))
        elif self.pianoMode == 'Minor':
            self.ui.PianoCKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-11.wav'))
            self.ui.PianoDKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-12.wav'))
            self.ui.PianoEKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-13.wav'))
            self.ui.PianoFKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-14.wav')) 
            self.ui.PianoGKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-15.wav')) 
            self.ui.PianoAKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-16.wav')) 
            self.ui.PianoBKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano-17.wav'))
            self.ui.PianoQKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano110.wav'))
            self.ui.PianoWKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano111.wav'))
            self.ui.PianoRKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano112.wav'))
            self.ui.PianoTKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano113.wav'))
            self.ui.PianoZKeyPushButton.clicked.connect(lambda: self.mixerPlay('piano/Piano114.wav'))

    def xylophoneModes(self):
        if self.ui.XylophoneModeOnePushButton.isChecked(): self.xylophoneMode = 'Mode 1'
        else: self.xylophoneMode = 'Mode 2'

    #!repetition
    def xylophoneSettings(self):
        if self.xylophoneMode == 'Mode 1':
          self.ui.Xylophone1KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto1.wav'))
          self.ui.Xylophone2KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto2.wav'))
          self.ui.Xylophone3KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto3.wav'))
          self.ui.Xylophone4KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto4.wav'))
          self.ui.Xylophone5KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto5.wav'))
          self.ui.Xylophone6KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto6.wav'))
          self.ui.Xylophone7KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto7.wav'))
          self.ui.Xylophone8KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/alto8.wav'))
        elif self.xylophoneMode == 'Mode 2':
          self.ui.Xylophone1KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_1.wav'))
          self.ui.Xylophone2KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_2.wav'))
          self.ui.Xylophone3KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_3.wav'))
          self.ui.Xylophone4KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_4.wav'))
          self.ui.Xylophone5KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_5.wav'))
          self.ui.Xylophone6KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_6.wav'))
          self.ui.Xylophone7KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_7.wav'))
          self.ui.Xylophone8KeyPushButton.clicked.connect(lambda: self.mixerPlay('xylophone/mode2_8.wav'))  

#! -------------------------------------------------------------------------------------------------------------------------------------------- #
 
                                                    ######?>> General Helper Functions: <<######
 
    # Load a Wave File and Play it using Mixer
    def mixerPlay(self, file):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.play()

    # Clearing Spectrogram Before Plot
    def clearAndPlotSpectrogram(self, signal, samplingRate):
        self.clearSpectrogram()
        self.plotSpectrogram(signal, samplingRate)

#! --------------------------------------------------------------------------------------------------------------------------------------------- #
                                                   
                                                    #?#####>> Global Functions: <<######

def FindIndexOfNearestValue(arrayToFindNearestValueIn, value):
    arrayToFindNearestValueIn = np.asarray(arrayToFindNearestValueIn)
    indexOfNearestValue = (np.abs(arrayToFindNearestValueIn - value)).argmin()
    return indexOfNearestValue

#?######### Application Main ##########

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    