
#*######### Imports ##########

import sys, os, wave, pygame, random, logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scipy.fft
import numpy as np
from re import T
from scipy import signal
from PyQt5.QtWidgets import*
from scipy.io import wavfile
from PyQt5.QtCore import QUrl
from GUI import Ui_MainWindow
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    filename='Logging.txt')

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
        
        self.counter=0        
        self.play = True
        self.samplingRate = None
        self.pianoMode = 'Major'
        self.xylophoneMode = 'Alto'
        self.originalMusicSignal = None
        self.equilizedMusicSignal = None
        self.timer.setInterval(400)
        self.fourierTransformOfOriginalMusicSignal = None
        pygame.mixer.pre_init(
            channels=1, allowedchanges=0, buffer=512, frequency=44100)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(65)
        self.timer= QtCore.QTimer()
        self.player = QMediaPlayer()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.instrumentsDataList = [ { "Instrument": "Bass", "Starting Frequency": 0, "Ending Frequency": 128, "Gain": 1 }, { "Instrument": "Trombone", "Starting Frequency": 128, "Ending Frequency": 550, "Gain": 0 }, { "Instrument": "E-Flat Clarinet", "Starting Frequency": 550, "Ending Frequency": 1000, "Gain": 0 }, { "Instrument": "Piccolo", "Starting Frequency": 1000, "Ending Frequency": 2000, "Gain": 1 }, { "Instrument": "Viola", "Starting Frequency": 2000, "Ending Frequency": 20000, "Gain": 1 } ]
        self.instrumentsUIElementsList = [ { "Instrument": "Bass", "Slider": self.ui.BassGainVerticalSlider, "Gain Value Label": self.ui.BassGainValueTextLabel }, { "Instrument": "Trombone", "Slider": self.ui.TromboneGainVerticalSlider, "Gain Value Label": self.ui.TromboneGainValueTextLabel }, { "Instrument": "E-Flat Clarinet", "Slider": self.ui.E_FlatClarinetGainVerticalSlider, "Gain Value Label": self.ui.E_FlatClarinetGainValueTextLabel }, { "Instrument": "Piccolo", "Slider": self.ui.PiccoloGainVerticalSlider, "Gain Value Label": self.ui.PiccoloGainValueTextLabel }, { "Instrument": "Viola", "Slider": self.ui.ViolaGainVerticalSlider, "Gain Value Label": self.ui.ViolaGainValueTextLabel } ]
        self.pianoButtonsAndSoundsList = [{"Button": self.ui.PianoCKeyPushButton, "Major": 'piano/Piano-c_C_major.wav', "Minor":'piano/Piano-11.wav', 'Text': 'A'},{"Button": self.ui.PianoDKeyPushButton, "Major": 'piano/Piano-d_D_major.wav', "Minor": 'piano/Piano-12.wav', 'Text': 'S'},{"Button": self.ui.PianoEKeyPushButton, "Major": 'piano/Piano-e_E_major.wav', "Minor": 'piano/Piano-13.wav', 'Text': 'D'},{"Button": self.ui.PianoFKeyPushButton, "Major": 'piano/Piano-f_F_major.wav', "Minor": 'piano/Piano-14.wav', 'Text': 'F'},{"Button": self.ui.PianoGKeyPushButton, "Major": 'piano/Piano-g_G_major.wav', "Minor":'piano/Piano-15.wav', 'Text': 'G'},{"Button": self.ui.PianoAKeyPushButton, "Major": 'piano/Piano-a_A_major.wav', "Minor": 'piano/Piano-16.wav', 'Text': 'H'},{"Button": self.ui.PianoBKeyPushButton, "Major": 'piano/Piano-b_B_major.wav', "Minor": 'piano/Piano-17.wav', 'Text': 'J'},{"Button": self.ui.PianoQKeyPushButton, "Major": 'piano/Piano-c_C#_major.wav', "Minor": 'piano/Piano110.wav', 'Text': 'Q'},{"Button": self.ui.PianoWKeyPushButton, "Major": 'piano/Piano-eb_D#_major.wav', "Minor": 'piano/Piano111.wav', 'Text': 'W'},{"Button": self.ui.PianoRKeyPushButton, "Major": 'piano/Piano-f_F#_major.wav', "Minor": 'piano/Piano112.wav', 'Text': 'E'},{"Button": self.ui.PianoTKeyPushButton, "Major": 'piano/Piano-g_G#_major.wav', "Minor":'piano/Piano113.wav', 'Text': 'R'},{"Button": self.ui.PianoZKeyPushButton, "Major": 'piano/Piano-bb_A#_major.wav', "Minor": 'piano/Piano114.wav', 'Text': 'T'}]
        self.xylophoneButtonsAndSoundsList = [{"Button": self.ui.Xylophone1KeyPushButton,"Alto":'xylophone/alto1.wav',"Soprano":'xylophone/mode2_1.wav', 'Text':'1'},{"Button": self.ui.Xylophone2KeyPushButton,"Alto":'xylophone/alto2.wav',"Soprano": 'xylophone/mode2_2.wav', 'Text':'2'},{"Button": self.ui.Xylophone3KeyPushButton,"Alto":'xylophone/alto3.wav',"Soprano":'xylophone/mode2_3.wav', 'Text':'3'},{"Button": self.ui.Xylophone4KeyPushButton,"Alto":'xylophone/alto4.wav',"Soprano":'xylophone/mode2_4.wav', 'Text':'4'},{"Button": self.ui.Xylophone5KeyPushButton,"Alto":'xylophone/alto5.wav',"Soprano":'xylophone/mode2_5.wav', 'Text':'5'},{"Button": self.ui.Xylophone6KeyPushButton,"Alto":'xylophone/alto6.wav',"Soprano":'xylophone/mode2_6.wav', 'Text':'6'},{"Button": self.ui.Xylophone7KeyPushButton,"Alto":'xylophone/alto7.wav',"Soprano":'xylophone/mode2_7.wav', 'Text':'7'},{"Button": self.ui.Xylophone8KeyPushButton,"Alto":'xylophone/alto8.wav',"Soprano":'xylophone/mode2_8.wav', 'Text':'8'}]
        self.bongosButtonsAndSoundsList = [{"Button": self.ui.BongosMKeyPushButton,"Sound":'bongos/Bongos_bongo1.wav', 'Text':'M'},{"Button": self.ui.BongosNKeyPushButton,"Sound":'bongos/Bongos_bongo2.wav', 'Text':'N'}]
        # self.uiElementsAndFunctionList = [{"Button" : self.ui.equaliseEmphasizerPushButton, "Function": self.equalise},{"Button": self.ui.pianoMajorPushButton, "Function":self.pianoSettings},{"Function":self.ui.pianoMinorPshButton,"Function":self.pianoSettings},{"Button":self.ui.XylophoneAltoModePushButton,"Function":self.xylophoneSettings},{"Button":self.ui.XylophoneSopranoModePushButton,"Function":self.xylophoneSettings}]
        self.pianoSettings()
        self.xylophoneSettings()
        
        #?######### Links of GUI Elements to Methods ##########
        
        self.timer.timeout.connect(self.updatePlot)
        self.ui.actionOpen.triggered.connect(lambda: self.OpenFile())       
        self.ui.pianoMinorPshButton.clicked.connect(self.pianoSettings)
        self.ui.pianoMajorPushButton.clicked.connect(self.pianoSettings)
        self.ui.equaliseEmphasizerPushButton.clicked.connect(self.equalise)
        self.ui.PlayAndPausePushButton.clicked.connect(lambda: self.playAndPause())
        self.ui.XylophoneAltoModePushButton.clicked.connect(self.xylophoneSettings)
        self.ui.XylophoneSopranoModePushButton.clicked.connect(self.xylophoneSettings)
        self.ui.VolumeUpDownHorizontalSlider.valueChanged.connect(lambda: self.changeVolume())
        # for uiElementDictionary in self.uiElementsAndFunctionList:
        #     uiElementDictionary["Button"].clicked.connect(uiElementDictionary["Function"])
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].valueChanged.connect(self.EquilizeMusicSignal)
        for bongosKeyDictionary in self.bongosButtonsAndSoundsList:
            bongosKeyDictionary["Button"].clicked.connect(lambda: self.instrumentsSelection('Bongos')) 

