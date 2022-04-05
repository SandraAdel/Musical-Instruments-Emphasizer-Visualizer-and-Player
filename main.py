import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph
from pyqtgraph import PlotWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import Qt, QUrl
import pandas as pd
from GUI import Ui_MainWindow
from scipy.io import wavfile
import scipy.fft
import numpy as np

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

        self.instrumentsDataList = [ { "Instrument": "Bass", "Starting Frequency": 0, "Ending Frequency": 128, "Gain": 1 }, { "Instrument": "Trombone", "Starting Frequency": 128, "Ending Frequency": 550, "Gain": 0 }, { "Instrument": "E-Flat Clarinet", "Starting Frequency": 550, "Ending Frequency": 1000, "Gain": 0 }, { "Instrument": "Piccolo", "Starting Frequency": 1000, "Ending Frequency": 2000, "Gain": 1 }, { "Instrument": "Viola", "Starting Frequency": 2000, "Ending Frequency": 20000, "Gain": 1 } ]
        self.instrumentsUIElementsList = [ { "Instrument": "Bass", "Slider": self.ui.BassGainVerticalSlider, "Gain Value Label": self.ui.BassGainValueTextLabel }, { "Instrument": "Trombone", "Slider": self.ui.TromboneGainVerticalSlider, "Gain Value Label": self.ui.TromboneGainValueTextLabel }, { "Instrument": "E-Flat Clarinet", "Slider": self.ui.E_FlatClarinetGainVerticalSlider, "Gain Value Label": self.ui.E_FlatClarinetGainValueTextLabel }, { "Instrument": "Piccolo", "Slider": self.ui.PiccoloGainVerticalSlider, "Gain Value Label": self.ui.PiccoloGainValueTextLabel }, { "Instrument": "Viola", "Slider": self.ui.ViolaGainVerticalSlider, "Gain Value Label": self.ui.ViolaGainValueTextLabel } ]

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
       # self.pianoMode= None

        # for instrumentDictionary in self.instrumentsUIElementsList:
        #     instrumentDictionary["Slider"].setMinimum(0)
        #     instrumentDictionary["Slider"].setMaximum(40)
        #     instrumentDictionary["Slider"].setValue(4)
        #     instrumentDictionary["Gain Value Label"].setText("1x")

        # Links of GUI Elements to Methods:
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
        self.ui.actionOpen.triggered.connect(lambda: self.OpenFile())
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].valueChanged.connect(self.EquilizeMusicSignal)
        self.ui.PianoSettingsComboBox.currentIndexChanged.connect(lambda: self.pianoSettings(self.ui.PianoSettingsComboBox.currentIndex()))
        self.ui.XylophoneSettingsComboBox.currentIndexChanged.connect(lambda: self.xylophoneSettings(self.ui.XylophoneSettingsComboBox.currentIndex()))
    # Methods
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
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-11.wav')))
        self.mediaPlayer.play()
    def Dkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-12.wav')))
        self.mediaPlayer.play() 
    def Ekey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-13.wav')))
        self.mediaPlayer.play()   
    def Fkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-14.wav')))
        self.mediaPlayer.play()          
    def Gkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-15.wav')))
        self.mediaPlayer.play() 
    def Akey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-16.wav')))
        self.mediaPlayer.play()     
    def Bkey(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-17.wav')))
        self.mediaPlayer.play() 
    def C_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano110.wav')))
        self.mediaPlayer.play()
    def D_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano111.wav')))
        self.mediaPlayer.play()         
    def F_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano112.wav')))
        self.mediaPlayer.play()
    def G_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano113.wav')))
        self.mediaPlayer.play() 
    def A_key(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano114.wav')))
        self.mediaPlayer.play()       
    def A_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-bb_A#_major.wav')))
        self.mediaPlayer.play()  
    def AkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-a_A_major.wav')))
        self.mediaPlayer.play()  
    def BkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-b_B_major.wav')))
        self.mediaPlayer.play()  
    def CkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-c_C_major.wav')))
        self.mediaPlayer.play()  
    def C_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-c_C#_major.wav')))
        self.mediaPlayer.play()  
    def DkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-d_D_major.wav')))
        self.mediaPlayer.play()                 
    def D_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-eb_D#_major.wav')))
        self.mediaPlayer.play()
    def EkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-e_E_major.wav')))
        self.mediaPlayer.play() 
    def FkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-f_F_major.wav')))
        self.mediaPlayer.play()      
    def F_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-f_F#_major.wav')))
        self.mediaPlayer.play()       
    def GkeyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-g_G_major.wav')))
        self.mediaPlayer.play()   
    def G_keyMajor(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Piano-g_G#_major.wav')))
        self.mediaPlayer.play()     
    def MBongo(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Bongos_bongo1.wav')))
        self.mediaPlayer.play()     
    def NBongo(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Bongos_bongo2.wav')))
        self.mediaPlayer.play()    
    def Xylophone1ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (1).wav')))
        self.mediaPlayer.play()
    def Xylophone2ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (2).wav')))
        self.mediaPlayer.play()                
    def Xylophone3ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (3).wav')))
        self.mediaPlayer.play()
    def Xylophone4ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (4).wav')))
        self.mediaPlayer.play()    
    def Xylophone5ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (5).wav')))
        self.mediaPlayer.play()    
    def Xylophone6ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (6).wav')))
        self.mediaPlayer.play()    
    def Xylophone7ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (7).wav')))
        self.mediaPlayer.play()    
    def Xylophone8ToneA(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (8).wav')))
        self.mediaPlayer.play()    
    def Xylophone1ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (8).wav')))
        self.mediaPlayer.play()
    def Xylophone2ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (9).wav')))
        self.mediaPlayer.play()
    def Xylophone3ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (10).wav')))
        self.mediaPlayer.play()     
    def Xylophone4ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (11).wav')))
        self.mediaPlayer.play()       
    def Xylophone5ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (12).wav')))
        self.mediaPlayer.play()        
    def Xylophone6ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (13).wav')))
        self.mediaPlayer.play()    
    def Xylophone7ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (14).wav')))
        self.mediaPlayer.play()    
    def Xylophone8ToneB(self):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(r'./Xylophone_C (15).wav')))
        self.mediaPlayer.play()    
                                                                     

   

    def OpenFile(self):

        self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Music File", directory="", filter="wav (*.wav)")[0]
        if  self.fileName:
            self.samplingRate, self.originalMusicSignal = wavfile.read(self.fileName)
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