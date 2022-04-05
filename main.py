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

global pianoMode 
global xylophoneMode

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
        #################Roaa###################3
        self.timer= QtCore.QTimer()
        self.timer.setInterval(400)
        self.player = QMediaPlayer()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.ui.VolumeUpDownHorizontalSlider.setMinimum(0)
        self.ui.VolumeUpDownHorizontalSlider.setMaximum(100)
        self.ui.VolumeUpDownHorizontalSlider.setValue(30)
        self.counter=0
        self.timer.timeout.connect(self.updatePlot)

        self.instrumentsDataList = [ { "Instrument": "Bass", "Starting Frequency": 0, "Ending Frequency": 128, "Gain": 1 }, { "Instrument": "Trombone", "Starting Frequency": 128, "Ending Frequency": 550, "Gain": 0 }, { "Instrument": "E-Flat Clarinet", "Starting Frequency": 550, "Ending Frequency": 1000, "Gain": 0 }, { "Instrument": "Piccolo", "Starting Frequency": 1000, "Ending Frequency": 2000, "Gain": 1 }, { "Instrument": "Viola", "Starting Frequency": 2000, "Ending Frequency": 20000, "Gain": 1 } ]
        self.instrumentsUIElementsList = [ { "Instrument": "Bass", "Slider": self.ui.BassGainVerticalSlider, "Gain Value Label": self.ui.BassGainValueTextLabel }, { "Instrument": "Trombone", "Slider": self.ui.TromboneGainVerticalSlider, "Gain Value Label": self.ui.TromboneGainValueTextLabel }, { "Instrument": "E-Flat Clarinet", "Slider": self.ui.E_FlatClarinetGainVerticalSlider, "Gain Value Label": self.ui.E_FlatClarinetGainValueTextLabel }, { "Instrument": "Piccolo", "Slider": self.ui.PiccoloGainVerticalSlider, "Gain Value Label": self.ui.PiccoloGainValueTextLabel }, { "Instrument": "Viola", "Slider": self.ui.ViolaGainVerticalSlider, "Gain Value Label": self.ui.ViolaGainValueTextLabel } ]
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Links of GUI Elements to Methods:
        self.ui.actionOpen.triggered.connect(lambda: self.OpenFile())
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].valueChanged.connect(self.EquilizeMusicSignal)

        
        self.ui.PlayPushButton.clicked.connect(lambda: self.play())
        self.ui.PausePushButton.clicked.connect(lambda: self.pause())
        self.ui.VolumeUpDownHorizontalSlider.valueChanged.connect(lambda: self.changeVolume())
        self.ui.BongosMKeyPushButton.clicked.connect(self.MBongo)
        self.ui.BongosNKeyPushButton.clicked.connect(self.NBongo)
        self.ui.Xylophone1KeyPushButton.clicked.connect(self.Xylophone1ToneA)
        self.ui.Xylophone2KeyPushButton.clicked.connect(self.Xylophone2ToneA)
        self.ui.Xylophone3KeyPushButton.clicked.connect(self.Xylophone3ToneA)
        self.ui.Xylophone4KeyPushButton.clicked.connect(self.Xylophone4ToneA)
        self.ui.Xylophone5KeyPushButton.clicked.connect(self.Xylophone5ToneA)
        self.ui.Xylophone6KeyPushButton.clicked.connect(self.Xylophone6ToneA)
        self.ui.Xylophone7KeyPushButton.clicked.connect(self.Xylophone7ToneA)
        self.ui.Xylophone8KeyPushButton.clicked.connect(self.Xylophone8ToneA)
        self.ui.PianoSettingsComboBox.currentIndexChanged.connect(lambda: self.pianoSettings(self.ui.PianoSettingsComboBox.currentIndex()))
        self.ui.XylophoneSettingsComboBox.currentIndexChanged.connect(lambda: self.xylophoneSettings(self.ui.XylophoneSettingsComboBox.currentIndex()))
    # Methods

    def OpenFile(self):
        self.ui.SongGraphGraphicsView.clear()
        self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Music File", directory="", filter="wav (*.wav)")[0]
        if  self.fileName:
            self.samplingRate, self.originalMusicSignal = wavfile.read(self.fileName) 
            self.clearSpectrogram()
            self.plotSpectrogram(self.originalMusicSignal, self.samplingRate)
            self.fourierTransformOfOriginalMusicSignal = scipy.fft.rfft(self.originalMusicSignal)
            self.playMusic(self.fileName)

    def play(self):
        self.timer.start()
        self.player.play()

    def pause(self):
        self.player.pause()
        self.timer.stop()


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
        self.play()

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

        #------>>>>> FOR SEEING ONLY IF IT WORKS BEFORE IMPLEMENTING PLAY: TO REMOVED BEFORE SUBMISSION
        wavfile.write('Equilized Ode To Joy.wav', 48000, self.equilizedMusicSignal.astype(np.int16))
        self.playMusic('Equilized Ode To Joy.wav')
        self.clearSpectrogram()
        self.plotSpectrogram(self.equilizedMusicSignal, self.samplingRate)

    def plotSpectrogram(self, sample, sample_rate):
        plt.specgram(sample, Fs=sample_rate)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        self.Canvas.draw()

    def clearSpectrogram(self):
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
        self.ui.SpectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)

    ######################## TAB 2 #######################################

    def pianoSettings(self,index):
        global pianoMode
        pianoMode=index
        if (index==1):
          self.ui.PianoCKeyPushButton.clicked.connect(self.CkeyMajor)
          self.ui.PianoDKeyPushButton.clicked.connect(self.DkeyMajor)
          self.ui.PianoEKeyPushButton.clicked.connect(self.EkeyMajor)
          self.ui.PianoFKeyPushButton.clicked.connect(self.FkeyMajor) 
          self.ui.PianoGKeyPushButton.clicked.connect(self.GkeyMajor) 
          self.ui.PianoAKeyPushButton.clicked.connect(self.AkeyMajor) 
          self.ui.PianoBKeyPushButton.clicked.connect(self.BkeyMajor)
          self.ui.PianoQKeyPushButton.clicked.connect(self.C_keyMajor)
          self.ui.PianoWKeyPushButton.clicked.connect(self.D_keyMajor)
          self.ui.PianoRKeyPushButton.clicked.connect(self.F_keyMajor)
          self.ui.PianoTKeyPushButton.clicked.connect(self.G_keyMajor)
          self.ui.PianoZKeyPushButton.clicked.connect(self.A_keyMajor)
        elif (index==2):
          self.ui.PianoCKeyPushButton.clicked.connect(self.Ckey)
          self.ui.PianoDKeyPushButton.clicked.connect(self.Dkey)
          self.ui.PianoEKeyPushButton.clicked.connect(self.Ekey)
          self.ui.PianoFKeyPushButton.clicked.connect(self.Fkey) 
          self.ui.PianoGKeyPushButton.clicked.connect(self.Gkey) 
          self.ui.PianoAKeyPushButton.clicked.connect(self.Akey) 
          self.ui.PianoBKeyPushButton.clicked.connect(self.Bkey)
          self.ui.PianoQKeyPushButton.clicked.connect(self.C_key)
          self.ui.PianoWKeyPushButton.clicked.connect(self.D_key)
          self.ui.PianoRKeyPushButton.clicked.connect(self.F_key)
          self.ui.PianoTKeyPushButton.clicked.connect(self.G_key)
          self.ui.PianoZKeyPushButton.clicked.connect(self.A_key)

    def xylophoneSettings(self,index):
        global xylophoneMode
        xylophoneMode=index
        if (index==1):
          self.ui.Xylophone1KeyPushButton.clicked.connect(self.Xylophone1ToneA)
          self.ui.Xylophone2KeyPushButton.clicked.connect(self.Xylophone2ToneA)
          self.ui.Xylophone3KeyPushButton.clicked.connect(self.Xylophone3ToneA)
          self.ui.Xylophone4KeyPushButton.clicked.connect(self.Xylophone4ToneA)
          self.ui.Xylophone5KeyPushButton.clicked.connect(self.Xylophone5ToneA)
          self.ui.Xylophone6KeyPushButton.clicked.connect(self.Xylophone6ToneA)
          self.ui.Xylophone7KeyPushButton.clicked.connect(self.Xylophone7ToneA)
          self.ui.Xylophone8KeyPushButton.clicked.connect(self.Xylophone8ToneA)
        elif (index==2):
          self.ui.Xylophone1KeyPushButton.clicked.connect(self.Xylophone1ToneB)
          self.ui.Xylophone2KeyPushButton.clicked.connect(self.Xylophone2ToneB)
          self.ui.Xylophone3KeyPushButton.clicked.connect(self.Xylophone3ToneB)
          self.ui.Xylophone4KeyPushButton.clicked.connect(self.Xylophone4ToneB)
          self.ui.Xylophone5KeyPushButton.clicked.connect(self.Xylophone5ToneB)
          self.ui.Xylophone6KeyPushButton.clicked.connect(self.Xylophone6ToneB)
          self.ui.Xylophone7KeyPushButton.clicked.connect(self.Xylophone7ToneB)
          self.ui.Xylophone8KeyPushButton.clicked.connect(self.Xylophone8ToneB)



    def Ckey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-11.wav')))
        self.mediaPlayer.play()
    def Dkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-12.wav')))
        self.mediaPlayer.play() 
    def Ekey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-13.wav')))
        self.mediaPlayer.play()   
    def Fkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-14.wav')))
        self.mediaPlayer.play()          
    def Gkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-15.wav')))
        self.mediaPlayer.play() 
    def Akey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-16.wav')))
        self.mediaPlayer.play()     
    def Bkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-17.wav')))
        self.mediaPlayer.play() 
    def C_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano110.wav')))
        self.mediaPlayer.play()
    def D_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano111.wav')))
        self.mediaPlayer.play()         
    def F_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano112.wav')))
        self.mediaPlayer.play()
    def G_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano113.wav')))
        self.mediaPlayer.play() 
    def A_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano114.wav')))
        self.mediaPlayer.play()       
    def A_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-bb_A#_major.wav')))
        self.mediaPlayer.play()  
    def AkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-a_A_major.wav')))
        self.mediaPlayer.play()  
    def BkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-b_B_major.wav')))
        self.mediaPlayer.play()  
    def CkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-c_C_major.wav')))
        self.mediaPlayer.play()  
    def C_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-c_C#_major.wav')))
        self.mediaPlayer.play()  
    def DkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-d_D_major.wav')))
        self.mediaPlayer.play()                 
    def D_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-eb_D#_major.wav')))
        self.mediaPlayer.play()
    def EkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-e_E_major.wav')))
        self.mediaPlayer.play() 
    def FkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-f_F_major.wav')))
        self.mediaPlayer.play()      
    def F_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-f_F#_major.wav')))
        self.mediaPlayer.play()       
    def GkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-g_G_major.wav')))
        self.mediaPlayer.play()   
    def G_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'piano/Piano-g_G#_major.wav')))
        self.mediaPlayer.play()     
    def MBongo(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'bongos/Bongos_bongo1.wav')))
        self.mediaPlayer.play()     
    def NBongo(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'bongos/Bongos_bongo2.wav')))
        self.mediaPlayer.play()    
    def Xylophone1ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (1).wav')))
        self.mediaPlayer.play()
    def Xylophone2ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (2).wav')))
        self.mediaPlayer.play()                
    def Xylophone3ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (3).wav')))
        self.mediaPlayer.play()
    def Xylophone4ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (4).wav')))
        self.mediaPlayer.play()    
    def Xylophone5ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (5).wav')))
        self.mediaPlayer.play()    
    def Xylophone6ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (6).wav')))
        self.mediaPlayer.play()    
    def Xylophone7ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (7).wav')))
        self.mediaPlayer.play()    
    def Xylophone8ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (8).wav')))
        self.mediaPlayer.play()    
    def Xylophone1ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (8).wav')))
        self.mediaPlayer.play()
    def Xylophone2ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (9).wav')))
        self.mediaPlayer.play()
    def Xylophone3ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (10).wav')))
        self.mediaPlayer.play()     
    def Xylophone4ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (11).wav')))
        self.mediaPlayer.play()       
    def Xylophone5ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (12).wav')))
        self.mediaPlayer.play()        
    def Xylophone6ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (13).wav')))
        self.mediaPlayer.play()    
    def Xylophone7ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (14).wav')))
        self.mediaPlayer.play()    
    def Xylophone8ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'xylophone/Xylophone_C (15).wav')))
        self.mediaPlayer.play()



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