#! ---------------------------------------------------------------------------------------------------------------------------------------------- #

                                            ##########? Class Methods ##########

                                        #?#######>> Tab 1 Player & Emphasizer <<########
                                        
    #?### Main Methods ####

    # Loading Wave File into Application on Main Graph
    def OpenFile(self):
        self.ui.SongGraphGraphicsView.clear()
        for instrumentDictionary in self.instrumentsUIElementsList:
            instrumentDictionary["Slider"].setValue(4)
        self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Music File", directory="", filter="wav (*.wav)")[0]
        if  self.fileName:
            self.samplingRate, self.originalMusicSignal = wavfile.read(self.fileName) 
            self.clearAndPlotSpectrogram(self.originalMusicSignal, self.samplingRate)
            self.fourierTransformOfOriginalMusicSignal = scipy.fft.rfft(self.originalMusicSignal)
            self.ui.PlayAndPausePushButton.setChecked(True)
            self.playMusic(self.fileName)
            logging.info('User open a File')

    # Play and Pause Signal 
    def playAndPause(self):
        if self.ui.PlayAndPausePushButton.isChecked() and self.play == True: self.TimerAndPlayerSetter(self.timer.start(), self.player.play(), 'icons/pause.png', False, 'Music is played')
        else: self.TimerAndPlayerSetter(self.timer.stop(),self.player.pause(),'icons/play.png',True, 'Music is paused')

    # Read Wave File and Play it's Contant
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
        self.playAndPause()

    # Change the Volume of the song
    def changeVolume(self):
        self.sliderValue=self.ui.VolumeUpDownHorizontalSlider.value()
        currentVolume = self.player.volume() 
        print(currentVolume)
        self.player.setVolume(self.sliderValue)
        logging.info('User Change the Volume')

    # Update Main Graph Plot
    def updatePlot(self):
        self.ui.SongGraphGraphicsView.clear()
        increment = int((self.samplingRate/2))
        self.ui.SongGraphGraphicsView.setYRange(min(self.signal),max(self.signal))
        self.ui.SongGraphGraphicsView.setXRange(self.time[self.counter],self.time[self.counter+increment] )
        self.ui.SongGraphGraphicsView.plot(self.time[self.counter:self.counter+increment], self.signal[self.counter:self.counter+increment])
        self.counter+=increment
    
    # Plot Spectrogram
    def plotSpectrogram(self, sample, sample_rate):
        plt.specgram(sample, Fs=sample_rate)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        self.Canvas.draw()

    # Clear Spectrogram Graph
    def clearSpectrogram(self):
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
        self.ui.spectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)

    # Equilize Music Signal     
    def EquilizeMusicSignal(self):

        logging.info('User Equilizing Signal')
        musicSignalMagnitudeValues = np.abs(self.fourierTransformOfOriginalMusicSignal)
        musicSignalPhaseValues = np.angle(self.fourierTransformOfOriginalMusicSignal)
        musicSignalFrequencyComponents = scipy.fft.rfftfreq(len(self.originalMusicSignal), 1/self.samplingRate)

        for dictionaryIndex, instrumentDictionary in enumerate(self.instrumentsUIElementsList):
            gainValue = round(( instrumentDictionary["Slider"].value() / 40 ) * 10, 2)
            instrumentDictionary["Gain Value Label"].setText(str(gainValue) + "x")
            self.instrumentsDataList[dictionaryIndex]["Gain"] = gainValue

        for instrumentDictionary in self.instrumentsDataList:
            startingFrequencyIndex, endingFrequencyIndex = FindIndexOfNearestValue(musicSignalFrequencyComponents, instrumentDictionary["Starting Frequency"]), FindIndexOfNearestValue(musicSignalFrequencyComponents, instrumentDictionary["Ending Frequency"])
            musicSignalMagnitudeValues[startingFrequencyIndex : endingFrequencyIndex + 1] *= instrumentDictionary["Gain"]

        fourierTransformOfEquilizedMusicSignal = musicSignalMagnitudeValues * np.exp(1j * musicSignalPhaseValues)  
        self.equilizedMusicSignal = np.fft.irfft(fourierTransformOfEquilizedMusicSignal)

    #  Play and Show Spectrogram of Equilized music Signal
    def equalise(self):
        logging.info('Playing Equilized Signal File')
        filename = 'Equilized Ode To Joy ' + str(random.randint(1,1000)) + '.wav'
        wavfile.write(os.path.join('./Equilized Music', filename), 48000, self.equilizedMusicSignal.astype(np.int16))
        self.playMusic(os.path.join('./Equilized Music', filename))
        self.clearAndPlotSpectrogram(self.equilizedMusicSignal, self.samplingRate)
    
