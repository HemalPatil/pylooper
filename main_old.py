# 20200902-0719 IST
# Trying to directly infuse single track looper from Riju into a UI
# Looking at his code and tutorial on YT (@ThePsychotenuse)
# Replace the looper infinite while loop with a button to control play and overdub
#   with a button

from PyQt5 import QtCore, QtGui, QtWidgets
import pyaudio
import numpy as np
import sys

# 20200902-0719 IST
#   audio_parameters[0] = 44100 (Bitrate, standard 44.1kHz audio)
#   audio_parameters[1] = 512 (CHUNK size, some buffer size - what are units? is it Bytes, kB?)
#   audio_parameters[2] = -130 (latency in milliseconds)
#   audio_parameters[3] = 1 (metronome beep length - is it a bar of music?)
audio_settings_file = open('AudioSetup.config', 'r')
audio_parameters = audio_settings_file.readlines()
audio_settings_file.close()

# 20200902-0725 IST
#   loop_parameters[0] = 170 BPM (this should be controllable via a control on the UI, I'll come back to this later)
#   loop_parameters[1] = 4 beats per bar
#   loop_parameters[2] = 2 number of bars per loop
#   loop_parameters[3] = 1 loop count-in (This shouldn't be necessary or at least be UI controllable, idk will figure out)
loop_settings_file = open('LoopSetup.config', 'r')
loop_parameters = loop_settings_file.readlines()
loop_settings_file.close()

RATE = int(audio_parameters[0]) #sample rate
CHUNK = int(audio_parameters[1]) #buffer size
FORMAT = pyaudio.paInt16 #16-bit audio
CHANNELS = 1 #mono (WHY RIJU WHY? We have 2 ears)

#this variable corrects for latency in overdubbing
#it is added to buffer index during write audio buffer to audio buffer array
latency_in_milliseconds = int(audio_parameters[2])
LATENCY = int((RATE / CHUNK) * (latency_in_milliseconds / 1000))

#length in buffers of actual beeps during countdown
metronome_beeplength = int(audio_parameters[3])

tempo = int(loop_parameters[0])
beats_per_bar = int(loop_parameters[1])
bars_per_loop = int(loop_parameters[2])
bars_of_countin = int(loop_parameters[3])

#length in buffers of audio loop
CLIPLENGTH = int((RATE / CHUNK) * (60 / tempo) * beats_per_bar * bars_per_loop)

isRecording = False

#buffer containing silence for period between clicks during count-in
silence = np.zeros(CHUNK, dtype = np.int16)

#buffer click now contains a sawtooth wave. RHS of modulo controls frequency
click = np.zeros(CHUNK, dtype = np.int16)
for i in range(CHUNK):
    click[i] = 100 * (i % 20)

#no of buffers i.e. time, between metronome clicks
metronome_clicktime = CLIPLENGTH / (beats_per_bar * bars_per_loop)

#length in buffers of count-in
countin_length = int((CLIPLENGTH / bars_per_loop) * bars_of_countin)

#initializing overdub attenuation factor
mix_ratio = 1

pa = None

class audioclip:
    def __init__(self):
        self.audio = np.zeros([CLIPLENGTH, CHUNK], dtype = np.int16)
        self.readp = 0
        self.writep = (CLIPLENGTH + LATENCY) % CLIPLENGTH

    def is_restarting(self):
        if (self.readp == 0):
            return True
        else:
            return False

    def incw(self):
        self.writep = ((self.writep + 1) % CLIPLENGTH)

    def incr(self):
        self.readp = ((self.readp + 1) % CLIPLENGTH)

    def write(self, data):
        self.audio[self.writep, :] = np.frombuffer(data, dtype = np.int16)
        self.incw()

    def read(self):
        tmp = self.readp
        self.incr()
        return(self.audio[tmp, :])

    def dub(self, data):
        datadump = np.frombuffer(data, dtype = np.int16)
        for i in range(CHUNK):
            self.audio[self.writep, i] = self.audio[self.writep, i] * 0.9 + datadump[i] * mix_ratio
        self.incw()

#main audio loop
clip1 = None
# audioclip()

def loop_callback(in_data, frame_count, time_info, status):
    global mix_ratio
    global clip1
    global isRecording
    if (clip1.is_restarting()):
        clip1.writep = (CLIPLENGTH + LATENCY) % CLIPLENGTH   #reset latency
        if isRecording:
            mix_ratio = mix_ratio * 0.9                      #nth overdub is mixed with loop at 0.9**n : 0.9 ratio

    if isRecording:
        clip1.dub(in_data)
    return(clip1.read(), pyaudio.paContinue)

