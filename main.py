########## Imports ##########

#! check for repetition
from re import T
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
        self.instrumentsDataList = [ { "Instrument": "Bass", "Starting Frequency": 0, "Ending Frequency": 128, "Gain": 1 }, { "Instrument": "Trombone", "Starting Frequency": 128, "Ending Frequency": 550, "Gain": 0 }, { "Instrument": "E-Flat Clarinet", "Starting Frequency": 550, "Ending Frequency": 1000, "Gain": 0 }, { "Instrument": "Piccolo", "Starting Frequency": 1000, "Ending Frequency": 2000, "Gain": 1 }, { "Instrument": "Viola", "Starting Frequency": 2000, "Ending Frequency": 20000, "Gain": 1 } ]
        self.instrumentsUIElementsList = [ { "Instrument": "Bass", "Slider": self.ui.BassGainVerticalSlider, "Gain Value Label": self.ui.BassGainValueTextLabel }, { "Instrument": "Trombone", "Slider": self.ui.TromboneGainVerticalSlider, "Gain Value Label": self.ui.TromboneGainValueTextLabel }, { "Instrument": "E-Flat Clarinet", "Slider": self.ui.E_FlatClarinetGainVerticalSlider, "Gain Value Label": self.ui.E_FlatClarinetGainValueTextLabel }, { "Instrument": "Piccolo", "Slider": self.ui.PiccoloGainVerticalSlider, "Gain Value Label": self.ui.PiccoloGainValueTextLabel }, { "Instrument": "Viola", "Slider": self.ui.ViolaGainVerticalSlider, "Gain Value Label": self.ui.ViolaGainValueTextLabel } ]
        self.timer= QtCore.QTimer()
        self.player = QMediaPlayer()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.timer.setInterval(400)
        # self.instrumentsName = 'Xylophone'
        self.pianoButtonsAndSoundsList = [{"Button": self.ui.PianoCKeyPushButton, "Major": 'piano/Piano-c_C_major.wav', "Minor":'piano/Piano-11.wav', 'Text': 'A'},
                                        {"Button": self.ui.PianoDKeyPushButton, "Major": 'piano/Piano-d_D_major.wav', "Minor": 'piano/Piano-12.wav', 'Text': 'S'},
                                        {"Button": self.ui.PianoEKeyPushButton, "Major": 'piano/Piano-e_E_major.wav', "Minor": 'piano/Piano-13.wav', 'Text': 'D'},
                                        {"Button": self.ui.PianoFKeyPushButton, "Major": 'piano/Piano-f_F_major.wav', "Minor": 'piano/Piano-14.wav', 'Text': 'F'},
                                        {"Button": self.ui.PianoGKeyPushButton, "Major": 'piano/Piano-g_G_major.wav', "Minor":'piano/Piano-15.wav', 'Text': 'G'},
                                        {"Button": self.ui.PianoAKeyPushButton, "Major": 'piano/Piano-a_A_major.wav', "Minor": 'piano/Piano-16.wav', 'Text': 'H'},
                                        {"Button": self.ui.PianoBKeyPushButton, "Major": 'piano/Piano-b_B_major.wav', "Minor": 'piano/Piano-17.wav', 'Text': 'J'},
                                        {"Button": self.ui.PianoQKeyPushButton, "Major": 'piano/Piano-c_C#_major.wav', "Minor": 'piano/Piano110.wav', 'Text': 'Q'},
                                        {"Button": self.ui.PianoWKeyPushButton, "Major": 'piano/Piano-eb_D#_major.wav', "Minor": 'piano/Piano111.wav', 'Text': 'W'},
                                        {"Button": self.ui.PianoRKeyPushButton, "Major": 'piano/Piano-f_F#_major.wav', "Minor": 'piano/Piano112.wav', 'Text': 'E'},
                                        {"Button": self.ui.PianoTKeyPushButton, "Major": 'piano/Piano-g_G#_major.wav', "Minor":'piano/Piano113.wav', 'Text': 'R'},
                                        {"Button": self.ui.PianoZKeyPushButton, "Major": 'piano/Piano-bb_A#_major.wav', "Minor": 'piano/Piano114.wav', 'Text': 'T'}]
        self.xylophoneButtonsAndSoundsList = [{"Button": self.ui.Xylophone1KeyPushButton,"Mode 1":'xylophone/alto1.wav',"Mode 2":'xylophone/mode2_1.wav', 'Text':'1'},
                                            {"Button": self.ui.Xylophone2KeyPushButton,"Mode 1":'xylophone/alto2.wav',"Mode 2": 'xylophone/mode2_2.wav', 'Text':'2'},
                                            {"Button": self.ui.Xylophone3KeyPushButton,"Mode 1":'xylophone/alto3.wav',"Mode 2":'xylophone/mode2_3.wav', 'Text':'3'},
                                            {"Button": self.ui.Xylophone4KeyPushButton,"Mode 1":'xylophone/alto4.wav',"Mode 2":'xylophone/mode2_4.wav', 'Text':'4'},
                                            {"Button": self.ui.Xylophone5KeyPushButton,"Mode 1":'xylophone/alto5.wav',"Mode 2":'xylophone/mode2_5.wav', 'Text':'5'},
                                            {"Button": self.ui.Xylophone6KeyPushButton,"Mode 1":'xylophone/alto6.wav',"Mode 2":'xylophone/mode2_6.wav', 'Text':'6'},
                                            {"Button": self.ui.Xylophone7KeyPushButton,"Mode 1":'xylophone/alto7.wav',"Mode 2":'xylophone/mode2_7.wav', 'Text':'7'},
                                            {"Button": self.ui.Xylophone8KeyPushButton,"Mode 1":'xylophone/alto8.wav',"Mode 2":'xylophone/mode2_8.wav', 'Text':'8'}]
        self.bongosButtonsAndSoundsList = [{"Button": self.ui.BongosMKeyPushButton,"Sound":'bongos/Bongos_bongo1.wav', 'Text':'M'},
                                            {"Button": self.ui.BongosNKeyPushButton,"Sound":'bongos/Bongos_bongo2.wav', 'Text':'N'}]
        self.functionsConnectionList = [{"Button": self.ui.pianoKeysPushButton,"Function": self.show, 'Text': 'Keys'}]#,
                                        # {"Button": self.ui.equaliseEmphasizerPushButton,"Function":self.equalise()},
                                        # {"Button": self.ui.pianoMajorPushButton,"Function":self.pianoModes},
        #                                 {"Button": self.ui.pianoMinorPshButton,"Function":self.pianoModes},
        #                                 {"Button": ,"Function":},
        #                                 {"Button": ,"Function":},
        #                                 {"Button": ,"Function":},
        #                                 {"Button": ,"Function":},
        #                                 {"Button": ,"Function":},
        #                                 {"Button": ,"Function":}]
        self.instrumentsModesList = [{"Button": self.ui.pianoMinorPshButton, "instrument mode":self.pianoMode},{"Button": self.ui.XylophoneModeOnePushButton, "instrument mode":self.xylophoneMode}]
        self.pianoSettings()
        self.xylophoneSettings()

        #?######### Links of GUI Elements to Methods ##########
        
        self.ui.actionOpen.triggered.connect(lambda: self.OpenFile())
        self.timer.timeout.connect(self.updatePlot)
        self.ui.VolumeUpDownHorizontalSlider.valueChanged.connect(lambda: self.changeVolume())
        
        #!repetition
        for functionKeyDictionary in self.functionsConnectionList:
            functionKeyDictionary["Button"].clicked.connect(self.connections)
        self.ui.PlayAndPausePushButton.clicked.connect(lambda: self.palyAndPause())
        # self.ui.pianoKeysPushButton.clicked.connect(self.ui.showAndHideKey)
        self.ui.equaliseEmphasizerPushButton.clicked.connect(self.equalise)
        self.ui.pianoMajorPushButton.clicked.connect(self.pianoSettings)
        self.ui.pianoMinorPshButton.clicked.connect(self.pianoSettings)
        self.ui.XylophoneModeOnePushButton.clicked.connect(self.xylophoneSettings)
        self.ui.XylophoneModeTwoPushButton.clicked.connect(self.xylophoneSettings)
        
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].valueChanged.connect(self.EquilizeMusicSignal)
        #!repetition
        for bongosKeyDictionary in self.bongosButtonsAndSoundsList:
            bongosKeyDictionary["Button"].clicked.connect(lambda: self.Player('Bongos'))  
        
        