#! --------------------------------------------------------------------------------------------------------------------------------------------- #

                                            #?#####>> Tab 2 Virtual  Musical Instrumnets <<######
    
    #?### Main Methods ####

    # Set Piano Settings and it's mode
    def pianoSettings(self):
        self.pianoMode = self.settings(self.pianoMode, self.ui.pianoMinorPshButton, 'Minor', 'Major', self.pianoButtonsAndSoundsList, 'Piano')

    # Set Xylophone Settings and it's mode
    def xylophoneSettings(self):
        self.xylophoneMode = self.settings(self.xylophoneMode, self.ui.XylophoneAltoModePushButton, 'Alto', 'Soprano', self.xylophoneButtonsAndSoundsList, 'Xylophone') 

    # Play instruments according to user Selection 
    def instrumentsSelection(self, instrumentsName):
        if instrumentsName == 'Piano': self.instrumentsPlayer(self.pianoButtonsAndSoundsList, self.pianoMode, 'User is Playing Piano')
        elif instrumentsName == 'Xylophone': self.instrumentsPlayer(self.xylophoneButtonsAndSoundsList, self.xylophoneMode, 'User is Playing Xylophone')
        elif instrumentsName == 'Bongos': self.instrumentsPlayer(self.bongosButtonsAndSoundsList, "Sound", 'User is Playing Bongos')
    