click_stream = None
def open_click_stream():
    global click_stream
    click_stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=False,
        output=True,
        frames_per_buffer = CHUNK
    )

loop_stream = None
def open_loop_stream():
    global loop_stream
    loop_stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer = CHUNK,
        start = False,
        stream_callback = loop_callback
    )

class PyLooperWindow(QtWidgets.QMainWindow):
    def startStopLoop_click(self):
        global isRecording
        global click_stream
        global loop_stream
        global clip1
        global mix_ratio
        global pa
        if self.isLoopOn:
            isRecording = False
            self.isLoopOn = False
            self.status.setText("STOPPED")
            self.track1Status.setText("STOPPED")
            self.startStopLoop.setText("Start Loop")
            loop_stream.stop_stream()
            loop_stream.close()
            click_stream.stop_stream()
            click_stream.close()
            loop_stream = None
            click_stream = None
            clip1 = None
            mix_ratio = 1
            pa.terminate()
        else:
            self.isLoopOn = True
            self.startStopLoop.setText("Stop Loop")
            self.status.setText("COUNT-IN")
            pa = pyaudio.PyAudio()
            open_click_stream()
            open_loop_stream()
            clip1 = audioclip()
            for i in range(countin_length): #count-in
                if (i % metronome_clicktime < metronome_beeplength):
                    click_stream.write(click, CHUNK)
                else:
                    click_stream.write(silence, CHUNK)
            loop_stream.start_stream()
            self.status.setText("LOOPING")
            for i in range(CLIPLENGTH): #metronome
                if (i % metronome_clicktime < metronome_beeplength):
                    click_stream.write(click, CHUNK)
                else:
                    click_stream.write(silence, CHUNK)

    def track1Record_click(self):
        global isRecording
        if isRecording:
            isRecording = False
            self.track1Status.setText("STOPPED")
        else:
            isRecording = True
            self.track1Status.setText("OVERDUB")

    def setupUi(self):
        self.track1Label = QtWidgets.QLabel(self)
        self.track1Label.setGeometry(QtCore.QRect(130, 80, 55, 16))
        self.track1Label.setObjectName("track1Label")
        self.track1Record = QtWidgets.QPushButton(self)
        self.track1Record.setGeometry(QtCore.QRect(130, 100, 93, 28))
        self.track1Record.setObjectName("track1Record")
        self.track1Record.clicked.connect(self.track1Record_click)
        self.track1StatusLabel = QtWidgets.QLabel(self)
        self.track1StatusLabel.setGeometry(QtCore.QRect(130, 130, 55, 16))
        self.track1StatusLabel.setObjectName("track1StatusLabel")
        self.track1Status = QtWidgets.QLineEdit(self)
        self.track1Status.setEnabled(False)
        self.track1Status.setGeometry(QtCore.QRect(230, 130, 113, 22))
        self.track1Status.setReadOnly(True)
        self.track1Status.setObjectName("track1Status")
        self.statusLabel = QtWidgets.QLabel(self)
        self.statusLabel.setGeometry(QtCore.QRect(20, 10, 55, 16))
        self.statusLabel.setObjectName("statusLabel")
        self.status = QtWidgets.QLineEdit(self)
        self.status.setEnabled(False)
        self.status.setGeometry(QtCore.QRect(70, 10, 113, 22))
        self.status.setReadOnly(True)
        self.status.setObjectName("status")
        self.startStopLoop = QtWidgets.QPushButton(self)
        self.startStopLoop.setGeometry(QtCore.QRect(220, 10, 93, 28))
        self.startStopLoop.setObjectName("startStopLoop")
        self.startStopLoop.clicked.connect(self.startStopLoop_click)
        self.track1Label.setText("Track1")
        self.track1StatusLabel.setText("Track1 Status")
        self.track1StatusLabel.adjustSize()
        self.track1Record.setText("Track1 Record")
        self.statusLabel.setText("Status")
        self.status.setText("STOPPED")
        self.track1Status.setText("STOPPED")
        self.startStopLoop.setText("Start Loop")
        self.setWindowTitle("PyLooper")
        self.setMinimumWidth(640)
        self.setMaximumWidth(1920)
        self.setMinimumHeight(480)
        self.setMaximumHeight(1080)
        self.isLoopOn = False

    def __init__(self):
        super(PyLooperWindow, self).__init__()
        self.setupUi()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pyLooperWindow = PyLooperWindow()
    pyLooperWindow.show()
    sys.exit(app.exec_())