#! ---------------------------------------------------------------------------------------------------------------------------------------------- #

                                            ##########? Class Methods ##########

                                        #?#######>> Tab 1 Player & Emphasizer <<########
                                        
    #?### Main Methods ####

    def connections(self):
        keyText = self.sender().text()
        print(keyText)
        keyDictionary = GetDictionaryByKeyValuePair(self.functionsConnectionList, 'Text', keyText)
        keyDictionary["Function"]

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
        if self.ui.PlayAndPausePushButton.isChecked() and self.play == True: self.TimerAndPlayer(self.timer.start(), self.player.play(), 'icons/pause.png', False)
        else: self.TimerAndPlayer(self.timer.stop(),self.player.pause(),'icons/play.png',True)

    def TimerAndPlayer(self,timer,player,icon,trueOrFalse):
        timer
        player
        self.ui.PlayAndPausePushButton.setIcon(QtGui.QIcon(icon))
        self.play = trueOrFalse
            
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
          
    #!repetition
    def pianoSettings(self):
        self.pianoMode = self.settings(self.pianoMode, self.ui.pianoMinorPshButton, 'Minor', 'Major', self.pianoButtonsAndSoundsList, 'Piano')

    def xylophoneSettings(self):
        self.xylophoneMode = self.settings(self.xylophoneMode, self.ui.XylophoneModeOnePushButton, 'Mode 1', 'Mode 2', self.xylophoneButtonsAndSoundsList, 'Xylophone') 

    def Player(self, instrumentsName):
        if instrumentsName == 'Piano':
            self.playerHelp(self.pianoButtonsAndSoundsList, self.pianoMode)
        elif instrumentsName == 'Xylophone':
            self.playerHelp(self.xylophoneButtonsAndSoundsList, self.xylophoneMode)
        elif instrumentsName == 'Bongos':
            self.playerHelp(self.bongosButtonsAndSoundsList, "Sound")
    
    def playerHelp(self, list, mode):
        keyText = self.sender().text()
        keyDictionary = GetDictionaryByKeyValuePair(list, 'Text', keyText)
        self.mixerPlay(keyDictionary[mode]) 

    def settings(self, instrumentMode, button, mode1, mode2, list, instrumentsName):
        if button.isChecked(): instrumentMode = mode1
        else: instrumentMode = mode2
        for KeyDictionary in list:
            KeyDictionary["Button"].clicked.connect(lambda: self.Player(instrumentsName))  
        return instrumentMode   
        
#! -------------------------------------------------------------------------------------------------------------------------------------------- #
 
                                                    ######?>> General Helper Functions: <<######
 
    # Load a Wave File and Play it using Mixer
    def mixerPlay(self, file):
        pygame.mixer.music.load(file)
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

def GetDictionaryByKeyValuePair(dictionaries_list, key_to_search_by, value_to_search_by):
        dictionary_to_find = {}
        for dictionary in dictionaries_list:
            if dictionary[key_to_search_by] == value_to_search_by:
                dictionary_to_find = dictionary
        return dictionary_to_find

#?######### Application Main ##########

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    