#! -------------------------------------------------------------------------------------------------------------------------------------------- #
 
                                                    ######?>> Helper Functions Tab 1: <<######
 
    # Clearing Spectrogram Before Plot
    def clearAndPlotSpectrogram(self, signal, samplingRate):
        self.clearSpectrogram()
        self.plotSpectrogram(signal, samplingRate)

    # Play and Pause Helping Function
    def TimerAndPlayerSetter(self, timer, player, icon, trueOrFalse, message):
        timer
        player
        self.ui.PlayAndPausePushButton.setIcon(QtGui.QIcon(icon))
        self.play = trueOrFalse
        logging.info(message)
    
#! -------------------------------------------------------------------------------------------------------------------------------------------- #

                                                    ######?>> Helper Functions Tab 2: <<######

    # Load a Wave File and Play it using Mixer
    def mixerPlay(self, file):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

    # Play intruments 
    def instrumentsPlayer(self, list, mode, message):
        keyText = self.sender().text()
        keyDictionary = GetDictionaryByKeyValuePair(list, 'Text', keyText)
        self.mixerPlay(keyDictionary[mode])
        logging.info(message) 

    # Set instruments mode and connect instruments buttons
    def settings(self, instrumentMode, button, mode1, mode2, list, instrumentsName):
        if button.isChecked(): instrumentMode = mode1
        else: instrumentMode = mode2
        for KeyDictionary in list:
            KeyDictionary["Button"].clicked.connect(lambda: self.instrumentsSelection(instrumentsName))  
        return instrumentMode

#! --------------------------------------------------------------------------------------------------------------------------------------------- #
                                                   
                                                    #?#####>> Global Functions: <<######
                                                    
#
def FindIndexOfNearestValue(arrayToFindNearestValueIn, value):
    arrayToFindNearestValueIn = np.asarray(arrayToFindNearestValueIn)
    indexOfNearestValue = (np.abs(arrayToFindNearestValueIn - value)).argmin()
    return indexOfNearestValue

#
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
    
